import socket
import threading
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VPNClient:
    def __init__(self, host='localhost', port=8443):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        """Connect to VPN server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logger.info(f"Connected to VPN Server at {self.host}:{self.port}")
            
            # Start receiving messages in a separate thread
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Send messages from user input
            self.send_messages()
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            self.disconnect()

    def send_messages(self):
        """Send messages to the server"""
        try:
            while True:
                message = input("Enter message (or 'quit' to exit): ")
                if message.lower() == 'quit':
                    break
                self.socket.send(message.encode('utf-8'))
                logger.info(f"Sent: {message}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    def receive_messages(self):
        """Receive messages from the server"""
        try:
            while True:
                data = self.socket.recv(4096)
                if not data:
                    break
                logger.info(f"Received: {data.decode('utf-8', errors='ignore')}")
        except Exception as e:
            logger.error(f"Error receiving message: {e}")

    def disconnect(self):
        """Disconnect from the server"""
        if self.socket:
            self.socket.close()
        logger.info("Disconnected from VPN Server")

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8443
    
    vpn_client = VPNClient(host, port)
    vpn_client.connect()