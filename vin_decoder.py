import requests
import logging
from typing import Optional, Dict
from nhtsa_vin_decoder import NHTSADecoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VINDecoder:
    """Decodes VIN numbers using multiple APIs."""
    
    def __init__(self):
        self.nhtsa_decoder = NHTSADecoder()
    
    def decode(self, vin: str) -> Optional[Dict[str, str]]:
        """
        Decode VIN using NHTSA API with fallbacks.
        
        Args:
            vin: 17-character VIN code
            
        Returns:
            Dictionary with decoded vehicle info or None if failed
        """
        if not vin or len(vin) != 17:
            logger.error(f"Invalid VIN: {vin}")
            return None
        
        # Try NHTSA API first
        result = self._decode_nhtsa(vin)
        if result:
            return result
        
        # Try alternative APIs if NHTSA fails
        result = self._decode_vin_decoder_net(vin)
        if result:
            return result
        
        logger.error(f"Failed to decode VIN: {vin}")
        return None
    
    def _decode_nhtsa(self, vin: str) -> Optional[Dict[str, str]]:
        """Decode using NHTSA API."""
        try:
            logger.info(f"Decoding VIN using NHTSA API: {vin}")
            vehicle_info = self.nhtsa_decoder.decode(vin)
            
            if vehicle_info:
                result = {
                    'Make': vehicle_info.get('Make', 'Unknown'),
                    'Model': vehicle_info.get('Model', 'Unknown'),
                    'ModelYear': vehicle_info.get('ModelYear', 'Unknown'),
                    'Manufacturer': vehicle_info.get('Manufacturer', 'Unknown'),
                    'VehicleType': vehicle_info.get('VehicleType', 'Unknown'),
                    'PlantCountry': vehicle_info.get('PlantCountry', 'Unknown'),
                }
                
                # Format vehicle name
                result['FormattedName'] = self._format_vehicle_name(result)
                logger.info(f"Successfully decoded VIN: {result['FormattedName']}")
                return result
            
        except Exception as e:
            logger.error(f"Error decoding VIN with NHTSA API: {e}")
        
        return None
    
    def _decode_vin_decoder_net(self, vin: str) -> Optional[Dict[str, str]]:
        """Decode using vindecoder.net API as fallback."""
        try:
            logger.info(f"Decoding VIN using vindecoder.net API: {vin}")
            
            url = f"https://vindecoder.net/api/decode/{vin}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    'Make': data.get('make', 'Unknown'),
                    'Model': data.get('model', 'Unknown'),
                    'ModelYear': data.get('year', 'Unknown'),
                    'Manufacturer': data.get('manufacturer', 'Unknown'),
                    'VehicleType': data.get('body_type', 'Unknown'),
                    'PlantCountry': data.get('country', 'Unknown'),
                }
                
                result['FormattedName'] = self._format_vehicle_name(result)
                logger.info(f"Successfully decoded VIN: {result['FormattedName']}")
                return result
                
        except Exception as e:
            logger.error(f"Error decoding VIN with vindecoder.net: {e}")
        
        return None
    
    def _format_vehicle_name(self, vehicle_info: Dict[str, str]) -> str:
        """
        Format vehicle info into a readable name.
        
        Args:
            vehicle_info: Dictionary with vehicle details
            
        Returns:
            Formatted string like "Nissan Silvia S15 (2002)"
        """
        make = vehicle_info.get('Make', 'Unknown')
        model = vehicle_info.get('Model', 'Unknown')
        year = vehicle_info.get('ModelYear', 'Unknown')
        
        # Remove 'Unknown' values
        parts = [part for part in [make, model, year] if part != 'Unknown']
        
        if len(parts) == 0:
            return "Unknown Vehicle"
        
        formatted = " ".join(parts)
        
        # Add year in parentheses if available
        if year != 'Unknown':
            formatted = f"{make} {model} ({year})"
        
        return formatted.strip()
    
    def get_vehicle_info_for_website(self, vin: str) -> Optional[Dict[str, str]]:
        """
        Get vehicle info formatted for website integration.
        
        Args:
            vin: 17-character VIN code
            
        Returns:
            Dictionary with website-ready vehicle info
        """
        decoded = self.decode(vin)
        
        if not decoded:
            return None
        
        return {
            'vin': vin,
            'make': decoded['Make'],
            'model': decoded['Model'],
            'year': decoded['ModelYear'],
            'full_name': decoded['FormattedName'],
            'manufacturer': decoded['Manufacturer'],
            'vehicle_type': decoded['VehicleType'],
            'country': decoded['PlantCountry'],
        }
