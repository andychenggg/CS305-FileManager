import socket
import argparse


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def start(self):
        try:
            # Create a socket (SOCK_STREAM means a TCP socket)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to the host and port
            self.socket.bind((self.host, self.port))

            # Start listening for incoming connections
            self.socket.listen(5)
            print(f'Server started on {self.host}:{self.port}')

            # Keep the server running
            while True:
                # Wait for a connection
                print('Waiting for a connection...')
                connection, client_address = self.socket.accept()

                try:
                    print(f'Connection from {client_address}')

                    # TODO: receive data --> parse as request --> respond
                    while True:
                        data = connection.recv(16)
                        print(f'received "{data}"')
                        if data:
                            print('sending data back to the client')
                            connection.sendall(data)
                        else:
                            print('no more data from', client_address)
                            break




                finally:
                    # Clean up the connection
                    connection.close()

        except Exception as e:
            print(f'An error occurred: {e}')
        finally:
            if self.socket:
                self.socket.close()
                print('Server closed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TCP Server for handling connections.')
    parser.add_argument('-i', '--host', default='localhost', help='Host address')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port number')

    args = parser.parse_args()

    server = Server(args.host, args.port)
    server.start()