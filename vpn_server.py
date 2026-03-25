import socket
import threading
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VPNServer:
    def __init__(self, host='localhost', port=8443):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.lock = threading.Lock()

    def start(self):
        """Start the VPN server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logger.info(f"VPN Server started on {self.host}:{self.port}")

        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                logger.info(f"New client connected: {client_address}")
                
                with self.lock:
                    self.clients.append(client_socket)
                
                # Handle client in a separate thread
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
            self.stop()

    def handle_client(self, client_socket, client_address):
        """Handle individual client connections"""
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                logger.info(f"Received from {client_address}: {data.decode('utf-8', errors='ignore')}")
                
                # Echo the message back to all clients
                self.broadcast_message(data, client_socket)
        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            with self.lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
            client_socket.close()
            logger.info(f"Client {client_address} disconnected")

    def broadcast_message(self, message, sender_socket):
        """Broadcast message to all connected clients"""
        with self.lock:
            for client in self.clients:
                if client != sender_socket:
                    try:
                        client.send(message)
                    except Exception as e:
                        logger.error(f"Error broadcasting message: {e}")

    def stop(self):
        """Stop the VPN server"""
        if self.server_socket:
            self.server_socket.close()
        for client in self.clients:
            client.close()
        logger.info("Server stopped")

if __name__ == "__main__":
    vpn_server = VPNServer()
    vpn_server.start()