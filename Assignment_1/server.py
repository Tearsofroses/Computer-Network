import logging
import socket
import threading
from collections import deque
import json
import psycopg2
import sys
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Database connection
try:
    db_conn = psycopg2.connect(
        dbname="filesharing",
        user="postgres",
        password=r"13?T+4i%ewse",
        host="localhost",
        port="5432"
    )
    cursor = db_conn.cursor()
    logging.info("Connected to PostgreSQL database.")
except Exception as e:
    logging.error(f"Failed to connect to database: {e}")
    sys.exit(1)

# Global state
MAX_CLIENTS = 5

# Maps hostname -> socket (populated when client sends 'introduce')
active_clients: Dict[str, socket.socket] = {}  # hostname -> socket
# FIFO queue of active connections (socket, addr) in connection order.
connection_queue: deque[Tuple[socket.socket, Tuple[str, int]]] = deque()
# Queue for sockets that are waiting to be accepted when a slot frees.
# Each entry is (socket, addr, threading.Event) where the Event is used
# to signal the per-connection worker to start handling the client.
waiting_queue: deque[Tuple[socket.socket, Tuple[str, int], threading.Event]] = deque()
client_lock = threading.Lock()

def log(message: str):
    """Thread-safe logging shortcut."""
    logging.info(message)

def register_or_update_file(lname: str, fname: str, extension: str, hostname: str, ip_addr: str):
    """Insert or update file metadata in the database, including extension."""
    try:
        cursor.execute(
            """
            INSERT INTO client_files (lname, fname, extension, hostname, address)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (address, fname, hostname) 
            DO UPDATE SET lname = EXCLUDED.lname, extension = EXCLUDED.extension
            """,
            (lname, fname, extension, hostname, ip_addr)
        )
        db_conn.commit()
        log(f"Registered file '{fname}' (ext: {extension}) from {hostname}@{ip_addr}")
    except Exception as e:
        logging.error(f"Database error during file registration: {e}")
        db_conn.rollback()

def handle_client_connection(client_sock: socket.socket, client_addr: Tuple[str, int]):
    """Process incoming commands from a connected peer."""
    client_hostname: Optional[str] = None

    try:
        while True:
            raw_data = client_sock.recv(4096).decode('utf-8').strip()
            if not raw_data:
                break

            try:
                command = json.loads(raw_data)
            except json.JSONDecodeError:
                log(f"Invalid JSON from {client_addr}: {raw_data}")
                continue

            action = command.get('action')

            # === Client Introduction ===
            if action == 'introduce':
                client_hostname = command.get('hostname')
                if client_hostname:
                    with client_lock:
                        active_clients[client_hostname] = client_sock
                    log(f"Client introduced: {client_hostname} ({client_addr[0]})")
                else:
                    log(f"Invalid introduce from {client_addr}: missing hostname")

            # === File Publishing ===
            elif action == 'publish':
                hostname = command.get('hostname')
                fname = command.get('fname')
                lname = command.get('lname')
                extension = command.get('extension', '')
                if all([hostname, fname, lname]):
                    register_or_update_file(lname, fname, extension, hostname, client_addr[0])
                    client_sock.sendall(b"File registered successfully.\n")
                else:
                    client_sock.sendall(b"Error: Missing publish fields.\n")

            # === File Discovery (Fetch) ===
            elif action == 'fetch':
                fname = command.get('fname')
                if not fname:
                    client_sock.sendall(json.dumps({'error': 'Missing fname'}).encode() + b'\n')
                    continue

                cursor.execute(
                    """
                    SELECT DISTINCT ON (address, hostname) address, hostname, lname, extension
                    FROM client_files
                    WHERE fname = %s
                    """,
                    (fname,)
                )
                results = cursor.fetchall()

                if results:
                    peers = [
                        {'ip': ip, 'hostname': host, 'lname': lname, 'extension': ext}
                        for ip, host, lname, ext in results
                        if host in active_clients
                    ]
                    response = {'addresses': peers}
                else:
                    response = {'error': 'File not available'}

                client_sock.sendall(json.dumps(response).encode('utf-8') + b'\n')

            # === Optional: File List Request (not used in client, but kept) ===
            elif action == 'file_list':
                files = command.get('files', [])
                log(f"Received file list from {client_addr}: {files}")

    except Exception as e:
        logging.exception(f"Error handling client {client_addr}: {e}")
    finally:
        # Cleanup
        if client_hostname and client_hostname in active_clients:
            with client_lock:
                del active_clients[client_hostname]
        # Remove from connection_queue if present and then promote a waiting client
        promoted_entry: Optional[Tuple[socket.socket, Tuple[str, int], threading.Event]] = None
        with client_lock:
            try:
                # connection_queue contains tuples (sock, addr)
                for item in list(connection_queue):
                    if item[0] is client_sock:
                        connection_queue.remove(item)
                        break
            except ValueError:
                pass

            # If there is a waiting client, promote the oldest waiting one
            if waiting_queue:
                promoted_entry = waiting_queue.popleft()
                # add promoted client to active connection queue (sock, addr)
                connection_queue.append((promoted_entry[0], promoted_entry[1]))

        try:
            client_sock.close()
        except Exception:
            pass

        log(f"Connection closed: {client_addr}")

        # If we promoted a waiting client, signal its event to start handling.
        if promoted_entry:
            promoted_sock, promoted_addr, promoted_event = promoted_entry
            log(f"Promoting waiting client {promoted_addr} into active connections")
            # set the event so the worker thread (already started) proceeds
            try:
                promoted_event.set()
            except Exception as e:
                logging.exception(f"Failed to set promote event for {promoted_addr}: {e}")


def discover_peer_files(hostname: str):
    """
    Show all files that <hostname> has PUBLISHED (i.e., registered via 'publish' command).
    This reads from the PostgreSQL database, not the peer's local folder.
    """
    try:
        cursor.execute(
            """
            SELECT fname, extension
            FROM client_files
            WHERE hostname = %s
            ORDER BY fname
            """,
            (hostname,)
        )
        results = cursor.fetchall()

        if not results:
            logging.warning(f"No published files found for host: {hostname}")
            return

        logging.info(f"Published files by {hostname}:")
        for fname, ext in results:
            full_name = f"{fname}.{ext}" if ext else fname
            logging.info(f"  • {full_name}")

    except Exception as e:
        logging.error(f"Failed to discover files for {hostname}: {e}")

def ping_peer(hostname: str):
    """Send a ping to verify if a peer is online."""
    cursor.execute(
        "SELECT DISTINCT address FROM client_files WHERE hostname = %s LIMIT 1",
        (hostname,)
    )
    result = cursor.fetchone()

    if not result:
        logging.warning(f"No record found for host: {hostname}")
        return

    ip_addr = result[0]
    try:
        ping_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ping_sock.settimeout(3.0)
        ping_sock.connect((ip_addr, 65433))

        ping_sock.sendall(json.dumps({'action': 'ping'}).encode('utf-8') + b'\n')
        response = ping_sock.recv(4096).decode('utf-8').strip()
        ping_sock.close()

        if response == "Hello there!":
            logging.info(f"{hostname} ({ip_addr}) is ONLINE")
        else:
            logging.warning(f"{hostname} responded but not recognized: {response}")
    except Exception as e:
        logging.warning(f"{hostname} ({ip_addr}) is OFFLINE — {e}")


def _waiting_worker(client_sock: socket.socket, client_addr: Tuple[str, int], promote_event: threading.Event):
    """Worker that waits until promoted before handling the client.

    The thread owns the socket and will close it when handle_client_connection
    returns (or on errors). This guarantees only the thread that services a
    socket will close it.
    """
    try:
        # Wait until server signals this connection can be handled
        promote_event.wait()
        # If the event was set, start normal handling
        handle_client_connection(client_sock, client_addr)
    except Exception as e:
        logging.exception(f"Waiting worker error for {client_addr}: {e}")

def server_console():
    """Interactive admin console for server management."""
    print("\nServer Admin Console")
    print("Commands:")
    print("  discover <hostname>  → List files shared by a peer")
    print("  ping <hostname>      → Check if peer is online")
    print("  exit                 → Shut down server\n")

    while True:
        try:
            cmd_line = input("server> ").strip()
            if not cmd_line:
                continue

            parts = cmd_line.split()
            action = parts[0].lower()

            if action == "discover" and len(parts) == 2:
                threading.Thread(target=discover_peer_files, args=(parts[1],), daemon=True).start()
            elif action == "ping" and len(parts) == 2:
                threading.Thread(target=ping_peer, args=(parts[1],), daemon=True).start
            elif action == "exit":
                print("Shutting down server...")
                break
            else:
                print("Invalid command. Type 'discover <host>', 'ping <host>', or 'exit'.")
        except KeyboardInterrupt:
            print("\nConsole interrupted.")
            break

def run_server(host: str = '0.0.0.0', port: int = 65432):
    """Start the main server listener."""
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(10)
    log(f"Server listening on {host}:{port}")

    try:
        while True:
            try:
                client_sock, client_addr = server_sock.accept()
                log(f"New connection from {client_addr}")

                # For robustness start a per-connection worker that will wait on an
                # Event until it is promoted into active connections. This avoids
                # races where the server would start a handler later and accidentally
                # close or mishandle sockets.
                promote_event = threading.Event()
                worker_thread = threading.Thread(
                    target=_waiting_worker,
                    args=(client_sock, client_addr, promote_event),
                    daemon=True
                )
                worker_thread.start()

                with client_lock:
                    if len(connection_queue) < MAX_CLIENTS:
                        # make active immediately
                        connection_queue.append((client_sock, client_addr))
                        promote_event.set()
                        log(f"Accepted and activated connection from {client_addr}")
                    else:
                        # queue for later promotion
                        waiting_queue.append((client_sock, client_addr, promote_event))
                        log(f"Connection from {client_addr} queued (server at capacity)")

            except socket.error:
                continue
    except KeyboardInterrupt:
        log("Server shutdown via interrupt.")
    finally:
        server_sock.close()
        try:
            cursor.close()
            db_conn.close()
            logging.info("Database connection closed.")
        except Exception:
            pass

if __name__ == "__main__":
    # Start server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Start the server command shell in the main thread
    server_console()

    # Signal the server to shutdown
    print("Server shutdown requested.")
    
    sys.exit(0)