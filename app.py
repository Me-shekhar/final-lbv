import streamlit as st
import pandas as pd

# --- ADAPTIVE THEME CONFIG ---
st.set_page_config(page_title="LBV Research Dashboard", layout="wide")

# --- CUSTOM CSS FOR CYAN/BLUE LIGHT MODE & DARK MODE SUPPORT ---
st.markdown("""
    <style>
    /* 1. DEFINE COLORS FOR LIGHT & DARK MODE */
    :root {
        --bg-color: #E0F7FA;          /* Light Cyan Background */
        --card-bg: #FFFFFF;           /* White Cards */
        --text-color: #1A365D;        /* Dark Blue Text */
        --accent-color: #00BCD4;      /* Cyan Accent */
        --border-color: #B2EBF2;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: #0F172A;      /* Deep Dark Blue Background */
            --card-bg: #1E293B;       /* Dark Slate Cards */
            --text-color: #F8FAFC;    /* Off-White Text */
            --accent-color: #22D3EE;  /* Bright Cyan Accent */
            --border-color: #334155;
        }
    }

    /* 2. APPLY THEME */
    .stApp { background-color: var(--bg-color); color: var(--text-color); }
    
    /* Input Cards */
    .input-card {
        background-color: var(--card-bg);
        padding: 25px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    /* Range Labels */
    .range-label {
        font-size: 0.8rem;
        color: var(--accent-color);
        font-weight: bold;
        margin-bottom: -10px;
    }

    /* Labels & Headings */
    label, h1, h2, h3 { color: var(--text-color) !important; }

    /* Buttons */
    .stButton>button {
        background-color: var(--accent-color);
        color: #000000;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- APP CONTENT ---
st.title("🧪 LBV Predictor: Multi-Fidelity Model")

# Layout: Main Input and Side History
col_main, col_hist = st.columns([2.5, 1])

# MOCK DATA FOR THE RANGES
fuel_options = {
    "Methane (CH4)": {"t": (300, 600), "phi": (0.7, 1.4), "p": (1, 10), "blend": False},
    "CH4-H2 Blend": {"t": (300, 800), "phi": (0.5, 2.5), "p": (1, 25), "blend": True}
}

with col_main:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    
    # Fuel Dropdown
    fuel = st.selectbox("HYDROCARBON SELECTION", list(fuel_options.keys()))
    data = fuel_options[fuel]
    
    # Fractions (Conditional Unlocking)
    if data["blend"]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<p class="range-label">Fraction Range: 0.0 - 1.0</p>', unsafe_allow_html=True)
            frac_a = st.select_slider("FRACTION A", options=[round(x*0.01, 2) for x in range(101)], value=0.5)
        with c2:
            st.markdown('<p class="range-label">Fraction Range: 0.0 - 1.0</p>', unsafe_allow_html=True)
            frac_b = st.select_slider("FRACTION B", options=[round(x*0.01, 2) for x in range(101)], value=0.5)
    else:
        st.info("💡 Pure fuel selected. Composition fractions are locked.")

    # Pressure Slider
    st.markdown(f'<p class="range-label">Dataset Range: {data["p"][0]} - {data["p"][1]} atm</p>', unsafe_allow_html=True)
    pres = st.select_slider("PRESSURE (atm)", options=list(range(data["p"][0], data["p"][1] + 1)))

    # Temperature Slider
    st.markdown(f'<p class="range-label">Dataset Range: {data["t"][0]} - {data["t"][1]} K</p>', unsafe_allow_html=True)
    temp = st.select_slider("INITIAL TEMPERATURE (K)", options=list(range(data["t"][0], data["t"][1] + 1, 10)))

    # Phi Slider
    st.markdown(f'<p class="range-label">Dataset Range: {data["phi"][0]} - {data["phi"][1]}</p>', unsafe_allow_html=True)
    phi = st.select_slider("EQUIVALENCE RATIO (φ)", options=[round(x*0.1, 1) for x in range(int(data["phi"][0]*10), int(data["phi"][1]*10) + 1)])

    # Predict Section
    st.write("---")
    u_col, b_col = st.columns([1, 2])
    with u_col:
        m_s_toggle = st.toggle("Show in m/s")
    
    if st.button("PREDICT LBV"):
        # We will link the PKL here next
        st.success("Calculation Complete!")
        st.metric("LBV Result", "42.50 cm/s" if not m_s_toggle else "0.4250 m/s")

    st.markdown('</div>', unsafe_allow_html=True)

with col_hist:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.subheader("📜 History")
    st.write("Recent queries will appear here.")
    # Placeholder for history list
    st.markdown('</div>', unsafe_allow_html=True)
