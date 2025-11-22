"""Test script to debug hidden costs API issue"""

import requests

def test_hidden_costs_api():
    """Test the hidden costs API endpoint"""
    try:
        # First, get all vehicles
        print("Fetching vehicles...")
        vehicles_resp = requests.get("http://theconeportal.net:5000/fleet_control/vehicle_list", timeout=15)
        vehicles_resp.raise_for_status()
        vehicles = vehicles_resp.json()
        print(f"Found {len(vehicles)} vehicles")
        
        # Test hidden costs for each vehicle
        for vehicle in vehicles:
            vehicle_name = vehicle.get("name", str(vehicle)) if isinstance(vehicle, dict) else str(vehicle)
            print(f"\nTesting hidden costs for vehicle: {vehicle_name}")
            
            try:
                hidden_url = "http://theconeportal.net:5000/fleet_control/vehicle_hidden_costs"
                hidden_resp = requests.get(hidden_url, params={"vehicle_name": vehicle_name}, timeout=15)
                print(f"  Response status: {hidden_resp.status_code}")
                hidden_resp.raise_for_status()
                
                hidden_data = hidden_resp.json()
                print(f"  Raw response: {hidden_data}")
                print(f"  Response type: {type(hidden_data)}")
                
                if not isinstance(hidden_data, list):
                    hidden_data = [hidden_data] if hidden_data else []
                
                print(f"  Found {len(hidden_data)} hidden cost records")
                
                for i, record in enumerate(hidden_data):
                    print(f"    Record {i}: {record}")
                    if isinstance(record, dict):
                        # Check different possible field names
                        for field in ['amount', 'cost', 'price']:
                            if field in record:
                                print(f"      {field}: {record[field]}")
                                
            except Exception as e:
                print(f"  Error: {e}")
                
    except Exception as e:
        print(f"Failed to test API: {e}")

if __name__ == "__main__":
    test_hidden_costs_api()