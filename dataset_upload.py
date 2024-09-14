import pandas as pd
from pymongo import MongoClient

# Load the dataset
df = pd.read_excel(r"C:\Users\R.SANTOSH\Documents\ai_bot\static\data\water.xlsx")

# Rename columns based on the dataset inspection
df.columns = ['Cropcode', 'Product', 'Green', 'Blue', 'Grey', 'Total']

# Drop rows with NaN in the 'Product' column
df.dropna(subset=['Product'], inplace=True)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['crop_bot']
collection = db['cropdata']

# Insert the data into MongoDB
data_dict = df.to_dict("records")
collection.insert_many(data_dict)

print("Data successfully inserted into MongoDB!")
