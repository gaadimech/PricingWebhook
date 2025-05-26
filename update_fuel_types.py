#!/usr/bin/env python3
"""
Script to update fuel types in pricing data:
- petrol → Petrol/CNG
- diesel → Diesel (keep as is)
- cng → EV
"""

import json
import os

def update_fuel_types():
    # Read the current JSON file
    with open('pricing_data.json', 'r') as f:
        data = json.load(f)
    
    # Create new data structure with updated fuel types
    new_data = {"data": {}}
    
    # Mapping for fuel type changes (case-sensitive based on actual data)
    fuel_type_mapping = {
        "petrol": "Petrol/CNG",
        "Petrol/CNG": "Petrol/CNG",  # In case it's already updated
        "diesel": "Diesel",
        "Diesel": "Diesel",  # In case it's already updated
        "cng": "EV",
        "CNG": "EV"  # In case it's already updated
    }
    
    # Process each fuel type
    for old_fuel_type, brands in data["data"].items():
        # Get the new fuel type name
        new_fuel_type = fuel_type_mapping.get(old_fuel_type, old_fuel_type)
        
        # Initialize the new fuel type section if it doesn't exist
        if new_fuel_type not in new_data["data"]:
            new_data["data"][new_fuel_type] = {}
        
        # Copy all brand data under the new fuel type
        for brand, models in brands.items():
            if brand not in new_data["data"][new_fuel_type]:
                new_data["data"][new_fuel_type][brand] = {}
            
            for model, pricing in models.items():
                # Update the original_fuel field in each model's data
                updated_pricing = pricing.copy()
                updated_pricing["original_fuel"] = new_fuel_type
                
                new_data["data"][new_fuel_type][brand][model] = updated_pricing
    
    # Backup the original file
    if os.path.exists('pricing_data_backup.json'):
        os.remove('pricing_data_backup.json')
    os.rename('pricing_data.json', 'pricing_data_backup.json')
    
    # Write the updated data
    with open('pricing_data.json', 'w') as f:
        json.dump(new_data, f, separators=(',', ':'))
    
    print("✅ Fuel types updated successfully!")
    print("📋 Changes made:")
    print("   • petrol → Petrol/CNG")
    print("   • diesel → Diesel")
    print("   • cng → EV")
    print("📁 Original file backed up as 'pricing_data_backup.json'")

if __name__ == "__main__":
    update_fuel_types() 