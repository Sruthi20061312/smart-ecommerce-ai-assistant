import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from textblob import TextBlob
import json
import random

st.set_page_config(
    page_title="Smart E-commerce AI Assistant",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; color: white; }
    .stButton > button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 10px;
        padding: 0.5em 1.5em;
        font-weight: bold;
        border: none;
    }
    .stButton > button:hover { background-color: #cc0000; }
    .feature-box {
        background-color: #1e2130;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 4px solid #FF4B4B;
    }
    .score-box {
        background-color: #1e2130;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        font-size: 2em;
        font-weight: bold;
    }
    .search-result {
        background-color: #1e2130;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #00cc88;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PRODUCT DATABASE (10 Products)
# ─────────────────────────────────────────────
PRODUCTS = {
    "Nike Running Shoes": {
        "category": "Footwear",
        "price_history": [4500, 4200, 3900, 4100, 3700, 3500, 3200],
        "sustainability_score": 62,
        "reviews": [
            "Amazing product! Best shoes ever! Must buy! Perfect! Love it!",
            "Good quality shoes. Comfortable for long runs. Durable material.",
            "Okay product. Nothing special. Gets the job done.",
            "BEST PRODUCT EVER!! BUY NOW!! AMAZING QUALITY!! 5 STARS!!",
            "Comfortable fit, good grip. Slightly expensive but worth it.",
        ]
    },
    "Samsung Galaxy Buds": {
        "category": "Electronics",
        "price_history": [8999, 8500, 7999, 8200, 7500, 6999, 6500],
        "sustainability_score": 45,
        "reviews": [
            "Great sound quality! Battery lasts long. Happy with purchase.",
            "FANTASTIC PRODUCT!! EVERYONE MUST BUY!! CHANGED MY LIFE!!",
            "Average noise cancellation. Sound is decent for the price.",
            "Stopped working after 2 months. Very disappointed.",
            "Good product overall. Pairing is smooth. Comfortable to wear.",
        ]
    },
    "Organic Cotton T-Shirt": {
        "category": "Clothing",
        "price_history": [899, 850, 799, 820, 780, 750, 720],
        "sustainability_score": 91,
        "reviews": [
            "Soft fabric, eco-friendly. Love that it's organic cotton.",
            "AMAZING SHIRT!! BEST QUALITY EVER!! SUPER SOFT!! 5 STARS!!",
            "Good material. Washes well. Colour didn't fade after multiple washes.",
            "Nice shirt. Comfortable for daily wear. Recommend to friends.",
            "Bit pricey for a t-shirt but the quality justifies the cost.",
        ]
    },
    "Philips Air Fryer": {
        "category": "Kitchen Appliance",
        "price_history": [12999, 11999, 10999, 11500, 10500, 9999, 9500],
        "sustainability_score": 55,
        "reviews": [
            "Changed my cooking! Healthy food, easy to clean. Great buy.",
            "BUY THIS NOW!! BEST FRYER EVER!! LIFE CHANGING PRODUCT!!",
            "Good fryer. Food comes out crispy. Slightly noisy though.",
            "Returned after a week. Quality not as expected. Disappointed.",
            "Excellent product. Easy to use. Family loves it.",
        ]
    },
    "Apple iPhone 15": {
        "category": "Electronics",
        "price_history": [79999, 77999, 75999, 74999, 72999, 70999, 68999],
        "sustainability_score": 58,
        "reviews": [
            "BEST PHONE EVER!! AMAZING CAMERA!! BUY NOW!! LOVE IT!!",
            "Good camera quality. Battery life improved from previous model.",
            "Expensive but worth it. Screen quality is excellent.",
            "Smooth performance. Face ID works great. Slightly heavy though.",
            "Great phone overall. iOS is smooth. Recommend to everyone.",
        ]
    },
    "Boat Rockerz Headphones": {
        "category": "Electronics",
        "price_history": [2999, 2799, 2599, 2499, 2299, 1999, 1799],
        "sustainability_score": 40,
        "reviews": [
            "Good sound for the price. Battery lasts 8 hours.",
            "AMAZING HEADPHONES!! BEST SOUND EVER!! MUST BUY!!",
            "Decent quality. Comfortable to wear. Mic quality average.",
            "Stopped working after 3 months. Poor build quality.",
            "Value for money product. Good bass. Recommended for budget buyers.",
        ]
    },
    "Bamboo Water Bottle": {
        "category": "Eco Products",
        "price_history": [599, 549, 499, 520, 480, 450, 420],
        "sustainability_score": 95,
        "reviews": [
            "Eco-friendly and durable. Keeps water cold for 12 hours.",
            "BEST BOTTLE EVER!! AMAZING QUALITY!! BUY NOW!!",
            "Good quality bamboo. Lid seals well. No leakage.",
            "Sustainable product. Happy to support eco-friendly brands.",
            "Nice design. Lightweight. Perfect for gym and office use.",
        ]
    },
    "Sony WH-1000XM5 Headphones": {
        "category": "Electronics",
        "price_history": [29999, 28500, 27999, 27000, 26500, 25999, 24999],
        "sustainability_score": 52,
        "reviews": [
            "Best noise cancellation I have used. Sound quality is superb.",
            "AMAZING!! BEST HEADPHONES EVER!! LIFE CHANGING!! BUY NOW!!",
            "Excellent ANC. Comfortable for long hours. Battery lasts 30 hours.",
            "Pricey but worth every rupee. Build quality is premium.",
            "Good headphones. Bluetooth connection is stable. Highly satisfied.",
        ]
    },
    "Prestige Electric Cooker": {
        "category": "Kitchen Appliance",
        "price_history": [3499, 3299, 2999, 3100, 2899, 2699, 2499],
        "sustainability_score": 60,
        "reviews": [
            "Cooks rice perfectly. Easy to clean. Good build quality.",
            "BUY THIS NOW!! BEST COOKER EVER!! AMAZING PRODUCT!!",
            "Decent cooker. Does the job well. Slightly small capacity.",
            "Good value for money. Family of 4 is perfect size.",
            "Works well. Lid fits tight. No steam leakage.",
        ]
    },
    "Wildcraft Backpack": {
        "category": "Bags",
        "price_history": [2499, 2299, 1999, 2100, 1899, 1699, 1499],
        "sustainability_score": 68,
        "reviews": [
            "Sturdy backpack. Good number of compartments. Comfortable straps.",
            "BEST BAG EVER!! AMAZING QUALITY!! MUST BUY FOR COLLEGE!!",
            "Decent quality. Zippers are smooth. Good for daily college use.",
            "Water resistant material. Laptop fits well. Happy with purchase.",
            "Good bag for the price. Comfortable to carry all day.",
        ]
    }
}

WEEKS = ["6 weeks ago", "5 weeks ago", "4 weeks ago", "3 weeks ago", "2 weeks ago", "Last week", "Today"]

def ask_ollama(prompt):
    return None  # Offline mode

# ─────────────────────────────────────────────
# PRODUCT SEARCH FUNCTION
# ─────────────────────────────────────────────
def search_products(query):
    query = query.lower().strip()
    results = []
    for name, data in PRODUCTS.items():
        if query in name.lower() or query in data["category"].lower():
            results.append(name)
    return results

# ─────────────────────────────────────────────
# FEATURE 1: FAKE REVIEW DETECTION
# ─────────────────────────────────────────────
def analyze_review(review_text):
    blob = TextBlob(review_text)
    sentiment = blob.sentiment.polarity
    word_count = len(review_text.split())
    exclamation_count = review_text.count("!")
    caps_ratio = sum(1 for c in review_text if c.isupper()) / max(len(review_text), 1)
    words = review_text.lower().split()
    unique_ratio = len(set(words)) / max(word_count, 1)

    spam_keywords = [
        "must buy", "buy now", "best ever", "changed my life",
        "life changing", "amazing amazing", "best best", "love love",
        "perfect perfect", "highly recommend", "dont miss", "order now",
        "everyone must", "trust me", "i swear"
    ]

    red_flags = []
    score = 0

    if word_count < 8:
        red_flags.append("⚠️ Too short (less than 8 words)")
        score += 25
    if exclamation_count >= 2:
        red_flags.append(f"⚠️ Too many exclamation marks ({exclamation_count} found)")
        score += 20
    if caps_ratio > 0.3:
        red_flags.append("⚠️ Excessive CAPS usage")
        score += 25
    if sentiment > 0.75:
        red_flags.append(f"⚠️ Suspiciously over-positive sentiment ({round(sentiment,2)})")
        score += 20
    if word_count > 5 and unique_ratio < 0.6:
        red_flags.append("⚠️ Repetitive words detected")
        score += 15

    review_lower = review_text.lower()
    found_spam = [kw for kw in spam_keywords if kw in review_lower]
    if found_spam:
        red_flags.append(f"⚠️ Spam phrases found: {', '.join(found_spam)}")
        score += 20

    positive_words = ["amazing", "perfect", "best", "awesome", "fantastic",
                      "excellent", "wonderful", "superb", "outstanding", "brilliant"]
    positive_count = sum(1 for w in words if w in positive_words)
    if positive_count >= 3:
        red_flags.append(f"⚠️ Too many positive adjectives ({positive_count} found)")
        score += 15

    specific_words = ["quality", "material", "size", "colour", "color", "weight",
                      "battery", "screen", "sound", "grip", "fit", "smell", "texture"]
    specific_count = sum(1 for w in words if w in specific_words)
    if specific_count == 0 and word_count > 6:
        red_flags.append("⚠️ No specific product details mentioned")
        score += 10

    score = min(score, 100)
    verdict = "🔴 LIKELY FAKE" if score >= 35 else "🟢 LIKELY GENUINE"
    return verdict, score, red_flags, round(sentiment, 2)

# ─────────────────────────────────────────────
# FEATURE 2: PRICE DROP PREDICTION
# ─────────────────────────────────────────────
def predict_price(product_name):
    data = PRODUCTS[product_name]
    prices = data["price_history"]
    avg_drop = (prices[0] - prices[-1]) / len(prices)
    predicted = max(prices[-1] - avg_drop, prices[-1] * 0.85)
    trend = "📉 Dropping" if prices[-1] < prices[-2] else "📈 Rising"
    return prices, round(predicted), trend

# ─────────────────────────────────────────────
# FEATURE 3: SUSTAINABILITY SCORE
# ─────────────────────────────────────────────
def get_sustainability(product_name):
    score = PRODUCTS[product_name]["sustainability_score"]
    category = PRODUCTS[product_name]["category"]
    if score >= 80:
        label = "🌿 Excellent — Eco Friendly"
        tips = "This product uses sustainable materials and ethical manufacturing."
    elif score >= 60:
        label = "🟡 Moderate — Could be better"
        tips = "Some sustainable practices used. Room for improvement in packaging."
    else:
        label = "🔴 Poor — High environmental impact"
        tips = "Consider alternatives with better eco certifications."
    return score, label, tips, category

# ─────────────────────────────────────────────
# FEATURE 4: OUTFIT GENERATOR
# ─────────────────────────────────────────────
def generate_outfit(occasion, style):
    outfits = {
        ("College", "Casual"): {
            "Top": "White oversized t-shirt or hoodie",
            "Bottom": "Blue slim-fit jeans or joggers",
            "Footwear": "White sneakers or canvas shoes",
            "Accessories": "Backpack, watch, minimal jewelry",
            "Tip": "Keep it simple and comfortable for long college days!"
        },
        ("Office", "Formal"): {
            "Top": "Light blue or white formal shirt",
            "Bottom": "Dark navy or black trousers",
            "Footwear": "Oxford shoes or formal loafers",
            "Accessories": "Belt, watch, minimal tie",
            "Tip": "Stick to neutral colors for a professional look!"
        },
        ("Party", "Trendy"): {
            "Top": "Graphic tee or stylish polo",
            "Bottom": "Slim chinos or dark jeans",
            "Footwear": "Trendy sneakers or loafers",
            "Accessories": "Cap, bracelet, sunglasses",
            "Tip": "Add a pop of color to stand out!"
        },
        ("Gym", "Sporty"): {
            "Top": "Dri-fit t-shirt or tank top",
            "Bottom": "Compression shorts or track pants",
            "Footwear": "Running shoes with good grip",
            "Accessories": "Water bottle, fitness band, earphones",
            "Tip": "Choose breathable fabric for better performance!"
        },
    }
    key = (occasion, style)
    outfit = outfits.get(key, {
        "Top": "Plain crew-neck t-shirt",
        "Bottom": "Comfortable jeans",
        "Footwear": "Clean white sneakers",
        "Accessories": "Minimal watch",
        "Tip": "Keep it clean and confident!"
    })
    return outfit

# ─────────────────────────────────────────────
# FEATURE 5: RETURN FRAUD DETECTION
# ─────────────────────────────────────────────
def detect_return_fraud(order_id, reason, days_used, num_returns):
    risk_score = 0
    flags = []
    if num_returns > 5:
        flags.append("⚠️ High return frequency (more than 5 returns)")
        risk_score += 35
    if days_used > 25:
        flags.append("⚠️ Item used for too long before return request")
        risk_score += 30
    if reason.lower() in ["not needed", "changed mind", "just checking"]:
        flags.append("⚠️ Suspicious return reason")
        risk_score += 20
    if not order_id.startswith("ORD"):
        flags.append("⚠️ Invalid order ID format")
        risk_score += 15
    risk_score = min(risk_score, 100)
    verdict = "🔴 HIGH FRAUD RISK" if risk_score >= 50 else "🟢 LEGITIMATE RETURN"
    return verdict, risk_score, flags

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.title("🛒 Smart AI Assistant")
st.sidebar.markdown("---")

# PRODUCT SEARCH IN SIDEBAR
st.sidebar.markdown("### 🔍 Search Products")
search_query = st.sidebar.text_input("Type product name:", placeholder="e.g. iPhone, shoes...")

if search_query:
    results = search_products(search_query)
    if results:
        st.sidebar.markdown(f"**Found {len(results)} product(s):**")
        for r in results:
            st.sidebar.markdown(f"✅ {r}")
        st.session_state["searched_product"] = results[0]
    else:
        st.sidebar.warning("No product found. Try: Nike, Samsung, iPhone, Bamboo...")

st.sidebar.markdown("---")
feature = st.sidebar.selectbox(
    "Choose a Feature",
    [
        "🏠 Home",
        "🔍 Product Search",
        "⚖️ Compare Products",
        "🕵️ Fake Review Detection",
        "📉 Price Drop Prediction",
        "🌿 Sustainability Score",
        "👗 Outfit Generator",
        "🚨 Return Fraud Detection"
    ]
)

# ─────────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────────
if feature == "🏠 Home":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e2130 0%, #0f1117 100%);
                border-radius: 16px; padding: 40px; text-align: center; margin-bottom: 20px;
                border: 1px solid #FF4B4B;">
        <h1 style="color: #FF4B4B; font-size: 2.8em;">🛒 Smart E-commerce AI Assistant</h1>
        <p style="color: #aaa; font-size: 1.2em;">Your AI-powered smart shopping co-pilot for Indian consumers</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("🛍️ Total Products", "10", delta="Indian Brands")
    with col_s2:
        st.metric("🤖 AI Features", "7", delta="All Offline")
    with col_s3:
        st.metric("📝 Reviews Analyzed", "50+", delta="Real Patterns")
    with col_s4:
        st.metric("⚡ Response Time", "<1 sec", delta="Instant")

    st.markdown("---")
    st.markdown("### 🚀 What Can This App Do?")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-box"><h3>🔍 Product Search</h3><p>Search any product and get full AI analysis — price, reviews, sustainability in one click.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-box"><h3>⚖️ Compare Products</h3><p>Compare 2 products side by side — price, eco score, fake reviews and get a winner recommendation.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-box"><h3>🕵️ Fake Review Detection</h3><p>Detect suspicious reviews using sentiment analysis and 8 linguistic pattern checks.</p></div>', unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown('<div class="feature-box"><h3>📉 Price Drop Prediction</h3><p>Predict future price drops based on 7-week historical trend analysis.</p></div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="feature-box"><h3>🌿 Sustainability Score</h3><p>Check how eco-friendly a product is with a detailed environmental impact score.</p></div>', unsafe_allow_html=True)
    with col6:
        st.markdown('<div class="feature-box"><h3>🚨 Return Fraud Detection</h3><p>Identify suspicious return patterns to protect sellers from fraud.</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 Why This App?")
    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        st.info("🇮🇳 Built for Indian shoppers — prices in ₹, Indian brands included")
    with col_w2:
        st.info("📴 Works 100% offline — no internet needed for demo or use")
    with col_w3:
        st.info("🤖 Real AI logic — not just a chatbot, actual pattern analysis")

    st.success("👈 Select any feature from the sidebar to get started!")

# ─────────────────────────────────────────────
# PRODUCT SEARCH PAGE
# ─────────────────────────────────────────────
elif feature == "🔍 Product Search":
    st.title("🔍 Smart Product Search")
    st.markdown("Search any product to get full AI analysis instantly!")
    st.markdown("---")

    search = st.text_input("🔍 Search product:", placeholder="Try: Nike, iPhone, Samsung, Bamboo, Backpack...")

    if search:
        results = search_products(search)
        if results:
            st.success(f"Found {len(results)} product(s) matching '{search}'")
            selected = st.selectbox("Select a product:", results)

            if st.button("🤖 Full AI Analysis"):
                st.markdown("---")
                st.markdown(f"## 📊 Full Analysis: {selected}")

                tab1, tab2, tab3 = st.tabs(["📉 Price & Reviews", "🌿 Sustainability", "🕵️ Review Check"])

                with tab1:
                    col1, col2 = st.columns(2)
                    prices, predicted, trend = predict_price(selected)
                    with col1:
                        st.markdown(f"**Current Price:** ₹{prices[-1]}")
                        st.markdown(f"**Predicted Next Week:** ₹{predicted}")
                        st.markdown(f"**Trend:** {trend}")
                        savings = prices[-1] - predicted
                        if savings > 0:
                            st.success(f"💰 Wait! Save ₹{savings} next week!")
                        else:
                            st.warning("🛒 Buy now — price may go up!")
                    with col2:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=WEEKS, y=prices, mode="lines+markers",
                            name="Price", line=dict(color="#FF4B4B", width=3)))
                        fig.add_trace(go.Scatter(x=[WEEKS[-1], "Next Week"],
                            y=[prices[-1], predicted], mode="lines+markers",
                            name="Predicted", line=dict(color="#00cc88", width=3, dash="dash")))
                        fig.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#1e2130",
                            font_color="white", height=300, title="Price Trend (₹)")
                        st.plotly_chart(fig, use_container_width=True)

                    st.markdown("### 📝 Sample Reviews")
                    for i, review in enumerate(PRODUCTS[selected]["reviews"]):
                        verdict, score, _, _ = analyze_review(review)
                        color = "🔴" if "FAKE" in verdict else "🟢"
                        st.markdown(f"{color} **Review {i+1}** (Score: {score}/100): _{review}_")

                with tab2:
                    score, label, tips, category = get_sustainability(selected)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Category:** {category}")
                        st.markdown(f"**Rating:** {label}")
                        st.markdown(f"**Score:** {score}/100")
                        st.progress(score / 100)
                        st.info(f"💡 {tips}")
                    with col2:
                        color = "#00cc88" if score >= 80 else "#ffaa00" if score >= 60 else "#FF4B4B"
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number", value=score,
                            title={"text": "Eco Score"},
                            gauge={"axis": {"range": [0, 100]}, "bar": {"color": color},
                                   "steps": [{"range": [0, 40], "color": "#3d0000"},
                                             {"range": [40, 70], "color": "#3d3000"},
                                             {"range": [70, 100], "color": "#003d1a"}]}
                        ))
                        fig.update_layout(paper_bgcolor="#0f1117", font_color="white", height=280)
                        st.plotly_chart(fig, use_container_width=True)

                with tab3:
                    st.markdown("### 🕵️ Review Analysis for All Reviews")
                    fake_count = 0
                    genuine_count = 0
                    for i, review in enumerate(PRODUCTS[selected]["reviews"]):
                        verdict, score, flags, sentiment = analyze_review(review)
                        if "FAKE" in verdict:
                            fake_count += 1
                        else:
                            genuine_count += 1
                        with st.expander(f"Review {i+1} — {verdict} (Score: {score}/100)"):
                            st.write(f"**Review:** {review}")
                            st.write(f"**Sentiment:** {sentiment}")
                            if flags:
                                for f in flags:
                                    st.write(f)

                    st.markdown("---")
                    col_f, col_g = st.columns(2)
                    with col_f:
                        st.error(f"🔴 Fake Reviews: {fake_count}")
                    with col_g:
                        st.success(f"🟢 Genuine Reviews: {genuine_count}")

                    fig = go.Figure(data=[go.Pie(
                        labels=["Fake", "Genuine"],
                        values=[fake_count, genuine_count],
                        hole=0.4,
                        marker_colors=["#FF4B4B", "#00cc88"]
                    )])
                    fig.update_layout(paper_bgcolor="#0f1117", font_color="white",
                                      title="Review Authenticity", height=300)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"No product found for '{search}'")
            st.info("Try searching: Nike, Samsung, iPhone, Bamboo, Sony, Boat, Wildcraft, Prestige, Philips")


# ─────────────────────────────────────────────
# COMPARE PRODUCTS PAGE
# ─────────────────────────────────────────────
elif feature == "⚖️ Compare Products":
    st.title("⚖️ Compare Products")
    st.markdown("Compare 2 products side by side and get a winner recommendation!")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        product_a = st.selectbox("Select Product 1:", list(PRODUCTS.keys()), key="prod_a")
    with col2:
        product_b = st.selectbox("Select Product 2:", list(PRODUCTS.keys()), index=1, key="prod_b")

    if st.button("⚖️ Compare Now"):
        if product_a == product_b:
            st.warning("Please select 2 different products!")
        else:
            st.markdown("---")

            # Get data for both
            prices_a, pred_a, trend_a = predict_price(product_a)
            prices_b, pred_b, trend_b = predict_price(product_b)
            eco_a, label_a, tips_a, cat_a = get_sustainability(product_a)
            eco_b, label_b, tips_b, cat_b = get_sustainability(product_b)

            # Count fake reviews
            fake_a = sum(1 for r in PRODUCTS[product_a]["reviews"] if analyze_review(r)[0] == "🔴 LIKELY FAKE")
            fake_b = sum(1 for r in PRODUCTS[product_b]["reviews"] if analyze_review(r)[0] == "🔴 LIKELY FAKE")
            genuine_a = len(PRODUCTS[product_a]["reviews"]) - fake_a
            genuine_b = len(PRODUCTS[product_b]["reviews"]) - fake_b

            # ── Side by side comparison ──
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"### 🅰️ {product_a}")
                st.markdown(f"**Category:** {cat_a}")
                st.markdown(f"**Current Price:** ₹{prices_a[-1]}")
                st.markdown(f"**Predicted Price:** ₹{pred_a}")
                st.markdown(f"**Price Trend:** {trend_a}")
                st.markdown(f"**Eco Score:** {eco_a}/100 — {label_a}")
                st.markdown(f"**Fake Reviews:** 🔴 {fake_a} / 🟢 {genuine_a}")

            with col_b:
                st.markdown(f"### 🅱️ {product_b}")
                st.markdown(f"**Category:** {cat_b}")
                st.markdown(f"**Current Price:** ₹{prices_b[-1]}")
                st.markdown(f"**Predicted Price:** ₹{pred_b}")
                st.markdown(f"**Price Trend:** {trend_b}")
                st.markdown(f"**Eco Score:** {eco_b}/100 — {label_b}")
                st.markdown(f"**Fake Reviews:** 🔴 {fake_b} / 🟢 {genuine_b}")

            st.markdown("---")

            # ── Bar Chart Comparison ──
            fig = go.Figure()
            categories = ["Eco Score", "Genuine Reviews (x10)", "Predicted Savings (%)"]
            savings_a = round(((prices_a[-1] - pred_a) / prices_a[-1]) * 100, 1)
            savings_b = round(((prices_b[-1] - pred_b) / prices_b[-1]) * 100, 1)

            values_a = [eco_a, genuine_a * 10, max(savings_a, 0)]
            values_b = [eco_b, genuine_b * 10, max(savings_b, 0)]

            fig.add_trace(go.Bar(name=product_a, x=categories, y=values_a,
                                 marker_color="#FF4B4B"))
            fig.add_trace(go.Bar(name=product_b, x=categories, y=values_b,
                                 marker_color="#00cc88"))
            fig.update_layout(
                title="Product Comparison Chart",
                barmode="group",
                paper_bgcolor="#0f1117",
                plot_bgcolor="#1e2130",
                font_color="white",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)

            # ── Price comparison line chart ──
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=WEEKS, y=prices_a, mode="lines+markers",
                name=product_a, line=dict(color="#FF4B4B", width=3)))
            fig2.add_trace(go.Scatter(x=WEEKS, y=prices_b, mode="lines+markers",
                name=product_b, line=dict(color="#00cc88", width=3)))
            fig2.update_layout(
                title="Price History Comparison (₹)",
                paper_bgcolor="#0f1117",
                plot_bgcolor="#1e2130",
                font_color="white",
                height=320
            )
            st.plotly_chart(fig2, use_container_width=True)

            # ── Winner Recommendation ──
            st.markdown("---")
            st.markdown("## 🏆 AI Recommendation")

            score_a = 0
            score_b = 0

            if eco_a > eco_b: score_a += 1
            else: score_b += 1

            if genuine_a > genuine_b: score_a += 1
            else: score_b += 1

            if pred_a < prices_a[-1]: score_a += 1
            if pred_b < prices_b[-1]: score_b += 1

            if score_a > score_b:
                st.success(f"✅ **Buy {product_a}!** Better eco score, more genuine reviews, and price is dropping!")
            elif score_b > score_a:
                st.success(f"✅ **Buy {product_b}!** Better eco score, more genuine reviews, and price is dropping!")
            else:
                st.info(f"🤝 Both products are similar! Choose based on your budget.")

            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                winner_eco = product_a if eco_a > eco_b else product_b
                st.metric("🌿 Eco Winner", winner_eco.split()[0])
            with col_r2:
                winner_rev = product_a if genuine_a > genuine_b else product_b
                st.metric("🕵️ Trust Winner", winner_rev.split()[0])
            with col_r3:
                cheaper = product_a if prices_a[-1] < prices_b[-1] else product_b
                st.metric("💰 Price Winner", cheaper.split()[0])


# ─────────────────────────────────────────────
# FAKE REVIEW DETECTION
# ─────────────────────────────────────────────
elif feature == "🕵️ Fake Review Detection":
    st.title("🕵️ Fake Review Detection")
    st.markdown("Paste any product review below to check if it's genuine or fake.")
    st.markdown("---")

    product = st.selectbox("Pick a sample product:", list(PRODUCTS.keys()))
    sample_reviews = PRODUCTS[product]["reviews"]

    col1, col2 = st.columns([2, 1])
    with col1:
        review_input = st.text_area("Enter a review:", height=120, placeholder="Type or paste a review here...")
    with col2:
        st.markdown("**Quick Test Reviews:**")
        for i, r in enumerate(sample_reviews):
            if st.button(f"Review {i+1}", key=f"rev_{i}"):
                st.session_state["review_input"] = r

    if "review_input" in st.session_state:
        review_input = st.session_state["review_input"]
        st.text_area("Selected review:", value=review_input, height=80, disabled=True)

    if st.button("🔍 Analyze Review"):
        if review_input and len(review_input.strip()) > 0:
            verdict, score, flags, sentiment = analyze_review(review_input)
            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"### Result: {verdict}")
                st.markdown(f"**Fake Probability Score: {score}/100**")
                st.progress(score / 100)
                st.markdown(f"**Sentiment Score:** {sentiment}")
                if flags:
                    st.markdown("**⚠️ Red Flags Found:**")
                    for flag in flags:
                        st.markdown(f"- {flag}")
                else:
                    st.success("✅ No red flags detected!")
            with col_b:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=score,
                    title={"text": "Fake Score"},
                    gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#FF4B4B"},
                           "steps": [{"range": [0, 35], "color": "#1a472a"},
                                     {"range": [35, 100], "color": "#7b0000"}]}
                ))
                fig.update_layout(paper_bgcolor="#0f1117", font_color="white", height=300)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please enter a review first!")

# ─────────────────────────────────────────────
# PRICE DROP PREDICTION
# ─────────────────────────────────────────────
elif feature == "📉 Price Drop Prediction":
    st.title("📉 Price Drop Prediction")
    st.markdown("See price history and predict if the price will drop soon.")
    st.markdown("---")

    product = st.selectbox("Select a product:", list(PRODUCTS.keys()))

    if st.button("📊 Predict Price"):
        prices, predicted, trend = predict_price(product)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### {product}")
            st.markdown(f"**Current Price:** ₹{prices[-1]}")
            st.markdown(f"**Predicted Next Week:** ₹{predicted}")
            st.markdown(f"**Trend:** {trend}")
            savings = prices[-1] - predicted
            if savings > 0:
                st.success(f"💰 Wait! You could save ₹{savings} next week!")
            else:
                st.warning("🛒 Buy now — price may go up!")
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=WEEKS, y=prices, mode="lines+markers",
                name="Actual Price", line=dict(color="#FF4B4B", width=3), marker=dict(size=8)))
            fig.add_trace(go.Scatter(x=[WEEKS[-1], "Next Week"], y=[prices[-1], predicted],
                mode="lines+markers", name="Predicted",
                line=dict(color="#00cc88", width=3, dash="dash"), marker=dict(size=10, symbol="star")))
            fig.update_layout(title="Price Trend (₹)", paper_bgcolor="#0f1117",
                plot_bgcolor="#1e2130", font_color="white", height=350)
            st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# SUSTAINABILITY SCORE
# ─────────────────────────────────────────────
elif feature == "🌿 Sustainability Score":
    st.title("🌿 Sustainability Score")
    st.markdown("Check how eco-friendly a product is before buying.")
    st.markdown("---")

    product = st.selectbox("Select a product:", list(PRODUCTS.keys()))

    if st.button("🌍 Check Sustainability"):
        score, label, tips, category = get_sustainability(product)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### {product}")
            st.markdown(f"**Category:** {category}")
            st.markdown(f"**Rating:** {label}")
            st.markdown(f"**Score: {score}/100**")
            st.progress(score / 100)
            st.info(f"💡 {tips}")
        with col2:
            color = "#00cc88" if score >= 80 else "#ffaa00" if score >= 60 else "#FF4B4B"
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=score,
                title={"text": "Eco Score"},
                gauge={"axis": {"range": [0, 100]}, "bar": {"color": color},
                       "steps": [{"range": [0, 40], "color": "#3d0000"},
                                 {"range": [40, 70], "color": "#3d3000"},
                                 {"range": [70, 100], "color": "#003d1a"}]}
            ))
            fig.update_layout(paper_bgcolor="#0f1117", font_color="white", height=300)
            st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# OUTFIT GENERATOR
# ─────────────────────────────────────────────
elif feature == "👗 Outfit Generator":
    st.title("👗 AI Outfit Generator")
    st.markdown("Get outfit recommendations powered by AI.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        occasion = st.selectbox("Select Occasion:", ["College", "Office", "Party", "Gym"])
    with col2:
        style = st.selectbox("Select Style:", ["Casual", "Formal", "Trendy", "Sporty"])

    budget = st.slider("Budget (₹):", 500, 10000, 2000, step=500)

    if st.button("👗 Generate Outfit"):
        outfit = generate_outfit(occasion, style)
        st.markdown("---")
        st.markdown(f"### 👗 Outfit for **{occasion}** ({style}) — Budget ₹{budget}")
        cols = st.columns(4)
        items = ["Top", "Bottom", "Footwear", "Accessories"]
        icons = ["👕", "👖", "👟", "⌚"]
        for i, (item, icon) in enumerate(zip(items, icons)):
            with cols[i]:
                st.markdown(f'<div class="feature-box"><h4>{icon} {item}</h4><p>{outfit[item]}</p></div>', unsafe_allow_html=True)
        st.success(f"💡 Style Tip: {outfit['Tip']}")

# ─────────────────────────────────────────────
# RETURN FRAUD DETECTION
# ─────────────────────────────────────────────
elif feature == "🚨 Return Fraud Detection":
    st.title("🚨 Return Fraud Detection")
    st.markdown("Detect suspicious return requests to protect sellers.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        order_id = st.text_input("Order ID:", placeholder="e.g. ORD123456")
        reason = st.selectbox("Return Reason:", [
            "Defective product", "Wrong item received",
            "Not needed", "Changed mind", "Just checking", "Size issue"
        ])
    with col2:
        days_used = st.slider("Days used before return:", 0, 60, 5)
        num_returns = st.slider("Total past returns by this customer:", 0, 20, 1)

    if st.button("🔍 Check Fraud Risk"):
        verdict, risk_score, flags = detect_return_fraud(order_id, reason, days_used, num_returns)
        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"### Result: {verdict}")
            st.markdown(f"**Risk Score: {risk_score}/100**")
            st.progress(risk_score / 100)
            if flags:
                st.markdown("**⚠️ Risk Factors:**")
                for flag in flags:
                    st.markdown(f"- {flag}")
            else:
                st.success("✅ No fraud indicators found!")
        with col_b:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=risk_score,
                title={"text": "Fraud Risk"},
                gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#FF4B4B"},
                       "steps": [{"range": [0, 50], "color": "#1a472a"},
                                 {"range": [50, 100], "color": "#7b0000"}]}
            ))
            fig.update_layout(paper_bgcolor="#0f1117", font_color="white", height=300)
            st.plotly_chart(fig, use_container_width=True)
