import matplotlib.pyplot as plt
import streamlit as st
import joblib
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Smart Green Home Energy Agent",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR STYLING ---
st.markdown("""
    <style>
    /* Main Background */
    .main {
        background-color: #f8f9fa;
    }
    /* Title Styling */
    h1 {
        color: #2E7D32;
        font-family: 'Helvetica Neue', sans-serif;
    }
    h2, h3 {
        color: #1B5E20;
    }
    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        text-align: center;
    }
    /* Button Styling */
    div.stButton > button {
        width: 100%;
        background-color: #2E7D32;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #1B5E20;
        color: white;
    }
    /* Success/Info Box Styling */
    .stSuccess, .stInfo {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Load trained model
# Note: Ensure the .pkl file is in the same directory
try:
    model = joblib.load("energy_model.pkl")
    scaler = joblib.load("scaler.pkl")
except FileNotFoundError:
    st.error("🚨 Model file 'energy_model.pkl' not found. Please ensure it is in the directory.")
    st.stop()

# --- HEADER SECTION ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100) # Placeholder generic green home icon
with col_title:
    st.title("Smart Green Home Energy Agent")
    st.markdown("### 🌿 AI-Powered Sustainable Building Analysis")

st.markdown("---")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("🏠 Building Parameters")
    st.info("Adjust the building's physical attributes below.")

    with st.expander("📐 Dimensions & Shape", expanded=True):
        relative_compactness = st.slider("Relative Compactness", 0.5, 1.0, 0.8)
        surface_area = st.slider("Surface Area (m²)", 500, 1000, 700)
        overall_height = st.slider("Overall Height (m)", 2.5, 5.0, 3.5)

    with st.expander("🧱 Envelope Properties", expanded=True):
        wall_area = st.slider("Wall Area (m²)", 200, 500, 300)
        roof_area = st.slider("Roof Area (m²)", 100, 300, 200)

    with st.expander("☀️ Orientation & Glazing", expanded=True):
        orientation = st.slider("Orientation (2-5)", 2, 5, 3)
        glazing_area = st.slider("Glazing Area Ratio", 0.0, 0.4, 0.2)
        glazing_dist = st.slider("Glazing Distribution", 0, 5, 2)
    
    st.header("⚙️ Smart Controls")
    thermostat_reduction = st.slider("Reduce Thermostat (°C)", 0, 3, 1)
    
    st.markdown("---")
    analyze_btn = st.button("🔍 Analyze Building Performance")

# --- MAIN DASHBOARD LOGIC ---

if analyze_btn:
    # Prepare Input
    input_data = np.array([[relative_compactness,
                            surface_area,
                            wall_area,
                            roof_area,
                            overall_height,
                            orientation,
                            glazing_area,
                            glazing_dist]])

    # Prediction
    input_scaled = scaler.transform(input_data)
    prediction = model.predict(input_scaled)
    heating = prediction[0][0]
    cooling = prediction[0][1]
    total_energy = heating + cooling

    # Calculations
    emission_factor = 0.82
    price_per_unit = 6
    carbon = total_energy * emission_factor
    cost = total_energy * price_per_unit

    # --- RESULTS SECTION ---
    
    st.subheader("📊 Energy Analysis Report")
    
    # Row 1: Load Breakdown
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔥 Heating Load", f"{round(heating, 2)} kWh")
    with col2:
        st.metric("❄️ Cooling Load", f"{round(cooling, 2)} kWh")
    with col3:
        st.metric("⚡ Total Consumption", f"{round(total_energy, 2)} kWh", delta_color="inverse")

    # Row 2: Impact
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("🌫 Carbon Footprint", f"{round(carbon, 2)} kg CO₂")
    with col5:
        st.metric("💰 Estimated Cost", f"₹ {round(cost, 2)}")
    with col6:
         # Energy Rating Logic
        if total_energy < 30:
            rating = "A+ (Excellent)"
            rating_color = "green"
        elif total_energy < 50:
            rating = "B (Good)"
            rating_color = "orange"
        else:
            rating = "C (High Usage)"
            rating_color = "red"
        st.metric("🏷 Energy Rating", rating)

    st.divider()

    # --- OPTIMIZATION SECTION ---
    st.subheader("🚀 Smart Optimization Results")
    
    # Optimization Logic
    heating_opt = heating * (1 - 0.05 * thermostat_reduction)
    cooling_opt = cooling * (1 - 0.04 * thermostat_reduction)
    total_energy_opt = heating_opt + cooling_opt
    
    carbon_opt = total_energy_opt * emission_factor
    cost_opt = total_energy_opt * price_per_unit

    energy_saved = total_energy - total_energy_opt
    carbon_saved = carbon - carbon_opt
    cost_saved = cost - cost_opt

    # Optimization Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("⚡ Optimized Energy", f"{round(total_energy_opt, 2)} kWh", delta=f"-{round(energy_saved, 2)} kWh")
    c2.metric("💰 Cost Savings", f"₹ {round(cost_saved, 2)}", delta=f"Saved")
    c3.metric("🌿 Carbon Reduction", f"{round(carbon_saved, 2)} kg", delta="Less CO₂")

    st.divider()

    # --- VISUALIZATION & SCORE ---
    
    col_graph, col_score = st.columns([1.5, 1])

    with col_graph:
        st.subheader("📈 Impact Visualization")
        
        # Styled Matplotlib Graph
        fig, ax = plt.subplots(figsize=(6, 4))
        labels = ["Current", "Optimized"]
        values = [total_energy, total_energy_opt]
        colors = ['#EF5350', '#66BB6A'] # Red for high, Green for optimized

        bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor='black', alpha=0.8)
        
        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom', fontweight='bold')

        ax.set_ylabel("Energy (kWh)", fontweight='bold')
        ax.set_title("Consumption Comparison", fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        
        st.pyplot(fig)

    with col_score:
        st.subheader("🏆 Sustainability Score")
        
        sustainability_score = max(0, 100 - total_energy)
        
        if sustainability_score > 80:
            level = "Excellent 🌿"
            bar_color = "green"
        elif sustainability_score > 60:
            level = "Good ✅"
            bar_color = "blue"
        elif sustainability_score > 40:
            level = "Average ⚖"
            bar_color = "orange"
        else:
            level = "Needs Improvement ⚠"
            bar_color = "red"

        # Circular progress simulation or simple progress bar
        st.markdown(f"<h1 style='text-align: center; color: {bar_color}; font-size: 48px;'>{round(sustainability_score, 1)}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>{level}</p>", unsafe_allow_html=True)
        st.progress(int(min(sustainability_score, 100)))

        # Tree Equivalent
        trees_equivalent = carbon_saved / 21
        st.info(f"🌳 **Eco Impact:** Your optimizations are equivalent to planting **{round(trees_equivalent, 2)} trees** per year!")

    # --- REPORT & SUGGESTIONS ---
    st.divider()
    
    with st.container():
        st.subheader("🧠 AI Energy Advisor Report")
        
        # Determine background color for report based on score
        report_bg = "#e8f5e9" if sustainability_score > 60 else "#fff3e0"
        
        report_html = f"""
        <div style="background-color: {report_bg}; padding: 20px; border-radius: 10px; border-left: 5px solid #2E7D32;">
            <p><strong>Building Analysis:</strong> This building currently consumes <b>{round(total_energy,2)} kWh</b>.</p>
            <p><strong>Optimization Strategy:</strong> Reducing the thermostat by <b>{thermostat_reduction}°C</b> results in savings of:</p>
            <ul>
                <li>⚡ <b>{round(energy_saved,2)} kWh</b> of electricity</li>
                <li>💰 <b>₹{round(cost_saved,2)}</b> in costs</li>
                <li>🌍 <b>{round(carbon_saved,2)} kg</b> of CO₂</li>
            </ul>
        </div>
        """
        st.markdown(report_html, unsafe_allow_html=True)

    st.subheader("💡 Smart Recommendations")
    
    rec_cols = st.columns(2)
    
    count = 0
    with rec_cols[0]:
        if glazing_area > 0.3:
            st.warning("⚠️ **Windows:** High glazing area detected. Install double-glazed windows or smart shading.")
            count += 1
        if relative_compactness < 0.7:
            st.warning("⚠️ **Shape:** Low compactness. Consider improving building shape efficiency.")
            count += 1
            
    with rec_cols[1]:
        if surface_area > 850:
            st.warning("⚠️ **Insulation:** Large surface area. High-performance insulation is recommended.")
            count += 1
        if thermostat_reduction > 0:
            st.success(f"✅ **Thermostat:** Great job! Reducing by {thermostat_reduction}°C is the easiest way to save.")
            count += 1
            
    if count == 0 and thermostat_reduction == 0:
        st.info("System is running at baseline. Try adjusting the Thermostat to see savings.")
