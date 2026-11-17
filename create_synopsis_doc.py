import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

doc = docx.Document()

# Set standard margins (1 inch)
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Set base Normal style
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(12)
font.color.rgb = RGBColor(0, 0, 0)
style.paragraph_format.line_spacing = 1.5
style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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

def add_heading_1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(13.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(20, 45, 80)
    return p

def add_subheading(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_body_p(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    return p

def add_bullet_p(text, bold_prefix=''):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.font.name = 'Times New Roman'
        r_bold.font.size = Pt(12)
        r_bold.font.bold = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    return p

def add_table_caption(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10)
    run.font.bold = True
    return p

def add_fig_caption(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10)
    run.font.bold = True
    return p

# ----------------- TITLE & COVER DETAILS -----------------
title_p = doc.add_paragraph()
title_p.paragraph_format.space_before = Pt(0)
title_p.paragraph_format.space_after = Pt(6)
title_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title_p.add_run('PROJECT WORK - PHASE I - MMCA34 (2025–27 Batch)\nSYNOPSIS REPORT')
r.font.name = 'Times New Roman'
r.font.size = Pt(15)
r.font.bold = True
r.font.color.rgb = RGBColor(16, 42, 77)

# Evaluation Meta Table
tbl_meta = doc.add_table(rows=3, cols=4)
tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_meta.autofit = False

tbl_meta.rows[0].cells[0].text = 'Student Name:'
tbl_meta.rows[0].cells[1].text = '[Enter Student Name]'
tbl_meta.rows[0].cells[2].text = 'USN:'
tbl_meta.rows[0].cells[3].text = '[Enter USN]'

tbl_meta.rows[1].cells[0].text = 'Project Title:'
tbl_meta.rows[1].cells[1].merge(tbl_meta.rows[1].cells[3])
tbl_meta.rows[1].cells[1].text = 'Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring'

tbl_meta.rows[2].cells[0].text = 'Project Guide:'
tbl_meta.rows[2].cells[1].text = '[Enter Project Guide Name, Designation]'
tbl_meta.rows[2].cells[2].text = 'Academic Year:'
tbl_meta.rows[2].cells[3].text = '2025–2026'

for row in tbl_meta.rows:
    for cell in row.cells:
        set_cell_margins(cell, top=60, bottom=60)
        for p in cell.paragraphs:
            p.paragraph_format.line_spacing = 1.15
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)

# Make headers bold in meta table
for r_i in range(3):
    tbl_meta.rows[r_i].cells[0].paragraphs[0].runs[0].font.bold = True
tbl_meta.rows[0].cells[2].paragraphs[0].runs[0].font.bold = True
tbl_meta.rows[2].cells[2].paragraphs[0].runs[0].font.bold = True

# Rubrics Component Table
add_table_caption('Table No: 1. Synopsis Evaluation Rubrics Mapping')
tbl_rubric = doc.add_table(rows=2, cols=4)
tbl_rubric.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ['Component', 'Evaluation Criteria', 'Max Marks', 'Marks Obtained']
for i, h in enumerate(headers):
    tbl_rubric.rows[0].cells[i].text = h
    set_cell_shading(tbl_rubric.rows[0].cells[i], 'E2E8F0')
    tbl_rubric.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True

row1 = tbl_rubric.rows[1]
row1.cells[0].text = 'Synopsis Evaluation'
row1.cells[1].text = 'Well-defined problem statement, literature survey, clear objectives, sound methodology, modules, technologies, and realistic Gantt chart timeline.'
row1.cells[2].text = '10'
row1.cells[3].text = ''

for row in tbl_rubric.rows:
    for cell in row.cells:
        set_cell_margins(cell, top=60, bottom=60)
        for p in cell.paragraphs:
            p.paragraph_format.line_spacing = 1.15
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(9.5)

# Table of Contents
add_table_caption('Table No: 2. Table of Contents')
tbl_toc = doc.add_table(rows=9, cols=3)
tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
toc_items = [
    ('Sl. No', 'Contents', 'Page No.'),
    ('1.', 'Introduction', '2'),
    ('2.', 'Literature Survey', '3'),
    ('3.', 'Problem Statement with Aim and Objectives', '4'),
    ('4.', 'SDG Alignment', '5'),
    ('5.', 'Methodology', '6'),
    ('6.', 'Modules Identified', '7'),
    ('7.', 'Tools and Technologies Identified', '8'),
    ('8.', 'Timeline Using Gantt Chart', '9')
]
for r_i, item in enumerate(toc_items):
    for c_i, val in enumerate(item):
        tbl_toc.rows[r_i].cells[c_i].text = val
        if r_i == 0:
            set_cell_shading(tbl_toc.rows[r_i].cells[c_i], 'E2E8F0')
            tbl_toc.rows[r_i].cells[c_i].paragraphs[0].runs[0].font.bold = True
        set_cell_margins(tbl_toc.rows[r_i].cells[c_i], top=40, bottom=40)

for row in tbl_toc.rows:
    for cell in row.cells:
        for p in cell.paragraphs:
            p.paragraph_format.line_spacing = 1.15
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(10)

doc.add_page_break()

# ----------------- 1. INTRODUCTION -----------------
add_heading_1('1. INTRODUCTION')
add_subheading('1.1 Background and Context')
add_body_p('Agriculture serves as the foundation of global food security and economic stability. However, contemporary farming is confronted with formidable challenges: escalating chemical input costs, severe labor shortages, environmental toxicity, and chronic soil degradation. In traditional farming practices, pest management and fertilizer application rely primarily on uniform, blanket broadcasting across entire fields using tractor-mounted sprayers or manual backpack sprayers. These methods distribute identical dosages across infested and healthy plants alike, leading to up to 70–80% chemical wastage, profound chemical leaching into groundwater systems, and serious occupational health hazards for farm workers.')
add_body_p('The convergence of the Internet of Things (IoT), edge computer vision, embedded robotics, and browser-based 3D digital twins introduces a potent solution: Precision Agriculture. By deploying compact, intelligent Unmanned Ground Vehicles (UGVs) directly within crop rows, farming operations can achieve plant-level monitoring and remediation, vastly improving resource efficiency.')

add_subheading('1.2 Project Overview: Agri Rover')
add_body_p('Agri Rover is a cyber-physical, autonomous agricultural robotic vehicle designed for localized precision crop care and in-situ soil analysis. The system combines real-time computer vision threat detection (OpenCV), automated micro-burst chemical dispensing (solenoid valves), and automated electrochemical ground soil probing (NPK, pH, and moisture). Furthermore, to eliminate the severe operational and financial risks associated with early-stage field algorithm testing, Agri Rover incorporates a high-fidelity 3D WebGL Digital Twin Simulator built using React and Three.js. This virtual twin operates with exact kinematic skid-steer physics, zero-radius point turns, row lane-lock enforcement, and real-time telemetry streaming, enabling safe, accessible, and zero-cost algorithm prototyping prior to physical hardware deployment.')

# ----------------- 2. LITERATURE SURVEY -----------------
add_heading_1('2. LITERATURE SURVEY')
add_subheading('2.1 Review of State-of-the-Art Solutions')
add_body_p('A thorough investigation of existing crop management platforms and autonomous agricultural robotics literature was conducted to assess technical strengths and operational limitations:')
add_bullet_p('Zhang and Pierce (2018) documented that tractor boom sprayers dominate large-scale farming but suffer from non-selective chemical broadcasting, significant soil compaction, high fuel costs, and total inability to collect localized soil health metrics.', '1. Conventional Mechanical Sprayers: ')
add_bullet_p('Aerial UAV systems offer high-speed broad-acre coverage; however, aerodynamic downwash causes substantial pesticide drift, battery run-times are strictly limited (15–20 minutes), and aerial optics cannot penetrate dense sub-canopy foliage or execute direct physical ground soil probing.', '2. Aerial UAV Sprayers: ')
add_bullet_p('Monolithic commercial UGVs (e.g., John Deere See & Spray) offer plant-level AI targeting but rely on proprietary software stacks, cost upwards of $50,000, and lack accessible digital twin simulation environments suitable for smallholder farmers or academic research.', '3. Commercial Autonomous UGVs: ')
add_bullet_p('Recent research in edge computing confirms that localized HSV color masking and lightweight visual thresholding running on single-board computers (Raspberry Pi) can accurately isolate foliar anomalies with sub-second latency, enabling micro-burst solenoid spraying.', '4. Edge Computer Vision & Sensing: ')

add_subheading('2.2 Comparative Summary: Existing Systems vs. Proposed Agri Rover')
add_table_caption('Table No: 3. Comparative Analysis of Existing Systems vs. Proposed Agri Rover')

tbl_comp = doc.add_table(rows=6, cols=4)
tbl_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
headers_comp = ['Feature / Parameter', 'Tractor Boom Sprayer', 'Agricultural Aerial Drone', 'Agri Rover (Proposed)']
for i, h in enumerate(headers_comp):
    tbl_comp.rows[0].cells[i].text = h
    set_cell_shading(tbl_comp.rows[0].cells[i], 'E2E8F0')
    tbl_comp.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True

comp_data = [
    ('Chemical Dispensing Mode', 'Uniform blanket broadcast (High waste)', 'Aerial spray broadcast (High wind drift)', 'Targeted AI micro-bursts (Up to 80% chemical saved)'),
    ('Soil Nutrient Analysis', 'None (Requires manual lab testing)', 'None (Cannot physically probe soil)', 'Automated motorized linear actuator NPK/pH/moisture probe'),
    ('Operating Environment', 'Open broad-acres (Causes soil compaction)', 'High-altitude canopy overview', 'Direct crop-row sub-canopy navigation (Skid-steer 4WD)'),
    ('Virtual Digital Twin Testing', 'Unavailable / Proprietary', 'Expensive commercial flight simulators', 'Zero-cost browser-based 3D WebGL Digital Twin (Three.js)'),
    ('Operator Safety & Cost', 'High chemical exposure & high fuel cost', 'Risk of crash damage & high hardware cost', 'Zero direct chemical exposure, low-cost electric Pi hardware')
]

for r_i, row in enumerate(comp_data):
    for c_i, val in enumerate(row):
        tbl_comp.rows[r_i+1].cells[c_i].text = val

for row in tbl_comp.rows:
    for cell in row.cells:
        set_cell_margins(cell, top=50, bottom=50)
        for p in cell.paragraphs:
            p.paragraph_format.line_spacing = 1.15
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(9.5)

# ----------------- 3. PROBLEM STATEMENT & OBJECTIVES -----------------
add_heading_1('3. PROBLEM STATEMENT WITH AIM AND OBJECTIVES')
add_subheading('3.1 Problem Statement')
add_body_p('Conventional agricultural spraying relies predominantly on indiscriminate, blanket chemical broadcasting across entire fields. This practice leads to severe agrochemical overuse, wasting up to 80% of applied chemicals, polluting groundwater ecosystems, degrading beneficial soil microbiomes, and exposing farm operators to acute health risks. Furthermore, small-to-medium scale farmers lack accessible, affordable tools to continuously monitor localized soil nutrients (NPK and pH) and are unable to validate autonomous robotics algorithms without high physical deployment risks and equipment costs.')

add_subheading('3.2 Project Aim')
add_body_p('To design, develop, and evaluate "Agri Rover" — an intelligent, cyber-physical autonomous IoT robotic vehicle coupled with a real-time 3D WebGL Digital Twin, delivering precision computer vision-guided targeted pesticide micro-bursts, automated in-situ soil nutrient probing, and zero-risk virtual simulation.')

add_subheading('3.3 Project Objectives')
add_bullet_p('Design and fabricate a rugged, 4-wheel skid-steer robotic chassis powered by high-torque DC geared motors and dual BTS7960 H-bridge drivers capable of navigating narrow crop rows with zero-radius turning capability.', '1. Autonomous Chassis Development: ')
add_bullet_p('Implement an edge computer vision pipeline using OpenCV on a Raspberry Pi 4 to detect foliar weeds and biological pests (caterpillars) in real time and compute spatial pixel offsets for localized actuation.', '2. Computer Vision AI Threat Detection: ')
add_bullet_p('Integrate a precision liquid chemical dispensing subsystem featuring 12V solenoid valves capable of directional micro-burst bursts directly at detected threats, achieving up to 80% reduction in chemical volume.', '3. Precision Micro-Burst Actuation: ')
add_bullet_p('Develop a motorized linear actuator soil testing probe with NPK, pH, and soil moisture sensors that automatically records georeferenced soil health metrics into an operational dashboard heatmap.', '4. In-Situ Soil Health Probing: ')
add_bullet_p('Build an interactive, browser-based 3D WebGL Digital Twin using React and Three.js for real-time telemetry streaming, algorithm validation, and remote manual teleoperation with comprehensive hardware safety fail-safes (battery voltage under-voltage cutoff <= 12.0V).', '5. 3D Digital Twin & Telemetry Dashboard: ')

# ----------------- 4. SDG ALIGNMENT -----------------
add_heading_1('4. SDG ALIGNMENT')
add_subheading('4.1 UN Sustainable Development Goals (SDG) Alignment')
add_body_p('The Agri Rover project is directly aligned with United Nations Sustainable Development Goals, specifically addressing sustainable farming, chemical management, and terrestrial ecosystem health:')
add_bullet_p('Target 2.4 mandates sustainable food production systems and resilient agricultural practices that increase productivity while progressively improving soil quality. Agri Rover advances this target through precision micro-spraying and automated NPK soil testing that preserves soil vitality and prevents land degradation.', '• Primary Alignment: SDG 2 — Zero Hunger (Target 2.4, Indicator 2.4.1): ')
add_bullet_p('Target 12.4 focuses on the environmentally sound management of chemicals to significantly reduce their release to air, water, and soil. Agri Rover reduces pesticide volume by up to 80%, substantially cutting chemical runoff into agricultural water basins.', '• Secondary Alignment: SDG 12 — Responsible Consumption & Production (Target 12.4): ')
add_bullet_p('By replacing blanket broad-spectrum chemical saturation with pinpoint micro-bursts and tracking soil pH/moisture, Agri Rover mitigates soil acidification and protects subterranean microbial biomes.', '• Ecosystem Alignment: SDG 15 — Life on Land: ')

add_subheading('4.2 ESG Compliance Summary')
add_table_caption('Table No: 4. Environmental, Social, and Governance (ESG) Framework Mapping')

tbl_esg = doc.add_table(rows=4, cols=3)
tbl_esg.alignment = WD_TABLE_ALIGNMENT.CENTER
headers_esg = ['ESG Pillar', 'Project Contribution', 'Supporting Evidence / Verification']
for i, h in enumerate(headers_esg):
    tbl_esg.rows[0].cells[i].text = h
    set_cell_shading(tbl_esg.rows[0].cells[i], 'E2E8F0')
    tbl_esg.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True

esg_rows = [
    ('Environmental (E)', 'Reduces pesticide consumption by up to 80% via targeted micro-bursts; clean 12V battery power eliminates tractor diesel emissions; prevents over-fertilization via soil NPK sensing.', 'Empirical chemical volume comparative test logs; battery discharge telemetry graphs; soil NPK sensor heatmaps.'),
    ('Social (S)', 'Eliminates direct human inhalation and skin contact with toxic pesticides via remote teleoperation; empowers smallholder farmers with an intuitive, low-cost automation platform.', 'Remote teleoperation latency logs (<50ms response); UI accessibility testing notes; agricultural hazard mitigation analysis.'),
    ('Governance (G)', 'Incorporates strict hardware safety interlocks (automatic emergency halt at battery <=12.0V); open-source, modular Python/Three.js architecture with complete auditability and version control.', 'Unit Test logs (UT-01 to UT-06); Git repository commit history; circuit wiring safety documentation.')
]
for r_i, row in enumerate(esg_rows):
    for c_i, val in enumerate(row):
        tbl_esg.rows[r_i+1].cells[c_i].text = val

for row in tbl_esg.rows:
    for cell in row.cells:
        set_cell_margins(cell, top=50, bottom=50)
        for p in cell.paragraphs:
            p.paragraph_format.line_spacing = 1.15
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(9.5)

# ----------------- 5. METHODOLOGY -----------------
add_heading_1('5. METHODOLOGY')
add_subheading('5.1 Cyber-Physical Architecture & System Workflow')
add_body_p('The methodology of Agri Rover is structured around a modular, event-driven cyber-physical framework spanning four tightly coupled functional layers:')
add_bullet_p('The perception node captures real-time 1080p video feed from the forward camera. The onboard OpenCV pipeline transforms frames into HSV color space, filters background noise via morphological operations, extracts crop row guidelines using Hough Line Transforms, and segments pest/weed color anomalies.', '1. Sensory Perception & AI Threat Detection: ')
add_bullet_p('The Raspberry Pi 4 processes visual bounding boxes and calculates horizontal spatial offsets from the rover centerline. Proportional control routines adjust pulse-width modulated (PWM) signals sent to the BTS7960 motor drivers to maintain crop-row centering, while steering differential motor speeds.', '2. Edge Navigation & Proportional Steering: ')
add_bullet_p('When a threat is confirmed with confidence above threshold, the system triggers the corresponding directional 12V solenoid valve via GPIO relay circuits for a calibrated 200ms micro-burst. During stationary soil sampling, the drive motors are immobilized, and a linear actuator drives the NPK/pH probe into the soil bed.', '3. Precision Chemical & Probe Actuation: ')
add_bullet_p('The React/Three.js client runs an exact WebGL 3D model of the rover and farmland environment. Bi-directional telemetry communicates rover position, battery voltage, active spray status, and georeferenced soil readings, rendering real-time heatmaps.', '4. Digital Twin Simulation & Telemetry: ')

add_subheading('5.2 System Data Flow Pipeline')
add_body_p('The end-to-end data pipeline functions as a continuous feedback loop: Camera Frame -> OpenCV Preprocessing -> HSV Color Segmentation -> Threat Bounding Box -> Spatial Offset Computation -> Directional Solenoid Valve Trigger / Motor Speed Compensation -> Telemetry Log -> 3D WebGL Digital Twin Dashboard.')
add_fig_caption('Fig. No: 1. End-to-End Cyber-Physical System Pipeline of Agri Rover')

# ----------------- 6. MODULES IDENTIFIED -----------------
add_heading_1('6. MODULES IDENTIFIED')
add_subheading('6.1 Functional System Modules')
add_body_p('The Agri Rover architecture is partitioned into six cohesive, loosely coupled functional modules:')
add_bullet_p('Controls skid-steer differential locomotion using 4 DC geared motors and dual BTS7960 43A H-bridge motor drivers. Implements forward, reverse, proportional row steering, and zero-radius point turns with selectable speed presets (30%, 60%, 100% PWM).', 'Module 1: Chassis Locomotion & Motor Driver: ')
add_bullet_p('Processes camera stream in real time using OpenCV. Executes HSV color thresholding (purple mask for biological pests like caterpillars, red mask for invasive weeds) and Hough line detection for crop row guidance.', 'Module 2: Computer Vision Threat Detection: ')
add_bullet_p('Controls a 12V DC diaphragm chemical pump and dual directional solenoid valves. Supports Option 1 (continuous blanket coverage) and Option 2 (OpenCV-guided precision micro-burst targeted actuation).', 'Module 3: Precision Chemical Spraying Subsystem: ')
add_bullet_p('Orchestrates a motorized linear actuator carrying electrochemical NPK, pH, and soil moisture probes. Automatically immobilizes rover drive motors during deployment and logs georeferenced soil data.', 'Module 4: Soil Nutrient & NPK Probing: ')
add_bullet_p('Renders a real-time 3D simulation of the rover, agricultural field, crop rows, and particle mist effects using React.js, Three.js, and WebGL with OrbitControls navigation and telemetry widgets.', 'Module 5: 3D WebGL Digital Twin & Telemetry Dashboard: ')
add_bullet_p('Continuously monitors 12V supply voltage. If simulated/actual battery drops below 12.0V (<=12%), an automatic emergency halt is asserted, cutting motor PWM and closing all chemical valves to prevent brownouts.', 'Module 6: Power Management & Safety Fail-Safe: ')

# ----------------- 7. TOOLS AND TECHNOLOGIES IDENTIFIED -----------------
add_heading_1('7. TOOLS AND TECHNOLOGIES IDENTIFIED')
add_subheading('7.1 Hardware Stack')
add_bullet_p('Central onboard embedded computer running 64-bit Raspberry Pi OS, executing Python controllers, GPIO interfacing, and OpenCV processing.', '• Raspberry Pi 4 Model B (4GB RAM): ')
add_bullet_p('High-power H-bridge drivers capable of handling up to 43A continuous load for robust 4-wheel skid-steer drive control under high field torque.', '• Dual BTS7960 Motor Drivers: ')
add_bullet_p('12V DC normally closed fast-acting valves (response time <50ms) for high-pressure directional chemical micro-bursts.', '• 12V Solenoid Actuation Valves & Diaphragm Pump: ')
add_bullet_p('Motorized 100mm stroke actuator with integrated electrochemical NPK, pH, and capacitive soil moisture probes.', '• Linear Actuator & Soil Sensor Array: ')
add_bullet_p('Rechargeable 12V 7Ah sealed lead-acid / LiFePO4 battery pack with LM2596 buck converters providing stable 5V rail for Raspberry Pi logic.', '• Power Subsystem: ')

add_subheading('7.2 Software & Framework Stack')
add_bullet_p('Primary language for embedded robotics scripts, video frame processing, and hardware control.', '• Python 3.10+: ')
add_bullet_p('Open-source computer vision library for color space transformations, morphological filtering, and spatial contour extraction.', '• OpenCV 4.x & NumPy: ')
add_bullet_p('Low-level Python library for software PWM generation and GPIO pin signal toggling.', '• RPi.GPIO: ')
add_bullet_p('JavaScript 3D rendering library utilizing WebGL to deliver the interactive browser-based digital twin without external plugins.', '• Three.js (v0.128.0) & WebGL: ')
add_bullet_p('Component-driven web framework for telemetry widgets, WASD teleoperation event handlers, and simulation overlays.', '• React.js (HTML5 / CSS3 / ES6+): ')
add_bullet_p('Git and GitHub for collaborative version control, issue tracking, and automated documentation.', '• Version Control: ')

# ----------------- 8. TIMELINE USING GANTT CHART -----------------
add_heading_1('8. TIMELINE USING GANTT CHART')
add_subheading('8.1 Project Schedule and Milestones (Phase-I and Phase-II)')
add_body_p('The project lifecycle spans across two academic semesters, organized into six structured phases from conceptual design to field validation:')
add_table_caption('Table No: 5. Project Implementation Timeline and Milestone Schedule')

tbl_gantt = doc.add_table(rows=7, cols=7)
tbl_gantt.alignment = WD_TABLE_ALIGNMENT.CENTER
headers_gantt = ['Phase / Milestone Activity', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6']
for i, h in enumerate(headers_gantt):
    tbl_gantt.rows[0].cells[i].text = h
    set_cell_shading(tbl_gantt.rows[0].cells[i], 'E2E8F0')
    tbl_gantt.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True

gantt_data = [
    ('Phase 1: Literature Survey & Problem Definition', '[XXXX]', '      ', '      ', '      ', '      ', '      '),
    ('Phase 2: SRS, System Design & Architecture', '      ', '[XXXX]', '      ', '      ', '      ', '      '),
    ('Phase 3: Digital Twin 3D Simulator (WebGL / Three.js)', '      ', '[XXXX]', '[XXXX]', '      ', '      ', '      '),
    ('Phase 4: Hardware Assembly & Motor Driver Interfacing', '      ', '      ', '[XXXX]', '[XXXX]', '      ', '      '),
    ('Phase 5: OpenCV Threat Vision & Solenoid Integration', '      ', '      ', '      ', '[XXXX]', '[XXXX]', '      '),
    ('Phase 6: In-Situ Soil Probing, Testing & Final Report', '      ', '      ', '      ', '      ', '[XXXX]', '[XXXX]')
]

for r_i, row in enumerate(gantt_data):
    for c_i, val in enumerate(row):
        cell = tbl_gantt.rows[r_i+1].cells[c_i]
        cell.text = val
        if '[XXXX]' in val:
            set_cell_shading(cell, 'CBD5E1')
            cell.paragraphs[0].runs[0].font.bold = True

for row in tbl_gantt.rows:
    for cell in row.cells:
        set_cell_margins(cell, top=40, bottom=40)
        for p in cell.paragraphs:
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(9.5)

# References
add_heading_1('9. REFERENCES')
refs = [
    'Zhang, Q., & Pierce, F. J. (2018). Precision Agriculture Technology for Crop Farming. CRC Press, Taylor & Francis Group.',
    'Raspberry Pi Foundation. (2024). Raspberry Pi 4 Model B Hardware & RPi.GPIO Documentation. https://www.raspberrypi.com/documentation/',
    'OpenCV Team. (2024). OpenCV Image Processing and Computer Vision Reference Manual (Version 4.x). https://docs.opencv.org/',
    'Mrdoob. (2024). Three.js JavaScript 3D Library Documentation (v0.128.0). https://threejs.org/docs/',
    'United Nations. (2023). Sustainable Development Goals: Goal 2 (Zero Hunger) & Goal 12 (Responsible Consumption and Production). https://sdgs.un.org/goals'
]
for ref in refs:
    add_bullet_p(ref)

doc.save('Agri_Rover_Phase1_Synopsis.docx')
print('Agri_Rover_Phase1_Synopsis.docx created successfully!')
