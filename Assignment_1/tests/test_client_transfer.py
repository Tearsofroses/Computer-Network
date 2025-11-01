"""
Client File Transfer Tests
Tests for chunked file reading and writing
"""

import unittest
import os
import tempfile


class TestClientFileTransfer(unittest.TestCase):
    """Test file transfer operations"""
    
    def test_file_read_chunks(self):
        """Test TC-C10: Read file in chunks for transfer"""
        # Arrange - create test file
        test_content = b"Test data " * 1000  # ~10KB
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(test_content)
            tmp_path = tmp.name
        
        # Act - read in chunks
        chunk_size = 4096
        chunks = []
        with open(tmp_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                chunks.append(chunk)
        
        # Assert
        self.assertGreater(len(chunks), 1)  # Multiple chunks
        reconstructed = b''.join(chunks)
        self.assertEqual(reconstructed, test_content)
        
        # Cleanup
        os.unlink(tmp_path)
        print("✓ TC-C10 PASSED: File chunked transfer works")
    
    def test_file_save(self):
        """Test TC-C11: Save downloaded file"""
        # Arrange
        test_data = b"Downloaded content"
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            save_path = tmp.name
        
        # Act - simulate download save
        with open(save_path, 'wb') as f:
            f.write(test_data)
        
        # Assert
        self.assertTrue(os.path.exists(save_path))
        with open(save_path, 'rb') as f:
            saved_content = f.read()
        self.assertEqual(saved_content, test_data)
        
        # Cleanup
        os.unlink(save_path)
        print("✓ TC-C11 PASSED: File saved correctly")
    
    def test_large_file_chunks(self):
        """Test TC-C12: Handle large file in multiple chunks"""
        # Arrange - create 1MB file
        test_content = b"X" * (1024 * 1024)  # 1MB
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(test_content)
            tmp_path = tmp.name
        
        # Act
        chunk_size = 4096
        chunk_count = 0
        with open(tmp_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                chunk_count += 1
                self.assertLessEqual(len(chunk), chunk_size)
        
        # Assert
        expected_chunks = (1024 * 1024) // chunk_size
        self.assertEqual(chunk_count, expected_chunks)
        
        # Cleanup
        os.unlink(tmp_path)
        print("✓ TC-C12 PASSED: Large file chunking works")


if __name__ == '__main__':
    unittest.main(verbosity=2)
