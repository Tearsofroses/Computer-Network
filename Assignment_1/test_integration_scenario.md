# Integration Test Scenario
## P2P File Sharing System - End-to-End Testing

### Test Environment Setup
```
Machine A (192.168.1.5):
- Server (port 65432)
- Client A (peer port 65433)
- PostgreSQL database

Machine B (192.168.1.X):
- Client B (peer port 65433)
```

---

## Integration Test Cases

### **ITC-01: Server Startup and Database Connection**
**Objective:** Verify server starts successfully and connects to database

**Steps:**
1. Start PostgreSQL service
2. Run `python server_ui.py` on Machine A
3. Observe server log

**Expected Result:**
- ✅ Server listening on 0.0.0.0:65432
- ✅ "Connected to PostgreSQL database" message
- ✅ Server UI window displays

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-02: Client A Connection to Server**
**Objective:** Verify local client connects to server

**Steps:**
1. Run `python client_ui.py` on Machine A
2. Observe client status and server log

**Expected Result:**
- ✅ Client status shows "Connected"
- ✅ Server log shows "Client introduced: [hostname]"
- ✅ File sharing service running on port 65433

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-03: Client B Remote Connection**
**Objective:** Verify remote client connects to server

**Steps:**
1. Run `python client_ui.py` on Machine B
2. Check connection status
3. Verify in Server UI that Client B appears in "Connected Clients" list

**Expected Result:**
- ✅ Client B shows "Connected"
- ✅ Server displays Client B hostname and IP
- ✅ Both clients visible in server UI

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-04: Client A Publishes File**
**Objective:** Test file publishing from local client

**Steps:**
1. On Client A:
   - Click "Browse" and select a test file (e.g., `test_document.pdf`)
   - Enter shared name: `mydocument`
   - Click "Publish"
2. Check activity log
3. Verify in database:
   ```sql
   SELECT * FROM client_files WHERE fname = 'mydocument';
   ```

**Expected Result:**
- ✅ Log shows "Published 'mydocument'"
- ✅ Database has entry with Client A's IP and hostname
- ✅ Extension stored correctly (pdf)

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-05: Client B Publishes Same File**
**Objective:** Test multiple peers sharing same filename

**Steps:**
1. On Client B:
   - Select different file with same name
   - Shared name: `mydocument`
   - Click "Publish"
2. Check database for multiple entries

**Expected Result:**
- ✅ Both Client A and B entries exist
- ✅ Different IPs and local paths
- ✅ Same fname value

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-06: Client A Searches for File**
**Objective:** Test file discovery

**Steps:**
1. On Client A:
   - Enter filename: `mydocument`
   - Click "Search"
2. Observe peer list

**Expected Result:**
- ✅ Shows both Client A and Client B as peers
- ✅ Displays correct IPs and hostnames
- ✅ Shows file extension

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-07: Client A Downloads from Client B**
**Objective:** Test peer-to-peer file transfer

**Steps:**
1. On Client A:
   - Search for `mydocument`
   - Select Client B's entry
   - Click "Download Selected"
   - Choose save location
2. Wait for download
3. Verify file integrity

**Expected Result:**
- ✅ Download completes successfully
- ✅ File saved with correct extension
- ✅ Activity log shows "Downloaded: mydocument.pdf"
- ✅ File content is identical to original

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-08: Server Admin Functions - Discover**
**Objective:** Test server's discover peer files feature

**Steps:**
1. In Server UI:
   - Enter Client B's hostname
   - Click "Discover Files"
2. Check server log

**Expected Result:**
- ✅ Server log lists all files published by Client B
- ✅ Shows filenames with extensions

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-09: Server Admin Functions - Ping**
**Objective:** Test server's ping functionality

**Steps:**
1. In Server UI:
   - Enter Client B's hostname
   - Click "Ping"
2. Observe server log

**Expected Result:**
- ✅ Log shows "[hostname] (IP) is ONLINE"
- ✅ Response time displayed

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-10: Client Disconnection Handling**
**Objective:** Verify graceful disconnect

**Steps:**
1. Close Client B application
2. Check Server UI
3. Try to download from Client B on Client A

**Expected Result:**
- ✅ Client B removed from "Connected Clients" list
- ✅ Search still shows Client B (in database)
- ✅ Download fails with connection error
- ✅ No server crash

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-11: Multiple File Types**
**Objective:** Test different file extensions

**Steps:**
1. Publish files with different extensions:
   - `.txt` (text file)
   - `.jpg` (image)
   - `.mp4` (video)
   - `.zip` (archive)
2. Search and download each type

**Expected Result:**
- ✅ All extensions stored correctly
- ✅ Downloaded files retain correct extensions
- ✅ Files open correctly after download

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-12: Large File Transfer**
**Objective:** Test transfer of large files (>100MB)

**Steps:**
1. Client A publishes a 150MB file
2. Client B searches and downloads it
3. Monitor transfer progress

**Expected Result:**
- ✅ File transfers in chunks (4096 bytes)
- ✅ Transfer completes successfully
- ✅ File size matches original
- ✅ MD5 hash matches

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-13: Concurrent Downloads**
**Objective:** Test simultaneous downloads from multiple clients

**Steps:**
1. Have 3 clients connected
2. All search for same file
3. All download simultaneously

**Expected Result:**
- ✅ All downloads complete
- ✅ No conflicts or errors
- ✅ Server remains stable

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-14: File Update Scenario**
**Objective:** Test updating published file

**Steps:**
1. Client A publishes `report.pdf`
2. Client A modifies the file locally
3. Client A publishes again with same name
4. Check database

**Expected Result:**
- ✅ Database shows updated local path
- ✅ Only one entry per (hostname, fname, address)
- ✅ ON CONFLICT clause works

**Actual Result:** [TO BE FILLED DURING TESTING]

---

### **ITC-15: Network Error Handling**
**Objective:** Test behavior on network interruption

**Steps:**
1. Start download from Client B
2. Disconnect Client B's network mid-transfer
3. Observe Client A's behavior

**Expected Result:**
- ✅ Download fails with timeout/connection error
- ✅ Client A shows error in log
- ✅ Partial file handled gracefully
- ✅ No application crash

**Actual Result:** [TO BE FILLED DURING TESTING]

---

## Test Execution Summary

| Test Case | Status | Pass/Fail | Notes |
|-----------|--------|-----------|-------|
| ITC-01 | ⏳ Pending | - | |
| ITC-02 | ⏳ Pending | - | |
| ITC-03 | ⏳ Pending | - | |
| ITC-04 | ⏳ Pending | - | |
| ITC-05 | ⏳ Pending | - | |
| ITC-06 | ⏳ Pending | - | |
| ITC-07 | ⏳ Pending | - | |
| ITC-08 | ⏳ Pending | - | |
| ITC-09 | ⏳ Pending | - | |
| ITC-10 | ⏳ Pending | - | |
| ITC-11 | ⏳ Pending | - | |
| ITC-12 | ⏳ Pending | - | |
| ITC-13 | ⏳ Pending | - | |
| ITC-14 | ⏳ Pending | - | |
| ITC-15 | ⏳ Pending | - | |

**Overall Pass Rate:** 0/15 (0%)

---

## How to Run Integration Tests

### Automated Unit Tests
```bash
# Run server tests
python test_server.py

# Run client tests
python test_client.py

# Run all tests
python -m pytest test_*.py -v
```

### Manual Integration Tests
1. Follow each ITC scenario step-by-step
2. Record actual results in the table
3. Take screenshots for documentation
4. Update pass/fail status

---

## Test Data Files (Create these for testing)

1. `test_document.pdf` - 2MB PDF file
2. `test_image.jpg` - 5MB image
3. `test_video.mp4` - 50MB video
4. `test_large.zip` - 150MB archive
5. `test_text.txt` - 1KB text file

---

## Performance Metrics to Collect

- Average file discovery time
- File transfer speed (MB/s)
- Server response time for publish/fetch
- Maximum concurrent clients tested
- Database query performance
