"""
Generate all official KSCST SPP 50th Series PDFs adhering strictly to naming conventions and layout:
1. 01_Agri_Rover_Robo.pdf (and KSCST_SPP_AgriRover_Project_Proposal.pdf)
2. 02_Agri_Rover_Robo_declaration_endorsement.pdf (and KSCST_Declaration_and_Endorsement_Form.pdf)
3. 03_Agri_Rover_Robo_Processing_Fee.pdf (Standalone signed processing fee form)
4. 04_Agri_Rover_Robo_Payment_Receipt.pdf (Payment receipt proof & instructions)
"""
import os
import shutil
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, PageBreak
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Times-Roman", 8.5)
        self.setFillColor(colors.HexColor("#64748B"))
        # Header rule & title
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, A4[1] - 30, A4[0] - 40, A4[1] - 30)
        self.drawString(40, A4[1] - 25, "KSCST SPP 50th Series (2026–2027) | Proposal: Agri Rover Robo | Department of MCA, BMSITM")
        
        # Footer rule & page number
        self.line(40, 36, A4[0] - 40, 36)
        self.drawString(40, 24, "Confidential — Submitted for KSCST Student Project Programme Evaluation")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 40, 24, page_str)
        self.restoreState()

# Single-page canvas without running headers for standalone forms
class SinglePageCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont("Times-Roman", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 26, A4[0] - 36, 26)
        self.drawString(36, 16, "KSCST 50th Series SPP (2026–2027) | BMS Institute of Technology & Management (1BY)")
        self.drawRightString(A4[0] - 36, 16, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

styles = getSampleStyleSheet()

# Base paragraph styles
title_style = ParagraphStyle(
    'DocTitle',
    fontName='Times-Bold',
    fontSize=11.5,
    leading=14,
    alignment=1, # Center
    textColor=colors.HexColor("#0F172A")
)

sub_title_style = ParagraphStyle(
    'DocSubTitle',
    fontName='Times-Bold',
    fontSize=10,
    leading=13,
    alignment=1,
    textColor=colors.HexColor("#B45309")
)

part_style = ParagraphStyle(
    'PartHeader',
    fontName='Times-Bold',
    fontSize=10.5,
    leading=13,
    textColor=colors.white
)

sec_style = ParagraphStyle(
    'SectionHeader',
    fontName='Times-Bold',
    fontSize=10.5,
    leading=13,
    textColor=colors.HexColor("#1E3A8A"),
    spaceBefore=8,
    spaceAfter=3
)

body_style = ParagraphStyle(
    'BodyJustified',
    fontName='Times-Roman',
    fontSize=9.5,
    leading=12.5,
    alignment=4, # Justify
    textColor=colors.HexColor("#1E293B"),
    spaceAfter=4
)

body_bold = ParagraphStyle(
    'BodyBold',
    fontName='Times-Bold',
    fontSize=9.5,
    leading=12.5,
    textColor=colors.HexColor("#0F172A")
)

bullet_style = ParagraphStyle(
    'BulletText',
    fontName='Times-Roman',
    fontSize=9.5,
    leading=12.5,
    alignment=4,
    leftIndent=12,
    firstLineIndent=-12,
    textColor=colors.HexColor("#1E293B"),
    spaceAfter=2.5
)

table_text = ParagraphStyle(
    'TableText',
    fontName='Times-Roman',
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor("#0F172A")
)

table_bold = ParagraphStyle(
    'TableBold',
    fontName='Times-Bold',
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor("#0F172A")
)

table_header = ParagraphStyle(
    'TableHeader',
    fontName='Times-Bold',
    fontSize=8.5,
    leading=11,
    alignment=1,
    textColor=colors.white
)

fig_caption = ParagraphStyle(
    'FigCaption',
    fontName='Times-BoldItalic',
    fontSize=8.5,
    leading=11,
    alignment=1,
    textColor=colors.HexColor("#475569"),
    spaceBefore=2,
    spaceAfter=6
)

def make_part_banner(text, width=515):
    p = Paragraph(text, part_style)
    tbl = Table([[p]], colWidths=[width])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#1E3A8A")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return tbl

print("Generating 1. Full Proposal PDF (01_Agri_Rover_Robo.pdf)...")
pdf_path_1 = "01_Agri_Rover_Robo.pdf"
doc1 = SimpleDocTemplate(
    pdf_path_1,
    pagesize=A4,
    leftMargin=40,
    rightMargin=40,
    topMargin=42,
    bottomMargin=44
)

story1 = []

# Top Header Logos
if os.path.exists("kscst_header_logos.png"):
    story1.append(RLImage("kscst_header_logos.png", width=515, height=90))
    story1.append(Spacer(1, 4))

story1.append(Paragraph("KARNATAKA STATE COUNCIL FOR SCIENCE AND TECHNOLOGY (KSCST)", title_style))
story1.append(Paragraph("Indian Institute of Science Campus, Bengaluru – 560012", ParagraphStyle('SubSub', fontName='Times-Italic', fontSize=9, alignment=1, textColor=colors.HexColor("#475569"))))
story1.append(Paragraph("FORMAT FOR STUDENT PROJECT PROPOSAL FOR THE 50th SERIES OF SPP: 2026–2027", sub_title_style))
story1.append(Paragraph("(Celebrating the Golden Jubilee of KSCST’s Flagship Student Project Programme) — MCA PROGRAMME", ParagraphStyle('Sub3', fontName='Times-Bold', fontSize=9, alignment=1, textColor=colors.HexColor("#1E3A8A"))))
story1.append(Spacer(1, 6))

# PART-A
story1.append(make_part_banner("PART–A: GENERAL INFORMATION (All details in UPPERCASE LETTERS, except Email ID)"))
story1.append(Spacer(1, 4))

meta_table_data = [
    [Paragraph("<b>1. PROJECT TITLE:</b>", table_text), Paragraph("<b>AGRI ROVER ROBO: SMARTPHONE-CONTROLLED AGRICULTURAL ROBOTIC VEHICLE FOR PRECISION CHEMICAL MICRO-SPRAYING AND REMOTE TELEOPERATION</b>", table_bold)],
    [Paragraph("<b>2. KEYWORDS (5–8):</b>", table_text), Paragraph("PRECISION AGRICULTURE, AGRICULTURAL ROBOTICS, SMARTPHONE TELEOPERATION, SKID-STEER 4WD, SOLENOID MICRO-SPRAYING, EDGE COMPUTING, RASPBERRY PI 4, BTS7960 MOTOR DRIVERS", table_text)],
    [Paragraph("<b>3. BROAD THEME:</b><br/>• Theme No. &amp; Name:<br/>• Sub-theme / Focus Area:", table_text), Paragraph("<b>THEME 1: SUSTAINABLE AGRICULTURE, FOOD SECURITY AND RURAL DEVELOPMENT AND INCLUSIVE TECHNOLOGIES</b><br/><br/><b>SUB-THEME:</b> PRECISION AND SMART AGRICULTURE &amp; FARM MECHANIZATION AND AGRICULTURAL ENGINEERING<br/><i>(Cross-Cutting Themes: Theme 4: AI &amp; Digital Tech; Theme 6: Advanced Manufacturing &amp; Robotics)</i>", table_text)],
    [Paragraph("<b>4. INSTITUTION DETAILS:</b><br/>• Name of Institution:<br/>• Course &amp; Department:<br/>• Affiliated University:<br/>• District &amp; Address:", table_text), Paragraph("<b>B.M.S. INSTITUTE OF TECHNOLOGY &amp; MANAGEMENT (BMSITM)</b><br/>COURSE: MASTER OF COMPUTER APPLICATIONS (MCA) [POSTGRADUATE]<br/>DEPARTMENT: DEPARTMENT OF MASTER OF COMPUTER APPLICATIONS<br/>AFFILIATED UNIVERSITY: VISVESVARAYA TECHNOLOGICAL UNIVERSITY (VTU), BELAGAVI (AUTONOMOUS)<br/>DISTRICT: BENGALURU URBAN<br/>ADDRESS: DODDABALLAPUR MAIN ROAD, AVALAHALLI, YELAHANKA, BENGALURU, KARNATAKA – 560064", table_text)],
    [Paragraph("<b>5. PROJECT GUIDE DETAILS:</b><br/>• Guide Name &amp; Designation:<br/>• Department &amp; Institution:<br/>• Email ID &amp; Mobile Number:<br/>• Co-Guide (if applicable):", table_text), Paragraph("<b>Dr. DWARAKANATH G V</b>, ASSOCIATE PROFESSOR &amp; PROJECT COORDINATOR<br/>DEPARTMENT OF MASTER OF COMPUTER APPLICATIONS, BMSITM<br/>EMAIL: dwarakanathgv@bmsit.in | MOBILE: +91 9886026526<br/>CO-GUIDE: NONE / NOT APPLICABLE", table_text)],
    [Paragraph("<b>6. COLLEGE SPP COORDINATOR:</b><br/>• Name &amp; Designation:<br/>• Department:<br/>• Email ID &amp; Mobile Number:", table_text), Paragraph("<b>Dr. MANJUNATH C</b>, ASSISTANT PROFESSOR<br/>DEPARTMENT OF MECHANICAL ENGINEERING, BMSITM<br/>EMAIL: manjuc@bmsit.in | MOBILE: +91 9880744476", table_text)],
    [Paragraph("<b>7. PROJECT DURATION:</b>", table_text), Paragraph("COMMENCEMENT: 01/10/2025  |  PROBABLE COMPLETION: 31/05/2027 (5-Month SPP Phase: Dec 2026 – Apr 2027)", table_text)]
]
tbl_meta_pdf = Table(meta_table_data, colWidths=[150, 365])
tbl_meta_pdf.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
]))
story1.append(tbl_meta_pdf)
story1.append(Spacer(1, 6))

# Student Team Table
story1.append(Paragraph("<b>Student Team Details (Maximum 4 Students - 2 Final Year MCA Members Enrolled):</b>", sec_style))
team_pdf_data = [
    [Paragraph("Sl.", table_header), Paragraph("Photograph", table_header), Paragraph("Student Name (BLOCK LETTERS)", table_header), Paragraph("USN / Reg. No.", table_header), Paragraph("Degree &amp; Branch &amp; Semester", table_header), Paragraph("Category", table_header), Paragraph("Contact Mobile &amp; Email", table_header)],
    [Paragraph("1", table_text), Paragraph("[ Photo<br/>Affixed ]", table_text), Paragraph("<b>Mr. THANMAY M</b><br/>(TEAM LEADER)", table_text), Paragraph("1BY24MC095", table_text), Paragraph("Degree: MCA<br/>Branch: MCA<br/>Sem: 4th (Final Year)", table_text), Paragraph("GENERAL", table_text), Paragraph("+91 9880123456<br/>thanmaym08@gmail.com", table_text)],
    [Paragraph("2", table_text), Paragraph("[ Photo<br/>Affixed ]", table_text), Paragraph("<b>Mr. MOHIT S</b>", table_text), Paragraph("1BY24MC063", table_text), Paragraph("Degree: MCA<br/>Branch: MCA<br/>Sem: 4th (Final Year)", table_text), Paragraph("GENERAL", table_text), Paragraph("+91 9845012345<br/>mohit.mca@bmsit.in", table_text)]
]
tbl_team_pdf = Table(team_pdf_data, colWidths=[20, 50, 115, 65, 95, 45, 125])
tbl_team_pdf.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ('ALIGN', (3, 0), (3, -1), 'CENTER'),
    ('ALIGN', (5, 0), (5, -1), 'CENTER'),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
]))
story1.append(tbl_team_pdf)
story1.append(Spacer(1, 8))

# PART-B
story1.append(make_part_banner("PART - B: PROJECT DESCRIPTION"))
story1.append(Spacer(1, 4))

story1.append(Paragraph("<b>1. Background and Need of the Project (Maximum 300 words)</b>", sec_style))
story1.append(Paragraph(
    "Indian agriculture sustains over 58% of the national population, yet smallholder and marginal farmers face acute challenges: "
    "debilitating labor shortages during critical crop cycles, surging operational costs, and severe occupational health hazards "
    "stemming from manual chemical spraying. Traditional manual backpack knapsack spraying directly exposes field workers to toxic organophosphate "
    "and pesticide mist, precipitating acute respiratory illnesses, chemical dermatosis, and neurological trauma. Simultaneously, indiscriminate "
    "manual blanket spraying leads to 30% to 50% chemical runoff into local soils and groundwater, devastating beneficial soil biota and inflating input expenses.<br/><br/>"
    "The <b>Agri Rover Robo</b> project addresses these urgent challenges by engineering an affordable, rugged, smartphone-controlled agricultural robotic "
    "vehicle specifically optimized for row crops and horticultural fields. Controlled remotely via an intuitive mobile application over local wireless telemetry, "
    "the rover eliminates human contact with toxic agrochemicals. By combining high-torque four-wheel-drive (4WD) mobility, real-time visual teleoperation via a "
    "forward-facing camera, and dual-nozzle directional micro-spraying, the vehicle enables farmers to navigate complex, muddy field furrows and apply localized chemical "
    "treatments precisely where needed. Operating under a prototype budget of under Rs. 19,500, this platform bridges the gap between expensive commercial tractors "
    "and hazardous manual labor for rural agricultural communities.",
    body_style
))

story1.append(Paragraph("<b>2. Review of Existing Work &amp; Research Gaps</b>", sec_style))
story1.append(Paragraph("• <b>Manual Knapsack Sprayers:</b> Heavy physical strain (16–20 kg tank on operator's back), direct inhalation and dermal absorption of toxic chemicals, non-uniform spray coverage, and extreme chemical wastage.", bullet_style))
story1.append(Paragraph("• <b>Agricultural Spraying Drones:</b> Commercial agricultural drones cost upwards of Rs. 4,50,000 to Rs. 8,00,000, suffer from rapid battery depletion (10–15 minute flight times), and generate severe aerial drift into non-target zones.", bullet_style))
story1.append(Paragraph("• <b>Tractor-Mounted Booms:</b> Cause severe soil compaction, require wide turning headlands, and cannot navigate small, fragmented landholdings characteristic of Indian farming.", bullet_style))
story1.append(Paragraph("• <b>Existing Academic Prototypes:</b> Often utilize lightweight plastic chassis and under-rated motor drivers (such as L298N drivers with 2A limits) that immediately burn out or stall when bogged down in wet mud carrying a chemical tank.", bullet_style))
story1.append(Paragraph("<b>Research Gap Addressed:</b> A critical need exists for a rugged, skid-steer mechatronic platform utilizing industrial-grade high-current H-bridges (BTS7960 43A) that reliably hauls a 10–20 kg gross operational payload across uneven muddy soil, coupled with a zero-install smartphone teleoperation cockpit providing low-latency live video streaming and directional micro-spraying.", body_style))

story1.append(Paragraph("<b>3. Problem Statement</b>", sec_style))
story1.append(Paragraph(
    "To engineer and field-validate an affordable, four-wheel-drive (4WD) robotic agricultural ground vehicle that eliminates hazardous human exposure to toxic agrochemicals "
    "by enabling remote smartphone teleoperation, real-time live camera visual telemetry, and precision directional chemical micro-spraying while maintaining sufficient mechanical "
    "torque to haul a 10–20 kg gross operational payload across muddy agricultural soil and 15-degree terrain gradients.",
    body_style
))

story1.append(Paragraph("<b>4. Project Objectives</b>", sec_style))
story1.append(Paragraph("1. <b>Mechatronic Field Powertrain:</b> Construct a rugged, 4WD skid-steer robotic vehicle with aggressive agricultural rubber tires capable of supporting a 10–20 kg gross operational payload across wet, uneven terrain.", bullet_style))
story1.append(Paragraph("2. <b>High-Current Inductive Power Delivery:</b> Integrate dual BTS7960 43A H-bridge drivers with hardware optical isolation and transient flyback suppression to reliably drive four high-torque 12V DC metal-gear motors delivering up to 140 kg·cm stall torque.", bullet_style))
story1.append(Paragraph("3. <b>Smartphone Teleoperation &amp; Visual Telemetry:</b> Develop a low-latency, intuitive smartphone teleoperation mobile application featuring virtual joystick steering, dedicated chemical actuation triggers, and real-time live camera video streaming.", bullet_style))
story1.append(Paragraph("4. <b>Precision Chemical Micro-Spraying:</b> Construct a directional chemical fluid delivery circuit comprising a 12V pressurized diaphragm pump and dual high-speed 12V solenoid valves for targeted micro-burst spraying.", bullet_style))
story1.append(Paragraph("5. <b>Operator Safety &amp; Economic Sustainability:</b> Completely eliminate chemical inhalation and skin contact for farm operators, cut pesticide/fungicide consumption by 30% to 50%, and demonstrate an affordable prototype build under Rs. 19,500.", bullet_style))

story1.append(Paragraph("<b>5. Innovation / Novelty</b>", sec_style))
story1.append(Paragraph("• <b>Industrial-Grade High-Current Powertrain:</b> Replaces fragile hobbyist motor drivers with dual BTS7960 43A drivers handling 43A peak current per motor channel, backed by optical isolation preventing inductive spikes from resetting the edge computer.", bullet_style))
story1.append(Paragraph("• <b>10–20 kg Payload Torque Capacity Proof:</b> Rigorous physics prove four 12V metal-gear motors produce 60 kg·cm rated / 140 kg·cm stall torque—delivering a 1.73x to 4.79x safety factor over the 34.76 kg·cm demand needed to haul a 20 kg loaded vehicle up a 15-degree mud incline.", bullet_style))
story1.append(Paragraph("• <b>Targeted Directional Micro-Spraying:</b> Rather than continuous indiscriminate blanket spraying, dual independent 12V solenoid valves deliver targeted 1.0-second directional micro-bursts to left or right crop foliage directly from phone touch controls, saving up to 50% chemical volume.", bullet_style))
story1.append(Paragraph("• <b>Zero-Install Smartphone Teleoperation Cockpit:</b> Any standard smartphone connects to the rover's local Wi-Fi to display a 56% center viewport live camera stream flanked by virtual analog joysticks and spray triggers.", bullet_style))
story1.append(Paragraph("• <b>Fail-Safe Cyber-Physical Architecture:</b> Common star ground eliminates ground loops; optoisolated relays and 1N4007 flyback diodes suppress back-EMF; and a software watchdog automatically brakes motors if wireless communication drops for &gt; 500 ms.", bullet_style))

# Figures & Methodology
story1.append(Paragraph("<b>6. Proposed Methodology &amp; System Architecture</b>", sec_style))
if os.path.exists("extracted_pdf_p10_1__Image73.png"):
    story1.append(RLImage("extracted_pdf_p10_1__Image73.png", width=480, height=195))
    story1.append(Paragraph("Figure 1: High-Level System Architecture, Powertrain, and Smartphone Teleoperation Pipeline", fig_caption))

story1.append(Paragraph(
    "<b>A. Mechanical Powertrain &amp; Skid-Steer Kinematics:</b> "
    "The chassis is constructed from laser-cut acrylic and reinforced aluminum extrusion, providing a low center of gravity. "
    "Differential skid-steering is implemented with four independent 12V DC metal-gear motors (100 RPM) coupled to 85mm rubber all-terrain tires. "
    "Zero-radius point turns allow the rover to pivot effortlessly at the end of crop rows without damaging crop furrows.<br/><br/>"
    "<b>B. Rigorous 10–20 kg Payload Torque Validation Derivation:</b><br/>"
    "To guarantee field performance under a worst-case 20.0 kg gross vehicle weight traversing soft wet agricultural soil and negotiating a 15-degree incline:<br/>"
    "1. Normal Force: <i>F<sub>N</sub> = M · g = 20.0 kg · 9.81 m/s<sup>2</sup> = 196.2 N</i>.<br/>"
    "2. Rolling Resistance (Soft Mud, <i>C<sub>rr</sub> = 0.15</i>): <i>F<sub>roll</sub> = C<sub>rr</sub> · F<sub>N</sub> = 0.15 · 196.2 N = 29.43 N</i>.<br/>"
    "3. Grade Resistance (15° Incline): <i>F<sub>grade</sub> = M · g · sin(15°) = 196.2 · 0.2588 = 50.78 N</i>.<br/>"
    "4. Total Pulling Force Required: <i>F<sub>total</sub> = F<sub>roll</sub> + F<sub>grade</sub> = 29.43 N + 50.78 N = 80.21 N</i>.<br/>"
    "5. Total Torque at Wheel Axle (Radius <i>R = 0.0425 m</i>): <i>T<sub>total</sub> = F<sub>total</sub> · R = 80.21 N · 0.0425 m = 3.409 N·m ≈ 34.76 kg·cm</i>.<br/>"
    "6. Torque Required Per Motor (4 Motors): <i>T<sub>motor</sub> = 34.76 / 4 = 8.69 kg·cm</i> per motor.<br/>"
    "7. Available Motor Torque: The selected 12V DC metal-geared motors deliver 15.0 kg·cm rated operating torque each (60.0 kg·cm total across 4 wheels) and 35.0 kg·cm stall torque each (140.0 kg·cm total across 4 wheels).<br/>"
    "8. Safety Factor Margin: On extreme 15° mud inclines, Safety Factor = 60.0 / 34.76 = <b>1.73x (rated)</b> and 140.0 / 34.76 = <b>4.03x (stall)</b>. On flat loose soil, demand is only 12.51 kg·cm, yielding a Safety Factor of <b>4.79x (rated)</b> and <b>11.19x (stall)</b>. Hence, the powertrain easily pulls the 10–20 kg rover without motor stalling or thermal runaway.",
    body_style
))

if os.path.exists("extracted_pdf_p18_8__Image95.png"):
    story1.append(RLImage("extracted_pdf_p18_8__Image95.png", width=480, height=195))
    story1.append(Paragraph("Figure 2: Complete Mechatronic Schematic with Raspberry Pi 4, Dual BTS7960 43A Drivers, and Star Ground", fig_caption))

story1.append(Paragraph(
    "<b>C. Directional Chemical Micro-Spraying Subsystem:</b> "
    "A 12V DC self-priming diaphragm pump draws chemical solution from a 3-liter onboard tank, pressurizing a dual-branch distribution manifold at 0.4 MPa. "
    "Two high-speed 12V normally closed solenoid valves independently gate fluid to Left and Right wide-angle brass atomizing misting nozzles. "
    "Each solenoid is actuated via an optoisolated relay/MOSFET channel protected by an antiparallel 1N4007 flyback diode. Active-LOW pulsing triggers precise "
    "1.0-second micro-bursts upon phone command, delivering targeted chemical mist directly onto crop foliage while eliminating unnecessary overspray.<br/><br/>"
    "<b>D. Smartphone Teleoperation &amp; Visual Telemetry Architecture:</b> "
    "A Python Flask/asyncio teleoperation web server runs on the Raspberry Pi 4, broadcasting a local Wi-Fi access point ('AgriRover-AP'). "
    "The operator connects using any smartphone browser or native web app, requiring no internet connectivity. The phone UI features a low-latency "
    "(&lt; 120 ms) MJPEG live video stream (640x480 @ 25-30 FPS) captured by the rover's wide-angle camera. Flanking the stream are responsive virtual analog joysticks "
    "for differential skid-steering and touch triggers for Left, Right, and Dual micro-spray actuation. A 200 ms heartbeat watchdog enforces auto-braking if connection drops.",
    body_style
))

if os.path.exists("extracted_pdf_p19_9__Image98.png"):
    story1.append(RLImage("extracted_pdf_p19_9__Image98.png", width=480, height=190))
    story1.append(Paragraph("Figure 3: Pressurized Chemical Fluid Circuit with Dual Solenoid Micro-Spraying Valves and Flyback Suppression", fig_caption))

if os.path.exists("extracted_pdf_p20_11__Image102.png"):
    story1.append(RLImage("extracted_pdf_p20_11__Image102.png", width=480, height=210))
    story1.append(Paragraph("Figure 4: Ergonomic Smartphone Teleoperation Cockpit with Live Video Stream, Virtual Joystick, and Spray Actuators", fig_caption))

story1.append(Paragraph("<b>7. Expected Deliverables</b>", sec_style))
story1.append(Paragraph("1. <b>Functional 4WD Robotic Rover Prototype:</b> Rugged skid-steer chassis transporting 10–20 kg gross operational payload across muddy soil.", bullet_style))
story1.append(Paragraph("2. <b>Smartphone Teleoperation Application:</b> Responsive cockpit application with virtual joystick driving, live camera feed, and directional spray controls.", bullet_style))
story1.append(Paragraph("3. <b>Calibrated Chemical Micro-Spraying System:</b> Dual-nozzle pressurized fluid circuit delivering calibrated 1.0-second chemical micro-bursts.", bullet_style))
story1.append(Paragraph("4. <b>Technical Documentation &amp; Academic Report:</b> Complete wiring schematics, CAD chassis models, source code repository, and field evaluation performance report.", bullet_style))

story1.append(Paragraph("<b>8. Expected Outcomes and Impact</b>", sec_style))
story1.append(Paragraph("• <b>Technical:</b> Proves the viability of low-cost edge computing (Raspberry Pi 4) and high-current drivers (BTS7960) for heavy-load agricultural robotics.", bullet_style))
story1.append(Paragraph("• <b>Social &amp; Health:</b> Completely protects agricultural workers from inhaling hazardous chemicals and prevents pesticide dermatosis and poisoning.", bullet_style))
story1.append(Paragraph("• <b>Environmental:</b> Reduces chemical runoff and groundwater contamination by 30% to 50% through targeted directional application.", bullet_style))
story1.append(Paragraph("• <b>Economic:</b> Drastically lowers crop protection costs for smallholder farmers; build cost under Rs. 19,500 compared to lakhs for commercial equipment.", bullet_style))
story1.append(Paragraph("• <b>Industrial &amp; Academic:</b> Provides a modular agritech reference architecture and advances student research in cyber-physical mechatronics at BMSITM.", bullet_style))

story1.append(Paragraph("<b>9. Relevance to State &amp; National Priorities</b>", sec_style))
story1.append(Paragraph("[X] <b>Sustainable Development Goals (SDGs):</b> Goal 2 (Zero Hunger), Goal 3 (Good Health), Goal 9 (Innovation), Goal 12 (Responsible Consumption).", bullet_style))
story1.append(Paragraph("[X] <b>Karnataka Priority Sector:</b> Farm mechanization and smart agriculture prioritized under the Karnataka State Innovation Strategy.", bullet_style))
story1.append(Paragraph("[X] <b>Rural Development &amp; Agriculture:</b> Low-cost mechanization tailored for smallholder farmers in rural Karnataka.", bullet_style))
story1.append(Paragraph("[X] <b>Environment &amp; Climate Resilience:</b> Reduction of toxic chemical leaching into village soil and water tables.", bullet_style))
story1.append(Paragraph("[X] <b>Digital India &amp; Startup Potential:</b> Indigenous hardware design, edge IoT automation, and mobile-enabled field services.", bullet_style))

# Work Plan
story1.append(Paragraph("<b>10. Work Plan (5-Month Execution Schedule)</b>", sec_style))
gantt_pdf_data = [
    [Paragraph("Project Activity / Milestone", table_header), Paragraph("Month 1<br/>(Dec 2026)", table_header), Paragraph("Month 2<br/>(Jan 2027)", table_header), Paragraph("Month 3<br/>(Feb 2027)", table_header), Paragraph("Month 4<br/>(Mar 2027)", table_header), Paragraph("Month 5<br/>(Apr 2027)", table_header)],
    [Paragraph("Literature Survey &amp; Component Procuring", table_text), Paragraph("✓", table_text), Paragraph("", table_text), Paragraph("", table_text), Paragraph("", table_text), Paragraph("", table_text)],
    [Paragraph("Chassis Fabrication &amp; Mechanical Powertrain Assembly", table_text), Paragraph("", table_text), Paragraph("✓", table_text), Paragraph("", table_text), Paragraph("", table_text), Paragraph("", table_text)],
    [Paragraph("Mechatronic Circuitry, BTS7960 Drivers &amp; Solenoid Integration", table_text), Paragraph("", table_text), Paragraph("✓", table_text), Paragraph("✓", table_text), Paragraph("", table_text), Paragraph("", table_text)],
    [Paragraph("Mobile App Teleoperation &amp; Camera Video Stream Development", table_text), Paragraph("", table_text), Paragraph("", table_text), Paragraph("✓", table_text), Paragraph("✓", table_text), Paragraph("", table_text)],
    [Paragraph("Field Soil Trials, Incline Climbing &amp; Spray Pattern Calibration", table_text), Paragraph("", table_text), Paragraph("", table_text), Paragraph("", table_text), Paragraph("✓", table_text), Paragraph("✓", table_text)],
    [Paragraph("Midterm Evaluation, Data Analysis &amp; Final KSCST Report", table_text), Paragraph("", table_text), Paragraph("", table_text), Paragraph("", table_text), Paragraph("", table_text), Paragraph("✓", table_text)]
]
tbl_gantt_pdf = Table(gantt_pdf_data, colWidths=[215, 60, 60, 60, 60, 60])
tbl_gantt_pdf.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 2.5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
]))
story1.append(tbl_gantt_pdf)
story1.append(Spacer(1, 6))

# Facilities Available
story1.append(Paragraph("<b>11. Facilities Available in Institution</b>", sec_style))
fac_pdf_data = [
    [Paragraph("<b>1. Laboratory:</b>", table_text), Paragraph("MCA Advanced Computing Lab &amp; Embedded Systems Laboratory, BMSITM", table_text)],
    [Paragraph("<b>2. Equipment:</b>", table_text), Paragraph("Digital Storage Oscilloscopes (DSO), Regulated DC Power Supplies (0–30V, 5A), Soldering Workstations", table_text)],
    [Paragraph("<b>3. Software:</b>", table_text), Paragraph("Python 3.10+, Flask, OpenCV 4.x, Visual Studio Code, Git/GitHub, Linux OS", table_text)],
    [Paragraph("<b>4. Instruments:</b>", table_text), Paragraph("Digital Multimeters (True-RMS DMM), Digital Tachometers, Infrared Temperature Probes", table_text)],
    [Paragraph("<b>5. Workshop:</b>", table_text), Paragraph("Mechanical Engineering Department Machine Shop &amp; Fabrication Lab, BMSITM (Drilling, Cutting, Bench Vices)", table_text)],
    [Paragraph("<b>6. Institutional Facilities:</b>", table_text), Paragraph("Campus Wi-Fi, High-Speed Computing Workstations, Campus Agricultural/Garden Field Testbeds", table_text)]
]
tbl_fac_pdf = Table(fac_pdf_data, colWidths=[150, 365])
tbl_fac_pdf.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('TOPPADDING', (0, 0), (-1, -1), 2.5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
]))
story1.append(tbl_fac_pdf)
story1.append(Spacer(1, 6))

# Budget Table
story1.append(Paragraph("<b>12. Budget Estimate (Prescribed Subheads - Total: ₹ 19,500/-)</b>", sec_style))
bgt_pdf_data = [
    [Paragraph("Prescribed Budget Subhead", table_header), Paragraph("Estimated Cost (₹)", table_header)],
    [Paragraph("1. Equipment / Components (Raspberry Pi 4, BTS7960 Drivers, Motors, Camera, Battery)", table_text), Paragraph("₹ 11,600/-", table_text)],
    [Paragraph("2. Consumables (12V Diaphragm Pump, Solenoid Valves, Mist Nozzles, Diodes, Tubing, Wiring)", table_text), Paragraph("₹ 3,100/-", table_text)],
    [Paragraph("3. Fabrication (Chassis Laser Cutting, Aluminum Brackets, 85mm Tires, Fluid Tank Mounts)", table_text), Paragraph("₹ 3,800/-", table_text)],
    [Paragraph("4. Software / Cloud Services (Open-Source Python, Linux, Flask, OpenCV)", table_text), Paragraph("₹ 0/-", table_text)],
    [Paragraph("5. Field Survey / Data Collection (Local Rural Farmland Travel &amp; Operator Testing)", table_text), Paragraph("₹ 500/-", table_text)],
    [Paragraph("6. Testing / Analysis (Spray Volume Calibration, Multimeter Testing, Incline Trials)", table_text), Paragraph("₹ 500/-", table_text)],
    [Paragraph("7. Miscellaneous (Hardware Fasteners, Heat-Shrink Sleeving, Contingency)", table_text), Paragraph("₹ 0/-", table_text)],
    [Paragraph("<b>TOTAL ESTIMATED PROJECT COST:</b>", table_bold), Paragraph("<b>₹ 19,500/-</b>", table_bold)]
]
tbl_bgt_pdf = Table(bgt_pdf_data, colWidths=[385, 130])
tbl_bgt_pdf.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#F1F5F9")),
    ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 2.5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
]))
story1.append(tbl_bgt_pdf)
story1.append(Paragraph("<i>Note: Any expenditure beyond sanctioned KSCST grant (up to ₹10,000) will be borne by institutional resources and team support.</i>", ParagraphStyle('Note', fontName='Times-Italic', fontSize=8, textColor=colors.HexColor("#64748B"), spaceBefore=2, spaceAfter=6)))

# References
story1.append(Paragraph("<b>13. References (IEEE Format)</b>", sec_style))
story1.append(Paragraph("[1] S. Bargoti and J. P. Underwood, 'Deep fruit detection in orchards,' in <i>Proc. IEEE ICRA</i>, Singapore, 2017, pp. 3626–3633.<br/>"
                        "[2] A. Sharma et al., 'Machine learning applications in precision agriculture: A comprehensive review,' <i>IEEE Access</i>, vol. 9, pp. 4843–4873, 2021.<br/>"
                        "[3] P. Gonzalez-de-Santos et al., 'Unmanned ground vehicles for smart agriculture: A review,' <i>Comp. &amp; Electron. in Agri.</i>, vol. 169, 2020.<br/>"
                        "[4] D. K. Fisher and F. J. Aguilar, 'Open-source hardware/software for agricultural telemetry,' <i>Comp. &amp; Electron. in Agri.</i>, vol. 153, 2018.<br/>"
                        "[5] R. S. S. Kumar, K. Venkatasubramanian, and G. Dwarakanath, 'Design and kinematics optimization of 4WD skid-steer rovers,' <i>J. Agri. Eng. Tech.</i>, 2022.<br/>"
                        "[6] S. Fountas et al., 'Agricultural robotics for field operations: Current status and economic feasibility,' <i>Robotics</i>, vol. 9, no. 1, p. 3, 2020.",
                        ParagraphStyle('RefText', fontName='Times-Roman', fontSize=8.5, leading=11, spaceAfter=6)))

# Fee details & signatures
story1.append(Paragraph("<b>14. Processing Fee Payment Details (₹1,180/- Mandatory Single Transaction)</b>", sec_style))
fee_summary_data = [
    [Paragraph("<b>Mode of Payment:</b> [X] UPI    [  ] NEFT", table_text), Paragraph("<b>Amount Paid:</b> ₹ 1,180/- (Incl. 18% GST)", table_text)],
    [Paragraph("<b>Transaction / UTR No.:</b> ____________________________", table_text), Paragraph("<b>Date &amp; Time:</b> 26 / 11 / 2026 | __________ IST", table_text)],
    [Paragraph("<b>Account Holder:</b> THANMAY M (+91 9880123456)", table_text), Paragraph("<b>KSCST Bank:</b> Canara Bank IISc Campus (A/C: 0683201000024, IFSC: CNRB0000683)", table_text)]
]
tbl_fee_sum = Table(fee_summary_data, colWidths=[255, 260])
tbl_fee_sum.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
    ('TOPPADDING', (0, 0), (-1, -1), 2.5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
]))
story1.append(tbl_fee_sum)
story1.append(Spacer(1, 6))

# Signatures in proposal
sig_boxes_pdf = [
    [
        Paragraph("<b>Signature of Project Guide:</b><br/><br/><br/>___________________________<br/><b>Dr. DWARAKANATH G V</b><br/>Assoc. Professor &amp; Project Coord.<br/>Dept. of MCA, BMSITM<br/>Date: 26/11/2026<br/>(Guide Seal)", table_text),
        Paragraph("<b>Signature of SPP Coordinator:</b><br/><br/><br/>___________________________<br/><b>Dr. MANJUNATH C</b><br/>Assistant Professor<br/>Dept. of Mech Engg, BMSITM<br/>Date: 26/11/2026<br/>(SPP Coord. Seal)", table_text),
        Paragraph("<b>Signature of HOD:</b><br/><br/><br/>___________________________<br/><b>Dr. M. SRIDEVI</b><br/>Head of the Department<br/>Dept. of MCA, BMSITM<br/>Date: 26/11/2026<br/>(HOD Seal)", table_text)
    ]
]
tbl_sig_boxes = Table(sig_boxes_pdf, colWidths=[171, 172, 172])
tbl_sig_boxes.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
]))
story1.append(tbl_sig_boxes)

doc1.build(story1, canvasmaker=NumberedCanvas)
print(f"SUCCESS: {pdf_path_1} generated cleanly!")

# Copy to KSCST_SPP_AgriRover_Project_Proposal.pdf as well
shutil.copy(pdf_path_1, "KSCST_SPP_AgriRover_Project_Proposal.pdf")
print("SUCCESS: Copied to KSCST_SPP_AgriRover_Project_Proposal.pdf")


# ==================== 2. DECLARATION & ENDORSEMENT PDF ====================
print("\nGenerating 2. Declaration & Endorsement Form (02_Agri_Rover_Robo_declaration_endorsement.pdf)...")
pdf_path_2 = "02_Agri_Rover_Robo_declaration_endorsement.pdf"
doc2 = SimpleDocTemplate(
    pdf_path_2,
    pagesize=A4,
    leftMargin=38,
    rightMargin=38,
    topMargin=32,
    bottomMargin=32
)

story2 = []

if os.path.exists("kscst_header_logos.png"):
    story2.append(RLImage("kscst_header_logos.png", width=519, height=91))
    story2.append(Spacer(1, 3))

story2.append(Paragraph("KARNATAKA STATE COUNCIL FOR SCIENCE AND TECHNOLOGY (KSCST)", title_style))
story2.append(Paragraph("Indian Institute of Science Campus, Bengaluru – 560012", ParagraphStyle('Sub', fontName='Times-Italic', fontSize=8.5, alignment=1, textColor=colors.HexColor("#475569"))))
story2.append(Paragraph("50th SERIES OF THE STUDENT PROJECT PROGRAMME (SPP: 2026–2027)", sub_title_style))
story2.append(Paragraph("DECLARATION BY STUDENTS AND INSTITUTIONAL ENDORSEMENT FORM", ParagraphStyle('DecT', fontName='Times-Bold', fontSize=10, alignment=1, textColor=colors.HexColor("#1E3A8A"))))
story2.append(Spacer(1, 4))

dec_meta = [
    [Paragraph("<b>Project Proposal Title:</b>", table_text), Paragraph("<b>Agri Rover Robo: Smartphone-Controlled Agricultural Robotic Vehicle for Precision Chemical Micro-Spraying and Remote Teleoperation</b>", table_bold)],
    [Paragraph("<b>Institution Name:</b>", table_text), Paragraph("B.M.S. INSTITUTE OF TECHNOLOGY &amp; MANAGEMENT (BMSITM), Yelahanka, Bengaluru – 560064", table_text)],
    [Paragraph("<b>Department / Stream:</b>", table_text), Paragraph("Department of Master of Computer Applications (MCA) [Postgraduate]", table_text)],
    [Paragraph("<b>Broad Theme (KSCST):</b>", table_text), Paragraph("Theme 1: Sustainable Agriculture, Food Security &amp; Rural Development (Cross-cutting: Theme 4 &amp; 6)", table_text)],
    [Paragraph("<b>College SPP Coordinator:</b>", table_text), Paragraph("Dr. MANJUNATH C, Assistant Professor, Dept. of Mechanical Engineering, BMSITM (manjuc@bmsit.in)", table_text)],
    [Paragraph("<b>Project Guide Name:</b>", table_text), Paragraph("Dr. DWARAKANATH G V, Project Coordinator &amp; Associate Professor, Dept. of MCA, BMSITM", table_text)]
]
tbl_dec_meta = Table(dec_meta, colWidths=[140, 379])
tbl_dec_meta.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('TOPPADDING', (0, 0), (-1, -1), 2),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
]))
story2.append(tbl_dec_meta)
story2.append(Spacer(1, 5))

story2.append(Paragraph("<b>DECLARATION BY STUDENTS</b>", ParagraphStyle('DecH', fontName='Times-Bold', fontSize=9.5, textColor=colors.HexColor("#1E3A8A"))))
story2.append(Paragraph(
    "We, the undersigned final year students of the Department of Master of Computer Applications (MCA), BMS Institute of Technology &amp; "
    "Management, Bengaluru, hereby declare that the project proposal entitled <i>'Agri Rover Robo: Smartphone-Controlled Agricultural Robotic "
    "Vehicle for Precision Chemical Micro-Spraying and Remote Teleoperation'</i> is a bona fide record of independent research and engineering work "
    "planned and executed by us under the guidance of Dr. Dwarakanath G V. This proposal has not been submitted previously to any other university, "
    "organization, or funding agency for the award of any degree, diploma, or financial sponsorship.",
    ParagraphStyle('DecB', fontName='Times-Roman', fontSize=8.5, leading=11, alignment=4, textColor=colors.HexColor("#1E293B"))
))
story2.append(Spacer(1, 4))

dec_stu_table = [
    [Paragraph("Sl.", table_header), Paragraph("Name of Student", table_header), Paragraph("USN", table_header), Paragraph("Signature with Date", table_header)],
    [Paragraph("1", table_text), Paragraph("<b>THANMAY M</b> (Team Leader)", table_text), Paragraph("1BY24MC095", table_text), Paragraph("____________________________", table_text)],
    [Paragraph("2", table_text), Paragraph("<b>MOHIT S</b>", table_text), Paragraph("1BY24MC063", table_text), Paragraph("____________________________", table_text)]
]
tbl_dec_stu = Table(dec_stu_table, colWidths=[25, 230, 114, 150])
tbl_dec_stu.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    ('ALIGN', (3, 0), (3, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 2.5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
]))
story2.append(tbl_dec_stu)
story2.append(Spacer(1, 6))

story2.append(Paragraph("<b>ENDORSEMENT BY PROJECT GUIDE, HOD &amp; HEAD OF INSTITUTION</b>", ParagraphStyle('EndH', fontName='Times-Bold', fontSize=9.5, textColor=colors.HexColor("#1E3A8A"))))
story2.append(Paragraph(
    "This is to certify that the project proposal entitled <i>'Agri Rover Robo: Smartphone-Controlled Agricultural Robotic Vehicle for Precision "
    "Chemical Micro-Spraying and Remote Teleoperation'</i> submitted by <b>Thanmay M</b> and <b>Mohit S</b>, final year MCA students of "
    "BMSITM, is an original research and engineering endeavor. The project has been reviewed and endorsed for submission under the 50th Series of the "
    "Student Project Programme (SPP: 2026–2027) of KSCST.",
    ParagraphStyle('EndB', fontName='Times-Roman', fontSize=8.5, leading=11, alignment=4, textColor=colors.HexColor("#1E293B"))
))
story2.append(Spacer(1, 4))

end_table_data = [
    [
        Paragraph("<b>Signature of Project Guide:</b><br/><br/><br/>___________________________<br/><b>Dr. DWARAKANATH G V</b><br/>Project Coordinator / Assoc. Prof<br/>Dept. of MCA, BMSITM<br/>Date: 26/11/2026", table_text),
        Paragraph("<b>Signature of HOD:</b><br/><br/><br/>___________________________<br/><b>Dr. M. SRIDEVI</b><br/>Head of the Department<br/>Dept. of MCA, BMSITM<br/>Date: 26/11/2026", table_text),
        Paragraph("<b>Signature of Principal:</b><br/><br/><br/>___________________________<br/><b>Dr. SANJAY H.A</b><br/>Principal / Head of Institution<br/>BMSITM, Bengaluru<br/><b>(Official College Seal)</b>", table_text)
    ]
]
tbl_end_pdf = Table(end_table_data, colWidths=[173, 173, 173])
tbl_end_pdf.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
]))
story2.append(tbl_end_pdf)

doc2.build(story2, canvasmaker=SinglePageCanvas)
print(f"SUCCESS: {pdf_path_2} generated cleanly (Strict 1 Page)!")
shutil.copy(pdf_path_2, "KSCST_Declaration_and_Endorsement_Form.pdf")


# ==================== 3. STANDALONE PROCESSING FEE FORM PDF ====================
print("\nGenerating 3. Processing Fee Form (03_Agri_Rover_Robo_Processing_Fee.pdf)...")
pdf_path_3 = "03_Agri_Rover_Robo_Processing_Fee.pdf"
doc3 = SimpleDocTemplate(
    pdf_path_3,
    pagesize=A4,
    leftMargin=40,
    rightMargin=40,
    topMargin=36,
    bottomMargin=36
)

story3 = []

if os.path.exists("kscst_header_logos.png"):
    story3.append(RLImage("kscst_header_logos.png", width=515, height=90))
    story3.append(Spacer(1, 4))

story3.append(Paragraph("KARNATAKA STATE COUNCIL FOR SCIENCE AND TECHNOLOGY (KSCST)", title_style))
story3.append(Paragraph("Indian Institute of Science Campus, Bengaluru – 560012", ParagraphStyle('SubF', fontName='Times-Italic', fontSize=9, alignment=1, textColor=colors.HexColor("#475569"))))
story3.append(Paragraph("50th SERIES OF THE STUDENT PROJECT PROGRAMME (SPP: 2026–2027)", sub_title_style))
story3.append(Spacer(1, 4))

story3.append(make_part_banner("DETAILS OF PROCESSING FEES MADE THROUGH NEFT / UPI PAYMENT"))
story3.append(Spacer(1, 6))

story3.append(Paragraph(
    "<b>TITLE OF THE PROJECT:</b> AGRI ROVER ROBO: SMARTPHONE-CONTROLLED AGRICULTURAL ROBOTIC VEHICLE FOR PRECISION CHEMICAL MICRO-SPRAYING AND REMOTE TELEOPERATION<br/>"
    "<b>NAME OF THE TEAM LEADER:</b> THANMAY M (USN: 1BY24MC095)<br/>"
    "<b>EMAIL ID:</b> thanmaym08@gmail.com    |    <b>CONTACT MOBILE NO.:</b> +91 9880123456<br/>"
    "<b>INSTITUTION:</b> B.M.S. INSTITUTE OF TECHNOLOGY &amp; MANAGEMENT (BMSITM), BENGALURU – 560064",
    body_style
))
story3.append(Spacer(1, 6))

fee_form_table = [
    [Paragraph("<b>BANK REF. NO. / UTR NO. / UPI NO. (12 DIGITS):</b>", table_text), Paragraph("________________________________________ <i>(12-digit code)</i>", table_text)],
    [Paragraph("<b>TRANSACTION ID:</b>", table_text), Paragraph("________________________________________", table_text)],
    [Paragraph("<b>NAME OF SENDER / ACCOUNT HOLDER:</b>", table_text), Paragraph("THANMAY M", table_bold)],
    [Paragraph("<b>CONTACT NUMBER OF SENDER:</b>", table_text), Paragraph("+91 9880123456", table_text)],
    [Paragraph("<b>NAME OF THE SENDER BANK:</b>", table_text), Paragraph("________________________________________", table_text)],
    [Paragraph("<b>PROCESSING FEES AMOUNT:</b>", table_text), Paragraph("<b>Rs. 1,180/-</b> <i>(Rupees One Thousand One Hundred and Eighty Only, Incl. 18% GST)</i>", table_bold)],
    [Paragraph("<b>DATE OF PAYMENT MADE:</b>", table_text), Paragraph("26 / 11 / 2026", table_text)],
    [Paragraph("<b>TIME OF PAYMENT MADE:</b>", table_text), Paragraph("___________ IST", table_text)],
    [Paragraph("<b>MODE OF PAYMENT MADE:</b>", table_text), Paragraph("UPI (GPay / PhonePe / Paytm / BHIM)  [X] UPI    [  ] NEFT", table_text)],
    [Paragraph("<b>KSCST BENEFICIARY ACCOUNT DETAILS:</b>", table_text), Paragraph("Current A/C: 0683201000024, Canara Bank, IISc Campus Branch, Bengaluru<br/>IFSC: CNRB0000683 | MICR: 560015023 | UPI ID: 0683201000024@cnrb", table_text)]
]
tbl_fee_doc = Table(fee_form_table, colWidths=[200, 315])
tbl_fee_doc.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('TOPPADDING', (0, 0), (-1, -1), 3.5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
]))
story3.append(tbl_fee_doc)
story3.append(Spacer(1, 10))

fee_sigs_data = [
    [
        Paragraph("<b>Signature of Team Leader:</b><br/><br/><br/>___________________________<br/><b>THANMAY M</b> (1BY24MC095)<br/>Date: 26/11/2026", table_text),
        Paragraph("<b>Signature of Project Guide with Seal:</b><br/><br/><br/>___________________________<br/><b>Dr. DWARAKANATH G V</b><br/>Assoc. Professor, Dept. of MCA, BMSITM<br/>Date: 26/11/2026", table_text),
        Paragraph("<b>Signature of HOD / SPP Coord with Seal:</b><br/><br/><br/>___________________________<br/><b>Dr. M. SRIDEVI / Dr. MANJUNATH C</b><br/>BMSITM, Bengaluru<br/>Date: 26/11/2026", table_text)
    ]
]
tbl_fee_sigs_pdf = Table(fee_sigs_data, colWidths=[171, 172, 172])
tbl_fee_sigs_pdf.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
]))
story3.append(tbl_fee_sigs_pdf)

doc3.build(story3, canvasmaker=SinglePageCanvas)
print(f"SUCCESS: {pdf_path_3} generated cleanly (Strict 1 Page)!")


# ==================== 4. PAYMENT RECEIPT PROOF TEMPLATE PDF ====================
print("\nGenerating 4. Payment Receipt Template (04_Agri_Rover_Robo_Payment_Receipt.pdf)...")
pdf_path_4 = "04_Agri_Rover_Robo_Payment_Receipt.pdf"
doc4 = SimpleDocTemplate(
    pdf_path_4,
    pagesize=A4,
    leftMargin=40,
    rightMargin=40,
    topMargin=36,
    bottomMargin=36
)

story4 = []

if os.path.exists("kscst_header_logos.png"):
    story4.append(RLImage("kscst_header_logos.png", width=515, height=90))
    story4.append(Spacer(1, 4))

story4.append(Paragraph("KARNATAKA STATE COUNCIL FOR SCIENCE AND TECHNOLOGY (KSCST)", title_style))
story4.append(Paragraph("PROOF OF PROCESSING FEE PAYMENT (UPI / NEFT RECEIPT)", sub_title_style))
story4.append(Spacer(1, 6))

story4.append(make_part_banner("MANDATORY UPLOAD 04: PAYMENT TRANSACTION RECEIPT (₹ 1,180/-)"))
story4.append(Spacer(1, 6))

story4.append(Paragraph(
    "<b>Project Title:</b> AGRI ROVER ROBO: SMARTPHONE-CONTROLLED AGRICULTURAL ROBOTIC VEHICLE FOR PRECISION CHEMICAL MICRO-SPRAYING AND REMOTE TELEOPERATION<br/>"
    "<b>Team Leader:</b> THANMAY M (USN: 1BY24MC095) | <b>Mobile:</b> +91 9880123456<br/>"
    "<b>Institution:</b> B.M.S. INSTITUTE OF TECHNOLOGY &amp; MANAGEMENT, BENGALURU – 560064<br/>"
    "<b>Amount:</b> Rs. 1,180/- (Single Transaction - Inclusive of 18% GST)",
    body_style
))
story4.append(Spacer(1, 8))

receipt_box_data = [
    [
        Paragraph(
            "<br/><br/><br/><br/><b>[ PASTE OFFICIAL UPI / NEFT PAYMENT RECEIPT SCREENSHOT HERE ]</b><br/><br/>"
            "<i>Ensure that the following details are clearly visible in the screenshot:</i><br/>"
            "• Beneficiary Name: Secretary, Karnataka State Council for Science and Technology<br/>"
            "• Canara Bank Current A/C: 0683201000024 | UPI ID: 0683201000024@cnrb<br/>"
            "• Amount Paid: Exactly ₹ 1,180.00<br/>"
            "• 12-Digit UTR / UPI Transaction Reference Number<br/>"
            "• Transaction Date &amp; Time (26/11/2026)<br/>"
            "• Payment Status: SUCCESS / COMPLETED<br/><br/><br/><br/>",
            ParagraphStyle('RcptBox', fontName='Times-Roman', fontSize=10, leading=14, alignment=1, textColor=colors.HexColor("#475569"))
        )
    ]
]
tbl_receipt_box = Table(receipt_box_data, colWidths=[515])
tbl_receipt_box.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#3B82F6")),
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
    ('TOPPADDING', (0, 0), (-1, -1), 15),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
]))
story4.append(tbl_receipt_box)
story4.append(Spacer(1, 10))

story4.append(Paragraph(
    "<b>KSCST Official Bank Account Details for Reference:</b><br/>"
    "• Account Holder: Secretary, Karnataka State Council for Science and Technology<br/>"
    "• Current Account No.: 0683201000024<br/>"
    "• Bank &amp; Branch: Canara Bank, Indian Institute of Science (IISc) Campus Branch, Bangalore – 560012<br/>"
    "• IFSC Code: CNRB0000683  |  MICR Code: 560015023  |  UPI ID: 0683201000024@cnrb",
    ParagraphStyle('BankRef', fontName='Times-Roman', fontSize=8.5, leading=11.5, textColor=colors.HexColor("#334155"))
))

doc4.build(story4, canvasmaker=SinglePageCanvas)
print(f"SUCCESS: {pdf_path_4} generated cleanly (Strict 1 Page)!")

print("\nALL 4 MANDATORY KSCST SUBMISSION PDFS ARE READY!")
