import socket
import json
import os
import threading
import shlex

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock()

    def connect(self):
        self.socket.connect((self.host, self.port))

    def send(self, data):
        with self.lock:
            self.socket.sendall(json.dumps(data).encode())

    def receive(self):
        with self.lock:
            response = self.socket.recv(4096)
            return json.loads(response.decode())

    def close(self):
        self.socket.close()

    def publish(self, lname, fname):
        data = {'command': 'publish', 'lname': lname, 'fname': fname}
        self.send(data)
        return self.receive()
    
    def fetch(self, fname):
        data = {'command': 'fetch', 'fname': fname}
        self.send(data)
        
        response = self.receive()

        if response['status'] == 'ok':
            peers = response['peers']
            return peers
        else:
            raise Exception(response['message'])
        
    def send_file(self, conn, lname):
        with open(lname, 'rb') as f:
            while True:
                bytes_read = f.read(4096)
                if not bytes_read:
                    break
                conn.sendall(bytes_read)
        conn.close()
        
    def request_file(self, peer, lname, fname):
        peer_host = peer.host
        peer_port = peer.port
        peer_socket = peer.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            peer_socket.connect()

