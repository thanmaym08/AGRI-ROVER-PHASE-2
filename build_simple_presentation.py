import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_simple_deck(output_path="Agri_Rover_Project_Presentation.pptx"):
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Select authentic project image from report (without solar panels)
    # Using the real field chassis photo
    image_path = os.path.join("assets", "agrirover_hardware_chassis.png")
    if not os.path.exists(image_path):
        image_path = os.path.join("assets", "agrirover_cad_mockup.png")

    # Clean, modern, accessible color palette
    BG_COLOR = RGBColor(15, 23, 42)         # #0F172A Dark Slate
    CARD_BG = RGBColor(30, 41, 59)          # #1E293B Clean Card
    CARD_BORDER = RGBColor(51, 65, 85)      # #334155 Subtle Border
    
    PRIMARY_GREEN = RGBColor(34, 197, 94)   # #22C55E Emerald Green
    ACCENT_CYAN = RGBColor(56, 189, 248)    # #38BDF8 Sky Blue
    ACCENT_AMBER = RGBColor(245, 158, 11)   # #F59E0B Warm Amber
    
    TEXT_MAIN = RGBColor(248, 250, 252)     # #F8FAFC Bright White
    TEXT_MUTED = RGBColor(203, 213, 225)    # #CBD5E1 High-readability light gray
    TEXT_DIM = RGBColor(148, 163, 184)      # #94A3B8 Dim label

    def set_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, tag_text, title_text, subtitle_text):
        # Category pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.45), Inches(2.2), Inches(0.32))
        pill.fill.solid()
        pill.fill.fore_color.rgb = RGBColor(20, 45, 35)
        pill.line.color.rgb = PRIMARY_GREEN
        pill.line.width = Pt(1)
        tf_p = pill.text_frame
        tf_p.word_wrap = False
        p_p = tf_p.paragraphs[0]
        p_p.text = tag_text.upper()
        p_p.font.size = Pt(9.5)
        p_p.font.bold = True
        p_p.font.color.rgb = PRIMARY_GREEN
        p_p.font.name = "Calibri"
        p_p.alignment = PP_ALIGN.CENTER

        # Title
        tx_t = slide.shapes.add_textbox(Inches(0.8), Inches(0.82), Inches(11.7), Inches(0.55))
        tf_t = tx_t.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN
        p_t.font.name = "Calibri"

        # Subtitle
        tx_s = slide.shapes.add_textbox(Inches(0.8), Inches(1.36), Inches(11.7), Inches(0.35))
        tf_s = tx_s.text_frame
        tf_s.word_wrap = True
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle_text
        p_s.font.size = Pt(11.5)
        p_s.font.color.rgb = TEXT_MUTED
        p_s.font.name = "Calibri"

        # Divider
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.75), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = CARD_BORDER
        line.line.fill.background()

    def add_footer(slide, current_slide, total_slides=7):
        tx = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(10.0), Inches(0.3))
        p = tx.text_frame.paragraphs[0]
        p.text = "AGRI ROVER  •  Department of MCA, BMSITM, Bengaluru"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DIM
        p.font.name = "Calibri"

        tx_pg = slide.shapes.add_textbox(Inches(11.2), Inches(7.05), Inches(1.333), Inches(0.3))
        p_pg = tx_pg.text_frame.paragraphs[0]
        p_pg.text = f"{current_slide} / {total_slides}"
        p_pg.alignment = PP_ALIGN.RIGHT
        p_pg.font.size = Pt(10)
        p_pg.font.color.rgb = PRIMARY_GREEN
        p_pg.font.bold = True
        p_pg.font.name = "Calibri"

    def make_card(slide, left, top, width, height, border_col=CARD_BORDER, bg_col=CARD_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_col
        card.line.color.rgb = border_col
        card.line.width = Pt(1.2)
        return card

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (Clean & Clear)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_bg(slide1)

    # Accent bar
    bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.65), Inches(2.5), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = PRIMARY_GREEN
    bar.line.fill.background()

    # College tag
    tx_c = slide1.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.35))
    p_c = tx_c.text_frame.paragraphs[0]
    p_c.text = "BMS INSTITUTE OF TECHNOLOGY & MANAGEMENT  |  DEPARTMENT OF MCA"
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = ACCENT_CYAN
    p_c.font.name = "Calibri"

    # Main Project Title
    tx_t = slide1.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(1.3))
    tf_t = tx_t.text_frame
    tf_t.word_wrap = True
    p1 = tf_t.paragraphs[0]
    p1.text = "AGRI ROVER"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_MAIN
    p1.font.name = "Calibri"

    p2 = tf_t.add_paragraph()
    p2.text = "Autonomous IoT Agricultural Rover for Precision Crop Care & Soil Moisture Monitoring"
    p2.font.size = Pt(16.5)
    p2.font.color.rgb = PRIMARY_GREEN
    p2.font.name = "Calibri"

    # Two Student Cards
    card1 = make_card(slide1, Inches(0.8), Inches(2.9), Inches(5.6), Inches(2.5), PRIMARY_GREEN)
    tx_s1 = slide1.shapes.add_textbox(Inches(1.1), Inches(3.1), Inches(5.0), Inches(2.1))
    tf1 = tx_s1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "STUDENT DEVELOPER 1"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GREEN
    
    p = tf1.add_paragraph()
    p.text = "[Student 1 Name]"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    
    p = tf1.add_paragraph()
    p.text = "USN: [Enter USN 1]\nMaster of Computer Applications (MCA)\nRole: Hardware Interfacing, Motor Control & Spray Mechanism"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    card2 = make_card(slide1, Inches(6.9), Inches(2.9), Inches(5.6), Inches(2.5), ACCENT_CYAN)
    tx_s2 = slide1.shapes.add_textbox(Inches(7.2), Inches(3.1), Inches(5.0), Inches(2.1))
    tf2 = tx_s2.text_frame
    tf2.word_wrap = True
    
    p = tf2.paragraphs[0]
    p.text = "STUDENT DEVELOPER 2"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    
    p = tf2.add_paragraph()
    p.text = "[Student 2 Name]"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    
    p = tf2.add_paragraph()
    p.text = "USN: [Enter USN 2]\nMaster of Computer Applications (MCA)\nRole: OpenCV Vision, Web Application & 3D Digital Twin"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    # Guide Card
    guide = make_card(slide1, Inches(0.8), Inches(5.65), Inches(11.733), Inches(1.0), CARD_BORDER)
    tx_g = slide1.shapes.add_textbox(Inches(1.1), Inches(5.75), Inches(11.1), Inches(0.8))
    tf_g = tx_g.text_frame
    tf_g.word_wrap = True
    p = tf_g.paragraphs[0]
    p.text = "PROJECT GUIDE:  [Enter Project Guide Name, Designation]"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p = tf_g.add_paragraph()
    p.text = "Department of MCA, BMS Institute of Technology & Management (VTU Affiliated), Bengaluru"
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    slide1.notes_slide.notes_text_frame.text = (
        "SLIDE 1 TALKING POINTS:\n"
        "• Greet the judges and introduce yourselves with your names and USNs.\n"
        "• State project title clearly: 'Agri Rover — Autonomous IoT Agricultural Rover for Precision Crop Care and Soil Moisture Monitoring'.\n"
        "• Explain the goal: To help small farmers reduce pesticide wastage using smart edge camera detection, targeted spraying, and real-time soil moisture monitoring."
    )
    add_footer(slide1, 1)

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT & UN SDGs (Simple & High Impact)
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_bg(slide2)
    add_header(slide2, "Problem & SDGs", "Agricultural Challenges & UN SDG Alignment", "Why traditional farming needs precision technology and how our project helps")

    # Left: 3 Core Problems
    left_w = Inches(5.6)
    make_card(slide2, Inches(0.8), Inches(1.95), left_w, Inches(4.7), RGBColor(239, 68, 68))
    tx_p = slide2.shapes.add_textbox(Inches(1.05), Inches(2.1), left_w - Inches(0.5), Inches(4.3))
    tf_p = tx_p.text_frame
    tf_p.word_wrap = True

    p = tf_p.paragraphs[0]
    p.text = "KEY AGRICULTURAL CHALLENGES"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(248, 113, 113)

    probs = [
        ("Huge Chemical Wastage (70-80%)", "Traditional sprayers broadcast pesticides across the entire field indiscriminately, wasting chemicals on bare ground and healthy plants."),
        ("Health Risks for Farmers", "Manual backpack spraying causes direct inhalation of toxic chemicals, leading to respiratory and skin diseases."),
        ("Lack of Soil Moisture Information", "Farmers often over-water or under-water crops because they have no quick way to test ground soil moisture in the field.")
    ]

    for title, desc in probs:
        p = tf_p.add_paragraph()
        p.text = f"\n•  {title}"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p = tf_p.add_paragraph()
        p.text = desc
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # Right: UN SDGs
    right_x = Inches(6.8)
    right_w = Inches(5.733)
    make_card(slide2, right_x, Inches(1.95), right_w, Inches(4.7), PRIMARY_GREEN)
    tx_s = slide2.shapes.add_textbox(right_x + Inches(0.25), Inches(2.1), right_w - Inches(0.5), Inches(4.3))
    tf_s = tx_s.text_frame
    tf_s.word_wrap = True

    p = tf_s.paragraphs[0]
    p.text = "UNITED NATIONS SDG ALIGNMENT"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GREEN

    sdg_list = [
        ("SDG 2: Zero Hunger (Target 2.4)", "Promotes sustainable and resilient agriculture by protecting crops from weeds and pests while monitoring soil health for better yields."),
        ("SDG 12: Responsible Consumption (Target 12.4)", "Drastically reduces chemical runoff into water bodies by cutting pesticide usage up to 80% through targeted spraying."),
        ("SDG 15: Life on Land", "Protects beneficial insects and soil microbial life by stopping unnecessary chemical flooding.")
    ]

    for title, desc in sdg_list:
        p = tf_s.add_paragraph()
        p.text = f"\n•  {title}"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p = tf_s.add_paragraph()
        p.text = desc
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    slide2.notes_slide.notes_text_frame.text = (
        "SLIDE 2 TALKING POINTS:\n"
        "• Problem: Explain that 70-80% of pesticides are wasted during manual or tractor spraying. This pollutes groundwater and harms the farmer's lungs.\n"
        "• Mention the lack of soil moisture data: Farmers irrigate blindly without knowing if the soil actually needs water.\n"
        "• SDGs: Highlight SDG 2 (Zero Hunger) and SDG 12 (Responsible Consumption). We cut 80% of chemical usage and protect the soil."
    )
    add_footer(slide2, 2)

    # =========================================================================
    # SLIDE 3: SYSTEM COMPONENTS (HARDWARE & SOFTWARE)
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_bg(slide3)
    add_header(slide3, "System Components", "What We Use: Hardware & Software Stack", "Simple, reliable, off-the-shelf components connected in a unified IoT framework")

    col_w = Inches(5.6)

    # Hardware Card
    make_card(slide3, Inches(0.8), Inches(1.95), col_w, Inches(4.7), ACCENT_CYAN)
    tx_hw = slide3.shapes.add_textbox(Inches(1.05), Inches(2.1), col_w - Inches(0.5), Inches(4.3))
    tf_hw = tx_hw.text_frame
    tf_hw.word_wrap = True

    p = tf_hw.paragraphs[0]
    p.text = "HARDWARE ON THE ROVER"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    hw_items = [
        ("ESP32-CAM Microcontroller", "Dual-core processor with onboard OV2640 camera for live Wi-Fi video streaming and motor control."),
        ("4-Wheel Skid-Steer Drivetrain", "4 DC geared motors powered by an L298N motor driver, allowing in-place zero-radius turns inside narrow crop rows."),
        ("Precision Spraying System", "12V high-pressure diaphragm pump connected via a 5V relay module for short, calibrated 200ms chemical bursts."),
        ("Soil Moisture Sensor", "Analog/digital ground moisture probe to test and log real-time soil hydration directly from the field."),
        ("Power Supply", "12V rechargeable battery with LM2596 step-down converter providing stable 5V power.")
    ]

    for title, desc in hw_items:
        p = tf_hw.add_paragraph()
        p.text = f"\n• {title}: "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        run = p.add_run(desc)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Software Card
    right_x = Inches(6.8)
    make_card(slide3, right_x, Inches(1.95), Inches(5.733), Inches(4.7), PRIMARY_GREEN)
    tx_sw = slide3.shapes.add_textbox(right_x + Inches(0.25), Inches(2.1), Inches(5.2), Inches(4.3))
    tf_sw = tx_sw.text_frame
    tf_sw.word_wrap = True

    p = tf_sw.paragraphs[0]
    p.text = "SOFTWARE & AI TOOLS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GREEN

    sw_items = [
        ("ESP32 Firmware (C++ / Arduino)", "Runs video streaming, handles Wi-Fi web requests, and executes motor commands and relay pulses."),
        ("OpenCV Computer Vision (Python)", "Processes live camera feed using color segmentation to instantly detect green weeds and leaf pests."),
        ("Mobile Web Controller (HMI)", "Responsive web app allowing the farmer to steer the rover, view the camera feed, and trigger spraying from a phone."),
        ("3D WebGL Digital Twin (Three.js)", "Interactive browser-based 3D simulator to test vehicle movement, steering, and spraying virtually without risk.")
    ]

    for title, desc in sw_items:
        p = tf_sw.add_paragraph()
        p.text = f"\n• {title}: "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        run = p.add_run(desc)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    slide3.notes_slide.notes_text_frame.text = (
        "SLIDE 3 TALKING POINTS:\n"
        "• Emphasize simplicity: We use the ESP32-CAM as our core onboard controller.\n"
        "• Hardware: 4 DC geared motors for skid-steer navigation, a 12V pump with relay for spraying, and a soil moisture sensor to test soil dampness.\n"
        "• Software: Python OpenCV for weed/pest detection, a simple smartphone web app to control the rover, and a Three.js 3D simulation for safe testing."
    )
    add_footer(slide3, 3)

    # =========================================================================
    # SLIDE 4: BLUEPRINT & WORKING MECHANISM (AUTHENTIC IMAGE)
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_bg(slide4)
    add_header(slide4, "Blueprint & Working Mechanism", "Agri Rover Blueprint & How It Works", "Physical vehicle configuration without solar panels and simple 4-step operation")

    # Left: Rover Image
    img_left = Inches(0.8)
    img_top = Inches(1.95)
    img_w = Inches(5.6)
    img_h = Inches(4.7)

    make_card(slide4, img_left, img_top, img_w, img_h, PRIMARY_GREEN)
    if os.path.exists(image_path):
        slide4.shapes.add_picture(image_path, img_left + Inches(0.12), img_top + Inches(0.12), img_w - Inches(0.24), img_h - Inches(0.65))
        cap = slide4.shapes.add_textbox(img_left + Inches(0.12), img_top + img_h - Inches(0.5), img_w - Inches(0.24), Inches(0.4))
        p = cap.text_frame.paragraphs[0]
        p.text = "Fig 1: Agri Rover Prototype (Open chassis showing camera, spray nozzles & moisture probe)"
        p.font.size = Pt(9)
        p.font.color.rgb = TEXT_MUTED
        p.alignment = PP_ALIGN.CENTER

    # Right: 4-Step How it Works
    right_x = Inches(6.8)
    right_w = Inches(5.733)

    steps = [
        ("1. Navigate Crop Rows", "Rover navigates between narrow crop rows (50–70cm) using 4-wheel skid-steer control from a smartphone or auto guidance.", ACCENT_CYAN),
        ("2. Spot Pests & Weeds", "ESP32-CAM streams real-time video to OpenCV. Color segmentation detects weed patches and pest-damaged leaves.", PRIMARY_GREEN),
        ("3. Precision Micro-Spray", "Upon detection, the relay activates the pump for a quick 200ms burst directly on the target. Healthy crops receive 0% chemical.", ACCENT_AMBER),
        ("4. Check Soil Moisture", "The soil moisture sensor checks the moisture level of the soil and displays the readings on the farmer's dashboard.", RGBColor(168, 85, 247))
    ]

    for i, (title, desc, col) in enumerate(steps):
        y_pos = Inches(1.95 + i*1.2)
        make_card(slide4, right_x, y_pos, right_w, Inches(1.1), col)
        
        # Number badge
        badge = slide4.shapes.add_shape(MSO_SHAPE.OVAL, right_x + Inches(0.15), y_pos + Inches(0.15), Inches(0.35), Inches(0.35))
        badge.fill.solid()
        badge.fill.fore_color.rgb = col
        badge.line.fill.background()
        tf_b = badge.text_frame
        p_b = tf_b.paragraphs[0]
        p_b.text = str(i + 1)
        p_b.font.size = Pt(11)
        p_b.font.bold = True
        p_b.font.color.rgb = BG_COLOR
        p_b.alignment = PP_ALIGN.CENTER

        tx = slide4.shapes.add_textbox(right_x + Inches(0.6), y_pos + Inches(0.08), right_w - Inches(0.7), Inches(0.95))
        tf = tx.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(11.5)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = TEXT_MUTED

    slide4.notes_slide.notes_text_frame.text = (
        "SLIDE 4 TALKING POINTS:\n"
        "• Point to the image: This is our rover prototype without solar panels, showing the open frame, camera mount, pesticide tank, and spray nozzles.\n"
        "• Walk through the 4 steps clearly:\n"
        "  1. Steer between crop rows.\n"
        "  2. Camera detects pests and weeds via OpenCV.\n"
        "  3. Pump sprays a 200ms targeted burst only where needed.\n"
        "  4. Soil moisture sensor checks ground dampness so farmers know when to irrigate."
    )
    add_footer(slide4, 4)

    # =========================================================================
    # SLIDE 5: COST ADVANTAGE & WHY IT'S DIFFERENT
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_bg(slide5)
    add_header(slide5, "Cost Factor & Innovation", "Why Agri Rover is Different: Cost & Impact", "Affordable precision agriculture designed specifically for small and medium farmers")

    # 4 Quick Stat Badges
    stats = [
        ("₹5,000 – ₹10,000", "Affordable Prototype Build Cost", PRIMARY_GREEN),
        ("80% SAVINGS", "Reduction in Chemical Pesticides", ACCENT_CYAN),
        ("ZERO INHALATION", "Remote Control Protects Health", ACCENT_AMBER),
        ("SOIL CHECK", "Instant Moisture Monitoring", RGBColor(168, 85, 247))
    ]
    for i, (val, lbl, col) in enumerate(stats):
        make_card(slide5, Inches(0.8 + i*2.98), Inches(1.95), Inches(2.8), Inches(0.85), col)
        tx = slide5.shapes.add_textbox(Inches(0.9 + i*2.98), Inches(2.0), Inches(2.6), Inches(0.75))
        tf = tx.text_frame
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col
        p = tf.add_paragraph()
        p.text = lbl
        p.font.size = Pt(8.5)
        p.font.color.rgb = TEXT_MUTED

    # Comparison Table (Simple & Clean)
    tbl_shape = slide5.shapes.add_table(5, 4, Inches(0.8), Inches(3.0), Inches(11.733), Inches(3.6))
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(2.4)
    tbl.columns[1].width = Inches(3.1)
    tbl.columns[2].width = Inches(3.1)
    tbl.columns[3].width = Inches(3.133)

    headers = ["Feature", "Manual / Tractor Spraying", "Agricultural Drones", "Agri Rover (Our Project)"]
    for col_idx, h in enumerate(headers):
        cell = tbl.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(20, 45, 35) if col_idx == 3 else RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_GREEN if col_idx == 3 else TEXT_MAIN
        p.alignment = PP_ALIGN.CENTER

    rows = [
        ("Total Cost", "Very High: ₹15L–₹30L+ (or labor intensive)", "High: ₹6L–₹12L+", "Low: ₹5,000–₹10,000 (Very Affordable)"),
        ("Chemical Wastage", "High: 70–80% wasted on soil and healthy crops", "Moderate: High wind drift losses", "Minimal: Up to 80% saved via micro-bursts"),
        ("Soil Moisture Check", "None (Farmer must guess)", "None (Drones cannot touch the ground)", "Included: Real-time ground moisture sensor"),
        ("Farmer Safety", "Dangerous: Direct chemical inhalation", "Safe: Flown remotely", "Safe: Remote control via smartphone")
    ]

    for row_idx, r_data in enumerate(rows, start=1):
        for col_idx, val in enumerate(r_data):
            cell = tbl.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(25, 36, 52) if col_idx == 3 else RGBColor(19, 30, 48)
            cell.text_frame.word_wrap = True
            cell.text_frame.margin_left = Inches(0.12)
            cell.text_frame.margin_right = Inches(0.12)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(10)
            p.font.bold = (col_idx == 3 or col_idx == 0)
            p.font.color.rgb = PRIMARY_GREEN if col_idx == 3 else (TEXT_MAIN if col_idx == 0 else TEXT_MUTED)

    slide5.notes_slide.notes_text_frame.text = (
        "SLIDE 5 TALKING POINTS:\n"
        "• Focus on the cost factor: Commercial drones cost ₹6 to ₹12 Lakhs and spray from above where wind causes drift. Tractors cost ₹20+ Lakhs.\n"
        "• Agri Rover costs less than ₹10,000 to build, drives at plant level to spray under the leaves, and includes a soil moisture sensor that drones cannot offer.\n"
        "• The 80% pesticide savings means the rover pays for itself in just a few harvests."
    )
    add_footer(slide5, 5)

    # =========================================================================
    # SLIDE 6: WHAT EXTERNAL JUDGES LOOK FOR (Evaluation Defense)
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_bg(slide6)
    add_header(slide6, "Evaluation & Defense", "What External Judges Look For & How We Deliver", "Key points that prove practical engineering, safety, and live demo readiness")

    eval_cards = [
        ("1. Real Hardware & Software Integration", [
            "We have not just built a model; our ESP32-CAM genuinely controls the motors and pump while streaming live video.",
            "OpenCV computer vision communicates with the rover to trigger the 200ms spray relay automatically."
        ], ACCENT_CYAN),
        ("2. Real-World Farmer Impact", [
            "Solves real Indian agricultural challenges: cuts chemical pesticide expenses by up to 80%.",
            "Eliminates health hazards by keeping the farmer away from toxic chemical spray."
        ], PRIMARY_GREEN),
        ("3. Soil Health Awareness", [
            "Includes a dedicated soil moisture sensor that reports ground water levels in real-time.",
            "Helps farmers make informed decisions about when to irrigate and when to spray."
        ], ACCENT_AMBER),
        ("4. Live Demo & Virtual Testing", [
            "Full live demo available: Smartphone web control, live camera video feed, and spray actuation.",
            "Supported by a 3D Digital Twin simulation for testing vehicle movement safely in a virtual field."
        ], RGBColor(168, 85, 247))
    ]

    for i, (title, bullets, col) in enumerate(eval_cards):
        row = i // 2
        col_idx = i % 2
        x = Inches(0.8 + col_idx*5.95)
        y = Inches(1.95 + row*2.4)
        w = Inches(5.78)
        h = Inches(2.25)

        make_card(slide6, x, y, w, h, col)
        tx = slide6.shapes.add_textbox(x + Inches(0.2), y + Inches(0.12), w - Inches(0.4), h - Inches(0.2))
        tf = tx.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col

        for b in bullets:
            p = tf.add_paragraph()
            p.text = f"✔  {b}"
            p.font.size = Pt(9.8)
            p.font.color.rgb = TEXT_MUTED

    slide6.notes_slide.notes_text_frame.text = (
        "SLIDE 6 TALKING POINTS:\n"
        "• Be prepared for judge questions:\n"
        "  - 'Is this actually working or just a concept?' -> 'Yes, we have live motor control, camera streaming, spray relay actuation, and live soil moisture logging.'\n"
        "  - 'Why only a soil moisture sensor?' -> 'Moisture is the primary daily metric a farmer needs before spraying or irrigating. It keeps the design practical, rugged, and low-cost.'\n"
        "  - 'How do you test it safely?' -> 'We use our 3D Digital Twin simulator to verify steering and lane keeping before testing in mud.'"
    )
    add_footer(slide6, 6)

    # =========================================================================
    # SLIDE 7: CONCLUSION & FUTURE SCOPE
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_bg(slide7)
    add_header(slide7, "Conclusion & Roadmap", "Summary of Achievements & Next Steps", "Delivering accessible IoT technology to transform everyday farming")

    # Left: Achievements
    make_card(slide7, Inches(0.8), Inches(1.95), Inches(5.6), Inches(3.6), PRIMARY_GREEN)
    tx_ach = slide7.shapes.add_textbox(Inches(1.05), Inches(2.1), Inches(5.1), Inches(3.3))
    tf_ach = tx_ach.text_frame
    tf_ach.word_wrap = True

    p = tf_ach.paragraphs[0]
    p.text = "PROJECT ACHIEVEMENTS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GREEN

    achs = [
        "80% Pesticide Reduction: Verified 200ms targeted spray bursts to eliminate broadcast chemical waste.",
        "Zero Operator Exposure: Remote smartphone teleoperation keeps farmers safe from toxic inhalation.",
        "Soil Moisture Monitoring: Real-time ground sensor provides instant soil hydration data.",
        "3D Digital Twin: Safe browser-based virtual simulator for testing rover navigation."
    ]
    for ach in achs:
        p = tf_ach.add_paragraph()
        p.text = f"\n✔  {ach}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED

    # Right: Future Scope
    make_card(slide7, Inches(6.8), Inches(1.95), Inches(5.733), Inches(3.6), ACCENT_CYAN)
    tx_fut = slide7.shapes.add_textbox(Inches(7.05), Inches(2.1), Inches(5.2), Inches(3.3))
    tf_fut = tx_fut.text_frame
    tf_fut.word_wrap = True

    p = tf_fut.paragraphs[0]
    p.text = "FUTURE ENHANCEMENTS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    futs = [
        "Advanced AI (YOLOv8): Upgrading from color detection to deep learning object detection for disease recognition.",
        "Autonomous GPS Navigation: Adding GPS waypoints so the rover can patrol fields completely autonomously.",
        "Solar Trickle Charger: Adding a small auxiliary solar panel on top for continuous daytime battery recharging."
    ]
    for fut in futs:
        p = tf_fut.add_paragraph()
        p.text = f"\n🚀  {fut}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED

    # Bottom Banner: Thank You
    make_card(slide7, Inches(0.8), Inches(5.75), Inches(11.733), Inches(1.1), ACCENT_AMBER)
    tx_ty = slide7.shapes.add_textbox(Inches(1.05), Inches(5.85), Inches(11.2), Inches(0.9))
    tf_ty = tx_ty.text_frame
    tf_ty.word_wrap = True
    p = tf_ty.paragraphs[0]
    p.text = "THANK YOU  |  QUESTIONS & DISCUSSION"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.alignment = PP_ALIGN.CENTER
    p = tf_ty.add_paragraph()
    p.text = "Ready for live demonstration: Mobile Controller, Video Stream & 3D Simulation\nMCA Project Team (MMCA34, 2025–2027) • BMSITM Bengaluru"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MAIN
    p.alignment = PP_ALIGN.CENTER

    slide7.notes_slide.notes_text_frame.text = (
        "SLIDE 7 TALKING POINTS:\n"
        "• Summarize achievements: We built an affordable rover that cuts pesticide waste by 80%, keeps farmers safe, and checks soil moisture.\n"
        "• Mention future scope: Adding YOLOv8 object detection and GPS navigation.\n"
        "• Thank the judges and invite them to see the live demonstration!"
    )
    add_footer(slide7, 7)

    prs.save(output_path)
    print(f"Simple presentation saved successfully to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    create_simple_deck()
