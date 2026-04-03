
import pandas as pd
import numpy as np



def process_data(data: pd.DataFrame) -> pd.DataFrame:
    # --- Rename non-standard columns ---
    if "User's ID" in data.columns:
        data = data.rename(columns={"User's ID": "ID"})
    if "Product_Display_Name" in data.columns and "Name" not in data.columns:
        data = data.rename(columns={"Product_Display_Name": "Name"})
    if "Review Count" in data.columns:
        data = data.rename(columns={"Review Count": "ReviewCount"})

    # Replace invalid values with NaN
    data['ProdID'] = data['ProdID'].replace(-2147483648, np.nan)
    data['ID'] = data['ID'].replace(-2147483648, np.nan)

    # Convert ID to numeric and clean
    data['ID'] = pd.to_numeric(data['ID'], errors='coerce')
    data = data.dropna(subset=['ID'])

    # Clean ProdID
    data = data.dropna(subset=['ProdID'])
    
    # Remove rows where ID or ProdID is 0
    data = data[(data['ID'] != 0) & (data['ProdID'] != 0)].copy()

    data['ID'] = data['ID'].astype('int64')
    data['ProdID'] = data['ProdID'].astype('int64')

    # ReviewCount
    if 'ReviewCount' in data.columns:
        data['ReviewCount'] = pd.to_numeric(
            data['ReviewCount'], errors='coerce'
        ).fillna(0).astype('int64')
    else:
        data['ReviewCount'] = 0

    # Drop unwanted column if exists
    if 'Unnamed: 0' in data.columns:
        data = data.drop(columns=['Unnamed: 0'])

    # Fill text columns
    for col in ['Category', 'Brand', 'Description', 'Tags']:
        if col in data.columns:
            data[col] = data[col].fillna('')
        else:
            data[col] = ''

    return data
