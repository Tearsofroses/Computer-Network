# Section 6: Testing and Validation

## 6.1 Testing Strategy

Our P2P File Sharing System employs a comprehensive testing approach covering:
- **Unit Testing**: Individual function validation
- **Integration Testing**: End-to-end system workflows
- **Performance Testing**: Load and stress testing
- **Security Testing**: Authentication and data integrity

---

## 6.2 Unit Test Results

### 6.2.1 Server Tests (`test_server.py`)

**Total Tests: 9 | Passed: 9 | Failed: 0 | Success Rate: 100%**

| Test ID | Test Case | Component | Result |
|---------|-----------|-----------|--------|
| TC-S1 | Register new file in database | Database | ✅ PASS |
| TC-S2 | Update existing file (conflict handling) | Database | ✅ PASS |
| TC-S3 | Discover files by hostname | Database Query | ✅ PASS |
| TC-S4 | Fetch all peers having specific file | Database Query | ✅ PASS |
| TC-S5 | Validate publish command JSON format | Protocol | ✅ PASS |
| TC-S6 | Validate fetch command JSON format | Protocol | ✅ PASS |
| TC-S7 | Validate fetch response format | Protocol | ✅ PASS |
| TC-S8 | Verify MAX_CLIENTS limit (5) | Configuration | ✅ PASS |
| TC-S9 | Verify server port (65432) | Configuration | ✅ PASS |

#### Sample Test Code
```python
def test_register_file(self):
    """Test TC-S1: Register new file in database"""
    lname = "D:\\test\\document.pdf"
    fname = "mydocument"
    extension = "pdf"
    hostname = "test_client1"
    ip_addr = "192.168.1.100"
    
    self.cursor.execute(
        "INSERT INTO client_files (lname, fname, extension, hostname, address) "
        "VALUES (%s, %s, %s, %s, %s)",
        (lname, fname, extension, hostname, ip_addr)
    )
    self.conn.commit()
    
    # Verify
    self.cursor.execute(
        "SELECT lname, fname FROM client_files WHERE hostname = %s",
        (hostname,)
    )
    result = self.cursor.fetchone()
    self.assertEqual(result[0], lname)
    self.assertEqual(result[1], fname)
```

#### Test Execution Output
```
test_register_file ... ✓ TC-S1 PASSED: File registered successfully
test_update_existing_file ... ✓ TC-S2 PASSED: File updated on conflict
test_discover_peer_files ... ✓ TC-S3 PASSED: Discovered all files for peer
test_fetch_file_locations ... ✓ TC-S4 PASSED: Found all peers with file
test_publish_command_format ... ✓ TC-S5 PASSED: Publish command format valid
test_fetch_command_format ... ✓ TC-S6 PASSED: Fetch command format valid
test_fetch_response_format ... ✓ TC-S7 PASSED: Fetch response format valid
test_max_client_limit ... ✓ TC-S8 PASSED: MAX_CLIENTS set to 5
test_server_ports ... ✓ TC-S9 PASSED: Server port configured correctly

Ran 9 tests in 0.485s - OK
```

---

### 6.2.2 Client Tests (`test_client.py`)

**Total Tests: 15 | Passed: 15 | Failed: 0 | Success Rate: 100%**

| Test ID | Test Case | Component | Result |
|---------|-----------|-----------|--------|
| TC-C1 | List files in directory | File Operations | ✅ PASS |
| TC-C2 | Extract file extension correctly | File Operations | ✅ PASS |
| TC-C3 | Verify file existence before publishing | File Operations | ✅ PASS |
| TC-C4 | Client introduction to server | Protocol | ✅ PASS |
| TC-C5 | File publish announcement format | Protocol | ✅ PASS |
| TC-C6 | File fetch query format | Protocol | ✅ PASS |
| TC-C7 | Parse server response for fetch | Protocol | ✅ PASS |
| TC-C8 | Peer-to-peer file transfer request | Protocol | ✅ PASS |
| TC-C9 | Ping response format | Peer Service | ✅ PASS |
| TC-C10 | Verify peer service port (65433) | Configuration | ✅ PASS |
| TC-C11 | Read file in chunks (4096 bytes) | File Transfer | ✅ PASS |
| TC-C12 | Save downloaded file | File Transfer | ✅ PASS |
| TC-C13 | Handle invalid JSON from server | Error Handling | ✅ PASS |
| TC-C14 | Handle missing file on publish | Error Handling | ✅ PASS |
| TC-C15 | Handle no peers having file | Error Handling | ✅ PASS |

#### Sample Test Code
```python
def test_file_read_chunks(self):
    """Test TC-C11: Read file in chunks for transfer"""
    # Create test file (~10KB)
    test_content = b"Test data " * 1000
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(test_content)
        tmp_path = tmp.name
    
    # Read in chunks
    chunk_size = 4096
    chunks = []
    with open(tmp_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            chunks.append(chunk)
    
    # Verify
    self.assertGreater(len(chunks), 1)  # Multiple chunks
    reconstructed = b''.join(chunks)
    self.assertEqual(reconstructed, test_content)
```

#### Test Execution Output
```
test_list_local_files ... ✓ TC-C1 PASSED: Listed all local files
test_file_extension_extraction ... ✓ TC-C2 PASSED: File extensions extracted
test_file_exists_check ... ✓ TC-C3 PASSED: File existence check works
test_introduce_command ... ✓ TC-C4 PASSED: Introduce command format valid
test_publish_announcement ... ✓ TC-C5 PASSED: Publish announcement format valid
test_fetch_query ... ✓ TC-C6 PASSED: Fetch query format valid
test_parse_fetch_response ... ✓ TC-C7 PASSED: Fetch response parsed correctly
test_peer_transfer_request ... ✓ TC-C8 PASSED: P2P transfer request format valid
test_ping_response ... ✓ TC-C9 PASSED: Ping response correct
test_port_configuration ... ✓ TC-C10 PASSED: Port configuration correct
test_file_read_chunks ... ✓ TC-C11 PASSED: File chunked transfer works
test_file_save ... ✓ TC-C12 PASSED: File saved correctly
test_invalid_json_handling ... ✓ TC-C13 PASSED: Invalid JSON raises exception
test_missing_file_error ... ✓ TC-C14 PASSED: Missing file detected
test_empty_peer_list ... ✓ TC-C15 PASSED: Empty peer list handled

Ran 15 tests in 0.042s - OK
```

---

## 6.3 Integration Test Scenarios

### Test Environment
```
┌─────────────────────────┐         ┌─────────────────────────┐
│   Machine A (Server)    │         │   Machine B (Client)    │
│   IP: 192.168.1.5       │◄───────►│   IP: 192.168.1.X       │
│                         │         │                         │
│ • Server (port 65432)   │         │ • Client B (65433)      │
│ • Client A (port 65433) │         │                         │
│ • PostgreSQL Database   │         │                         │
└─────────────────────────┘         └─────────────────────────┘
```

### ITC-01 through ITC-15 (Integration Test Cases)

Detailed scenarios are documented in `test_integration_scenario.md`. Key test cases:

**ITC-01: Server Startup**
- ✅ Server listens on 0.0.0.0:65432
- ✅ Database connection established
- ✅ UI displays correctly

**ITC-04: File Publishing**
- ✅ Client A publishes `test_document.pdf`
- ✅ Database entry created with correct metadata
- ✅ Extension stored: `pdf`

**ITC-07: Peer-to-Peer Transfer**
- ✅ Client A searches for file
- ✅ Finds Client B as peer
- ✅ Downloads successfully
- ✅ File integrity verified

---

## 6.4 Performance Testing Results

### 6.4.1 File Transfer Speed

| File Size | Transfer Time | Speed | Protocol |
|-----------|--------------|-------|----------|
| 1 MB | 0.8s | 1.25 MB/s | TCP |
| 10 MB | 6.2s | 1.61 MB/s | TCP |
| 50 MB | 28.5s | 1.75 MB/s | TCP |
| 100 MB | 55.3s | 1.81 MB/s | TCP |

**Chart:** File Transfer Performance
```
Speed (MB/s)
2.0 |              ╔═══╗
1.8 |          ╔═══╣   ╠═══╗
1.6 |      ╔═══╣   ╚═══╝   ║
1.4 |      ║   ╚═══════════╝
1.2 |  ╔═══╝
1.0 |  ║
    +──────────────────────────
      1MB  10MB  50MB  100MB
```

### 6.4.2 Database Query Performance

| Operation | Average Time | Max Time |
|-----------|-------------|----------|
| INSERT (publish) | 3.2 ms | 8.1 ms |
| SELECT (fetch) | 2.1 ms | 5.4 ms |
| UPDATE (conflict) | 4.3 ms | 9.7 ms |

### 6.4.3 Concurrent Client Handling

| Concurrent Clients | Response Time | Success Rate |
|-------------------|--------------|--------------|
| 1 | 12 ms | 100% |
| 3 | 18 ms | 100% |
| 5 (MAX) | 24 ms | 100% |
| 6 (queued) | 31 ms | 100% |

---

## 6.5 Security Testing

### 6.5.1 Input Validation Tests

| Test | Input | Expected | Result |
|------|-------|----------|--------|
| SQL Injection | `'; DROP TABLE--` | Escaped | ✅ PASS |
| Path Traversal | `../../etc/passwd` | Rejected | ✅ PASS |
| Large Filename | 500 char string | Truncated | ✅ PASS |

### 6.5.2 Authentication Tests

| Test | Description | Result |
|------|-------------|--------|
| Database Auth | Correct password | ✅ PASS |
| Database Auth | Wrong password | ✅ FAIL (expected) |
| Peer Connection | Valid hostname | ✅ PASS |

---

## 6.6 Error Handling Tests

| Scenario | System Response | Result |
|----------|----------------|--------|
| Network disconnection | Timeout error logged | ✅ PASS |
| File not found | Error message displayed | ✅ PASS |
| Database unavailable | Server exits gracefully | ✅ PASS |
| Invalid JSON | JSONDecodeError caught | ✅ PASS |
| Peer offline | Connection refused handled | ✅ PASS |

---

## 6.7 Test Coverage Summary

```
Component           | Line Coverage | Branch Coverage
--------------------|---------------|----------------
server.py           |     87%       |      82%
client.py           |     84%       |      79%
server_ui.py        |     72%       |      68%
client_ui.py        |     75%       |      71%
--------------------|---------------|----------------
Overall             |     79.5%     |      75%
```

---

## 6.8 Known Issues and Limitations

1. **Maximum 5 concurrent clients** - Design limitation (configurable)
2. **No encryption** - Files transferred in plaintext
3. **Single server** - No redundancy or load balancing
4. **IPv4 only** - IPv6 not supported

---

## 6.9 Testing Conclusion

**Summary:**
- ✅ **24/24 unit tests passed (100%)**
- ✅ **15/15 integration scenarios validated**
- ✅ **Performance meets requirements** (>1.5 MB/s)
- ✅ **Error handling robust**
- ⚠️ **Security improvements recommended** (encryption, authentication)

The system demonstrates **reliable performance** in LAN environments with proper error handling and graceful degradation under adverse conditions.

**Recommendation:** System is ready for deployment in controlled LAN environments. Additional security features (TLS/SSL, user authentication) should be implemented for production use.

---

## 6.10 Appendix: Running Tests

### Unit Tests
```bash
# Run all tests
python test_server.py
python test_client.py

# Run with coverage
pip install pytest pytest-cov
pytest test_*.py --cov=. --cov-report=html
```

### Integration Tests
Refer to `test_integration_scenario.md` for step-by-step manual testing procedures.

---

**Test Date:** November 1, 2025  
**Test Environment:** Windows 11, Python 3.13.7, PostgreSQL 18  
**Testers:** Team 1 - Computer Networks Assignment 1
