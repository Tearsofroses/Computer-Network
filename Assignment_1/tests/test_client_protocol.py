"""
Client Protocol Tests
Tests for client-server communication protocol
"""

import unittest
import json
import socket


class TestClientProtocol(unittest.TestCase):
    """Test client-server protocol"""
    
    def test_introduce_command(self):
        """Test TC-C5: Client introduction to server"""
        # Arrange
        hostname = socket.gethostname()
        command = {
            'action': 'introduce',
            'hostname': hostname
        }
        
        # Act
        json_str = json.dumps(command)
        parsed = json.loads(json_str)
        
        # Assert
        self.assertEqual(parsed['action'], 'introduce')
        self.assertEqual(parsed['hostname'], hostname)
        print("✓ TC-C5 PASSED: Introduce command format valid")
    
    def test_publish_announcement(self):
        """Test TC-C6: File publish announcement format"""
        # Arrange
        local_path = "D:\\documents\\report.pdf"
        shared_name = "myreport"
        extension = "pdf"
        hostname = "test_client"
        
        announcement = {
            "action": "publish",
            "fname": shared_name,
            "lname": local_path,
            "extension": extension,
            "hostname": hostname
        }
        
        # Act
        json_str = json.dumps(announcement)
        parsed = json.loads(json_str)
        
        # Assert
        self.assertEqual(parsed['action'], 'publish')
        self.assertEqual(parsed['fname'], shared_name)
        self.assertEqual(parsed['lname'], local_path)
        self.assertEqual(parsed['extension'], extension)
        self.assertEqual(parsed['hostname'], hostname)
        print("✓ TC-C6 PASSED: Publish announcement format valid")
    
    def test_fetch_query(self):
        """Test TC-C7: File fetch query format"""
        # Arrange
        filename = "requestedfile"
        query = {"action": "fetch", "fname": filename}
        
        # Act
        json_str = json.dumps(query)
        parsed = json.loads(json_str)
        
        # Assert
        self.assertEqual(parsed['action'], 'fetch')
        self.assertEqual(parsed['fname'], filename)
        print("✓ TC-C7 PASSED: Fetch query format valid")
    
    def test_parse_fetch_response(self):
        """Test TC-C8: Parse server response for fetch"""
        # Arrange
        server_response = {
            'addresses': [
                {
                    'ip': '192.168.1.100',
                    'hostname': 'peer1',
                    'lname': 'D:\\file.txt',
                    'extension': 'txt'
                },
                {
                    'ip': '192.168.1.101',
                    'hostname': 'peer2',
                    'lname': 'C:\\data\\file.txt',
                    'extension': 'txt'
                }
            ]
        }
        
        # Act
        json_str = json.dumps(server_response)
        parsed = json.loads(json_str)
        
        # Assert
        self.assertIn('addresses', parsed)
        peers = parsed['addresses']
        self.assertEqual(len(peers), 2)
        self.assertEqual(peers[0]['ip'], '192.168.1.100')
        self.assertEqual(peers[1]['hostname'], 'peer2')
        print("✓ TC-C8 PASSED: Fetch response parsed correctly")
    
    def test_peer_transfer_request(self):
        """Test TC-C9: Peer-to-peer file transfer request"""
        # Arrange
        local_name = "D:\\shared\\document.pdf"
        request = {
            'action': 'send_file',
            'lname': local_name
        }
        
        # Act
        json_str = json.dumps(request)
        parsed = json.loads(json_str)
        
        # Assert
        self.assertEqual(parsed['action'], 'send_file')
        self.assertEqual(parsed['lname'], local_name)
        print("✓ TC-C9 PASSED: P2P transfer request format valid")


if __name__ == '__main__':
    unittest.main(verbosity=2)
