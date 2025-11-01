"""
Client File Operations Tests
Tests for local file handling, listing, and validation
"""

import unittest
import os
import tempfile


class TestClientFileOperations(unittest.TestCase):
    """Test client file handling"""
    
    def test_list_local_files(self):
        """Test TC-C1: List files in directory"""
        # Create temporary directory with test files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_files = ['file1.txt', 'file2.pdf', 'image.jpg']
            for fname in test_files:
                open(os.path.join(tmpdir, fname), 'w').close()
            
            # Act
            files = [f for f in os.listdir(tmpdir) if os.path.isfile(os.path.join(tmpdir, f))]
            
            # Assert
            self.assertEqual(len(files), 3)
            self.assertIn('file1.txt', files)
            self.assertIn('file2.pdf', files)
            self.assertIn('image.jpg', files)
            print("✓ TC-C1 PASSED: Listed all local files")
    
    def test_file_extension_extraction(self):
        """Test TC-C2: Extract file extension correctly"""
        # Arrange & Act
        test_cases = [
            ("document.pdf", "pdf"),
            ("photo.jpg", "jpg"),
            ("archive.tar.gz", "gz"),
            ("noextension", ""),
        ]
        
        # Assert
        for filepath, expected_ext in test_cases:
            _, ext = os.path.splitext(filepath)
            extension = ext.lstrip('.') if ext else ''
            self.assertEqual(extension, expected_ext)
        
        print("✓ TC-C2 PASSED: File extensions extracted correctly")
    
    def test_file_exists_check(self):
        """Test TC-C3: Verify file existence before publishing"""
        # Arrange
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            existing_file = tmp.name
        
        non_existing_file = "D:\\nonexistent\\file.txt"
        
        # Act & Assert
        self.assertTrue(os.path.exists(existing_file))
        self.assertFalse(os.path.exists(non_existing_file))
        
        # Cleanup
        os.unlink(existing_file)
        print("✓ TC-C3 PASSED: File existence check works")
    
    def test_file_size_check(self):
        """Test TC-C4: Get file size correctly"""
        # Arrange
        test_content = b"Test data " * 100
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(test_content)
            tmp_path = tmp.name
        
        # Act
        file_size = os.path.getsize(tmp_path)
        
        # Assert
        self.assertEqual(file_size, len(test_content))
        
        # Cleanup
        os.unlink(tmp_path)
        print("✓ TC-C4 PASSED: File size check works")


if __name__ == '__main__':
    unittest.main(verbosity=2)
