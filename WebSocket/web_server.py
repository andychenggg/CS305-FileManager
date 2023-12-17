import socket
import base64
import hashlib
import struct


class WebSocketServer:
    def __init__(self, port=8765):
        self.port = port
        self.server_socket = None
        self.client_socket = None

    @staticmethod
    def create_websocket_response(key):
        magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        hash = hashlib.sha1(key.encode() + magic_string.encode())
        response_key = base64.b64encode(hash.digest()).strip()
        response = (
            'HTTP/1.1 101 Switching Protocols\r\n'
            'Upgrade: websocket\r\n'
            'Connection: Upgrade\r\n'
            'Sec-WebSocket-Accept: ' + response_key.decode() + '\r\n\r\n'
        )
        return response

    @staticmethod
    def parse_http_headers(header_string):
        headers = {}
        lines = header_string.splitlines()
        for line in lines:
            parts = line.partition(": ")
            if len(parts) == 3:
                headers[parts[0].lower()] = parts[2]
        return headers

    def handshake(self):
        request = self.client_socket.recv(1024).decode()
        headers = self.parse_http_headers(request)
        response = self.create_websocket_response(headers['sec-websocket-key'])
        self.client_socket.send(response.encode())

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(5)
        print("WebSocket server is running on port", self.port)

        self.client_socket, addr = self.server_socket.accept()
        print("Connection from", addr)

        self.handshake()
        self.run()

    def run(self):
        try:
            while True:
                cmd = input("Enter command (list/exit): ")
                if cmd.lower() == 'exit':
                    break
                elif cmd.lower() == 'list':
                    # 这里可以添加列出某些信息的代码
                    response = "Listing items..."
                else:
                    response = f"Unknown command: {cmd}"

                frame = self.encode_websocket_frame(response)
                self.client_socket.sendall(frame)
        except KeyboardInterrupt:
            print("\nServer is shutting down.")
        finally:
            self.client_socket.close()
            self.server_socket.close()

    @staticmethod
    def encode_websocket_frame(data):
        opcode = 0x1  # 文本帧
        data_bytes = data.encode()
        frame_header = bytearray()
        frame_header.append(0x80 | opcode)
        length = len(data_bytes)
        if length <= 125:
            frame_header.append(length)
        elif length <= 65535:
            frame_header.append(126)
            frame_header.extend(struct.pack('>H', length))
        else:
            frame_header.append(127)
            frame_header.extend(struct.pack('>Q', length))
        frame = frame_header + data_bytes
        return frame


if __name__ == "__main__":
    server = WebSocketServer(port=8765)
    server.start()
