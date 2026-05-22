import obd
import time
from typing import Optional, Tuple
import logging
from obd_interface import OBDInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DesktopOBDInterface(OBDInterface):
    """Desktop OBD-II implementation using python-obd library."""
    
    def __init__(self, port: Optional[str] = None, baudrate: int = 38400):
        self.port = port
        self.baudrate = baudrate
        self.connection: Optional[obd.OBD] = None
    
    def connect(self, timeout: int = 10) -> bool:
        """Connect to OBD-II adapter via python-obd."""
        try:
            logger.info(f"Attempting to connect to OBD-II adapter on port: {self.port or 'auto'}")
            
            if self.port:
                self.connection = obd.OBD(self.port, baudrate=self.baudrate, timeout=timeout)
            else:
                self.connection = obd.OBD(baudrate=self.baudrate, timeout=timeout)
            
            if self.connection.is_connected():
                logger.info("Successfully connected to OBD-II adapter")
                return True
            else:
                logger.error("Failed to connect to OBD-II adapter")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to OBD-II adapter: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from OBD-II adapter."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from OBD-II adapter")
    
    def is_connected(self) -> bool:
        """Check if currently connected to OBD-II adapter."""
        return self.connection is not None and self.connection.is_connected()
    
    def read_vin(self, max_retries: int = 3) -> Optional[str]:
        """Read VIN from vehicle via OBD-II."""
        if not self.is_connected():
            logger.error("Not connected to OBD-II adapter")
            return None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Reading VIN (attempt {attempt + 1}/{max_retries})")
                vin_response = self.connection.query(obd.commands.VIN)
                
                if not vin_response.is_null():
                    vin = str(vin_response.value).strip()
                    logger.info(f"Successfully read VIN: {vin}")
                    
                    if len(vin) == 17:
                        return vin
                    else:
                        logger.warning(f"Invalid VIN length: {len(vin)} (expected 17)")
                        return None
                else:
                    logger.warning(f"VIN read returned null value (attempt {attempt + 1})")
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error reading VIN (attempt {attempt + 1}): {e}")
                time.sleep(1)
        
        logger.error(f"Failed to read VIN after {max_retries} attempts")
        return None
    
    def send_command(self, command: str) -> Optional[str]:
        """Send raw OBD command and get response."""
        if not self.is_connected():
            logger.error("Not connected to OBD-II adapter")
            return None
        
        try:
            response = self.connection.query(obd.commands[command])
            if not response.is_null():
                return str(response.value).strip()
            return None
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return None
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test connection by reading RPM."""
        if not self.is_connected():
            return False, "Not connected to OBD-II adapter"
        
        try:
            rpm_response = self.connection.query(obd.commands.RPM)
            if not rpm_response.is_null():
                return True, "Connection test successful"
            else:
                return False, "Connection test failed - no response"
        except Exception as e:
            return False, f"Connection test error: {e}"
