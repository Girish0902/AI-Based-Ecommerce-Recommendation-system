import os
import requests
import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
print(f"HF_TOKEN present: {bool(HF_TOKEN)}")

# Test Image
img = Image.new('RGB', (100, 100), color = 'red')
img_byte_arr = BytesIO()
img.save(img_byte_arr, format='PNG')
img_bytes = img_byte_arr.getvalue()
encoded = base64.b64encode(img_bytes).decode("utf-8")

API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/clip-ViT-B-32"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

print(f"Attempting POST to {API_URL}")

try:
    response = requests.post(API_URL, headers=headers, json={"inputs": encoded}, timeout=10)
    print(f"Response Code: {response.status_code}")
    print(f"Response HEADERS: {response.headers}")
    if response.status_code != 200:
        print(f"Response Text: {response.text}")
    else:
        print("Success!")
except Exception as e:
    print("\n!!! EXCEPTION CAUGHT !!!")
    print(f"Type: {type(e)}")
    print(f"Message: {e}")
    
    # Check for proxy env vars
    print("\nProxy Environment Variables:")
    for k, v in os.environ.items():
        if "PROXY" in k.upper():
            print(f"{k}: {v}")
