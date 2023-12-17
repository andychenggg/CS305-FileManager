from __future__ import annotations

import os
import sys

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class KeyManager:
    def __init__(self):
        self.pem_pri_key = None
        self.pem_pub_key = None
        self.sym_key_bytes: bytes | None = None

    def load_sym_key(self, sym_key_b64):
        encrypted_key_bytes: bytes = base64.b64decode(sym_key_b64)
        private_key = serialization.load_pem_private_key(
            self.pem_pri_key,
            password=None,  # 如果私钥有密码，需要在这里提供
        )
        self.sym_key_bytes: bytes = private_key.decrypt(
            encrypted_key_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print(self.sym_key_bytes, file=sys.stderr)

    def generate_keys(self) -> bytes:
        # Generate a private key for use in the exchange
        pri_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        # Get the public key from the private key
        pub_key = pri_key.public_key()
        # Serialize the private key to be saved
        self.pem_pri_key: bytes = pri_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        # Serialize the public key to be shared with the client
        self.pem_pub_key: bytes = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return self.pem_pub_key

    def encrypt(self, resp_encode_bytes: bytes) -> bytes:
        # AES 需要一个合适长度的密钥，您可能需要根据 symmetric_key 来生成或截断以适应 AES 密钥长度
        # AES 也需要一个初始化向量（IV）
        iv = os.urandom(16)

        # 创建 AES 加密器实例
        cipher = Cipher(algorithms.AES(self.sym_key_bytes), modes.CFB(iv), backend=default_backend())
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
        cipher = Cipher(algorithms.AES(self.sym_key_bytes), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # 解密数据
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

        return decrypted_data

# Generate the keys and print them out to check
# private_key, public_key = generate_keys()
# print(f"Private Key:\n{private_key.decode('utf-8')}")
# print(f"Public Key:\n{public_key.decode('utf-8')}")
