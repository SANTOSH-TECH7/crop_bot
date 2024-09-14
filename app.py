from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from fuzzywuzzy import process
import traceback

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['crop_bot']
collection = db['cropdata']

# Helper function to check if a value is float
def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Fetch water footprint data from MongoDB
def get_water_footprints():
    data = collection.find({}, {'_id': 0})  # Fetch crop data
    water_footprints = {}
    for doc in data:
        if is_float(doc['Green']) and is_float(doc['Blue']) and is_float(doc['Grey']) and is_float(doc['Total']):
            product = doc['Product']
            water_footprints[product] = {
                'Green': float(doc['Green']),
                'Blue': float(doc['Blue']),
                'Grey': float(doc['Grey']),
                'Total': float(doc['Total'])
            }
    return water_footprints

water_footprints = get_water_footprints()

# Fuzzy matching function for product
def get_product_info(product_name):
    products = water_footprints.keys()
    best_match, score = process.extractOne(product_name, products)
    if score < 80:  # Adjust threshold if needed
        return None, "Product not found. Please try another one."
    return best_match, None

# Water footprint calculation logic
def calculate_water_footprint(product, quantity):
    product_info = water_footprints.get(product)
    if not product_info:
        return "Product not found. Please try another one."
    
    green = product_info['Green']
    blue = product_info['Blue']
    grey = product_info['Grey']
    total = product_info['Total']

    green_total = green * quantity
    blue_total = blue * quantity
    grey_total = grey * quantity
    total_total = total * quantity

    return {
        'green_water': green_total,
        'blue_water': blue_total,
        'grey_water': grey_total,
        'total_water': total_total
    }

# Home route to display the form and pass crops to the template
@app.route('/')
def index():
    crops = list(water_footprints.keys())  # List all crops from the database
    return render_template('index.html', crops=crops)  # Render HTML with the crops list

# API to calculate water footprint
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()  # Get JSON data from POST request
        product_name = data.get('product')
        quantity = data.get('quantity')

        if not product_name or not quantity:  # Validate inputs
            return jsonify({'error': 'Invalid input'})

        # Get best product match using fuzzy matching
        best_match, error = get_product_info(product_name)
        if error:
            return jsonify({'error': error})

        # Calculate water footprint
        result = calculate_water_footprint(best_match, float(quantity))
        return jsonify(result)  # Return result as JSON

    except Exception as e:
        print("Error:", e)
        print(traceback.format_exc())
        return jsonify({'error': 'An error occurred. Please try again.'})

if __name__ == '__main__':
    import logging
    from logging.handlers import RotatingFileHandler

    # Configure logging
    handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
