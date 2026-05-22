import unittest
from unittest.mock import Mock, patch
from vin_decoder import VINDecoder


class TestVINDecoder(unittest.TestCase):
    """Unit tests for VINDecoder."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.decoder = VINDecoder()
    
    @patch('vin_decoder.requests.get')
    def test_decode_nhtsa_success(self, mock_get):
        """Test successful VIN decoding via NHTSA API."""
        # Mock NHTSA API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'Results': [{
                'Make': 'Nissan',
                'Model': 'Silvia',
                'ModelYear': '2002',
                'Manufacturer': 'Nissan Motor Co., Ltd.',
                'VehicleType': 'Passenger Car',
                'PlantCountry': 'Japan'
            }]
        }
        mock_get.return_value = mock_response
        
        result = self.decoder.decode('JN1AZ54D1W0000001')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['Make'], 'Nissan')
        self.assertEqual(result['Model'], 'Silvia')
        self.assertEqual(result['ModelYear'], '2002')
    
    @patch('vin_decoder.requests.get')
    def test_decode_nhtsa_failure(self, mock_get):
        """Test VIN decoding when NHTSA API fails."""
        # Mock NHTSA API failure
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.decoder.decode('JN1AZ54D1W0000001')
        
        # Should return None or empty dict on failure
        self.assertIsNone(result)
    
    @patch('vin_decoder.requests.get')
    def test_decode_fallback_api(self, mock_get):
        """Test VIN decoding fallback to alternative API."""
        # Mock NHTSA API failure
        mock_response_nhtsa = Mock()
        mock_response_nhtsa.status_code = 404
        
        # Mock fallback API success
        mock_response_fallback = Mock()
        mock_response_fallback.status_code = 200
        mock_response_fallback.json.return_value = {
            'make': 'Toyota',
            'model': 'Supra',
            'year': '1994'
        }
        
        mock_get.side_effect = [mock_response_nhtsa, mock_response_fallback]
        
        result = self.decoder.decode('JN1AZ54D1W0000001')
        
        # Should return result from fallback API
        self.assertIsNotNone(result)
    
    def test_format_vehicle_info(self):
        """Test vehicle info formatting."""
        vehicle_info = {
            'Make': 'Nissan',
            'Model': 'Silvia',
            'ModelYear': '2002'
        }
        
        formatted = self.decoder.format_vehicle_info(vehicle_info)
        
        self.assertIn('Nissan', formatted)
        self.assertIn('Silvia', formatted)
        self.assertIn('2002', formatted)


if __name__ == '__main__':
    unittest.main()
