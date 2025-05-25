#!/usr/bin/env python3
"""
Simple test script to verify CSV loading and basic functionality
"""

import csv
import json

def test_csv_loading():
    """Test if CSV can be loaded"""
    try:
        with open('GM Pricing March Website Usage -Final.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = list(reader)
        
        print(f"✅ CSV loaded successfully: {len(data)} rows")
        print(f"Columns: {list(data[0].keys()) if data else 'No data'}")
        
        # Test data structure
        if data:
            sample = data[0]
            print(f"\nSample record:")
            print(f"  Fuel Type: {sample.get('FuelType', 'N/A')}")
            print(f"  Car Brand: {sample.get('Car Brand', 'N/A')}")
            print(f"  Car Model: {sample.get('Car Model', 'N/A')}")
            print(f"  Periodic Service Price: {sample.get('Periodic Service Price GaadiMech', 'N/A')}")
        
        # Get unique values
        brands = sorted(list(set(record['Car Brand'] for record in data)))
        fuel_types = sorted(list(set(record['FuelType'] for record in data)))
        
        print(f"\nUnique brands ({len(brands)}): {brands[:5]}...")
        print(f"Unique fuel types: {fuel_types}")
        
        # Test search functionality
        print(f"\n🔍 Testing search for 'petrol Maruti Swift':")
        for record in data:
            if (record['FuelType'].lower() == 'petrol' and
                record['Car Brand'].lower() == 'maruti' and
                record['Car Model'].lower() == 'swift'):
                print(f"✅ Found match:")
                print(f"  Periodic Service: ₹{record['Periodic Service Price GaadiMech']}")
                print(f"  Express Service: ₹{record['Express Service Price GaadiMech']}")
                print(f"  Discounted Price: ₹{record['Discounted Price']}")
                break
        else:
            print("❌ No match found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return False

def test_api_logic():
    """Test the API logic without Flask"""
    print(f"\n🧪 Testing API logic...")
    
    # Simulate API request
    request_data = {
        "CarManufacturer": "Maruti",
        "CarModel": "Swift", 
        "FuelType": "petrol"
    }
    
    print(f"Request: {json.dumps(request_data, indent=2)}")
    
    # Load data
    try:
        with open('GM Pricing March Website Usage -Final.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            pricing_data = list(reader)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False
    
    # Search logic
    car_manufacturer = request_data['CarManufacturer'].strip()
    car_model = request_data['CarModel'].strip()
    fuel_type = request_data['FuelType'].strip()
    
    matching_record = None
    for record in pricing_data:
        if (record['FuelType'].lower() == fuel_type.lower() and
            record['Car Brand'].lower() == car_manufacturer.lower() and
            record['Car Model'].lower() == car_model.lower()):
            matching_record = record
            break
    
    if matching_record:
        print(f"✅ Found matching record!")
        
        # Clean price function
        def clean_price(price_str):
            if not price_str or price_str.strip() == '' or price_str == '#N/A':
                return "Not Available"
            try:
                cleaned = ''.join(c for c in str(price_str) if c.isdigit() or c == '.')
                if cleaned:
                    return str(int(float(cleaned)))
                return "Not Available"
            except:
                return "Not Available"
        
        response = {
            "success": True,
            "data": {
                "car_details": {
                    "fuel_type": matching_record['FuelType'],
                    "brand": matching_record['Car Brand'],
                    "model": matching_record['Car Model']
                },
                "service_prices": {
                    "periodic_service": {
                        "price": clean_price(matching_record['Periodic Service Price GaadiMech']),
                        "description": "Regular maintenance service"
                    },
                    "express_service": {
                        "price": clean_price(matching_record['Express Service Price GaadiMech']),
                        "description": "Quick service option"
                    },
                    "discounted_price": {
                        "price": clean_price(matching_record['Discounted Price']),
                        "description": "Special discounted rate"
                    },
                    "comprehensive_service": {
                        "price": clean_price(matching_record['Comprehensive Service Price GaadiMech']),
                        "description": "Complete service package"
                    }
                },
                "paint_services": {
                    "dent_and_paint": {
                        "price": clean_price(matching_record['Dent & Paint Price GaadiMech']),
                        "description": "Dent repair and painting"
                    },
                    "full_body_paint": {
                        "price": clean_price(matching_record['Dent and Paint Full Body']),
                        "description": "Complete body painting"
                    }
                }
            }
        }
        
        print(f"Response: {json.dumps(response, indent=2)}")
        return True
    else:
        print(f"❌ No matching record found")
        return False

if __name__ == "__main__":
    print("🚀 Testing GaadiMech Pricing Webhook Components")
    print("=" * 60)
    
    success1 = test_csv_loading()
    success2 = test_api_logic()
    
    if success1 and success2:
        print(f"\n✅ All tests passed! The webhook should work correctly.")
        print(f"\n📝 Next steps:")
        print(f"1. Run: source venv/bin/activate && python app_simple.py")
        print(f"2. Test with: curl http://localhost:5000/health")
        print(f"3. Deploy to a free hosting platform")
    else:
        print(f"\n❌ Some tests failed. Please check the issues above.") 