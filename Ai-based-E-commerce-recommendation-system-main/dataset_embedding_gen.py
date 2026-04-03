
import os
import pandas as pd
import numpy as np
import torch
from transformers import CLIPProcessor, CLIPModel

# Run this script LOCALLY to update 'text_embeddings_cache.npy'
# whenever you change your dataset.

from firebase_utils import get_data_from_firebase, initialize_firebase_app
from backend.cleaning_data import process_data

def generate_embeddings():
    print("Initializing Firebase...")
    initialize_firebase_app()
    
    print("Loading Data...")
    raw_data = get_data_from_firebase()
    if raw_data is None:
        print("Failed to load data.")
        return
    data = process_data(raw_data)
    
    print(f"Loaded {len(data)} items. Preparing Model...")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # we use the OpenAI version locally as it loads reliably with 'transformers'
    model_name = "openai/clip-vit-large-patch14"
    model = CLIPModel.from_pretrained(model_name).to(device)
    processor = CLIPProcessor.from_pretrained(model_name)
    
    print("Generating Embeddings...")
    
    data_filled = data.fillna('')
    literals = (data_filled['Brand'] + " " + data_filled['Name'] + " " + data_filled['Category']).astype(str).tolist()
    
    batch_features = []
    batch_size = 64
    total = len(literals)
    
    for i in range(0, total, batch_size):
        print(f"Processing {i}/{total}...")
        batch_text = literals[i:i+batch_size]
        
        inputs = processor(text=batch_text, return_tensors="pt", padding=True, truncation=True).to(device)
        
        with torch.no_grad():
            outputs = model.get_text_features(**inputs)
            
            # Fix: 'outputs' is a Tensor for get_text_features, but strictly speaking 
            # some versions return an object if return_dict=True (default).
            # However, prompt shows it is BaseModelOutput... so we must access tensor.
            # Actually, get_text_features usually returns a Tensor directly, 
            # BUT if we used model(...) it would be an object.
            # Let's handle both just in case, but based on error 'BaseModelOutputWithPooling', 
            # it implies we might have called something else or transformers changed.
            # wait, CLIPModel.get_text_features SHOULD return a torch.FloatTensor.
            # IF it is returning an object, we should check text_embeds.
            
            if hasattr(outputs, 'text_embeds'):
                 features = outputs.text_embeds
            elif hasattr(outputs, 'pooler_output'):
                 features = outputs.pooler_output
            else:
                 # If it is already a tensor (which get_text_features usually is)
                 features = outputs
                 
            # Normalize
            features = features / features.norm(p=2, dim=-1, keepdim=True)
            batch_features.append(features.cpu().numpy())
            
    if batch_features:
        all_features = np.concatenate(batch_features, axis=0)
        np.save("text_embeddings_cache.npy", all_features)
        print("Success! Saved to text_embeddings_cache.npy")
    else:
        print("No features generated.")

if __name__ == "__main__":
    generate_embeddings()
