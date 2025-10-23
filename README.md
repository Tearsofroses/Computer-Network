<div align="center">
  
**Vietnam National University, Ho Chi Minh City**  
**University of Technology**  
**Faculty of Computer Science and Engineering**

[![HCMUT Logo](https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/HCMUT_official_logo.png/238px-HCMUT_official_logo.png)](https://www.hcmut.edu.vn/vi)

**Computer Networks / Semester 251**  
**Group 1**

</div>

---

# 🧠 Project Repository: Computer Networks Assignments

## Lecturer: [Nguyễn Thành Nhân]
## Team Members

| No. | Name                  | Student ID | Class | Email                              |
| :-: | --------------------- | :--------: | :---: | ---------------------------------- |
|  1  | Nguyễn Duy Thành      | 2353101    | CC06  | thanh.nguyen09012005@hcmut.edu.vn  |
|  2  | Đặng Sinh Hùng        | 2352420    | CC06  | hung.dang2109@hcmut.edu.vn         |
|  3  | Châu Kiến Toàn        | 2353192    | CC06  | toan.chaukien@hcmut.edu.vn         |
|  4  | Phạm Quang Tiến Thành | 2353103    | CC06  | thanh.pham04052005@hcmut.edu.vn    |

---

## 📚 Overview

This repository contains two major assignments for the **Computer Networks** course at HCMUT.  
Each project explores different aspects of **TCP/IP-based communication**, **socket programming**, and **network protocol design**.

---

## 📦 Repository Structure
```markdown
## 📦 Repository Structure
```text
Computer-Networks/
├── Assignment_1/
│   ├── client.py
│   ├── client_ui.py
│   ├── server.py
│   ├── server_ui.py
├── Assignment_2/
└── README.md   ← (this file)
```

---

## Assignment 1 – File Sharing Network Application

A lightweight, GUI-driven peer-to-peer file sharing system built with Python, using a central server for coordination and direct peer-to-peer transfers for file exchange. No cloud. No middlemen. Just your network.

### Features
Central Server tracks which peers have which files
Clients publish local files under custom names
Search & Download files from any online peer
Tkinter GUI for both Server and Client (no command-line required)
PostgreSQL backend for persistent file metadata
Direct P2P transfer on port 65433 (bypasses server for actual data)
Admin console in server: discover <host>, ping <host>
Graceful shutdown support

### Architecture
```markdown
[Client A] ←→ [Central Server] ←→ [Client B]
     ↓              ↑              ↓
  (65433)        (65432)        (65433)
     ↓              ↑              ↓
[Local Files]   [PostgreSQL]   [Local Files]
```
Server runs on 0.0.0.0:65432
Clients run a local service on 0.0.0.0:65433
File metadata stored in PostgreSQL
File content transferred directly between peers

### Files Overview
- Protocol design document  
- Source code (client & server)  
- System architecture diagrams  
- Performance validation & test report  

---
## Prerequisites

Python 3.8+
PostgreSQL server running locally
psycopg2 Python package

## Database Setup
CREATE DATABASE filesharing;

\c filesharing

CREATE TABLE client_files (
    id SERIAL PRIMARY KEY,
    lname TEXT NOT NULL,        -- local path on peer
    fname TEXT NOT NULL,        -- shared name
    extension TEXT,             -- file extension (without dot)
    hostname TEXT NOT NULL,
    address INET NOT NULL,
    UNIQUE(address, fname, hostname)
);

## How to run 
1. Start the server
python server_ui.py
- Opens a GUI window
- Shows connected clients
- Logs all activity
- Use Admin Commands to Discover Files or Ping a host

2. Start Clients (on same network)
python client_ui.py
- Publish a file:
  Click Browse → select a file
  Enter a Shared Name (e.g., myphoto)
  Click Publish
- Download a file:
  Enter the Shared Name → click Search
  Select a peer from the list
  Click Download Selected → choose save location

## Network Configuration
Change the server IP in client_ui.py to your machine running server IP:
SERVER_IP = 'your.server.ip.here'

## 🧰 Languages & Tools

- **Programming Language**  
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width=40px/>

- **Networking & Threading**  
  <img src="https://cdn-icons-png.flaticon.com/512/919/919854.png" width=40px/>  
  Python `socket` & `threading` libraries

- **Version Control**  
  <img src="https://cdn1.iconfinder.com/data/icons/logotypes/32/github-256.png" width=30px/>

- **Documentation & Reporting**  
  <img src="https://images.ctfassets.net/nrgyaltdicpt/6gsvc5Ogjmu04I4Miu0uGg/cb1d4391717d2ab8d5e42ede6fb0eef1/overleaf_wide_colour_light_bg.png" width=70px/>
