import unittest
from unittest.mock import Mock, patch, MagicMock
from bluetooth_manager import BluetoothManager


class TestBluetoothManager(unittest.TestCase):
    """Unit tests for BluetoothManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = BluetoothManager()
    
    @patch('bluetooth_manager.ANDROID_AVAILABLE', False)
    def test_request_permissions_desktop(self):
        """Test permission request on desktop."""
        result = self.manager.request_permissions()
        self.assertTrue(result)
    
    @patch('bluetooth_manager.ANDROID_AVAILABLE', True)
    @patch('bluetooth_manager.check_permission')
    @patch('bluetooth_manager.request_permissions')
    def test_request_permissions_android(self, mock_req_perm, mock_check_perm):
        """Test permission request on Android."""
        mock_check_perm.return_value = True
        
        result = self.manager.request_permissions()
        
        self.assertTrue(result)
        mock_check_perm.assert_called()
    
    @patch('bluetooth_manager.ANDROID_AVAILABLE', False)
    def test_discover_devices_desktop(self):
        """Test device discovery on desktop."""
        devices = self.manager.discover_devices()
        
        self.assertIsInstance(devices, list)
        self.assertGreater(len(devices), 0)
    
    @patch('bluetooth_manager.ANDROID_AVAILABLE', True)
    def test_discover_devices_android_no_adapter(self):
        """Test device discovery on Android without adapter."""
        self.manager._bluetooth_adapter = None
        
        devices = self.manager.discover_devices()
        
        self.assertEqual(devices, [])
    
    @patch('bluetooth_manager.ANDROID_AVAILABLE', False)
    def test_pair_device_desktop(self):
        """Test device pairing on desktop."""
        result = self.manager.pair_device('00:11:22:33:44:55')
        self.assertTrue(result)
    
    def test_default_pin(self):
        """Test default PIN code."""
        self.assertEqual(self.manager.default_pin, '1234')
    
    def test_set_pin(self):
        """Test setting custom PIN."""
        self.manager.default_pin = '0000'
        self.assertEqual(self.manager.default_pin, '0000')


if __name__ == '__main__':
    unittest.main()
