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

def calculate_tool_life(cutting_speed, material_factor):
    return material_factor / cutting_speed

def calculate_cutting_force(tensile_strength, depth_of_cut, tool_diameter):
    return tensile_strength * depth_of_cut * tool_diameter / 1000

def calculate_torque(cutting_force, tool_diameter):
    return (cutting_force * tool_diameter) / 2000

def calculate_heat_generation(cutting_speed, feed_rate, cutting_force):
    return 0.5 * cutting_speed * feed_rate * cutting_force

def calculate_tool_wear(cutting_speed, feed_rate, time):
    return 0.001 * cutting_speed * feed_rate * time  # Simplified model for tool wear over time

# Streamlit UI
st.title("Cutting Parameter Calculator")

# Tabs for Basic and Advanced Modes
tab1, tab2 = st.tabs(["Basic", "Advanced"])

with tab1:
    st.header("Basic Cutting Parameter Calculator")
    
    # User Inputs
    operation = st.selectbox("Select Operation", ["Milling", "Turning", "Drilling", "Tapping"], key="basic_operation")
    selected_material = st.selectbox("Select Material", list(materials.keys()))
    selected_tool_material = st.selectbox("Select Tool Material", list(tool_materials.keys()))
    cutter_diameter = st.number_input("Enter Cutter Diameter (mm)", min_value=1.0, value=10.0)
    feed_per_tooth = st.number_input("Enter Feed per Tooth (mm)", min_value=0.01, value=0.1)
    number_of_teeth = st.number_input("Enter Number of Teeth on Cutter", min_value=1, value=4)

    # Calculations
    cutting_speed = materials[selected_material]["cutting_speed"] * tool_materials[selected_tool_material]
    rpm = calculate_rpm(cutting_speed, cutter_diameter)
    feed_rate = calculate_feed_rate(feed_per_tooth, number_of_teeth, rpm)

    # Display Results
    st.subheader("Calculated Parameters")
    st.write(f"**Operation:** {operation}")
    st.write(f"**Spindle Speed (RPM):** {rpm:.2f}")
    st.write(f"**Feed Rate (mm/min):** {feed_rate:.2f}")

with tab2:
    st.header("Advanced Cutting Parameter Calculator")

    # User Inputs
    operation = st.selectbox("Select Operation", ["Milling", "Turning", "Drilling", "Tapping"], key="adv_operation")
    selected_material = st.selectbox("Select Material", list(materials.keys()), key="adv_material")
    selected_tool_material = st.selectbox("Select Tool Material", list(tool_materials.keys()), key="adv_tool_material")
    cutter_diameter = st.number_input("Enter Cutter Diameter (mm)", min_value=1.0, value=10.0, key="adv_cutter_diameter")
    number_of_teeth = st.number_input("Enter Number of Teeth on Cutter", min_value=1, value=4, key="adv_number_of_teeth")
    depth_of_cut = st.number_input("Enter Depth of Cut (mm)", min_value=0.1, value=2.0, key="adv_depth_of_cut")
    feed_per_tooth = st.number_input("Enter Feed per Tooth (mm)", min_value=0.01, value=0.1, key="adv_feed_per_tooth")

    # Calculations
    cutting_speed = materials[selected_material]["cutting_speed"] * tool_materials[selected_tool_material]
    rpm = calculate_rpm(cutting_speed, cutter_diameter)
    feed_rate = calculate_feed_rate(feed_per_tooth, number_of_teeth, rpm)
    tool_life = calculate_tool_life(cutting_speed, materials[selected_material]["machinability"]) * 60  # Convert hours to minutes

    # Advanced Calculations
    cutting_force = calculate_cutting_force(materials[selected_material]["tensile_strength"], depth_of_cut, cutter_diameter)
    torque = calculate_torque(cutting_force, cutter_diameter)
    heat_generation = calculate_heat_generation(cutting_speed, feed_rate, cutting_force)

    # Display Results
    st.subheader("Calculated Parameters")
    st.write(f"**Operation:** {operation}")
    st.write(f"**Spindle Speed (RPM):** {rpm:.2f}")
    st.write(f"**Feed Rate (mm/min):** {feed_rate:.2f}")
    st.write(f"**Estimated Tool Life (minutes):** {tool_life:.2f}")

    st.subheader("Advanced Calculations")
    st.write(f"**Cutting Force (N):** {cutting_force:.2f}")
    st.write(f"**Torque (Nm):** {torque:.2f}")
    st.write(f"**Heat Generation (J/s):** {heat_generation:.2f}")

    # Graph: Tool Life vs Cutting Speed
    st.subheader("Tool Life vs Cutting Speed")
    cutting_speeds = [cutting_speed * i for i in range(1, 6)]
    tool_lives = [calculate_tool_life(cs, materials[selected_material]["machinability"]) * 60 for cs in cutting_speeds]  # Convert hours to minutes

    plt.figure(figsize=(10, 5))
    plt.plot(cutting_speeds, tool_lives, marker='o')
    plt.xlabel("Cutting Speed (m/min)")
    plt.ylabel("Tool Life (minutes)")
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
    machine_hour_rate = st.number_input("Enter Machine Hour Rate ($/hour)", min_value=10.0, value=50.0, key="adv_machine_hour_rate")
    tool_cost = st.number_input("Enter Tool Cost ($)", min_value=1.0, value=100.0, key="adv_tool_cost")
    material_cost = st.number_input("Enter Material Cost ($/kg)", min_value=0.1, value=2.0, key="adv_material_cost")
    cycle_time = (depth_of_cut / feed_rate) * 60  # in minutes

    estimated_cost = (cycle_time / 60) * machine_hour_rate + tool_cost + material_cost
    st.write(f"**Estimated Cost of Machining ($):** {estimated_cost:.2f}")

    # Material Database Expansion
    st.subheader("Material Database Management")
    material_expansion = st.radio("Manage Material Data", ["View Materials", "Import Materials", "Export Materials"], key="adv_material_expansion")

    if material_expansion == "View Materials":
        st.write(pd.DataFrame(materials).transpose())
    elif material_expansion == "Import Materials":
        uploaded_file = st.file_uploader("Upload Material Data (CSV)", type=["csv"], key="adv_upload_materials")
        if uploaded_file is not None:
            imported_materials = pd.read_csv(uploaded_file)
            st.write(imported_materials)
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
        pdf.cell(200, 10, txt=f"Feed Rate (mm/min): {feed_rate:.2f}", ln=True)
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

    # Process Simulation (Enhanced)
    if st.button("Run Process Simulation"):
        st.subheader("Process Simulation")
        simulation_time = st.slider("Select Simulation Time (minutes)", min_value=1, max_value=60, value=10)
        st.write("Simulating the cutting process...")

        time_steps = np.linspace(0, simulation_time, num=10)
        cutting_forces = []
        tool_wear_values = []
        temperatures = []

        for t in time_steps:
            cutting_force = calculate_cutting_force(materials[selected_material]["tensile_strength"], depth_of_cut, cutter_diameter)
            cutting_forces.append(cutting_force)
            tool_wear = calculate_tool_wear(cutting_speed, feed_rate, t)
            tool_wear_values.append(tool_wear)
            temperature = calculate_heat_generation(cutting_speed, feed_rate, cutting_force) / 1000  # Simplified temperature estimate
            temperatures.append(temperature)
            st.write(f"Time: {t:.1f} min, Cutting Force: {cutting_force:.2f} N, Tool Wear: {tool_wear:.2f} mm, Temperature: {temperature:.2f} °C")

        # Plotting Simulation Results
        st.subheader("Simulation Results")
        fig, ax = plt.subplots(3, 1, figsize=(10, 15))
        ax[0].plot(time_steps, cutting_forces, label='Cutting Force (N)', color='b')
        ax[0].set_xlabel('Time (minutes)')
        ax[0].set_ylabel('Cutting Force (N)')
        ax[0].set_title('Cutting Force vs Time')
        ax[0].legend()

        ax[1].plot(time_steps, tool_wear_values, label='Tool Wear (mm)', color='r')
        ax[1].set_xlabel('Time (minutes)')
        ax[1].set_ylabel('Tool Wear (mm)')
        ax[1].set_title('Tool Wear vs Time')
        ax[1].legend()

        ax[2].plot(time_steps, temperatures, label='Temperature (°C)', color='g')
        ax[2].set_xlabel('Time (minutes)')
        ax[2].set_ylabel('Temperature (°C)')
        ax[2].set_title('Temperature vs Time')
        ax[2].legend()

        st.pyplot(fig)
        st.write("Simulation completed.")

st.write("\n---\n")
st.write("**Note:** This is a prototype tool and should be used with caution. Always verify the calculations with industry standards and safety guidelines before applying them in actual machining operations.")
