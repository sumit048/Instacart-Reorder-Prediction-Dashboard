import streamlit as st
import pandas as pd
import numpy as np
import joblib
import base64
from utils.db_import import load_data_from_db

# ------------------ PAGE CONFIGURATION ------------------
st.set_page_config(page_title="Instacart Reorder Predictor", layout="wide")

# ------------------ CUSTOM GLOBAL STYLES ------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
    background-color: #023020 !important;
    color: #FFF4CB !important;
}

h1, h2, h3 {
    color: #FFF4CB !important;
    font-weight: 700;
}

input, textarea, select, .stNumberInput input, .stTextInput input {
    background-color: #043d2c !important;
    color: #FFF4CB !important;
    border: 3px solid black !important;
    border-radius: 6px !important;
    padding: 8px !important;
    font-weight: 500;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: #043d2c !important;
    color: #FFF4CB !important;
    border: 3px solid black !important;
    border-radius: 6px !important;
}

label, .stTextInput label, .stSelectbox label, .stSlider label {
    color: black !important;
    font-weight: 600;
}

.css-1emrehy, .css-14xtw13, .stSlider {
    color: black !important;
}

[data-testid="stSlider"] [role="slider"] {
    background-color: orange !important;
    border-radius: 50% !important;
    width: 20px;
    height: 20px;
    border: 2px solid black;
}

[data-testid="stSlider"] > div > div:nth-child(1) {
    background-color: transparent !important;
    height: 6px;
    border-radius: 4px;
}

.stButton > button {
    font-size: 13px;
    padding: 10px 16px;
    margin-bottom: 0.5rem;
    border: 3px solid black;
    border-radius: 10px;
    background-color: transparent !important;
    color: #FFF4CB !important;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: rgba(255,255,255,0.05) !important;
    transform: scale(1.03);
}

[data-testid="stMetricValue"] {
    color: #FFF4CB;
    font-size: 1.6rem;
    font-weight: bold;
}

div[class^="block-container"] {
    padding: 2rem;
    border-radius: 16px;
    background-color: #ffffff0d;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

header, .st-emotion-cache-18ni7ap {
    visibility: hidden;
    height: 0;
    margin: 0;
    padding: 0;
}

.block-container {
    padding-top: 0rem !important;
}

#logo-container {
    position: absolute;
    top: 5px;
    right: 20px;
    z-index: 9999;
}

.active-button {
    background-color: #FFF4CB !important;
    color: #023020 !important;
    font-weight: bold;
    border: 3px solid black;
    border-radius: 8px;
    padding: 10px 24px;
    display: inline-block;
    margin-right: 1rem;
    margin-bottom: 1rem;
    cursor: default;
}

.toggle-container {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 2rem;
}
.toggle-button {
    font-size: 16px;
    font-weight: 600;
    padding: 12px 28px;
    border: 3px solid black;
    border-radius: 10px;
    background-color: transparent;
    color: #FFF4CB;
    transition: all 0.2s ease;
    cursor: pointer;
    text-align: center;
}
.toggle-button:hover {
    background-color: rgba(255, 255, 255, 0.07);
    transform: scale(1.04);
}
.toggle-button.active {
    background-color: #FFF4CB;
    color: #023020;
}
</style>
""", unsafe_allow_html=True)

# ------------------ LOGO SECTION ------------------
def image_to_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

encoded_logo = image_to_base64("instacart_logo.png")

st.markdown(f"""
<div id="logo-container">
    <img src="data:image/png;base64,{encoded_logo}" width="180"/>
</div>
""", unsafe_allow_html=True)

# ------------------ LOAD TRAINED MODEL ------------------
uploaded_model = st.file_uploader("Upload your model (.joblib)", type=["joblib"])

if uploaded_model is not None:
    model = joblib.load(uploaded_model)
    st.success("✅ Model loaded successfully!")
else:
    st.warning("⚠️ Please upload your trained model file (model.joblib) to proceed.")
    st.stop()

# ------------------ SETUP PAGE STATE ------------------
if "page" not in st.session_state:
    st.session_state.page = "single"

# ------------------ PAGE TITLE ------------------
st.markdown("<div style='padding-top: 80px;'></div>", unsafe_allow_html=True)
st.markdown("<h1 style='color: #FFF4CB; font-weight: 800;'>🛒 Instacart Reorder Prediction Dashboard</h1>", unsafe_allow_html=True)

# ------------------ PAGE SWITCHING BUTTONS ------------------
col1, col2 = st.columns([1, 1])
with col1:
    if st.session_state.page == "single":
        st.markdown("<div class='toggle-button active'>🍇 Single Prediction</div>", unsafe_allow_html=True)
    else:
        if st.button("🍇 Single Prediction", key="to_single"):
            st.session_state.page = "single"
            st.rerun()

with col2:
    if st.session_state.page == "batch":
        st.markdown("<div class='toggle-button active'>📂 Batch Prediction</div>", unsafe_allow_html=True)
    else:
        if st.button("📂 Batch Prediction", key="to_batch"):
            st.session_state.page = "batch"
            st.rerun()

# ------------------ SINGLE PREDICTION MODE ------------------
if st.session_state.page == "single":
    st.subheader("Enter Order Details")

    user_id = st.number_input("User ID", min_value=1, value=1)
    # Load product names and IDs (make sure products.csv is present)
    products_df = load_data_from_db("sqlite:///instacart.db", "products")
    product_map = dict(zip(products_df["product_name"], products_df["product_id"]))
    product_name = st.selectbox("Product Name", list(product_map.keys()))
    product_id = product_map[product_name]
    st.write(f"Selected Product ID: `{product_id}`")

    order_dow = st.selectbox("Day of Week", list(range(7)), format_func=lambda x: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][x])
    order_hour_of_day = st.slider("Order Hour", 0, 23, 10)
    add_to_cart_order = st.number_input("Add-to-Cart Position", min_value=1, value=1)
    user_total_orders = st.number_input("User Total Orders", min_value=1, value=5)
    product_reorder_rate = st.slider("Product Reorder Rate", min_value=0.0, max_value=1.0, value=0.3)
    days_since_prior_order = st.slider("Days Since Prior Order", min_value=0, max_value=30, value=7)

    if user_id > 200000 or product_id > 50000:
        st.error("❌ Unknown user or product – reorder cannot be predicted reliably.")
    else:
        if st.button("🔍 Predict Reorder"):
            input_data = np.array([[user_id, product_id, order_dow, order_hour_of_day,
                                    add_to_cart_order, user_total_orders,
                                    product_reorder_rate, days_since_prior_order]])
            prediction = model.predict(input_data)[0]

            if prediction == 1:
                st.markdown("""
                <div style="background-color:#22c55e; padding:20px; border-radius:12px; text-align:center; animation: fadeIn 0.7s ease-out;">
                    <img src="https://cdn-icons-png.flaticon.com/512/845/845646.png" width="80"/>
                    <h3 style="color:white; margin-top:10px;">Product likely to be reordered</h3>
                </div>
                <style>
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                </style>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color:#dc2626; padding:20px; border-radius:12px; text-align:center; animation: fadeIn 0.7s ease-out;">
                    <img src="https://cdn-icons-png.flaticon.com/512/463/463612.png" width="80"/>
                    <h3 style="color:white; margin-top:10px;">Product not likely to be reordered</h3>
                </div>
                <style>
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                </style>
                """, unsafe_allow_html=True)
# ------------------ BATCH PREDICTION MODE ------------------
elif st.session_state.page == "batch":
    st.subheader("Upload a CSV of Orders 📂")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("📄 Preview of uploaded data:", df.head())

        if st.button("📊 Predict for All Rows"):
            # ✅ Keep only columns used during model training
            required_cols = [
                "user_id", "product_id", "order_dow", "order_hour_of_day",
                "add_to_cart_order", "user_total_orders",
                "product_reorder_rate", "days_since_prior_order"
            ]

            # Validate columns
            if not set(required_cols).issubset(df.columns):
                st.error("Uploaded file is missing one or more required columns.")
                st.stop()

            # Drop extra columns
            df_model_input = df[required_cols]

            # Predict
            predictions = model.predict(df_model_input)
            df["reordered_prediction"] = predictions

            yes = int((df["reordered_prediction"] == 1).sum())
            no = int((df["reordered_prediction"] == 0).sum())

            col1, col2, col3 = st.columns(3)
            col1.metric("✅ Will Reorder", yes)
            col2.metric("❌ Will Not Reorder", no)
            col3.metric("📦 Total Rows", len(df))

            st.dataframe(df)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Results", csv, "instacart_predictions.csv", "text/csv")
