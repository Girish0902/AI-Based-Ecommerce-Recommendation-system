# evaluation_metrics.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from firebase_utils import get_data_from_firebase
data = get_data_from_firebase()
if data is None:
    print("Failed to load data")
    exit()

from backend.cleaning_data import process_data

def train_test_split_by_user(data, test_size=0.2):
    train_data = []
    test_data = []

    for user_id, user_df in data.groupby("ID"):
        if len(user_df) < 5:
            continue
        train, test = train_test_split(user_df, test_size=test_size, random_state=42)
        train_data.append(train)
        test_data.append(test)

    return pd.concat(train_data), pd.concat(test_data)

def get_relevant_items(test_data, user_id):
    return set(
        test_data[
            (test_data["ID"] == user_id) &
            (test_data["Rating"] >= 4)
        ]["ProdID"]
    )

def collaborative_filtering_recommendations_ids(data, target_user_id, top_n=10):
    user_item_matrix = data.pivot_table(
        index='ID', columns='ProdID', values='Rating', aggfunc='mean'
    ).fillna(0)

    user_similarity = cosine_similarity(user_item_matrix)
    target_user_index = user_item_matrix.index.get_loc(target_user_id)

    similar_users = user_similarity[target_user_index].argsort()[::-1][1:]
    recommended_items = []

    for user_index in similar_users:
        rated_items = user_item_matrix.iloc[user_index]
        not_rated = (rated_items > 0) & (user_item_matrix.iloc[target_user_index] == 0)
        recommended_items.extend(user_item_matrix.columns[not_rated])

    return list(dict.fromkeys(recommended_items))[:top_n]

def precision_recall_at_k(recommended_items, relevant_items):
    if not recommended_items:
        return 0.0, 0.0

    recommended_items = set(recommended_items)

    true_positives = recommended_items & relevant_items

    precision = len(true_positives) / len(recommended_items)
    recall = len(true_positives) / len(relevant_items) if relevant_items else 0.0

    return precision, recall

def evaluate_model(data):
    train_data, test_data = train_test_split_by_user(data)

    precisions = []
    recalls = []

    for user_id in test_data["ID"].unique():
        relevant_items = get_relevant_items(test_data, user_id)
        if not relevant_items:
            continue

        recommended_items = collaborative_filtering_recommendations_ids(
            train_data, user_id, top_n=20
        )

        precision, recall = precision_recall_at_k(
            recommended_items, relevant_items
        )

        precisions.append(precision)
        recalls.append(recall)

    return np.mean(precisions), np.mean(recalls)

precision, recall = evaluate_model(data)

print(f"Precision@10: {precision:.4f}")
print(f"Recall@10: {recall:.4f}")