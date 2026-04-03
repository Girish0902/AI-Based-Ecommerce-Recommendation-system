# 🚀 AI-Store: AI-Enabled Recommendation Engine for E-Commerce Platform

## Project Overview

**AI-Store** is a full-stack e-commerce application built with **Streamlit** that uses **Machine Learning** to provide personalized product recommendations. The platform combines three AI recommendation algorithms to deliver the best shopping experience.

---

## 🎯 Core Features

### 1. **AI-Powered Recommendations** (3 Algorithms)
   - **Rating-Based** → For new users (top-rated products globally)
   - **Collaborative Filtering** → For existing users (similar users' preferences)
   - **Content-Based** → Product similarity using product tags/features
   - **Hybrid Approach** → Combines all three intelligently based on user context

### 2. **User Authentication**
   - Firebase authentication (email/password signup & login)
   - Tracks user sessions with unique `user_id` and `firebase_uid`
   - Differentiates between "new users" and "returning users" for appropriate recommendations

### 3. **E-Commerce Features**
   - Product catalog with search functionality
   - Shopping cart system with persistent state
   - Wishlist to save favorite items
   - Order tracking and history
   - Checkout with payment integration (Razorpay)
   - User profile management

### 4. **AI Chatbot Assistant**
   - Powered by **Groq API** (LLaMA 3.1 8B model)
   - Provides product recommendations via natural language
   - Shows top-rated products with clickable links
   - Helps users make purchasing decisions

---

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | streamlit  (Python-based, compiles to React) |
| **Backend** | Python + Pandas + Scikit-learn |
| **ML Models** | Collaborative Filtering, Content-Based, Rating-Based |
| **Database/Auth** | Firebase Realtime DB + Firebase Auth |
| **Payment** | Razorpay API |
| **AI Chatbot** | Groq API + LLaMA 3.1 model |
| **Data** | CSV (cleaned_data.csv) with 5.69 MB dataset |
| **Deployment** | Reflex Cloud (reflex.run) |

---

## 🏗️ Architecture

### **Folder Structure**

```
AI-Store/
├── app.py                 # Main Reflex app entry point
├── rxconfig.py            # Reflex configuration
├── config.py              # Shared configuration (DATA_PATH)
├── cleaned_data.csv       # ML dataset (5.69 MB)
├── requirements.txt       # Python dependencies
│
├── backend/               # ML algorithms & recommendation engine
│   ├── recommender.py     # Main orchestrator (combines 3 algorithms)
│   ├── collaborative_filtering.py  # User-user similarity
│   ├── content_filtering.py        # Product-product similarity (TF-IDF)
│   ├── rating_based.py            # Top-rated products for new users
│   ├── cleaning_data.py   # Data preprocessing
│   └── __init__.py
│
├── state/                 # Reflex state management (reactive data)
│   ├── user_state.py      # User auth, session, login/signup
│   ├── recommendation_state.py    # ML recommendations display
│   ├── products_state.py  # Product search & filtering
│   ├── cart_state.py      # Shopping cart logic
│   ├── wishlist_state.py  # Wishlist management
│   └── payment_state.py   # Payment status tracking
│
├── pages/                 # Frontend pages (routes)
│   ├── home.py           # Landing page with recommendations
│   ├── login.py          # Firebase login
│   ├── signup.py         # Firebase registration
│   ├── product_detail.py # Single product view
│   ├── cart.py           # Shopping cart display
│   ├── checkout.py       # Order summary & checkout
│   ├── payment.py        # Razorpay payment page
│   ├── profile.py        # User profile & settings
│   ├── wishlist.py       # Saved products
│   └── orders.py         # Order history
│
├── components/            # Reusable UI components
│   ├── navbar.py         # Navigation bar with search
│   ├── product_card.py   # Product display card
│   └── chatbot.py        # Floating AI assistant
│
└── assets/               # Static images, icons, etc.
```

---

## 🤖 ML Recommendation System

### **How It Works**

```
User visits app
    ↓
Is user logged in? NO → Is new user? YES → Use Rating-Based
                                            (Top-rated products globally)
                      ↓
                Use Collaborative Filtering
                (Find similar users, recommend their favorite products)
                      ↓
                Is user viewing a product? YES → Blend with Content-Based
                (Find similar products using TF-IDF tags)
                      ↓
                Return combined recommendations
```

### **Three Algorithms Explained**

#### **1️⃣ Rating-Based (for new users)**
- **Logic**: Average product ratings
- **Use Case**: First-time visitors
- **Pros**: No cold-start problem
- **Data**: Group products → calculate mean rating → sort descending

```python
product_stats = df.groupby('ProdID').agg({
    'Rating': 'mean',  # Average rating
    "User's ID": 'count'  # Number of reviews
})
```

#### **2️⃣ Collaborative Filtering (user-user similarity)**
- **Logic**: Find users similar to you, recommend what they liked
- **Use Case**: Returning users
- **Algorithm**: 
  1. Create user-item matrix (users × products → ratings)
  2. Calculate cosine similarity between users
  3. Find top similar users
  4. Recommend products they rated highly but you haven't seen

```python
user_item_matrix = df.pivot_table(
    index="User's ID", 
    columns="ProdID", 
    values="Rating"
)
user_similarity = cosine_similarity(user_item_matrix)
```

#### **3️⃣ Content-Based Filtering (product similarity)**
- **Logic**: Find products similar to what you're viewing
- **Use Case**: While browsing a specific product
- **Algorithm**:
  1. Convert product tags → TF-IDF vectors
  2. Calculate cosine similarity between products
  3. Return similar products

```python
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(products['Tags'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
```

---

## 🔄 Data Flow Example

### **Scenario: User logs in and browses**

1. **Home Page Loads** (`home.py`)
   - Calls `RecommendationState.fetch_general_recommendations()`

2. **State Logic** (`recommendation_state.py`)
   - Checks: `if user.logged_in and not user.is_new_user`
   - Calls ML engine with `user_id` and optional `current_product_id`

3. **ML Engine** (`recommender.py`)
   - Calls `get_collaborative_recommendations(user_id=123)`
   - Returns top 20 similar products

4. **State Conversion**
   - Converts DataFrame → List of dicts
   - Adds computed fields: Price, Image URLs, Clean Ratings
   - Limits to 8 products + shuffles for variety

5. **UI Renders** (`home.py`)
   - Maps each product to `product_card()` component
   - Shows loading spinner during fetch
   - Grid layout: 4 columns

---

## 🗄️ State Management 

### **UserState** (`user_state.py`)
```python
class UserState(rx.State):
    user_id: int              # Unique user identifier
    logged_in: bool           # Authentication status
    is_new_user: bool         # First-time visitor?
    firebase_uid: str         # Firebase unique ID
    email: str                # Email address
    
    def login_with_firebase()  # Firebase login
    def signup_with_firebase() # Firebase registration
```

### **RecommendationState** (`recommendation_state.py`)
```python
class RecommendationState(UserState):
    recommendations: List[Dict] # List of product dicts
    is_loading: bool            # Show spinner?
    
    def fetch_recommendations()  # Call ML engine
```

### **ProductsState** (`products_state.py`)
```python
class ProductsState(rx.State):
    all_products: List[Dict]  # All filtered products
    search_query: str         # Current search term
    
    def search_products()     # Filter & search
```

### **CartState** (`cart_state.py`)
```python
class CartState(rx.State):
    cart_items: List[Dict]    # Products in cart
    total_price: float        # Cart total
    
    def add_to_cart()         # Add product
    def remove_from_cart()    # Remove product
```

### **PaymentState** (`payment_state.py`)
```python
class PaymentState(rx.State):
    payment_status: str       # "pending", "completed", "failed"
    razorpay_order_id: str    # Razorpay order ID
```

---

## 🔐 Authentication Flow

```
User → Signup
    ↓
Firebase creates user account
    ↓
User ID + Email stored in UserState
    ↓
App redirects to home
    ↓
Recommendations now use Collaborative Filtering (instead of Rating-Based)
```

---

## 📱 Frontend Pages (User Journey)

| Page | Route | Purpose |
|------|-------|---------|
| **Home** | `/` | Landing page with recommendations |
| **Login** | `/login` | Firebase email/password login |
| **Signup** | `/signup` | Firebase registration |
| **Product Detail** | `/product/{id}` | Single product + reviews + content-based recs |
| **Search Results** | `/` (with query) | Dynamic product filtering |
| **Cart** | `/cart` | View items + manage quantities |
| **Checkout** | `/checkout` | Order summary |
| **Payment** | `/payment` | Razorpay payment gateway |
| **Profile** | `/profile` | User preferences & saved data |
| **Wishlist** | `/wishlist` | Saved favorite products |
| **Orders** | `/orders` | Order history & tracking |

---

## 🎯 Key User Interactions

### **1. New User Experience**
```
New User visits → Not logged in → Sees top-rated products (Rating-Based)
    → Clicks "Sign Up" → Firebase registration
    → Redirected to Home
    → Now sees personalized recommendations (Collaborative + Content)
```

### **2. Product Search**
```
User types in navbar search → ProductsState.search_query updated
    → Filtered products displayed on home
    → Can click to view details or add to cart
```

### **3. Add to Cart**
```
User clicks "Add to Cart" → CartState.add_to_cart()
    → Product + quantity stored in state
    → Cart icon in navbar updates count
    → Persists across pages
```

### **4. Checkout Process**
```
User clicks Cart → Sees all items + total
    → Clicks Checkout → Order summary page
    → Clicks "Pay Now" → Razorpay modal
    → Completes payment → PaymentState.payment_status = "completed"
    → Redirected to success page
```

### **5. AI Chatbot**
```
User clicks chat icon → ChatState.is_open = true
    → Types question: "What are best sellers?"
    → Message sent to Groq API (LLaMA model)
    → Bot reads top products from CSV
    → Responds with formatted list + clickable links
```

---

## 💾 Data Sources

### **Product Dataset** (`cleaned_data.csv`)
- **Size**: 5.69 MB
- **Columns**:
  - `ProdID` → Product ID
  - `User's ID` → User who rated it
  - `Rating` → 1-5 star rating
  - `Category` → Product category
  - `Brand` → Brand name
  - `Tags` → Product features (for TF-IDF)
  - `ImageURL` → Product image
  - `Product_Display_Name` → Human-readable name
  - `Description` → Product description

### **ML Algorithm Inputs**
- Collaborative: All user ratings (User-Item matrix)
- Content-Based: Product tags (TF-IDF vectorization)
- Rating-Based: Product ratings + review counts

---

## 🚀 Deployment 

```bash
# Environment variables needed:
FIREBASE_API_KEY
FIREBASE_AUTH_DOMAIN
FIREBASE_PROJECT_ID
FIREBASE_STORAGE_BUCKET
FIREBASE_SENDER_ID
FIREBASE_APP_ID
GROQ_API_KEY
RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET
```

---

## 📊 Technical Highlights

### **Why 3 ML Algorithms?**
✅ **Hybrid approach** handles different scenarios
✅ **New users** get recommendations without history
✅ **Returning users** get personalized suggestions
✅ **While browsing** get similar products
✅ **Reduces cold-start problem** and improves diversity

### **Scalability Considerations**
- Dataset: 5.69 MB (can handle ~100K products)
- ML computation: Fast (cosine similarity is O(n²) but small dataset)
- Recommendation caching: Could cache results (future optimization)
- Load balancing: Reflex Cloud handles auto-scaling

---

## 📈 Future Enhancements

- [ ] Deep learning models (Neural Collaborative Filtering)
- [ ] Real-time inventory management
- [ ] Personalized email notifications
- [ ] Analytics dashboard
- [ ] A/B testing for recommendations
- [ ] Multi-language support
- [ ] Mobile app version
- [ ] Recommendation caching with Redis

---

## ✨ Summary

**AI-Store** combines a modern Python web framework with sophisticated ML algorithms (Collaborative + Content + Rating-based filtering) to deliver:

1. **Personalized recommendations** for each user
2. **Seamless e-commerce experience** (search, cart, checkout, payment)
3. **AI assistance** via chatbot with LLaMA model
4. **Scalable architecture** ready for deployment on Reflex Cloud

The project demonstrates **full-stack AI/ML engineering** with real-world e-commerce features! 🎉

---
