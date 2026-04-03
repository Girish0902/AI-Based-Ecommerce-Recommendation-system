
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import numpy as np
import os
import streamlit as st

# Setup credentials (reusing logic from firebase_utils)
def init_firebase():
    if not firebase_admin._apps:
        if os.path.exists('serviceAccountKey.json'):
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://ai-based-recommendation-55bcb-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
        else:
            print("No serviceAccountKey.json found!")
            return False
    return True

def migrate_ids():
    if not init_firebase():
        return

    print("Fetching data...")
    ref_products = db.reference('/products')
    data = ref_products.get()
    
    if not data:
        print("No product data found.")
        return

    # Convert to DataFrame
    if isinstance(data, list):
        data = [x for x in data if x is not None]
        df = pd.DataFrame(data)
    else:
        print("Data format not recognized (expected list).")
        return

    print(f"Original records: {len(df)}")
    
    # Check if 'Name' exists
    if 'Name' not in df.columns:
        print("Column 'Name' not found. Cannot deduplicate.")
        return

    # 1. Create a Mapping: Unique Product (Name + Brand) -> New Serial ID
    # We clean Name/Brand to ensure better matching
    df['Name_Clean'] = df['Name'].astype(str).str.strip().str.lower()
    df['Brand_Clean'] = df['Brand'].astype(str).str.strip().str.lower() if 'Brand' in df.columns else ''
    
    # Identify unique products
    unique_products = df.drop_duplicates(subset=['Name_Clean', 'Brand_Clean'])
    unique_products = unique_products.sort_values(by=['Name_Clean']) # Sort for clean 1..N order
    
    # Assign New IDs
    unique_products['New_ProdID'] = range(1, len(unique_products) + 1)
    
    # Create mapping dictionary
    # Map (Name_Clean, Brand_Clean) -> New_ProdID
    # Also Map Old_ProdID -> New_ProdID (This is tricky if Old_ProdID 100 maps to Soap AND Shampoo - inconsistency. 
    # But we map primarily by Name).
    
    # Let's map strict Name+Brand to ID
    id_map = dict(zip(zip(unique_products['Name_Clean'], unique_products['Brand_Clean']), unique_products['New_ProdID']))
    
    # Also need OLD ID to NEW ID map for updating Wishlists
    # Since multiple Old IDs might map to one New ID (consolidation), or one Old ID might split (if named differently),
    # We have to be careful. Wishlist stores Old_ProdID.
    # We need a fallback map: Old_ProdID -> Most common New_ProdID for that ID?
    # Or iterate the original DF: For each row, we have Old ID and New ID.
    
    print("Mapping IDs...")
    
    # Apply New IDs to dataframe
    def get_new_id(row):
        n = str(row['Name']).strip().lower()
        b = str(row['Brand']).strip().lower() if 'Brand' in row else ''
        return id_map.get((n, b))

    df['ProdID_New'] = df.apply(get_new_id, axis=1)
    
    # Generate Old -> New Map for Wishlists
    # Logic: For each Old ID, find what New ID it corresponds to.
    # If Old ID maps to multiple (data inconsistency), pick the most frequent one?
    old_to_new_map = {}
    
    # We iterate unique pairs of (ProdID, ProdID_New) in the DF
    mapping_df = df[['ProdID', 'ProdID_New']].drop_duplicates()
    
    # Check for conflicts
    # If an Old ProdID maps to multiple New ProdIDs (meaning Old ID 100 was used for both "Soap" and "Car"),
    # we can't perfectly migrate wishlist without knowing which one they meant.
    # We will assume Old IDs generally point to one product type.
    
    for _, row in mapping_df.iterrows():
        old = row['ProdID']
        new = row['ProdID_New']
        if old not in old_to_new_map:
            old_to_new_map[old] = new
        else:
            # Conflict! 
            pass
            
    # Update Dataframe ProdID
    df['ProdID'] = df['ProdID_New']
    
    # Clean up temp cols
    final_df = df.drop(columns=['Name_Clean', 'Brand_Clean', 'ProdID_New', 'New_ProdID'], errors='ignore')
    
    print("Updating /products database...")
    records = final_df.to_dict(orient='records')
    ref_products.set(records)
    print("Products updated.")
    
    # 2. Update Wishlists
    print("Updating User Wishlists...")
    ref_users = db.reference('/users')
    users_data = ref_users.get()
    
    if users_data:
        updated_count = 0
        for uid, udata in users_data.items():
            if 'wishlist' in udata and isinstance(udata['wishlist'], list):
                old_list = udata['wishlist']
                new_list = []
                changed = False
                for oid in old_list:
                    # Wishlist items might be strings or ints
                    # Try to match typeless
                    matched = False
                    for existing_old, mapped_new in old_to_new_map.items():
                        if str(existing_old) == str(oid):
                            new_list.append(mapped_new)
                            matched = True
                            break
                    if not matched:
                        # Keep it if we can't map it? Or drop?
                        # If ID doesn't exist in new map, it was a ghost product. Drop it.
                        print(f"Warning: User {uid} has item {oid} not found in product list.")
                        changed = True # It's changed because we're dropping it
                    
                if new_list != old_list:
                    ref_users.child(uid).child('wishlist').set(new_list)
                    updated_count += 1
        
        print(f"Updated wishlists for {updated_count} users.")
    else:
        print("No users found.")

    print("Migration Complete.")

if __name__ == "__main__":
    migrate_ids()
