import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
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
            self.drawString(45, 805, "KSCST 50th Series SPP (2026-2027) | Project Proposal: Agri Rover Robo (BMSITM MCA)")
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

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=15,
        alignment=1,
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
        fontSize=10.5,
        leading=13.5,
        spaceBefore=8,
        spaceAfter=3,
        textColor=colors.HexColor("#1E3A8A")
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        leading=12.5,
        alignment=4,
        spaceAfter=3,
        textColor=colors.HexColor("#1E293B")
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11.5,
        alignment=4,
        leftIndent=10,
        spaceAfter=2,
        textColor=colors.HexColor("#1E293B")
    )

    caption_style = ParagraphStyle(
        'FigCaption',
        parent=styles['Normal'],
        fontName='Times-BoldItalic',
        fontSize=8,
        leading=10,
        alignment=1,
        spaceBefore=2,
        spaceAfter=5,
        textColor=colors.HexColor("#334155")
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0F172A")
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0F172A")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=8,
        leading=10.5,
        alignment=1,
        textColor=colors.white
    )

    story = []

    # Title & Banner
    story.append(Paragraph("KARNATAKA STATE COUNCIL FOR SCIENCE AND TECHNOLOGY (KSCST)", title_style))
    story.append(Paragraph("Indian Institute of Science Campus, Bengaluru – 560012", caption_style))
    story.append(Paragraph("50th SERIES OF THE STUDENT PROJECT PROGRAMME (SPP: 2026–2027)", sub_title_style))
    story.append(Paragraph("PROJECT PROPOSAL FOR POSTGRADUATE (MCA) TEAMS", ParagraphStyle('SubSub', parent=sub_title_style, fontSize=9.5, textColor=colors.HexColor("#1E3A8A"))))
    story.append(Spacer(1, 4))

    # Meta Table
    meta_table_data = [
        [Paragraph("<b>Institution Name:</b>", table_cell_bold), Paragraph("B.M.S. INSTITUTE OF TECHNOLOGY & MANAGEMENT (BMSITM)<br/>Yelahanka, Bengaluru – 560064", table_cell_style)],
        [Paragraph("<b>Department / Stream:</b>", table_cell_bold), Paragraph("Department of Master of Computer Applications (MCA) [Postgraduate]", table_cell_style)],
        [Paragraph("<b>Broad Theme (KSCST):</b>", table_cell_bold), Paragraph("<b>Theme 1: Sustainable Agriculture, Food Security & Rural Development</b><br/>(Cross-Cutting: Theme 4: AI & Digital Tech; Theme 6: Robotics & Automation)", table_cell_style)],
        [Paragraph("<b>Project Proposal Title:</b>", table_cell_bold), Paragraph("<b>Agri Rover Robo - IoT Automation</b>", table_cell_style)],
        [Paragraph("<b>Project Duration:</b>", table_cell_bold), Paragraph("Commencement: 01/10/2025  |  Probable Completion: 31/05/2027", table_cell_style)],
        [Paragraph("<b>KSCST Coordinator:</b>", table_cell_bold), Paragraph("Dr. MANJUNATH, Assistant Professor, Dept. of Mechanical Engineering, BMSITM (manjuc@bmsit.in | 9880744476)", table_cell_style)],
        [Paragraph("<b>Project Guide:</b>", table_cell_bold), Paragraph("Dr. DWARAKANATH G V, Project Coordinator & Assoc. Prof, Dept. of MCA, BMSITM", table_cell_style)],
        [Paragraph("<b>Head of Department:</b>", table_cell_bold), Paragraph("Dr. M. SRIDEVI, Head of the Department, Department of MCA, BMSITM", table_cell_style)]
    ]
    t_meta = Table(meta_table_data, colWidths=[120, 385])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 5))

    # Team Table (Updated: 2 Members)
    story.append(Paragraph("<b>Table 2: Student Project Team Details</b>", caption_style))
    team_table_data = [
        [Paragraph("Sl.", table_header_style), Paragraph("Student Name", table_header_style), Paragraph("USN", table_header_style), Paragraph("Mobile No.", table_header_style), Paragraph("Email ID", table_header_style)],
        [Paragraph("1", table_cell_style), Paragraph("<b>THANMAY M (Team Leader)</b>", table_cell_style), Paragraph("1BY24MC095", table_cell_style), Paragraph("+91 9880123456", table_cell_style), Paragraph("thanmaym08@gmail.com", table_cell_style)],
        [Paragraph("2", table_cell_style), Paragraph("<b>MOHIT S</b>", table_cell_style), Paragraph("1BY24MC063", table_cell_style), Paragraph("+91 9845012345", table_cell_style), Paragraph("mohit.mca@bmsit.in", table_cell_style)]
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
    story.append(Spacer(1, 6))

    # Section 1: Abstract
    story.append(Paragraph("1. PROJECT SUMMARY / ABSTRACT", h1_style))
    story.append(Paragraph("<b>Agri Rover Robo</b> is engineered specifically as a rugged, highly reliable, and affordable smartphone-controlled agricultural robotic vehicle for smallholder farmers. In sharp contrast to heavy industrial autonomous machines ($15,000 to $150,000) that rely on fragile RTK-GPS, LiDAR, and automated path-tracking algorithms that frequently fail in muddy crop rows and dense foliage shadows, Agri Rover Robo completely eliminates autonomous navigation and automated spraying in favor of direct, intuitive human teleoperation via a custom mobile smartphone application.", body_style))
    story.append(Paragraph("The system is engineered strictly around three intended core capabilities: (1) <b>Manual smartphone-controlled 4WD rover locomotion</b> with a virtual touch joystick, supporting smooth forward, reverse, differential steering, and zero-radius point turns; (2) <b>Real-time first-person-view (FPV) camera video streaming</b> directly to the operator's smartphone screen with low latency; and (3) <b>Manual phone-triggered directional precision chemical micro-spraying</b> using independent Left, Right, or Dual spray trigger buttons. Powered by a Raspberry Pi 4 embedded controller, dual BTS7960 43A motor drivers, four 12V high-torque DC geared motors, a 12V diaphragm pump, and dual 12V normally closed direct-acting brass solenoid valves, Agri Rover Robo completely removes the operator from the toxic pesticide drift zone, slashes chemical consumption by 70–80%, and delivers a practical field solution at a target cost under Rs. 20,000.", body_style))

    # Section 2: Introduction
    story.append(Paragraph("2. INTRODUCTION AND PROBLEM STATEMENT", h1_style))
    story.append(Paragraph("Agriculture forms the bedrock of Karnataka's economy, supporting millions of small and marginal farmers across varied cropping belts including cotton, sugarcane, maize, pulses, and horticulture. However, smallholder farmers face severe structural crises: (1) <i>Acute Farmer Occupational Health Hazards:</i> Manual backpack spraying exposes operators directly to toxic pesticide aerosols; (2) <i>Severe Chemical Wastage & Leaching:</i> Unguided broadcast spraying wastes 70–80% of chemicals into groundwater; (3) <i>Extreme Capital Cost & Complexity of Autonomous Robots:</i> Heavy commercial UGVs cost over Rs. 15–90 Lakhs and suffer frequent navigation stalls in muddy furrows.", body_style))
    story.append(Paragraph("<b>Problem Statement:</b> To design, fabricate, and evaluate 'Agri Rover Robo' — an affordable, rugged, smartphone-controlled agricultural robotic vehicle dedicated exclusively to manual smartphone teleoperation, real-time live camera streaming, and manual phone-triggered directional precision chemical micro-spraying, eliminating expensive autonomous sensors while guaranteeing complete operator safety and 70–80% chemical conservation.", body_style))

    # Section 3: Comparative Table
    story.append(Paragraph("3. COMPARATIVE BENCHMARKING OF AGRICULTURAL ROBOTICS", h1_style))
    comp_table_data = [
        [Paragraph("Platform", table_header_style), Paragraph("Drivetrain", table_header_style), Paragraph("Control Mode", table_header_style), Paragraph("Video Streaming", table_header_style), Paragraph("Spraying & Cost", table_header_style)],
        [Paragraph("Farm-ng Amiga", table_cell_bold), Paragraph("4WD Hub Electric", table_cell_style), Paragraph("Gamepad / ROS2", table_cell_style), Paragraph("Optional WebRTC", table_cell_style), Paragraph("Manual boom ($15k+)", table_cell_style)],
        [Paragraph("Naio Oz", table_cell_bold), Paragraph("4WD BLDC Geared", table_cell_style), Paragraph("Autonomous RTK", table_cell_style), Paragraph("No live streaming", table_cell_style), Paragraph("Mechanical hoe (30k Euro)", table_cell_style)],
        [Paragraph("Ecorobotix ARA", table_cell_bold), Paragraph("Tractor Trailed", table_cell_style), Paragraph("Autonomous ISOBUS", table_cell_style), Paragraph("Closed optical loop", table_cell_style), Paragraph("52 micro-valves ($90k+)", table_cell_style)],
        [Paragraph("TerraSentia", table_cell_bold), Paragraph("4WD Skid-Steer", table_cell_style), Paragraph("Autonomous / Tab", table_cell_style), Paragraph("Yes (FPV stream)", table_cell_style), Paragraph("None - Phenotyping ($12k)", table_cell_style)],
        [Paragraph("<b>Agri Rover Robo</b>", table_cell_bold), Paragraph("<b>High-Torque 4WD</b>", table_cell_style), Paragraph("<b>Smartphone App</b>", table_cell_style), Paragraph("<b>Real-Time 1080p</b>", table_cell_style), Paragraph("<b>Phone Solenoids (&lt;Rs 20k)</b>", table_cell_style)],
    ]
    t_comp = Table(comp_table_data, colWidths=[90, 95, 95, 100, 125])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#FEF3C7")),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 6))

    # Section 4: Objectives
    story.append(Paragraph("4. PROJECT AIM AND OBJECTIVES", h1_style))
    story.append(Paragraph("<b>Project Aim:</b> To design, fabricate, and evaluate 'Agri Rover Robo' — an affordable, smartphone-controlled agricultural robotic vehicle dedicated exclusively to manual smartphone teleoperation, real-time live camera streaming, and manual phone-triggered directional precision micro-spraying.", body_style))
    story.append(Paragraph("<b>1. Rugged 4WD Skid-Steer Chassis:</b> Fabricate high-traction 4WD chassis with 4x 12V high-torque DC metal geared motors capable of hauling 10–20 kg of payload through mud.", bullet_style))
    story.append(Paragraph("<b>2. High-Current Motor Driver:</b> Dual BTS7960 43A H-bridges for optically isolated PWM regulation supporting forward, reverse, and zero-radius point turns.", bullet_style))
    story.append(Paragraph("<b>3. Smartphone Teleoperation App:</b> Develop intuitive mobile app with virtual touch joystick, live telemetry, and dedicated Left/Right/Dual micro-spray trigger buttons.", bullet_style))
    story.append(Paragraph("<b>4. Real-Time Video Streaming:</b> Mount 1080p wide-angle camera streaming low-latency (&lt;120ms) sub-canopy video directly to the smartphone screen over dedicated SoftAP Wi-Fi.", bullet_style))
    story.append(Paragraph("<b>5. Precision Chemical Fluidics:</b> Integrate 12V high-pressure diaphragm pump, 2L fluid tank, dual 12V fast-acting brass solenoids (&lt;40ms), and brass misting nozzles.", bullet_style))
    story.append(Paragraph("<b>6. Fail-Safe Interlocks:</b> Enforce 500ms heartbeat watchdog (auto-halt on link loss), under-voltage lockout (V &lt;= 11.1V), and master physical emergency disconnect.", bullet_style))

    story.append(PageBreak())

    # Section 5: Methodology
    story.append(Paragraph("5. DETAILED METHODOLOGY AND SYSTEM ARCHITECTURE", h1_style))
    story.append(Paragraph("Agri Rover Robo operates strictly as a human-in-the-loop cyber-physical system, removing operator exposure while providing complete manual control over navigation and chemical micro-spraying:", body_style))

    if os.path.exists("extracted_pdf_p10_1__Image73.png"):
        story.append(Image("extracted_pdf_p10_1__Image73.png", width=6.2*inch, height=4.0*inch))
        story.append(Paragraph("Fig. 1: End-to-End Cyber-Physical Architecture of Agri Rover Robo (Raspberry Pi 4 Core)", caption_style))

    story.append(Paragraph("<b>Smartphone Mobile Cockpit Application:</b> The operator connects to the rover's high-power local Wi-Fi Access Point ('AgriRobo_Net', IP: 192.168.4.1). No internet or cellular connectivity is required in remote fields. Port 80 serves the touch web application, Port 8080 manages the bi-directional JSON WebSocket control/telemetry pipe at 20 Hz, and Port 8081 delivers the live low-latency MJPEG video feed directly to the operator's viewport.", body_style))

    if os.path.exists("extracted_pdf_p18_8__Image95.png"):
        img_cam = Image("extracted_pdf_p18_8__Image95.png", width=3.2*inch, height=1.75*inch)
    else:
        img_cam = Paragraph("Camera Feed Image", table_cell_style)
    
    if os.path.exists("extracted_pdf_p19_9__Image98.png"):
        img_wire = Image("extracted_pdf_p19_9__Image98.png", width=3.2*inch, height=1.75*inch)
    else:
        img_wire = Paragraph("Wiring Schematic Image", table_cell_style)

    img_table = Table([[img_cam, img_wire],
                       [Paragraph("Fig. 2: Live Smartphone Video Viewport", caption_style),
                        Paragraph("Fig. 3: Raspberry Pi 4 Hardware Pinout", caption_style)]],
                      colWidths=[250, 255])
    img_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(img_table)

    story.append(PageBreak())

    # Section 6: Load & Torque Proof (10-20 kg)
    story.append(Paragraph("6. MECHANICAL LOAD CAPACITY & MOTOR TORQUE PROOF (10–20 KG)", h1_style))
    story.append(Paragraph("To confirm that four 12V DC metal geared motors can reliably haul the rover chassis, 2-liter fluid tank, battery, and electronics across muddy agricultural soil, a rigorous mechanical torque and tractive force calculation was conducted:", body_style))

    mass_table_data = [
        [Paragraph("Subsystem Component", table_header_style), Paragraph("Materials & Description", table_header_style), Paragraph("Mass (kg)", table_header_style)],
        [Paragraph("Chassis Frame & Rocker Suspension", table_cell_bold), Paragraph("Laser-cut 4mm aluminum & acrylic composite plates, fasteners", table_cell_style), Paragraph("3.50 kg", table_cell_style)],
        [Paragraph("Drivetrain Motors & Tires", table_cell_bold), Paragraph("4x 12V DC planetary metal gear motors + 85mm deep-lug tires", table_cell_style), Paragraph("2.10 kg", table_cell_style)],
        [Paragraph("Power Battery Pack", table_cell_bold), Paragraph("12V 7Ah rechargeable battery pack + wiring harness", table_cell_style), Paragraph("2.25 kg", table_cell_style)],
        [Paragraph("Electronics & Enclosure", table_cell_bold), Paragraph("Raspberry Pi 4, Dual BTS7960 43A, relays, buck converters", table_cell_style), Paragraph("1.25 kg", table_cell_style)],
        [Paragraph("Fluidic Hardware (Dry)", table_cell_bold), Paragraph("12V diaphragm pump, 2L tank, dual solenoids, nozzles, lines", table_cell_style), Paragraph("1.40 kg", table_cell_style)],
        [Paragraph("Chemical Liquid Payload", table_cell_bold), Paragraph("Full 2.0-liter water/chemical pesticide liquid mix", table_cell_style), Paragraph("2.00 kg", table_cell_style)],
        [Paragraph("<b>TOTAL OPERATING WEIGHT (Nominal)</b>", table_cell_bold), Paragraph("<b>Nominal fully-loaded operating weight in field</b>", table_cell_style), Paragraph("<b>12.50 kg</b>", table_cell_bold)],
        [Paragraph("<b>MAX GROSS DESIGN WEIGHT</b>", table_cell_bold), Paragraph("<b>Worst-case rating (chassis armor + 5L chemical expansion)</b>", table_cell_style), Paragraph("<b>20.00 kg</b>", table_cell_bold)]
    ]
    t_mass = Table(mass_table_data, colWidths=[145, 275, 85])
    t_mass.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-3), [colors.white, colors.HexColor("#F8FAFC")]),
        ('BACKGROUND', (0,-2), (-1,-2), colors.HexColor("#FEF3C7")),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_mass)
    story.append(Spacer(1, 5))

    story.append(Paragraph("<b>Mathematical Torque Proof (Worst-Case 20.0 kg Mass on 15° Mud Slope):</b><br/>"
                           "• Normal Gravitational Force: F_N = M × g = 20.0 kg × 9.81 m/s² = 196.2 N.<br/>"
                           "• Rolling Resistance on Soft Mud (C_rr = 0.15): F_roll = 0.15 × 196.2 N = 29.43 N.<br/>"
                           "• Hill Climbing Grade Resistance (15° Incline): F_grade = 196.2 N × sin(15°) = 50.78 N.<br/>"
                           "• Total Required Tractive Force: F_total = 29.43 N + 50.78 N = 80.21 N.<br/>"
                           "• Total Axle Torque (85mm wheel diameter, R = 0.0425m): τ_total = 80.21 N × 0.0425m = 3.409 N-m = <b>34.76 kg-cm</b>.<br/>"
                           "• Required Torque per Motor (4WD): <b>τ_motor = 34.76 / 4 = 8.69 kg-cm per motor</b>.<br/>"
                           "• Available Continuous Torque per Motor: <b>15.0 kg-cm</b> (Stall: 35.0 kg-cm; Total 4-motor continuous: <b>60.0 kg-cm</b>).<br/>"
                           "• <b>Safety Factor on 15° Mud Incline: SF = 15.0 / 8.69 = 1.73x (Confirmed Compliant)</b>.<br/>"
                           "• <b>Safety Factor on Level Loose Soil (Req: 3.13 kg-cm): SF = 15.0 / 3.13 = 4.79x (Outstanding Headroom)</b>.", body_style))
    story.append(Spacer(1, 4))

    if os.path.exists("extracted_pdf_p20_11__Image102.png"):
        story.append(Image("extracted_pdf_p20_11__Image102.png", width=4.5*inch, height=2.1*inch))
        story.append(Paragraph("Fig. 4: Fabricated 4WD Hardware Chassis & Dual BTS7960 Motor Driver Stage", caption_style))

    story.append(PageBreak())

    # Section 7: Budget Table
    story.append(Paragraph("7. ITEMIZED ESTIMATED PROJECT BUDGET", h1_style))
    bgt_table_data = [
        [Paragraph("Sl.", table_header_style), Paragraph("Item Description", table_header_style), Paragraph("Qty", table_header_style), Paragraph("Unit Cost (Rs.)", table_header_style), Paragraph("Total (Rs.)", table_header_style)],
        [Paragraph("1", table_cell_style), Paragraph("Raspberry Pi 4 Model B (4GB RAM) Single Board Computer", table_cell_style), Paragraph("1", table_cell_style), Paragraph("4,800", table_cell_style), Paragraph("4,800", table_cell_style)],
        [Paragraph("2", table_cell_style), Paragraph("Dual BTS7960 43A High-Power H-Bridge Motor Drivers", table_cell_style), Paragraph("2", table_cell_style), Paragraph("650", table_cell_style), Paragraph("1,300", table_cell_style)],
        [Paragraph("3", table_cell_style), Paragraph("High-Torque 12V DC Planetary Geared Motors (15 kg-cm) + Tires", table_cell_style), Paragraph("4", table_cell_style), Paragraph("800", table_cell_style), Paragraph("3,200", table_cell_style)],
        [Paragraph("4", table_cell_style), Paragraph("Heavy-Duty 4WD Aluminum/Acrylic Chassis Frame (20kg payload)", table_cell_style), Paragraph("1 Set", table_cell_style), Paragraph("2,500", table_cell_style), Paragraph("2,500", table_cell_style)],
        [Paragraph("5", table_cell_style), Paragraph("12V DC High-Pressure Diaphragm Chemical Pump (4.0 L/min, 0.6 MPa)", table_cell_style), Paragraph("1", table_cell_style), Paragraph("1,100", table_cell_style), Paragraph("1,100", table_cell_style)],
        [Paragraph("6", table_cell_style), Paragraph("12V Fast-Acting Directional Brass Solenoid Valves (&lt;40ms)", table_cell_style), Paragraph("2", table_cell_style), Paragraph("600", table_cell_style), Paragraph("1,200", table_cell_style)],
        [Paragraph("7", table_cell_style), Paragraph("2.0L Chemical Fluid Tank, Pressure Tubing & Atomizing Brass Nozzles", table_cell_style), Paragraph("1 Set", table_cell_style), Paragraph("950", table_cell_style), Paragraph("950", table_cell_style)],
        [Paragraph("8", table_cell_style), Paragraph("1080p HD Wide-Angle Camera Module + Vibration-Damped Mount", table_cell_style), Paragraph("1", table_cell_style), Paragraph("1,500", table_cell_style), Paragraph("1,500", table_cell_style)],
        [Paragraph("9", table_cell_style), Paragraph("12.6V 3S Li-ion Battery Pack (20A BMS) / 12V 7Ah SLA + Smart Charger", table_cell_style), Paragraph("1", table_cell_style), Paragraph("1,800", table_cell_style), Paragraph("1,800", table_cell_style)],
        [Paragraph("10", table_cell_style), Paragraph("LM2596 Buck Converters, Relays, Fusing, Emergency Kill-Switch, Wiring", table_cell_style), Paragraph("1 Set", table_cell_style), Paragraph("1,150", table_cell_style), Paragraph("1,150", table_cell_style)],
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
    story.append(Paragraph("<b>• Total Estimated Hardware & Fabrication Cost: Rs. 19,500/-</b><br/>"
                           "<b>• Amount of Financial Assistance Requested from KSCST (SPP): Rs. 10,000/-</b><br/>"
                           "<b>• Remaining Institutional / Student Contribution: Rs. 9,500/-</b>", body_style))
    story.append(Spacer(1, 6))

    # Section 8: Gantt Chart
    story.append(Paragraph("8. PROJECT IMPLEMENTATION TIMELINE (GANTT CHART)", h1_style))
    gantt_table_data = [
        [Paragraph("Phase / Milestone Activity", table_header_style), Paragraph("M1-2", table_header_style), Paragraph("M3-4", table_header_style), Paragraph("M5-6", table_header_style), Paragraph("M7-8", table_header_style), Paragraph("M9-10", table_header_style), Paragraph("M11-12", table_header_style)],
        [Paragraph("Literature Survey & Benchmarking", table_cell_style), Paragraph("<b>[XXXX]</b>", table_cell_bold), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style)],
        [Paragraph("Chassis CAD & Component Procurement", table_cell_style), Paragraph("", table_cell_style), Paragraph("<b>[XXXX]</b>", table_cell_bold), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style)],
        [Paragraph("Chassis Fabrication & 4WD Drivetrain", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("<b>[XXXX]</b>", table_cell_bold), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style)],
        [Paragraph("Dual BTS7960 & Smartphone App Dev", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("<b>[XXXX]</b>", table_cell_bold), Paragraph("", table_cell_style), Paragraph("", table_cell_style)],
        [Paragraph("Fluidic Sprayer, Pump & Solenoids", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("<b>[XXXX]</b>", table_cell_bold), Paragraph("", table_cell_style)],
        [Paragraph("Field Load Testing (20kg) & Final Report", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("", table_cell_style), Paragraph("<b>[XXXX]</b>", table_cell_bold)],
    ]
    t_gantt = Table(gantt_table_data, colWidths=[205, 50, 50, 50, 50, 50, 50])
    t_gantt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_gantt)

    story.append(PageBreak())

    # Section 9: Declarations & Endorsements (Updated: 2 Members)
    story.append(Paragraph("DECLARATION BY STUDENTS", h1_style))
    story.append(Paragraph("We, the undersigned final year students of the Department of Master of Computer Applications (MCA), BMS Institute of Technology & Management, Bengaluru, hereby declare that the project proposal entitled <b>'Agri Rover Robo - IoT Automation'</b> is a bona fide record of independent research and engineering work planned and executed by us under the guidance of Dr. Dwarakanath G V. This proposal has not been submitted previously to any other university or funding agency.", body_style))
    story.append(Spacer(1, 4))

    sig_table_data = [
        [Paragraph("Sl.", table_header_style), Paragraph("Student Name", table_header_style), Paragraph("USN", table_header_style), Paragraph("Signature with Date", table_header_style)],
        [Paragraph("1", table_cell_style), Paragraph("<b>THANMAY M (Team Leader)</b>", table_cell_style), Paragraph("1BY24MC095", table_cell_style), Paragraph("<br/><br/>____________________________", table_cell_style)],
        [Paragraph("2", table_cell_style), Paragraph("<b>MOHIT S</b>", table_cell_style), Paragraph("1BY24MC063", table_cell_style), Paragraph("<br/><br/>____________________________", table_cell_style)]
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

    story.append(Paragraph("ENDORSEMENT BY PROJECT GUIDE, HOD & HEAD OF INSTITUTION", h1_style))
    story.append(Paragraph("This is to certify that the project proposal entitled <b>'Agri Rover Robo - IoT Automation'</b> submitted by Thanmay M and Mohit S is an original research and engineering endeavor. The project has been reviewed and endorsed for submission under the 50th Series of the Student Project Programme (SPP: 2026–2027) of KSCST.", body_style))
    story.append(Spacer(1, 6))

    end_boxes_data = [
        [
            Paragraph("<b>Signature of Project Guide:</b><br/><br/><br/><br/>___________________________<br/><b>Dr. DWARAKANATH G V</b><br/>Project Coordinator / Assoc. Prof<br/>Dept. of MCA, BMSITM<br/>Date: 26/11/2026", table_cell_style),
            Paragraph("<b>Signature of HOD:</b><br/><br/><br/><br/>___________________________<br/><b>Dr. M. SRIDEVI</b><br/>Head of the Department<br/>Dept. of MCA, BMSITM<br/>Date: 26/11/2026", table_cell_style),
            Paragraph("<b>Signature of Principal:</b><br/><br/><br/><br/>___________________________<br/><b>Dr. SANJAY H.A</b><br/>Principal / Head of Institution<br/>BMSITM, Bengaluru<br/>(Official College Seal)", table_cell_style)
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
