#main.py
import pandas as pd
import numpy as np

from backend.cleaning_data import process_data
from backend.rating_based import get_top_rated_items
from backend.content_filtering import content_based_recommendation
from backend.collaborative_filtering import collaborative_filtering_recommendations
from backend.hybrid import hybrid_recommendation_filtering

# Load raw data
# Load raw data
from firebase_utils import get_data_from_firebase
raw_data = get_data_from_firebase()
if raw_data is None:
    print("Failed to load data")
    exit()

# Process data
data = process_data(raw_data)


# Get top 10 rated products
rating_based_recommendation = get_top_rated_items(data, top_n=10)
print("Rating-based recommendations:")
rating_based_recommendation


# To get content based recommended items
item_name = 'OPI Infinite Shine, Nail Lacquer Nail Polish, Bubble Bath'
content_based_recom = content_based_recommendation(data, item_name, top_n = 8)
print("\nContent-based recommendations:")
content_based_recom

# To get Collaborative based recommended items
target_user_id = 4
collaborative_filtering_rec = collaborative_filtering_recommendations(data, target_user_id, 
                                                                      top_n = 5)
print("\nCollaborative filtering recommendations:")
collaborative_filtering_rec

# Hybrid recommendation
hybrid_rec = hybrid_recommendation_filtering(
    data,
    item_name=item_name,
    target_user_id=target_user_id,
    top_n=5
)

# Fallback if hybrid is empty
if hybrid_rec.empty:
    print("\nHybrid was empty, showing top-rated items instead")
    hybrid_rec = get_top_rated_items(data, top_n=5)

print("\nHybrid recommendations:")
hybrid_rec