import pandas as pd
import numpy as np

from backend.cleaning_data import process_data
from backend.rating_based import get_top_rated_items
from backend.content_filtering import content_based_recommendation
from backend.collaborative_filtering import collaborative_filtering_recommendations

def hybrid_recommendation_filtering(data:pd.DataFrame, item_name:str, target_user_id:int, top_n:int = 10):
    content_based_rec = content_based_recommendation(data,item_name, top_n)
    collaborative_based_rec=collaborative_filtering_recommendations(data, target_user_id, top_n)
    hybrid_approach = (pd.concat([content_based_rec, collaborative_based_rec]).drop_duplicates().head(top_n))
    return hybrid_approach

if __name__ == "__main__":
    from firebase_utils import get_data_from_firebase
    # Fetch from Firebase
    raw_data = get_data_from_firebase()
    if raw_data is not None:
         data = process_data(raw_data)
    else:
         print("Failed to load data")
         exit()
    from backend.cleaning_data import process_data

    item_name = "OPI Infinite Shine, Nail Lacquer Nail Polish, Bubble Bath"
    target_user_id = 5
    top_n = 5

    hybrid_rec = hybrid_recommendation_filtering(data, item_name, target_user_id, top_n)
    print(hybrid_rec)
