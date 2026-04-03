import pandas as pd
import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
def content_based_recommendation(data, item_name, top_n=10):
    if item_name not in data['Name'].values:
        print(f"item '{item_name}' not found in the data.")
        return pd.DataFrame()
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix_content = tfidf_vectorizer.fit_transform(data['Tags'])
    cosine_similarity_content = cosine_similarity(tfidf_matrix_content, tfidf_matrix_content)
    # Find the index LABEL of the item
    item_label_index = data[data['Name']==item_name].index[0]
    # Convert LABEL to POSITION (for matrix access)
    item_position = data.index.get_loc(item_label_index)
    
    similar_items = list(enumerate(cosine_similarity_content[item_position]))
    similar_prod = sorted(similar_items, key=lambda x:x[1], reverse=True)
    top_similar_prod = similar_prod[:top_n]
    recommended_items_indices = [x[0] for x in top_similar_prod]
    recommended_item_details = data.iloc[recommended_items_indices][['ProdID', 'Name', 'ImageURL', 'Brand', 'Rating', 'ReviewCount']]
    return recommended_item_details
# Then write this in the same file

# TO test the system
if __name__ == "__main__":
    import pandas as pd
    from firebase_utils import get_data_from_firebase
    from preprocess_data import process_data

    # Fetch from Firebase
    raw_data = get_data_from_firebase()
    if raw_data is not None:
        data = process_data(raw_data)
    else:
        print("Failed to load data from Firebase")
        exit()
    item_name = "OPI Infinite Shine, Nail Lacquer Nail Polish, Bubble Bath"
    result = content_based_recommendation(data, item_name, top_n=5)
    print(result)
