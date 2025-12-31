🧪 LBV Predictor V2: Multi-Fidelity Research Dashboard
A state-of-the-art machine learning platform for predicting the Laminar Burning Velocity (LBV) of 18+ different fuel families. This project integrates sparse, high-fidelity experimental data with dense, low-fidelity chemical kinetic simulations.

📌 Project Architecture
This project is built as a bridge between Chemical Engineering and Data Science. The system is connected as follows:

Data Layer: Sourced from 2,185 experimental points and ~8,000 simulation points.

Training Layer: A Python-based XGBoost pipeline using Fidelity Weighting (10:1 ratio) to prioritize real-world experimental "truth."

Storage Layer: The model is stored as a 35MB .pkl bundle, managed via Git LFS (Large File Storage) to bypass GitHub's upload limits.

Deployment Layer: A Streamlit frontend hosted on the cloud, providing real-time inference in under 100ms.

🛠️ Key Technical Features
1. Multi-Fidelity Learning
Instead of treating all data equally, we implemented a Weighted Loss Function.

Experimental Data: Weighted at 10.0 (The "Anchor").

Simulation Data: Weighted at 1.0 (The "Trend-setter"). This ensures the model learns the smooth trends from simulations but always "anchors" its predictions to experimental values.

2. Intelligent Metadata Validation
The website doesn't just "guess"; it validates.

Source Attribution: The UI dynamically displays whether a fuel prediction is based on Experiments, Simulations, or both.

Blend Enforcement: If a user selects a fuel blend (e.g., 85% Methane / 15% Hydrogen) that wasn't in the training set, the app triggers a custom validation error preventing unphysical results.

3. Adaptive Thermodynamic Sliders
To prevent the common "RangeError" in web apps, we implemented Dynamic Slider Keys. Whenever a fuel is changed, the sliders for Temperature, Pressure, and Phi reset to the specific training limits of that fuel.

📂 File Structure
app.py: The Streamlit frontend and backend logic.

lbv_main_v2.pkl: The 35MB model bundle (XGBoost model + LabelEncoder + Metadata).

master_dataset2.csv: The raw dataset (10,301 rows).

requirements.txt: Environment configuration for cloud deployment.

.gitattributes: Configuration for Git LFS to track the large model file.

🚀 How it Works (The Flow)
User Input: The user selects a fuel. The app reads the metadata dictionary inside the .pkl to find the valid ranges.

Validation: The system checks if the selected Blend Ratio exists.

Inference: The XGBoost model processes the 6-feature vector: [Fuel_ID, Frac_A, Frac_B, Phi, Temp, Pres].

Output: The result is displayed in cm/s or m/s with a success message indicating the data source reliability.

📊 Performance Summary
R² (Liquid Hydrocarbons): > 0.99 (Excellent)

R² (Gaseous Blends): ~0.73 (Reflecting high experimental variance)

MAE: < 5 cm/s (Aggregated average)

📜 Research Disclaimer
This tool is intended for research and educational purposes. While the model is highly accurate, predictions near the flammability limits should be verified with detailed chemical kinetic solvers or experimental setups.

Watermark: PROJECT_LBV_2025_V2_SECURE
