import streamlit as st
from huggingface_hub import InferenceClient
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EcommerceChatbot:
    def __init__(self, api_key, data):
        """Initialize chatbot with Hugging Face Inference API and product data."""
        # HuggingFaceH4/zephyr-7b-beta is fast and works well on the free HF tier
        self.model_id = "HuggingFaceH4/zephyr-7b-beta"
        self.api_key = api_key
        try:
            self.client = InferenceClient(model=self.model_id, token=api_key, timeout=15)
        except Exception:
            self.client = None
        self.data = data
        self.history = []

    def get_system_prompt(self):
        """Create strict system prompt with topic restrictions."""
        if self.data.empty:
             return "You are a shopping assistant. No products are currently loaded."

        categories = self.data['Category'].value_counts().head(10).index.tolist()
        brands = self.data['Brand'].value_counts().head(10).index.tolist()
        
        system_prompt = f"""You are a helpful e-commerce shopping assistant ONLY for beauty and personal care products.

STRICT RULES:
1. Keep ALL responses under 50 words
2. Primarily focus on: products, shopping, beauty, personal care, orders, recommendations.
3. Be polite and professional. You ARE allowed to answer basic greetings (Hi, Hello) and polite small talk (How are you?).
4. If asked about entirely unrelated sensitive topics (politics, news, sports, coding), gracefully redirect: "I can only help with shopping and product questions. How can I assist with your purchase today?"
5. Be friendly but concise.

Available Categories: {', '.join(categories[:5])}
Top Brands: {', '.join(brands[:5])}
Total Products: {len(self.data)}"""
        return system_prompt
    
    def search_products(self, query):
        """Search products based on user query."""
        if self.data.empty:
            return pd.DataFrame()
            
        query_lower = query.lower()
        
        # Handle "Best Selling" / "Popular" queries explicitly
        popular_keywords = ['best', 'popular', 'top', 'trending', 'hot']
        if any(w in query_lower for w in popular_keywords):
            if 'Rating' in self.data.columns:
                 return self.data.sort_values(by='Rating', ascending=False).head(5)
            return self.data.head(5)

        # 1. Exact Category Match Implementation
        # This fixes the "Perfume" -> "Lotion" issue by prioritizing the Category column
        unique_categories = self.data['Category'].dropna().unique()
        
        # Explicit mapping for common terms -> Categories
        # (Add more if needed based on your dataset)
        category_aliases = {
            "perfume": "Fragrance",
            "scent": "Fragrance",
            "cologne": "Fragrance",
            "Fragnance": "Fragrance",
            "makeup": "Makeup",
            "lipstick": "Makeup",
            "eye": "Makeup",
            "face": "Makeup",
            "hair": "Hair Care",
            "shampoo": "Hair Care",
            "conditioner": "Hair Care",
            "skin": "Skin Care",
            "lotion": "Skin Care",
            "moisturizer": "Skin Care",
            "cream": "Skin Care",
            "nail": "Nail Polish",
            "polish": "Nail Polish",
            "lacquer": "Nail Polish"
        }
        
        target_category = None
        
        # Check aliases first
        for key, val in category_aliases.items():
            if key in query_lower and val in unique_categories:
                target_category = val
                break
        
        # Check actual category names
        if not target_category:
            for cat in unique_categories:
                if cat.lower() in query_lower:
                    target_category = cat
                    break
        
        if target_category:
            # Filter strictly by this category
            cat_results = self.data[self.data['Category'] == target_category]
            
            # If query has other words (e.g., "Chanel Perfume"), further filter by them
            # removing the category name itself from query to finding specific item
            clean_query = query_lower.replace(target_category.lower(), "").strip()
            
            if clean_query and len(clean_query) > 2:
                 sub_mask = (
                    cat_results['Name'].str.lower().str.contains(clean_query, na=False) |
                    cat_results['Brand'].str.lower().str.contains(clean_query, na=False)
                 )
                 refined_results = cat_results[sub_mask]
                 if not refined_results.empty:
                     return refined_results.head(3)
            
            # If no refinement or refinement failed, return top items from category
            if 'Rating' in cat_results.columns:
                 return cat_results.sort_values(by='Rating', ascending=False).head(3)
            return cat_results.head(3)

        # 2. Fallback to Broad Search (existing logic)
        # 2. Fallback to Broad Search (Smart Keyword)
        # Remove common conversational fillers
        fillers = ['suggest', 'recommend', 'show', 'me', 'items', 'products', 'looking', 'for', 'find', 'search', 'buy', 'get', 'a', 'an', 'the', 'i', 'want', 'can', 'you', 'please', 'is', 'are']
        clean_query_words = [w for w in query_lower.split() if w not in fillers]
        
        if clean_query_words:
            # A. Try searching for the cleaned phrase (e.g. "red lipstick")
            cleaned_search_str = " ".join(clean_query_words)
            mask = (
                self.data['Name'].str.lower().str.contains(cleaned_search_str, na=False) |
                self.data['Brand'].str.lower().str.contains(cleaned_search_str, na=False) |
                self.data['Category'].str.lower().str.contains(cleaned_search_str, na=False)
            )
            results = self.data[mask].head(3)
            if not results.empty:
                return results

            # B. If detailed phrase fails, try ANY word match (OR logic)
            if len(clean_query_words) > 1:
                 joined_or = "|".join(clean_query_words)
                 mask_or = (
                    self.data['Name'].str.lower().str.contains(joined_or, na=False) |
                    self.data['Category'].str.lower().str.contains(joined_or, na=False)
                 )
                 return self.data[mask_or].head(3)
        
        return pd.DataFrame()
    
    def is_shopping_related(self, message):
        """Check if query is shopping/e-commerce related."""
        shopping_keywords = [
            'product', 'buy', 'purchase', 'price', 'recommend', 'shop', 'order',
            'brand', 'category', 'beauty', 'care', 'makeup', 'hair', 'skin',
            'nail', 'shampoo', 'lipstick', 'cream', 'oil', 'perfume', 'rating',
            'review', 'stock', 'available', 'compare', 'best', 'cheap', 'deal'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in shopping_keywords)
    
    def start_chat(self):
        """Initialize chat session history with system prompt."""
        system_prompt = self.get_system_prompt()
        self.history = [
            {"role": "system", "content": system_prompt}
        ]
        return system_prompt
    
    def send_message(self, user_message):
        """Send message with topic validation and get response via Hugging Face.
        Returns: (response_text, found_products_df)
        """
        
        # 4️⃣ Search Your Product Data FIRST
        products = self.search_products(user_message)
        
        # 6️⃣ Construct a Controlled Prompt (Relaxed for casual chat)
        # We only hard-block truly problematic topics
        off_topic_hard_block = [
            'news', 'politics', 'sports', 'code', 'program',
            'math', 'calculate', 'translate', 'history', 'science'
        ]
        
        if any(pattern in user_message.lower() for pattern in off_topic_hard_block):
            return "I can only help with shopping and product questions. How can I assist with your purchase today? 🛍️", pd.DataFrame()

        # 5️⃣ Convert Products into Text (Prompt Injection)
        product_list = ""
        if not products.empty:
            product_list = "\n".join([
                f"- {row['Name']} – ₹{row['Price']}" 
                for _, row in products.iterrows()
            ])
            prompt_context = f"Available products:\n{product_list}"
        else:
            # FALLBACK: If strictly shopping related but no results, show Top Rated
            if self.is_shopping_related(user_message):
                if 'Rating' in self.data.columns:
                     fallback_products = self.data.sort_values(by='Rating', ascending=False).head(3)
                else:
                     fallback_products = self.data.head(3)
                
                if not fallback_products.empty:
                    product_list = "\n".join([
                        f"- {row['Name']} – ₹{row['Price']}" 
                        for _, row in fallback_products.iterrows()
                    ])
                    # Update products df so front-end renders them too
                    products = fallback_products
                    prompt_context = f"No exact matches found. However, here are our Top Rated items you can recommend instead:\n{product_list}"
                else:
                    prompt_context = "No products found in the catalog."
            else:
                prompt_context = "No products found in the catalog for this specific query."
        
        # Build prompt
        full_prompt = f"""[SYSTEM] You are a helpful e-commerce shopping assistant. 
Rules:
- Be polite and professional.
- Only answer small talk if the user explicitly asks "How are you?" or greets you first. Do NOT start every message with a greeting.
- ONLY recommend products from the provided list if shopping-related.
- If no products match a shopping query, say you can't find specific matches.
- Response must be under 50 words.

[CONTEXT]
{prompt_context}

[USER]
{user_message}

[ASSISTANT]
"""
        
        # Use local history for context but primarily rely on injected products
        self.history.append({"role": "user", "content": full_prompt})
        
        try:
            if self.client is None:
                raise Exception("No client initialized")
            # Call HuggingFace Inference API
            completion = self.client.chat_completion(
                messages=[{"role": "user", "content": full_prompt}],
                max_tokens=150,
                temperature=0.1
            )
            # Extract Response
            response_text = completion.choices[0].message.content
            self.history.append({"role": "assistant", "content": response_text})
            return response_text, products
            
        except Exception as e:
            # Smart rule-based fallback — always gives a useful answer
            return self._fallback_response(user_message, products), products

    def _fallback_response(self, user_message: str, products) -> str:
        """Rule-based response when HuggingFace API is unavailable."""
        msg = user_message.lower()
        greetings = ['hi', 'hello', 'hey', 'hii', 'hiii']
        if any(g in msg for g in greetings):
            return "Hi there! 👋 I'm your shopping assistant. Ask me about products, brands, or categories!"
        if 'best' in msg or 'top' in msg or 'popular' in msg:
            if not products.empty:
                names = products['Name'].head(3).tolist()
                return f"Here are some top picks: {', '.join(names)}. Want more details?"
            return "I can help find top products! What category are you interested in?"
        if not products.empty:
            names = products['Name'].head(2).tolist()
            return f"I found some matches: {', '.join(names)}. Check the cards below!"
        return "I can help you find beauty & personal care products. Try asking for a specific category like 'shampoo' or 'lipstick'!"


def render_chatbot_ui(data, visible=True):
    """Render chatbot UI embedded in sidebar."""
    if not visible:
        return

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'chatbot_instance' not in st.session_state:
        st.session_state.chatbot_instance = None
    
    # Initialize Bot logic if needed
    if st.session_state.chatbot_instance is None:
        try:
            # Try getting key from secrets first
            api_key = None
            # Safely try secrets first, fall back to .env
            api_key = None
            try:
                hf = st.secrets.get("HF_TOKEN", "")
                if hf:
                    api_key = hf
            except Exception:
                pass
            if not api_key:
                api_key = os.getenv("HF_TOKEN", "")

            if not api_key:
                st.warning("⚠️ Chatbot disabled — add your HF_TOKEN to the .env file to enable it.")
                st.caption("Get a free token at https://huggingface.co/settings/tokens")
            else:
                st.session_state.chatbot_instance = EcommerceChatbot(api_key, data)
                st.session_state.chatbot_instance.start_chat()
                if not st.session_state.chat_history:
                    st.session_state.chat_history.append({
                        "role": "bot", 
                        "message": "Hi! 👋 how can I help you shop!"
                    })
        except Exception as e:
            st.error(f"Error: {e}")

    # --- Chat Interface (No Floating CSS) ---
    
    # Scoped CSS for Sidebar Inputs
    st.markdown("""
        <style>
            /* Remove default input styling to make it flush */
            section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {
                padding: 0.5rem 1rem !important;
                min-height: 2.5rem !important;
                height: 2.5rem !important;
                font-size: 14px !important;
                border-radius: 20px !important;
                border: 1px solid #eee !important;
                background: #f9f9f9 !important;
                color: #111111 !important; /* Force text color to be black so it doesn't disappear in dark mode */
            }
            /* Style the placeholder text */
            section[data-testid="stSidebar"] div[data-testid="stTextInput"] input::placeholder {
                color: #888888 !important;
            }
            .product-mini-card {
                border: 1px solid #eee;
                border-radius: 8px;
                padding: 8px;
                margin-top: 5px;
                background: white;
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            .product-mini-card img {
                width: 100%;
                border-radius: 4px;
            }
            .product-mini-card-name {
                font-weight: bold;
                font-size: 11px;
                color: #333;
            }
            .product-mini-card-price {
                color: #ff4b4b;
                font-weight: bold;
                font-size: 11px;
            }
            section[data-testid="stSidebar"] div[data-testid="stTextInput"] div[data-testid="input_container"] {
                min-height: 2.5rem !important;
                border: none !important;
                background: transparent !important;
            }
            .rec-img-fixed {
                width: 100%;
                height: 150px !important;
                object-fit: contain !important;
                border-radius: 8px;
                background-color: #fff;
                margin-bottom: 5px;
            }
            div[data-testid="InputInstructions"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🤖 Shopping Assistant")
    
    # Simple container for messages
    # Custom Scrollable Message Area (Standardized Height)
    all_msgs_html = ""
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            all_msgs_html += f'<div style="background-color: #e0f7fa; padding: 12px; border-radius: 12px; margin-bottom: 8px; text-align: right; color: #000000; font-size: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">{msg["message"]}</div>'
        else:
            # Bot Message
            bot_html = f'<div style="background-color: #f1f3f4; padding: 12px; border-radius: 12px; margin-bottom: 8px; text-align: left; color: #000000; font-size: 14px; border: 1px solid #e0e0e0; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">'
            bot_html += f'<div>{msg["message"]}</div>'
            
            # 1️⃣1️⃣ Display Product Cards (Separately) - REMOVED per user request
            # if "products" in msg and not msg["products"].empty:
            #    ... (removed)
            
            bot_html += '</div>'
            all_msgs_html += bot_html
    
    st.markdown(
        f'<div style="height: 400px; overflow-y: auto; border: 1px solid #ddd; border-radius: 10px; padding: 10px; background: #ffffff; margin-bottom: 15px;">'
        f'{all_msgs_html}'
        f'</div>', 
        unsafe_allow_html=True
    )
    
    # Input
    with st.form(key="sidebar_chat_form", clear_on_submit=True, border=False):
        user_input = st.text_input("Ask about products...", placeholder="Shampoo for dry hair...", label_visibility="collapsed")
        submitted = st.form_submit_button("Send", use_container_width=True)

    # (Interactive Product Cards have been moved to the main content area in demo_streamlit.py)


    if submitted and user_input:
        st.session_state.chat_history.append({"role": "user", "message": user_input})
        
        if st.session_state.chatbot_instance:
            try:
                resp, found_prods = st.session_state.chatbot_instance.send_message(user_input)
                st.session_state.chat_history.append({
                    "role": "bot", 
                    "message": resp,
                    "products": found_prods
                })
            except Exception as e:
                st.session_state.chat_history.append({"role": "bot", "message": "Error connecting to AI."})
        st.rerun()