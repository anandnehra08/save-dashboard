import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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
    
    # Custom Styles
    title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E1B4B'),
        alignment=1 # Center
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
        alignment=4 # Justify
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
        alignment=2 # Right
    )

    # Header
    story.append(Paragraph("CAMPUS SCHOOL ERP SUITE", title_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Main Campus, Education Hub City | Contact: +91 98765 43210", subtitle_style))
    story.append(Spacer(1, 15))
    
    # Cert Meta Row
    meta_data = [
        [Paragraph(f"<b>Cert No:</b> {cert_data.get('cert_no', 'N/A')}", meta_style),
         Paragraph(f"<b>Date:</b> {cert_data.get('issue_date', 'N/A')}", meta_right)]
    ]
    meta_table = Table(meta_data, colWidths=[350, 350])
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # Badge
    story.append(Paragraph(f"<u>{cert_data.get('cert_type', 'CERTIFICATE')}</u>", badge_style))
    story.append(Spacer(1, 20))
    
    # Main Content
    text = f"""
    This is to certify that Master / Ms. <b>{cert_data.get('student_name', '')}</b>, 
    Son / Daughter of Shri <b>{cert_data.get('father_name', '')}</b> and Smt. <b>{cert_data.get('mother_name', '')}</b>, 
    is / was a bona fide student of this institution studying in <b>{cert_data.get('class_sec', '')}</b>.<br/><br/>
    According to the school register, his / her Date of Birth is <b>{cert_data.get('dob', 'N/A')}</b>.<br/>
    Remarks / Conduct: <b>{cert_data.get('reason_conduct', 'Good')}</b>.<br/>
    He / She bears a good moral character during his / her stay in the school. We wish him / her all success in future endeavors.
    """
    story.append(Paragraph(text, body_style))
    story.append(Spacer(1, 40))
    
    # Signatures
    sig_data = [
        [Paragraph("____________________<br/>Prepared By", subtitle_style),
         Paragraph("____________________<br/>Checked By", subtitle_style),
         Paragraph("____________________<br/>Principal / Office Seal", subtitle_style)]
    ]
    sig_table = Table(sig_data, colWidths=[230, 230, 230])
    story.append(sig_table)
    
    doc.build(story)
    
    with open(output_filename, "wb") as f:
        f.write(buffer.getvalue())
        
    return output_filenamefrom weasyprint import HTML

def generate_certificate_pdf(cert_data, output_filename="certificate.pdf"):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @page {{ size: A4 landscape; margin: 15mm; }}
        body {{ font-family: 'Georgia', serif; color: #1e1b4b; margin: 0; padding: 0; }}
        .border-outer {{ border: 5px solid #1E1B4B; padding: 5px; height: 95%; }}
        .border-inner {{ border: 2px solid #312E81; padding: 25px; height: 93%; text-align: center; background: #fafafa; }}
        .header h1 {{ font-size: 28pt; margin: 0; color: #1E1B4B; text-transform: uppercase; }}
        .header p {{ font-size: 11pt; margin: 5px 0 0 0; color: #475569; italic; }}
        .title-badge {{ display: inline-block; border-bottom: 2px solid #1E1B4B; padding: 4px 20px; margin: 20px 0; font-size: 18pt; font-weight: bold; text-transform: uppercase; color: #1E1B4B; }}
        .cert-body {{ font-size: 13pt; line-height: 2.2; text-align: justify; margin: 20px 40px; color: #334155; }}
        .underline-text {{ border-bottom: 1px dotted #1E1B4B; font-weight: bold; color: #0f172a; padding: 0 8px; }}
        .footer {{ margin-top: 50px; display: table; width: 100%; font-size: 11pt; }}
        .footer-cell {{ display: table-cell; width: 33%; text-align: center; vertical-align: bottom; }}
    </style>
    </head>
    <body>
        <div class="border-outer">
            <div class="border-inner">
                <div class="header">
                    <h1>Campus School ERP Suite</h1>
                    <p>Main Campus, Education Hub City | Contact: +91 98765 43210</p>
                </div>
                <div style="text-align: left; font-size: 10pt; margin-top: 10px;">
                    <strong>Cert No:</strong> {cert_data['cert_no']} <span style="float: right;"><strong>Date:</strong> {cert_data['issue_date']}</span>
                </div>
                <div class="title-badge">{cert_data['cert_type']}</div>
                <div class="cert-body">
                    This is to certify that Master / Ms. <span class="underline-text">{cert_data['student_name']}</span>, 
                    Son / Daughter of Shri <span class="underline-text">{cert_data['father_name']}</span> 
                    and Smt. <span class="underline-text">{cert_data['mother_name']}</span>, 
                    is / was a bona fide student of this institution studying in 
                    <span class="underline-text">{cert_data['class_sec']}</span>.
                    <br><br>
                    According to the school register, his / her Date of Birth is <span class="underline-text">{cert_data['dob']}</span>.
                    <br>
                    Remarks / Conduct: <span class="underline-text">{cert_data['reason_conduct']}</span>.
                    He / She bears a good moral character during his / her stay in the school. We wish him / her all success in future endeavors.
                </div>
                <div class="footer">
                    <div class="footer-cell"><p>____________________<br>Prepared By</p></div>
                    <div class="footer-cell"><p>____________________<br>Checked By</p></div>
                    <div class="footer-cell"><p>____________________<br>Principal / Office Seal</p></div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    HTML(string=html_content).write_pdf(output_filename)
    return output_filename
