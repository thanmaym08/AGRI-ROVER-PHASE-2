#!/usr/bin/env python3
"""
Agri Rover — Updated Prototype Hardware BOM & Comprehensive System Guide
File: create_updated_prototype_bom_pdf.py

Features:
 - Integrated System Wiring Diagram
 - Separate Images of Every Component
 - Motor Driver Compatibility Matrix
 - Updated Budget factoring in already owned components (Motor Driver & Spray Pump)
 - Direct Clickable Shopping Links (Amazon.in, Flipkart, Robu.in)
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Output PDF path
OUTPUT_PDF = r"f:\agrirover phase 2\Prototype\Agri_Rover_Prototype_Hardware_Guide_Updated.pdf"
BRAIN_DIR = r"C:\Users\Thanm\.gemini\antigravity\brain\4add96ef-3939-4a05-9f2c-a9a5038f3828"

# Images
IMG_SCHEMATIC = os.path.join(BRAIN_DIR, "integrated_wiring_diagram_1790828177841.jpg")
IMG_CHASSIS = os.path.join(BRAIN_DIR, "chassis_and_wheels_1790828247807.jpg")
IMG_PARTS = os.path.join(BRAIN_DIR, "electronics_parts_kit_1790827636803.jpg")
IMG_CAM = os.path.join(BRAIN_DIR, "esp32_cam_module_1790614793837.jpg")
IMG_ROVER = os.path.join(BRAIN_DIR, "esp32_rover_prototype_1790614892086.jpg")

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#7f8c8d"))

        # Running header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(40, 805, "AGRI ROVER PHASE 2 — HARDWARE INTEGRATION & COMPATIBILITY GUIDE")
            self.setStrokeColor(colors.HexColor("#2ecc71"))
            self.setLineWidth(1)
            self.line(40, 798, 555, 798)

        # Running footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 30, footer_text)
        self.drawString(40, 30, "BMSITM MCA PROJECT MMCA34 | AFFILIATED TO VTU | AUTONOMOUS")
        self.setStrokeColor(colors.HexColor("#bdc3c7"))
        self.setLineWidth(0.5)
        self.line(40, 42, 555, 42)

        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=35,
        rightMargin=35,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1b2a47"),
        spaceAfter=3
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#27ae60"),
        spaceAfter=8
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#555555")
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1b2a47"),
        spaceBefore=10,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#2c3e50")
    )

    caption_style = ParagraphStyle(
        'CaptionStyle',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#7f8c8d"),
        alignment=1,
        spaceAfter=6
    )

    th_style = ParagraphStyle(
        'THStyle',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    td_style = ParagraphStyle(
        'TDStyle',
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#2c3e50")
    )

    td_bold = ParagraphStyle(
        'TDBold',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1b2a47")
    )

    td_owned = ParagraphStyle(
        'TDOwned',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#27ae60")
    )

    link_style = ParagraphStyle(
        'LinkStyle',
        fontName='Helvetica',
        fontSize=7.8,
        leading=10,
        textColor=colors.HexColor("#0066cc")
    )

    story = []

    # ========================== PAGE 1: INTEGRATED SYSTEM SCHEMATIC ==========================
    story.append(Paragraph("🌿 AGRI ROVER: ESP32-CAM PROTOTYPE", title_style))
    story.append(Paragraph("Hardware Integration Guide, Motor Driver Compatibility & Updated BOM", subtitle_style))

    meta_text = (
        "<b>Project Code:</b> MMCA34 (Phase II Prototype) &nbsp;|&nbsp; "
        "<b>Institution:</b> BMS Institute of Technology & Management (BMSITM)<br/>"
        "<b>Status:</b> Custom Configuration (Motor Driver & Spray Pump Already Owned) &nbsp;|&nbsp; "
        "<b>Remaining Cost:</b> ~₹1,400 – ₹1,700 INR"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2ecc71"), spaceAfter=8))

    story.append(Paragraph("1. Fully Integrated System Wiring Diagram", h2_style))
    story.append(Paragraph("This schematic illustrates how all prototype components—including your motor driver, spray pump, ESP32-CAM, buck converter, relay, and 12V battery—wire together into a single, cohesive circuit with brownout protection.", body_style))
    story.append(Spacer(1, 4))

    if os.path.exists(IMG_SCHEMATIC):
        story.append(Image(IMG_SCHEMATIC, width=525, height=295))
        story.append(Paragraph("Figure 1: Complete Integrated Electrical Wiring Schematic for the Agri Rover ESP32-CAM Prototype.", caption_style))

    story.append(Spacer(1, 6))
    key_points = """
    <b>Key Wiring Highlights:</b><br/>
    • <b>Common Star Ground:</b> Battery Negative (-), Buck Converter GND, Motor Driver GND, Relay GND, and ESP32-CAM GND are tied to one shared rail.<br/>
    • <b>Logic Isolation & Decoupling:</b> The LM2596 buck converter outputs 5.10V to the ESP32-CAM with a 1000µF capacitor across 5V and GND to suppress motor inrush noise.<br/>
    • <b>Parallel Motors:</b> Left motors are wired in parallel to Channel A (OUT1/OUT2); Right motors are wired in parallel to Channel B (OUT3/OUT4).<br/>
    • <b>Inductive Protection:</b> A 1N4007 flyback diode is soldered across the spray pump terminals to absorb inductive kickback.
    """
    story.append(Paragraph(key_points, body_style))

    story.append(PageBreak())

    # ========================== PAGE 2: SEPARATE COMPONENT IMAGES ==========================
    story.append(Paragraph("2. Visual Component Catalog (Separate Item Showcase)", h2_style))
    story.append(Paragraph("Inspect each module below to ensure exact visual and pin-level alignment before assembling your prototype.", body_style))
    story.append(Spacer(1, 6))

    # Grid 1: Camera + Chassis
    cell_cam = Image(IMG_CAM, width=255, height=170) if os.path.exists(IMG_CAM) else Paragraph("[Camera]", body_style)
    cell_chassis = Image(IMG_CHASSIS, width=255, height=170) if os.path.exists(IMG_CHASSIS) else Paragraph("[Chassis]", body_style)

    table_grid1 = Table([[cell_cam, cell_chassis]], colWidths=[262, 263])
    table_grid1.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(table_grid1)

    table_cap1 = Table([[
        Paragraph("<b>[A] AI-Thinker ESP32-CAM Module</b><br/>OV2640 2MP lens, Flash LED, 4MB PSRAM.", caption_style),
        Paragraph("<b>[B] 4WD Smart Car Robot Chassis Kit</b><br/>4x TT gear motors, 4x rubber wheels, acrylic plates.", caption_style)
    ]], colWidths=[262, 263])
    story.append(table_cap1)
    story.append(Spacer(1, 8))

    # Grid 2: Electronics Parts Kit + Fully Assembled Robot
    cell_parts = Image(IMG_PARTS, width=255, height=170) if os.path.exists(IMG_PARTS) else Paragraph("[Parts]", body_style)
    cell_rover = Image(IMG_ROVER, width=255, height=170) if os.path.exists(IMG_ROVER) else Paragraph("[Assembled]", body_style)

    table_grid2 = Table([[cell_parts, cell_rover]], colWidths=[262, 263])
    table_grid2.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(table_grid2)

    table_cap2 = Table([[
        Paragraph("<b>[C] Auxiliary Electronics & Actuation Kit</b><br/>Buck converter, 5V relay, pump, nozzle, battery case.", caption_style),
        Paragraph("<b>[D] Fully Assembled Prototype Rover</b><br/>Chassis with front camera tilt mount & mist nozzle.", caption_style)
    ]], colWidths=[262, 263])
    story.append(table_cap2)

    story.append(PageBreak())

    # ========================== PAGE 3: MOTOR DRIVER COMPATIBILITY & UPDATED BOM ==========================
    story.append(Paragraph("3. Motor Driver Compatibility Analysis", h2_style))
    story.append(Paragraph("<b>Are all motor drivers compatible with this project?</b><br/>"
                           "<b>YES, almost all standard dual DC motor drivers are compatible!</b> As long as your driver has 4 logic input pins (typically labeled IN1, IN2, IN3, IN4) and accepts 3.3V or 5V logic, it will seamlessly interface with the ESP32-CAM firmware.", body_style))
    story.append(Spacer(1, 4))

    driver_compat_data = [
        [Paragraph("Driver Model", th_style), Paragraph("Input Pins", th_style), Paragraph("Voltage / Current", th_style), Paragraph("Compatibility Status & Notes", th_style)],
        [
            Paragraph("<b>L298N (Red Board)</b>", td_bold),
            Paragraph("IN1, IN2, IN3, IN4", td_style),
            Paragraph("5V–35V / 2.0A cont.", td_style),
            Paragraph("<font color='#27ae60'><b>100% Compatible.</b></font> Most popular. Built-in heatsink, screw terminals.", td_style)
        ],
        [
            Paragraph("<b>DRV8833 Dual Driver</b>", td_bold),
            Paragraph("IN1, IN2, IN3, IN4", td_style),
            Paragraph("2.7V–10.8V / 1.5A cont.", td_style),
            Paragraph("<font color='#27ae60'><b>100% Compatible.</b></font> Highly efficient MOSFET H-bridge with near-zero voltage drop.", td_style)
        ],
        [
            Paragraph("<b>TB6612FNG Driver</b>", td_bold),
            Paragraph("AIN1, AIN2, BIN1, BIN2", td_style),
            Paragraph("4.5V–15V / 1.2A cont.", td_style),
            Paragraph("<font color='#27ae60'><b>100% Compatible.</b></font> Connect STBY to 5V/3.3V, tie PWMA/PWMB to HIGH.", td_style)
        ],
        [
            Paragraph("<b>L293D Breakout Board</b>", td_bold),
            Paragraph("IN1, IN2, IN3, IN4", td_style),
            Paragraph("4.5V–36V / 600mA cont.", td_style),
            Paragraph("<font color='#27ae60'><b>100% Compatible.</b></font> Safe for yellow TT motors. (Avoid Arduino Uno shield format).", td_style)
        ],
        [
            Paragraph("<b>BTS7960 43A Driver</b>", td_bold),
            Paragraph("RPWM, LPWM, R_EN, L_EN", td_style),
            Paragraph("6V–27V / 43A peak", td_style),
            Paragraph("<font color='#d35400'><b>Compatible (Overkill).</b></font> Single channel; requires 2 modules for skid-steer.", td_style)
        ]
    ]

    t_driver = Table(driver_compat_data, colWidths=[105, 105, 95, 220])
    t_driver.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1b2a47")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dcdde1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    story.append(t_driver)
    story.append(Spacer(1, 10))

    # Updated Purchasing Table
    story.append(Paragraph("4. Updated Bill of Materials & Direct Purchase Links", h2_style))
    story.append(Paragraph("Items you already own are highlighted in green. You only need to purchase the remaining items (Total: ~₹1,400 – ₹1,700).", body_style))
    story.append(Spacer(1, 4))

    bom_data = [
        [Paragraph("Item", th_style), Paragraph("Component Specification", th_style), Paragraph("Status / Price", th_style), Paragraph("Direct Buying Links (Clickable)", th_style)],
        [
            Paragraph("<b>1</b>", td_bold),
            Paragraph("<b>Motor Driver Module</b><br/>(L298N / DRV8833 / TB6612 / L293D breakout)", td_style),
            Paragraph("<b>ALREADY OWNED</b><br/><font color='#27ae60'><b>₹0 (Saved!)</b></font>", td_owned),
            Paragraph("<i>Reuse your existing motor driver. Connect inputs to GPIO 12, 13, 14, 15.</i>", td_style)
        ],
        [
            Paragraph("<b>2</b>", td_bold),
            Paragraph("<b>Chemical Spray Pump Motor</b><br/>(12V Diaphragm / DC mini pump)", td_style),
            Paragraph("<b>ALREADY OWNED</b><br/><font color='#27ae60'><b>₹0 (Saved!)</b></font>", td_owned),
            Paragraph("<i>Reuse your existing pump motor. Wire with 1N4007 flyback diode.</i>", td_style)
        ],
        [
            Paragraph("<b>3</b>", td_bold),
            Paragraph("<b>ESP32-CAM + OV2640 + MB USB Shield</b><br/>Dual-core 240MHz, 4MB PSRAM, Micro-USB CH340 baseboard.", td_style),
            Paragraph("₹650 – ₹800", td_style),
            Paragraph(
                "• <a href='https://www.amazon.in/s?k=ESP32-CAM+with+MB+shield'><u>Amazon.in (ESP32-CAM MB)</u></a><br/>"
                "• <a href='https://robu.in/product/esp32-cam-ch340-development-board/'><u>Robu.in (ESP32-CAM Board)</u></a><br/>"
                "• <a href='https://www.flipkart.com/search?q=ESP32-CAM'><u>Flipkart (ESP32-CAM)</u></a>",
                link_style
            )
        ],
        [
            Paragraph("<b>4</b>", td_bold),
            Paragraph("<b>4WD Robot Smart Car Chassis Kit</b><br/>Acrylic frame plate, 4x TT gear motors, 4x rubber wheels, hardware.", td_style),
            Paragraph("₹550 – ₹720", td_style),
            Paragraph(
                "• <a href='https://www.amazon.in/s?k=4WD+Smart+Robot+Car+Chassis+Kit'><u>Amazon.in (4WD Chassis Kit)</u></a><br/>"
                "• <a href='https://robu.in/product/smart-car-robot-chassis-kit-4wd/'><u>Robu.in (4WD Smart Car)</u></a><br/>"
                "• <a href='https://www.flipkart.com/search?q=4WD+smart+robot+car+chassis'><u>Flipkart (4WD Chassis)</u></a>",
                link_style
            )
        ],
        [
            Paragraph("<b>5</b>", td_bold),
            Paragraph("<b>LM2596 DC-DC Buck Step-Down Module</b><br/>Tuned to 5.10V output (prevents camera brownouts).", td_style),
            Paragraph("₹90 – ₹130", td_style),
            Paragraph(
                "• <a href='https://www.amazon.in/s?k=LM2596+buck+converter'><u>Amazon.in (LM2596 Converter)</u></a><br/>"
                "• <a href='https://robu.in/product/lm2596-dc-dc-step-down-module/'><u>Robu.in (LM2596 Module)</u></a>",
                link_style
            )
        ],
        [
            Paragraph("<b>6</b>", td_bold),
            Paragraph("<b>5V 1-Channel Relay Module (Optocoupled)</b><br/>Switches 12V pump power from ESP32 GPIO 2.", td_style),
            Paragraph("₹60 – ₹90", td_style),
            Paragraph(
                "• <a href='https://www.amazon.in/s?k=5V+1+channel+relay+module'><u>Amazon.in (5V Relay Module)</u></a><br/>"
                "• <a href='https://robu.in/product/1-channel-isolated-5v-relay-module/'><u>Robu.in (1-Ch 5V Relay)</u></a>",
                link_style
            )
        ],
        [
            Paragraph("<b>7</b>", td_bold),
            Paragraph("<b>Brass Misting Nozzle (0.3mm) + Tubing</b><br/>Atomizing mist nozzle + 1m 6mm silicone tube.", td_style),
            Paragraph("₹150 – ₹220", td_style),
            Paragraph(
                "• <a href='https://www.amazon.in/s?k=brass+misting+nozzle+with+tee+connector'><u>Amazon.in (Mist Nozzle)</u></a><br/>"
                "• <a href='https://www.amazon.in/s?k=silicone+tube+pipe+6mm'><u>Amazon.in (6mm Tube)</u></a>",
                link_style
            )
        ],
        [
            Paragraph("<b>8</b>", td_bold),
            Paragraph("<b>12V 3S 18650 Battery Holder with DC Jack</b><br/>Holds 3x 18650 Li-ion cells (nominal 11.1V–12.6V).", td_style),
            Paragraph("₹180 – ₹280", td_style),
            Paragraph(
                "• <a href='https://www.amazon.in/s?k=3S+18650+battery+holder+with+DC+jack'><u>Amazon.in (3S Battery Holder)</u></a><br/>"
                "• <a href='https://robu.in/product/3s-18650-battery-holder-with-dc-plug/'><u>Robu.in (3S Battery Case)</u></a>",
                link_style
            )
        ],
        [
            Paragraph("<b>9</b>", td_bold),
            Paragraph("<b>Protection & Wiring Pack</b><br/>Jumper wires, 1x 1000µF 16V cap, 1x 1N4007 diode.", td_style),
            Paragraph("₹120 – ₹180", td_style),
            Paragraph(
                "• <a href='https://www.amazon.in/s?k=jumper+wires+male+to+female+and+male+to+male'><u>Amazon.in (Jumper Wires)</u></a><br/>"
                "• <a href='https://www.amazon.in/s?k=1000uf+capacitor+and+1n4007+diode'><u>Amazon.in (Capacitor & Diode)</u></a>",
                link_style
            )
        ]
    ]

    t_bom = Table(bom_data, colWidths=[22, 190, 88, 225])
    t_bom.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#27ae60")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dcdde1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    story.append(t_bom)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Updated PDF created: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
