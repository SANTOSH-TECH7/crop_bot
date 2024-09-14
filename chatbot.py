from pymongo import MongoClient
from fuzzywuzzy import process
import re

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.crop_bot  # Use your database name
collection = db.cropdata  # Use your collection name where the data is stored

# Helper function to check if a string can be converted to float
def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Fetch water footprint data from MongoDB
def get_water_footprints():
    data = collection.find({}, {'_id': 0})  # Fetch all documents excluding the '_id' field
    water_footprints = {}
    for doc in data:
        if is_float(doc['Green']) and is_float(doc['Blue']) and is_float(doc['Grey']) and is_float(doc['Total']):
            product = doc['Product']
            water_footprints[product] = {
                'Green': float(doc['Green']),  # Convert only if valid
                'Blue': float(doc['Blue']),    # Convert only if valid
                'Grey': float(doc['Grey']),    # Convert only if valid
                'Total': float(doc['Total'])   # Convert only if valid
            }
    return water_footprints

water_footprints = get_water_footprints()

def get_product_info(product_name):
    # Extract and normalize product names from the dataset
    products = water_footprints.keys()

    # Find the best match using fuzzy matching
    best_match, score = process.extractOne(product_name, products)

    if score < 80:  # Adjust threshold as needed
        return None, "Product not found. Please try another one."

    return best_match, None

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

    return (f"For {quantity} kg of {product}:\n"
            f"- Green Water Footprint: {green_total:.2f} liters\n"
            f"- Blue Water Footprint: {blue_total:.2f} liters\n"
            f"- Grey Water Footprint: {grey_total:.2f} liters\n"
            f"- Total Water Footprint: {total_total:.2f} liters")

print("Welcome to the Water Footprint Chatbot!")
print("You can ask about the water footprint of any product.")
print("For example, you can say 'Give me the water footprint for 5 kg of rice' or 'rice 5'.")

while True:
    user_input = input("Enter a product description and quantity or type 'exit' to quit: ").strip().lower()

    if user_input == 'exit':
        break

    # Extract product and quantity from the user input
    match = re.match(r'(.*?)(\d+)\s*kg$', user_input)

    if match:
        product_name = match.group(1).strip()
        try:
            quantity = float(match.group(2))
        except ValueError:
            print("Invalid quantity. Please enter a numeric value followed by 'kg'.")
            continue

        # Get the best matching product
        product_name, error = get_product_info(product_name)

        if error:
            print(error)
        else:
            result = calculate_water_footprint(product_name, quantity)
            print(result)
    else:
        print("Invalid input format. Please enter the product description followed by 'kg'.")

print("Thank you for using the Water Footprint Chatbot!")
