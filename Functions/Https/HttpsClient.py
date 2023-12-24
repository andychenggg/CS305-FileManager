import argparse
import base64
import sys

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
        self.symmetric_key: bytes = b''

    def connect_to_server(self):
        self.socket.connect((self.server_host, self.server_port))
        print(f"Connected to server at {self.server_host}:{self.server_port}\n")

    def request_public_key(self, prt: bool = True):
        self.socket.sendall(b'GET / HTTP/1.1\r\nrequest-public-key: 1\r\n\r\n')
        public_key_pem = self.socket.recv(4096)
        public_key = load_pem_public_key(public_key_pem, backend=default_backend())
        if prt:
            print(f"Received public key from server: \n{public_key_pem}\n")
        return public_key

    def generate_symmetric_key(self, prt: bool = True):
        # Generate a random symmetric key for AES
        self.symmetric_key: bytes = os.urandom(32)
        if prt:
            print("Symmetric key generated: \n", self.symmetric_key, '\n')

    def encrypt_and_send_symmetric_key(self, public_key, prt: bool = True):
        # Encrypt the symmetric key with the server's public key
        encrypted_key_bytes: bytes = public_key.encrypt(
            self.symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        if prt:
            print(f"Encrypted symmetric key: \n{encrypted_key_bytes}\n")
        encrypted_key: str = base64.b64encode(encrypted_key_bytes).decode('utf-8')
        request = f'POST / HTTP/1.1\r\ngive-symmetric-key: {encrypted_key}\r\n\r\n'
        # Send the encrypted symmetric key to the server
        self.socket.sendall(request.encode('utf-8'))
        resp = self.socket.recv(4096).decode()
        if resp.split('\r\n')[0].split(' ')[1] != '200':
            print(resp, file=sys.stderr)
            raise socket.error
        print("Encrypted symmetric key sent to server\n")

    def encrypt(self, resp_encode_bytes: bytes) -> bytes:
        # AES 需要一个合适长度的密钥，您可能需要根据 symmetric_key 来生成或截断以适应 AES 密钥长度
        # AES 也需要一个初始化向量（IV）
        iv = os.urandom(16)

        # 创建 AES 加密器实例
        cipher = Cipher(algorithms.AES(self.symmetric_key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # 加密数据
        encrypted_data = encryptor.update(resp_encode_bytes) + encryptor.finalize()
        encrypted_pack = iv + encrypted_data

        # Base64 编码
        encoded_encrypted_pack = base64.b64encode(encrypted_pack)

        return encoded_encrypted_pack

    def decrypt(self, req_b64_bytes: bytes) -> bytes:
        # Base64 解码
        encrypted_package = base64.b64decode(req_b64_bytes)
        iv = encrypted_package[:16]
        encrypted_data = encrypted_package[16:]

        # 创建 AES 解密器实例
        cipher = Cipher(algorithms.AES(self.symmetric_key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # 解密数据
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        return decrypted_data

    def close_connection(self):
        self.socket.close()
        print("Connection closed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TCP Server for handling connections.')
    parser.add_argument('-i', '--host', default='localhost', help='Host address')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port number')

    args = parser.parse_args()

    # Initialize the client
    client = EncryptedClient(args.host, args.port)

    # Connect to the server
    client.connect_to_server()

    # Request the public key from the server
    server_public_key = client.request_public_key()

    # Generate a symmetric key
    client.generate_symmetric_key()

    # Encrypt the symmetric key with the server's public key and send it to the server
    client.encrypt_and_send_symmetric_key(server_public_key)

    http_req = ("GET /?sustech-http=1 HTTP/1.1\r\n"
                "Accept: application/json\r\n"
                "connection: keep-alive\r\n"
                "Authorization: Basic dXNlcjE6cGFzczE=\r\n\r\n")

    client.socket.sendall(http_req.encode())

    resp = client.socket.recv(4096)
    body = resp.decode().split('\r\n\r\n')[-1]
    print(f"Original body: \n{body}\n")
    print("Decrypted body: \n", client.decrypt(body.encode()).decode(), '\n')

    # Close the connection
    client.close_connection()
