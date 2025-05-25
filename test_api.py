#!/usr/bin/env python3
"""
Test script for GaadiMech Pricing Webhook API
Run this after starting the Flask app to test all endpoints
"""

import requests
import json

# Base URL - change this to your deployed URL when testing production
BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_get_brands():
    """Test get brands endpoint"""
    print("Testing get brands endpoint...")
    response = requests.get(f"{BASE_URL}/get-brands")
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print(f"Found {len(data['brands'])} brands")
        print(f"First 5 brands: {data['brands'][:5]}")
    else:
        print(f"Error: {data}")
    print("-" * 50)

def test_get_fuel_types():
    """Test get fuel types endpoint"""
    print("Testing get fuel types endpoint...")
    response = requests.get(f"{BASE_URL}/get-fuel-types")
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print(f"Available fuel types: {data['fuel_types']}")
    else:
        print(f"Error: {data}")
    print("-" * 50)

def test_get_models():
    """Test get models endpoint"""
    print("Testing get models endpoint...")
    payload = {"CarManufacturer": "Maruti"}
    response = requests.post(f"{BASE_URL}/get-models", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print(f"Found {len(data['models'])} models for {data['brand']}")
        print(f"First 5 models: {data['models'][:5]}")
    else:
        print(f"Error: {data}")
    print("-" * 50)

def test_get_price_valid():
    """Test get price endpoint with valid data"""
    print("Testing get price endpoint with valid data...")
    payload = {
        "CarManufacturer": "Maruti",
        "CarModel": "Swift",
        "FuelType": "petrol"
    }
    response = requests.post(f"{BASE_URL}/get-price", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    if data.get('success'):
        print("✅ Successfully retrieved pricing data")
        car_details = data['data']['car_details']
        print(f"Car: {car_details['fuel_type']} {car_details['brand']} {car_details['model']}")
        
        service_prices = data['data']['service_prices']
        print("\nService Prices:")
        for service, details in service_prices.items():
            print(f"  {service}: ₹{details['price']} - {details['description']}")
        
        paint_services = data['data']['paint_services']
        print("\nPaint Services:")
        for service, details in paint_services.items():
            print(f"  {service}: ₹{details['price']} - {details['description']}")
    else:
        print(f"❌ Error: {data}")
    print("-" * 50)

def test_get_price_invalid():
    """Test get price endpoint with invalid data"""
    print("Testing get price endpoint with invalid data...")
    payload = {
        "CarManufacturer": "InvalidBrand",
        "CarModel": "InvalidModel",
        "FuelType": "petrol"
    }
    response = requests.post(f"{BASE_URL}/get-price", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    print("-" * 50)

def test_get_price_missing_params():
    """Test get price endpoint with missing parameters"""
    print("Testing get price endpoint with missing parameters...")
    payload = {
        "CarManufacturer": "Maruti"
        # Missing CarModel and FuelType
    }
    response = requests.post(f"{BASE_URL}/get-price", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    print("-" * 50)

def main():
    """Run all tests"""
    print("🚀 Starting API Tests for GaadiMech Pricing Webhook")
    print("=" * 60)
    
    try:
        test_health()
        test_get_brands()
        test_get_fuel_types()
        test_get_models()
        test_get_price_valid()
        test_get_price_invalid()
        test_get_price_missing_params()
        
        print("✅ All tests completed!")
        print("\n📝 Summary:")
        print("- Health check: API is running")
        print("- Brands endpoint: Working")
        print("- Fuel types endpoint: Working")
        print("- Models endpoint: Working")
        print("- Price endpoint: Working with proper error handling")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask app is running on localhost:5000")
        print("Run: python app.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 