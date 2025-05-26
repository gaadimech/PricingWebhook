from flask import Flask, request, jsonify
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Convert CSV to optimized JSON structure for faster lookups
def create_optimized_data():
    """Create an optimized data structure from CSV for faster lookups"""
    import csv
    
    try:
        with open('GM Pricing March Website Usage -Final.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = list(reader)
        
        # Create nested dictionary for O(1) lookups: fuel_type -> brand -> model -> prices
        optimized = {}
        brands = set()
        fuel_types = set()
        
        for record in data:
            fuel = record['FuelType'].lower()
            brand = record['Car Brand'].lower()
            model = record['Car Model'].lower()
            
            fuel_types.add(record['FuelType'])
            brands.add(record['Car Brand'])
            
            if fuel not in optimized:
                optimized[fuel] = {}
            if brand not in optimized[fuel]:
                optimized[fuel][brand] = {}
            
            # Clean and store prices
            def clean_price(price_str):
                if not price_str or price_str.strip() == '' or price_str == '#N/A':
                    return None
                try:
                    cleaned = ''.join(c for c in str(price_str) if c.isdigit() or c == '.')
                    return int(float(cleaned)) if cleaned else None
                except:
                    return None
            
            optimized[fuel][brand][model] = {
                'original_fuel': record['FuelType'],
                'original_brand': record['Car Brand'],
                'original_model': record['Car Model'],
                'periodic_service': clean_price(record['Periodic Service Price GaadiMech']),
                'express_service': clean_price(record['Express Service Price GaadiMech']),
                'discounted_price': clean_price(record['Discounted Price']),
                'comprehensive_service': clean_price(record['Comprehensive Service Price GaadiMech']),
                'dent_paint': clean_price(record['Dent & Paint Price GaadiMech']),
                'full_body_paint': clean_price(record['Dent and Paint Full Body'])
            }
        
        # Save optimized data to JSON file
        result = {
            'data': optimized,
            'brands': sorted(list(brands)),
            'fuel_types': sorted(list(fuel_types)),
            'total_records': len(data)
        }
        
        with open('pricing_data.json', 'w') as f:
            json.dump(result, f, separators=(',', ':'))  # Compact JSON
        
        print(f"✅ Optimized data created: {len(data)} records")
        return result
        
    except Exception as e:
        print(f"❌ Error creating optimized data: {e}")
        return None

# Try to load existing optimized data, create if doesn't exist
try:
    with open('pricing_data.json', 'r') as f:
        pricing_data = json.load(f)
    
    # Calculate stats from the new structure
    total_records = sum(
        sum(len(models) for models in brands.values()) 
        for brands in pricing_data['data'].values()
    )
    
    # Extract unique brands and fuel types
    brands = set()
    fuel_types = list(pricing_data['data'].keys())
    
    for fuel_data in pricing_data['data'].values():
        for brand_data in fuel_data.values():
            for model_data in brand_data.values():
                brands.add(model_data['original_brand'])
    
    # Add metadata to pricing_data for compatibility
    pricing_data['total_records'] = total_records
    pricing_data['brands'] = sorted(list(brands))
    pricing_data['fuel_types'] = fuel_types
    
    print(f"✅ Loaded optimized data: {total_records} records, {len(brands)} brands, {len(fuel_types)} fuel types")
    
except FileNotFoundError:
    print("📦 Creating optimized data structure...")
    pricing_data = create_optimized_data()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "GaadiMech Pricing Webhook API - Optimized",
        "status": "active",
        "data_loaded": pricing_data is not None,
        "total_records": pricing_data['total_records'] if pricing_data else 0,
        "total_brands": len(pricing_data['brands']) if pricing_data else 0,
        "endpoints": {
            "/get-price": "POST - Get pricing information",
            "/get-brands": "GET - Get available car brands", 
            "/get-models": "POST - Get models for a brand",
            "/get-fuel-types": "GET - Get available fuel types",
            "/health": "GET - Health check"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "data_loaded": pricing_data is not None,
        "total_records": pricing_data['total_records'] if pricing_data else 0
    })

@app.route('/get-price', methods=['POST'])
def get_price():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "message": "Please provide JSON data with CarManufacturer, CarModel, and FuelType"
            }), 400
        
        car_manufacturer = data.get('CarManufacturer', '').strip()
        car_model = data.get('CarModel', '').strip() 
        fuel_type = data.get('FuelType', '').strip()
        
        if not all([car_manufacturer, car_model, fuel_type]):
            return jsonify({
                "error": "Missing required parameters",
                "message": "Please provide CarManufacturer, CarModel, and FuelType",
                "received": {
                    "CarManufacturer": car_manufacturer,
                    "CarModel": car_model,
                    "FuelType": fuel_type
                }
            }), 400
        
        if not pricing_data:
            return jsonify({
                "error": "Data not available",
                "message": "Pricing data could not be loaded"
            }), 500
        
        # Fast O(1) lookup - find exact fuel type match (case-insensitive)
        fuel_key = None
        for available_fuel in pricing_data['data'].keys():
            if fuel_type.lower() == available_fuel.lower():
                fuel_key = available_fuel
                break
        
        brand_key = car_manufacturer.lower()
        model_key = car_model.lower()
        
        if (fuel_key and fuel_key in pricing_data['data'] and 
            brand_key in pricing_data['data'][fuel_key] and
            model_key in pricing_data['data'][fuel_key][brand_key]):
            
            record = pricing_data['data'][fuel_key][brand_key][model_key]
            
            def format_price(price):
                return str(price) if price is not None else "Not Available"
            
            response = {
                "success": True,
                "data": {
                    "car_details": {
                        "fuel_type": record['original_fuel'],
                        "brand": record['original_brand'],
                        "model": record['original_model']
                    },
                    "service_prices": {
                        "periodic_service": {
                            "price": format_price(record['periodic_service']),
                            "description": "Regular maintenance service"
                        },
                        "express_service": {
                            "price": format_price(record['express_service']),
                            "description": "Quick service option"
                        },
                        "discounted_price": {
                            "price": format_price(record['discounted_price']),
                            "description": "Special discounted rate"
                        },
                        "comprehensive_service": {
                            "price": format_price(record['comprehensive_service']),
                            "description": "Complete service package"
                        }
                    },
                    "paint_services": {
                        "dent_and_paint": {
                            "price": format_price(record['dent_paint']),
                            "description": "Dent repair and painting"
                        },
                        "full_body_paint": {
                            "price": format_price(record['full_body_paint']),
                            "description": "Complete body painting"
                        }
                    }
                }
            }
            
            return jsonify(response)
        
        else:
            # Find suggestions
            suggestions = {
                "similar_brands": [],
                "similar_models": []
            }
            
            # Look for partial matches
            for brand in pricing_data['brands']:
                if car_manufacturer.lower() in brand.lower():
                    suggestions["similar_brands"].append(brand)
            
            return jsonify({
                "error": "No matching record found",
                "message": f"No pricing data found for {fuel_type} {car_manufacturer} {car_model}",
                "suggestions": suggestions
            }), 404
            
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/get-brands', methods=['GET'])
def get_brands():
    try:
        if not pricing_data:
            return jsonify({"error": "Data not available"}), 500
        
        return jsonify({
            "success": True,
            "brands": pricing_data['brands']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-models', methods=['POST'])
def get_models():
    try:
        data = request.get_json()
        brand = data.get('CarManufacturer', '').strip()
        
        if not brand:
            return jsonify({"error": "CarManufacturer is required"}), 400
        
        if not pricing_data:
            return jsonify({"error": "Data not available"}), 500
        
        models = set()
        brand_key = brand.lower()
        
        # Search across all fuel types for this brand
        for fuel_data in pricing_data['data'].values():
            if brand_key in fuel_data:
                for model_key, model_data in fuel_data[brand_key].items():
                    models.add(model_data['original_model'])
        
        return jsonify({
            "success": True,
            "brand": brand,
            "models": sorted(list(models))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-fuel-types', methods=['GET'])
def get_fuel_types():
    try:
        if not pricing_data:
            return jsonify({"error": "Data not available"}), 500
        
        return jsonify({
            "success": True,
            "fuel_types": pricing_data['fuel_types']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 