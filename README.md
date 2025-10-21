<div align="center">
  
**Vietnam National University, Ho Chi Minh City**  
**University of Technology**  
**Faculty of Computer Science and Engineering**

[![HCMUT Logo](https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/HCMUT_official_logo.png/238px-HCMUT_official_logo.png)](https://www.hcmut.edu.vn/vi)

**Computer Networks / Semester 231**  
**Group 1**

</div>

---

# 🧠 Project Repository: Computer Networks Assignments

## Lecturer: [Your Lecturer’s Name]
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
Computer-Networks/
├── Assignment1_FileSharing/
│ ├── client/
│ ├── server/
│ ├── report/
│ ├── docs/
│ └── README.md
├── Assignment2_[ProjectName]/
│ ├── src/
│ ├── report/
│ └── README.md
└── main_README.md ← (this file)

---

## 🧩 Assignment 1 – File Sharing Network Application

### 🎯 Objective
Develop a **simple file-sharing system** where:
- A **central server** tracks connected clients and the files they share.
- Clients **publish** files to the server and **fetch** files from peers directly.
- Transfers between clients are **peer-to-peer (P2P)** using the **TCP protocol**.
- Multithreading supports multiple simultaneous downloads.

### ⚙️ Features
- Custom **application-layer protocol**  
- **Server commands**: `discover`, `ping`  
- **Client commands**: `publish`, `fetch`  
- **Concurrent downloads** via threads  
- Simple **CLI-based shell** for interaction  

### 🧱 Architecture
 ┌──────────────┐
     │    Server    │
     │ (File Index) │
     └──────┬───────┘
            │
    ┌───────┴────────┐
    │     Internet    │
    └───────┬────────┘
┌───────────┴───────────┐
│                       │
┌────────┐ ┌────────┐
│Client A│ <──P2P──> │Client B│
└────────┘ └────────┘

### 🧾 Deliverables
- Protocol design document  
- Source code (client & server)  
- System architecture diagrams  
- Performance validation & test report  

---

## 🧮 Assignment 2 – [Your Project Title]
*(e.g., “Multi-threaded Web Server” / “Chat Application using TCP/UDP”)*

### 🎯 Objective
Build a **more advanced networked system** focusing on:
- Reliability  
- Concurrency  
- Application-layer protocol implementation  

### ⚙️ Features
- [Feature 1 – short description]  
- [Feature 2 – short description]  
- [Feature 3 – short description]  

### 🧱 Architecture

### 🧾 Deliverables
- Detailed design report  
- Source code & documentation  
- Performance and stress tests  
- Role assignment & contribution summary  

---

## 🧪 Testing & Validation
- Tested in a **LAN** and **Internet** environment using **Python sockets (TCP)**.  
- Supports multiple concurrent clients.  
- Verified protocol correctness and packet flow via **Wireshark**.  

---

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

- **Testing Tools**  
  <img src="https://upload.wikimedia.org/wikipedia/commons/d/d5/Wireshark_icon.svg" width=40px/>  
  Wireshark for packet inspection 
