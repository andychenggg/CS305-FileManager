import socket
import argparse
import threading
from WebSocket.web_server import WebSocketServer
from Functions.PersistentConn import persistent_connection_process
from Functions.Authentication.Authentication import authorize
from Functions.Download.viewFile import viewFile
from Functions.UplAndDel.UplAndDel import uplAndDel
from Entities.Request import Request
from Entities.Response import Response
from Entities.Command import Command
from Entities.Configuration import Configuration


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.function_chain = [
            persistent_connection_process,
            authorize,
            viewFile,
            uplAndDel
        ]
        self.web_server = None

    def start(self):
        try:
            # Create a WebSocket server
            self.web_server = WebSocketServer(self.host, self.port + 1)
            web_socket_thread = threading.Thread(target=self.web_server.start)
            web_socket_thread.start()
            # Create a socket (SOCK_STREAM means a TCP socket)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to the host and port
            self.socket.bind((self.host, self.port))

            # Start listening for incoming connections
            self.socket.listen(100)
            print(f'HTTP Server started on {self.host}:{self.port}')

            # Keep the server running
            thread_index = 0
            while True:
                print('HTTP Waiting for a connection...')
                connection, client_address = self.socket.accept()
                client_thread = threading.Thread(
                    target=self.conn_thread,
                    args=(connection, client_address, thread_index)
                )
                thread_index += 1
                client_thread.start()

        except Exception as e:
            print(f'An error occurred: {e}')
        finally:
            if self.socket:
                self.socket.close()
                print('Server closed')

    def conn_thread(self, conn: socket, address: tuple, index: int):
        # try:
        print(f'Connection from {address}, thread {index}')
        # Keep the connection open to handle multiple requests
        config = Configuration(index)
        while True:
            data = conn.recv(4096)
            if not data:
                break

            # print(f"data from thread {index}")
            print(data.decode('utf-8'))
            resp, cmd = self.handle(data, config)
            if cmd.chunked:
                conn.sendall(resp_encode(resp))
                send_chunk_file(resp, conn)
            else:
                conn.sendall(resp_encode(resp))
            # Check if the client requests to refresh the page
            if cmd.refresh:
                self.web_server.broadcast_refresh()
                break
            # Check if the client requests to close the connection
            if cmd.close_conn:
                break

    # except Exception as e:
    #     print(f'An error occurred in thread {index}: {e}')
    # finally:
    #     # Close the connection
    #     conn.close()
    #     print(f'thread {index}: Connection closed.')

    def handle(self, origin_str: bytes, config: Configuration) -> (Response, Command):
        req = Request(origin_str.decode('utf-8'))
        print('req path', req.path)
        resp = Response()
        cmd = Command()
        for i in range(3):
            if i < 2:
                func = self.function_chain[i]
            else:
                if req.path.startswith('/upload') or req.path.startswith('/delete'):
                    func = self.function_chain[3]
                else:
                    print('diao yong le download')
                    func = self.function_chain[2]
            func(req, resp, cmd, config)
            if cmd.close_conn or cmd.resp_imm:
                return resp, cmd

        # print(resp.parse_resp_to_str())
        return resp, cmd


def send_chunk_file(resp: Response, conn: socket):
    with open(resp.chunk_path, 'rb') as file:
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            chunk_len = f"{len(chunk):x}".encode('utf-8')
            print('chunked len', chunk_len)
            conn.sendall(chunk_len + b'\r\n' + chunk + b'\r\n')
        conn.sendall(b'0\r\n\r\n')


def resp_encode(resp: Response) -> bytes:
    if resp.file:
        return resp.parse_resp_to_str().encode("utf-8") + resp.file_content
    else:
        return resp.parse_resp_to_str().encode("utf-8") + resp.body.encode("utf-8")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TCP Server for handling connections.')
    parser.add_argument('-i', '--host', default='localhost', help='Host address')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port number')

    args = parser.parse_args()

    server = Server(args.host, args.port)
    server_thread = threading.Thread(target=server.start)
    server_thread.start()
