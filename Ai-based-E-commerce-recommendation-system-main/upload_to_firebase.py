
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import pandas as pd
import json
import os

# 1. Initialize Firebase
# Make sure serviceAccountKey.json is in the same directory
cred = credentials.Certificate('serviceAccountKey.json')

# Initialize with the provided DB URL
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ai-based-recommendation-55bcb-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

def upload_data():
    print("Reading CSV...")
    try:
        df = pd.read_csv('clean_data.csv')
        
        # Replace NaN with safe values (Firebase doesn't like NaNs)
        df = df.fillna("")
        
        # Convert to dictionary format
        # orient='records' gives a list of dicts: [{}, {}, ...]
        records = df.to_dict(orient='records')
        
        print(f"Uploading {len(records)} products to Firebase...")
        
        # Get reference to the root/products node
        ref = db.reference('/products')
        
        # Set the data (this overwrites existing data at this path)
        ref.set(records)
        
        print("Upload successful! ✅")
        
    except FileNotFoundError:
        print("Error: Dataset file not found!")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    upload_data()
