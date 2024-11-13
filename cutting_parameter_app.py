import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import json

# Material and Tooling Data (Updated with Real-World Values)
materials = {
    "Aluminum 6061": {"cutting_speed": 300, "machinability": 250, "tensile_strength": 310, "hardness": 95},
    "Steel 1045": {"cutting_speed": 90, "machinability": 140, "tensile_strength": 585, "hardness": 170},
    "Titanium Grade 5 (Ti-6Al-4V)": {"cutting_speed": 50, "machinability": 26, "tensile_strength": 950, "hardness": 349},
    "Stainless Steel 304": {"cutting_speed": 70, "machinability": 45, "tensile_strength": 505, "hardness": 201},
    "Cast Iron": {"cutting_speed": 120, "machinability": 180, "tensile_strength": 220, "hardness": 180}
}

tool_materials = {
    "HSS": 1.0,
    "Carbide": 2.5,
    "Ceramic": 5.0,
    "CBN": 7.0,
    "Diamond": 10.0
}

# Calculation Functions

def calculate_rpm(cutting_speed, tool_diameter):
    return (cutting_speed * 1000) / (3.14 * tool_diameter)

def calculate_feed_rate(feed_per_tooth, number_of_teeth, rpm):
    return feed_per_tooth * number_of_teeth * rpm

def calculate_tool_life(cutting_speed, n, c):
    return (c / (cutting_speed ** n)) * 60  # Convert hours to minutes

def calculate_cutting_force(tensile_strength, depth_of_cut, width_of_cut):
    return tensile_strength * depth_of_cut * width_of_cut

def calculate_torque(cutting_force, tool_diameter):
    return (cutting_force * tool_diameter) / 2000

def calculate_heat_generation(cutting_speed, feed_rate, cutting_force):
    return 0.8 * cutting_speed * feed_rate * cutting_force

def calculate_tool_wear(cutting_speed, feed_rate, time):
    return 0.0005 * cutting_speed * feed_rate * time  # Improved model for tool wear over time

# Streamlit UI
st.title("Cutting Parameter Calculator")

# Tabs for Basic and Advanced Modes
tab1, tab2 = st.tabs(["Basic", "Advanced"])

# Unit Selection
units = st.radio("Select Units", ["Metric", "Imperial"])
unit_conversion_factor = 1.0
if units == "Imperial":
    unit_conversion_factor = 25.4
    cutting_speed_conversion_factor = 3.281  # Convert m/min to ft/min
else:
    cutting_speed_conversion_factor = 1.0

with tab1:
    st.header("Basic Cutting Parameter Calculator")
    
    # User Inputs
    operation = st.selectbox("Select Operation", ["Milling", "Turning", "Drilling", "Tapping"], key="basic_operation")
    selected_material = st.selectbox("Select Material", list(materials.keys()))
    selected_tool_material = st.selectbox("Select Tool Material", list(tool_materials.keys()))
    cutter_diameter = st.number_input("Enter Cutter Diameter ({'mm' if units == 'Metric' else 'in'})", min_value=1.0, value=10.0) * unit_conversion_factor
    feed_per_tooth = st.number_input("Enter Feed per Tooth ({'mm' if units == 'Metric' else 'in'})", min_value=0.01, value=0.1) * unit_conversion_factor
    number_of_teeth = st.number_input("Enter Number of Teeth on Cutter", min_value=1, value=4)

    # Calculations
    cutting_speed = materials[selected_material]["cutting_speed"] * tool_materials[selected_tool_material] * cutting_speed_conversion_factor
    rpm = calculate_rpm(cutting_speed, cutter_diameter)
    feed_rate = calculate_feed_rate(feed_per_tooth, number_of_teeth, rpm)

    # Display Results
    st.subheader("Calculated Parameters")
    st.write(f"**Operation:** {operation}")
    st.write(f"**Spindle Speed (RPM):** {rpm:.2f}")
    st.write(f"**Feed Rate ({'mm/min' if units == 'Metric' else 'in/min'}):** {feed_rate:.2f}")

with tab2:
    st.header("Advanced Cutting Parameter Calculator")

    # User Inputs
    operation = st.selectbox("Select Operation", ["Milling", "Turning", "Drilling", "Tapping"], key="adv_operation")
    selected_material = st.selectbox("Select Material", list(materials.keys()), key="adv_material")
    selected_tool_material = st.selectbox("Select Tool Material", list(tool_materials.keys()), key="adv_tool_material")
    cutter_diameter = st.number_input("Enter Cutter Diameter ({'mm' if units == 'Metric' else 'in'})", min_value=1.0, value=10.0, key="adv_cutter_diameter") * unit_conversion_factor
    number_of_teeth = st.number_input("Enter Number of Teeth on Cutter", min_value=1, value=4, key="adv_number_of_teeth")
    depth_of_cut = st.number_input("Enter Depth of Cut ({'mm' if units == 'Metric' else 'in'})", min_value=0.1, value=2.0, key="adv_depth_of_cut") * unit_conversion_factor
    width_of_cut = st.number_input("Enter Width of Cut ({'mm' if units == 'Metric' else 'in'})", min_value=0.1, value=5.0, key="adv_width_of_cut") * unit_conversion_factor
    feed_per_tooth = st.number_input("Enter Feed per Tooth ({'mm' if units == 'Metric' else 'in'})", min_value=0.01, value=0.1, key="adv_feed_per_tooth") * unit_conversion_factor
    tool_life_n = st.number_input("Enter Tool Life Exponent (n)", min_value=0.1, value=0.25, key="adv_tool_life_n")
    tool_life_c = st.number_input("Enter Tool Life Constant (C)", min_value=1.0, value=300.0, key="adv_tool_life_c")

    # Calculations
    cutting_speed = materials[selected_material]["cutting_speed"] * tool_materials[selected_tool_material] * cutting_speed_conversion_factor
    rpm = calculate_rpm(cutting_speed, cutter_diameter)
    feed_rate = calculate_feed_rate(feed_per_tooth, number_of_teeth, rpm)
    tool_life = calculate_tool_life(cutting_speed, tool_life_n, tool_life_c)

    # Advanced Calculations
    cutting_force = calculate_cutting_force(materials[selected_material]["tensile_strength"], depth_of_cut, width_of_cut)
    torque = calculate_torque(cutting_force, cutter_diameter)
    heat_generation = calculate_heat_generation(cutting_speed, feed_rate, cutting_force)

    # Display Results
    st.subheader("Calculated Parameters")
    st.write(f"**Operation:** {operation}")
    st.write(f"**Spindle Speed (RPM):** {rpm:.2f}")
    st.write(f"**Feed Rate ({'mm/min' if units == 'Metric' else 'in/min'}):** {feed_rate:.2f}")
    st.write(f"**Estimated Tool Life (minutes):** {tool_life:.2f}")

    st.subheader("Advanced Calculations")
    st.write(f"**Cutting Force (N):** {cutting_force:.2f}")
    st.write(f"**Torque (Nm):** {torque:.2f}")
    st.write(f"**Heat Generation (J/s):** {heat_generation:.2f}")

    # Graph: Tool Life vs Cutting Speed
    st.subheader("Tool Life vs Cutting Speed")
    cutting_speeds = [cutting_speed * i for i in range(1, 6)]
    tool_lives = [calculate_tool_life(cs, tool_life_n, tool_life_c) for cs in cutting_speeds]

    plt.figure(figsize=(10, 5))
    plt.plot(cutting_speeds, tool_lives, marker='o')
    plt.xlabel("Cutting Speed (m/min)")
    plt.ylabel("Tool Life (minutes)")
    plt.title("Tool Life vs Cutting Speed")
    st.pyplot(plt)
    plt.close()

    # Recommendations for Cooling/Lubrication
    st.subheader("Recommendations for Cooling/Lubrication")
    if cutting_speed > 200:
        st.write("**Recommendation:** Use flood coolant to prevent excessive heat and prolong tool life.")
    elif cutting_speed > 100:
        st.write("**Recommendation:** Use mist cooling to balance cooling and lubrication.")
    else:
        st.write("**Recommendation:** Air blast cooling is sufficient for this cutting speed.")

    # Cost Estimation Tool
    st.subheader("Cost Estimation")
    machine_hour_rate = st.number_input("Enter Machine Hour Rate ($/hour)", min_value=10.0, value=50.0, key="adv_machine_hour_rate")
    tool_cost = st.number_input("Enter Tool Cost ($)", min_value=1.0, value=100.0, key="adv_tool_cost")
    material_cost = st.number_input("Enter Material Cost ($/kg)", min_value=0.1, value=2.0, key="adv_material_cost")
    labor_cost_per_hour = st.number_input("Enter Labor Cost ($/hour)", min_value=10.0, value=30.0, key="adv_labor_cost")
    energy_cost_per_hour = st.number_input("Enter Energy Cost ($/hour)", min_value=1.0, value=5.0, key="adv_energy_cost")
    
    if feed_rate != 0:
        cycle_time = (depth_of_cut / feed_rate) * 60  # in minutes
    else:
        cycle_time = float('inf')  # Handle as infinite or prompt an error

    estimated_cost = ((cycle_time / 60) * (machine_hour_rate + labor_cost_per_hour + energy_cost_per_hour)) + tool_cost + material_cost
    st.write(f"**Estimated Cost of Machining ($):** {estimated_cost:.2f}")

    # Material Database Expansion
    st.subheader("Material Database Management")
    material_expansion = st.radio("Manage Material Data", ["View Materials", "Import Materials", "Export Materials"], key="adv_material_expansion")

    if material_expansion == "View Materials":
        st.write(pd.DataFrame(materials).transpose())
    elif material_expansion == "Import Materials":
        uploaded_file = st.file_uploader("Upload Material Data (CSV)", type=["csv"], key="adv_upload_materials")
        if uploaded_file is not None:
            try:
                imported_materials = pd.read_csv(uploaded_file)
                st.write(imported_materials)
            except Exception as e:
                st.error(f"An error occurred while loading the file: {e}")
    elif material_expansion == "Export Materials":
        materials_df = pd.DataFrame(materials).transpose()
        materials_df.to_csv("materials_export.csv")
        st.write("Materials exported to materials_export.csv")
        st.download_button(
            label="Download Materials Data",
            data=materials_df.to_csv(index=False),
            file_name="materials_export.csv",
            mime="text/csv"
        )

    # Detailed Reporting
    if st.button("Generate PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Cutting Parameter Report", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Operation: {operation}", ln=True)
        pdf.cell(200, 10, txt=f"Material: {selected_material}", ln=True)
        pdf.cell(200, 10, txt=f"Tool Material: {selected_tool_material}", ln=True)
        pdf.cell(200, 10, txt=f"Spindle Speed (RPM): {rpm:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Feed Rate ({'mm/min' if units == 'Metric' else 'in/min'}): {feed_rate:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Estimated Tool Life (minutes): {tool_life:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Cutting Force (N): {cutting_force:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Torque (Nm): {torque:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Heat Generation (J/s): {heat_generation:.2f}", ln=True)
        pdf_file = "cutting_parameter_report.pdf"
        pdf.output(pdf_file)
        st.write("PDF Report generated: cutting_parameter_report.pdf")
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="Download PDF Report",
                data=f,
                file_name=pdf_file,
                mime="application/pdf"
            )

st.write("\n---\n")
st.write("**Disclaimer:** This tool uses calculations based on industry standards and real-world data; however, users are strongly advised to verify calculations with their specific equipment and conditions. Safety and accuracy are critical in machining operations.")
