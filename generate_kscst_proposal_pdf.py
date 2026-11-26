import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Times-Roman", 8.5)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(45, 805, "KSCST 50th Series SPP (2026-2027) | Project Proposal: Agri Rover (BMSITM MCA)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(45, 800, 550, 800)
            
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(550, 32, page_text)
        self.drawString(45, 32, "Confidential - Submitted to Karnataka State Council for Science and Technology (KSCST)")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(45, 42, 550, 42)
        self.restoreState()

def build_pdf():
    pdf_filename = "KSCST_SPP_AgriRover_Project_Proposal.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=15,
        alignment=1, # Center
        textColor=colors.HexColor("#0F172A")
    )
    
    sub_title_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=10,
        leading=13,
        alignment=1,
        textColor=colors.HexColor("#B45309")
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=11,
        leading=14,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.HexColor("#1E3A8A")
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=10,
        leading=13,
        spaceBefore=6,
        spaceAfter=2,
        textColor=colors.HexColor("#0F172A")
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13,
        alignment=4, # Justify
        spaceAfter=4,
        textColor=colors.HexColor("#1E293B")
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        leading=12.5,
        alignment=4,
        leftIndent=12,
        spaceAfter=3,
        textColor=colors.HexColor("#1E293B")
    )

    caption_style = ParagraphStyle(
        'FigCaption',
        parent=styles['Normal'],
        fontName='Times-BoldItalic',
        fontSize=8.5,
        leading=11,
        alignment=1,
        spaceBefore=2,
        spaceAfter=6,
        textColor=colors.HexColor("#334155")
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=colors.white
    )

    story = []

    # Title & Banner
    story.append(Paragraph("KARNATAKA STATE COUNCIL FOR SCIENCE AND TECHNOLOGY (KSCST)", title_style))
    story.append(Paragraph("Indian Institute of Science Campus, Bengaluru – 560012", caption_style))
    story.append(Paragraph("50th SERIES OF THE STUDENT PROJECT PROGRAMME (SPP: 2026–2027)", sub_title_style))
    story.append(Paragraph("PROJECT PROPOSAL FOR POSTGRADUATE (MCA) TEAMS", ParagraphStyle('SubSub', parent=sub_title_style, fontSize=9.5, textColor=colors.HexColor("#1E3A8A"))))
    story.append(Spacer(1, 6))

    # Meta Table
    meta_table_data = [
        [Paragraph("<b>Institution Name:</b>", table_cell_bold), Paragraph("B.M.S. INSTITUTE OF TECHNOLOGY & MANAGEMENT (BMSITM)<br/>Yelahanka, Bengaluru – 560064", table_cell_style)],
        [Paragraph("<b>Department / Stream:</b>", table_cell_bold), Paragraph("Department of Master of Computer Applications (MCA) [Postgraduate]", table_cell_style)],
        [Paragraph("<b>Broad Theme (KSCST):</b>", table_cell_bold), Paragraph("<b>Theme 1: Sustainable Agriculture, Food Security & Rural Development</b><br/>(Cross-Cutting: Theme 4: AI & Digital Tech; Theme 6: Robotics & Automation)", table_cell_style)],
        [Paragraph("<b>Project Proposal Title:</b>", table_cell_bold), Paragraph("<b>Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring</b>", table_cell_style)],
        [Paragraph("<b>Project Duration:</b>", table_cell_bold), Paragraph("Commencement: 01/10/2025  |  Probable Completion: 31/05/2027", table_cell_style)],
        [Paragraph("<b>KSCST Coordinator:</b>", table_cell_bold), Paragraph("Dr. MANJUNATHA C, Assoc. Prof, Dept of Chemistry, BMSITM (manjuc@bmsit.in | 9880744476)", table_cell_style)],
        [Paragraph("<b>Project Guide:</b>", table_cell_bold), Paragraph("Dr. DWARAKANATH G V, Project Coordinator & Assoc. Prof, Dept. of MCA, BMSITM", table_cell_style)]
    ]
    t_meta = Table(meta_table_data, colWidths=[130, 375])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 6))

    # Team Table
    story.append(Paragraph("<b>Table 2: Student Project Team Details (Max 4 Students)</b>", caption_style))
    team_table_data = [
        [Paragraph("Sl.", table_header_style), Paragraph("Student Name", table_header_style), Paragraph("USN", table_header_style), Paragraph("Mobile No.", table_header_style), Paragraph("Email ID", table_header_style)],
        [Paragraph("1", table_cell_style), Paragraph("<b>THANMAY M (Team Leader)</b>", table_cell_style), Paragraph("1BY24MC095", table_cell_style), Paragraph("+91 9880123456", table_cell_style), Paragraph("thanmaym08@gmail.com", table_cell_style)],
        [Paragraph("2", table_cell_style), Paragraph("KEERTHANA", table_cell_style), Paragraph("1BY24MC045", table_cell_style), Paragraph("+91 9845123456", table_cell_style), Paragraph("keerthana.mca@bmsit.in", table_cell_style)],
        [Paragraph("3", table_cell_style), Paragraph("MOHAN", table_cell_style), Paragraph("1BY24MC058", table_cell_style), Paragraph("+91 9742123456", table_cell_style), Paragraph("mohan.mca@bmsit.in", table_cell_style)],
        [Paragraph("4", table_cell_style), Paragraph("MONICA", table_cell_style), Paragraph("1BY24MC061", table_cell_style), Paragraph("+91 9611123456", table_cell_style), Paragraph("monica.mca@bmsit.in", table_cell_style)],
    ]
    t_team = Table(team_table_data, colWidths=[25, 175, 80, 85, 140])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 8))

    # Section 1: Abstract
    story.append(Paragraph("1. PROJECT SUMMARY / ABSTRACT", h1_style))
    story.append(Paragraph("<b>Agri Rover</b> is an autonomous cyber-physical robotic vehicle engineered for localized precision agriculture, automated in-situ soil health diagnostics, and zero-risk digital twin algorithm testing. Contemporary agriculture across Karnataka faces severe headwinds: chronic farm labor shortages, rising agrochemical costs, widespread soil degradation due to over-fertilization, and environmental toxicity caused by conventional blanket tractor sprayers that waste up to 70–80% of applied chemicals.", body_style))
    story.append(Paragraph("Agri Rover replaces broad-spectrum broadcast spraying with real-time edge computer vision (OpenCV) running onboard a <b>Raspberry Pi 4 Model B</b> single-board computer. The robot captures 1080p sub-canopy video, transforms frames to HSV color space, isolates foliar threats (caterpillar pests and invasive weeds) via morphological segmentation, and triggers directional 12V solenoid valves for millisecond-calibrated micro-burst chemical delivery, saving up to 80% of active pesticide volume. Simultaneously, a motorized linear actuator deploys electrochemical soil probes (NPK, pH, and capacitive soil moisture) directly into the crop bed while the 4WD skid-steer chassis (dual BTS7960 43A H-bridges) is immobilized by a software safety interlock.", body_style))
    story.append(Paragraph("A cornerstone engineering contribution of Agri Rover is its high-fidelity <b>3D WebGL Digital Twin Simulator</b> built with React and Three.js. The simulator mirrors exact physical kinematics, zero-radius point turns, row lane-lock steering, and telemetry streaming over WebSockets/REST, enabling smallholder farmers and researchers to validate patrol and spraying algorithms in virtual farmland prior to physical hardware deployment.", body_style))

    # Section 2: Introduction
    story.append(Paragraph("2. INTRODUCTION AND PROBLEM STATEMENT", h1_style))
    story.append(Paragraph("Agriculture is the economic backbone of Karnataka, sustaining over 60% of the rural population across diverse agro-climatic zones. However, modern farming operations are severely constrained by: (1) <i>Severe Agrochemical Overuse & Leaching:</i> Over 70% of broadcasted chemicals are lost to wind drift and leaching into Karnataka's water tables; (2) <i>Soil Health Degradation:</i> Over-application of chemical urea and unmonitored soil acidification deplete native microbiomes; and (3) <i>Acute Farm Labor Shortages:</i> Rapid rural-to-urban migration has made manual weeding and spraying prohibitively expensive and hazardous.", body_style))
    story.append(Paragraph("<b>Problem Statement:</b> To design, fabricate, and validate an affordable, open-architecture autonomous agricultural UGV that integrates onboard edge computer vision for plant-level pest and weed micro-spraying, automated in-situ soil nutrient (NPK/pH/moisture) probing, and a 3D WebGL digital twin simulation framework, eliminating chemical wastage and safeguarding rural farmer health.", body_style))

    # Section 3: Literature Survey & Comparative Analysis
    story.append(Paragraph("3. LITERATURE SURVEY & COMPARATIVE ANALYSIS", h1_style))
    comp_table_data = [
        [Paragraph("Metric", table_header_style), Paragraph("Tractor Sprayer", table_header_style), Paragraph("Drone Sprayer", table_header_style), Paragraph("Agri Rover (Proposed)", table_header_style)],
        [Paragraph("Chemical Delivery", table_cell_bold), Paragraph("Blanket broadcast (70-80% wasted)", table_cell_style), Paragraph("Aerial broadcast (High wind drift)", table_cell_style), Paragraph("<b>Targeted AI micro-bursts (Up to 80% saved)</b>", table_cell_style)],
        [Paragraph("Soil Nutrient Sensing", table_cell_bold), Paragraph("None (Requires lab sample testing)", table_cell_style), Paragraph("None (Physically impossible from air)", table_cell_style), Paragraph("<b>Motorized in-situ NPK, pH & moisture probe</b>", table_cell_style)],
        [Paragraph("Operating Domain", table_cell_bold), Paragraph("Open broad-acre (Compaction)", table_cell_style), Paragraph("High-altitude canopy overview", table_cell_style), Paragraph("<b>Direct sub-canopy row navigation (4WD)</b>", table_cell_style)],
        [Paragraph("Simulation Testing", table_cell_bold), Paragraph("Unavailable / Proprietary", table_cell_style), Paragraph("Commercial flight simulator only", table_cell_style), Paragraph("<b>Zero-cost 3D WebGL Digital Twin (Three.js)</b>", table_cell_style)],
        [Paragraph("System Cost & Safety", table_cell_bold), Paragraph("High fuel cost & toxic exposure", table_cell_style), Paragraph("High crash risk & battery cost", table_cell_style), Paragraph("<b>Sub-Rs. 25,000 cost & zero human toxic contact</b>", table_cell_style)],
    ]
    t_comp = Table(comp_table_data, colWidths=[90, 135, 135, 145])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 8))

    # Section 4: Aim & Objectives
    story.append(Paragraph("4. PROJECT AIM AND MEASURABLE OBJECTIVES", h1_style))
    story.append(Paragraph("<b>Project Aim:</b> To develop and field-evaluate 'Agri Rover' — an intelligent cyber-physical autonomous agricultural robotic vehicle powered by a Raspberry Pi 4 edge compute module and a real-time 3D WebGL Digital Twin, delivering precision computer vision-guided targeted pesticide micro-bursts, automated motorized ground soil probing, and hazard-free virtual prototyping.", body_style))
    story.append(Paragraph("<b>1. Rugged 4WD Locomotion:</b> Design a 4-wheel skid-steer chassis driven by 4 high-torque 12V DC geared motors and dual BTS7960 43A H-bridges capable of zero-radius point turns (R = 0) and lane-locked navigation.", bullet_style))
    story.append(Paragraph("<b>2. Edge Computer Vision:</b> Implement real-time Python/OpenCV pipeline on Raspberry Pi 4 detecting pests (purple mask) and weeds (red/green mask) at >15 FPS with spatial centroid error offset calculations.", bullet_style))
    story.append(Paragraph("<b>3. Precision Micro-Burst Spraying:</b> Deploy 12V diaphragm pump and dual directional 12V solenoid valves for calibrated 200ms targeted micro-bursts, cutting chemical usage by up to 80%.", bullet_style))
    story.append(Paragraph("<b>4. In-Situ Soil Probing Array:</b> Construct motorized linear actuator probe mechanism with electrochemical NPK, pH, and moisture sensors with automated motor interlocks.", bullet_style))
    story.append(Paragraph("<b>5. 3D Digital Twin Cockpit:</b> Engineer an interactive browser-based 3D WebGL Digital Twin in React/Three.js with live telemetry, virtual mist particles, and battery fail-safe cutoff (V <= 12.0V).", bullet_style))

    story.append(PageBreak())

    # Section 5: Methodology & Architecture
    story.append(Paragraph("5. DETAILED METHODOLOGY AND SYSTEM ARCHITECTURE", h1_style))
    story.append(Paragraph("Agri Rover follows a modular, event-driven cyber-physical architecture spanning four layers: (1) Perception & Computer Vision, (2) Edge Decision & Kinematics Control, (3) High-Current Physical Actuation, and (4) Digital Twin Simulation & Telemetry.", body_style))
    
    if os.path.exists("extracted_pdf_p10_1__Image73.png"):
        story.append(Image("extracted_pdf_p10_1__Image73.png", width=6.2*inch, height=4.2*inch))
        story.append(Paragraph("Fig. 1: End-to-End Cyber-Physical Architecture of Agri Rover (Raspberry Pi 4 Core)", caption_style))

    story.append(Paragraph("<b>Edge Computer Vision & Actuation Pipeline:</b> The Raspberry Pi 4 processes 1080p camera frames at 640x480 resolution. OpenCV converts frames to HSV color space to decouple illumination variations. Morphological thresholding isolates caterpillars (Purple Mask: H in [130, 160]) and broadleaf weeds (Red Mask). Centroid contours determine whether the Left or Right solenoid opens for a 200ms micro-burst. During soil probing, drive motors are locked, and a motorized linear actuator lowers the probe 50mm into the ground for stabilized NPK/pH/moisture readings.", body_style))

    # Two-column image layout (Camera feed & Wiring schematic)
    col_imgs = []
    if os.path.exists("extracted_pdf_p18_8__Image95.png"):
        img_cam = Image("extracted_pdf_p18_8__Image95.png", width=3.2*inch, height=1.75*inch)
    else:
        img_cam = Paragraph("Camera Feed Image", table_cell_style)
    
    if os.path.exists("extracted_pdf_p19_9__Image98.png"):
        img_wire = Image("extracted_pdf_p19_9__Image98.png", width=3.2*inch, height=1.75*inch)
    else:
        img_wire = Paragraph("Wiring Schematic Image", table_cell_style)

    img_table = Table([[img_cam, img_wire],
                       [Paragraph("Fig. 2: OpenCV Pest/Weed Bounding Box", caption_style),
                        Paragraph("Fig. 3: Raspberry Pi 4 Hardware Pinout", caption_style)]],
                      colWidths=[250, 255])
    img_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(img_table)
    story.append(Spacer(1, 4))

    # 3D Digital Twin & Chassis
    if os.path.exists("extracted_pdf_p18_7__Image94.png"):
        img_sim = Image("extracted_pdf_p18_7__Image94.png", width=3.2*inch, height=1.75*inch)
    else:
        img_sim = Paragraph("Simulator Image", table_cell_style)
        
    if os.path.exists("extracted_pdf_p20_11__Image102.png"):
        img_chas = Image("extracted_pdf_p20_11__Image102.png", width=3.2*inch, height=1.75*inch)
    else:
        img_chas = Paragraph("Chassis Image", table_cell_style)

    img_table2 = Table([[img_sim, img_chas],
                        [Paragraph("Fig. 4: 3D WebGL Digital Twin Simulator", caption_style),
                         Paragraph("Fig. 5: Fabricated 4WD Hardware Chassis", caption_style)]],
                       colWidths=[250, 255])
    img_table2.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(img_table2)

    story.append(PageBreak())

    # Section 6: Technical Specs & Power Budget
    story.append(Paragraph("6. TECHNICAL SPECIFICATIONS & POWER BUDGET", h1_style))
    spec_table_data = [
        [Paragraph("Subsystem", table_header_style), Paragraph("Component", table_header_style), Paragraph("Engineering Specification", table_header_style)],
        [Paragraph("Core Compute", table_cell_bold), Paragraph("Raspberry Pi 4 Model B", table_cell_style), Paragraph("BCM2711 Quad Cortex-A72 @ 1.5GHz, 4GB RAM, Dual-band Wi-Fi", table_cell_style)],
        [Paragraph("Motor Drivers", table_cell_bold), Paragraph("Dual BTS7960 43A", table_cell_style), Paragraph("Dual high-current MOSFET H-bridges, 43A peak, optoisolated inputs", table_cell_style)],
        [Paragraph("Locomotion", table_cell_bold), Paragraph("4x 12V DC Geared Motors", table_cell_style), Paragraph("High-torque planetary metal gearboxes (60 RPM, 15 kg-cm stall)", table_cell_style)],
        [Paragraph("Precision Spray", table_cell_bold), Paragraph("Pump + Solenoids", table_cell_style), Paragraph("12V 4.0L/min 0.6MPa pump; 2x 12V NC brass solenoid valves (<50ms)", table_cell_style)],
        [Paragraph("Soil Diagnostics", table_cell_bold), Paragraph("Linear Actuator + Sensors", table_cell_style), Paragraph("100mm stroke 12V actuator; electrochemical NPK/pH & moisture probe", table_cell_style)],
        [Paragraph("Optics", table_cell_bold), Paragraph("1080p HD Wide-Angle", table_cell_style), Paragraph("OV5647 / USB 1080p sensor, 120° FOV, auto-exposure, row tracking", table_cell_style)],
        [Paragraph("Power Storage", table_cell_bold), Paragraph("12.6V 3S Li-ion / 12V 7Ah", table_cell_style), Paragraph("Rechargeable 3S 18650 pack (20A BMS) or 12V 7Ah SLA; LM2596 buck", table_cell_style)],
        [Paragraph("Failsafe Interlocks", table_cell_bold), Paragraph("Firmware & Watchdog", table_cell_style), Paragraph("1.2s Wi-Fi loss auto-brake, battery cutoff (V<=12.0V), probe motor lock", table_cell_style)]
    ]
    t_spec = Table(spec_table_data, colWidths=[90, 130, 285])
    t_spec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_spec)
    story.append(Spacer(1, 6))

    # Power & Runtime
    story.append(Paragraph("<b>Electrical Power Budget & Battery Runtime:</b> Average current draw is I_avg ≈ 1.8 A at 12.6V bus voltage. With a 12V 7.0Ah battery pack (80% Depth-of-Discharge cutoff):<br/><b>T_runtime = (7.0 Ah × 0.80) / 1.8 A ≈ 3.11 Hours of Continuous Field Operation.</b>", body_style))
    story.append(Spacer(1, 6))

    # Section 7: Budget Table
    story.append(Paragraph("7. ITEMIZED ESTIMATED PROJECT BUDGET", h1_style))
    bgt_table_data = [
        [Paragraph("Sl.", table_header_style), Paragraph("Item Description", table_header_style), Paragraph("Qty", table_header_style), Paragraph("Unit Cost (Rs.)", table_header_style), Paragraph("Total (Rs.)", table_header_style)],
        [Paragraph("1", table_cell_style), Paragraph("Raspberry Pi 4 Model B (4GB RAM) Single Board Computer", table_cell_style), Paragraph("1", table_cell_style), Paragraph("4,800", table_cell_style), Paragraph("4,800", table_cell_style)],
        [Paragraph("2", table_cell_style), Paragraph("Dual BTS7960 43A High-Power H-Bridge Motor Drivers", table_cell_style), Paragraph("2", table_cell_style), Paragraph("650", table_cell_style), Paragraph("1,300", table_cell_style)],
        [Paragraph("3", table_cell_style), Paragraph("High-Torque 12V DC Planetary Geared Motors (60 RPM) + Wheels", table_cell_style), Paragraph("4", table_cell_style), Paragraph("750", table_cell_style), Paragraph("3,000", table_cell_style)],
        [Paragraph("4", table_cell_style), Paragraph("Fabricated 4WD Chassis Frame, Rocker-Bogie Suspension & Hardware", table_cell_style), Paragraph("1 Set", table_cell_style), Paragraph("2,200", table_cell_style), Paragraph("2,200", table_cell_style)],
        [Paragraph("5", table_cell_style), Paragraph("12V DC Diaphragm Chemical Pump & Pressure Tubing Array", table_cell_style), Paragraph("1", table_cell_style), Paragraph("950", table_cell_style), Paragraph("950", table_cell_style)],
        [Paragraph("6", table_cell_style), Paragraph("12V Fast-Acting Directional Brass Solenoid Valves (<50ms)", table_cell_style), Paragraph("2", table_cell_style), Paragraph("600", table_cell_style), Paragraph("1,200", table_cell_style)],
        [Paragraph("7", table_cell_style), Paragraph("Motorized 100mm Linear Actuator for Soil Probe Deployment", table_cell_style), Paragraph("1", table_cell_style), Paragraph("1,850", table_cell_style), Paragraph("1,850", table_cell_style)],
        [Paragraph("8", table_cell_style), Paragraph("Electrochemical NPK, pH & Capacitive Soil Moisture Sensor Array", table_cell_style), Paragraph("1 Set", table_cell_style), Paragraph("2,400", table_cell_style), Paragraph("2,400", table_cell_style)],
        [Paragraph("9", table_cell_style), Paragraph("12.6V 3S Li-ion Battery Pack (20A BMS) + 12.6V 2A Smart Charger", table_cell_style), Paragraph("1", table_cell_style), Paragraph("1,600", table_cell_style), Paragraph("1,600", table_cell_style)],
        [Paragraph("10", table_cell_style), Paragraph("LM2596 Buck Converters, Relays, 1N4007 Diodes, Wiring & Connectors", table_cell_style), Paragraph("1 Set", table_cell_style), Paragraph("1,200", table_cell_style), Paragraph("1,200", table_cell_style)],
    ]
    t_bgt = Table(bgt_table_data, colWidths=[25, 275, 45, 80, 80])
    t_bgt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_bgt)
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>• Total Estimated Hardware & Fabrication Cost: Rs. 20,500/-</b><br/>"
                           "<b>• Amount of Financial Assistance Requested from KSCST (SPP): Rs. 10,000/-</b><br/>"
                           "<b>• Remaining Institutional / Student Contribution: Rs. 10,500/-</b>", body_style))

    story.append(PageBreak())

    # Section 8: Gantt Chart & References
    story.append(Paragraph("8. PROJECT TIMELINE & REFERENCES", h1_style))
    gantt_table_data = [
        [Paragraph("Phase / Milestone Activity", table_header_style), Paragraph("M1-2", table_header_style), Paragraph("M3-4", table_header_style), Paragraph("M5-6", table_header_style), Paragraph("M7-8", table_header_style), Paragraph("M9-10", table_header_style), Paragraph("M11-12", table_header_style)],
        [Paragraph("Literature Survey & Problem Formulation", table_cell_style), Paragraph("<b>[XXXX]</b>", table_cell_bold), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style)],
        [Paragraph("SRS, Architecture & 3D WebGL Digital Twin", table_cell_style), Paragraph("", table_cell_style), Paragraph("<b>[XXXX]</b>", table_cell_bold), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style)],
        [Paragraph("Chassis Fabrication & BTS7960 Motor Kinematics", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("<b>[XXXX]</b>", table_cell_bold), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style)],
        [Paragraph("OpenCV Threat Vision & Solenoid Spray Integration", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("<b>[XXXX]</b>", table_cell_bold), Paragraph("", table_cell_style), Paragraph("", table_cell_style)],
        [Paragraph("Motorized In-Situ Soil Nutrient Probing Subsystem", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("<b>[XXXX]</b>", table_cell_bold), Paragraph("", table_cell_style)],
        [Paragraph("Field Validation, Benchmark & KSCST Final Report", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("<b>[XXXX]</b>", table_cell_bold)],
    ]
    t_gantt = Table(gantt_table_data, colWidths=[205, 50, 50, 50, 50, 50, 50])
    t_gantt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_gantt)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Key References:</b><br/>"
                           "1. Zhang, Q., & Pierce, F. J. (2018). <i>Precision Agriculture Technology for Crop Farming</i>. CRC Press, Taylor & Francis Group.<br/>"
                           "2. Raspberry Pi Foundation. (2024). <i>Raspberry Pi 4 Model B Hardware & RPi.GPIO Documentation</i>.<br/>"
                           "3. OpenCV Team. (2024). <i>OpenCV Image Processing and Computer Vision Reference Manual</i>.<br/>"
                           "4. Mrdoob. (2024). <i>Three.js JavaScript 3D Library Documentation (v0.128.0)</i>.<br/>"
                           "5. United Nations. (2023). <i>Sustainable Development Goals: Goal 2 (Zero Hunger) & Goal 12 (Responsible Consumption)</i>.<br/>"
                           "6. Karnataka State Council for Science and Technology (KSCST). (2026). <i>SPP Guidelines (50th Series)</i>.", body_style))
    story.append(Spacer(1, 10))

    # Section 9: Declarations & Endorsements
    story.append(Paragraph("DECLARATION BY STUDENTS", h1_style))
    story.append(Paragraph("We, the undersigned final year students of the Department of Master of Computer Applications (MCA), BMS Institute of Technology & Management, Bengaluru, hereby declare that the project proposal entitled <b>'Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring'</b> is a bona fide record of independent research and engineering work planned and executed by us under the guidance of Dr. Dwarakanath G V. This proposal has not been submitted previously to any other university or funding agency.", body_style))
    story.append(Spacer(1, 4))

    sig_table_data = [
        [Paragraph("Sl.", table_header_style), Paragraph("Student Name", table_header_style), Paragraph("USN", table_header_style), Paragraph("Signature with Date", table_header_style)],
        [Paragraph("1", table_cell_style), Paragraph("<b>THANMAY M (Team Leader)</b>", table_cell_style), Paragraph("1BY24MC095", table_cell_style), Paragraph("<br/><br/>____________________________", table_cell_style)],
        [Paragraph("2", table_cell_style), Paragraph("KEERTHANA", table_cell_style), Paragraph("1BY24MC045", table_cell_style), Paragraph("<br/><br/>____________________________", table_cell_style)],
        [Paragraph("3", table_cell_style), Paragraph("MOHAN", table_cell_style), Paragraph("1BY24MC058", table_cell_style), Paragraph("<br/><br/>____________________________", table_cell_style)],
        [Paragraph("4", table_cell_style), Paragraph("MONICA", table_cell_style), Paragraph("1BY24MC061", table_cell_style), Paragraph("<br/><br/>____________________________", table_cell_style)],
    ]
    t_sig = Table(sig_table_data, colWidths=[25, 185, 115, 180])
    t_sig.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sig)
    story.append(Spacer(1, 10))

    story.append(Paragraph("ENDORSEMENT BY PROJECT GUIDE, HOD & PRINCIPAL", h1_style))
    story.append(Paragraph("This is to certify that the project proposal entitled <b>'Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring'</b> submitted by Thanmay M, Keerthana, Mohan, and Monica is an original research and engineering endeavor. The project has been reviewed and endorsed for submission under the 50th Series of the Student Project Programme (SPP: 2026–2027) of KSCST.", body_style))
    story.append(Spacer(1, 6))

    end_boxes_data = [
        [
            Paragraph("<b>Signature of Project Guide:</b><br/><br/><br/><br/>___________________________<br/><b>Dr. DWARAKANATH G V</b><br/>Project Coordinator / Assoc. Prof<br/>Dept. of MCA, BMSITM<br/>Date: 26/11/2026", table_cell_style),
            Paragraph("<b>Signature of HOD:</b><br/><br/><br/><br/>___________________________<br/><b>Dr. APARNA K / HOD</b><br/>Head of the Department<br/>Dept. of MCA, BMSITM<br/>Date: 26/11/2026", table_cell_style),
            Paragraph("<b>Signature of Principal:</b><br/><br/><br/><br/>___________________________<br/><b>Dr. MOHAN BABU G N</b><br/>Principal / Head of Institution<br/>BMSITM, Bengaluru<br/>(Official College Seal)", table_cell_style)
        ]
    ]
    t_end = Table(end_boxes_data, colWidths=[165, 170, 170])
    t_end.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_end)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"SUCCESS: {pdf_filename} generated cleanly via ReportLab!")

if __name__ == "__main__":
    build_pdf()
