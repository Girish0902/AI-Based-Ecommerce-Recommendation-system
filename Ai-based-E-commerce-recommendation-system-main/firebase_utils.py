
import pandas as pd
import os
import json

FIREBASE_AVAILABLE = False
USERS_FILE = "users.json"

def initialize_firebase_app():
    pass

# ── Local User Store (replaces Firebase /users node) ──────────────────────────

def _load_users() -> dict:
    """Load users from local JSON file."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_users(users: dict) -> bool:
    """Persist users to local JSON file."""
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
        return True
    except Exception:
        return False

# ── Wishlist Store ─────────────────────────────────────────────────────────────

WISHLIST_FILE = "wishlists.json"

def _load_wishlists() -> dict:
    if os.path.exists(WISHLIST_FILE):
        try:
            with open(WISHLIST_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_wishlists(data: dict) -> bool:
    try:
        with open(WISHLIST_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False

# ── Public API (matches original firebase_utils interface) ─────────────────────

def load_local_csv():
    """Load data from local CSV file."""
    csv_files = ['clean_data.csv', 'cleaned_data.csv']
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                if df is not None and not df.empty:
                    return df
            except Exception:
                continue
    return None

def get_data_from_firebase():
    """Load product data (local CSV fallback)."""
    return load_local_csv()

def get_users_from_firebase() -> dict:
    """Return all registered users keyed by user_id string."""
    return _load_users()

def save_user_to_firebase(user_data: dict) -> bool:
    """Save a new user. Returns True on success."""
    users = _load_users()
    uid = str(user_data.get("user_id", ""))
    if not uid:
        return False
    users[uid] = {
        "user_id": user_data.get("user_id"),
        "email": user_data.get("email", ""),
        "password": user_data.get("password", ""),
    }
    return _save_users(users)

def get_wishlist_from_firebase(user_id) -> list:
    """Return wishlist for a given user_id."""
    wishlists = _load_wishlists()
    return wishlists.get(str(user_id), [])

def update_wishlist_in_firebase(user_id, wishlist_items) -> bool:
    """Persist wishlist for a given user_id."""
    wishlists = _load_wishlists()
    wishlists[str(user_id)] = wishlist_items
    return _save_wishlists(wishlists)
