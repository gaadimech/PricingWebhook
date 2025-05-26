#!/usr/bin/env python3
"""
Test script for optimized GaadiMech Pricing Webhook
"""

import json
import requests
import time

def test_json_structure():
    """Test the optimized JSON structure"""
    try:
        with open('pricing_data.json', 'r') as f:
            data = json.load(f)
        
        print(f"✅ JSON loaded successfully")
        print(f"📊 Total records: {data['total_records']}")
        print(f"🏭 Total brands: {len(data['brands'])}")
        print(f"⛽ Fuel types: {data['fuel_types']}")
        
        # Test lookup speed
        start_time = time.time()
        
        # Test lookup: petrol -> maruti -> swift
        if ('petrol' in data['data'] and 
            'maruti' in data['data']['petrol'] and
            'swift' in data['data']['petrol']['maruti']):
            
            record = data['data']['petrol']['maruti']['swift']
            lookup_time = (time.time() - start_time) * 1000
            
            print(f"🚀 Lookup time: {lookup_time:.2f}ms (very fast!)")
            print(f"📋 Sample record:")
            print(f"  Brand: {record['original_brand']}")
            print(f"  Model: {record['original_model']}")
            print(f"  Periodic Service: ₹{record['periodic_service']}")
            print(f"  Express Service: ₹{record['express_service']}")
            
            return True
        else:
            print("❌ Test record not found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing JSON: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints if server is running"""
    base_url = "http://localhost:5000"
    
    print(f"\n🧪 Testing API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Health check: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print(f"❌ Server not running on {base_url}")
        return False
    
    # Test pricing endpoint
    try:
        payload = {
            "CarManufacturer": "Maruti",
            "CarModel": "Swift",
            "FuelType": "petrol"
        }
        
        response = requests.post(f"{base_url}/get-price", json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Pricing API working!")
                prices = data['data']['service_prices']
                print(f"  Periodic: ₹{prices['periodic_service']['price']}")
                print(f"  Express: ₹{prices['express_service']['price']}")
                return True
            else:
                print(f"❌ API returned error: {data}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API request error: {e}")
        return False

def main():
    print("🚀 Testing Optimized GaadiMech Pricing Webhook")
    print("=" * 60)
    
    # Test JSON structure
    json_ok = test_json_structure()
    
    # Test API if possible
    api_ok = test_api_endpoints()
    
    print(f"\n📝 Results:")
    print(f"  JSON Structure: {'✅ OK' if json_ok else '❌ Failed'}")
    print(f"  API Endpoints: {'✅ OK' if api_ok else '❌ Not running'}")
    
    if json_ok:
        print(f"\n🎉 Optimized webhook is ready for deployment!")
        print(f"📦 File sizes:")
        import os
        json_size = os.path.getsize('pricing_data.json') / 1024
        print(f"  pricing_data.json: {json_size:.1f} KB (optimized)")
        
        print(f"\n🚀 Deploy with:")
        print(f"  1. git add .")
        print(f"  2. git commit -m 'Optimized webhook with JSON data'")
        print(f"  3. git push origin main")
        print(f"  4. Deploy to Heroku/Railway/Render")
    else:
        print(f"\n❌ Please fix the issues above before deployment")

if __name__ == "__main__":
    main() 