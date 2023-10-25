import asyncio
import random
import socket
from collections import defaultdict
import sys

peers = defaultdict(lambda: set())
request_logs  = {}


async def ping_pong(filename, address):
    while True:
        # print("checking if server", address, "is alive for", filename)
        try:
            server_address = address.split(":")
            server_address[1] = int(server_address[1])
            server_address = tuple(server_address)

            # Create a TCP/IP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect the socket to the server's address and port
            sock.connect(server_address)

            # Send a request for the file you want to receive
            file_request = 'ping'
            sock.sendall(file_request.encode())

            data = sock.recv(1024)

            # Close the socket
            sock.close()

            if data.decode() != 'pong':
                raise Exception('PONG_FAILED')

            # print('server', address, 'for file', filename, 'is alive')
        except Exception as e:
            peers[filename].remove(address)
            print('pinging server', address, 'for file', filename, 'failed:', e)
            return
        await asyncio.sleep(5)



class CounterUDPServer:
    def init(self):
        self.counter = 0

    async def send_counter(self, addr):
        self.counter += 1
        next_value = self.counter
        await asyncio.sleep(0.5)
        print(f"sending {next_value} to {addr}")
        self.transport.sendto(str(next_value).encode(), addr)

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print(f"got {data.decode()} from {addr}")

        req_data = data.decode().strip().split()
        req = req_data[0]
        filename = req_data[1]

        if req == "get":
            if (len(peers[filename]) == 0):
                self.transport.sendto('NO_PEER'.encode(), addr)
                request_logs[addr] = f"{data.decode()} \n response : is getting this {filename} \n this file hasn't been shared"
            else:
                random_index = random.randint(0, len(peers[filename]) - 1)
                self.transport.sendto(
                    f'{list(peers[filename])[random_index]}'.encode(), addr)
                request_logs[addr] = f"{data.decode()} \n response : is getting this {filename} \n peers that have this file : {peers[filename]}"
        elif req == 'share':
            peers[filename].add(req_data[2])
            bg_ping_pong = asyncio.create_task(
                ping_pong(filename, req_data[2]))
            request_logs[addr] = f"{data.decode()} \n response : is sharing this {filename} \n peers that have this file : {peers[filename]}"
            self.transport.sendto(f'File {filename} shared successfully'.encode(), addr)
        else:
            self.transport.sendto('INVALID_METHOD'.encode(), addr)



async def run_server(addr, port):
    asyncio.create_task(read_user_input())
    loop = asyncio.get_running_loop()
    await loop.create_datagram_endpoint(
        lambda: CounterUDPServer(),
        local_addr=(addr, port)
    )
    print(f"Listening on {addr}:{port}")
    while True:
        await asyncio.sleep(3600)


async def read_user_input():
    while True:
        user_input = await asyncio.to_thread(input)
        if user_input == "request logs":
            for peer in  request_logs:
                print(f"{peer} : {request_logs[peer]}")
        elif user_input == "file_logs -all":
            for k, v in peers.items():
                print(f"{k} : {v}")
        elif user_input.startswith("file_logs>"):
            _ , file_name = user_input.split(">")
            if peers[file_name] :
                print(peers[file_name])
            else:
                print("This file doesn't exist")
        else:
            print("Invalid command")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py ip_address:port_number")
        exit(1)

    try:
        address, port = sys.argv[1].split(":")
        asyncio.run(run_server(address,port))

    except ValueError:
        print("Invalid address or port number. Please use the format ip_address:port_number")
        exit(1) 

