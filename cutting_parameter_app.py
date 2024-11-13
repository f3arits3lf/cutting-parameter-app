import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import json

# Material and Tooling Data
materials = {
    "Aluminum 6061": {"cutting_speed": 300, "machinability": 100, "tensile_strength": 310, "hardness": 95},
    "Steel 1045": {"cutting_speed": 100, "machinability": 60, "tensile_strength": 585, "hardness": 170},
    "Titanium": {"cutting_speed": 60, "machinability": 30, "tensile_strength": 900, "hardness": 300},
}

tool_materials = {
    "HSS": 1.0,
    "Carbide": 2.5,
    "Ceramic": 5.0
}

# Calculation Functions
def calculate_rpm(cutting_speed, tool_diameter):
    return (cutting_speed * 1000) / (3.14 * tool_diameter)

def calculate_feed_rate(feed_per_tooth, number_of_teeth, rpm):
    return feed_per_tooth * number_of_teeth * rpm

def calculate_tool_life(cutting_speed, material_factor):
    return material_factor / cutting_speed

def calculate_cutting_force(tensile_strength, depth_of_cut, tool_diameter):
    return tensile_strength * depth_of_cut * tool_diameter / 1000

def calculate_torque(cutting_force, tool_diameter):
    return (cutting_force * tool_diameter) / 2000

def calculate_heat_generation(cutting_speed, feed_rate, cutting_force):
    return 0.5 * cutting_speed * feed_rate * cutting_force

# Streamlit UI
st.sidebar.title("Cutting Parameter Calculator")
operation = st.sidebar.selectbox("Select Operation", ["Milling", "Turning", "Drilling", "Tapping"])

# User Inputs
selected_material = st.sidebar.selectbox("Select Material", list(materials.keys()))
selected_tool_material = st.sidebar.selectbox("Select Tool Material", list(tool_materials.keys()))

cutter_diameter = st.sidebar.number_input("Enter Cutter Diameter (mm)", min_value=1.0, value=10.0)
number_of_teeth = st.sidebar.number_input("Enter Number of Teeth on Cutter", min_value=1, value=4)
depth_of_cut = st.sidebar.number_input("Enter Depth of Cut (mm)", min_value=0.1, value=2.0)
feed_per_tooth = st.sidebar.number_input("Enter Feed per Tooth (mm)", min_value=0.01, value=0.1)

# Calculations
cutting_speed = materials[selected_material]["cutting_speed"] * tool_materials[selected_tool_material]
rpm = calculate_rpm(cutting_speed, cutter_diameter)
feed_rate = calculate_feed_rate(feed_per_tooth, number_of_teeth, rpm)
tool_life = calculate_tool_life(cutting_speed, materials[selected_material]["machinability"])

# Advanced Calculations
cutting_force = calculate_cutting_force(materials[selected_material]["tensile_strength"], depth_of_cut, cutter_diameter)
torque = calculate_torque(cutting_force, cutter_diameter)
heat_generation = calculate_heat_generation(cutting_speed, feed_rate, cutting_force)

# Display Results
st.title(f"{operation} Parameters")

st.subheader("Calculated Parameters")
st.write(f"**Spindle Speed (RPM):** {rpm:.2f}")
st.write(f"**Feed Rate (mm/min):** {feed_rate:.2f}")
st.write(f"**Estimated Tool Life (hours):** {tool_life:.2f}")

st.subheader("Advanced Calculations")
st.write(f"**Cutting Force (N):** {cutting_force:.2f}")
st.write(f"**Torque (Nm):** {torque:.2f}")
st.write(f"**Heat Generation (J/s):** {heat_generation:.2f}")

# Graph: Tool Life vs Cutting Speed
st.subheader("Tool Life vs Cutting Speed")
cutting_speeds = [cutting_speed * i for i in range(1, 6)]
tool_lives = [calculate_tool_life(cs, materials[selected_material]["machinability"]) for cs in cutting_speeds]

plt.figure(figsize=(10, 5))
plt.plot(cutting_speeds, tool_lives, marker='o')
plt.xlabel("Cutting Speed (m/min)")
plt.ylabel("Tool Life (hours)")
plt.title("Tool Life vs Cutting Speed")
st.pyplot(plt)

# Recommendations for Cooling/Lubrication
st.subheader("Recommendations for Cooling/Lubrication")
if cutting_speed > 200:
    st.write("**Recommendation:** Use flood coolant to prevent excessive heat and prolong tool life.")
else:
    st.write("**Recommendation:** Air blast or mist cooling is sufficient for this cutting speed.")

# Cost Estimation Tool
st.subheader("Cost Estimation")
machine_hour_rate = st.sidebar.number_input("Enter Machine Hour Rate ($/hour)", min_value=10.0, value=50.0)
tool_cost = st.sidebar.number_input("Enter Tool Cost ($)", min_value=1.0, value=100.0)
material_cost = st.sidebar.number_input("Enter Material Cost ($/kg)", min_value=0.1, value=2.0)
cycle_time = (depth_of_cut / feed_rate) * 60  # in minutes

estimated_cost = (cycle_time / 60) * machine_hour_rate + tool_cost + material_cost
st.write(f"**Estimated Cost of Machining ($):** {estimated_cost:.2f}")

# Material Database Expansion
st.sidebar.subheader("Material Database Management")
material_expansion = st.sidebar.radio("Manage Material Data", ["View Materials", "Import Materials", "Export Materials"])

if material_expansion == "View Materials":
    st.sidebar.write(pd.DataFrame(materials).transpose())
elif material_expansion == "Import Materials":
    uploaded_file = st.sidebar.file_uploader("Upload Material Data (CSV)", type=["csv"])
    if uploaded_file is not None:
        imported_materials = pd.read_csv(uploaded_file)
        st.sidebar.write(imported_materials)
elif material_expansion == "Export Materials":
    materials_df = pd.DataFrame(materials).transpose()
    materials_df.to_csv("materials_export.csv")
    st.sidebar.write("Materials exported to materials_export.csv")

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
    pdf.cell(200, 10, txt=f"Feed Rate (mm/min): {feed_rate:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Estimated Tool Life (hours): {tool_life:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Cutting Force (N): {cutting_force:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Torque (Nm): {torque:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Heat Generation (J/s): {heat_generation:.2f}", ln=True)
    pdf.output("cutting_parameter_report.pdf")
    st.write("PDF Report generated: cutting_parameter_report.pdf")

# Process Simulation (Basic)
if st.button("Run Process Simulation"):
    st.subheader("Process Simulation")
    st.write("Simulating the cutting process...")
    for i in range(1, 6):
        st.write(f"Step {i}: Cutting at speed {cutting_speed * i} m/min")
    st.write("Simulation completed.")

st.write("\n---\n")
st.write("**Note:** This is a prototype tool and should be used with caution. Always verify the calculations with industry standards and safety guidelines before applying them in actual machining operations.")