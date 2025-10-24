import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import socket
import os
import shlex

# Import the client functions
from client import (
    shutdown_event, run_file_sharing_service, register_with_server,
    announce_file_to_server, download_file_from_peer
)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

SERVER_IP = get_local_ip()
SERVER_PORT = 65432
class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P File Sharer – Client")
        self.root.geometry("720x520")
        self.root.configure(padx=10, pady=10)

        self.server_sock = None
        self.service_thread = None

        self._build_ui()
        self._start_background()

    # --------------------------------------------------------------- UI
    def _build_ui(self):
        # ----- Connection status -----
        self.status_var = tk.StringVar(value="Not connected")
        ttk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 10, "bold")).pack(anchor="w")

        # ----- Publish section -----
        pub_frame = ttk.LabelFrame(self.root, text="Publish a file")
        pub_frame.pack(fill="x", pady=8)

        ttk.Label(pub_frame, text="Local file:").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.pub_local_var = tk.StringVar()
        ttk.Entry(pub_frame, textvariable=self.pub_local_var, width=50).grid(row=0, column=1, padx=4, pady=2)
        ttk.Button(pub_frame, text="Browse…", command=self._browse_local).grid(row=0, column=2, padx=4)

        ttk.Label(pub_frame, text="Shared name:").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.pub_shared_var = tk.StringVar()
        ttk.Entry(pub_frame, textvariable=self.pub_shared_var, width=50).grid(row=1, column=1, padx=4, pady=2)

        ttk.Button(pub_frame, text="Publish", command=self._publish).grid(row=1, column=2, padx=4, pady=2)

        # ----- Fetch section -----
        fetch_frame = ttk.LabelFrame(self.root, text="Download a file")
        fetch_frame.pack(fill="x", pady=8)

        ttk.Label(fetch_frame, text="File name to fetch:").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.fetch_var = tk.StringVar()
        ttk.Entry(fetch_frame, textvariable=self.fetch_var, width=50).grid(row=0, column=1, padx=4, pady=2)
        ttk.Button(fetch_frame, text="Search", command=self._search_file).grid(row=0, column=2, padx=4)

        # ----- Peer list -----
        self.peer_tree = ttk.Treeview(self.root, columns=("IP", "Hostname", "LocalName", "Extension"), show="headings", height=6)
        self.peer_tree.heading("IP", text="IP")
        self.peer_tree.heading("Hostname", text="Hostname")
        self.peer_tree.heading("LocalName", text="Local Name")
        self.peer_tree.heading("Extension", text="Extension")
        self.peer_tree.column("IP", width=120, anchor="center")
        self.peer_tree.column("Hostname", width=150)
        self.peer_tree.column("LocalName", width=200)
        self.peer_tree.column("Extension", width=100, anchor="center")
        self.peer_tree.pack(fill="both", expand=True, pady=8)

        ttk.Button(self.root, text="Download Selected", command=self._download_selected).pack(pady=4)

        # ----- Log console -----
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill="both", expand=True, pady=8)
        self.log_text = tk.Text(log_frame, height=6, state="disabled", wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=4, pady=4)

    # --------------------------------------------------------------- Helpers
    def _log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _browse_local(self):
        path = filedialog.askopenfilename(title="Select file to share")
        if path:
            self.pub_local_var.set(path)
            # Suggest a shared name = basename without extension
            base = os.path.basename(path)
            name, _ = os.path.splitext(base)
            self.pub_shared_var.set(name)

    # --------------------------------------------------------------- Background
    def _start_background(self):
        self.service_thread = threading.Thread(target=run_file_sharing_service, daemon=True)
        self.service_thread.start()

        def connect():
            try:
                self.server_sock = register_with_server(SERVER_IP, SERVER_PORT)
                self.root.after(0, lambda: self.status_var.set("Connected to server"))
                self._log("Connected to central server.")
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set("Connection failed"))
                self._log(f"Failed to connect: {e}")

        threading.Thread(target=connect, daemon=True).start()

    # --------------------------------------------------------------- Actions
    def _publish(self):
        local = self.pub_local_var.get().strip()
        shared = self.pub_shared_var.get().strip()
        if not local or not shared:
            messagebox.showwarning("Input missing", "Both local file and shared name are required.")
            return
        if not os.path.isfile(local):
            messagebox.showerror("File not found", f"Local file does not exist:\n{local}")
            return

        def do():
            try:
                announce_file_to_server(self.server_sock, local, shared)
                self.root.after(0, lambda: self._log(f"Published '{shared}'"))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Publish error: {e}"))

        threading.Thread(target=do, daemon=True).start()

    def _search_file(self):
        fname = self.fetch_var.get().strip()
        if not fname:
            messagebox.showwarning("Empty", "Enter a file name to search.")
            return

        for item in self.peer_tree.get_children():
            self.peer_tree.delete(item)

        def do():
            try:
                query = {"action": "fetch", "fname": fname}
                self.server_sock.sendall(json.dumps(query).encode('utf-8') + b'\n')
                raw = self.server_sock.recv(4096).decode('utf-8').strip()
                resp = json.loads(raw)

                if 'addresses' not in resp or not resp['addresses']:
                    self.root.after(0, lambda: self._log("No peers have this file."))
                    return

                peers = resp['addresses']
                for p in peers:
                    self.root.after(0, lambda p=p: self.peer_tree.insert("", "end",
                        values=(p['ip'], p['hostname'], p.get('lname', ''), p.get('extension', ''))))

                self.root.after(0, lambda: self._log(f"Found {len(peers)} peer(s) for '{fname}'"))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Search error: {e}"))

        threading.Thread(target=do, daemon=True).start()

    def _download_selected(self):
        sel = self.peer_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a peer from the list first.")
            return
        values = self.peer_tree.item(sel[0])['values']
        ip, _, lname, ext = values
        fname = self.fetch_var.get()
        initial_save = fname + ('.' + ext if ext else '')
        save_as = filedialog.asksaveasfilename(title="Save file as", initialfile=initial_save)
        if not save_as:
            return

        def do():
            try:
                download_file_from_peer(ip, lname, save_as)
                self.root.after(0, lambda: self._log(f"Downloaded to {save_as}"))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Download failed: {e}"))

        threading.Thread(target=do, daemon=True).start()

    # --------------------------------------------------------------- Shutdown
    def close(self):
        shutdown_event.set()
        if self.server_sock:
            try: self.server_sock.close()
            except: pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()