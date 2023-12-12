from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from Entities.Request import Request
from Entities.Response import Response
from Entities.Command import Command
from Entities.Configuration import Configuration

def getPublicKey(req: Request, resp: Response, cmd: Command, config: Configuration):
    if req.headers.get("request-public-key") is not None and config.is_first_time:
        cmd.resp_imm = True
        resp.statusCode = "200"
        resp.statusMessage = resp.code_massage[resp.statusCode]
        resp.body = "Access to this resource requires authentication"

class KeyManager:
    def __init__(self):
        self.pem_pri_key = None
        self.pem_pub_key = None
        self.sym_key = None

    def generate_keys(self):
        # Generate a private key for use in the exchange
        pri_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        # Get the public key from the private key
        pub_key = pri_key.public_key()
        # Serialize the private key to be saved
        self.pem_pri_key = pri_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        # Serialize the public key to be shared with the client
        self.pem_pub_key = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return self.pem_pub_key



# Generate the keys and print them out to check
# private_key, public_key = generate_keys()
# print(f"Private Key:\n{private_key.decode('utf-8')}")
# print(f"Public Key:\n{public_key.decode('utf-8')}")
