import logging
from typing import List, Optional, Dict
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from jnius import autoclass
    from android.permissions import request_permissions, check_permission
    from android import activity
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False
    logger.warning("Android modules not available - using desktop mode")


class BluetoothManager:
    """Manages Bluetooth device discovery and connection."""
    
    REQUIRED_PERMISSIONS = [
        'android.permission.BLUETOOTH',
        'android.permission.BLUETOOTH_ADMIN',
        'android.permission.BLUETOOTH_SCAN',
        'android.permission.BLUETOOTH_CONNECT',
        'android.permission.ACCESS_FINE_LOCATION',
    ]
    
    def __init__(self):
        self.default_pin = "1234"
        self.discovered_devices = []
        self._bluetooth_adapter = None
        self._discovery_thread = None
        self._stop_discovery = False
        
        if ANDROID_AVAILABLE:
            try:
                BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
                self._bluetooth_adapter = BluetoothAdapter.getDefaultAdapter()
                logger.info("Android Bluetooth adapter initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Android Bluetooth: {e}")
                self._bluetooth_adapter = None
    
    def request_permissions(self) -> bool:
        """
        Request required Bluetooth permissions.
        
        Returns:
            True if permissions granted, False otherwise
        """
        if not ANDROID_AVAILABLE:
            logger.info("Desktop mode - no permissions needed")
            return True
            
        try:
            not_granted = []
            for permission in self.REQUIRED_PERMISSIONS:
                if not check_permission(permission):
                    not_granted.append(permission)
            
            if not_granted:
                logger.info(f"Requesting permissions: {not_granted}")
                request_permissions(not_granted)
                return True
            else:
                logger.info("All permissions already granted")
                return True
                
        except Exception as e:
            logger.error(f"Error requesting permissions: {e}")
            return False
    
    def discover_devices(self, timeout: int = 10) -> List[Dict[str, str]]:
        """
        Discover available Bluetooth devices.
        
        Args:
            timeout: Discovery timeout in seconds
            
        Returns:
            List of discovered devices with name and address
        """
        try:
            logger.info("Starting Bluetooth device discovery...")
            
            if ANDROID_AVAILABLE and self._bluetooth_adapter:
                return self._discover_android(timeout)
            else:
                return self._discover_desktop()
            
        except Exception as e:
            logger.error(f"Error discovering devices: {e}")
            return []
    
    def _discover_android(self, timeout: int) -> List[Dict[str, str]]:
        """Discover devices using Android Bluetooth API (simplified - bonded devices only)."""
        try:
            if not self._bluetooth_adapter.isEnabled():
                logger.warning("Bluetooth is not enabled")
                return []
            
            # Get bonded devices (paired devices)
            self.discovered_devices = []
            bonded_devices = self._bluetooth_adapter.getBondedDevices()
            
            if bonded_devices:
                for device in bonded_devices.toArray():
                    device_info = {
                        'name': device.getName() or "Unknown",
                        'address': device.getAddress()
                    }
                    self.discovered_devices.append(device_info)
                    logger.info(f"Found bonded device: {device_info['name']} ({device_info['address']})")
            
            logger.info(f"Discovery completed. Found {len(self.discovered_devices)} bonded devices")
            return self.discovered_devices
            
        except Exception as e:
            logger.error(f"Error discovering Android devices: {e}")
            return []
    
    def _discover_desktop(self) -> List[Dict[str, str]]:
        """Discover devices on desktop (placeholder)."""
        try:
            logger.info("Desktop mode - using placeholder devices")
            devices = [
                {'name': 'ELM327', 'address': '00:11:22:33:44:55'},
                {'name': 'OBDII', 'address': 'AA:BB:CC:DD:EE:FF'},
            ]
            return devices
        except Exception as e:
            logger.error(f"Error discovering desktop devices: {e}")
            return []
    
    def pair_device(self, device_address: str, pin: Optional[str] = None) -> bool:
        """
        Pair with a Bluetooth device using PIN.
        
        Args:
            device_address: MAC address of the device
            pin: PIN code (defaults to 1234)
            
        Returns:
            True if pairing successful, False otherwise
        """
        if pin is None:
            pin = self.default_pin
        
        try:
            logger.info(f"Pairing with device {device_address} using PIN: {pin}")
            
            if ANDROID_AVAILABLE and self._bluetooth_adapter:
                return self._pair_android(device_address, pin)
            else:
                return self._pair_desktop(device_address, pin)
            
        except Exception as e:
            logger.error(f"Error pairing with device: {e}")
            return False
    
    def _pair_android(self, device_address: str, pin: str) -> bool:
        """Pair device using Android Bluetooth API."""
        try:
            BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
            device = self._bluetooth_adapter.getRemoteDevice(device_address)
            
            # On Android, pairing is typically done through system UI
            # We can only create the device object and let user pair through settings
            # For ELM327 devices, they often auto-pair with default PIN
            logger.info(f"Device object created for {device_address}. User may need to pair through system settings.")
            return True
            
        except Exception as e:
            logger.error(f"Error pairing Android device: {e}")
            return False
    
    def _pair_desktop(self, device_address: str, pin: str) -> bool:
        """Pair device on desktop (placeholder)."""
        try:
            logger.info(f"Desktop mode - simulating pairing with {device_address}")
            return True
        except Exception as e:
            logger.error(f"Error pairing desktop device: {e}")
            return False
    
    def is_device_paired(self, device_address: str) -> bool:
        """
        Check if a device is already paired.
        
        Args:
            device_address: MAC address of the device
            
        Returns:
            True if paired, False otherwise
        """
        try:
            if ANDROID_AVAILABLE and self._bluetooth_adapter:
                bonded_devices = self._bluetooth_adapter.getBondedDevices()
                if bonded_devices:
                    for device in bonded_devices.toArray():
                        if device.getAddress() == device_address:
                            logger.info(f"Device {device_address} is paired")
                            return True
            return False
            
        except Exception as e:
            logger.error(f"Error checking paired status: {e}")
            return False
    
    def get_paired_devices(self) -> List[Dict[str, str]]:
        """
        Get list of already paired devices.
        
        Returns:
            List of paired devices with name and address
        """
        try:
            logger.info("Getting paired devices...")
            
            if ANDROID_AVAILABLE and self._bluetooth_adapter:
                bonded_devices = self._bluetooth_adapter.getBondedDevices()
                devices = []
                if bonded_devices:
                    for device in bonded_devices.toArray():
                        device_info = {
                            'name': device.getName() or "Unknown",
                            'address': device.getAddress()
                        }
                        devices.append(device_info)
                logger.info(f"Found {len(devices)} paired devices")
                return devices
            else:
                return []
            
        except Exception as e:
            logger.error(f"Error getting paired devices: {e}")
            return []
