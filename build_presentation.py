import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path="Agri_Rover_Project_Presentation.pptx"):
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Authentic project images extracted from previous project report
    cad_image_path = os.path.join("assets", "agrirover_cad_mockup.png")
    chassis_image_path = os.path.join("assets", "agrirover_hardware_chassis.png")

    # Brand Colors (Professional Agritech Dark Theme)
    BG_COLOR = RGBColor(11, 19, 43)        # #0B132B Deep Tech Navy
    CARD_BG = RGBColor(26, 38, 57)         # #1A2639 Container Box
    CARD_BORDER = RGBColor(46, 64, 87)     # #2E4057 Subtle Stroke
    CARD_BG_ALT = RGBColor(19, 30, 48)     # Darker surface box
    
    PRIMARY_GREEN = RGBColor(34, 197, 94)  # #22C55E Emerald / Tech Green
    ACCENT_CYAN = RGBColor(56, 189, 248)   # #38BDF8 Cyan
    ACCENT_GOLD = RGBColor(245, 158, 11)   # #F59E0B Amber
    ACCENT_PURPLE = RGBColor(168, 85, 247) # #A855F7 Purple
    
    TEXT_LIGHT = RGBColor(248, 250, 252)   # #F8FAFC Heading text
    TEXT_MUTED = RGBColor(148, 163, 184)   # #94A3B8 Secondary text
    TEXT_DIM = RGBColor(100, 116, 139)     # #64748B Dim label text

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, category, title, subtitle):
        # Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.42), Inches(2.4), Inches(0.32))
        badge.fill.solid()
        badge.fill.fore_color.rgb = RGBColor(16, 45, 38)
        badge.line.color.rgb = PRIMARY_GREEN
        badge.line.width = Pt(1)
        tf_b = badge.text_frame
        tf_b.word_wrap = False
        tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = 0
        p_b = tf_b.paragraphs[0]
        p_b.text = category.upper()
        p_b.font.size = Pt(9.5)
        p_b.font.bold = True
        p_b.font.color.rgb = PRIMARY_GREEN
        p_b.font.name = "Calibri"
        p_b.alignment = PP_ALIGN.CENTER

        # Title
        tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.7), Inches(0.55))
        tf_t = tx_title.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_LIGHT
        p_t.font.name = "Calibri"

        # Subtitle
        tx_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.35))
        tf_s = tx_sub.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = tf_s.margin_right = tf_s.margin_top = tf_s.margin_bottom = 0
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle
        p_s.font.size = Pt(11)
        p_s.font.color.rgb = TEXT_MUTED
        p_s.font.name = "Calibri"

        # Horizontal accent line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.72), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = CARD_BORDER
        line.line.fill.background()

    def add_footer(slide, current_slide, total_slides=7):
        tx = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
        tf = tx.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = f"AGRI ROVER | Autonomous IoT Agricultural Vehicle — Phase II Presentation  •  BMSITM Bangalore"
        p.font.size = Pt(9)
        p.font.color.rgb = TEXT_DIM
        p.font.name = "Calibri"

        tx_pg = slide.shapes.add_textbox(Inches(11.0), Inches(7.05), Inches(1.533), Inches(0.3))
        tf_pg = tx_pg.text_frame
        tf_pg.word_wrap = True
        tf_pg.margin_left = tf_pg.margin_right = tf_pg.margin_top = tf_pg.margin_bottom = 0
        p_pg = tf_pg.paragraphs[0]
        p_pg.text = f"Slide {current_slide} of {total_slides}"
        p_pg.alignment = PP_ALIGN.RIGHT
        p_pg.font.size = Pt(9)
        p_pg.font.color.rgb = PRIMARY_GREEN
        p_pg.font.bold = True
        p_pg.font.name = "Calibri"

    def create_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
        return card

    # =========================================================================
    # SLIDE 1: TITLE SLIDE & BOTH STUDENTS DETAILS
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1)

    # Top accent bar
    glow = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.6), Inches(4.5), Inches(0.06))
    glow.fill.solid()
    glow.fill.fore_color.rgb = PRIMARY_GREEN
    glow.line.fill.background()

    # Department / Institution Tag
    inst_box = slide1.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.35))
    tf_inst = inst_box.text_frame
    p_inst = tf_inst.paragraphs[0]
    p_inst.text = "BMS INSTITUTE OF TECHNOLOGY & MANAGEMENT (BMSITM)  |  DEPARTMENT OF MCA"
    p_inst.font.size = Pt(11)
    p_inst.font.bold = True
    p_inst.font.color.rgb = ACCENT_CYAN
    p_inst.font.name = "Calibri"

    # Main Title
    title_box = slide1.shapes.add_textbox(Inches(0.8), Inches(1.15), Inches(11.7), Inches(1.3))
    tf_main = title_box.text_frame
    tf_main.word_wrap = True
    p_m1 = tf_main.paragraphs[0]
    p_m1.text = "AGRI ROVER"
    p_m1.font.size = Pt(40)
    p_m1.font.bold = True
    p_m1.font.color.rgb = TEXT_LIGHT
    p_m1.font.name = "Calibri"
    
    p_m2 = tf_main.add_paragraph()
    p_m2.text = "Autonomous IoT Agricultural Vehicle for Precision Crop Care & Soil Health Monitoring"
    p_m2.font.size = Pt(17)
    p_m2.font.bold = False
    p_m2.font.color.rgb = PRIMARY_GREEN
    p_m2.font.name = "Calibri"

    # Project Phase Badge
    phase_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.55), Inches(3.8), Inches(0.35))
    phase_box.fill.solid()
    phase_box.fill.fore_color.rgb = RGBColor(19, 35, 60)
    phase_box.line.color.rgb = ACCENT_CYAN
    phase_box.line.width = Pt(1)
    tf_pb = phase_box.text_frame
    tf_pb.margin_left = tf_pb.margin_right = tf_pb.margin_top = tf_pb.margin_bottom = 0
    p_pb = tf_pb.paragraphs[0]
    p_pb.text = "PROJECT WORK: PHASE II  •  2025–2027 BATCH"
    p_pb.alignment = PP_ALIGN.CENTER
    p_pb.font.size = Pt(9.5)
    p_pb.font.bold = True
    p_pb.font.color.rgb = ACCENT_CYAN
    p_pb.font.name = "Calibri"

    # Pill tags
    tags = ["Edge Computer Vision", "Targeted Solenoid Spraying", "In-Situ Soil Probing", "3D WebGL Digital Twin"]
    for i, tag in enumerate(tags):
        tag_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8 + i*1.95), Inches(2.55), Inches(1.85), Inches(0.35))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = CARD_BG
        tag_box.line.color.rgb = CARD_BORDER
        tag_box.line.width = Pt(1)
        tf_tb = tag_box.text_frame
        tf_tb.margin_left = tf_tb.margin_right = tf_tb.margin_top = tf_tb.margin_bottom = 0
        p_tb = tf_tb.paragraphs[0]
        p_tb.text = tag
        p_tb.alignment = PP_ALIGN.CENTER
        p_tb.font.size = Pt(8.5)
        p_tb.font.color.rgb = TEXT_MUTED
        p_tb.font.name = "Calibri"

    # Student 1 Card
    card_s1 = create_card(slide1, Inches(0.8), Inches(3.2), Inches(5.6), Inches(2.3), CARD_BG, PRIMARY_GREEN)
    tx_s1 = slide1.shapes.add_textbox(Inches(1.05), Inches(3.35), Inches(5.1), Inches(2.0))
    tf_s1 = tx_s1.text_frame
    tf_s1.word_wrap = True
    
    p = tf_s1.paragraphs[0]
    p.text = "STUDENT DEVELOPER 1"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GREEN
    
    p = tf_s1.add_paragraph()
    p.text = "[Student 1 Name]"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_LIGHT
    
    p = tf_s1.add_paragraph()
    p.text = "USN: [1BY25MC... / Enter USN]\nDepartment of Master of Computer Applications (MCA)\nFocus: Embedded Firmware, BTS7960 Motor Kinematics & Soil Probing Mechanism"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MUTED

    # Student 2 Card
    card_s2 = create_card(slide1, Inches(6.9), Inches(3.2), Inches(5.6), Inches(2.3), CARD_BG, ACCENT_CYAN)
    tx_s2 = slide1.shapes.add_textbox(Inches(7.15), Inches(3.35), Inches(5.1), Inches(2.0))
    tf_s2 = tx_s2.text_frame
    tf_s2.word_wrap = True
    
    p = tf_s2.paragraphs[0]
    p.text = "STUDENT DEVELOPER 2"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    
    p = tf_s2.add_paragraph()
    p.text = "[Student 2 Name]"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_LIGHT
    
    p = tf_s2.add_paragraph()
    p.text = "USN: [1BY25MC... / Enter USN]\nDepartment of Master of Computer Applications (MCA)\nFocus: OpenCV Threat Vision, 3D WebGL Digital Twin & WebSocket Telemetry"
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MUTED

    # Project Guide Banner
    guide_card = create_card(slide1, Inches(0.8), Inches(5.7), Inches(11.733), Inches(0.95), CARD_BG_ALT, CARD_BORDER)
    tx_g = slide1.shapes.add_textbox(Inches(1.05), Inches(5.8), Inches(11.2), Inches(0.75))
    tf_g = tx_g.text_frame
    tf_g.word_wrap = True
    p_g = tf_g.paragraphs[0]
    p_g.text = "PROJECT GUIDE:  [Enter Project Guide Name, Designation]  |  Department of MCA, BMSITM"
    p_g.font.size = Pt(11)
    p_g.font.bold = True
    p_g.font.color.rgb = ACCENT_GOLD
    p_g2 = tf_g.add_paragraph()
    p_g2.text = "Autonomous Institution Affiliated to Visvesvaraya Technological University (VTU), Belagavi  •  Bengaluru, Karnataka"
    p_g2.font.size = Pt(9.5)
    p_g2.font.color.rgb = TEXT_MUTED

    # Speaker Notes for Slide 1
    slide1.notes_slide.notes_text_frame.text = (
        "JUDGE VIVA INTRO (Slide 1):\n"
        "• Welcome the external evaluator and introduce yourselves by Name and USN.\n"
        "• State project title: 'Agri Rover — Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring'.\n"
        "• Highlight that this is an integrated cyber-physical project for MCA Phase II at BMSITM combining mechanical robotics, embedded systems, edge computer vision, and a browser-based 3D WebGL Digital Twin.\n"
        "• Point out your division of responsibilities: Embedded control & hardware kinematics (Student 1) vs. Computer vision & digital twin telemetry (Student 2)."
    )
    add_footer(slide1, 1)

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT & UN SDG ALIGNMENT
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2)
    add_header(slide2, "Problem Context & UN Alignment", "Real-World Agricultural Crises & UN SDG Mapping", "Bridging the critical gap between hazardous chemical spraying and sustainable soil stewardship")

    # Left Column: Problems
    left_w = Inches(5.6)
    card_prob_hdr = create_card(slide2, Inches(0.8), Inches(1.9), left_w, Inches(0.4), RGBColor(40, 20, 25), RGBColor(239, 68, 68))
    tx_ph = slide2.shapes.add_textbox(Inches(0.95), Inches(1.95), left_w - Inches(0.3), Inches(0.3))
    tx_ph.text_frame.paragraphs[0].text = "CURRENT INDUSTRIAL PROBLEMS"
    tx_ph.text_frame.paragraphs[0].font.size = Pt(10.5)
    tx_ph.text_frame.paragraphs[0].font.bold = True
    tx_ph.text_frame.paragraphs[0].font.color.rgb = RGBColor(248, 113, 113)

    problems = [
        ("70–80% Chemical Pesticide Wastage", "Conventional tractor boom and manual backpack spraying indiscriminately broadcasts chemicals across healthy crops and bare soil, wasting money and resources."),
        ("Environmental Toxicity & Leaching", "Chemical overspray leaches into local groundwater aquifers, causes topsoil acidification, and destroys vital subterranean microbial biomes."),
        ("Direct Human Inhalation & Hazards", "Farm laborers face chronic occupational diseases, organophosphate poisoning, and dermal toxicity from manual high-pressure knapsack spraying."),
        ("Absence of Ground-Truth Soil Intelligence", "Farmers lack localized, in-situ NPK (Nitrogen, Phosphorus, Potassium) and pH testing, leading to severe blind over-fertilization.")
    ]

    for i, (title, desc) in enumerate(problems):
        y_pos = Inches(2.4 + i*1.08)
        c = create_card(slide2, Inches(0.8), y_pos, left_w, Inches(0.98), CARD_BG, CARD_BORDER)
        tx = slide2.shapes.add_textbox(Inches(0.95), y_pos + Inches(0.08), left_w - Inches(0.3), Inches(0.85))
        tf = tx.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"•  {title}"
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = RGBColor(254, 202, 202)
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(9)
        p2.font.color.rgb = TEXT_MUTED

    # Right Column: UN SDG Alignment
    right_x = Inches(6.8)
    right_w = Inches(5.733)
    card_sdg_hdr = create_card(slide2, right_x, Inches(1.9), right_w, Inches(0.4), RGBColor(16, 45, 38), PRIMARY_GREEN)
    tx_sh = slide2.shapes.add_textbox(right_x + Inches(0.15), Inches(1.95), right_w - Inches(0.3), Inches(0.3))
    tx_sh.text_frame.paragraphs[0].text = "UNITED NATIONS SUSTAINABLE DEVELOPMENT GOALS (SDG)"
    tx_sh.text_frame.paragraphs[0].font.size = Pt(10.5)
    tx_sh.text_frame.paragraphs[0].font.bold = True
    tx_sh.text_frame.paragraphs[0].font.color.rgb = PRIMARY_GREEN

    sdgs = [
        ("SDG 2: ZERO HUNGER", "Target 2.4 (Indicator 2.4.1)", "Ensures sustainable food production systems and resilient agricultural practices. Agri Rover protects crop yields from destructive pests while preventing soil nutrient exhaustion via real-time NPK feedback.", PRIMARY_GREEN),
        ("SDG 12: RESPONSIBLE CONSUMPTION", "Target 12.4 (Chemical Management)", "Achieves environmentally sound management of chemicals throughout their life cycle. Solenoid micro-bursting cuts total agrochemical volume by up to 80%, directly preventing runoff into water supplies.", ACCENT_CYAN),
        ("SDG 15: LIFE ON LAND", "Soil Biodiversity & Degradation", "Halts and reverses land degradation and biodiversity loss. Targeted pest elimination preserves beneficial earthworms, pollinating insects, and healthy microbial soil ecosystems.", ACCENT_GOLD)
    ]

    for i, (sdg_name, target, desc, color) in enumerate(sdgs):
        y_pos = Inches(2.4 + i*1.12)
        c = create_card(slide2, right_x, y_pos, right_w, Inches(1.02), CARD_BG, color)
        tx = slide2.shapes.add_textbox(right_x + Inches(0.15), y_pos + Inches(0.08), right_w - Inches(0.3), Inches(0.9))
        tf = tx.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"{sdg_name}  —  {target}"
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = color
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(9)
        p2.font.color.rgb = TEXT_MUTED

    # ESG Mini-Card
    esg_card = create_card(slide2, right_x, Inches(5.85), right_w, Inches(0.85), CARD_BG_ALT, CARD_BORDER)
    tx_esg = slide2.shapes.add_textbox(right_x + Inches(0.15), Inches(5.9), right_w - Inches(0.3), Inches(0.75))
    tf_esg = tx_esg.text_frame
    tf_esg.word_wrap = True
    p1 = tf_esg.paragraphs[0]
    p1.text = "ESG COMPLIANCE FRAMEWORK"
    p1.font.size = Pt(10)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_LIGHT
    p2 = tf_esg.add_paragraph()
    p2.text = "• Environmental: 100% electric zero-emission rover; 80% chemical runoff reduction\n• Social: Zero carcinogenic inhalation risk for operators; democratized farming automation\n• Governance: Open reproducible architecture with automated low-voltage (≤12V) hardware cutoffs"
    p2.font.size = Pt(8.5)
    p2.font.color.rgb = TEXT_MUTED

    slide2.notes_slide.notes_text_frame.text = (
        "JUDGE TALKING POINTS (Slide 2):\n"
        "• State why traditional farming fails: 80% of spray never touches pests; it falls on soil and water tables.\n"
        "• Map directly to VTU / UN SDG rubrics: Specifically SDG 2 (Target 2.4 - Sustainable Food Production) and SDG 12 (Target 12.4 - Chemical Management).\n"
        "• Highlight the ESG compliance: Environmental (zero emissions + 80% chemical cut), Social (zero toxic exposure for farm labor), Governance (transparent safety interlocks)."
    )
    add_footer(slide2, 2)

    # =========================================================================
    # SLIDE 3: UNIFIED HARDWARE & SOFTWARE ARCHITECTURE
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3)
    add_header(slide3, "System Architecture", "Unified Cyber-Physical Hardware & Software Stack", "Complete end-to-end integration between mechanical actuation, edge perception, and digital twin telemetry")

    col_w = Inches(5.7)
    
    # Left Column: HARDWARE ARCHITECTURE
    col_hw_x = Inches(0.8)
    card_hw_hdr = create_card(slide3, col_hw_x, Inches(1.9), col_w, Inches(0.4), RGBColor(20, 35, 55), ACCENT_CYAN)
    tx_hh = slide3.shapes.add_textbox(col_hw_x + Inches(0.15), Inches(1.95), col_w - Inches(0.3), Inches(0.3))
    tx_hh.text_frame.paragraphs[0].text = "HARDWARE SUBSYSTEMS & ACTUATION"
    tx_hh.text_frame.paragraphs[0].font.size = Pt(10.5)
    tx_hh.text_frame.paragraphs[0].font.bold = True
    tx_hh.text_frame.paragraphs[0].font.color.rgb = ACCENT_CYAN

    hw_modules = [
        ("Mobility & Drivetrain", "Heavy-duty Skid-Steer / Rocker-Bogie Chassis with Planetary Gear DC Motors, driven by Dual BTS7960 43A H-Bridge Drivers for zero-radius in-place turns ($R=0$) in narrow crop rows."),
        ("Edge Compute & Power Management", "Raspberry Pi 4 Model B (4GB RAM) supervisory controller, dual LM2596 high-efficiency buck regulators, and 12V LiFePO4 battery pack with live ADC voltage telemetry."),
        ("Precision Fluidic Spraying Mechanism", "12V high-pressure DC diaphragm pump (PWM regulated via GPIO 26), chemical reservoir, dual 12V normally-closed solenoid valves (GPIO 24/25), and dual fan-mist nozzles."),
        ("In-Situ Motorized Soil Prober", "NEMA 17 stepper-driven lead screw linear actuator (100mm stroke) lowering industrial NPK, pH, and capacitive moisture probe with mechanical drive-lockout interlock.")
    ]

    for i, (name, details) in enumerate(hw_modules):
        y_pos = Inches(2.4 + i*1.08)
        c = create_card(slide3, col_hw_x, y_pos, col_w, Inches(0.98), CARD_BG, CARD_BORDER)
        tx = slide3.shapes.add_textbox(col_hw_x + Inches(0.15), y_pos + Inches(0.08), col_w - Inches(0.3), Inches(0.85))
        tf = tx.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"⚙  {name}"
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = ACCENT_CYAN
        p2 = tf.add_paragraph()
        p2.text = details
        p2.font.size = Pt(9)
        p2.font.color.rgb = TEXT_MUTED

    # Right Column: SOFTWARE ARCHITECTURE
    col_sw_x = Inches(6.833)
    card_sw_hdr = create_card(slide3, col_sw_x, Inches(1.9), col_w, Inches(0.4), RGBColor(16, 45, 38), PRIMARY_GREEN)
    tx_sh2 = slide3.shapes.add_textbox(col_sw_x + Inches(0.15), Inches(1.95), col_w - Inches(0.3), Inches(0.3))
    tx_sh2.text_frame.paragraphs[0].text = "SOFTWARE, AI & DIGITAL TWIN STACK"
    tx_sh2.text_frame.paragraphs[0].font.size = Pt(10.5)
    tx_sh2.text_frame.paragraphs[0].font.bold = True
    tx_sh2.text_frame.paragraphs[0].font.color.rgb = PRIMARY_GREEN

    sw_modules = [
        ("Edge Vision AI Pipeline (OpenCV)", "Color space conversion (BGR to HSV), purple segmentation mask for caterpillars/larvae, multi-band red mask for weeds, morphological noise filtering, and centroid offset calculation at 20+ FPS."),
        ("Embedded Motion Control & Safety FSM", "Deterministic Python Finite State Machine (Standby, Teleop, Auto Patrol, Active Probing, Emergency Halt) with hard-coded ≤12.0V battery lockout and motor-probe interlock."),
        ("WebSocket Telemetry Bridge & PWA", "Low-latency (<100ms) bidirectional WebSocket bridge relaying wheel velocities, battery voltage, active spray events, and georeferenced soil readings to a responsive Web dashboard."),
        ("3D WebGL Digital Twin Simulator", "Interactive Three.js environment replicating skid-steer kinematics, point turns, particle mist emitters, and crop row lanes for zero-risk, zero-cost virtual algorithm validation.")
    ]

    for i, (name, details) in enumerate(sw_modules):
        y_pos = Inches(2.4 + i*1.08)
        c = create_card(slide3, col_sw_x, y_pos, col_w, Inches(0.98), CARD_BG, CARD_BORDER)
        tx = slide3.shapes.add_textbox(col_sw_x + Inches(0.15), y_pos + Inches(0.08), col_w - Inches(0.3), Inches(0.85))
        tf = tx.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"💻  {name}"
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = PRIMARY_GREEN
        p2 = tf.add_paragraph()
        p2.text = details
        p2.font.size = Pt(9)
        p2.font.color.rgb = TEXT_MUTED

    # Bottom Interlink Banner
    interlink_card = create_card(slide3, Inches(0.8), Inches(5.85), Inches(11.733), Inches(0.85), CARD_BG_ALT, CARD_BORDER)
    tx_il = slide3.shapes.add_textbox(Inches(1.05), Inches(5.9), Inches(11.2), Inches(0.75))
    tf_il = tx_il.text_frame
    tf_il.word_wrap = True
    p1 = tf_il.paragraphs[0]
    p1.text = "HARDWARE-SOFTWARE HANDSHAKE PROTOCOL"
    p1.font.size = Pt(10)
    p1.font.bold = True
    p1.font.color.rgb = ACCENT_GOLD
    p2 = tf_il.add_paragraph()
    p2.text = "Forward Camera Stream  ──>  OpenCV HSV Segmentation  ──>  Spatial Offset  ──>  RPi.GPIO Solenoid Pulse (200ms)  ──>  WebSocket JSON Broadcast  ──>  3D Digital Twin HUD Update"
    p2.font.size = Pt(9)
    p2.font.color.rgb = TEXT_LIGHT

    slide3.notes_slide.notes_text_frame.text = (
        "JUDGE TALKING POINTS (Slide 3):\n"
        "• Emphasize the true cyber-physical coupling: Hardware and software are NOT separate silos.\n"
        "• Hardware highlights: BTS7960 43A motor drivers provide high current for rough soil; dual 12V solenoid valves enable directional left/right spraying; NEMA 17 linear slide handles the soil probe.\n"
        "• Software highlights: OpenCV pipeline running locally on the Raspberry Pi 4 CPU at 20 FPS without expensive GPU hardware.\n"
        "• Point out the bottom Handshake Protocol to prove the full event loop from camera frame to physical solenoid click to WebGL visualization."
    )
    add_footer(slide3, 3)

    # =========================================================================
    # SLIDE 4: BLUEPRINT & WORKING MECHANISM (AUTHENTIC CAD BLUEPRINT IMAGE)
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4)
    add_header(slide4, "Engineering Blueprint & Workflow", "Agri Rover Blueprint & In-Field Working Mechanism", "Clear modular breakdown of physical subsystems (without solar panels) and 4-stage operational execution")

    # Left: Authentic CAD Blueprint Image Box
    img_left = Inches(0.8)
    img_top = Inches(1.9)
    img_width = Inches(5.8)
    img_height = Inches(4.8)

    frame = create_card(slide4, img_left, img_top, img_width, img_height, CARD_BG_ALT, PRIMARY_GREEN)
    
    # Insert authentic project image
    if os.path.exists(cad_image_path):
        slide4.shapes.add_picture(cad_image_path, img_left + Inches(0.12), img_top + Inches(0.12), img_width - Inches(0.24), img_height - Inches(0.65))
        cap_box = slide4.shapes.add_textbox(img_left + Inches(0.12), img_top + img_height - Inches(0.5), img_width - Inches(0.24), Inches(0.4))
        tf_cap = cap_box.text_frame
        p_cap = tf_cap.paragraphs[0]
        p_cap.text = "Fig 1: Industrial 3D CAD Blueprint of Agri Rover (Open-deck configuration showing internal actuators & soil probe)"
        p_cap.font.size = Pt(8.5)
        p_cap.font.color.rgb = TEXT_MUTED
        p_cap.alignment = PP_ALIGN.CENTER

    # Right: Step-by-Step Working Mechanism (4 Steps)
    flow_x = Inches(6.85)
    flow_w = Inches(5.68)
    
    steps = [
        ("Step 1: Autonomous Row Guidance & Lane Lock", "The rover maneuvers down the crop corridor using Hough transform line tracking. Skid-steer proportional steering maintains rover centering in 50–70cm rows, executing in-place pivot turns ($R=0$) at headland boundaries.", ACCENT_CYAN),
        ("Step 2: Edge AI Threat Localization", "The onboard HD camera delivers frames at 20+ FPS to the OpenCV engine. Color segmentation calculates threat centroids and determines whether the infestation is on the left or right foliage bank.", PRIMARY_GREEN),
        ("Step 3: Directional Solenoid Micro-Burst", "Upon threat confirmation, the controller fires the corresponding 12V solenoid valve (GPIO 24 or 25) for exactly 200ms at 75% pump pressure. Only infected foliage is sprayed; healthy crops receive zero chemical.", ACCENT_GOLD),
        ("Step 4: Automated Ground Soil Probing", "At scheduled waypoints or manual UI trigger, vehicle drive motors lock out. The NEMA 17 stepper lowers the NPK/pH/moisture probe 100mm into the soil, records stabilized readings in <5s, and retracts.", ACCENT_PURPLE)
    ]

    for i, (stitle, sdesc, col) in enumerate(steps):
        y_pos = Inches(1.9 + i*1.22)
        c = create_card(slide4, flow_x, y_pos, flow_w, Inches(1.12), CARD_BG, CARD_BORDER)
        
        badge = slide4.shapes.add_shape(MSO_SHAPE.OVAL, flow_x + Inches(0.15), y_pos + Inches(0.15), Inches(0.38), Inches(0.38))
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

        tx = slide4.shapes.add_textbox(flow_x + Inches(0.65), y_pos + Inches(0.08), flow_w - Inches(0.8), Inches(1.0))
        tf = tx.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = stitle
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf.add_paragraph()
        p2.text = sdesc
        p2.font.size = Pt(8.8)
        p2.font.color.rgb = TEXT_MUTED

    slide4.notes_slide.notes_text_frame.text = (
        "JUDGE TALKING POINTS (Slide 4 - Blueprint & Mechanism):\n"
        "• Direct the judge's attention to the 3D CAD Blueprint on the left:\n"
        "  - Point out the motorized vertical probe at the front (lead-screw driven).\n"
        "  - Point out the Rocker-Bogie wheel suspension for rough agricultural terrain.\n"
        "  - Show the rear-mounted pesticide reservoir and side-facing micro-spray boom nozzles.\n"
        "  - Explain why it is shown without solar panels: To reveal the open modular deck, electronics bay, and fluid piping.\n"
        "• Walk through the 4-step sequence: Row Guidance -> Threat ID -> 200ms Solenoid Micro-Burst -> Ground Soil Probing with drive interlock."
    )
    add_footer(slide4, 4)

    # =========================================================================
    # SLIDE 5: COMPETITIVE ADVANTAGE & COST-BENEFIT ANALYSIS
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5)
    add_header(slide5, "Competitive Advantage & Cost Factor", "How Agri Rover Compares With Existing Market Solutions", "Disruptive cost efficiency, zero chemical wastage, and unprecedented accessibility for small-to-medium farmers")

    # Metrics highlight ribbon (4 KPIs)
    kpis = [
        ("80% LESS CHEMICALS", "Targeted AI micro-bursts vs. blanket broadcast", PRIMARY_GREEN),
        ("15x COST REDUCTION", "₹35k–₹45k build vs. ₹8L–₹25L commercial machinery", ACCENT_CYAN),
        ("<5s SOIL SAMPLING", "Instant in-situ NPK vs. 3–7 day lab delays", ACCENT_GOLD),
        ("ZERO HUMAN EXPOSURE", "100% remote teleop eliminates toxic inhalation", ACCENT_PURPLE)
    ]
    for i, (val, sub, col) in enumerate(kpis):
        kbox = create_card(slide5, Inches(0.8 + i*2.98), Inches(1.9), Inches(2.8), Inches(0.85), CARD_BG, col)
        tx = slide5.shapes.add_textbox(Inches(0.9 + i*2.98), Inches(1.95), Inches(2.6), Inches(0.75))
        tf = tx.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = val
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(8)
        p2.font.color.rgb = TEXT_MUTED

    # Comparison Table
    table_shape = slide5.shapes.add_table(6, 4, Inches(0.8), Inches(2.95), Inches(11.733), Inches(3.7))
    tbl = table_shape.table
    tbl.columns[0].width = Inches(2.333)
    tbl.columns[1].width = Inches(3.0)
    tbl.columns[2].width = Inches(3.0)
    tbl.columns[3].width = Inches(3.4)

    headers = ["Evaluation Criteria", "Tractor Boom Sprayer", "Agricultural Drone (UAV)", "Agri Rover (Our Solution)"]
    for col_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(16, 45, 38) if col_idx == 3 else RGBColor(26, 38, 57)
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_GREEN if col_idx == 3 else TEXT_LIGHT
        p.alignment = PP_ALIGN.CENTER

    data = [
        ("Capital Investment / Cost", "Prohibitive: ₹20,00,000 – ₹50,00,000+", "High: ₹6,00,000 – ₹15,00,000+", "Affordable: ₹35,000 – ₹45,000 (~$450)\nBuilt with off-the-shelf industrial parts"),
        ("Chemical Usage & Wastage", "High Wastage (70–80% wasted on soil/leaves)", "Moderate Wastage (40–50% drift losses)", "Minimal Wastage (Up to 80% saved)\nLocalized 200ms directional solenoid bursts"),
        ("Integrated Soil Testing", "None (Requires physical lab visits: 3–7 days)", "None (Aerial sensors cannot measure ground NPK)", "In-Situ Ground Probing (<5 seconds)\nMotorized NPK, pH & moisture data logging"),
        ("Navigation & Canopy Access", "Damages tall/dense crop rows; high soil compaction", "Top-canopy only; cannot spray under-foliage pests", "Row-Level Skid-Steer Navigation ($R=0$)\nDirect side-canopy & under-leaf nozzle access"),
        ("Virtual Validation / Digital Twin", "No virtual testing; physical damage risks in field", "Expensive physical test flights; crash liability", "High-Fidelity 3D WebGL Digital Twin\nZero-risk, zero-cost pre-deployment simulation")
    ]

    for row_idx, row_vals in enumerate(data, start=1):
        for col_idx, val in enumerate(row_vals):
            cell = tbl.cell(row_idx, col_idx)
            cell.fill.solid()
            if col_idx == 3:
                cell.fill.fore_color.rgb = RGBColor(20, 36, 40)
            else:
                cell.fill.fore_color.rgb = CARD_BG if row_idx % 2 == 1 else CARD_BG_ALT
            cell.text_frame.word_wrap = True
            cell.text_frame.margin_left = Inches(0.1)
            cell.text_frame.margin_right = Inches(0.1)
            cell.text_frame.margin_top = Inches(0.08)
            cell.text_frame.margin_bottom = Inches(0.08)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(9.5 if col_idx == 3 else 9)
            p.font.bold = (col_idx == 3 or col_idx == 0)
            p.font.color.rgb = PRIMARY_GREEN if col_idx == 3 else (TEXT_LIGHT if col_idx == 0 else TEXT_MUTED)
            if col_idx > 0:
                p.alignment = PP_ALIGN.LEFT

    slide5.notes_slide.notes_text_frame.text = (
        "JUDGE TALKING POINTS (Slide 5 - Cost & Differentiation):\n"
        "• Judges love comparative matrices: Address why commercial drones and tractors do NOT solve Indian smallholder problems.\n"
        "• Drones cost ₹6 to ₹15 Lakhs and suffer from rotor spray drift; tractor sprayers cost ₹20+ Lakhs and cannot enter narrow rows.\n"
        "• Agri Rover costs only ₹35,000 to ₹45,000 (~$450), fits directly between 50-70cm rows, sprays under the leaves, and includes soil probing.\n"
        "• Highlight payback period: An 80% reduction in expensive chemical pesticides means the farmer recovers the entire rover cost in 2–3 seasons."
    )
    add_footer(slide5, 5)

    # =========================================================================
    # SLIDE 6: WHAT EXTERNAL JUDGES LOOK FOR (WITH FIELD CHASSIS IMAGE)
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6)
    add_header(slide6, "Evaluation Criteria & Viva Defense", "What External Judges Look For & How Agri Rover Delivers", "Demonstrating engineering rigor, safety fail-safes, real-world feasibility, and research contributions")

    # Left: Authentic In-Field Chassis Image
    chassis_left = Inches(0.8)
    chassis_top = Inches(1.9)
    chassis_w = Inches(4.5)
    chassis_h = Inches(4.8)

    create_card(slide6, chassis_left, chassis_top, chassis_w, chassis_h, CARD_BG_ALT, PRIMARY_GREEN)
    if os.path.exists(chassis_image_path):
        slide6.shapes.add_picture(chassis_image_path, chassis_left + Inches(0.12), chassis_top + Inches(0.12), chassis_w - Inches(0.24), chassis_h - Inches(0.65))
        cbox = slide6.shapes.add_textbox(chassis_left + Inches(0.12), chassis_top + chassis_h - Inches(0.5), chassis_w - Inches(0.24), Inches(0.4))
        p_c = cbox.text_frame.paragraphs[0]
        p_c.text = "Fig 2: Physical Hardware Chassis in Field (Mist spraying in crop row without solar panels)"
        p_c.font.size = Pt(8.5)
        p_c.font.color.rgb = TEXT_MUTED
        p_c.alignment = PP_ALIGN.CENTER

    # Right: 4 Judge Evaluation Criteria Cards
    eval_x = Inches(5.55)
    eval_w = Inches(6.983)

    judge_cards = [
        ("1. Technical Rigor & Cyber-Physical Integration", [
            "Hardware & software are tightly coupled: Raspberry Pi GPIO drives dual BTS7960 43A motor bridges and solenoid relays with sub-50ms latency.",
            "Live WebSockets stream wheel speeds, tank level, battery voltage, and soil logs to browser in real-time (<100ms)."
        ], ACCENT_CYAN),
        ("2. Engineering Safety & Failsafe Interlocks", [
            "Automated Under-Voltage Cutoff: Immediate emergency shutdown whenever battery drops <= 12.0V (<=12%).",
            "Drive-Probe Interlock: Traction motors locked at 0% PWM during linear actuator ground penetration to prevent mechanical shear."
        ], RGBColor(239, 68, 68)),
        ("3. Frugal Engineering & Smallholder Accessibility", [
            "Entire prototype engineered within ₹35,000–₹45,000 using standard off-the-shelf components.",
            "Open reproducible architecture (Python, OpenCV, WebGL) with zero proprietary software licensing fees."
        ], PRIMARY_GREEN),
        ("4. Demonstration Readiness & 3D Digital Twin", [
            "Backed by physical hardware prototype and interactive 3D WebGL Digital Twin with full kinematic simulation.",
            "Enables safe virtual validation before field deployment, eliminating physical collision and crash risks."
        ], ACCENT_GOLD)
    ]

    for i, (title, bullets, col) in enumerate(judge_cards):
        y_pos = Inches(1.9 + i*1.22)
        c = create_card(slide6, eval_x, y_pos, eval_w, Inches(1.12), CARD_BG, col)
        tx = slide6.shapes.add_textbox(eval_x + Inches(0.15), y_pos + Inches(0.08), eval_w - Inches(0.3), Inches(1.0))
        tf = tx.text_frame
        tf.word_wrap = True
        
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(10.5)
        p1.font.bold = True
        p1.font.color.rgb = col

        for bullet in bullets:
            pb = tf.add_paragraph()
            pb.text = f"✔  {bullet}"
            pb.font.size = Pt(8.5)
            pb.font.color.rgb = TEXT_MUTED

    slide6.notes_slide.notes_text_frame.text = (
        "JUDGE TALKING POINTS (Slide 6 - Viva Rubric Defense):\n"
        "• Point directly to the real field prototype photo on the left: This proves we are not just doing theory; we have a physical working vehicle in real soil.\n"
        "• Answer common judge questions proactively:\n"
        "  - Q: 'What happens if the rover gets stuck while the soil probe is in the ground?'\n"
        "    A: 'Our software implements a mandatory drive interlock. Wheel PWM is forced to 0% until the linear actuator confirms full retraction.'\n"
        "  - Q: 'How do you handle battery brownout?'\n"
        "    A: 'We monitor battery voltage continuously. If it drops below 12.0V, an automatic safety FSM halt shuts down motors and closes valves.'\n"
        "  - Q: 'Why did you build a 3D Digital Twin?'\n"
        "    A: 'It allows zero-cost virtual algorithm validation, testing steering and lane-lock without risking physical crashes.'"
    )
    add_footer(slide6, 6)

    # =========================================================================
    # SLIDE 7: PHASE 2 ROADMAP, CONCLUSION & Q&A
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7)
    add_header(slide7, "Future Scope & Project Conclusion", "Project Phase 2 Roadmap & Key Achievements", "Summary of milestones achieved, upcoming technological expansions, and open defense session")

    # Left: Milestones Achieved
    left_x = Inches(0.8)
    col_w2 = Inches(5.7)
    c_m = create_card(slide7, left_x, Inches(1.9), col_w2, Inches(3.7), CARD_BG, PRIMARY_GREEN)
    tx_m = slide7.shapes.add_textbox(left_x + Inches(0.2), Inches(2.05), col_w2 - Inches(0.4), Inches(3.4))
    tf_m = tx_m.text_frame
    tf_m.word_wrap = True
    
    p = tf_m.paragraphs[0]
    p.text = "PHASE 1 & CURRENT ACHIEVEMENTS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_GREEN
    
    achievements = [
        "80% Agrochemical Savings: Successfully tested directional micro-bursting with 200ms solenoid pulses, eradicating broadcast waste.",
        "Zero Human Toxicity: Completely separated human operators from direct chemical inhalation via remote teleop and autonomous patrol.",
        "In-Situ Soil Health Mapping: Motorized probe logs ground-truth NPK, pH, and moisture with automated drive-interlock safety.",
        "Zero-Risk 3D Digital Twin: Interactive Three.js WebGL simulation replicates physical kinematic motion and telemetry streaming.",
        "Robust Illumination Handling: OpenCV HSV color segmentation isolates pests and weeds despite outdoor sunlight variability."
    ]
    for ach in achievements:
        p_ach = tf_m.add_paragraph()
        p_ach.text = f"★  {ach}"
        p_ach.font.size = Pt(9)
        p_ach.font.color.rgb = TEXT_MUTED

    # Right: Phase 2 Active Development Roadmap
    right_x2 = Inches(6.833)
    c_r = create_card(slide7, right_x2, Inches(1.9), col_w2, Inches(3.7), CARD_BG, ACCENT_CYAN)
    tx_r = slide7.shapes.add_textbox(right_x2 + Inches(0.2), Inches(2.05), col_w2 - Inches(0.4), Inches(3.4))
    tf_r = tx_r.text_frame
    tf_r.word_wrap = True
    
    p = tf_r.paragraphs[0]
    p.text = "PHASE 2 EXPANSION ROADMAP"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    
    roadmap = [
        "Edge AI Deep Learning Upgrade: Transitioning from HSV thresholding to quantized INT8 YOLOv8n running on Google Coral Edge TPU at >=30 FPS.",
        "Centimeter-Accurate RTK-GPS Navigation: Integrating multi-constellation RTK-GPS for automated headland row turns and geo-fenced path execution.",
        "Multi-Rover Swarm Telematics: Implementing lightweight MQTT pub/sub for coordinated fleet operations across multi-acre commercial plantations.",
        "Auxiliary Trickle-Charging Canopy: Evaluating optional passive roof-mount solar trickle-charger for indefinite daytime field endurance."
    ]
    for rd in roadmap:
        p_rd = tf_r.add_paragraph()
        p_rd.text = f"🚀  {rd}"
        p_rd.font.size = Pt(9.2)
        p_rd.font.color.rgb = TEXT_MUTED

    # Bottom Thank You & Q&A Banner
    qa_card = create_card(slide7, Inches(0.8), Inches(5.75), Inches(11.733), Inches(1.1), CARD_BG_ALT, ACCENT_GOLD)
    tx_qa = slide7.shapes.add_textbox(Inches(1.05), Inches(5.82), Inches(11.2), Inches(0.95))
    tf_qa = tx_qa.text_frame
    tf_qa.word_wrap = True
    
    p_q1 = tf_qa.paragraphs[0]
    p_q1.text = "THANK YOU  |  QUESTIONS & DISCUSSION WELCOME"
    p_q1.font.size = Pt(13)
    p_q1.font.bold = True
    p_q1.font.color.rgb = ACCENT_GOLD
    p_q1.alignment = PP_ALIGN.CENTER
    
    p_q2 = tf_qa.add_paragraph()
    p_q2.text = "Developed by MCA Project Team (MMCA34, 2025–2027 Batch)  •  BMS Institute of Technology & Management, Bengaluru\nLive Demonstration: Hardware Prototype & Interactive 3D WebGL Digital Twin Dashboard"
    p_q2.font.size = Pt(9.5)
    p_q2.font.color.rgb = TEXT_LIGHT
    p_q2.alignment = PP_ALIGN.CENTER

    slide7.notes_slide.notes_text_frame.text = (
        "JUDGE TALKING POINTS (Slide 7 - Conclusion & Q&A):\n"
        "• Conclude confidently: 'In conclusion, Agri Rover transforms agricultural crop care by combining 80% chemical reduction, in-situ soil intelligence, and affordable robotics.'\n"
        "• Briefly outline Phase 2: Upgrading to quantized YOLOv8n on Edge TPU and RTK-GPS waypoint navigation.\n"
        "• Offer to start the live demonstration: 'We now invite the respected judges to review our physical rover hardware and interact with our live 3D WebGL Digital Twin simulator.'"
    )
    add_footer(slide7, 7)

    prs.save(output_path)
    print(f"Presentation saved successfully to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    create_deck()
