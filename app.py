import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from textblob import TextBlob
import json
import random

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Smart E-commerce AI Assistant",
    page_icon="🛒",
    layout="wide"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
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
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SAMPLE PRODUCT DATABASE
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
    }
}

WEEKS = ["6 weeks ago", "5 weeks ago", "4 weeks ago", "3 weeks ago", "2 weeks ago", "Last week", "Today"]

# ─────────────────────────────────────────────
# AI FUNCTION (Ollama + Offline Fallback)
# ─────────────────────────────────────────────
def ask_ollama(prompt):
    return None  # Offline mode - using rule-based AI only

# ─────────────────────────────────────────────
# FEATURE 1: FAKE REVIEW DETECTION
# ─────────────────────────────────────────────
def analyze_review(review_text):
    blob = TextBlob(review_text)
    sentiment = blob.sentiment.polarity  # -1 to +1
    word_count = len(review_text.split())
    exclamation_count = review_text.count("!")
    caps_ratio = sum(1 for c in review_text if c.isupper()) / max(len(review_text), 1)

    red_flags = []
    score = 0  # Higher = more likely fake

    if word_count < 8:
        red_flags.append("⚠️ Too short (less than 8 words)")
        score += 25
    if exclamation_count >= 3:
        red_flags.append("⚠️ Too many exclamation marks")
        score += 20
    if caps_ratio > 0.4:
        red_flags.append("⚠️ Excessive CAPS usage")
        score += 25
    if sentiment > 0.85:
        red_flags.append("⚠️ Suspiciously over-positive sentiment")
        score += 20
    if word_count > 5 and len(set(review_text.lower().split())) / word_count < 0.5:
        red_flags.append("⚠️ Repetitive words detected")
        score += 10

    score = min(score, 100)
    verdict = "🔴 LIKELY FAKE" if score >= 50 else "🟢 LIKELY GENUINE"
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
st.sidebar.image("https://img.icons8.com/color/96/shopping-cart.png", width=80)
st.sidebar.title("🛒 AI Assistant")
st.sidebar.markdown("**Smart E-commerce AI**")
st.sidebar.markdown("---")

feature = st.sidebar.selectbox(
    "Choose a Feature",
    [
        "🏠 Home",
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
    st.title("🛒 Smart E-commerce AI Assistant")
    st.markdown("### Your AI-powered smart shopping co-pilot")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-box"><h3>🕵️ Fake Review Detection</h3><p>Detect suspicious reviews using sentiment analysis and linguistic patterns.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-box"><h3>📉 Price Drop Prediction</h3><p>Predict future price drops based on historical price trends.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-box"><h3>🌿 Sustainability Score</h3><p>Check how eco-friendly a product is before you buy.</p></div>', unsafe_allow_html=True)

    col4, col5 = st.columns(2)
    with col4:
        st.markdown('<div class="feature-box"><h3>👗 Outfit Generator</h3><p>Get AI-powered outfit recommendations for any occasion.</p></div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="feature-box"><h3>🚨 Return Fraud Detection</h3><p>Identify suspicious return patterns to protect sellers.</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.info("👈 Select a feature from the sidebar to get started!")

# ─────────────────────────────────────────────
# FAKE REVIEW DETECTION
# ─────────────────────────────────────────────
elif feature == "🕵️ Fake Review Detection":
    st.title("🕵️ Fake Review Detection")
    st.markdown("Paste any product review below to check if it's genuine or fake.")
    st.markdown("---")

    product = st.selectbox("Or pick a sample product to test its reviews:", list(PRODUCTS.keys()))
    sample_reviews = PRODUCTS[product]["reviews"]

    col1, col2 = st.columns([2, 1])
    with col1:
        review_input = st.text_area("Enter a review to analyze:", height=120, placeholder="Type or paste a review here...")
    with col2:
        st.markdown("**Quick Test — Sample Reviews:**")
        for i, r in enumerate(sample_reviews):
            if st.button(f"Review {i+1}", key=f"rev_{i}"):
                review_input = r
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
                st.markdown(f"**Sentiment Score:** {sentiment} (-1=Negative, +1=Positive)")

                if flags:
                    st.markdown("**⚠️ Red Flags Found:**")
                    for flag in flags:
                        st.markdown(f"- {flag}")
                else:
                    st.success("✅ No red flags detected!")

            with col_b:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    title={"text": "Fake Score"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#FF4B4B"},
                        "steps": [
                            {"range": [0, 50], "color": "#1a472a"},
                            {"range": [50, 100], "color": "#7b0000"},
                        ],
                    }
                ))
                fig.update_layout(paper_bgcolor="#0f1117", font_color="white", height=300)
                st.plotly_chart(fig, use_container_width=True)

            # Try Ollama for extra insight
            ai_response = ask_ollama(f"In 2 sentences, explain why this review might be fake or genuine: '{review_input}'")
            if ai_response:
                st.markdown("**🤖 AI Insight:**")
                st.info(ai_response)
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
            fig.add_trace(go.Scatter(
                x=WEEKS, y=prices,
                mode="lines+markers",
                name="Actual Price",
                line=dict(color="#FF4B4B", width=3),
                marker=dict(size=8)
            ))
            fig.add_trace(go.Scatter(
                x=[WEEKS[-1], "Next Week"], y=[prices[-1], predicted],
                mode="lines+markers",
                name="Predicted",
                line=dict(color="#00cc88", width=3, dash="dash"),
                marker=dict(size=10, symbol="star")
            ))
            fig.update_layout(
                title="Price Trend (₹)",
                paper_bgcolor="#0f1117",
                plot_bgcolor="#1e2130",
                font_color="white",
                height=350
            )
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
                mode="gauge+number",
                value=score,
                title={"text": "Eco Score"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": color},
                    "steps": [
                        {"range": [0, 40], "color": "#3d0000"},
                        {"range": [40, 70], "color": "#3d3000"},
                        {"range": [70, 100], "color": "#003d1a"},
                    ],
                }
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
        st.markdown(f"### 👗 Outfit for **{occasion}** ({style} Style) — Budget ₹{budget}")

        cols = st.columns(4)
        items = ["Top", "Bottom", "Footwear", "Accessories"]
        icons = ["👕", "👖", "👟", "⌚"]
        for i, (item, icon) in enumerate(zip(items, icons)):
            with cols[i]:
                st.markdown(f'<div class="feature-box"><h4>{icon} {item}</h4><p>{outfit[item]}</p></div>', unsafe_allow_html=True)

        st.success(f"💡 Style Tip: {outfit['Tip']}")

        # Try Ollama for extra suggestion
        ai_response = ask_ollama(f"Give one short styling tip for a {style} {occasion} outfit in India within ₹{budget} budget.")
        if ai_response:
            st.markdown("**🤖 AI Styling Tip:**")
            st.info(ai_response)

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
            "Defective product",
            "Wrong item received",
            "Not needed",
            "Changed mind",
            "Just checking",
            "Size issue"
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
                mode="gauge+number",
                value=risk_score,
                title={"text": "Fraud Risk"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#FF4B4B"},
                    "steps": [
                        {"range": [0, 50], "color": "#1a472a"},
                        {"range": [50, 100], "color": "#7b0000"},
                    ],
                }
            ))
            fig.update_layout(paper_bgcolor="#0f1117", font_color="white", height=300)
            st.plotly_chart(fig, use_container_width=True)
