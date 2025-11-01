"""
Server Database Tests
Tests for database operations including file registration, updates, and queries
"""

import unittest
import psycopg2
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestServerDatabase(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Setup test database connection"""
        try:
            self.conn = psycopg2.connect(
                dbname="filesharing",
                user="postgres",
                password=r"13?T+4i%ewse",
                host="localhost",
                port="5432"
            )
            self.cursor = self.conn.cursor()
            # Clear test data
            self.cursor.execute("DELETE FROM client_files WHERE hostname LIKE 'test_%'")
            self.conn.commit()
        except Exception as e:
            self.skipTest(f"Database not available: {e}")
    
    def tearDown(self):
        """Cleanup test data"""
        if hasattr(self, 'cursor'):
            self.cursor.execute("DELETE FROM client_files WHERE hostname LIKE 'test_%'")
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
    
    def test_register_file(self):
        """Test TC-S1: Register new file in database"""
        # Arrange
        lname = "D:\\test\\document.pdf"
        fname = "mydocument"
        extension = "pdf"
        hostname = "test_client1"
        ip_addr = "192.168.1.100"
        
        # Act
        self.cursor.execute(
            """
            INSERT INTO client_files (lname, fname, extension, hostname, address)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (lname, fname, extension, hostname, ip_addr)
        )
        self.conn.commit()
        
        # Assert
        self.cursor.execute(
            "SELECT lname, fname, extension FROM client_files WHERE hostname = %s",
            (hostname,)
        )
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], lname)
        self.assertEqual(result[1], fname)
        self.assertEqual(result[2], extension)
        print("✓ TC-S1 PASSED: File registered successfully")
    
    def test_update_existing_file(self):
        """Test TC-S2: Update existing file (conflict handling)"""
        # Arrange
        fname = "myfile"
        hostname = "test_client2"
        ip_addr = "192.168.1.101"
        
        # Insert original
        self.cursor.execute(
            """
            INSERT INTO client_files (lname, fname, extension, hostname, address)
            VALUES (%s, %s, %s, %s, %s)
            """,
            ("D:\\old\\path.txt", fname, "txt", hostname, ip_addr)
        )
        self.conn.commit()
        
        # Act - Update with new path
        new_lname = "D:\\new\\path.txt"
        self.cursor.execute(
            """
            INSERT INTO client_files (lname, fname, extension, hostname, address)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (address, fname, hostname) 
            DO UPDATE SET lname = EXCLUDED.lname, extension = EXCLUDED.extension
            """,
            (new_lname, fname, "txt", hostname, ip_addr)
        )
        self.conn.commit()
        
        # Assert
        self.cursor.execute(
            "SELECT lname FROM client_files WHERE hostname = %s AND fname = %s",
            (hostname, fname)
        )
        result = self.cursor.fetchone()
        self.assertEqual(result[0], new_lname)
        print("✓ TC-S2 PASSED: File updated on conflict")
    
    def test_discover_peer_files(self):
        """Test TC-S3: Discover files by hostname"""
        # Arrange
        hostname = "test_client3"
        ip_addr = "192.168.1.102"
        
        # Insert multiple files
        files = [
            ("D:\\docs\\file1.txt", "file1", "txt"),
            ("D:\\images\\photo.jpg", "photo", "jpg"),
            ("D:\\videos\\clip.mp4", "clip", "mp4")
        ]
        
        for lname, fname, ext in files:
            self.cursor.execute(
                """
                INSERT INTO client_files (lname, fname, extension, hostname, address)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (lname, fname, ext, hostname, ip_addr)
            )
        self.conn.commit()
        
        # Act
        self.cursor.execute(
            """
            SELECT fname, extension
            FROM client_files
            WHERE hostname = %s
            ORDER BY fname
            """,
            (hostname,)
        )
        results = self.cursor.fetchall()
        
        # Assert
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][0], "clip")  # Alphabetically first
        self.assertEqual(results[1][0], "file1")
        self.assertEqual(results[2][0], "photo")
        print("✓ TC-S3 PASSED: Discovered all files for peer")
    
    def test_fetch_file_locations(self):
        """Test TC-S4: Fetch all peers having a specific file"""
        # Arrange
        fname = "sharedfile"
        
        # Multiple peers with same file
        peers = [
            ("test_peer1", "192.168.1.103", "D:\\data\\file.txt", "txt"),
            ("test_peer2", "192.168.1.104", "D:\\downloads\\file.txt", "txt"),
            ("test_peer3", "192.168.1.105", "C:\\Users\\file.txt", "txt")
        ]
        
        for hostname, ip, lname, ext in peers:
            self.cursor.execute(
                """
                INSERT INTO client_files (lname, fname, extension, hostname, address)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (lname, fname, ext, hostname, ip)
            )
        self.conn.commit()
        
        # Act
        self.cursor.execute(
            """
            SELECT DISTINCT ON (address, hostname) address, hostname, lname, extension
            FROM client_files
            WHERE fname = %s
            """,
            (fname,)
        )
        results = self.cursor.fetchall()
        
        # Assert
        self.assertEqual(len(results), 3)
        ips = [str(r[0]) for r in results]
        self.assertIn("192.168.1.103", ips)
        self.assertIn("192.168.1.104", ips)
        self.assertIn("192.168.1.105", ips)
        print("✓ TC-S4 PASSED: Found all peers with file")


if __name__ == '__main__':
    unittest.main(verbosity=2)
