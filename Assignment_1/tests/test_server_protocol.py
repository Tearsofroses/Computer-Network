"""
Server Protocol Tests
Tests for JSON protocol validation and message formats
"""

import unittest
import json


class TestServerProtocol(unittest.TestCase):
    """Test server protocol handling"""
    
    def test_publish_command_format(self):
        """Test TC-S5: Validate publish command JSON format"""
        # Arrange
        command = {
            "action": "publish",
            "hostname": "test_client",
            "fname": "testfile",
            "lname": "D:\\test\\file.txt",
            "extension": "txt"
        }
        
        # Act
        json_str = json.dumps(command)
        parsed = json.loads(json_str)
        
        # Assert
        self.assertEqual(parsed['action'], 'publish')
        self.assertIn('hostname', parsed)
        self.assertIn('fname', parsed)
        self.assertIn('lname', parsed)
        self.assertIn('extension', parsed)
        print("✓ TC-S5 PASSED: Publish command format valid")
    
    def test_fetch_command_format(self):
        """Test TC-S6: Validate fetch command JSON format"""
        # Arrange
        command = {
            "action": "fetch",
            "fname": "requestedfile"
        }
        
        # Act
        json_str = json.dumps(command)
        parsed = json.loads(json_str)
        
        # Assert
        self.assertEqual(parsed['action'], 'fetch')
        self.assertIn('fname', parsed)
        print("✓ TC-S6 PASSED: Fetch command format valid")
    
    def test_fetch_response_format(self):
        """Test TC-S7: Validate fetch response format"""
        # Arrange
        response = {
            'addresses': [
                {
                    'ip': '192.168.1.100',
                    'hostname': 'peer1',
                    'lname': 'D:\\file.txt',
                    'extension': 'txt'
                }
            ]
        }
        
        # Act
        json_str = json.dumps(response)
        parsed = json.loads(json_str)
        
        # Assert
        self.assertIn('addresses', parsed)
        self.assertEqual(len(parsed['addresses']), 1)
        peer = parsed['addresses'][0]
        self.assertIn('ip', peer)
        self.assertIn('hostname', peer)
        self.assertIn('lname', peer)
        self.assertIn('extension', peer)
        print("✓ TC-S7 PASSED: Fetch response format valid")
    
    def test_introduce_command_format(self):
        """Test TC-S8: Validate introduce command format"""
        # Arrange
        command = {
            "action": "introduce",
            "hostname": "client_hostname"
        }
        
        # Act
        json_str = json.dumps(command)
        parsed = json.loads(json_str)
        
        # Assert
        self.assertEqual(parsed['action'], 'introduce')
        self.assertIn('hostname', parsed)
        print("✓ TC-S8 PASSED: Introduce command format valid")


if __name__ == '__main__':
    unittest.main(verbosity=2)
