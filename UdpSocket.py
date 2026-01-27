import socket


class UdpSocket:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 58764
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
    def send(self, message, address):
        self.sock.sendto(message.encode(), address)
    def receive(self, buffer_size=1024):
        data, addr = self.sock.recvfrom(buffer_size)
        return data.decode(), addr
    def close(self):
        self.sock.close()