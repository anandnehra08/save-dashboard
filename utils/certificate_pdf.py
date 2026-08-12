import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_certificate_pdf(cert_data, output_filename="certificate.pdf"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E1B4B'),
        alignment=1
    )
    
    subtitle_style = ParagraphStyle(
        'CertSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        textColor=colors.HexColor('#475569'),
        alignment=1
    )
    
    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#1E1B4B'),
        alignment=1
    )
    
    body_style = ParagraphStyle(
        'CertBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=22,
        textColor=colors.HexColor('#334155'),
        alignment=4
    )
    
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#0F172A')
    )

    meta_right = ParagraphStyle(
        'MetaRight',
        parent=meta_style,
        alignment=2
    )

    story.append(Paragraph("CAMPUS SCHOOL ERP SUITE", title_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Main Campus, Education Hub City | Contact: +91 98765 43210", subtitle_style))
    story.append(Spacer(1, 15))
    
    meta_data = [
        [
            Paragraph(f"<b>Cert No:</b> {cert_data.get('cert_no', 'N/A')}", meta_style),
            Paragraph(f"<b>Date:</b> {cert_data.get('issue_date', 'N/A')}", meta_right)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[350, 350])
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph(f"<u>{cert_data.get('cert_type', 'CERTIFICATE')}</u>", badge_style))
    story.append(Spacer(1, 20))
    
    student_name = cert_data.get('student_name', '')
    father_name = cert_data.get('father_name', '')
    mother_name = cert_data.get('mother_name', '')
    class_sec = cert_data.get('class_sec', '')
    dob = cert_data.get('dob', 'N/A')
    reason_conduct = cert_data.get('reason_conduct', 'Good')

    text = f"This is to certify that Master / Ms. <b>{student_name}</b>, Son / Daughter of Shri <b>{father_name}</b> and Smt. <b>{mother_name}</b>, is / was a bona fide student of this institution studying in <b>{class_sec}</b>.<br/><br/>According to the school register, his / her Date of Birth is <b>{dob}</b>.<br/>Remarks / Conduct: <b>{reason_conduct}</b>.<br/>He / She bears a good moral character during his / her stay in the school. We wish him / her all success in future endeavors."
    
    story.append(Paragraph(text, body_style))
    story.append(Spacer(1, 40))
    
    sig_data = [
        [
            Paragraph("____________________<br/>Prepared By", subtitle_style),
            Paragraph("____________________<br/>Checked By", subtitle_style),
            Paragraph("____________________<br/>Principal / Office Seal", subtitle_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[230, 230, 230])
    story.append(sig_table)
    
    doc.build(story)
    
    with open(output_filename, "wb") as f:
        f.write(buffer.getvalue())
        
    return output_filename
