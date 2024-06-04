# BitTorrent Network

This project implements a simple BitTorrent-like network using Python. The implementation includes a Peer class to handle file sharing among peers and a Tracker class to manage peer connections and file requests.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Classes and Methods](#classes-and-methods)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The BitTorrent Network project aims to simulate a basic peer-to-peer (P2P) file sharing system similar to the BitTorrent protocol. The system includes peers that can request and share files and a tracker that coordinates these activities.

## Features

- Peer-to-peer file sharing
- Tracker for managing peer connections
- Logging of file requests and sharing activities
- Simple and extensible codebase

## Installation

To run this project, you need to have Python installed on your system. You can install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Tracker

To start the tracker, run the `Tracker.py` script:

```bash
python BItTorrent/Tracker.py <tracker_ip>:<tracker_port>
```

### Running a Peer

To start a peer, run the `Peer_class.py` script with the required arguments:

```bash
python BItTorrent/Peer_class.py <command> <filename> <tracker_address> <listen_address>
```

- `<command>`: The command to execute (`share` or `get`).
- `<filename>`: The name of the file to share or get.
- `<tracker_address>`: The address of the tracker.
- `<listen_address>`: The address to listen for incoming connections.

## Classes and Methods

### Peer Class

- `__init__(self, command, file_path, tracker_address, listen_address)`: Initializes the peer with the specified command, file path, tracker address, and listen address.
- `run(self)`: Executes the specified command (`get` or `share`).
- `download_file(self)`: Downloads a file from another peer.
- `share_file(self)`: Shares a file with another peer.
- `handle_client(self, reader, writer)`: Handles incoming client connections.

### Tracker Class

- `ping_pong(filename, address)`: Handles the ping-pong mechanism for file requests.
- `run_server(addr, port)`: Starts the tracker server.
- `send_counter(self, addr)`: Sends the count of active peers.
- `connection_made(self, transport)`: Handles new connections.
- `datagram_received(self, data, addr)`: Handles received datagrams.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
