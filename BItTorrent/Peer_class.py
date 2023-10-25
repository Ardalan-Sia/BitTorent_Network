import socket
import argparse
import asyncio
import os

class Peer:
    def __init__(self, command, file_path, tracker_address, listen_address):
        self.command = command
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.tracker_address = tracker_address
        self.listen_address = listen_address
        self.UDP_IP, self.UDP_PORT = tracker_address.split(":")
        self.UDP_PORT = int(self.UDP_PORT)
        self.request_logs  = []



    def run(self):
        if self.command == "get":
            self.download_file()
            asyncio.run(self.share_file())

        elif self.command == "share":
            asyncio.run(self.share_file())
        else:
            print("Invalid mode")
            exit(-1)

    def download_file(self):
        message = f'get {self.file_name}'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (self.UDP_IP, self.UDP_PORT))

        sock.settimeout(5)
        try:
            data, addr = sock.recvfrom(1024)
            print("Received response:", data.decode())
        except socket.timeout:
            print("No response received within 5 seconds.")
            exit(-1)

        if data.decode() == "NO_PEER":
            print("No peer for the file")
            exit(-1)
        
        print("Downloading file from",  data.decode())
        server_address = data.decode().split(":")
        server_address[1] = int(server_address[1])
        server_address = tuple(server_address)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)

        sock.sendall(self.file_name.encode())

        file_data = b''
        while True:
            data = sock.recv(1024)
            if not data:
                break
            file_data += data

        directory = f"{str(self.listen_address).split(':')[1]}"
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(f"{directory}/{self.file_name}", 'wb') as f:
            f.write(file_data)

        sock.close()
        self.request_logs.append(f"received response : {data.decode()}") 
        self.request_logs.append('file downloaded successfully') 

    async def handle_client(self, reader, writer):
        file_request = await reader.read(1024)
        file_request = file_request.decode().strip()

        if file_request != 'ping':
            with open(file_request, 'rb') as f:
                file_data = f.read()
        else:
            file_data = 'pong'.encode()

        writer.write(file_data)
        await writer.drain()

        writer.close()

    async def share_file(self):
        message = f'share {self.file_name} {self.listen_address}'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (self.UDP_IP, self.UDP_PORT))

        sock.settimeout(5)
        try:
            data, addr = sock.recvfrom(1024)
            print("@")
            # print("Received response:", data.decode())
            self.request_logs.append(f"received response : {data.decode()}") 
        except socket.timeout:
            print("No response received within 5 seconds.")
            exit(-1)
            

        server_address = self.listen_address.split(":")
        server_address[1] = int(server_address[1])
        server_address = tuple(server_address)

        asyncio.create_task(read_user_input(self))
        server = await asyncio.start_server(self.handle_client, *server_address)

        async with server:
            await server.serve_forever()


async def read_user_input(self):
    while True:
        user_input = await asyncio.to_thread(input)
        if user_input == "request logs":
            print(self.request_logs)
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="command (share|get)")
    parser.add_argument("filename", help="file to share")
    parser.add_argument("tracker_address", help="tracker address to get network data")
    parser.add_argument("listen_address", help="address to bind listener")
    args = parser.parse_args()

    peer = Peer(args.command, args.filename, args.tracker_address, args.listen_address)
    peer.run()
