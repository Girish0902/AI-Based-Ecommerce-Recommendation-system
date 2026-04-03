import streamlit as st
import pandas as pd
import numpy as np
import os
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# -----------------------------
# Configuration
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_NAME = "openai/clip-vit-large-patch14"

# -----------------------------
# Load CLIP model (Cached)
# -----------------------------
@st.cache_resource
def load_clip_model():
    model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    return model, processor

# -----------------------------
# Feature Extraction
# -----------------------------
def get_image_features(image, model, processor):
    """
    Extracts features using local transformers model.
    """
    try:
        inputs = processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.get_image_features(**inputs)
            
            # Safe extraction for various return types
            if hasattr(outputs, 'image_embeds'):
                outputs = outputs.image_embeds
            elif hasattr(outputs, 'pooler_output'):
                outputs = outputs.pooler_output
            
            # Normalize
            outputs = outputs / outputs.norm(p=2, dim=-1, keepdim=True)
            return outputs.cpu().numpy()
    except Exception as e:
        st.error(f"Error extracting features: {e}")
        return None

def get_dataset_features(data):
    """
    Loads pre-computed embeddings from file.
    Warning: These MUST match the dimensions of the currently loaded model (768 for ViT-L/14).
    """
    try:
        if os.path.exists("text_embeddings_cache.npy"):
            all_features = np.load("text_embeddings_cache.npy")
            
            # Dimension Check (Heuristic)
            # ViT-Base-32 = 512, ViT-Large-14 = 768
            # If we are using Large, and cache is 512, we must warn.
            if all_features.shape[1] != 768:
                st.warning(f"⚠️ Embedding Catch Mismatch! Cache is {all_features.shape[1]}d, Model is 768d. Please regenerate embeddings using 'dataset_embedding_gen.py'.")
                return np.array([]), []

            if len(all_features) == len(data):
                return all_features, data.index.tolist()
            else:
                st.warning("Data/Cache length mismatch. Using partial match.")
                min_len = min(len(all_features), len(data))
                return all_features[:min_len], data.index.tolist()[:min_len]
        return np.array([]), []
    except Exception as e:
        st.error(f"Error loading cache: {e}")
        return np.array([]), []

def recommend_by_image(uploaded_image, data=None, top_n=5):
    """
    Main function to be called from the Streamlit App.
    """
    # 1. Load Data
    if data is None:
        from firebase_utils import get_data_from_firebase
        from backend.cleaning_data import process_data
        
        raw_data = get_data_from_firebase()
        if raw_data is None or raw_data.empty:
            st.error("No data available.")
            return pd.DataFrame()
        data = process_data(raw_data)
    
    # 2. Get Features (Cached)
    dataset_features, valid_indices = get_dataset_features(data)
    
    if len(dataset_features) == 0:
        st.error("Embedding cache missing or invalid dimensions. Please regenerate.")
        return pd.DataFrame()

    # 3. Load Model
    with st.spinner("Loading AI Model (openai/clip-vit-large-patch14)..."):
        model, processor = load_clip_model()

    # 4. Process Query Image
    with st.spinner("Analyzing image..."):
        query_features_np = get_image_features(uploaded_image, model, processor)
        
    if query_features_np is None:
        return pd.DataFrame()
        
    try:
        # Squeeze if needed
        if query_features_np.ndim > 1:
            query_features_np = query_features_np.flatten()
            
        # 5. Compute Similarity
        # (N, D) @ (D,) -> (N,)
        similarities = (dataset_features @ query_features_np)
        
        # 6. Get Top N
        top_indices_local = similarities.argsort()[::-1][:top_n]
        top_df_indices = [valid_indices[i] for i in top_indices_local]
        safe_indices = [i for i in top_df_indices if i in data.index]
        
        recommended_df = data.loc[safe_indices].copy()
        return recommended_df
        
    except Exception as e:
        st.error(f"Processing Error: {e}")
        # Debug info
        st.write(f"Cache Shape: {dataset_features.shape}")
        st.write(f"Query Shape: {query_features_np.shape}")
        return pd.DataFrame()

# Placeholder
def get_text_embeddings(text):
    return None