import io
import os
from weasyprint import HTML
import streamlit as st

def generate_fee_receipt_pdf(data: dict) -> bytes:
    """
    Generates a professional Fee Receipt PDF using WeasyPrint
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{
                size: A4;
                margin: 15mm 12mm;
                background-color: #ffffff;
            }}
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                color: #2c3e50;
            }}
            .receipt-card {{
                border: 2px solid #2c3e50;
                padding: 20px;
                border-radius: 8px;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #2c3e50;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .header h1 {{
                margin: 0;
                color: #1a5276;
                font-size: 22pt;
            }}
            .header p {{
                margin: 4px 0;
                font-size: 10pt;
                color: #566573;
            }}
            .details-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .details-table td {{
                padding: 8px;
                font-size: 11pt;
            }}
            .bold {{
                font-weight: bold;
            }}
            .payment-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}
            .payment-table th, .payment-table td {{
                border: 1px solid #bdc3c7;
                padding: 10px;
                text-align: left;
                font-size: 11pt;
            }}
            .payment-table th {{
                background-color: #f2f4f4;
            }}
            .footer {{
                margin-top: 40px;
                display: table;
                width: 100%;
            }}
            .footer-cell {{
                display: table-cell;
                width: 50%;
                font-size: 10pt;
            }}
            .text-right {{
                text-align: right;
            }}
        </style>
    </head>
    <body>
        <div class="receipt-card">
            <div class="header">
                <h1>CAMPUS SCHOOL ERP PRO</h1>
                <p>Affiliated to CBSE Board | Excellence in Education</p>
                <p>Phone: +91 9876543210 | Email: info@campusschool.edu</p>
                <h3 style="margin-top: 10px; text-decoration: underline;">FEE RECEIPT</h3>
            </div>

            <table class="details-table">
                <tr>
                    <td class="bold">Receipt No:</td>
                    <td>{data.get('receipt_no', 'N/A')}</td>
                    <td class="bold">Date:</td>
                    <td>{data.get('payment_date', 'N/A')}</td>
                </tr>
                <tr>
                    <td class="bold">SR Number:</td>
                    <td>{data.get('sr_no', 'N/A')}</td>
                    <td class="bold">Student Name:</td>
                    <td>{data.get('student_name', 'N/A')}</td>
                </tr>
                <tr>
                    <td class="bold">Class & Sec:</td>
                    <td>{data.get('class', '')} - {data.get('section', '')}</td>
                    <td class="bold">Payment Mode:</td>
                    <td>{data.get('payment_mode', 'Cash')}</td>
                </tr>
            </table>

            <table class="payment-table">
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Amount (₹)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Total Fee Due</td>
                        <td>₹ {float(data.get('total_due', 0)):,.2f}</td>
                    </tr>
                    <tr>
                        <td>Discount / Concession</td>
                        <td>₹ {float(data.get('discount', 0)):,.2f}</td>
                    </tr>
                    <tr>
                        <td class="bold">Amount Paid Today</td>
                        <td class="bold" style="color: #27ae60;">₹ {float(data.get('amount_paid', 0)):,.2f}</td>
                    </tr>
                    <tr>
                        <td class="bold">Remaining Balance</td>
                        <td class="bold" style="color: #c0392b;">₹ {max(0, float(data.get('total_due', 0)) - float(data.get('amount_paid', 0)) - float(data.get('discount', 0))):,.2f}</td>
                    </tr>
                </tbody>
            </table>

            <p style="margin-top: 15px; font-size: 10pt;"><b>Remarks:</b> {data.get('remarks', 'N/A')}</p>

            <div class="footer">
                <div class="footer-cell">
                    <p>Depositor Signature: _______________</p>
                </div>
                <div class="footer-cell text-right">
                    <p>Authorized Signatory: _______________</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes
