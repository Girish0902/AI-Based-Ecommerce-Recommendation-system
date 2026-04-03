import pandas as pd
def get_top_rated_items(data:pd.DataFrame, top_n: int=10) -> pd.DataFrame:
        """Returns top N products based on average rating."""
        average_ratings = (data.groupby(['ProdID', 'Name','ReviewCount','Brand','ImageURL'])
                   ['Rating'].mean().reset_index())
        top_rated_items = average_ratings.sort_values(by = 'Rating', ascending=False)
        return top_rated_items.head(top_n)

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
        print(get_top_rated_items(data))
