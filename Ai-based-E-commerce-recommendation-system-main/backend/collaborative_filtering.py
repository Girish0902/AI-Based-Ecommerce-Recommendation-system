import pandas as pd
import sklearn
from sklearn.metrics.pairwise import cosine_similarity

def collaborative_filtering_recommendations(data, target_user_id, top_n = 10):
  user_item_matrix = data.pivot_table(index= 'ID', columns='ProdID', values='Rating', aggfunc= 'mean').fillna(0)
  
  if target_user_id not in user_item_matrix.index:
      return pd.DataFrame()
      
  user_similarity = cosine_similarity(user_item_matrix)
  target_user_index = user_item_matrix.index.get_loc(target_user_id)
  user_similarities = user_similarity[target_user_index]
  similar_users_indices = user_similarities.argsort()[::-1][1:]
  recommended_items = []

  for user_index in similar_users_indices:
    rated_by_similar_user = user_item_matrix.iloc[user_index]
    not_rated_by_target_user = (rated_by_similar_user!=0) & (user_item_matrix.iloc[target_user_index]==0)

    recommended_items.extend(user_item_matrix.columns[not_rated_by_target_user][:top_n])
  recommended_items_details = data[data['ProdID'].isin(recommended_items)][['ProdID', 'Name', 'ImageURL', 'Brand', 'Rating', 'ReviewCount']]
  return recommended_items_details


#Example usage
if __name__ == "__main__":
    import pandas as pd
    from firebase_utils import get_data_from_firebase
    from preprocess_data import process_data

    # Fetch from Firebase
    raw_data = get_data_from_firebase()
    if raw_data is not None:
        data = process_data(raw_data)
    else:
        print("Failed to load data")
        exit()

    target_user_id = 4
    print(collaborative_filtering_recommendations(data, target_user_id))