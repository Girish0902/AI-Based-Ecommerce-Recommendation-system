import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def item_based_collaborative_filtering(data, product_id, top_n=5):
    """
    Returns recommendations based on Item-Item Collaborative Filtering.
    (People who liked 'product_id' also liked...)
    """
    # 1. Create User-Item Matrix
    # Rows: Users, Columns: Products
    user_item_matrix = data.pivot_table(index='ID', columns='ProdID', values='Rating', aggfunc='mean').fillna(0)
    
    # 2. Check if product exists in matrix
    if product_id not in user_item_matrix.columns:
        return pd.DataFrame()
    
    # 3. Calculate Item-Item Similarity
    # Transpose to get Item-User matrix, so cosine_similarity calculates similarity between items
    item_user_matrix = user_item_matrix.T
    item_similarity_matrix = cosine_similarity(item_user_matrix)
    item_similarity_df = pd.DataFrame(item_similarity_matrix, index=item_user_matrix.index, columns=item_user_matrix.index)
    
    # 4. Get similar items
    similar_items = item_similarity_df[product_id].sort_values(ascending=False)
    
    # Filter out the item itself and get top N
    similar_items = similar_items.drop(product_id).head(top_n)
    
    # 5. Get details of recommended items
    recommended_prod_ids = similar_items.index.tolist()
    recommended_items_details = data[data['ProdID'].isin(recommended_prod_ids)][['Name','ReviewCount','Brand','ImageURL','Rating','ProdID']]
    
    # Drop duplicates in case data has multiple entries per product
    recommended_items_details = recommended_items_details.drop_duplicates(subset=['ProdID'])
    
    return recommended_items_details

if __name__ == "__main__":
    # Test
    try:
        from firebase_utils import get_data_from_firebase
        raw_data = get_data_from_firebase()
        # Fetch from Firebase
        # Ensure we have ProdID in data if it wasn't there originally or created in process_data
        # Assuming process_data or raw data has 'ProdID' based on previous context. 
        # If not, we might need to rely on 'Name' or create IDs.
        # Based on collaborative_based_filtering.py, 'ProdID' exists.
        
        test_prod_id = raw_data['ProdID'].iloc[0]
        print(f"Testing recommendations for {test_prod_id}...")
        recs = item_based_collaborative_filtering(raw_data, test_prod_id)
        print(recs)
    except Exception as e:
        print(f"Test failed: {e}")
