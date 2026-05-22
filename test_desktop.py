"""
Desktop test script for VIN Reader.
Tests core functionality without Android-specific features.
"""

from obd_manager import OBDManager
from vin_decoder import VINDecoder


def test_vin_decoder():
    """Test VIN decoder with a sample VIN."""
    print("=== Testing VIN Decoder ===")
    
    decoder = VINDecoder()
    
    # Test with a known VIN (Nissan Silvia S15 2002)
    test_vin = "JN1BLNU16U0200001"  # Example VIN
    
    print(f"Testing VIN: {test_vin}")
    result = decoder.decode(test_vin)
    
    if result:
        print("✓ VIN decoded successfully!")
        print(f"Make: {result.get('Make')}")
        print(f"Model: {result.get('Model')}")
        print(f"Year: {result.get('ModelYear')}")
        print(f"Formatted Name: {result.get('FormattedName')}")
    else:
        print("✗ Failed to decode VIN")
    
    return result is not None


def test_obd_connection():
    """Test OBD connection (requires actual device)."""
    print("\n=== Testing OBD Connection ===")
    
    obd = OBDManager()
    
    print("Attempting to connect to OBD-II adapter...")
    connected = obd.connect()
    
    if connected:
        print("✓ Connected successfully!")
        
        # Test connection
        success, message = obd.test_connection()
        print(f"Connection test: {message}")
        
        # Try to read VIN
        print("Attempting to read VIN...")
        vin = obd.read_vin()
        
        if vin:
            print(f"✓ VIN read successfully: {vin}")
            
            # Decode the VIN
            decoder = VINDecoder()
            vehicle_info = decoder.decode(vin)
            
            if vehicle_info:
                print(f"✓ Vehicle info: {vehicle_info.get('FormattedName')}")
            else:
                print("✗ Failed to decode VIN")
        else:
            print("✗ Failed to read VIN (may not be supported by vehicle)")
        
        obd.disconnect()
    else:
        print("✗ Failed to connect to OBD-II adapter")
        print("Make sure:")
        print("  - OBD-II adapter is powered on")
        print("  - Bluetooth is enabled")
        print("  - Adapter is paired with computer")
    
    return connected


def main():
    """Run all tests."""
    print("VIN Reader Desktop Test Suite")
    print("=" * 40)
    
    # Test VIN decoder (doesn't require hardware)
    decoder_passed = test_vin_decoder()
    
    # Test OBD connection (requires hardware)
    print("\n" + "=" * 40)
    print("OBD Connection Test")
    print("This test requires an actual OBD-II adapter connected via Bluetooth")
    response = input("Do you want to test OBD connection? (y/n): ")
    
    if response.lower() == 'y':
        obd_passed = test_obd_connection()
    else:
        print("Skipping OBD connection test")
        obd_passed = None
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"VIN Decoder: {'✓ PASSED' if decoder_passed else '✗ FAILED'}")
    
    if obd_passed is not None:
        print(f"OBD Connection: {'✓ PASSED' if obd_passed else '✗ FAILED'}")
    else:
        print("OBD Connection: SKIPPED")
    
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Test with actual OBD-II device")
    print("3. Build APK: buildozer android debug")


if __name__ == "__main__":
    main()
