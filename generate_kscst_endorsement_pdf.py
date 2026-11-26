import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

def build_endorsement_pdf():
    pdf_filename = "KSCST_Declaration_and_Endorsement_Form.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=40,
        bottomMargin=40
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
        fontSize=11,
        leading=14,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.HexColor("#1E3A8A")
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13.5,
        alignment=4,
        spaceAfter=5,
        textColor=colors.HexColor("#1E293B")
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Times-Roman',
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
    story.append(Paragraph("Indian Institute of Science Campus, Bengaluru – 560012", ParagraphStyle('SubSub', parent=title_style, fontName='Times-Italic', fontSize=9, textColor=colors.HexColor("#475569"))))
    story.append(Paragraph("50th SERIES OF THE STUDENT PROJECT PROGRAMME (SPP: 2026–2027)", sub_title_style))
    story.append(Paragraph("DECLARATION BY STUDENTS AND INSTITUTIONAL ENDORSEMENT FORM", ParagraphStyle('FormTitle', parent=sub_title_style, fontSize=10, textColor=colors.HexColor("#1E3A8A"))))
    story.append(Spacer(1, 8))

    # Meta Table
    meta_table_data = [
        [Paragraph("<b>Project Proposal Title:</b>", table_cell_style), Paragraph("<b>Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring</b>", table_cell_style)],
        [Paragraph("<b>Institution Name:</b>", table_cell_style), Paragraph("B.M.S. INSTITUTE OF TECHNOLOGY & MANAGEMENT (BMSITM), Yelahanka, Bengaluru – 560064", table_cell_style)],
        [Paragraph("<b>Department / Stream:</b>", table_cell_style), Paragraph("Department of Master of Computer Applications (MCA) [Postgraduate]", table_cell_style)],
        [Paragraph("<b>Broad Theme (KSCST):</b>", table_cell_style), Paragraph("<b>Theme 1: Sustainable Agriculture, Food Security & Rural Development</b> (Cross-cutting: Theme 4 & 6)", table_cell_style)],
        [Paragraph("<b>Project Guide Name:</b>", table_cell_style), Paragraph("Dr. DWARAKANATH G V, Project Coordinator & Associate Professor, Dept. of MCA, BMSITM", table_cell_style)],
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
    story.append(Spacer(1, 10))

    # Declaration by Students
    story.append(Paragraph("DECLARATION BY STUDENTS", h1_style))
    story.append(Paragraph("We, the undersigned final year students of the Department of Master of Computer Applications (MCA), BMS Institute of Technology & Management, Bengaluru, hereby declare that the project proposal entitled <b>'Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring'</b> is a bona fide record of independent research and engineering work planned and executed by us under the guidance of Dr. Dwarakanath G V. This proposal has not been submitted previously to any other university, organization, or funding agency for the award of any degree, diploma, or financial sponsorship.", body_style))
    story.append(Spacer(1, 4))

    sig_table_data = [
        [Paragraph("Sl.", table_header_style), Paragraph("Name of Student", table_header_style), Paragraph("USN", table_header_style), Paragraph("Signature with Date", table_header_style)],
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
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_sig)
    story.append(Spacer(1, 14))

    # Institutional Endorsements
    story.append(Paragraph("ENDORSEMENT BY PROJECT GUIDE, HOD & HEAD OF INSTITUTION", h1_style))
    story.append(Paragraph("This is to certify that the project proposal entitled <b>'Agri Rover: Autonomous IoT Agricultural Vehicle for Precision Crop Care and Soil Health Monitoring'</b> submitted by Thanmay M, Keerthana, Mohan, and Monica, final year MCA students of BMSITM, is an original research and engineering endeavor. The project has been reviewed and endorsed for submission under the 50th Series of the Student Project Programme (SPP: 2026–2027) of the Karnataka State Council for Science and Technology (KSCST). All necessary institutional laboratory and computing facilities will be provided to the students.", body_style))
    story.append(Spacer(1, 8))

    end_boxes_data = [
        [
            Paragraph("<b>Signature of Project Guide:</b><br/><br/><br/><br/><br/>___________________________<br/><b>Dr. DWARAKANATH G V</b><br/>Project Coordinator / Assoc. Prof<br/>Dept. of MCA, BMSITM<br/>Date: 26/11/2026", table_cell_style),
            Paragraph("<b>Signature of HOD:</b><br/><br/><br/><br/><br/>___________________________<br/><b>Dr. APARNA K / HOD</b><br/>Head of the Department<br/>Dept. of MCA, BMSITM<br/>Date: 26/11/2026", table_cell_style),
            Paragraph("<b>Signature of Principal:</b><br/><br/><br/><br/><br/>___________________________<br/><b>Dr. MOHAN BABU G N</b><br/>Principal / Head of Institution<br/>BMSITM, Bengaluru<br/>(Official College Seal)", table_cell_style)
        ]
    ]
    t_end = Table(end_boxes_data, colWidths=[165, 170, 170])
    t_end.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_end)

    doc.build(story)
    print(f"SUCCESS: {pdf_filename} generated cleanly!")

if __name__ == "__main__":
    build_endorsement_pdf()
