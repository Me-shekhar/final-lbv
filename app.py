import streamlit as st
import pandas as pd
import pickle
import xgboost as xgb

# --- ADAPTIVE THEME CONFIG ---
st.set_page_config(page_title="LBV Research Dashboard", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    :root {
        --bg-color: #E0F7FA;
        --card-bg: #FFFFFF;
        --text-color: #1A365D;
        --accent-color: #00BCD4;
        --border-color: #B2EBF2;
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: #0F172A;
            --card-bg: #1E293B;
            --text-color: #F8FAFC;
            --accent-color: #22D3EE;
            --border-color: #334155;
        }
    }
    .stApp { background-color: var(--bg-color); color: var(--text-color); }
    .input-card {
        background-color: var(--card-bg);
        padding: 25px;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .range-label { font-size: 0.8rem; color: var(--accent-color); font-weight: bold; margin-bottom: -10px; }
    label, h1, h2, h3 { color: var(--text-color) !important; }
    .stButton>button { background-color: var(--accent-color); color: #000000; font-weight: bold; width: 100%; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD THE MODEL BUNDLE ---
@st.cache_resource
def load_bundle():
    # Make sure this file is uploaded to your GitHub repository!
    with open("lbv_model_bundle.pkl", "rb") as f:
        return pickle.load(f)

try:
    bundle = load_bundle()
    model = bundle["model"]
    le = bundle["label_encoder"]
except FileNotFoundError:
    st.error("❌ Error: 'lbv_model_bundle.pkl' not found. Please upload it to your GitHub repo.")
    st.stop()

if 'history' not in st.session_state:
    st.session_state.history = []

# --- ACTUAL DATA RANGES (From master_dataset.csv) ---
fuel_options = {
    "ethyl_valerate": {"t": (120, 610), "phi": (0.7, 1.4), "p": (1, 1), "blend": False},
    "propane_air": {"t": (300, 650), "phi": (0.7, 1.3), "p": (1, 5), "blend": False},
    "n_decane_air": {"t": (335, 650), "phi": (0.7, 1.5), "p": (1, 1), "blend": False},
    "nh3_h2_air": {"t": (298, 726), "phi": (0.7, 1.4), "p": (1, 1), "blend": True},
    "c1_c4_alkane_air": {"t": (300, 600), "phi": (0.6, 0.8), "p": (1, 1), "blend": False},
    "ethyl_acetate_air": {"t": (358, 600), "phi": (0.6, 1.5), "p": (1, 1), "blend": False},
    "ch4_h2_air": {"t": (206, 662), "phi": (0.7, 1.2), "p": (1, 1), "blend": True},
    "iso_octane_air": {"t": (300, 640), "phi": (0.7, 1.4), "p": (1, 1), "blend": False},
    "toluene": {"t": (300, 611), "phi": (0.3, 3.0), "p": (1, 1), "blend": False},
    "n-heptane": {"t": (358, 606), "phi": (0.6, 1.5), "p": (1, 1), "blend": False},
    "syngas_air": {"t": (300, 650), "phi": (0.4, 2.1), "p": (1, 5), "blend": False},
    "n-butanol_air": {"t": (343, 600), "phi": (0.7, 1.3), "p": (1, 1), "blend": False},
    "n-pentanol_air": {"t": (335, 555), "phi": (0.7, 1.3), "p": (1, 1), "blend": False},
    "diluted_syngas": {"t": (300, 645), "phi": (0.7, 1.3), "p": (1, 1), "blend": True},
    "methane_air": {"t": (300, 606), "phi": (0.6, 1.4), "p": (1, 5), "blend": False},
    "DME_air": {"t": (381, 547), "phi": (1.0, 1.0), "p": (1, 1), "blend": True},
    "methanol_air": {"t": (300, 609), "phi": (0.7, 1.3), "p": (1, 1), "blend": False},
    "LPG_air": {"t": (300, 600), "phi": (0.7, 1.7), "p": (1, 1), "blend": False}
}

st.title("🧪 LBV Predictor: Research Dashboard")
col_main, col_hist = st.columns([2.5, 1])

with col_main:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    fuel = st.selectbox("HYDROCARBON SELECTION", list(fuel_options.keys()))
    data = fuel_options[fuel]
    
    if fuel in ["methane_air", "ch4_h2_air"]:
        st.warning("⚠️ High experimental variance detected for this fuel.")

    frac_a, frac_b = 1.0, 0.0
    if data["blend"]:
        c1, c2 = st.columns(2)
        with c1:
            frac_a = st.select_slider("FRACTION A", options=[round(x*0.01, 2) for x in range(101)], value=0.5)
        with c2:
            frac_b = st.select_slider("FRACTION B", options=[round(x*0.01, 2) for x in range(101)], value=0.5)

    st.markdown(f'<p class="range-label">Limit: {data["p"][0]} - {data["p"][1]} bar</p>', unsafe_allow_html=True)
    pres = st.select_slider("PRESSURE (bar)", options=list(range(data["p"][0], data["p"][1] + 1)))

    st.markdown(f'<p class="range-label">Limit: {data["t"][0]} - {data["t"][1]} K</p>', unsafe_allow_html=True)
    temp = st.select_slider("INITIAL TEMPERATURE (K)", options=list(range(int(data["t"][0]), int(data["t"][1]) + 1)))

    st.markdown(f'<p class="range-label">Limit: {data["phi"][0]} - {data["phi"][1]}</p>', unsafe_allow_html=True)
    phi_opts = [round(x*0.01, 2) for x in range(int(data["phi"][0]*100), int(data["phi"][1]*100) + 1)]
    phi = st.select_slider("EQUIVALENCE RATIO (φ)", options=phi_opts, value=phi_opts[len(phi_opts)//2])

    st.write("---")
    u_col, b_col = st.columns([1, 2])
    with u_col:
        m_s_toggle = st.toggle("Show in m/s")
    
    if st.button("PREDICT LBV"):
        # MODEL PREDICTION LOGIC
        try:
            fuel_encoded = le.transform([fuel])[0]
            input_row = pd.DataFrame([[fuel_encoded, frac_a, frac_b, phi, temp, pres]], 
                                    columns=['fuel_id_encoded', 'frac_A', 'frac_B', 'phi', 'temperature_K', 'pressure_bar'])
            res_cm = model.predict(input_row)[0]
            final_val = res_cm / 100 if m_s_toggle else res_cm
            unit = "m/s" if m_s_toggle else "cm/s"
            
            st.success("Analysis Complete")
            st.metric("Laminar Burning Velocity", f"{final_val:.4f} {unit}")
            st.session_state.history.insert(0, {"f": fuel, "phi": phi, "res": f"{final_val:.2f} {unit}"})
        except Exception as e:
            st.error(f"Prediction Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

with col_hist:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.subheader("📜 History")
    for entry in st.session_state.history[:5]:
        st.markdown(f"**{entry['f']}** (φ={entry['phi']}) → `{entry['res']}`")
        st.write("---")
    st.markdown('</div>', unsafe_allow_html=True)
        
