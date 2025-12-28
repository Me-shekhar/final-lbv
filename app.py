import streamlit as st
import pandas as pd

# --- UI CONFIGURATION ---
st.set_page_config(page_title="LBV Predictor Dashboard", layout="wide")

# --- CUSTOM CSS FOR BLUE/WHITE THEME & DASHBOARD LAYOUT ---
st.markdown("""
    <style>
    /* Background and Sidebar */
    .stApp { background-color: #F0F4F8; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #D1E1F0; }
    
    /* Headers */
    h1, h2, h3 { color: #1E3A8A; font-family: 'Inter', sans-serif; }
    
    /* Cards for Inputs and History */
    .input-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* Range Label Styling */
    .range-label {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        margin-bottom: -15px;
    }

    /* Prediction Button */
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        border-radius: 10px;
        border: none;
        height: 50px;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .stButton>button:hover { background-color: #1E40AF; color: white; }
    
    /* Metric Display */
    [data-testid="stMetricValue"] { color: #2563EB; font-size: 2.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA RANGES (Update with your CSV values later) ---
fuel_info = {
    "Methane (CH4)": {"t": (300, 600), "p": (0.7, 1.4), "pr": (1, 10), "is_blend": False},
    "Hydrogen (H2)": {"t": (300, 500), "p": (0.5, 4.0), "pr": (1, 5), "is_blend": False},
    "CH4-H2 Blend": {"t": (300, 800), "p": (0.6, 1.6), "pr": (1, 20), "is_blend": True}
}

# --- HEADER SECTION ---
st.title("🔬 LBV Research Predictor")
st.markdown("##### Accurate Laminar Burning Velocity forecasting via Experimental & Simulation Data")
st.write("---")

# --- MAIN DASHBOARD LAYOUT ---
col_main, col_hist = st.columns([2.5, 1])

with col_main:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.subheader("🛠️ Input Parameters")
    
    # 1. Fuel Selection
    fuel = st.selectbox("Select Hydrocarbon / Fuel Type", list(fuel_info.keys()))
    current = fuel_info[fuel]
    
    # 2. Fractions Section (Unlocks only for blends)
    if current["is_blend"]:
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            st.markdown('<p class="range-label">Range: 0.0 - 1.0</p>', unsafe_allow_html=True)
            frac_a = st.select_slider("Fraction A", options=[round(x*0.01, 2) for x in range(101)], value=0.5)
        with f_col2:
            st.markdown('<p class="range-label">Range: 0.0 - 1.0</p>', unsafe_allow_html=True)
            frac_b = st.select_slider("Fraction B", options=[round(x*0.01, 2) for x in range(101)], value=0.5)
    else:
        st.info("💡 Fraction controls locked for single-component fuels.")
        frac_a, frac_b = 1.0, 0.0

    # 3. Sliders with Range Labels above them
    st.write("")
    
    # Temperature
    st.markdown(f'<p class="range-label">Valid Range: {current["t"][0]}K - {current["t"][1]}K</p>', unsafe_allow_html=True)
    temp = st.select_slider("Initial Temperature (K)", options=list(range(current["t"][0], current["t"][1]+1, 5)))

    # Equivalence Ratio
    st.markdown(f'<p class="range-label">Valid Range: {current["p"][0]} - {current["p"][1]}</p>', unsafe_allow_html=True)
    phi = st.select_slider("Equivalence Ratio (φ)", options=[round(x*0.1, 1) for x in range(int(current["p"][0]*10), int(current["p"][1]*10)+1)])

    # Pressure
    st.markdown(f'<p class="range-label">Valid Range: {current["pr"][0]}atm - {current["pr"][1]}atm</p>', unsafe_allow_html=True)
    pres = st.select_slider("Pressure (atm)", options=list(range(current["pr"][0], current["pr"][1]+1)))

    # 4. Action Section
    st.write("---")
    unit_col, btn_col = st.columns([1, 2])
    with unit_col:
        unit_toggle = st.toggle("Convert to m/s", help="Toggle between cm/s and m/s")
    
    if st.button("🚀 PREDICT LBV"):
        # Placeholder for Model Prediction
        res_cm = 42.15 
        final_val = res_cm / 100 if unit_toggle else res_cm
        u_label = "m/s" if unit_toggle else "cm/s"
        st.metric(label="Predicted Result", value=f"{final_val:.4f} {u_label}")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_hist:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.subheader("📜 Recent History")
    
    # Sample History Items
    history_data = [
        {"f": "CH4", "phi": 1.0, "v": "38.2 cm/s"},
        {"f": "H2", "phi": 1.2, "v": "120.4 cm/s"},
        {"f": "Blend", "phi": 0.9, "v": "45.1 cm/s"}
    ]
    
    for item in history_data:
        st.write(f"**{item['f']}** | φ: {item['phi']} → `{item['v']}`")
        st.write("---")
    
    st.markdown('</div>', unsafe_allow_html=True)
