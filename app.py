import streamlit as st
import pandas as pd
import pickle
import xgboost as xgb
import os

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
    .stButton>button { background-color: var(--accent-color); color: #000000; font-weight: bold; width: 100%; height: 50px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD THE V2 BUNDLE ---
@st.cache_resource
def load_v2():
    # This automatically handles the large LFS file on Streamlit Cloud
    if not os.path.exists("lbv_main_v2.pkl"):
        st.error("Model file 'lbv_main_v2.pkl' not found. Ensure it is uploaded via Git LFS.")
        st.stop()
    with open("lbv_main_v2.pkl", "rb") as f:
        return pickle.load(f)

bundle = load_v2()
model = bundle["model"]
le = bundle["le"]
metadata = bundle["metadata"]
watermark = bundle.get("watermark", "LBV-V2-BETA")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- APP LAYOUT ---
st.title("🧪 LBV Predictor: Research Dashboard V2")
st.caption(f"Model Signature: {watermark}")

col_main, col_hist = st.columns([2.5, 1])

with col_main:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    
    # 1. FUEL SELECTION
    fuel_list = sorted(list(metadata.keys()))
    selected_fuel = st.selectbox("HYDROCARBON SELECTION", fuel_list)
    fuel_info = metadata[selected_fuel]
    
    # Show Source Badge
    st.info(f"📊 **Data Source:** {fuel_info['source_info']}")
    
    if selected_fuel in ["methane_air", "ch4_h2_air", "Methane"]:
        st.warning("⚠️ Note: High experimental variance recorded for this fuel family.")

    # 2. BLEND FRACTIONS
    # We use keys like f"fa_{selected_fuel}" to force slider reset on fuel change
    frac_a, frac_b = 1.0, 0.0
    # Check if the fuel ever has blends in metadata
    has_blends = any(pair[1] > 0 for pair in fuel_info["valid_blends"])
    
    if has_blends:
        c1, c2 = st.columns(2)
        with c1:
            frac_a = st.select_slider("FRACTION A", options=[round(x*0.01, 2) for x in range(101)], value=1.0, key=f"fa_{selected_fuel}")
        with c2:
            frac_b = st.select_slider("FRACTION B", options=[round(x*0.01, 2) for x in range(101)], value=0.0, key=f"fb_{selected_fuel}")
    else:
        st.info(f"Fixed composition for {selected_fuel} (Pure Fuel).")

    # 3. THERMODYNAMIC SLIDERS (Using Metadata Ranges)
    st.markdown(f'<p class="range-label">Training Limit: {fuel_info["pres_range"][0]} - {fuel_info["pres_range"][1]} bar</p>', unsafe_allow_html=True)
    p_opts = list(range(int(fuel_info["pres_range"][0]), int(fuel_info["pres_range"][1]) + 1))
    pres = st.select_slider("PRESSURE (bar)", options=p_opts, key=f"p_{selected_fuel}")

    st.markdown(f'<p class="range-label">Training Limit: {fuel_info["temp_range"][0]} - {fuel_info["temp_range"][1]} K</p>', unsafe_allow_html=True)
    t_opts = list(range(int(fuel_info["temp_range"][0]), int(fuel_info["temp_range"][1]) + 1))
    temp = st.select_slider("INITIAL TEMPERATURE (K)", options=t_opts, key=f"t_{selected_fuel}")

    st.markdown(f'<p class="range-label">Training Limit: {fuel_info["phi_range"][0]} - {fuel_info["phi_range"][1]}</p>', unsafe_allow_html=True)
    phi_min, phi_max = fuel_info["phi_range"]
    phi_opts = [round(x*0.01, 2) for x in range(int(phi_min*100), int(phi_max*100) + 1)]
    phi = st.select_slider("EQUIVALENCE RATIO (φ)", options=phi_opts, value=phi_opts[len(phi_opts)//2], key=f"phi_{selected_fuel}")

    st.write("---")
    m_s_toggle = st.toggle("Show in m/s")
    
    # 4. PREDICTION LOGIC
    if st.button("🚀 PREDICT LBV"):
        current_blend = (frac_a, frac_b)
        
        # VALIDATION: Blend Ratio Check
        if current_blend not in fuel_info["valid_blends"]:
            st.error(f"❌ The blend ratio {frac_a}:{frac_b} is not supported for {selected_fuel} in this dataset.")
            st.markdown("**Available Ratios for this fuel:**")
            st.write(fuel_info["valid_blends"])
        else:
            try:
                fuel_encoded = le.transform([selected_fuel])[0]
                input_row = pd.DataFrame([[fuel_encoded, frac_a, frac_b, phi, temp, pres]], 
                                        columns=['fuel_id_encoded', 'frac_A', 'frac_B', 'phi', 'temperature_K', 'pressure_bar'])
                
                res_cm = model.predict(input_row)[0]
                final_val = res_cm / 100 if m_s_toggle else res_cm
                unit = "m/s" if m_s_toggle else "cm/s"
                
                st.success(f"Analysis Complete using {fuel_info['source_info']} logic.")
                st.metric("Laminar Burning Velocity", f"{final_val:.4f} {unit}")
                
                # Update History
                st.session_state.history.insert(0, {"f": selected_fuel, "phi": phi, "res": f"{final_val:.2f} {unit}"})
            except Exception as e:
                st.error(f"Prediction Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

with col_hist:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.subheader("📜 History")
    if not st.session_state.history:
        st.write("No predictions yet.")
    for entry in st.session_state.history[:5]:
        st.markdown(f"**{entry['f']}** (φ={entry['phi']}) → `{entry['res']}`")
        st.write("---")
    st.markdown('</div>', unsafe_allow_html=True)
