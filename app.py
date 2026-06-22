import streamlit as st

# 1. UI Setup
st.set_page_config(page_title="VectorAtmos VCU Engine", layout="wide")
st.title("VectorAtmos dMRV: VCU & Revenue Engine")
st.markdown("Interactive demonstration of the Verra VM0047 pipeline converting satellite telemetry into Verified Carbon Units (VCUs). **Hover over the (?) icon next to any metric to see the exact calculation.**")
st.divider()

# 2. Interactive Parameters (Sidebar)
st.sidebar.header("Input Telemetry Parameters")
project_area = st.sidebar.slider("Project Area (Hectares)", 1000, 34400, 10320)
canopy_height = st.sidebar.slider("Avg Predicted Canopy Height (meters)", 5.0, 35.0, 15.0)

st.sidebar.header("Compliance Deductions")
baseline_emissions = st.sidebar.slider("Dynamic Baseline (tCO2e/ha)", 0.0, 5.0, 1.0)
leakage = st.sidebar.slider("Leakage Deductions (tCO2e/ha)", 0.0, 5.0, 0.5)

st.sidebar.header("Market Variables")
market_price = st.sidebar.slider("Market Price ($/VCU)", 10.0, 50.0, 22.0)

# 3. The Allometric Math Pipeline
agb = 0.0512 * (canopy_height ** 1.892)
total_biomass = agb * 1.24
carbon_stock = total_biomass * 0.47
gross_seq = carbon_stock * 3.6667
net_seq_per_ha = gross_seq - baseline_emissions - leakage
total_vcus = net_seq_per_ha * project_area
gross_revenue = total_vcus * market_price

# 4. Step-by-Step Interface Display
st.subheader("Stage 1: Allometric Biomass Conversion (Per Hectare)")
col1, col2, col3, col4 = st.columns(4)

col1.metric("1. Aboveground Biomass", f"{agb:.2f} Mg/ha", 
            help="AGB = 0.0512 * (Canopy Height ^ 1.892). Uses regional Caribbean forestry coefficients.")

col2.metric("2. Total Dry Biomass", f"{total_biomass:.2f} Mg/ha", 
            help="Total Dry Biomass = AGB * 1.24. Incorporates underground root systems using the standard 0.24 tropical root-to-shoot ratio.")

col3.metric("3. Carbon Stock", f"{carbon_stock:.2f} Mg C/ha", 
            help="Carbon Stock = Total Dry Biomass * 0.47. Converts dry organic wood mass into pure atomic carbon weight.")

col4.metric("4. Gross Sequestration", f"{gross_seq:.2f} tCO2e/ha", 
            help="Gross Sequestration = Carbon Stock * 3.6667. Scales the carbon weight by the molecular weight ratio of CO2 (44/12) to determine atmospheric greenhouse gas volume.")

st.markdown("---")

st.subheader("Stage 2: Compliance Protocol (Net Carbon Equation)")
col5, col6, col7 = st.columns(3)

col5.metric("Gross Sequestration", f"{gross_seq:.2f} tCO2e/ha", 
            help="The total atmospheric CO2 captured before baseline and leakage deductions.")

col6.metric("Compliance Deductions", f"- {(baseline_emissions + leakage):.2f} tCO2e/ha", 
            help="Sum of Baseline Emissions (what would have decayed normally) and Leakage (deforestation shifted outside the project boundary).")

col7.metric("Net Additionality", f"{net_seq_per_ha:.2f} tCO2e/ha", 
            help="Net Additionality = Gross Sequestration - Baseline - Leakage. This is the true, auditable per-hectare impact.")

st.markdown("---")

st.subheader("Stage 3: Total Asset & Revenue Yield")
st.info("Based on the input telemetry and strict Verra VM0047 deductions, these are the project-wide commercial outputs.")

col8, col9 = st.columns(2)
col8.metric("Total Mintable VCUs", f"{total_vcus:,.0f}", 
            help="Total VCUs = Net Additionality per hectare * Total Project Area. One VCU equals one metric ton of CO2e.")

col9.metric("Total Gross Revenue", f"${gross_revenue:,.2f}", 
            help="Gross Revenue = Total Mintable VCUs * Voluntary Carbon Market Price. (Displayed prior to registry issuance levies).")