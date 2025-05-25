from flask import Flask, request, jsonify
import csv
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variable to store the data
pricing_data = []

def load_pricing_data():
    """Load CSV data using built-in csv module"""
    global pricing_data
    try:
        with open('GM Pricing March Website Usage -Final.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            pricing_data = list(reader)
        print(f"✅ CSV loaded successfully: {len(pricing_data)} rows")
        return True
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return False

# Load data on startup
data_loaded = load_pricing_data()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "GaadiMech Pricing Webhook API",
        "status": "active",
        "data_loaded": data_loaded,
        "total_records": len(pricing_data),
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
        "data_loaded": data_loaded,
        "total_records": len(pricing_data)
    })

@app.route('/get-price', methods=['POST'])
def get_price():
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided",
                "message": "Please provide JSON data with CarManufacturer, CarModel, and FuelType"
            }), 400
        
        # Extract parameters
        car_manufacturer = data.get('CarManufacturer', '').strip()
        car_model = data.get('CarModel', '').strip()
        fuel_type = data.get('FuelType', '').strip()
        
        # Validate required parameters
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
        
        if not data_loaded or not pricing_data:
            return jsonify({
                "error": "Data not available",
                "message": "Pricing data could not be loaded"
            }), 500
        
        # Search for matching record (case-insensitive)
        matching_record = None
        for record in pricing_data:
            if (record['FuelType'].lower() == fuel_type.lower() and
                record['Car Brand'].lower() == car_manufacturer.lower() and
                record['Car Model'].lower() == car_model.lower()):
                matching_record = record
                break
        
        if not matching_record:
            # Try to find similar matches for better error message
            similar_brands = set()
            similar_models = set()
            
            for record in pricing_data:
                if car_manufacturer.lower() in record['Car Brand'].lower():
                    similar_brands.add(record['Car Brand'])
                if car_model.lower() in record['Car Model'].lower():
                    similar_models.add(record['Car Model'])
            
            return jsonify({
                "error": "No matching record found",
                "message": f"No pricing data found for {fuel_type} {car_manufacturer} {car_model}",
                "suggestions": {
                    "similar_brands": list(similar_brands)[:5],
                    "similar_models": list(similar_models)[:5]
                }
            }), 404
        
        # Clean up price values
        def clean_price(price_str):
            if not price_str or price_str.strip() == '' or price_str == '#N/A':
                return "Not Available"
            try:
                # Remove any non-numeric characters except decimal point
                cleaned = ''.join(c for c in str(price_str) if c.isdigit() or c == '.')
                if cleaned:
                    return str(int(float(cleaned)))
                return "Not Available"
            except:
                return "Not Available"
        
        # Prepare response with all pricing information
        pricing_info = {
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
        
        return jsonify({
            "success": True,
            "data": pricing_info
        })
        
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/get-brands', methods=['GET'])
def get_brands():
    """Get list of available car brands"""
    try:
        if not data_loaded or not pricing_data:
            return jsonify({"error": "Data not available"}), 500
        
        brands = sorted(list(set(record['Car Brand'] for record in pricing_data)))
        return jsonify({
            "success": True,
            "brands": brands
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-models', methods=['POST'])
def get_models():
    """Get list of available models for a specific brand"""
    try:
        data = request.get_json()
        brand = data.get('CarManufacturer', '').strip()
        
        if not brand:
            return jsonify({"error": "CarManufacturer is required"}), 400
        
        if not data_loaded or not pricing_data:
            return jsonify({"error": "Data not available"}), 500
        
        models = []
        for record in pricing_data:
            if record['Car Brand'].lower() == brand.lower():
                models.append(record['Car Model'])
        
        models = sorted(list(set(models)))
        
        return jsonify({
            "success": True,
            "brand": brand,
            "models": models
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-fuel-types', methods=['GET'])
def get_fuel_types():
    """Get list of available fuel types"""
    try:
        if not data_loaded or not pricing_data:
            return jsonify({"error": "Data not available"}), 500
        
        fuel_types = sorted(list(set(record['FuelType'] for record in pricing_data)))
        return jsonify({
            "success": True,
            "fuel_types": fuel_types
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 