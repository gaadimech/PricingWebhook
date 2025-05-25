# GaadiMech Pricing Webhook API

A Flask-based webhook API that provides car service pricing information for integration with Wati chatbot.

## Features

- Fetch pricing information based on Car Manufacturer, Car Model, and Fuel Type
- Multiple service packages: Periodic, Express, Comprehensive, Discounted
- Paint services: Dent & Paint, Full Body Paint
- Helper endpoints to get available brands, models, and fuel types
- CORS enabled for web integration
- Error handling with helpful suggestions

## API Endpoints

### 1. Get Pricing Information
**POST** `/get-price`

Request body:
```json
{
  "CarManufacturer": "Maruti",
  "CarModel": "Swift",
  "FuelType": "petrol"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "car_details": {
      "fuel_type": "petrol",
      "brand": "Maruti",
      "model": "Swift"
    },
    "service_prices": {
      "periodic_service": {
        "price": "2999",
        "description": "Regular maintenance service"
      },
      "express_service": {
        "price": "3299",
        "description": "Quick service option"
      },
      "discounted_price": {
        "price": "2799",
        "description": "Special discounted rate"
      },
      "comprehensive_service": {
        "price": "4599",
        "description": "Complete service package"
      }
    },
    "paint_services": {
      "dent_and_paint": {
        "price": "2499",
        "description": "Dent repair and painting"
      },
      "full_body_paint": {
        "price": "20900",
        "description": "Complete body painting"
      }
    }
  }
}
```

### 2. Get Available Brands
**GET** `/get-brands`

Response:
```json
{
  "success": true,
  "brands": ["Audi", "BMW", "Chevrolet", "Citroen", ...]
}
```

### 3. Get Models for a Brand
**POST** `/get-models`

Request body:
```json
{
  "CarManufacturer": "Maruti"
}
```

### 4. Get Available Fuel Types
**GET** `/get-fuel-types`

Response:
```json
{
  "success": true,
  "fuel_types": ["petrol", "Diesel", "CNG"]
}
```

### 5. Health Check
**GET** `/health`

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Free Deployment Options

### Option 1: Heroku (Recommended)

1. Create a Heroku account at https://heroku.com
2. Install Heroku CLI
3. Deploy:
```bash
git init
git add .
git commit -m "Initial commit"
heroku create your-app-name
git push heroku main
```

### Option 2: Railway

1. Go to https://railway.app
2. Connect your GitHub repository
3. Deploy automatically

### Option 3: Render

1. Go to https://render.com
2. Connect your GitHub repository
3. Choose "Web Service"
4. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

### Option 4: PythonAnywhere (Free tier available)

1. Upload files to PythonAnywhere
2. Set up a web app with Flask
3. Configure WSGI file

## Wati Integration

Once deployed, use your webhook URL in Wati:

1. **Webhook URL**: `https://your-app-url.herokuapp.com/get-price`
2. **Method**: POST
3. **Headers**: `Content-Type: application/json`
4. **Body**: 
```json
{
  "CarManufacturer": "{{CarManufacturer}}",
  "CarModel": "{{CarModel}}",
  "FuelType": "{{FuelType}}"
}
```

## Testing the API

You can test the API using curl:

```bash
# Test pricing endpoint
curl -X POST https://your-app-url.herokuapp.com/get-price \
  -H "Content-Type: application/json" \
  -d '{
    "CarManufacturer": "Maruti",
    "CarModel": "Swift",
    "FuelType": "petrol"
  }'

# Test health endpoint
curl https://your-app-url.herokuapp.com/health
```

## Error Handling

The API provides detailed error messages:
- Missing parameters
- Invalid car/model/fuel combinations
- Suggestions for similar matches
- Server errors

## Data Source

The pricing data is loaded from `GM Pricing March Website Usage -Final.csv` which contains:
- Car brands and models
- Fuel types (Petrol, Diesel, CNG)
- Service pricing for different packages
- Paint service pricing

## Support

For issues or questions, please check the logs or contact the development team. 