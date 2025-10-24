import socket
import json
import os
import threading
import shlex
from pathlib import Path

# Global flag to signal shutdown of background services
shutdown_event = threading.Event()

def safe_join(base_dir, user_path):
    base = Path(base_dir).resolve()
    target = (base / user_path).resolve()
    if not str(target).startswith(str(base)):
        raise ValueError("Access denied")
    return str(target)

def list_local_files(directory='.'):
    """Return a list of filenames in the given directory."""
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except Exception as e:
        return f"Error listing files: {e}"

def handle_peer_connection(client_conn, shared_dir):
    """Handle incoming peer requests: file list, file transfer, or ping."""
    try:
        raw_data = client_conn.recv(4096).decode('utf-8').strip()
        request = json.loads(raw_data)

        if request['action'] == 'send_file':
            local_filename = request['lname']
            file_path = safe_join(shared_dir, local_filename)
            stream_file_to_peer(client_conn, file_path)

        elif request['action'] == 'request_file_list':
            files = list_local_files(shared_dir)
            response = {'files': files}
            client_conn.sendall(json.dumps(response).encode('utf-8') + b'\n')

        elif request['action'] == 'ping':
            client_conn.sendall(b'Hello there!\n')

    except Exception as e:
        print(f"Error handling peer request: {e}")
    finally:
        client_conn.close()

def stream_file_to_peer(conn, file_path):
    """Send a file to the connected peer in chunks."""
    if not os.path.exists(file_path):
        return
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                conn.sendall(chunk)
    except Exception as e:
        print(f"Error sending file {file_path}: {e}")

def run_file_sharing_service(port=65433, shared_dir='./'):
    """Start a background server to accept incoming peer connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f"File sharing service running on port {port}...")

    while not shutdown_event.is_set():
        try:
            server.settimeout(1.0)
            client_conn, client_addr = server.accept()
            thread = threading.Thread(
                target=handle_peer_connection,
                args=(client_conn, shared_dir),
                daemon=True
            )
            thread.start()
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Server error: {e}")
            break

    server.close()

def announce_file_to_server(sock, local_path, shared_name):
    """Tell the central server about a file we want to share."""
    if not os.path.exists(local_path):
        print(f"File not found: {local_path}")
        return

    # Extract extension (without dot)
    _, ext = os.path.splitext(local_path)
    extension = ext.lstrip('.') if ext else ''

    hostname = socket.gethostname()
    announcement = {
        "action": "publish",
        "fname": shared_name,
        "lname": local_path,
        "extension": extension,
        "hostname": hostname
    }
    sock.sendall(json.dumps(announcement).encode('utf-8') + b'\n')
    response = sock.recv(4096).decode('utf-8').strip()
    print(response)

def query_file_locations(sock, filename):
    """Ask the server which peers have the requested file."""
    query = {"action": "fetch", "fname": filename}
    sock.sendall(json.dumps(query).encode('utf-8') + b'\n')
    
    try:
        raw_response = sock.recv(4096).decode('utf-8').strip()
        server_response = json.loads(raw_response)

        if 'addresses' not in server_response or not server_response['addresses']:
            print("No peers currently have this file.")
            return

        peers = server_response['addresses']
        print(f"Found {len(peers)} peer(s) with '{filename}':")
        for p in peers:
            print(f"  - {p['hostname']} @ {p['ip']} (ext: {p.get('extension', '')})")

        if len(peers) == 1:
            chosen = peers[0]
        else:
            ip = input("Enter IP to download from: ").strip()
            chosen = next((p for p in peers if p['ip'] == ip), None)
            if not chosen:
                print("Invalid IP selected.")
                return

        # Construct save name with extension
        save_name = filename
        if 'extension' in chosen and chosen['extension']:
            save_name += '.' + chosen['extension']

        download_file_from_peer(chosen['ip'], chosen['lname'], save_name)

    except json.JSONDecodeError:
        print("Invalid response from server.")
    except Exception as e:
        print(f"Error querying file: {e}")

def download_file_from_peer(peer_ip, local_name_on_peer, save_as):
    """Connect to a peer and download the specified file."""
    peer_port = 65433
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((peer_ip, peer_port))
        client.sendall(json.dumps({
            'action': 'send_file',
            'lname': local_name_on_peer
        }).encode('utf-8') + b'\n')

        with open(save_as, 'wb') as f:
            while True:
                data = client.recv(4096)
                if not data:
                    break
                f.write(data)

        print(f"Successfully downloaded '{save_as}' from {peer_ip}")
    except Exception as e:
        print(f"Failed to download from {peer_ip}:{peer_port} — {e}")
    finally:
        client.close()

def register_with_server(server_host, server_port):
    """Connect and introduce ourselves to the central server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_host, server_port))

    hostname = socket.gethostname()
    sock.sendall(json.dumps({
        'action': 'introduce',
        'hostname': hostname
    }).encode('utf-8') + b'\n')

    return sock

def main(server_ip, server_port):
    # Start local file-sharing service in background
    service_thread = threading.Thread(
        target=run_file_sharing_service,
        args=(65433, './'),
        daemon=True
    )
    service_thread.start()

    # Connect to central server
    server_socket = register_with_server(server_ip, server_port)

    print("Connected to server. Available commands:")
    print("  publish <local_file> <shared_name>")
    print("  fetch <shared_name>")
    print("  exit")

    try:
        while True:
            cmd_input = input("\n> ").strip()
            if not cmd_input:
                continue

            parts = shlex.split(cmd_input)

            if len(parts) == 3 and parts[0].lower() == 'publish':
                _, local_file, shared_name = parts
                announce_file_to_server(server_socket, local_file, shared_name)

            elif len(parts) == 2 and parts[0].lower() == 'fetch':
                _, filename = parts
                query_file_locations(server_socket, filename)

            elif cmd_input.lower() == 'exit':
                print("Shutting down...")
                shutdown_event.set()
                server_socket.close()
                break

            else:
                print("Invalid command. Use: publish lname fname | fetch fname | exit")

    except KeyboardInterrupt:
        print("\nInterrupted. Exiting...")
    finally:
        shutdown_event.set()
        server_socket.close()
        service_thread.join(timeout=2)