import streamlit as st
import pandas as pd
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="LBV Predictor", layout="centered")

# --- CUSTOM AESTHETIC STYLING (Healing Colors) ---
st.markdown("""
    <style>
    .main { background-color: #f0f4f4; }
    .stButton>button {
        background-color: #4db6ac;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
    }
    .stButton>button:hover { background-color: #00897b; border: none; }
    div[data-testid="stMetricValue"] { color: #00796b; }
    .history-box {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE FOR HISTORY ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- APP HEADER ---
st.title("🌿 LBV Research Portal")
st.markdown("Select your parameters below to predict **Laminar Burning Velocity**.")

# --- INPUT SECTION ---
with st.container():
    st.subheader("Parameter Selection")
    
    # 1. Fuel Selection (Dropdown only)
    fuel_list = ["Methane (CH4)", "Hydrogen (H2)", "Methane-Hydrogen Blend", "Propane", "Syngas"]
    selected_fuel = st.selectbox("Select Fuel Type", options=fuel_list, index=0)

    # 2. Fractions Logic (Unlocked only if "Blend" is selected)
    # You can customize this list based on which fuels in your dataset are blends
    col1, col2 = st.columns(2)
    if "Blend" in selected_fuel or "Syngas" in selected_fuel:
        with col1:
            frac_a = st.select_slider("Fraction A", options=[round(x * 0.01, 2) for x in range(0, 101)], value=0.50)
        with col2:
            frac_b = st.select_slider("Fraction B", options=[round(x * 0.01, 2) for x in range(0, 101)], value=0.50)
    else:
        frac_a = 1.0
        frac_b = 0.0
        st.info("Single component fuel selected. Fractions are locked.")

    # 3. Environment Parameters (Slider only to prevent typing)
    phi = st.select_slider("Equivalence Ratio (φ)", options=[round(x * 0.1, 1) for x in range(5, 26)], value=1.0)
    temp = st.select_slider("Initial Temperature (K)", options=list(range(300, 801, 10)), value=300)
    pres = st.select_slider("Pressure (bar)", options=list(range(1, 51)), value=1)

# --- PREDICTION & TOGGLE ---
st.divider()
t_col1, t_col2 = st.columns([2, 1])

with t_col2:
    unit_mode = st.toggle("Switch to m/s", value=False)

if st.button("Predict LBV", use_container_width=True):
    with st.spinner('Calculating physics...'):
        time.sleep(0.5) # Simulating calculation
        
        # NOTE: Once we create the .pkl, we will replace this dummy math
        # Placeholder prediction (cm/s)
        dummy_prediction = 35.42 + (phi * 2) + (temp / 100) 
        
        # Unit conversion
        if unit_mode:
            final_val = dummy_prediction / 100
            unit = "m/s"
        else:
            final_val = dummy_prediction
            unit = "cm/s"
            
        st.metric(label="Predicted Result", value=f"{final_val:.4f} {unit}")
        
        # Add to history
        new_entry = {
            "Fuel": selected_fuel,
            "Phi": phi,
            "Temp": temp,
            "Result": f"{final_val:.4f} {unit}"
        }
        st.session_state.history.insert(0, new_entry)

# --- HISTORY SECTION ---
st.divider()
st.subheader("📜 Prediction History")
if st.session_state.history:
    for item in st.session_state.history[:5]: # Show last 5
        st.markdown(f"""
        <div class="history-box">
            <strong>Fuel:</strong> {item['Fuel']} | <strong>Phi:</strong> {item['Phi']} | 
            <strong>Temp:</strong> {item['Temp']}K | <strong>LBV:</strong> {item['Result']}
        </div><br>
        """, unsafe_allow_html=True)
else:
    st.write("No predictions yet.")
