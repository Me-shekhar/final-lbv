import streamlit as st
import pandas as pd

# --- NEUBRUTALISM STYLING ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #FFFFFF; color: #000000; }
    
    /* Input Box Containers */
    div[data-baseweb="select"], div[data-baseweb="slider"], .stNumberInput {
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #000000;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background-color: #000000;
        color: #FFFFFF;
        border: 2px solid #000000;
        border-radius: 0px;
        font-weight: bold;
        box-shadow: 4px 4px 0px #888888;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #FFFFFF;
        color: #000000;
        box-shadow: 2px 2px 0px #000000;
    }

    /* Range Labels */
    .range-label {
        font-size: 0.8rem;
        font-weight: bold;
        color: #555555;
        margin-bottom: -10px;
    }

    /* History Cards */
    .history-card {
        border: 2px solid #000000;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 3px 3px 0px #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOCK DATA RANGES (Replace these with your actual dataset min/max) ---
fuel_data_info = {
    "Methane (CH4)": {"temp": (300, 600), "phi": (0.7, 1.4), "pres": (1, 10), "blend": False},
    "Hydrogen (H2)": {"temp": (300, 500), "phi": (0.5, 4.0), "pres": (1, 5), "blend": False},
    "CH4-H2 Blend": {"temp": (300, 800), "phi": (0.6, 1.6), "pres": (1, 20), "blend": True}
}

st.title("📂 LBV_RESEARCH_v1.0")
st.write("---")

# 1. FUEL SELECTION
selected_fuel = st.selectbox("HYDROCARBON / FUEL TYPE", list(fuel_data_info.keys()))
info = fuel_data_info[selected_fuel]

# 2. FRACTIONS (Conditional)
if info["blend"]:
    st.markdown('<p class="range-label">Ratio: 0.0 to 1.0</p>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        frac_a = st.select_slider("FRACTION A", options=[round(x*0.01, 2) for x in range(101)], value=0.5)
    with col_b:
        frac_b = st.select_slider("FRACTION B", options=[round(x*0.01, 2) for x in range(101)], value=0.5)
else:
    st.info(f"Fixed composition for {selected_fuel}.")
    frac_a, frac_b = 1.0, 0.0

# 3. ENVIRONMENT PARAMETERS WITH DYNAMIC LABELS
st.write("") 

# Temperature
st.markdown(f'<p class="range-label">Valid Range: {info["temp"][0]}K - {info["temp"][1]}K</p>', unsafe_allow_html=True)
temp = st.select_slider("INITIAL TEMPERATURE (K)", 
                        options=list(range(info["temp"][0], info["temp"][1] + 1, 10)))

# Equivalence Ratio
st.markdown(f'<p class="range-label">Valid Range: {info["phi"][0]} - {info["phi"][1]}</p>', unsafe_allow_html=True)
phi = st.select_slider("EQUIVALENCE RATIO (φ)", 
                       options=[round(x*0.1, 1) for x in range(int(info["phi"][0]*10), int(info["phi"][1]*10) + 1)])

# Pressure
st.markdown(f'<p class="range-label">Valid Range: {info["pres"][0]}atm - {info["pres"][1]}atm</p>', unsafe_allow_html=True)
pres = st.select_slider("PRESSURE (atm)", 
                        options=list(range(info["pres"][0], info["pres"][1] + 1)))

# 4. PREDICT AND TOGGLE
st.write("---")
unit_toggle = st.toggle("CONVERT TO m/s")

if st.button("PREDICT LBV"):
    # Mock result until PKL is connected
    res_cm = 38.2
    display_res = res_cm / 100 if unit_toggle else res_cm
    unit = "m/s" if unit_toggle else "cm/s"
    
    st.markdown(f"""
        <div style="border: 3px solid black; padding: 20px; background-color: #00ff00; box-shadow: 6px 6px 0px black;">
            <h2 style="margin:0;">RESULT: {display_res} {unit}</h2>
        </div>
    """, unsafe_allow_html=True)

# 5. HISTORY
st.write("### 📜 HISTORY")
st.markdown("""
    <div class="history-card">
        <strong>CH4</strong> | Temp: 300K | Phi: 1.0 | <strong>38.2 cm/s</strong>
    </div>
""", unsafe_allow_html=True)
