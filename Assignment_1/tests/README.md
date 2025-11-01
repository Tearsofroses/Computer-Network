# P2P File Sharing - Tests Directory

## Structure

```
tests/
├── __init__.py                    # Package initializer
├── test_server_database.py        # Server database operations (4 tests)
├── test_server_protocol.py        # Server protocol validation (4 tests)
├── test_server_config.py          # Server configuration (3 tests)
├── test_client_file_ops.py        # Client file operations (4 tests)
├── test_client_protocol.py        # Client protocol (5 tests)
├── test_client_transfer.py        # Client file transfer (3 tests)
└── test_client_errors.py          # Client error handling (5 tests)
```

## Test Categories

### Server Tests (11 tests)
1. **Database Tests** (`test_server_database.py`)
   - TC-S1: Register new file
   - TC-S2: Update existing file
   - TC-S3: Discover peer files
   - TC-S4: Fetch file locations

2. **Protocol Tests** (`test_server_protocol.py`)
   - TC-S5: Publish command format
   - TC-S6: Fetch command format
   - TC-S7: Fetch response format
   - TC-S8: Introduce command format

3. **Configuration Tests** (`test_server_config.py`)
   - TC-S9: MAX_CLIENTS limit
   - TC-S10: Server ports
   - TC-S11: Database configuration

### Client Tests (17 tests)
1. **File Operations** (`test_client_file_ops.py`)
   - TC-C1: List local files
   - TC-C2: Extract file extension
   - TC-C3: File existence check
   - TC-C4: File size check

2. **Protocol Tests** (`test_client_protocol.py`)
   - TC-C5: Introduce command
   - TC-C6: Publish announcement
   - TC-C7: Fetch query
   - TC-C8: Parse fetch response
   - TC-C9: P2P transfer request

3. **Transfer Tests** (`test_client_transfer.py`)
   - TC-C10: Read file chunks
   - TC-C11: Save downloaded file
   - TC-C12: Large file chunks

4. **Error Handling** (`test_client_errors.py`)
   - TC-C13: Invalid JSON handling
   - TC-C14: Missing file error
   - TC-C15: Empty peer list
   - TC-C16: Malformed response
   - TC-C17: Network timeout

## Running Tests

### Run All Tests
```bash
# From Assignment_1 directory
python run_all_tests.py
```

### Run Specific Test Module
```bash
# Server database tests
python -m unittest tests.test_server_database

# Client protocol tests
python -m unittest tests.test_client_protocol
```

### Run Specific Test Case
```bash
# Single test
python -m unittest tests.test_server_database.TestServerDatabase.test_register_file
```

### Run with Coverage
```bash
pip install coverage
coverage run -m unittest discover tests
coverage report
coverage html
```

## Test Requirements

### Prerequisites
- Python 3.8+
- PostgreSQL with `filesharing` database
- Required packages: `psycopg2-binary`

### Database Setup
```sql
CREATE DATABASE filesharing;
\c filesharing
CREATE TABLE client_files (
    id SERIAL PRIMARY KEY,
    lname TEXT NOT NULL,
    fname TEXT NOT NULL,
    extension TEXT NOT NULL,
    hostname TEXT NOT NULL,
    address INET NOT NULL,
    UNIQUE(address, fname, hostname)
);
```

## Expected Results

**Total: 28 tests**
- Server Tests: 11
- Client Tests: 17

**Success Rate: 100%** (all tests should pass)

## Notes

- Tests use `test_` prefix for hostnames to avoid conflicts
- Database tests automatically clean up test data
- File operation tests use temporary files
- All tests are isolated and can run independently
