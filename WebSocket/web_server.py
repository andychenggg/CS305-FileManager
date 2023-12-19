import json
import socket
import base64
import hashlib
import struct
import threading
from Functions.Authentication.Authentication import get_cookie_str
from Functions.Authentication.Login import submit_login


class WebSocketServer:
    def __init__(self, host='localhost', port=8081):
        self.port = port
        self.local_host = host
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sockets = []
        self.announcement_list = ['Welcome to the CS305 file server!']

    @staticmethod
    def create_websocket_response(key):
        magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        _hash = hashlib.sha1(key.encode() + magic_string.encode())
        response_key = base64.b64encode(_hash.digest()).strip()
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

    def handshake(self, client_socket):
        request = client_socket.recv(1024).decode()
        headers = self.parse_http_headers(request)
        response = self.create_websocket_response(headers['sec-websocket-key'])
        client_socket.sendall(response.encode())

    def start(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.local_host, self.port))
        self.server_socket.listen(15)
        print(f"Web socket started on {self.local_host}:{self.port}\n")
        command_thread = threading.Thread(target=self.handle_command_input)
        command_thread.start()
        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                print("Web socket Connection from", addr)

                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
                self.client_sockets.append(client_socket)
        except KeyboardInterrupt:
            print("\nWeb socket Server is shutting down.")
        finally:
            for client in self.client_sockets:
                client.close()
            self.server_socket.close()

    # handle command input
    def handle_command_input(self):
        print("Type 'exit' to stop the server.")
        while True:
            cmd = input("Shell>> ")
            parts = cmd.split()
            if not parts:
                print("No command entered. Type 'help' for available commands.")
            else:
                cmd = parts[0].lower()
                if cmd.lower() == 'exit':
                    print("Stopping server...")
                    for client in self.client_sockets:
                        client.close()
                    self.server_socket.close()
                    break
                elif cmd == 'send' and len(parts) > 1:
                    announcement = ' '.join(parts[1:])
                    self.announcement_list.append(announcement)
                    self.broadcast_announcement_list()
                    print(f"Announcement added: {announcement}")
                elif cmd == 'refresh':
                    self.broadcast_refresh()
                    print("Refresh message sent to all clients.")
                elif cmd == 'help':
                    print("Available commands:")
                    print("  send <message>  - Add a new announcement.")
                    print("  delete <index>  - Delete an announcement by its index. Use 'all' to delete all.")
                    print("  list            - List all announcements.")
                    print("  refresh         - Refresh all clients.")
                    print("  exit            - Stop the server.")
                    print("  help            - Show this help message.")
                elif cmd == 'delete' and len(parts) == 2:
                    index = parts[1]
                    if index.lower() == 'all':
                        self.announcement_list.clear()
                        print("All announcements have been deleted.")
                    else:
                        try:
                            idx = int(index) - 1
                            if 0 <= idx < len(self.announcement_list):
                                del self.announcement_list[idx]
                                print(f"Announcement at index {index} has been deleted.")
                            else:
                                print(f"Index {index} is out of range.")
                        except ValueError:
                            print(f"Invalid index: {index}. Please enter a number or 'all'.")
                    self.broadcast_announcement_list()
                elif cmd == 'list':
                    if self.announcement_list:
                        print("Current announcements:")
                        for idx, announcement in enumerate(self.announcement_list, 1):
                            print(f"  {idx}. {announcement}")
                    else:
                        print("There are no current announcements.")
                else:
                    print("Unknown command or incorrect usage. Type 'help' for available commands.")

    def broadcast_announcement_list(self):
        message = json.dumps(self.announcement_list)
        for client in self.client_sockets:
            try:
                response_frame = self.encode_websocket_frame(message)
                client.sendall(response_frame)
            except Exception as e:
                print(f"Error sending message to client: {e}")

    def broadcast_refresh(self):
        message = 'refresh'
        for client in self.client_sockets:
            try:
                response_frame = self.encode_websocket_frame(message)
                client.sendall(response_frame)
            except Exception as e:
                print(f"Error sending refresh message to client: {e}")

    def handle_client(self, client_socket):
        try:
            self.handshake(client_socket)
            self.broadcast_announcement_list()
            while True:
                frame = self.recv_frame(client_socket)
                if not frame:
                    break

                message: str = self.decode_frame(frame)
                print("Received message:", message)

                # if submit login
                if message.startswith('LOGIN '):
                    json_str: str = message[6:]
                    resp: str = submit_login(json_str)
                    response_frame = self.encode_websocket_frame(resp)
                    client_socket.sendall(response_frame)
        except ConnectionAbortedError:
            print("Connection aborted by the client.")
        finally:
            client_socket.close()
            self.client_sockets.remove(client_socket)

    @staticmethod
    def decode_frame(frame):
        decoded = bytearray()
        for i in range(frame['length']):
            decoded.append(frame['data'][i] ^ frame['mask'][i % 4])
        try:
            return decoded.decode('utf-8')
        except UnicodeDecodeError:
            print("Received data cannot be decoded as UTF-8. It might be binary data.")
            return decoded

    @staticmethod
    def recv_frame(client_socket):
        initial_data = client_socket.recv(2)
        if not initial_data:
            return None

        length = initial_data[1] & 0x7F
        if length == 126:
            length = struct.unpack('>H', client_socket.recv(2))[0]
        elif length == 127:
            length = struct.unpack('>Q', client_socket.recv(8))[0]

        mask = client_socket.recv(4)
        encoded = client_socket.recv(length)
        return {'length': length, 'mask': mask, 'data': encoded}

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
