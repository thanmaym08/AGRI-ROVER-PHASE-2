import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
import os

doc = docx.Document()

# Set standard margins (0.75 inch)
for section in doc.sections:
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

# Configure default style
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(11)
font.color.rgb = RGBColor(15, 23, 42)
style.paragraph_format.line_spacing = 1.2
style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

def set_cell_margins(cell, top=70, bottom=70, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)

def add_header_banner():
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run("KARNATAKA STATE COUNCIL FOR SCIENCE AND TECHNOLOGY (KSCST)\n")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(13)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(15, 23, 42)

    r2 = p.add_run("Indian Institute of Science Campus, Bengaluru – 560012\n")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(10.5)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(51, 65, 85)

    r3 = p.add_run("50th SERIES OF THE STUDENT PROJECT PROGRAMME (SPP: 2026–2027)\n")
    r3.font.name = 'Times New Roman'
    r3.font.size = Pt(12)
    r3.font.bold = True
    r3.font.color.rgb = RGBColor(180, 83, 9)

    r4 = p.add_run("OFFICIAL PROJECT PROPOSAL FORMAT FOR POSTGRADUATE (MCA) TEAMS")
    r4.font.name = 'Times New Roman'
    r4.font.size = Pt(11)
    r4.font.bold = True
    r4.font.color.rgb = RGBColor(30, 58, 138)

def add_section_title(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(30, 58, 138)
    return p

def add_subheading(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGBColor(15, 23, 42)
    return p

def add_body_p(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    return p

def add_bullet_p(text, bold_prefix=''):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.font.name = 'Times New Roman'
        r_bold.font.size = Pt(11)
        r_bold.font.bold = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    return p

def add_table_caption(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = RGBColor(30, 58, 138)
    return p

def add_fig_caption(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(9.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(51, 65, 85)
    return p

def add_picture_centered(img_path, width_in_inches=5.4):
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(5)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(img_path, width=Inches(width_in_inches))
    else:
        print(f"Warning: Image {img_path} not found.")

# ==================== BUILD PROPOSAL DOCUMENT ====================
add_header_banner()

# Metadata Box Table
add_table_caption("Table 1: Institutional, Departmental & Project Registration Details")
tbl_meta = doc.add_table(rows=7, cols=2)
tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
meta_data = [
    ("Name of the Institution:", "B.M.S. INSTITUTE OF TECHNOLOGY & MANAGEMENT (BMSITM)\nDoddaballapur Main Road, Avalahalli, Yelahanka, Bengaluru – 560064"),
    ("Department / Programme:", "Department of Master of Computer Applications (MCA) [Postgraduate - 2-Year Program]"),
    ("Broad Indicative Theme (KSCST):", "Theme 1: Sustainable Agriculture, Food Security and Rural Development and Inclusive Technologies\n(Interdisciplinary alignment with Theme 4: AI & Digital Tech and Theme 6: Robotics & Automation)"),
    ("Project Proposal Title:", "Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring"),
    ("Project Duration / Schedule:", "Date of Commencement: 01/10/2025    |    Probable Date of Completion: 31/05/2027"),
    ("College KSCST SPP Coordinator:", "Dr. MANJUNATHA C, Associate Professor\nDepartment of Chemistry, BMSITM | Email: manjuc@bmsit.in | Mobile: +91 9880744476"),
    ("Project Coordinator & Guide:", "Dr. DWARAKANATH G V, Project Coordinator & Associate Professor\nDepartment of MCA, BMSITM | Email: dwarakanath.gv@bmsit.in | Mobile: +91 9886026526")
]
for r_i, (k, v) in enumerate(meta_data):
    row = tbl_meta.rows[r_i]
    row.cells[0].text = k
    row.cells[1].text = v
    set_cell_shading(row.cells[0], 'F1F5F9')
    row.cells[0].paragraphs[0].runs[0].font.bold = True
    row.cells[0].paragraphs[0].runs[0].font.size = Pt(9.5)
    row.cells[1].paragraphs[0].runs[0].font.size = Pt(9.5)
    set_cell_margins(row.cells[0], top=40, bottom=40, left=80, right=80)
    set_cell_margins(row.cells[1], top=40, bottom=40, left=80, right=80)

# Student Team Table
add_table_caption("Table 2: Student Project Team Details (Maximum 4 Students)")
tbl_team = doc.add_table(rows=5, cols=5)
tbl_team.alignment = WD_TABLE_ALIGNMENT.CENTER
team_headers = ["Sl.", "Name of Student", "USN", "Contact Mobile", "Email ID"]
for c_i, h in enumerate(team_headers):
    tbl_team.rows[0].cells[c_i].text = h
    set_cell_shading(tbl_team.rows[0].cells[c_i], '1E3A8A')
    p = tbl_team.rows[0].cells[c_i].paragraphs[0]
    p.runs[0].font.bold = True
    p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
    p.runs[0].font.size = Pt(9.5)

team_members = [
    ("1", "THANMAY M (Team Leader)", "1BY24MC095", "+91 9880123456", "thanmaym08@gmail.com"),
    ("2", "KEERTHANA", "1BY24MC045", "+91 9845123456", "keerthana.mca@bmsit.in"),
    ("3", "MOHAN", "1BY24MC058", "+91 9742123456", "mohan.mca@bmsit.in"),
    ("4", "MONICA", "1BY24MC061", "+91 9611123456", "monica.mca@bmsit.in")
]
for r_i, member in enumerate(team_members):
    row = tbl_team.rows[r_i+1]
    for c_i, val in enumerate(member):
        row.cells[c_i].text = val
        p = row.cells[c_i].paragraphs[0]
        p.runs[0].font.size = Pt(9)
        if c_i == 1 and "Team Leader" in val:
            p.runs[0].font.bold = True
        set_cell_margins(row.cells[c_i], top=35, bottom=35, left=60, right=60)
    if r_i % 2 == 1:
        for c in row.cells:
            set_cell_shading(c, 'F8FAFC')

# Note on USN placeholders
p_note = doc.add_paragraph()
p_note.paragraph_format.space_before = Pt(2)
p_note.paragraph_format.space_after = Pt(8)
r_n = p_note.add_run("* Note: Please verify and confirm exact USNs and mobile numbers for all 4 team members prior to submission.")
r_n.font.size = Pt(8.5)
r_n.font.italic = True
r_n.font.color.rgb = RGBColor(100, 116, 139)

doc.add_page_break()

# ==================== TECHNICAL PROPOSAL SECTIONS ====================
add_section_title("1. PROJECT SUMMARY / ABSTRACT")
add_body_p("Agri Rover is an autonomous cyber-physical robotic vehicle engineered specifically for localized precision agriculture, automated in-situ soil health diagnostics, and zero-risk digital twin algorithm testing. Contemporary agriculture across Karnataka faces severe headwinds: chronic farm labor shortages, rising agrochemical costs, widespread soil degradation due to over-fertilization, and environmental toxicity caused by conventional blanket tractor sprayers that waste up to 70–80% of applied chemicals.")
add_body_p("Agri Rover replaces broad-spectrum broadcast spraying with real-time edge computer vision (OpenCV) running onboard a Raspberry Pi 4 Model B single-board computer. The robot captures 1080p sub-canopy video, transforms frames to HSV color space, isolates foliar threats (caterpillar pests and invasive weeds) via morphological segmentation, and triggers directional 12V solenoid valves for millisecond-calibrated micro-burst chemical delivery, saving up to 80% of active pesticide volume. Simultaneously, a motorized linear actuator deploys electrochemical soil probes (NPK, pH, and capacitive soil moisture) directly into the crop bed while the 4WD skid-steer chassis (dual BTS7960 43A H-bridges) is immobilized by a software safety interlock.")
add_body_p("A cornerstone engineering contribution of Agri Rover is its high-fidelity 3D WebGL Digital Twin Simulator built with React and Three.js. The simulator mirrors exact physical kinematics, zero-radius point turns, row lane-lock steering, and telemetry streaming over WebSockets/REST, enabling smallholder farmers and researchers to validate patrol and spraying algorithms in virtual farmland prior to physical hardware deployment.")

add_section_title("2. INTRODUCTION AND PROBLEM STATEMENT")
add_subheading("2.1 Background and Socio-Agricultural Relevance in Karnataka")
add_body_p("Agriculture is the economic backbone of Karnataka, sustaining over 60% of the rural population across diverse agro-climatic zones ranging from coastal paddy fields to drought-prone dryland farming in North Karnataka. However, modern farming operations are severely constrained by:")
add_bullet_p("Traditional tractor-mounted boom sprayers and manual backpack sprayers broadcast chemical mist uniformly across entire fields, drenching barren soil and healthy crops equally. Over 70% of chemicals are lost to wind drift, volatilization, and runoff, causing severe chemical residue buildup in Karnataka's river basins and water tables.", "1. Severe Agrochemical Overuse & Leaching: ")
add_bullet_p("Over-application of chemical nitrogen (urea) and unmonitored soil acidification have depleted native soil microbiomes across major cropping belts (cotton, sugarcane, maize, tomato), leading to falling crop yields and chronic micronutrient deficiencies.", "2. Soil Health Degradation & Lack of Real-Time NPK Testing: ")
add_bullet_p("Rapid urban migration has caused acute agricultural labor deficits during peak weeding and spraying seasons, with daily farm wages escalating sharply and manual backpack spraying posing grave occupational respiratory and neurological risks to operators.", "3. Acute Farm Labor Shortages & Operator Health Hazards: ")

add_subheading("2.2 Problem Statement")
add_body_p("To design, fabricate, and validate an affordable, open-architecture autonomous agricultural UGV that integrates onboard edge computer vision for plant-level pest and weed micro-spraying, automated in-situ soil nutrient (NPK/pH/moisture) probing, and a 3D WebGL digital twin simulation framework, eliminating chemical wastage and safeguarding rural farmer health.")

add_section_title("3. REVIEW OF LITERATURE AND PRIOR ART")
add_body_p("A comprehensive literature review of agricultural spraying and autonomous field robotics was conducted to benchmark existing solutions:")
add_bullet_p("Zhang & Pierce (2018) established that commercial tractor sprayers inflict heavy soil compaction, consume significant diesel fuel, and cannot perform plant-level targeted spraying.", "1. Tractor Boom Sprayers: ")
add_bullet_p("Agricultural octocopter drones provide rapid broad-acre spraying but suffer from severe aerodynamic propeller downwash (causing spray drift), short 15–20 minute flight times, inability to inspect sub-canopy foliage, and complete inability to perform physical ground soil testing.", "2. Aerial Spraying UAVs: ")
add_bullet_p("Monolithic commercial smart sprayers (e.g., John Deere See & Spray, Bilberry) offer high AI accuracy but cost over $50,000 (Rs. 40+ Lakhs), rely on locked proprietary software, and are financially inaccessible to small and marginal Indian farmers.", "3. Commercial Autonomous UGVs: ")
add_bullet_p("Recent literature demonstrates that edge single-board computers (Raspberry Pi 4) paired with optimized OpenCV routines can achieve >15 FPS inference latency for foliar weed and pest classification, enabling sub-second directional solenoid actuation without needing expensive cloud servers.", "4. Edge Vision & Embedded Computing: ")

# Comparative Table
add_table_caption("Table 3: Comparative Analysis — Conventional Systems vs. Agri Rover")
tbl_comp = doc.add_table(rows=6, cols=4)
tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
headers_comp = ["Parameter / Metric", "Tractor Boom Sprayer", "Agricultural Spray Drone", "Agri Rover (Proposed)"]
for i, h in enumerate(headers_comp):
    tbl_comp.rows[0].cells[i].text = h
    set_cell_shading(tbl_comp.rows[0].cells[i], '1E3A8A')
    p = tbl_comp.rows[0].cells[i].paragraphs[0]
    p.runs[0].font.bold = True
    p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
    p.runs[0].font.size = Pt(9)

comp_rows = [
    ("Chemical Dispensing", "Blanket broadcast (70-80% wasted)", "Aerial broadcast (High wind drift)", "Pinpoint AI micro-bursts (Up to 80% saved)"),
    ("Soil Nutrient Sensing", "None (Requires lab sample turnaround)", "None (Physically impossible from air)", "Motorized in-situ NPK, pH & moisture probe"),
    ("Field Operating Domain", "Open broad-acre (Causes compaction)", "High-altitude canopy overview", "Direct sub-canopy row navigation (4WD Skid)"),
    ("Simulation Testing", "Unavailable / Proprietary", "Commercial flight simulator only", "Zero-cost 3D WebGL Digital Twin (Three.js)"),
    ("System Cost & Safety", "High fuel cost & severe toxic exposure", "High crash risk & expensive batteries", "Sub-Rs. 25,000 cost & zero human toxic contact")
]
for r_i, row in enumerate(comp_rows):
    r = tbl_comp.rows[r_i+1]
    for c_i, val in enumerate(row):
        r.cells[c_i].text = val
        p = r.cells[c_i].paragraphs[0]
        p.runs[0].font.size = Pt(8.5)
        set_cell_margins(r.cells[c_i], top=35, bottom=35, left=60, right=60)
    if r_i % 2 == 1:
        for c in r.cells: set_cell_shading(c, 'F8FAFC')

add_section_title("4. PROJECT AIM AND OBJECTIVES")
add_subheading("4.1 Project Aim")
add_body_p("To develop and field-evaluate 'Agri Rover' — an intelligent cyber-physical autonomous agricultural robotic vehicle powered by a Raspberry Pi 4 edge compute module and a real-time 3D WebGL Digital Twin, delivering precision computer vision-guided targeted pesticide micro-bursts, automated motorized ground soil probing, and hazard-free virtual prototyping.")

add_subheading("4.2 Measurable Technical Objectives")
add_bullet_p("Design and assemble a 4-wheel skid-steer rover chassis driven by 4 high-torque 12V DC geared motors and dual BTS7960 43A H-bridge drivers capable of zero-radius point turns (R = 0) and lane-locked crop-row navigation.", "1. Rugged 4WD Locomotion & High-Current Motor Subsystem: ")
add_bullet_p("Implement an onboard real-time computer vision pipeline using Python and OpenCV on Raspberry Pi 4 to detect biological foliar pests (purple color mask) and weeds (red/green anomaly mask) at >15 FPS with spatial pixel centroid offset calculations.", "2. Edge Computer Vision & Threat Perception: ")
add_bullet_p("Build a high-pressure chemical fluid dispensing subsystem with a 12V diaphragm pump and dual directional 12V solenoid valves capable of calibrated 200ms targeted micro-bursts directly onto detected targets.", "3. Precision Chemical Micro-Burst Actuation: ")
add_bullet_p("Construct a motorized linear actuator probe mechanism integrating electrochemical NPK, pH, and capacitive soil moisture sensors with drive motor lockout interlocks and real-time georeferenced spatial logging.", "4. In-Situ Soil Health Probing Array: ")
add_bullet_p("Engineer an interactive browser-based 3D WebGL Digital Twin simulator using React.js and Three.js for real-time telemetry rendering, manual teleoperation, virtual spray mist particles, and battery fail-safe cutoff (V <= 12.0V).", "5. 3D Digital Twin Simulation & Telemetry Cockpit: ")

doc.add_page_break()

# ==================== METHODOLOGY & ARCHITECTURE ====================
add_section_title("5. DETAILED METHODOLOGY AND SYSTEM ARCHITECTURE")
add_subheading("5.1 Cyber-Physical Architecture Overview")
add_body_p("The Agri Rover methodology follows a tightly integrated, event-driven cyber-physical framework comprising four interacting layers: (1) Perception & Computer Vision, (2) Edge Decision & Kinematics Control, (3) High-Current Physical Actuation, and (4) Digital Twin Simulation & Telemetry.")

add_picture_centered("extracted_pdf_p10_1__Image73.png", width_in_inches=5.8)
add_fig_caption("Fig. 1: End-to-End Cyber-Physical System Architecture of Agri Rover (Raspberry Pi 4 Core)")

add_subheading("5.2 Edge Computer Vision Pipeline (OpenCV on Raspberry Pi 4)")
add_body_p("The perception engine captures real-time video via a high-definition 1080p wide-angle camera mounted on the rover front boom. The frame pipeline operates continuously:")
add_bullet_p("Incoming RGB frames are downscaled to 640 x 480 resolution to optimize CPU cache throughput and converted to Hue-Saturation-Value (HSV) color space, decoupling illumination variations from chromaticity.", "a. Preprocessing & Color Space Conversion: ")
add_bullet_p("Targeted color masks segment foliar anomalies: Purple Mask (H in [130, 160], S in [50, 255], V in [50, 255]) isolates caterpillars and biological pests; Red Mask isolates invasive broadleaf weeds. Morphological opening and closing filters eliminate sensor noise.", "b. Morphological Thresholding: ")
add_bullet_p("Contour analysis computes the bounding box and centroid coordinates (Cx, Cy) of all valid targets. The horizontal error offset Δx = Cx - x_center determines whether the Left or Right solenoid valve triggers.", "c. Centroid & Spatial Offset Extraction: ")

add_picture_centered("extracted_pdf_p18_8__Image95.png", width_in_inches=5.2)
add_fig_caption("Fig. 2: First-Person Camera Feed with Real-Time OpenCV Threat Bounding Box Annotations")

add_subheading("5.3 Physical Actuation & Motor Kinematics (Dual BTS7960 43A)")
add_body_p("Locomotion relies on a 4-wheel differential skid-steer geometry. Left and Right motor pairs are driven independently by dual BTS7960 43A H-bridges controlled via hardware-isolated GPIO PWM on the Raspberry Pi 4. The kinematics model supports:")
add_bullet_p("Applying equal forward PWM to both tracks propels the rover down crop lanes. Software lane-lock routines compensate for terrain drift using Hough line angle feedback.", "• Forward / Reverse Propulsion: ")
add_bullet_p("Applying forward PWM to track A and reverse PWM to track B rotates the rover about its central vertical axis (R = 0), enabling automated 180° headland U-turns within narrow 50–70 cm crop row spacings without crushing plants.", "• Zero-Radius Point Turning: ")

add_picture_centered("extracted_pdf_p19_9__Image98.png", width_in_inches=5.6)
add_fig_caption("Fig. 3: Raspberry Pi 4 GPIO Hardware Wiring Schematic & Dual BTS7960 Motor Interconnect")

add_subheading("5.4 Precision Micro-Burst Spraying & Soil Health Probing Subsystem")
add_body_p("Chemical actuation utilizes a high-pressure 12V DC diaphragm pump feeding dual directional fast-acting 12V solenoid valves. When OpenCV confirms a threat with area exceeding the threshold, the corresponding solenoid opens for a calibrated 200ms micro-burst. Antiparallel 1N4007 flyback diodes clamp inductive voltage spikes, protecting the logic rails.")
add_body_p("For soil diagnostics, the rover transitions into stationary probing mode: (1) Drive motors are locked via software interlock; (2) A motorized linear actuator lowers the electrochemical sensor probe 50mm into the soil bed; (3) ADC readings for Nitrogen, Phosphorus, Potassium (NPK), pH, and moisture are stabilized over a 2-second sampling window; (4) The actuator fully retracts to stowage; and (5) Telemetry packets upload the georeferenced data to the operational dashboard.")

add_picture_centered("extracted_pdf_p13_4__Image81.png", width_in_inches=5.2)
add_fig_caption("Fig. 4: Autonomous Patrol, Targeted Micro-Burst & In-Situ Soil Probing Activity Diagram")

doc.add_page_break()

add_subheading("5.5 3D WebGL Digital Twin Simulator (React.js & Three.js)")
add_body_p("To eliminate hardware damage during early-stage control and vision algorithm prototyping, Agri Rover integrates an interactive 3D WebGL Digital Twin built with React and Three.js. The simulator renders a virtual 3D crop field with textured terrain, Rocker-Bogie suspension articulation, instanced particle mist spray cones, and real-time HUD telemetry gauges (battery voltage, speed presets, lane-lock status). Bi-directional WebSockets allow seamless teleoperation and simulated autonomous patrols.")

add_picture_centered("extracted_pdf_p18_7__Image94.png", width_in_inches=5.6)
add_fig_caption("Fig. 5: Interactive 3D WebGL Digital Twin Cockpit with Real-Time Farmland & Particle Mist Rendering")

add_picture_centered("extracted_pdf_p20_11__Image102.png", width_in_inches=5.2)
add_fig_caption("Fig. 6: Fabricated Hardware Chassis, Rocker-Bogie Suspension & Motor Driver Assembly")

add_section_title("6. TECHNICAL SPECIFICATIONS & POWER BUDGET")
add_subheading("6.1 Cyber-Physical Hardware Specifications")
add_table_caption("Table 4: Agri Rover Physical and Electronic Specifications")
tbl_spec = doc.add_table(rows=10, cols=3)
tbl_spec.alignment = WD_TABLE_ALIGNMENT.CENTER
spec_headers = ["Subsystem", "Component / Parameter", "Engineering Specification"]
for i, h in enumerate(spec_headers):
    tbl_spec.rows[0].cells[i].text = h
    set_cell_shading(tbl_spec.rows[0].cells[i], '1E3A8A')
    p = tbl_spec.rows[0].cells[i].paragraphs[0]
    p.runs[0].font.bold = True
    p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
    p.runs[0].font.size = Pt(9)

specs_data = [
    ("Core Embedded Compute", "Raspberry Pi 4 Model B", "Broadcom BCM2711, Quad-core Cortex-A72 @ 1.5GHz, 4GB LPDDR4 RAM, Gigabit Ethernet, 2.4/5GHz Wi-Fi"),
    ("Motor Driver Subsystem", "Dual BTS7960 43A H-Bridges", "Dual high-power MOSFET half-bridge drivers, 43A peak current per channel, optoisolated logic inputs"),
    ("Drive Actuators", "4x 12V DC Geared Motors", "High-torque planetary metal gearboxes (60 RPM, 15 kg-cm stall torque per motor) with mud-tread tires"),
    ("Precision Spraying", "12V Diaphragm Pump + Solenoids", "12V 4.0L/min 0.6MPa self-priming pump; 2x 12V NC fast-acting brass solenoid valves (<50ms response)"),
    ("Soil Health Probing", "Linear Actuator + Sensor Array", "100mm stroke 12V linear actuator; electrochemical NPK/pH probe and capacitive soil moisture sensor"),
    ("Perception Optics", "1080p HD Wide-Angle Camera", "OV5647 / USB 1080p sensor, 120° FOV, hardware auto-exposure, manual focus lock for crop row tracking"),
    ("Power Storage", "12.6V 3S Li-ion / 12V 7Ah SLA", "Rechargeable 3S 18650 Li-ion pack (with 20A BMS) or 12V 7Ah SLA battery; isolated LM2596 buck rails"),
    ("Chassis & Suspension", "Rocker-Bogie 4WD Skid-Steer", "Laser-cut 3mm acrylic/aluminum frame, passive rocker suspension maintaining ground contact on rough soil"),
    ("Safety Interlocks", "Hardware & Firmware Failsafes", "Auto-braking watchdog timeout (1.2s Wi-Fi loss), battery undervoltage cutoff (V <= 12.0V), probe motor lock")
]
for r_i, row in enumerate(specs_data):
    r = tbl_spec.rows[r_i+1]
    for c_i, val in enumerate(row):
        r.cells[c_i].text = val
        p = r.cells[c_i].paragraphs[0]
        p.runs[0].font.size = Pt(8.5)
        set_cell_margins(r.cells[c_i], top=30, bottom=30, left=50, right=50)
    if r_i % 2 == 1:
        for c in r.cells: set_cell_shading(c, 'F8FAFC')

add_subheading("6.2 Electrical Power Budget and Battery Runtime Analysis")
add_table_caption("Table 5: Electrical Power Budget & Current Draw Analysis")
tbl_pwr = doc.add_table(rows=7, cols=5)
tbl_pwr.alignment = WD_TABLE_ALIGNMENT.CENTER
pwr_headers = ["Subsystem / Load", "Voltage Rail", "Idle Current", "Peak Operating Current", "Operating Duty Cycle"]
for i, h in enumerate(pwr_headers):
    tbl_pwr.rows[0].cells[i].text = h
    set_cell_shading(tbl_pwr.rows[0].cells[i], '1E3A8A')
    p = tbl_pwr.rows[0].cells[i].paragraphs[0]
    p.runs[0].font.bold = True
    p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
    p.runs[0].font.size = Pt(8.5)

pwr_data = [
    ("Raspberry Pi 4 + Camera", "5.0V (Buck 1)", "600 mA", "1,200 mA (Active OpenCV)", "100% continuous"),
    ("Dual BTS7960 + 4 Motors", "12.0V (Battery)", "100 mA", "2,800 mA (Field acceleration)", "60% intermittent"),
    ("12V Chemical Pump", "12.0V (Switched)", "0 mA", "1,500 mA (Pressurization)", "15% burst"),
    ("Directional Solenoids (x2)", "12.0V (Relay)", "0 mA", "800 mA (200ms micro-burst)", "10% micro-burst"),
    ("Soil Linear Actuator", "12.0V (Relay)", "0 mA", "1,000 mA (Extension/Retract)", "5% spot probing"),
    ("TOTAL (Reflected on 12V)", "12.6V Main Bus", "~400 mA (4.8W)", "~4,800 mA Peak (57.6W)", "Mean ~1.8A (21.6W)")
]
for r_i, row in enumerate(pwr_data):
    r = tbl_pwr.rows[r_i+1]
    for c_i, val in enumerate(row):
        r.cells[c_i].text = val
        p = r.cells[c_i].paragraphs[0]
        p.runs[0].font.size = Pt(8.5)
        if r_i == len(pwr_data)-1:
            p.runs[0].font.bold = True
        set_cell_margins(r.cells[c_i], top=30, bottom=30, left=50, right=50)
    if r_i % 2 == 1 and r_i != len(pwr_data)-1:
        for c in r.cells: set_cell_shading(c, 'F8FAFC')
    elif r_i == len(pwr_data)-1:
        for c in r.cells: set_cell_shading(c, 'FEF3C7')

add_body_p("Battery Runtime Formulation: With a 12V 7.0Ah battery pack operating at an average field discharge current of I_avg ≈ 1.8 A (accounting for an 80% Depth-of-Discharge cutoff to protect cell health):")
add_body_p("T_runtime = (7.0 Ah × 0.80) / 1.8 A ≈ 3.11 Hours of Continuous Field Patrol.")

doc.add_page_break()

# ==================== NOVELTY, BUDGET & SCHEDULE ====================
add_section_title("7. NOVELTY, INNOVATION AND SOCIETAL IMPACT")
add_subheading("7.1 Novelty and Distinguishing Engineering Features")
add_bullet_p("While existing research focuses either exclusively on aerial drones or stationary soil IoT nodes, Agri Rover is the first low-cost platform to unify edge computer vision micro-burst spraying with automated mechanical soil penetration probing in a single sub-canopy UGV.", "1. Unified Sub-Canopy Crop-Care & Soil Diagnostic Architecture: ")
add_bullet_p("Commercial smart sprayers rely on broad continuous broadcast nozzles. Agri Rover implements millisecond-calibrated solenoid micro-bursts triggered only when target confidence and pixel centroid alignment are verified, cutting chemical runoff by up to 80%.", "2. Targeted Micro-Burst Chemical Delivery: ")
add_bullet_p("By delivering a physics-accurate 3D WebGL simulator accessible in any web browser, farmers and students can visualize robot kinematics, spray mist trajectories, and crop-row navigation without risking hardware collisions or incurring prototyping expenses.", "3. Zero-Risk Accessible 3D WebGL Digital Twin: ")

add_subheading("7.2 Alignment with UN Sustainable Development Goals (SDGs)")
add_bullet_p("Target 2.4 mandates resilient, sustainable food production systems that progressively improve soil health. Agri Rover achieves this by eliminating over-fertilization via in-situ NPK testing and preventing toxic chemical saturation.", "• UN SDG 2 (Zero Hunger - Target 2.4): ")
add_bullet_p("Target 12.4 mandates the environmentally sound management of chemicals to drastically reduce release into water and soil. Agri Rover slashes active pesticide consumption by up to 80%.", "• UN SDG 12 (Responsible Consumption & Production - Target 12.4): ")
add_bullet_p("By halting broad-spectrum chemical drenching and tracking soil pH, Agri Rover prevents soil acidification and preserves subterranean soil microbiomes.", "• UN SDG 15 (Life on Land): ")

add_section_title("8. ITEMIZED ESTIMATED PROJECT BUDGET")
add_table_caption("Table 6: Detailed Component Cost Breakdown & Financial Assistance Requested")
tbl_bgt = doc.add_table(rows=11, cols=5)
tbl_bgt.alignment = WD_TABLE_ALIGNMENT.CENTER
bgt_headers = ["Sl.", "Item Description", "Qty", "Unit Cost (Rs.)", "Total Cost (Rs.)"]
for i, h in enumerate(bgt_headers):
    tbl_bgt.rows[0].cells[i].text = h
    set_cell_shading(tbl_bgt.rows[0].cells[i], '1E3A8A')
    p = tbl_bgt.rows[0].cells[i].paragraphs[0]
    p.runs[0].font.bold = True
    p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
    p.runs[0].font.size = Pt(9)

budget_items = [
    ("1", "Raspberry Pi 4 Model B (4GB RAM) Single Board Computer", "1", "4,800", "4,800"),
    ("2", "Dual BTS7960 43A High-Power H-Bridge Motor Drivers", "2", "650", "1,300"),
    ("3", "High-Torque 12V DC Planetary Geared Motors (60 RPM) + Wheels", "4", "750", "3,000"),
    ("4", "Fabricated 4WD Chassis Frame, Rocker-Bogie Suspension & Hardware", "1 Set", "2,200", "2,200"),
    ("5", "12V DC Diaphragm Chemical Pump & Pressure Tubing Array", "1", "950", "950"),
    ("6", "12V Fast-Acting Directional Brass Solenoid Valves (<50ms)", "2", "600", "1,200"),
    ("7", "Motorized 100mm Linear Actuator for Soil Probe Deployment", "1", "1,850", "1,850"),
    ("8", "Electrochemical NPK, pH & Capacitive Soil Moisture Sensor Array", "1 Set", "2,400", "2,400"),
    ("9", "12.6V 3S Li-ion Battery Pack (20A BMS) + 12.6V 2A Smart Charger", "1", "1,600", "1,600"),
    ("10", "LM2596 Buck Converters, Relays, 1N4007 Diodes, Connectors, Wiring", "1 Set", "1,200", "1,200")
]
total_cost = 20500
kscst_req = 10000
college_contrib = 10500

for r_i, item in enumerate(budget_items):
    r = tbl_bgt.rows[r_i+1]
    for c_i, val in enumerate(item):
        r.cells[c_i].text = val
        p = r.cells[c_i].paragraphs[0]
        p.runs[0].font.size = Pt(8.5)
        set_cell_margins(r.cells[c_i], top=30, bottom=30, left=50, right=50)
    if r_i % 2 == 1:
        for c in r.cells: set_cell_shading(c, 'F8FAFC')

# Summary Rows
p_sum1 = doc.add_paragraph()
p_sum1.paragraph_format.space_before = Pt(6)
p_sum1.paragraph_format.space_after = Pt(2)
p_sum1.add_run(f"• Total Estimated Hardware & Fabrication Cost: Rs. {total_cost:,}/-\n").bold = True
p_sum1.add_run(f"• Amount of Financial Assistance Requested from KSCST (SPP): Rs. {kscst_req:,}/-\n").bold = True
p_sum1.add_run(f"• Remaining Institutional / Student Contribution: Rs. {college_contrib:,}/-").bold = True

add_section_title("9. PROJECT IMPLEMENTATION TIMELINE (GANTT CHART)")
add_table_caption("Table 7: Milestone Schedule & Deliverables Timeline (2025–2027)")
tbl_gantt = doc.add_table(rows=7, cols=7)
tbl_gantt.alignment = WD_TABLE_ALIGNMENT.CENTER
g_headers = ["Phase / Activity Milestone", "M1-M2", "M3-M4", "M5-M6", "M7-M8", "M9-M10", "M11-M12"]
for i, h in enumerate(g_headers):
    tbl_gantt.rows[0].cells[i].text = h
    set_cell_shading(tbl_gantt.rows[0].cells[i], '1E3A8A')
    p = tbl_gantt.rows[0].cells[i].paragraphs[0]
    p.runs[0].font.bold = True
    p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
    p.runs[0].font.size = Pt(8.5)

g_data = [
    ("Literature Review, Farmer Survey & Problem Formulation", "[XXXX]", "", "", "", "", ""),
    ("System SRS, Architecture & 3D Digital Twin Simulator", "", "[XXXX]", "", "", "", ""),
    ("Chassis Fabrication & Dual BTS7960 Motor Kinematics", "", "", "[XXXX]", "", "", ""),
    ("OpenCV Threat Vision & Solenoid Spray Integration", "", "", "", "[XXXX]", "", ""),
    ("Motorized In-Situ Soil Nutrient Probing Subsystem", "", "", "", "", "[XXXX]", ""),
    ("Field Validation, Benchmark Testing & KSCST Final Report", "", "", "", "", "", "[XXXX]")
]
for r_i, row in enumerate(g_data):
    r = tbl_gantt.rows[r_i+1]
    for c_i, val in enumerate(row):
        cell = r.cells[c_i]
        cell.text = val
        p = cell.paragraphs[0]
        p.runs[0].font.size = Pt(8.5)
        if "[XXXX]" in val:
            set_cell_shading(cell, 'CBD5E1')
            p.runs[0].bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_margins(cell, top=30, bottom=30, left=40, right=40)

add_section_title("10. REFERENCES")
refs = [
    "Zhang, Q., & Pierce, F. J. (2018). Precision Agriculture Technology for Crop Farming. CRC Press, Taylor & Francis Group.",
    "Raspberry Pi Foundation. (2024). Raspberry Pi 4 Model B Hardware & RPi.GPIO Documentation. https://www.raspberrypi.com/documentation/",
    "OpenCV Team. (2024). OpenCV Image Processing and Computer Vision Reference Manual (Version 4.x). https://docs.opencv.org/",
    "Mrdoob. (2024). Three.js JavaScript 3D Library Documentation (v0.128.0). https://threejs.org/docs/",
    "United Nations. (2023). Sustainable Development Goals: Goal 2 (Zero Hunger) & Goal 12 (Responsible Consumption and Production). https://sdgs.un.org/goals",
    "Karnataka State Council for Science and Technology (KSCST). (2026). Student Project Programme Guidelines (50th Series). Indian Institute of Science Campus, Bengaluru."
]
for ref in refs:
    add_bullet_p(ref)

doc.add_page_break()

# ==================== DECLARATIONS & ENDORSEMENTS ====================
add_section_title("DECLARATION BY STUDENTS")
add_body_p("We, the undersigned students of the Department of Master of Computer Applications (MCA), BMS Institute of Technology & Management, Bengaluru, hereby declare that the project proposal entitled 'Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring' is a bona fide record of independent work planned and executed by us under the guidance of Dr. Dwarakanath G V.")
add_body_p("We further declare that this project proposal has not been submitted previously to any other university, organization, or funding agency for the award of any degree, diploma, or financial sponsorship.")

# Student signature table
tbl_sig = doc.add_table(rows=5, cols=4)
tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
sig_headers = ["Sl.", "Name of Student", "USN", "Signature with Date"]
for i, h in enumerate(sig_headers):
    tbl_sig.rows[0].cells[i].text = h
    set_cell_shading(tbl_sig.rows[0].cells[i], 'F1F5F9')
    tbl_sig.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True
    tbl_sig.rows[0].cells[i].paragraphs[0].runs[0].font.size = Pt(9.5)

sig_data = [
    ("1", "THANMAY M (Team Leader)", "1BY24MC095", "\n\n________________________"),
    ("2", "KEERTHANA", "1BY24MC045", "\n\n________________________"),
    ("3", "MOHAN", "1BY24MC058", "\n\n________________________"),
    ("4", "MONICA", "1BY24MC061", "\n\n________________________")
]
for r_i, row in enumerate(sig_data):
    r = tbl_sig.rows[r_i+1]
    for c_i, val in enumerate(row):
        r.cells[c_i].text = val
        p = r.cells[c_i].paragraphs[0]
        p.runs[0].font.size = Pt(9)
        set_cell_margins(r.cells[c_i], top=40, bottom=40, left=50, right=50)

doc.add_paragraph().paragraph_format.space_after = Pt(12)

add_section_title("ENDORSEMENT BY PROJECT GUIDE & INSTITUTIONAL HEADS")
add_body_p("This is to certify that the project proposal entitled 'Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring' submitted by Thanmay M, Keerthana, Mohan, and Monica, final year students of MCA, is an original research and engineering endeavor. The project has been reviewed and endorsed for submission under the 50th Series of the Student Project Programme (SPP: 2026–2027) of the Karnataka State Council for Science and Technology (KSCST).")

# Institutional Endorsements Table
tbl_end = doc.add_table(rows=1, cols=3)
tbl_end.alignment = WD_TABLE_ALIGNMENT.CENTER
end_boxes = [
    "Signature of Project Guide:\n\n\n\n_________________________\nDr. DWARAKANATH G V\nProject Coordinator / Faculty\nDept. of MCA, BMSITM\nDate: 26/11/2026",
    "Signature of HOD:\n\n\n\n_________________________\nDr. APARNA K / HOD\nHead of the Department\nDept. of MCA, BMSITM\nDate: 26/11/2026",
    "Signature of Principal:\n\n\n\n_________________________\nDr. MOHAN BABU G N\nPrincipal / Head of Institution\nBMSITM, Bengaluru\n(Official Seal)"
]
for c_i, text in enumerate(end_boxes):
    cell = tbl_end.rows[0].cells[c_i]
    cell.text = text
    set_cell_shading(cell, 'F8FAFC')
    for p in cell.paragraphs:
        p.paragraph_format.line_spacing = 1.15
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9)
    set_cell_margins(cell, top=60, bottom=60, left=60, right=60)

output_filename = "KSCST_SPP_AgriRover_Project_Proposal.docx"
doc.save(output_filename)
print(f"SUCCESS: {output_filename} generated cleanly!")
