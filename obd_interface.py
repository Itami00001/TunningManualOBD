from abc import ABC, abstractmethod
from typing import Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OBDInterface(ABC):
    """Abstract interface for OBD-II connections."""
    
    @abstractmethod
    def connect(self, timeout: int = 10) -> bool:
        """
        Connect to OBD-II adapter.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from OBD-II adapter."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if currently connected to OBD-II adapter."""
        pass
    
    @abstractmethod
    def read_vin(self, max_retries: int = 3) -> Optional[str]:
        """
        Read VIN from vehicle via OBD-II.
        
        Args:
            max_retries: Maximum number of retry attempts
            
        Returns:
            VIN string if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def send_command(self, command: str) -> Optional[str]:
        """
        Send raw OBD command and get response.
        
        Args:
            command: OBD command string (e.g., "09 02")
            
        Returns:
            Response string if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection by reading a simple parameter.
        
        Returns:
            Tuple of (success, message)
        """
        pass
