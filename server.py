import socket
import argparse
import threading

from Functions.PersistentConn import persistent_connection_process
from Functions.Authentication.Authentication import authorize
from html_package.HTMLManager import HTMLManager
from Entities.Request import Request
from Entities.Response import Response
from Entities.Command import Command
from Entities.Configuration import Configuration


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.html = HTMLManager()
        self.function_chain = [
            persistent_connection_process,
            authorize
        ]

    def start(self):
        try:
            # Create a socket (SOCK_STREAM means a TCP socket)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to the host and port
            self.socket.bind((self.host, self.port))

            # Start listening for incoming connections
            self.socket.listen(100)
            print(f'Server started on {self.host}:{self.port}')

            # Keep the server running
            thread_index = 0
            while True:
                print('Waiting for a connection...')
                connection, client_address = self.socket.accept()
                client_thread = threading.Thread(target=self.conn_thread, args=(connection, client_address, thread_index))
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
            config = Configuration()
            while True:
                data = conn.recv(4096)
                if not data:
                    break

                print(f"data from thread {index}")
                print(data.decode('utf-8'))

                resp, cmd = self.handle(data, config)
                conn.sendall(resp)
                # Check if the client requests to close the connection
                if cmd.close_conn:
                    break

        # except Exception as e:
        #     print(f'An error occurred in thread {index}: {e}')
        # finally:
        #     # Close the connection
        #     conn.close()
        #     print(f'thread {index}: Connection closed.')

    def handle(self, origin_str: bytes, config: Configuration) -> (bytes, Command):
        req = Request(origin_str.decode('utf-8'))
        resp = Response()
        cmd = Command()
        for func in self.function_chain:
            func(req, resp, cmd, config)
            if cmd.close_conn or cmd.resp_imm:
                return resp.parse_resp_to_str().encode("utf-8"), cmd
        print(resp.parse_resp_to_str())
        return resp.parse_resp_to_str().encode("utf-8"), cmd


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TCP Server for handling connections.')
    parser.add_argument('-i', '--host', default='localhost', help='Host address')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port number')

    args = parser.parse_args()

    server = Server(args.host, args.port)
    server.start()
