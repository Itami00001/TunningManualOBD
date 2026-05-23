import socket
import time
from typing import Optional, Tuple
import logging
from obd_interface import OBDInterface

try:
    from jnius import autoclass
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AndroidOBDInterface(OBDInterface):
    """Android OBD-II implementation using Bluetooth socket."""
    
    def __init__(self, device_address: str):
        self.device_address = device_address
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.java_socket = None
    
    def connect(self, timeout: int = 10) -> bool:
        """Connect to OBD-II adapter via Bluetooth socket."""
        if not ANDROID_AVAILABLE:
            logger.error("Android not available, cannot use AndroidOBDInterface")
            return False
            
        try:
            logger.info(f"Connecting to OBD-II adapter at {self.device_address}")
            
            # Use Java Bluetooth socket with proper UUID
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
            UUID = autoclass('java.util.UUID')
            
            adapter = BluetoothAdapter.getDefaultAdapter()
            if not adapter or not adapter.isEnabled():
                logger.error("Bluetooth not available or not enabled")
                return False
            
            device = adapter.getRemoteDevice(self.device_address)
            
            # SPP UUID for serial port profile
            spp_uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
            
            # Create RFCOMM socket with UUID
            self.java_socket = device.createRfcommSocketToServiceRecord(spp_uuid)
            self.java_socket.connect()
            
            self.connected = True
            
            # Initialize ELM327
            self._send_command("AT Z")  # Reset
            time.sleep(0.5)
            self._send_command("AT E0")  # Echo off
            time.sleep(0.2)
            self._send_command("AT SP 0")  # Set protocol to auto
            time.sleep(0.2)
            
            logger.info("Successfully connected to OBD-II adapter")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to OBD-II adapter: {e}")
            self.connected = False
            if self.java_socket:
                try:
                    self.java_socket.close()
                except:
                    pass
                self.java_socket = None
            return False
    
    def disconnect(self):
        """Disconnect from OBD-II adapter."""
        if self.java_socket:
            try:
                self._send_command("AT Z")  # Reset before disconnect
                time.sleep(0.2)
            except:
                pass
            self.java_socket.close()
            self.java_socket = None
            self.connected = False
            logger.info("Disconnected from OBD-II adapter")
    
    def is_connected(self) -> bool:
        """Check if currently connected to OBD-II adapter."""
        return self.connected and self.java_socket is not None
    
    def _send_command(self, command: str) -> Optional[str]:
        """Send command to ELM327 and get response."""
        if not self.is_connected():
            logger.error("Not connected to OBD-II adapter")
            return None
        
        try:
            # Send command via Java socket
            output_stream = self.java_socket.getOutputStream()
            output_stream.write((command + "\r").encode())
            output_stream.flush()
            
            # Read response via Java socket
            input_stream = self.java_socket.getInputStream()
            response = ""
            buffer = bytearray()
            
            # Read until we see the ELM327 prompt '>'
            while True:
                data = input_stream.read(1024)
                if not data:
                    break
                buffer.extend(data)
                response = buffer.decode()
                if ">" in response:
                    break
            
            # Clean up response
            lines = response.split("\r")
            cleaned = [line.strip() for line in lines if line.strip() and not line.strip().startswith(">")]
            result = " ".join(cleaned)
            
            logger.debug(f"Command: {command}, Response: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return None
    
    def read_vin(self, max_retries: int = 3) -> Optional[str]:
        """Read VIN from vehicle via OBD-II."""
        if not self.is_connected():
            logger.error("Not connected to OBD-II adapter")
            return None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Reading VIN (attempt {attempt + 1}/{max_retries})")
                
                # Send VIN command (Service 09, PID 02)
                response = self._send_command("09 02")
                
                if response and "NO DATA" not in response:
                    # Parse VIN from response
                    # ELM327 returns VIN as: 49 02 1 1 <VIN_DATA>
                    # VIN_DATA is 17 bytes representing the VIN
                    parts = response.split()
                    if len(parts) >= 2:
                        # Extract VIN data (skip header)
                        vin_data = "".join(parts[2:])  # Skip "49 02 1"
                        if len(vin_data) >= 17:
                            vin = vin_data[:17]
                            logger.info(f"Successfully read VIN: {vin}")
                            return vin
                
                logger.warning(f"VIN read failed (attempt {attempt + 1})")
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error reading VIN (attempt {attempt + 1}): {e}")
                time.sleep(1)
        
        logger.error(f"Failed to read VIN after {max_retries} attempts")
        return None
    
    def send_command(self, command: str) -> Optional[str]:
        """Send raw OBD command and get response."""
        return self._send_command(command)
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test connection by sending AT command."""
        if not self.is_connected():
            return False, "Not connected to OBD-II adapter"
        
        try:
            response = self._send_command("AT I")  # Get ELM327 version
            if response and "ELM" in response.upper():
                return True, f"Connection test successful: {response}"
            else:
                return False, "Connection test failed - unexpected response"
        except Exception as e:
            return False, f"Connection test error: {e}"
