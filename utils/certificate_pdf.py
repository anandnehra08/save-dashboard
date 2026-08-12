from weasyprint import HTML

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
