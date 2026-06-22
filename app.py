import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF

# 1. UI Setup
st.set_page_config(page_title="VectorAtmos VCU Engine", layout="wide")
st.title("VectorAtmos dMRV: VCU & Revenue Engine")
st.markdown("Interactive demonstration of the Verra VM0047 pipeline converting satellite telemetry into Verified Carbon Units (VCUs). **Hover over the (?) icon next to any metric to see the exact calculation.**")
st.divider()

# 2. Interactive Parameters (Sidebar with Context)
st.sidebar.header("Input Telemetry Parameters")
st.sidebar.info("These physical metrics are typically derived from Google Earth Engine (Sentinel-1 SAR & GEDI LiDAR).")
project_area = st.sidebar.slider("Project Area (Hectares)", 1000, 34400, 10320, 
                                 help="The exact legal boundary secured in the government Memorandum of Agreement (MoA).")
canopy_height = st.sidebar.slider("Avg Predicted Canopy Height (meters)", 5.0, 35.0, 15.0, 
                                  help="Continuous canopy height predicted by the AI regressor across the target grid.")

st.sidebar.header("Compliance Deductions")
st.sidebar.info("These deductions isolate the true 'additionality' of the project to satisfy Verra methodology.")
baseline_emissions = st.sidebar.slider("Dynamic Baseline (tCO2e/ha)", 0.0, 5.0, 1.0, 
                                       help="Carbon changes measured in a natural 'donor pool' to represent what would have happened without the project.")
leakage = st.sidebar.slider("Leakage Deductions (tCO2e/ha)", 0.0, 5.0, 0.5, 
                            help="Deductions for deforestation that the project simply displaced to the 5km buffer zone.")

st.sidebar.header("Market Variables")
market_price = st.sidebar.slider("Market Price ($/VCU)", 10.0, 50.0, 22.0, 
                                 help="The estimated sale price per ton on the Voluntary Carbon Market (VCM).")

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

col1.metric("1. Aboveground Biomass", f"{agb:.2f} Mg/ha", help="AGB = 0.0512 * (Canopy Height ^ 1.892)")
col2.metric("2. Total Dry Biomass", f"{total_biomass:.2f} Mg/ha", help="Incorporates 0.24 tropical root-to-shoot ratio.")
col3.metric("3. Carbon Stock", f"{carbon_stock:.2f} Mg C/ha", help="Total Dry Biomass * 47% Carbon Fraction.")
col4.metric("4. Gross Sequestration", f"{gross_seq:.2f} tCO2e/ha", help="Carbon Stock * molecular weight ratio of CO2 (44/12).")

st.markdown("---")

st.subheader("Stage 2: Compliance Protocol (Net Carbon Equation)")

# --- PLOTLY WATERFALL CHART INTEGRATION ---
fig = go.Figure(go.Waterfall(
    name = "Additionality Pipeline", orientation = "v",
    measure = ["relative", "relative", "relative", "total"],
    x = ["Gross Sequestration", "Baseline Deductions", "Leakage Deductions", "Net Additionality"],
    textposition = "outside",
    text = [f"{gross_seq:.2f}", f"-{baseline_emissions:.2f}", f"-{leakage:.2f}", f"{net_seq_per_ha:.2f}"],
    y = [gross_seq, -baseline_emissions, -leakage, net_seq_per_ha],
    connector = {"line":{"color":"rgb(63, 63, 63)"}},
    decreasing = {"marker":{"color":"#FF5733"}},
    increasing = {"marker":{"color":"#28B463"}},
    totals = {"marker":{"color":"#2E86C1"}}
))
fig.update_layout(title="Per Hectare Carbon Yield Pipeline (tCO2e/ha)", showlegend=False, height=400)
st.plotly_chart(fig, use_container_width=True)
# ------------------------------------------

st.markdown("---")

st.subheader("Stage 3: Total Asset & Revenue Yield")
col5, col6 = st.columns(2)
col5.metric("Total Mintable VCUs", f"{total_vcus:,.0f}", help="Net Additionality per hectare * Total Project Area.")
col6.metric("Total Gross Revenue", f"${gross_revenue:,.2f}", help="Total Mintable VCUs * Voluntary Carbon Market Price.")

st.markdown("---")

# 5. PDF Generation Feature
st.subheader("Export Project Prospectus")
st.write("Generate a formal summary of the current calculations for your records.")

def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "VectorAtmos: VCU Calculation Prospectus", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "1. Input Parameters", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Project Area: {project_area:,.0f} Hectares", ln=True)
    pdf.cell(0, 10, f"Avg Predicted Canopy Height: {canopy_height:.1f} meters", ln=True)
    pdf.cell(0, 10, f"Dynamic Baseline Deductions: {baseline_emissions:.2f} tCO2e/ha", ln=True)
    pdf.cell(0, 10, f"Leakage Deductions: {leakage:.2f} tCO2e/ha", ln=True)
    pdf.cell(0, 10, f"Market Price Assessment: ${market_price:.2f} / VCU", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "2. Per Hectare Yield Metrics", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Gross Sequestration: {gross_seq:.2f} tCO2e/ha", ln=True)
    pdf.cell(0, 10, f"Net Additionality: {net_seq_per_ha:.2f} tCO2e/ha", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. Final Commercial Output", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Total Mintable VCUs: {total_vcus:,.0f} VCUs", ln=True)
    pdf.cell(0, 10, f"Total Gross Revenue: ${gross_revenue:,.2f}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# Download Button
pdf_bytes = create_pdf()
st.download_button(
    label="📄 Download PDF Summary",
    data=pdf_bytes,
    file_name="VectorAtmos_VCU_Summary.pdf",
    mime="application/pdf"
)
