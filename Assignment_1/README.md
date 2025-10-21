# File Sharing Network Application

Course: Computer Networks Semester 251
Assignment: 1 – Develop a Network Application
Weight: 15% of total course grade

## Objective

The goal of this assignment is to design and implement a simple file-sharing application using the TCP/IP protocol stack.
Students are required to define their own application-layer communication protocol and implement both client and server components.

## Application Overview

This application implements a centralized file-tracking system with peer-to-peer file transfer between clients.

## System Components

### Central Server

Maintains a list of connected clients and the files stored on each client.

Responds to client requests for file locations.

Provides basic management commands for monitoring clients.

### Client

Registers available local files with the server.

Requests files from other clients via server coordination.

Fetches files directly from peer clients (P2P download).

Supports multiple simultaneous transfers using multithreading.

## Requirements
- Python 3
- PosgreSQL on the SERVER machine.
- Python library 'pyscopg2'

## Installation
Installation from source is straightforward:
```
$ git clone https://github.com/Tearsofroses/Computer-Network.git
$ cd Assigment_1
```

## Usage
1. Run the central server with PosgreSQL installed on the machine.

2. Run the client with the same SERVER_HOST setting in the client.py file as the IP configuration of the server.

## Demo

