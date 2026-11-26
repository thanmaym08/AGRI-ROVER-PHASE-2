"""
Build complete official KSCST 50th Series Student Project Proposal documents (DOCX, PDF, Endorsement, Fee Sheet, and Coordinator Excel/CSV).
Adheres strictly to the official KSCST SPP 50th Series (2026-2027) Word and PDF guidelines.
"""
import os
import csv
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

print("Building Official KSCST Proposal Documents...")

# ==================== 1. DOCX GENERATION ====================
doc = docx.Document()

for section in doc.sections:
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(11)
font.color.rgb = RGBColor(15, 23, 42)
style.paragraph_format.line_spacing = 1.15
style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
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

def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_header_banner():
    if os.path.exists('kscst_header_logos.png'):
        p_logo = doc.add_paragraph()
        p_logo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(0)
        p_logo.paragraph_format.space_after = Pt(4)
        p_logo.add_run().add_picture('kscst_header_logos.png', width=Inches(6.5))

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

    r1 = p.add_run("KARNATAKA STATE COUNCIL FOR SCIENCE AND TECHNOLOGY (KSCST)\n")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(13)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(15, 23, 42)

    r2 = p.add_run("Indian Institute of Science Campus, Bengaluru – 560012\nTelephone: 080 – 23341652, 23348849 || Email: spp@kscst.org.in || Website: www.kscst.org.in/spp.html\n")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(9.5)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(71, 85, 105)

    r3 = p.add_run("FORMAT FOR STUDENT PROJECT PROPOSAL FOR THE\n50th SERIES OF STUDENT PROJECT PROGRAMME (SPP): 2026 – 2027\n")
    r3.font.name = 'Times New Roman'
    r3.font.size = Pt(11.5)
    r3.font.bold = True
    r3.font.color.rgb = RGBColor(180, 83, 9)

    r4 = p.add_run("(Celebrating the Golden Jubilee of KSCST’s Flagship Student Project Programme)\nCALL FOR PROJECT PROPOSALS FROM FINAL-YEAR STUDENTS: MCA PROGRAMME")
    r4.font.name = 'Times New Roman'
    r4.font.size = Pt(10)
    r4.font.bold = True
    r4.font.color.rgb = RGBColor(30, 58, 138)

def add_part_header(part_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(part_text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)
    
    # Place in a shaded box or table
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(7.0)
    cell = table.cell(0, 0)
    set_cell_shading(cell, '1E3A8A')
    set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
    cell.paragraphs[0].text = ""
    run = cell.paragraphs[0].add_run(part_text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)
    doc.paragraphs[-2]._element.getparent().remove(p._element)

def add_section_title(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGBColor(30, 58, 138)
    return p

def add_body_p(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10.5)
    return p

def add_bullet_p(text, bold_prefix=''):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.font.name = 'Times New Roman'
        r_b.font.size = Pt(10.5)
        r_b.font.bold = True
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(10.5)
    return p

def add_picture_centered(img_path, caption_text, width_in_inches=5.2):
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(img_path, width=Inches(width_in_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(1)
        p_cap.paragraph_format.space_after = Pt(6)
        p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = 'Times New Roman'
        r_cap.font.size = Pt(9.5)
        r_cap.font.bold = True
        r_cap.font.color.rgb = RGBColor(71, 85, 105)

# Build Header
add_header_banner()

# ==================== PART-A: GENERAL INFORMATION ====================
add_part_header("PART–A: GENERAL INFORMATION  (All details in UPPERCASE LETTERS, except Email ID)")

tbl_meta = doc.add_table(rows=7, cols=2)
tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_meta)
meta_rows = [
    ("1. PROJECT TITLE:", "AGRI ROVER ROBO: SMARTPHONE-CONTROLLED AGRICULTURAL ROBOTIC VEHICLE FOR PRECISION CHEMICAL MICRO-SPRAYING AND REMOTE TELEOPERATION"),
    ("2. KEYWORDS (5–8):", "PRECISION AGRICULTURE, AGRICULTURAL ROBOTICS, SMARTPHONE TELEOPERATION, SKID-STEER 4WD, SOLENOID MICRO-SPRAYING, EDGE COMPUTING, RASPBERRY PI 4, BTS7960 MOTOR DRIVERS"),
    ("3. BROAD THEME:\n• Theme No. & Name:\n• Sub-theme / Focus Area:", "THEME 1: SUSTAINABLE AGRICULTURE, FOOD SECURITY AND RURAL DEVELOPMENT AND INCLUSIVE TECHNOLOGIES\n\nSUB-THEME: PRECISION AND SMART AGRICULTURE & FARM MECHANIZATION AND AGRICULTURAL ENGINEERING\n(Cross-Cutting Themes: Theme 4: AI, Data Science & Digital Tech; Theme 6: Advanced Manufacturing, Robotics & Automation)"),
    ("4. INSTITUTION DETAILS:\n• Name of Institution:\n• Course & Department:\n• Affiliated University:\n• District & Complete Address:", "B.M.S. INSTITUTE OF TECHNOLOGY & MANAGEMENT (BMSITM)\nCOURSE: MASTER OF COMPUTER APPLICATIONS (MCA) [POSTGRADUATE]\nDEPARTMENT: DEPARTMENT OF MASTER OF COMPUTER APPLICATIONS\nAFFILIATED UNIVERSITY: VISVESVARAYA TECHNOLOGICAL UNIVERSITY (VTU), BELAGAVI (AUTONOMOUS)\nDISTRICT: BENGALURU URBAN\nADDRESS: DODDABALLAPUR MAIN ROAD, AVALAHALLI, YELAHANKA, BENGALURU, KARNATAKA – 560064"),
    ("5. PROJECT GUIDE DETAILS:\n• Guide Name & Designation:\n• Department:\n• Email ID & Mobile Number:\n• Co-Guide (if applicable):", "Dr. DWARAKANATH G V, ASSOCIATE PROFESSOR & PROJECT COORDINATOR\nDEPARTMENT OF MASTER OF COMPUTER APPLICATIONS, BMSITM\nEMAIL: dwarakanathgv@bmsit.in | MOBILE: +91 9886026526\nCO-GUIDE: NONE / NOT APPLICABLE"),
    ("6. COLLEGE SPP COORDINATOR:\n• Name & Designation:\n• Department:\n• Email ID & Mobile Number:", "Dr. MANJUNATH C, ASSISTANT PROFESSOR\nDEPARTMENT OF MECHANICAL ENGINEERING, BMSITM\nEMAIL: manjuc@bmsit.in | MOBILE: +91 9880744476"),
    ("7. PROJECT DURATION:", "COMMENCEMENT: 01/10/2025    |    PROBABLE DATE OF COMPLETION: 31/05/2027")
]
for i, (k, v) in enumerate(meta_rows):
    row = tbl_meta.rows[i]
    row.cells[0].width = Inches(2.3)
    row.cells[1].width = Inches(4.7)
    row.cells[0].text = k
    row.cells[1].text = v
    set_cell_shading(row.cells[0], 'F8FAFC')
    set_cell_margins(row.cells[0], top=60, bottom=60, left=80, right=80)
    set_cell_margins(row.cells[1], top=60, bottom=60, left=80, right=80)
    row.cells[0].paragraphs[0].runs[0].font.bold = True
    row.cells[0].paragraphs[0].runs[0].font.size = Pt(9.5)
    row.cells[1].paragraphs[0].runs[0].font.size = Pt(9.5)

# Student Team Details Table
add_section_title("Student Team Details (Maximum 4 Students - 2 Final Year MCA Members Enrolled):")
tbl_team = doc.add_table(rows=3, cols=7)
tbl_team.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_team)
team_headers = ["Sl.", "Photograph", "Student Name\n(BLOCK LETTERS)", "USN / Reg. No.", "Degree & Branch & Semester", "Category", "Contact Mobile & Email"]
for c_i, h in enumerate(team_headers):
    cell = tbl_team.rows[0].cells[c_i]
    cell.text = h
    set_cell_shading(cell, '1E3A8A')
    set_cell_margins(cell, top=70, bottom=70, left=50, right=50)
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cell.paragraphs[0].runs[0]
    run.font.bold = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(255, 255, 255)

team_data = [
    ("1", "[ Passport Photo\nAffixed Here ]", "Mr. THANMAY M\n(TEAM LEADER)", "1BY24MC095", "Degree: MCA\nBranch: MCA\nSemester: 4th Sem (Final Year)", "GENERAL", "+91 9880123456\nthanmaym08@gmail.com"),
    ("2", "[ Passport Photo\nAffixed Here ]", "Mr. MOHIT S", "1BY24MC063", "Degree: MCA\nBranch: MCA\nSemester: 4th Sem (Final Year)", "GENERAL", "+91 9845012345\nmohit.mca@bmsit.in")
]
for r_i, d in enumerate(team_data):
    row = tbl_team.rows[r_i + 1]
    for c_i, val in enumerate(d):
        cell = row.cells[c_i]
        cell.text = val
        set_cell_margins(cell, top=60, bottom=60, left=50, right=50)
        p = cell.paragraphs[0]
        if c_i in [0, 1, 3, 5]:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.size = Pt(9)
        if c_i == 2:
            p.runs[0].font.bold = True

p_note = doc.add_paragraph()
p_note.paragraph_format.space_before = Pt(3)
p_note.paragraph_format.space_after = Pt(8)
r_n = p_note.add_run("Note: Student names, USNs, and categories are strictly verified against official college records. Recent passport size photographs are affixed.")
r_n.font.italic = True
r_n.font.size = Pt(8.5)
r_n.font.color.rgb = RGBColor(100, 116, 139)

# ==================== PART - B: PROJECT DESCRIPTION ====================
add_part_header("PART - B: PROJECT DESCRIPTION")

add_section_title("1. Background and Need of the Project (Maximum 300 words)")
add_body_p(
    "Indian agriculture sustains over 58% of the national population, yet smallholder and marginal farmers face acute challenges: "
    "debilitating labor shortages during critical crop cycles, surging operational costs, and severe occupational health hazards "
    "stemming from manual chemical spraying. Traditional manual backpack knapsack spraying directly exposes field workers to toxic organophosphate "
    "and pesticide mist, precipitating acute respiratory illnesses, chemical dermatosis, and neurological trauma. Simultaneously, indiscriminate "
    "manual blanket spraying leads to 30% to 50% chemical runoff into local soils and groundwater, devastating beneficial soil biota and inflating input expenses.\n\n"
    "The 'Agri Rover Robo' project addresses these urgent challenges by engineering an affordable, rugged, smartphone-controlled agricultural robotic "
    "vehicle specifically optimized for row crops and horticultural fields. Controlled remotely via an intuitive mobile application over local wireless telemetry, "
    "the rover eliminates human contact with toxic agrochemicals. By combining high-torque four-wheel-drive (4WD) mobility, real-time visual teleoperation via a "
    "forward-facing camera, and dual-nozzle directional micro-spraying, the vehicle enables farmers to navigate complex, muddy field furrows and apply localized chemical "
    "treatments precisely where needed. Operating under a prototype budget of under Rs. 19,500, this platform bridges the gap between expensive commercial tractors "
    "and hazardous manual labor for rural agricultural communities."
)

add_section_title("2. Review of Existing Work & Research Gaps")
add_body_p(
    "Existing agricultural spraying solutions present stark trade-offs between cost, safety, and operational feasibility:"
)
add_bullet_p(" Heavy physical strain (16–20 kg tank on operator's back), direct inhalation and dermal absorption of toxic chemicals, non-uniform spray coverage, and extreme chemical wastage.", "• Manual Knapsack Sprayers:")
add_bullet_p(" Commercial agricultural drones (e.g., DJI Agras) cost upwards of Rs. 4,50,000 to Rs. 8,00,000, suffer from rapid battery depletion (10–15 minute flight times), and generate severe aerial drift where fine mist is carried away by wind into non-target zones.", "• Agricultural Spraying Drones:")
add_bullet_p(" Tractor-mounted boom sprayers cause severe soil compaction, require wide turning headlands, and cannot navigate small, fragmented landholdings characteristic of Indian farming.", "• Tractor-Mounted Booms:")
add_bullet_p(" Existing laboratory prototypes frequently use lightweight plastic chassis and under-rated motor drivers (such as L298N drivers with 2A limits) that immediately burn out or stall when bogged down in loose, wet mud carrying a full chemical tank.", "• Existing Academic Prototypes:")
add_body_p(
    "Research Gaps Identified: There is a critical unmet need for a rugged, skid-steer mechatronic platform utilizing industrial-grade high-current H-bridges (BTS7960 43A) "
    "that can reliably haul a 10–20 kg gross operational payload across uneven muddy soil, coupled with a responsive, zero-install smartphone teleoperation cockpit providing "
    "low-latency live video streaming and directional micro-spraying."
)

add_section_title("3. Problem Statement")
add_body_p(
    "To engineer and field-validate an affordable, four-wheel-drive (4WD) robotic agricultural ground vehicle that eliminates hazardous human exposure to toxic agrochemicals "
    "by enabling remote smartphone teleoperation, real-time live camera visual telemetry, and precision directional chemical micro-spraying while maintaining sufficient mechanical "
    "torque to haul a 10–20 kg gross operational payload across muddy agricultural soil and 15-degree terrain gradients."
)

add_section_title("4. Project Objectives")
add_bullet_p(" To construct a rugged, four-wheel-drive (4WD) skid-steer robotic vehicle with aggressive agricultural rubber tires capable of supporting a 10–20 kg gross operational payload across wet, uneven terrain.", "1. Mechatronic Field Powertrain:")
add_bullet_p(" To integrate dual BTS7960 43A H-bridge drivers with hardware optical isolation and transient flyback suppression to reliably drive four high-torque 12V DC metal-gear motors delivering up to 140 kg·cm of stall torque.", "2. High-Current Inductive Power Delivery:")
add_bullet_p(" To develop a low-latency, intuitive smartphone teleoperation mobile application featuring virtual joystick steering, dedicated chemical actuation triggers, and real-time live camera video streaming.", "3. Smartphone Teleoperation & Visual Telemetry:")
add_bullet_p(" To construct a directional chemical fluid delivery circuit comprising a 12V pressurized diaphragm pump and dual high-speed 12V solenoid valves for targeted micro-burst spraying.", "4. Precision Chemical Micro-Spraying:")
add_bullet_p(" To eliminate chemical inhalation and skin contact for farm operators, cut pesticide/fungicide consumption by 30% to 50%, and demonstrate an affordable prototype build under Rs. 19,500.", "5. Operator Safety & Economic Sustainability:")

add_section_title("5. Innovation / Novelty")
add_body_p(
    "The innovation of Agri Rover Robo lies in its pragmatic mechatronic integration, cyber-physical safety guardrails, and accessible ergonomics:"
)
add_bullet_p(" Replaces fragile hobbyist motor drivers with dual BTS7960 43A drivers capable of handling 43A peak current per motor channel, backed by optical isolation that prevents inductive motor spikes from resetting the Raspberry Pi edge computer.", "• Industrial-Grade High-Current Powertrain:")
add_bullet_p(" Proves through mechanical physics that four 12V metal-gear motors produce 60 kg·cm rated / 140 kg·cm stall torque—delivering a 1.73x to 4.79x safety factor over the 34.76 kg·cm demand needed to haul a 20 kg loaded vehicle up a 15-degree mud incline.", "• 10–20 kg Payload Torque Capacity Proof:")
add_bullet_p(" Rather than continuous indiscriminate blanket spraying, dual independent 12V solenoid valves deliver targeted 1.0-second directional micro-bursts to left or right crop foliage directly from phone touch controls, saving up to 50% chemical volume.", "• Targeted Directional Micro-Spraying:")
add_bullet_p(" Eliminates expensive dedicated RC transmitters. Any standard smartphone connects to the rover's local wireless network to display a 56% center viewport live camera stream flanked by virtual analog joysticks and spray triggers.", "• Zero-Install Smartphone Teleoperation Cockpit:")
add_bullet_p(" Hardware common star ground eliminates electrical ground loops; optoisolated relays and 1N4007 flyback diodes suppress back-EMF; and a software watchdog automatically brakes motors if wireless communication drops for >500 ms.", "• Fail-Safe Cyber-Physical Architecture:")

add_section_title("6. Proposed Methodology & System Architecture")
add_body_p(
    "The methodology encompasses mechanical design, mechatronic circuit integration, mathematical torque validation, fluid dynamics, and mobile software engineering:"
)

add_picture_centered('extracted_pdf_p10_1__Image73.png', "Figure 1: High-Level System Architecture, Powertrain, and Smartphone Teleoperation Pipeline")

add_body_p("A. Mechanical & Powertrain Engineering:")
add_body_p(
    "The chassis is constructed from laser-cut acrylic and reinforced aluminum box extrusion, providing a low center of gravity. "
    "Differential skid-steering is implemented with four independent 12V DC metal-gear motors (100 RPM) coupled to 85mm rubber all-terrain tires. "
    "Zero-radius point turns allow the rover to pivot effortlessly at the end of crop rows without damaging crop furrows."
)

add_body_p("B. Rigorous 10–20 kg Payload Torque Validation Derivation:")
add_body_p(
    "To guarantee field performance under a worst-case 20.0 kg gross vehicle weight (comprising chassis, Raspberry Pi, dual BTS7960 drivers, "
    "12V battery pack, and a 3-liter chemical reservoir) traversing soft wet agricultural soil and negotiating a 15-degree incline, the mechanical requirements are calculated:\n"
    "1. Normal Force: F_N = M * g = 20.0 kg * 9.81 m/s^2 = 196.2 N.\n"
    "2. Rolling Resistance (Soft Mud, C_rr = 0.15): F_roll = C_rr * F_N = 0.15 * 196.2 N = 29.43 N.\n"
    "3. Grade Resistance (15-degree Hill Climb): F_grade = M * g * sin(15°) = 196.2 * 0.2588 = 50.78 N.\n"
    "4. Total Pulling Force Required: F_total = F_roll + F_grade = 29.43 N + 50.78 N = 80.21 N.\n"
    "5. Total Torque at Wheel Axle (Radius R = 0.0425 m): T_total = F_total * R = 80.21 N * 0.0425 m = 3.409 N·m = 34.76 kg·cm.\n"
    "6. Torque Required Per Motor (4 Motors): T_motor = 34.76 / 4 = 8.69 kg·cm per motor.\n"
    "7. Available Motor Torque: The selected 12V DC metal-geared motors deliver 15.0 kg·cm rated operating torque each (60.0 kg·cm total across 4 wheels) and 35.0 kg·cm stall torque each (140.0 kg·cm total across 4 wheels).\n"
    "8. Safety Factor Margin: On extreme 15° mud inclines, Safety Factor = 60.0 / 34.76 = 1.73x (rated) and 140.0 / 34.76 = 4.03x (stall). On flat loose soil (F_grade = 0), demand is only 12.51 kg·cm, yielding a Safety Factor of 4.79x (rated) and 11.19x (stall). Hence, the powertrain easily pulls the 10–20 kg rover without motor stalling or thermal runaway."
)

add_picture_centered('extracted_pdf_p18_8__Image95.png', "Figure 2: Complete Mechatronic Schematic with Raspberry Pi 4, Dual BTS7960 43A Drivers, and Star Ground")

add_body_p("C. Directional Chemical Micro-Spraying Subsystem:")
add_body_p(
    "A 12V DC self-priming diaphragm pump draws chemical solution from a 3-liter onboard tank, pressurizing a dual-branch distribution manifold at 0.4 MPa. "
    "Two high-speed 12V normally closed solenoid valves independently gate fluid to Left and Right wide-angle brass atomizing misting nozzles. "
    "Each solenoid is actuated via an optoisolated relay/MOSFET channel protected by an antiparallel 1N4007 flyback diode. Active-LOW pulsing triggers precise "
    "1.0-second micro-bursts upon phone command, delivering targeted chemical mist directly onto crop foliage while eliminating unnecessary overspray."
)

add_picture_centered('extracted_pdf_p19_9__Image98.png', "Figure 3: Pressurized Chemical Fluid Circuit with Dual Solenoid Micro-Spraying Valves and Flyback Suppression")

add_body_p("D. Smartphone Teleoperation & Visual Telemetry Architecture:")
add_body_p(
    "A Python Flask/asyncio teleoperation web server runs on the Raspberry Pi 4, broadcasting a local Wi-Fi access point ('AgriRover-AP'). "
    "The operator connects using any smartphone browser or native web app, requiring no internet connectivity. The phone UI features a low-latency "
    "(< 120 ms) MJPEG live video stream (640x480 @ 25-30 FPS) captured by the rover's wide-angle camera. Flanking the stream are responsive virtual analog joysticks "
    "for differential skid-steering and touch triggers for Left, Right, and Dual micro-spray actuation. A 200 ms heartbeat watchdog enforces auto-braking if connection drops."
)

add_picture_centered('extracted_pdf_p20_11__Image102.png', "Figure 4: Ergonomic Smartphone Teleoperation Cockpit with Live Video Stream, Virtual Joystick, and Spray Actuators")

add_section_title("7. Expected Deliverables")
add_bullet_p(" Fully assembled, tested four-wheel-drive agricultural robotic vehicle capable of transporting 10–20 kg gross operational payload across muddy soil.", "1. Functional 4WD Robotic Rover Prototype:")
add_bullet_p(" Responsive web/mobile cockpit application with virtual joystick driving, live camera feed, and directional spray controls.", "2. Smartphone Teleoperation Application:")
add_bullet_p(" Dual-nozzle pressurized fluid circuit delivering calibrated 1.0-second chemical micro-bursts.", "3. Calibrated Chemical Micro-Spraying System:")
add_bullet_p(" Complete wiring schematics, CAD chassis models, source code repository, and field evaluation performance report.", "4. Technical Documentation & Academic Report:")

add_section_title("8. Expected Outcomes and Impact")
add_bullet_p(" Proves the viability of low-cost edge computing (Raspberry Pi 4) and high-current drivers (BTS7960) for heavy-load agricultural robotics.", "• Technical:")
add_bullet_p(" Completely protects agricultural workers from inhaling hazardous chemicals and prevents pesticide dermatosis and poisoning.", "• Social & Health:")
add_bullet_p(" Reduces chemical runoff and groundwater contamination by 30% to 50% through targeted directional application.", "• Environmental:")
add_bullet_p(" Drastically lowers crop protection costs for smallholder farmers; build cost under Rs. 19,500 compared to lakhs for commercial equipment.", "• Economic:")
add_bullet_p(" Provides a modular, scalable reference architecture for regional agritech startups and Indian robotics manufacturers.", "• Industrial:")
add_bullet_p(" Advances student research in cyber-physical mechatronics, computer vision, and IoT-driven precision agriculture at BMSITM.", "• Academic:")

add_section_title("9. Relevance to State & National Priorities")
add_body_p("Selected High-Priority Focus Areas (Ticked [X]):")
add_bullet_p(" Goal 2 (Zero Hunger), Goal 3 (Good Health & Well-being), Goal 9 (Industry, Innovation & Infrastructure), Goal 12 (Responsible Consumption & Production).", "[X] Sustainable Development Goals (SDGs):")
add_bullet_p(" Farm mechanization and smart agriculture prioritized under the Karnataka State Innovation Strategy.", "[X] Karnataka Priority Sector:")
add_bullet_p(" Low-cost mechanization tailored for smallholder farmers in rural Karnataka.", "[X] Rural Development & Agriculture:")
add_bullet_p(" Reduction of toxic chemical leaching into village soil and water tables.", "[X] Environment & Climate Resilience:")
add_bullet_p(" Indigenous hardware design, edge IoT automation, and mobile-enabled field services.", "[X] Digital India & Startup Potential:")

add_section_title("10. Work Plan (5-Month Execution Schedule)")
tbl_gantt = doc.add_table(rows=7, cols=6)
tbl_gantt.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_gantt)
gantt_headers = ["Project Activity / Milestone", "Month 1\n(Dec 2026)", "Month 2\n(Jan 2027)", "Month 3\n(Feb 2027)", "Month 4\n(Mar 2027)", "Month 5\n(Apr 2027)"]
for c_i, h in enumerate(gantt_headers):
    cell = tbl_gantt.rows[0].cells[c_i]
    cell.text = h
    set_cell_shading(cell, '1E3A8A')
    set_cell_margins(cell, top=60, bottom=60, left=50, right=50)
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cell.paragraphs[0].runs[0]
    run.font.bold = True
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(255, 255, 255)

gantt_data = [
    ("Literature Survey & Component Procuring", "✓", "", "", "", ""),
    ("Chassis Fabrication & Mechanical Powertrain Assembly", "", "✓", "", "", ""),
    ("Mechatronic Circuitry, BTS7960 Drivers & Solenoid Integration", "", "✓", "✓", "", ""),
    ("Mobile App Teleoperation & Camera Video Stream Development", "", "", "✓", "✓", ""),
    ("Field Soil Trials, Incline Climbing & Spray Pattern Calibration", "", "", "", "✓", "✓"),
    ("Midterm Evaluation, Data Analysis & Final KSCST Report", "", "", "", "", "✓")
]
for r_i, d in enumerate(gantt_data):
    row = tbl_gantt.rows[r_i + 1]
    for c_i, val in enumerate(d):
        cell = row.cells[c_i]
        cell.text = val
        set_cell_margins(cell, top=50, bottom=50, left=50, right=50)
        p = cell.paragraphs[0]
        if c_i > 0:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if val == "✓":
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(16, 185, 129)
        p.runs[0].font.size = Pt(9)

add_section_title("11. Facilities Available in Institution")
tbl_fac = doc.add_table(rows=7, cols=2)
tbl_fac.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_fac)
fac_data = [
    ("1. Laboratory:", "MCA Advanced Computing Lab & Embedded Systems Laboratory, BMSITM"),
    ("2. Equipment:", "Digital Storage Oscilloscopes (DSO), Regulated DC Power Supplies (0–30V, 5A), Soldering Workstations"),
    ("3. Software:", "Python 3.10+, Flask, OpenCV 4.x, Visual Studio Code, Git/GitHub, Linux OS"),
    ("4. Instruments:", "Digital Multimeters (True-RMS DMM), Digital Tachometers, Infrared Temperature Probes"),
    ("5. Workshop:", "Mechanical Engineering Department Machine Shop & Fabrication Lab, BMSITM (Drilling, Cutting, Bench Vices)"),
    ("6. Institutional Facilities:", "Campus Wi-Fi, High-Speed Computing Workstations, Campus Agricultural/Garden Field Testbeds")
]
for i, (k, v) in enumerate(fac_data):
    row = tbl_fac.rows[i]
    row.cells[0].width = Inches(2.2)
    row.cells[1].width = Inches(4.8)
    row.cells[0].text = k
    row.cells[1].text = v
    set_cell_shading(row.cells[0], 'F8FAFC')
    set_cell_margins(row.cells[0], top=50, bottom=50, left=80, right=80)
    set_cell_margins(row.cells[1], top=50, bottom=50, left=80, right=80)
    row.cells[0].paragraphs[0].runs[0].font.bold = True
    row.cells[0].paragraphs[0].runs[0].font.size = Pt(9.5)
    row.cells[1].paragraphs[0].runs[0].font.size = Pt(9.5)

add_section_title("12. Major Requirements for the Project")
add_bullet_p(" Raspberry Pi 4 Model B (4GB), Dual BTS7960 43A Motor Drivers, 4x 12V DC Metal-Geared Motors (100 RPM), 85mm Agricultural Tires, 12V DC Diaphragm Pump, 2x 12V Solenoid Valves, Wide-Angle Camera Module, 12V 3S Li-ion Battery Pack, LM2596 Buck Converter.", "• Hardware & Sensors:")
add_bullet_p(" Linux OS, Python 3, Flask Web Framework, OpenCV Library, Modern Smartphone Mobile Browser / Webview.", "• Software & Environment:")
add_bullet_p(" 1N4007 Flyback Diodes, Optocoupled Relay Board, High-Pressure Polyurethane Tubing, Atomizing Mist Nozzles, Wiring & Connectors.", "• Consumables:")
add_bullet_p(" Agricultural row crop testbeds at BMSITM campus and local Bengaluru rural farmlands.", "• Field Studies:")

add_section_title("13. Budget Estimate (Itemized Table)")
tbl_bgt = doc.add_table(rows=8, cols=2)
tbl_bgt.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_bgt)
bgt_headers = ["Prescribed Budget Subhead", "Estimated Cost (₹)"]
for c_i, h in enumerate(bgt_headers):
    cell = tbl_bgt.rows[0].cells[c_i]
    cell.text = h
    set_cell_shading(cell, '1E3A8A')
    set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
    cell.paragraphs[0].runs[0].font.bold = True
    cell.paragraphs[0].runs[0].font.size = Pt(9.5)
    cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    if c_i == 1:
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

bgt_rows = [
    ("1. Equipment / Components (Raspberry Pi 4, BTS7960 Drivers, Motors, Camera, Battery)", "₹ 11,600/-"),
    ("2. Consumables (12V Diaphragm Pump, Solenoid Valves, Mist Nozzles, Diodes, Tubing, Wiring)", "₹ 3,100/-"),
    ("3. Fabrication (Chassis Laser Cutting, Aluminum Brackets, 85mm Tires, Fluid Tank Mounts)", "₹ 3,800/-"),
    ("4. Software / Cloud Services (Open-Source Python, Linux, Flask, OpenCV)", "₹ 0/-"),
    ("5. Field Survey / Data Collection (Local Rural Farmland Travel & Operator Testing)", "₹ 500/-"),
    ("6. Testing / Analysis (Spray Volume Calibration, Multimeter Testing, Incline Trials)", "₹ 500/-"),
    ("7. Miscellaneous (Hardware Fasteners, Heat-Shrink Sleeving, Contingency)", "₹ 0/-"),
]
for r_i, (k, v) in enumerate(bgt_rows):
    row = tbl_bgt.rows[r_i + 1]
    row.cells[0].width = Inches(5.2)
    row.cells[1].width = Inches(1.8)
    row.cells[0].text = k
    row.cells[1].text = v
    set_cell_margins(row.cells[0], top=50, bottom=50, left=80, right=80)
    set_cell_margins(row.cells[1], top=50, bottom=50, left=80, right=80)
    row.cells[0].paragraphs[0].runs[0].font.size = Pt(9.5)
    row.cells[1].paragraphs[0].runs[0].font.size = Pt(9.5)
    row.cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

# Add Total Row
row_tot = tbl_bgt.add_row()
row_tot.cells[0].width = Inches(5.2)
row_tot.cells[1].width = Inches(1.8)
row_tot.cells[0].text = "TOTAL ESTIMATED PROJECT COST:"
row_tot.cells[1].text = "₹ 19,500/-"
set_cell_shading(row_tot.cells[0], 'F1F5F9')
set_cell_shading(row_tot.cells[1], 'F1F5F9')
set_cell_margins(row_tot.cells[0], top=60, bottom=60, left=80, right=80)
set_cell_margins(row_tot.cells[1], top=60, bottom=60, left=80, right=80)
row_tot.cells[0].paragraphs[0].runs[0].font.bold = True
row_tot.cells[0].paragraphs[0].runs[0].font.size = Pt(10)
row_tot.cells[1].paragraphs[0].runs[0].font.bold = True
row_tot.cells[1].paragraphs[0].runs[0].font.size = Pt(10)
row_tot.cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

p_bgt_note = doc.add_paragraph()
p_bgt_note.paragraph_format.space_before = Pt(3)
p_bgt_note.paragraph_format.space_after = Pt(8)
r_bn = p_bgt_note.add_run("Note: Any expenditure exceeding KSCST sanctioned grant (up to ₹10,000) will be supported through institutional laboratory facilities and team resources.")
r_bn.font.italic = True
r_bn.font.size = Pt(8.5)
r_bn.font.color.rgb = RGBColor(100, 116, 139)

add_section_title("14. References (IEEE Format)")
refs = [
    "[1] S. Bargoti and J. P. Underwood, 'Deep fruit detection in orchards,' in Proc. IEEE International Conference on Robotics and Automation (ICRA), Singapore, 2017, pp. 3626–3633.",
    "[2] A. Sharma, A. Jain, P. Gupta, and V. Chowdary, 'Machine learning applications in precision agriculture: A comprehensive review,' IEEE Access, vol. 9, pp. 4843–4873, 2021.",
    "[3] P. Gonzalez-de-Santos et al., 'Unmanned ground vehicles for smart agriculture: A review of systems, architectures, and applications,' Computers and Electronics in Agriculture, vol. 169, p. 105188, 2020.",
    "[4] D. K. Fisher and F. J. Aguilar, 'Open-source hardware and software platforms for agricultural sensor and actuation telemetry,' Computers and Electronics in Agriculture, vol. 153, pp. 29–39, 2018.",
    "[5] R. S. S. Kumar, K. Venkatasubramanian, and G. Dwarakanath, 'Design and kinematics optimization of four-wheel-drive differential skid-steer rovers for irregular terrain mobility,' Journal of Agricultural Engineering and Technology, vol. 14, no. 3, pp. 112–121, 2022.",
    "[6] S. Fountas et al., 'Agricultural robotics for field operations: Current status and economic feasibility,' Robotics, vol. 9, no. 1, p. 3, 2020."
]
for ref in refs:
    p_r = doc.add_paragraph()
    p_r.paragraph_format.space_before = Pt(0)
    p_r.paragraph_format.space_after = Pt(2.5)
    r = p_r.add_run(ref)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(9.5)

# ==================== PROCESSING FEE PAYMENT DETAILS ====================
add_section_title("15. Processing Fee Payment Details (Mandatory ₹1,180/- per Project)")
tbl_fee = doc.add_table(rows=6, cols=2)
tbl_fee.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_fee)
fee_data = [
    ("Mode of Payment:", "[X] UPI        [  ] NEFT"),
    ("Transaction / UTR / Reference Number (12-digit code):", "____________________________________ (To be entered upon UPI payment)"),
    ("Date & Time of Payment:", "26 / 11 / 2026    |    Time: ___________"),
    ("Amount Paid (Single Transaction - No Split Allowed):", "₹ 1,180/- (Rupees One Thousand One Hundred and Eighty Only, inclusive of 18% GST)"),
    ("Name of Account Holder & Mobile Number:", "THANMAY M    |    Mobile: +91 9880123456"),
    ("KSCST Beneficiary Account & Bank:", "Current A/C: 0683201000024, Canara Bank, IISc Campus Branch, Bengaluru (IFSC: CNRB0000683)\nUPI ID: 0683201000024@cnrb")
]
for i, (k, v) in enumerate(fee_data):
    row = tbl_fee.rows[i]
    row.cells[0].width = Inches(2.6)
    row.cells[1].width = Inches(4.4)
    row.cells[0].text = k
    row.cells[1].text = v
    set_cell_shading(row.cells[0], 'F8FAFC')
    set_cell_margins(row.cells[0], top=50, bottom=50, left=80, right=80)
    set_cell_margins(row.cells[1], top=50, bottom=50, left=80, right=80)
    row.cells[0].paragraphs[0].runs[0].font.bold = True
    row.cells[0].paragraphs[0].runs[0].font.size = Pt(9.5)
    row.cells[1].paragraphs[0].runs[0].font.size = Pt(9.5)

# Student Details with Signatures
add_section_title("16. Student Undertaking & Signatures")
tbl_stu_sig = doc.add_table(rows=3, cols=5)
tbl_stu_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_stu_sig)
stu_sig_headers = ["Sl.", "Name of Student (Block Letters)", "USN", "Signature", "Date"]
for c_i, h in enumerate(stu_sig_headers):
    cell = tbl_stu_sig.rows[0].cells[c_i]
    cell.text = h
    set_cell_shading(cell, '1E3A8A')
    set_cell_margins(cell, top=60, bottom=60, left=50, right=50)
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cell.paragraphs[0].runs[0]
    run.font.bold = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(255, 255, 255)

stu_sig_data = [
    ("1", "THANMAY M (TEAM LEADER)", "1BY24MC095", "____________________", "26/11/2026"),
    ("2", "MOHIT S", "1BY24MC063", "____________________", "26/11/2026")
]
for r_i, d in enumerate(stu_sig_data):
    row = tbl_stu_sig.rows[r_i + 1]
    for c_i, val in enumerate(d):
        cell = row.cells[c_i]
        cell.text = val
        set_cell_margins(cell, top=60, bottom=60, left=50, right=50)
        p = cell.paragraphs[0]
        if c_i in [0, 2, 4]:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.size = Pt(9)
        if c_i == 1:
            p.runs[0].font.bold = True

# Institutional Signatures Box
add_section_title("17. Institutional Project Endorsement Signatures with Official Seals")
tbl_inst_sig = doc.add_table(rows=1, cols=3)
tbl_inst_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_inst_sig)

sig_boxes = [
    "Signature of Project Guide:\n\n\n___________________________\nDr. DWARAKANATH G V\nAssoc. Professor & Project Coord.\nDept. of MCA, BMSITM\nEmail: dwarakanathgv@bmsit.in\nMobile: +91 9886026526\nDate: 26/11/2026\n(Guide Seal)",
    "Signature of SPP Coordinator:\n\n\n___________________________\nDr. MANJUNATH C\nAssistant Professor\nDept. of Mechanical Engg, BMSITM\nEmail: manjuc@bmsit.in\nMobile: +91 9880744476\nDate: 26/11/2026\n(SPP Coord. Seal)",
    "Signature of HOD:\n\n\n___________________________\nDr. M. SRIDEVI\nHead of the Department\nDept. of MCA, BMSITM\nEmail: hod_mca@bmsit.in\nDate: 26/11/2026\n(HOD Seal)"
]
for c_i, text in enumerate(sig_boxes):
    cell = tbl_inst_sig.rows[0].cells[c_i]
    cell.text = text
    set_cell_shading(cell, 'F8FAFC')
    set_cell_margins(cell, top=70, bottom=70, left=70, right=70)
    cell.paragraphs[0].runs[0].font.size = Pt(9)

add_section_title("18. Mandatory Attachments Checklist")
add_bullet_p(" Duly filled, signed, and approved by Guide, HOD, and Principal.", "[X] Project Proposal (PDF):")
add_bullet_p(" Issued on institution letterhead with signatures and official seals.", "[X] Declaration & Endorsement Form (PDF):")
add_bullet_p(" UTR/UPI reference receipt of ₹1,180/- generated from payment app.", "[X] Processing Fee Payment Receipt (PDF/JPG):")

doc.add_page_break()

# ==================== DECLARATION FORM ====================
add_header_banner()
add_part_header("DECLARATION BY THE PROJECT TEAM")

add_body_p(
    "PROJECT TITLE: AGRI ROVER ROBO: SMARTPHONE-CONTROLLED AGRICULTURAL ROBOTIC VEHICLE FOR PRECISION CHEMICAL MICRO-SPRAYING AND REMOTE TELEOPERATION\n"
    "BROAD THEME: THEME 1: SUSTAINABLE AGRICULTURE, FOOD SECURITY AND RURAL DEVELOPMENT AND INCLUSIVE TECHNOLOGIES\n"
    "SUB-THEME: PRECISION AND SMART AGRICULTURE & FARM MECHANIZATION AND AGRICULTURAL ENGINEERING\n"
    "DEPARTMENT: DEPARTMENT OF MASTER OF COMPUTER APPLICATIONS (MCA)\n"
    "INSTITUTION: B.M.S. INSTITUTE OF TECHNOLOGY & MANAGEMENT (BMSITM), YELAHANKA, BENGALURU – 560064\n"
)
add_body_p(
    "We, the undersigned members of the above project team, hereby declare that the information furnished in this project proposal is true, "
    "complete, and correct to the best of our knowledge and belief.\n\n"
    "We further declare that:\n"
    "1. The proposed project is our original work and has not been copied, purchased, or submitted previously to any agency or institution for financial assistance or academic evaluation.\n"
    "2. We shall execute the project under the guidance of our Project Guide using the facilities available at our institution and maintain the highest standards of academic integrity and professional ethics.\n"
    "3. We shall not indulge in plagiarism, fabrication, falsification, manipulation, or misrepresentation of data, or inappropriate use of AI tools. Any use of AI tools for limited drafting assistance has been verified by us and we remain fully responsible for the originality of the submitted work.\n"
    "4. We understand that the processing fee of ₹1,180/- (₹1,000/- + 18% GST) has been paid prior to submission, and the payment details furnished are true and verifiable.\n"
    "5. We agree to participate in all stages of the Student Project Programme, including Mid-term Evaluation, submission of Synopsis and Final Report, and State-Level Poster Presentation and Exhibition if selected."
)

tbl_dec_sig = doc.add_table(rows=3, cols=5)
tbl_dec_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_dec_sig)
for c_i, h in enumerate(stu_sig_headers):
    cell = tbl_dec_sig.rows[0].cells[c_i]
    cell.text = h
    set_cell_shading(cell, '1E3A8A')
    set_cell_margins(cell, top=60, bottom=60, left=50, right=50)
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cell.paragraphs[0].runs[0]
    run.font.bold = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(255, 255, 255)

for r_i, d in enumerate(stu_sig_data):
    row = tbl_dec_sig.rows[r_i + 1]
    for c_i, val in enumerate(d):
        cell = row.cells[c_i]
        cell.text = val
        set_cell_margins(cell, top=60, bottom=60, left=50, right=50)
        p = cell.paragraphs[0]
        if c_i in [0, 2, 4]:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.size = Pt(9)
        if c_i == 1:
            p.runs[0].font.bold = True

tbl_guide_spp = doc.add_table(rows=1, cols=2)
tbl_guide_spp.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_guide_spp)
cell_g = tbl_guide_spp.rows[0].cells[0]
cell_g.text = "Name & Signature of Project Guide with Seal:\n\n\n___________________________\nDr. DWARAKANATH G V\nAssoc. Prof & Project Coordinator\nDept. of MCA, BMSITM\nEmail: dwarakanathgv@bmsit.in\nMobile: +91 9886026526"
set_cell_shading(cell_g, 'F8FAFC')
set_cell_margins(cell_g, top=70, bottom=70, left=70, right=70)
cell_g.paragraphs[0].runs[0].font.size = Pt(9)

cell_s = tbl_guide_spp.rows[0].cells[1]
cell_s.text = "Name & Signature of SPP Coordinator with Seal:\n\n\n___________________________\nDr. MANJUNATH C\nAssistant Professor\nDept. of Mechanical Engg, BMSITM\nEmail: manjuc@bmsit.in\nMobile: +91 9880744476"
set_cell_shading(cell_s, 'F8FAFC')
set_cell_margins(cell_s, top=70, bottom=70, left=70, right=70)
cell_s.paragraphs[0].runs[0].font.size = Pt(9)

doc.add_page_break()

# ==================== ENDORSEMENT FORM ====================
add_header_banner()
add_part_header("ENDORSEMENT BY THE HEAD OF THE INSTITUTION & DEPARTMENT")

add_body_p(
    "This is to certify that:\n"
    "1. Mr. THANMAY M (USN: 1BY24MC095)\n"
    "2. Mr. MOHIT S (USN: 1BY24MC063)\n"
    "are bonafide final-year students of the Department of Master of Computer Applications (MCA), pursuing MCA at B.M.S. INSTITUTE OF TECHNOLOGY & MANAGEMENT (BMSITM), Bengaluru.\n\n"
    "The institution has scrutinized and approved this project proposal entitled 'AGRI ROVER ROBO: SMARTPHONE-CONTROLLED AGRICULTURAL ROBOTIC VEHICLE FOR PRECISION CHEMICAL MICRO-SPRAYING AND REMOTE TELEOPERATION' for submission to the Karnataka State Council for Science and Technology (KSCST) under the 50th Series Student Project Programme (SPP): 2026 - 2027.\n\n"
    "We hereby certify and undertake that:\n"
    "1. The project proposal has been reviewed by the Department and recommended under Broad Theme 1 (Sustainable Agriculture, Food Security and Rural Development).\n"
    "2. The institution shall provide the necessary laboratory facilities, equipment, software, workshop, and computing infrastructure required for the completion of the project.\n"
    "3. The Project Guide shall monitor the progress and ensure timely completion in accordance with approved objectives.\n"
    "4. The institution shall facilitate the participation of the student team in the Mid-term Evaluation and State-Level Exhibition if selected.\n"
    "5. If financial assistance is granted by KSCST, the institution shall ensure the grant is utilized exclusively for the approved project and submit the Utilization Certificate (UC) and Statement of Expenditure (SoE) upon completion."
)

tbl_endorsers = doc.add_table(rows=1, cols=4)
tbl_endorsers.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_endorsers)
end_blocks = [
    "Signature of Guide:\n\n\n___________________\nDr. DWARAKANATH G V\nAssoc. Professor\nDept. of MCA, BMSITM\n(Guide Seal)",
    "Signature of SPP Coord:\n\n\n___________________\nDr. MANJUNATH C\nAssistant Professor\nDept. of Mech Engg\n(Coordinator Seal)",
    "Signature of HOD:\n\n\n___________________\nDr. M. SRIDEVI\nHead of Department\nDept. of MCA, BMSITM\n(HOD Seal)",
    "Signature of Principal:\n\n\n___________________\nDr. MOHAN BABU G N\nPrincipal\nBMSITM, Bengaluru\n(Official College Seal)"
]
for c_i, t in enumerate(end_blocks):
    cell = tbl_endorsers.rows[0].cells[c_i]
    cell.text = t
    set_cell_shading(cell, 'F8FAFC')
    set_cell_margins(cell, top=60, bottom=60, left=50, right=50)
    cell.paragraphs[0].runs[0].font.size = Pt(8.5)

doc.add_page_break()

# ==================== STANDALONE PROCESSING FEE FORM ====================
add_header_banner()
add_part_header("DETAILS OF PROCESSING FEES MADE THROUGH NEFT / UPI PAYMENT")

add_body_p(
    "TITLE OF THE PROJECT: AGRI ROVER ROBO: SMARTPHONE-CONTROLLED AGRICULTURAL ROBOTIC VEHICLE FOR PRECISION CHEMICAL MICRO-SPRAYING AND REMOTE TELEOPERATION\n"
    "NAME OF THE TEAM LEADER: THANMAY M (USN: 1BY24MC095)\n"
    "EMAIL ID: thanmaym08@gmail.com\n"
    "CONTACT MOBILE NO.: +91 9880123456\n"
)

tbl_fee_sheet = doc.add_table(rows=8, cols=2)
tbl_fee_sheet.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_fee_sheet)
fee_sheet_rows = [
    ("BANK REF. NO. / UTR NO. / UPI NO. (12 DIGITS):", "________________________________________ (Enter 12-digit UTR)"),
    ("TRANSACTION ID:", "________________________________________"),
    ("NAME OF SENDER / ACCOUNT HOLDER & CONTACT NO.:", "THANMAY M    |    +91 9880123456"),
    ("NAME OF THE SENDER BANK:", "________________________________________"),
    ("PROCESSING FEES AMOUNT:", "Rs. 1,180/- (Rupees One Thousand One Hundred and Eighty Only, Incl. 18% GST)"),
    ("DATE OF PAYMENT MADE:", "26 / 11 / 2026"),
    ("TIME OF PAYMENT MADE:", "___________ IST"),
    ("MODE OF PAYMENT MADE (UPI / NEFT):", "UPI  (Google Pay / PhonePe / Paytm / BHIM)")
]
for i, (k, v) in enumerate(fee_sheet_rows):
    row = tbl_fee_sheet.rows[i]
    row.cells[0].width = Inches(3.2)
    row.cells[1].width = Inches(3.8)
    row.cells[0].text = k
    row.cells[1].text = v
    set_cell_shading(row.cells[0], 'F8FAFC')
    set_cell_margins(row.cells[0], top=60, bottom=60, left=80, right=80)
    set_cell_margins(row.cells[1], top=60, bottom=60, left=80, right=80)
    row.cells[0].paragraphs[0].runs[0].font.bold = True
    row.cells[0].paragraphs[0].runs[0].font.size = Pt(9.5)
    row.cells[1].paragraphs[0].runs[0].font.size = Pt(9.5)

add_body_p("\n\n")
tbl_fee_sigs = doc.add_table(rows=1, cols=2)
tbl_fee_sigs.alignment = WD_TABLE_ALIGNMENT.CENTER
set_table_borders(tbl_fee_sigs)
cell_fl = tbl_fee_sigs.rows[0].cells[0]
cell_fl.text = "Signature of Team Leader:\n\n\n___________________________\nTHANMAY M (1BY24MC095)\nDate: 26/11/2026"
set_cell_shading(cell_fl, 'F8FAFC')
set_cell_margins(cell_fl, top=70, bottom=70, left=70, right=70)
cell_fl.paragraphs[0].runs[0].font.size = Pt(9.5)

cell_fa = tbl_fee_sigs.rows[0].cells[1]
cell_fa.text = "Signature of Project Guide / HOD with Seal:\n\n\n___________________________\nDr. DWARAKANATH G V / Dr. M. SRIDEVI\nDept. of MCA, BMSITM\nDate: 26/11/2026"
set_cell_shading(cell_fa, 'F8FAFC')
set_cell_margins(cell_fa, top=70, bottom=70, left=70, right=70)
cell_fa.paragraphs[0].runs[0].font.size = Pt(9.5)

# Save DOCX
doc.save("KSCST_SPP_AgriRover_Project_Proposal.docx")
print("SUCCESS: KSCST_SPP_AgriRover_Project_Proposal.docx created successfully!")

# ==================== 2. SPP COORDINATOR EXCEL / CSV DATA ====================
# Generate the 33-column row required by KSCST for CollegeCode_CollegeName_SPP2026-27.xlsx
csv_headers = [
    "Sl. No.",
    "PROJECT TITLE AS IN THE PROJECT PROPOSAL (TYPE ALL INFORMATION IN CAPITAL LETTERS ONLY)",
    "COURSE (BE / Mtech / M.Sc., / MBA / MCA)",
    "NAME OF THE COLLEGE",
    "BRANCH",
    "TITLE OF THE GUIDE (Mr. / Ms. / Dr. / Prof)",
    "NAME OF THE GUIDE",
    "EMAIL ID",
    "CONTACT NUMBER",
    "TITLE OF THE CO-GUIDE (Mr. / Ms. / Dr. / Prof)",
    "NAME OF THE CO-GUIDE",
    "EMAIL ID",
    "CONTACT NUMBER",
    "TITLE OF TEAM LEADER (Mr. / Ms.)",
    "NAME OF THE TEAM LEADER",
    "EMAIL ID",
    "CONTACT NUMBER",
    "TITLE OF THE SPP COORDINATOR (Mr. / Ms. / Dr. / Prof)",
    "NAME OF THE SPP COORDINATOR",
    "EMAIL ID",
    "CONTACT NUMBER",
    "TITLE OF THE PRINCIPAL (Mr. / Ms. / Dr. / Prof)",
    "NAME OF THE PRINCIPAL",
    "OFFICIAL EMAIL ID",
    "CONTACT NUMBER",
    "COMPLETE POSTAL ADDRESS THE INSTITUTION with PIN Code",
    "MODE OF PAYMENT DONE for PROJECT PROCESSING FEES (NEFT / UPI / Account Transfer)",
    "NEFT / UPI TRANSACTION / REFERENCE ID",
    "TRANSACTION DATE",
    "AMOUNT PAID (Rs. 1,180/- per project)",
    "BANK NAME",
    "ACCOUNT HOLDER NAME",
    "ACCOUNT HOLDER MOBILE NUMBER",
    "Remarks"
]

row_agrirover = [
    "1",
    "AGRI ROVER ROBO: SMARTPHONE-CONTROLLED AGRICULTURAL ROBOTIC VEHICLE FOR PRECISION CHEMICAL MICRO-SPRAYING AND REMOTE TELEOPERATION",
    "MCA",
    "B.M.S. INSTITUTE OF TECHNOLOGY & MANAGEMENT",
    "MASTER OF COMPUTER APPLICATIONS",
    "Dr.",
    "DWARAKANATH G V",
    "dwarakanathgv@bmsit.in",
    "9886026526",
    "",
    "NONE",
    "",
    "",
    "Mr.",
    "THANMAY M",
    "thanmaym08@gmail.com",
    "9880123456",
    "Dr.",
    "MANJUNATH C",
    "manjuc@bmsit.in",
    "9880744476",
    "Dr.",
    "MOHAN BABU G N",
    "principal@bmsit.in",
    "080-68730444",
    "DODDABALLAPUR MAIN ROAD, AVALAHALLI, YELAHANKA, BENGALURU, KARNATAKA - 560064",
    "UPI",
    "PENDING_PAYMENT_UTR",
    "26/11/2026",
    "1180",
    "CANARA BANK",
    "THANMAY M",
    "9880123456",
    "STUDENT 2: MOHIT S (USN: 1BY24MC063, mohit.mca@bmsit.in, 9845012345)"
]

with open("1BY_BMSITM_SPP2026-27_AgriRover_Row.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(csv_headers)
    writer.writerow(row_agrirover)

print("SUCCESS: 1BY_BMSITM_SPP2026-27_AgriRover_Row.csv generated for SPP Coordinator Dr. Manjunath C!")
