from flask import Flask, request, jsonify
import pandas as pd
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the CSV data
def load_pricing_data():
    try:
        df = pd.read_csv('GM Pricing March Website Usage -Final.csv')
        # Clean column names (remove extra spaces)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

# Global variable to store the data
pricing_data = load_pricing_data()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "GaadiMech Pricing Webhook API",
        "status": "active",
        "endpoints": {
            "/get-price": "POST - Get pricing information",
            "/health": "GET - Health check"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "data_loaded": pricing_data is not None})

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
        
        if pricing_data is None:
            return jsonify({
                "error": "Data not available",
                "message": "Pricing data could not be loaded"
            }), 500
        
        # Search for matching record (case-insensitive)
        filtered_data = pricing_data[
            (pricing_data['FuelType'].str.lower() == fuel_type.lower()) &
            (pricing_data['Car Brand'].str.lower() == car_manufacturer.lower()) &
            (pricing_data['Car Model'].str.lower() == car_model.lower())
        ]
        
        if filtered_data.empty:
            # Try to find similar matches for better error message
            similar_brands = pricing_data[pricing_data['Car Brand'].str.lower().str.contains(car_manufacturer.lower(), na=False)]['Car Brand'].unique()
            similar_models = pricing_data[pricing_data['Car Model'].str.lower().str.contains(car_model.lower(), na=False)]['Car Model'].unique()
            
            return jsonify({
                "error": "No matching record found",
                "message": f"No pricing data found for {fuel_type} {car_manufacturer} {car_model}",
                "suggestions": {
                    "similar_brands": similar_brands.tolist()[:5] if len(similar_brands) > 0 else [],
                    "similar_models": similar_models.tolist()[:5] if len(similar_models) > 0 else []
                }
            }), 404
        
        # Get the first matching record
        record = filtered_data.iloc[0]
        
        # Prepare response with all pricing information
        pricing_info = {
            "car_details": {
                "fuel_type": record['FuelType'],
                "brand": record['Car Brand'],
                "model": record['Car Model']
            },
            "service_prices": {
                "periodic_service": {
                    "price": record['Periodic Service Price GaadiMech'],
                    "description": "Regular maintenance service"
                },
                "express_service": {
                    "price": record['Express Service Price GaadiMech'],
                    "description": "Quick service option"
                },
                "discounted_price": {
                    "price": record['Discounted Price'],
                    "description": "Special discounted rate"
                },
                "comprehensive_service": {
                    "price": record['Comprehensive Service Price GaadiMech'],
                    "description": "Complete service package"
                }
            },
            "paint_services": {
                "dent_and_paint": {
                    "price": record['Dent & Paint Price GaadiMech'],
                    "description": "Dent repair and painting"
                },
                "full_body_paint": {
                    "price": record['Dent and Paint Full Body'],
                    "description": "Complete body painting"
                }
            }
        }
        
        # Clean up any NaN values
        def clean_price(price):
            if pd.isna(price) or price == '#N/A':
                return "Not Available"
            return str(int(price)) if isinstance(price, (int, float)) else str(price)
        
        # Apply cleaning to all prices
        for category in pricing_info["service_prices"]:
            pricing_info["service_prices"][category]["price"] = clean_price(pricing_info["service_prices"][category]["price"])
        
        for category in pricing_info["paint_services"]:
            pricing_info["paint_services"][category]["price"] = clean_price(pricing_info["paint_services"][category]["price"])
        
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
        if pricing_data is None:
            return jsonify({"error": "Data not available"}), 500
        
        brands = sorted(pricing_data['Car Brand'].unique().tolist())
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
        
        if pricing_data is None:
            return jsonify({"error": "Data not available"}), 500
        
        models = pricing_data[pricing_data['Car Brand'].str.lower() == brand.lower()]['Car Model'].unique().tolist()
        models = sorted(models)
        
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
        if pricing_data is None:
            return jsonify({"error": "Data not available"}), 500
        
        fuel_types = sorted(pricing_data['FuelType'].unique().tolist())
        return jsonify({
            "success": True,
            "fuel_types": fuel_types
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 