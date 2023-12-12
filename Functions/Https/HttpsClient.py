from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import socket


# Client code to establish a secure connection with the server
class EncryptedClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.symmetric_key = None

    def connect_to_server(self):
        self.socket.connect((self.server_host, self.server_port))
        print(f"Connected to server at {self.server_host}:{self.server_port}")

    def request_public_key(self):
        self.socket.sendall(b'GET PUBLIC KEY')
        public_key_pem = self.socket.recv(4096)
        public_key = load_pem_public_key(public_key_pem, backend=default_backend())
        print("Received public key from server")
        return public_key

    def generate_symmetric_key(self):
        # Generate a random symmetric key for AES
        self.symmetric_key = os.urandom(32)
        print("Symmetric key generated")

    def encrypt_and_send_symmetric_key(self, public_key):
        # Encrypt the symmetric key with the server's public key
        encrypted_key = public_key.encrypt(
            self.symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # Send the encrypted symmetric key to the server
        self.socket.sendall(encrypted_key)
        print("Encrypted symmetric key sent to server")

    def close_connection(self):
        self.socket.close()
        print("Connection closed")


# Example usage of the client
server_host = 'localhost'
server_port = 12345

# Initialize the client
client = EncryptedClient(server_host, server_port)

# Connect to the server
client.connect_to_server()

# Request the public key from the server
server_public_key = client.request_public_key()

# Generate a symmetric key
client.generate_symmetric_key()

# Encrypt the symmetric key with the server's public key and send it to the server
client.encrypt_and_send_symmetric_key(server_public_key)

# Close the connection
client.close_connection()
