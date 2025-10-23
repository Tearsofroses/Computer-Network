import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
import sys

# Import the server functions
from server import run_server, server_console, log as server_log

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P File Sharer – Server")
        self.root.geometry("680x540")
        self.root.configure(padx=10, pady=10)

        self.server_thread = None
        self._build_ui()
        self._start_server()

    def _build_ui(self):
        # ----- Status -----
        self.status_var = tk.StringVar(value="Starting…")
        ttk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=4)

        # ----- Active clients -----
        client_frame = ttk.LabelFrame(self.root, text="Connected Clients")
        client_frame.pack(fill="both", expand=True, pady=8)

        self.client_tree = ttk.Treeview(client_frame, columns=("Hostname", "IP"), show="headings", height=8)
        self.client_tree.heading("Hostname", text="Hostname")
        self.client_tree.heading("IP", text="IP")
        self.client_tree.column("Hostname", width=200)
        self.client_tree.column("IP", width=150, anchor="center")
        self.client_tree.pack(fill="both", expand=True, padx=4, pady=4)

        # ----- Admin commands -----
        cmd_frame = ttk.LabelFrame(self.root, text="Admin Commands")
        cmd_frame.pack(fill="x", pady=8)

        ttk.Label(cmd_frame, text="Hostname:").grid(row=0, column=0, padx=4, pady=4, sticky="e")
        self.cmd_host_var = tk.StringVar()
        ttk.Entry(cmd_frame, textvariable=self.cmd_host_var, width=30).grid(row=0, column=1, padx=4, pady=4)

        ttk.Button(cmd_frame, text="Discover Files", command=self._discover).grid(row=0, column=2, padx=4)
        ttk.Button(cmd_frame, text="Ping", command=self._ping).grid(row=0, column=3, padx=4)

        # ----- Log console -----
        log_frame = ttk.LabelFrame(self.root, text="Server Log")
        log_frame.pack(fill="both", expand=True, pady=8)
        self.log_text = tk.Text(log_frame, height=10, state="disabled", wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=4, pady=4)

        # Redirect logging
        class TextHandler(logging.Handler):
            def emit(self, record):
                msg = self.format(record)
                self._append(msg)
        handler = TextHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        handler._append = lambda m: self.root.after(0, lambda: self._log(m))
        logging.getLogger().addHandler(handler)

    def _log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # --------------------------------------------------------------- Server start
    def _start_server(self):
        def run():
            try:
                self.root.after(0, lambda: self.status_var.set("Running on 0.0.0.0:65432"))
                run_server()
            except Exception as e:
                self.root.after(0, lambda: self._log(f"Server crashed: {e}"))
        self.server_thread = threading.Thread(target=run, daemon=True)
        self.server_thread.start()

        # Periodic refresh of client list
        def refresh():
            from server import active_clients, client_lock
            with client_lock:
                current = set(active_clients.keys())
            for item in self.client_tree.get_children():
                self.client_tree.delete(item)
            for hn in current:
                ip = active_clients[hn].getpeername()[0]
                self.client_tree.insert("", "end", values=(hn, ip))
            self.root.after(3000, refresh)
        self.root.after(3000, refresh)

    # --------------------------------------------------------------- Admin actions
    def _discover(self):
        hn = self.cmd_host_var.get().strip()
        if not hn:
            messagebox.showwarning("Empty", "Enter a hostname.")
            return
        threading.Thread(target=self._do_discover, args=(hn,), daemon=True).start()

    def _do_discover(self, hostname):
        from server import discover_peer_files
        try:
            discover_peer_files(hostname)  # prints to console → captured by log handler
        except Exception as e:
            self.root.after(0, lambda: self._log(f"Discover error: {e}"))

    def _ping(self):
        hn = self.cmd_host_var.get().strip()
        if not hn:
            messagebox.showwarning("Empty", "Enter a hostname.")
            return
        threading.Thread(target=self._do_ping, args=(hn,), daemon=True).start()

    def _do_ping(self, hostname):
        from server import ping_peer
        try:
            ping_peer(hostname)
        except Exception as e:
            self.root.after(0, lambda: self._log(f"Ping error: {e}"))

    # --------------------------------------------------------------- Shutdown
    def close(self):
        self._log("Shutting down server…")
        import os, signal
        os.kill(os.getpid(), signal.SIGINT)  # triggers KeyboardInterrupt in server thread
        self.root.after(1000, self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()