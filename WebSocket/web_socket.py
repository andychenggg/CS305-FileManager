import socket
import base64
import hashlib
import struct


# 重新定义之前的一些函数

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


def parse_http_headers(header_string):
    headers = {}
    lines = header_string.splitlines()
    for line in lines:
        parts = line.partition(": ")
        if len(parts) == 3:
            headers[parts[0].lower()] = parts[2]
    return headers


def handshake(client_socket):
    request = client_socket.recv(1024).decode()
    headers = parse_http_headers(request)
    response = create_websocket_response(headers['sec-websocket-key'])
    client_socket.send(response.encode())


def start_websocket_server(port=8765):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', port))
    server_socket.listen(5)
    print("WebSocket server is running on port", port)

    client_socket, addr = server_socket.accept()
    print("Connection from", addr)

    handshake(client_socket)

    return server_socket, client_socket


# 新的函数用于编码 WebSocket 帧

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


def start_websocket_server_with_input(port=8765):
    server_socket, client_socket = start_websocket_server(port)

    try:
        while True:
            data = input("Enter message to send: ")
            if data.lower() == 'exit':
                break
            frame = encode_websocket_frame(data)
            client_socket.sendall(frame)
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        client_socket.close()
        server_socket.close()


start_websocket_server_with_input()
