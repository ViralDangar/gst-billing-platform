from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Flowable
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO


def safe_get(data, key, default=""):
    """Safely retrieves a value from a dict, returning default if missing or None."""
    val = data.get(key)
    return val if val is not None else default


def safe_decimal(val, decimal_places=2):
    """Formats a number to decimal string, returns empty string if None/Empty."""
    if val is None or val == "":
        return ""
    try:
        return f"{float(val):.{decimal_places}f}"
    except (ValueError, TypeError):
        return ""


def number_to_words(num):
    """Convert a number to words (Indian numbering system)."""
    if num is None or num == "":
        return ""
    
    try:
        num = float(num)
    except:
        return ""
    
    if num == 0:
        return "Zero"
    
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def two_digits(n):
        if n < 20:
            return ones[n]
        else:
            return tens[n // 10] + (" " + ones[n % 10] if n % 10 else "")
    
    def three_digits(n):
        if n < 100:
            return two_digits(n)
        else:
            return ones[n // 100] + " Hundred" + (" " + two_digits(n % 100) if n % 100 else "")
    
    if num < 0:
        return "Minus " + number_to_words(-num)
    
    # Handle decimal part
    rupees = int(num)
    paise = int(round((num - rupees) * 100))
    
    if rupees == 0:
        words = ""
    elif rupees < 1000:
        words = three_digits(rupees)
    elif rupees < 100000:  # Less than 1 lakh
        words = two_digits(rupees // 1000) + " Thousand"
        if rupees % 1000:
            words += " " + three_digits(rupees % 1000)
    elif rupees < 10000000:  # Less than 1 crore
        words = two_digits(rupees // 100000) + " Lakh"
        if (rupees % 100000) // 1000:
            words += " " + two_digits((rupees % 100000) // 1000) + " Thousand"
        if rupees % 1000:
            words += " " + three_digits(rupees % 1000)
    else:  # 1 crore and above
        words = three_digits(rupees // 10000000) + " Crore"
        if (rupees % 10000000) // 100000:
            words += " " + two_digits((rupees % 10000000) // 100000) + " Lakh"
        if (rupees % 100000) // 1000:
            words += " " + two_digits((rupees % 100000) // 1000) + " Thousand"
        if rupees % 1000:
            words += " " + three_digits(rupees % 1000)
    
    result = words + " Rupees" if words else ""
    if paise:
        result += " and " + two_digits(paise) + " Paise"
    
    return result.strip() + " Only"


class RoundedBox(Flowable):
    """A flowable that draws a rounded rectangle box around content."""
    
    def __init__(self, content, width, padding=5, radius=8, stroke_color=colors.black, stroke_width=0.5, fill_color=None):
        Flowable.__init__(self)
        self.content = content
        self.box_width = width
        self.padding = padding
        self.radius = radius
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.fill_color = fill_color
        
        self.content_width, self.content_height = content.wrap(width - 2 * padding, 10000)
        self.width = width
        self.height = self.content_height + 2 * padding
    
    def wrap(self, availWidth, availHeight):
        return self.width, self.height
    
    def draw(self):
        canvas = self.canv
        canvas.setStrokeColor(self.stroke_color)
        canvas.setLineWidth(self.stroke_width)
        
        if self.fill_color:
            canvas.setFillColor(self.fill_color)
            canvas.roundRect(0, 0, self.width, self.height, self.radius, stroke=1, fill=1)
        else:
            canvas.roundRect(0, 0, self.width, self.height, self.radius, stroke=1, fill=0)
        
        self.content.drawOn(canvas, self.padding, self.padding)


class RoundedTable(Flowable):
    """A flowable that draws a table with rounded corner border."""
    
    def __init__(self, table, radius=8, stroke_color=colors.black, stroke_width=0.5):
        Flowable.__init__(self)
        self.table = table
        self.radius = radius
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        
        self.table_width, self.table_height = table.wrap(0, 0)
        self.width = self.table_width
        self.height = self.table_height
    
    def wrap(self, availWidth, availHeight):
        self.table_width, self.table_height = self.table.wrap(availWidth, availHeight)
        self.width = self.table_width
        self.height = self.table_height
        return self.width, self.height
    
    def draw(self):
        canvas = self.canv
        self.table.drawOn(canvas, 0, 0)
        canvas.setStrokeColor(self.stroke_color)
        canvas.setLineWidth(self.stroke_width)
        canvas.roundRect(0, 0, self.width, self.height, self.radius, stroke=1, fill=0)


def generate_invoice_pdf(invoice_data):
    """
    Generates a PDF matching the 'Dev Enterprise' invoice layout with rounded corners.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=8 * mm,
        leftMargin=8 * mm,
        topMargin=8 * mm,
        bottomMargin=8 * mm,
    )

    styles = getSampleStyleSheet()

    # ============ Custom Styles ============
    style_title = ParagraphStyle(
        'Title', parent=styles['Heading1'], alignment=TA_CENTER,
        fontSize=14, fontName='Helvetica-Bold', spaceAfter=0, spaceBefore=0
    )
    style_subtitle = ParagraphStyle(
        'Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, spaceAfter=2
    )
    style_company_name = ParagraphStyle(
        'CompanyName', parent=styles['Heading1'], alignment=TA_CENTER,
        fontSize=22, fontName='Helvetica-Bold', spaceAfter=2, spaceBefore=4
    )
    style_center = ParagraphStyle(
        'Center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, leading=11
    )
    style_gstin_header = ParagraphStyle(
        'GSTINHeader', parent=styles['Normal'], alignment=TA_LEFT,
        fontSize=11, fontName='Helvetica-Bold', spaceBefore=4, spaceAfter=4
    )
    style_left_bold = ParagraphStyle(
        'LeftBold', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', leading=12
    )
    style_left = ParagraphStyle(
        'Left', parent=styles['Normal'], fontSize=10, leading=12
    )
    style_table_header = ParagraphStyle(
        'TableHeader', parent=styles['Normal'], alignment=TA_CENTER,
        fontSize=10, fontName='Helvetica-Bold', leading=10
    )
    style_table_cell = ParagraphStyle(
        'TableCell', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, leading=10
    )
    style_table_cell_left = ParagraphStyle(
        'TableCellLeft', parent=styles['Normal'], alignment=TA_LEFT, fontSize=8, leading=10
    )
    style_table_cell_right = ParagraphStyle(
        'TableCellRight', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=8, leading=10
    )
    style_small = ParagraphStyle(
        'Small', parent=styles['Normal'], fontSize=7, leading=9
    )
    style_small_bold = ParagraphStyle(
        'SmallBold', parent=styles['Normal'], fontSize=7, fontName='Helvetica-Bold', leading=9
    )
    style_footer_right = ParagraphStyle(
        'FooterRight', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=8, leading=10
    )
    style_footer_right_bold = ParagraphStyle(
        'FooterRightBold', parent=styles['Normal'], alignment=TA_RIGHT,
        fontSize=8, fontName='Helvetica-Bold', leading=10
    )

    elements = []
    page_width = A4[0] - 16 * mm

    full_width = 194 * mm

    # ================= EXTRACT DATA =================
    s_name = safe_get(invoice_data, 'seller_name')
    s_addr = safe_get(invoice_data, 'seller_address')
    s_mobile = safe_get(invoice_data, 'seller_mobile')
    s_email = safe_get(invoice_data, 'seller_email')
    s_gst = safe_get(invoice_data, 'seller_gstin')
    s_state = safe_get(invoice_data, 'seller_state')
    s_bank = safe_get(invoice_data, 'seller_bank_details')
    
    # Parse bank details if available
    bank_name = ""
    bank_branch = ""
    bank_ac = ""
    bank_ifsc = ""
    if s_bank:
        bank_name = s_bank
    
    b_name = safe_get(invoice_data, 'customer_name')
    b_addr = safe_get(invoice_data, 'customer_address')
    b_gst = safe_get(invoice_data, 'customer_gstin')
    b_state = safe_get(invoice_data, 'customer_state')

    inv_no = safe_get(invoice_data, 'invoice_number')
    inv_date = invoice_data.get('invoice_date')
    if inv_date:
        if hasattr(inv_date, 'strftime'):
            inv_date = inv_date.strftime('%d/%m/%Y')
        else:
            inv_date = str(inv_date)
    else:
        inv_date = ""

    # ================= 1. TOP HEADER WITH ROUNDED BOX =================
    header_content_data = [
        [Paragraph("<b><u>TAX INVOICE</u></b>", style_title)],
        [Paragraph("<b>Subject to Mumbai Jurisdiction</b>", style_subtitle)],
        # [Spacer(1, 2 * mm)],
        [Paragraph(f"<b>{s_name}</b>", style_company_name)],
        [Paragraph(s_addr, style_center)],
    ]

    # Add contact details if available
    contact_parts = []
    if s_mobile:
        contact_parts.append(f"Mobile: {s_mobile}")
    if s_email:
        contact_parts.append(f"Email: {s_email}")
    if contact_parts:
        header_content_data.append([Paragraph(" | ".join(contact_parts), style_subtitle)])

    header_content_data.append([Paragraph(f"<b>GSTIN No. : {s_gst}</b>", style_gstin_header)])
    
    header_content_table = Table(header_content_data, colWidths=[page_width - 10])
    header_content_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    
    header_box = RoundedBox(header_content_table, width=page_width, padding=8, radius=10)
    elements.append(header_box)
    
    elements.append(Spacer(1, 2 * mm))
    # elements.append(Paragraph(f"<b>GSTIN No. : {s_gst}</b>", style_gstin_header))

    # ================= 2. BUYER & INVOICE DETAILS GRID =================
    buyer_content = [
        Paragraph(f"<b>M/s. {b_name}</b>", style_left_bold),
        Paragraph(b_addr, style_left),
        # Spacer(1, 2 * mm),
        Paragraph(f"State Code : {s_state}", style_left),
        Paragraph(f"<b>GSTIN Number : {b_gst}</b>", style_left_bold),
    ]

    inv_detail_data = [
        [Paragraph(f"<b>Invoice No.: {inv_no} </b>", style_left)],
        [Paragraph(f"<b>Date &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp .: {inv_date} </b>", style_left)],
        [Paragraph(f"<b>P.O. No &nbsp&nbsp&nbsp .: {inv_date}</b>", style_left)],

        # [Paragraph("", style_left), Paragraph("", style_left)],
        [Paragraph(f"<b>State Code.: {s_state}</b>", style_left), Paragraph("", style_left)],
    ]

    # inv_detail_table = Table(inv_detail_data, colWidths=[30 * mm, 55 * mm])
    # inv_detail_table.setStyle(TableStyle([
    #     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    #     ('LEFTPADDING', (0, 0), (-1, -1), 0),
    #     ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    #     ('TOPPADDING', (0, 0), (-1, -1), 1),
    #     ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    #     ('SPAN', (0, 3), (1, 3)),
    # ]))

    header_data = [[buyer_content, inv_detail_data]]
    header_table = Table(header_data, colWidths=[100 * mm, 94 * mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBEFORE', (1, 0), (1, 0), 0.5, colors.black),  # Vertical line between buyer and invoice

    ]))
    
    buyer_invoice_box = RoundedTable(header_table, radius=8)
    elements.append(buyer_invoice_box)
    elements.append(Spacer(1, 2 * mm))

    # ================= 3. ITEM TABLE =================
    # Determine if IGST or CGST/SGST based on tax_summary
    tax_summary = safe_get(invoice_data, 'tax_summary', {})
    is_igst = 'IGST' in tax_summary
    
    if is_igst:
        headers = ['Sr.\nNo.', 'Description', 'HSN/SAC\nCODE', 'Qty', 'Rate', 'IGST\n%', 'Amount']
        col_widths = [10*mm, 65*mm, 22*mm, 18*mm, 22*mm, 18*mm, 36*mm]  # = 194mm
    else:
        headers = ['Sr.\nNo.', 'Description', 'HSN/SAC\nCODE', 'Qty', 'Rate', 'CGST\n%', 'SGST\n%', 'Amount']
        col_widths = [10*mm, 55*mm, 21*mm, 15*mm, 20*mm, 15*mm, 15*mm, 43*mm]  # = 194mm

    data = []
    data.append([Paragraph(h, style_table_header) for h in headers])

    items = safe_get(invoice_data, 'items', [])
    total_qty = 0
    total_amt = 0

    for idx, item in enumerate(items, 1):
        qty_val = item.get('quantity')
        rate_val = item.get('rate')
        amt_val = item.get('taxable_value')
        gst_rate = item.get('gst_rate', 0)

        try:
            total_qty += float(qty_val) if qty_val else 0
        except:
            pass
        try:
            total_amt += float(amt_val) if amt_val else 0
        except:
            pass

        if is_igst:
            row = [
                Paragraph(str(idx), style_table_cell),
                Paragraph(safe_get(item, 'product_name'), style_table_cell_left),
                Paragraph(safe_get(item, 'hsn_sac'), style_table_cell),
                Paragraph(safe_decimal(qty_val, 0) if qty_val else "", style_table_cell),
                Paragraph(safe_decimal(rate_val), style_table_cell_right),
                Paragraph(safe_decimal(gst_rate, 0) if gst_rate else "", style_table_cell),
                Paragraph(safe_decimal(amt_val), style_table_cell_right),
            ]
        else:
            half_gst = float(gst_rate) / 2 if gst_rate else 0
            row = [
                Paragraph(str(idx), style_table_cell),
                Paragraph(safe_get(item, 'product_name'), style_table_cell_left),
                Paragraph(safe_get(item, 'hsn_sac'), style_table_cell),
                Paragraph(safe_decimal(qty_val, 0) if qty_val else "", style_table_cell),
                Paragraph(safe_decimal(rate_val), style_table_cell_right),
                Paragraph(safe_decimal(half_gst, 0) if half_gst else "", style_table_cell),
                Paragraph(safe_decimal(half_gst, 0) if half_gst else "", style_table_cell),
                Paragraph(safe_decimal(amt_val), style_table_cell_right),
            ]
        data.append(row)

    # Fill empty rows
    min_rows = 12
    num_cols = len(headers)
    while len(data) < min_rows:
        data.append([''] * num_cols)

    item_table = Table(data, colWidths=col_widths, repeatRows=1)
    item_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
        ('LINEAFTER', (0, 0), (-2, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    
    item_table_box = RoundedTable(item_table, radius=8)
    elements.append(item_table_box)
    elements.append(Spacer(1, 2 * mm))

    # ================= 4. TAX ANALYSIS & SUMMARY SECTION =================
    tax_headers = ['GST %', 'Taxable Amt', 'CGST Amt', 'SGST Amt', 'IGST Amt', 'Total Amt']
    tax_data = [[Paragraph(h, style_table_header) for h in tax_headers]]

    gst_rates = ['0 %', '5 %', '12 %', '18 %', '28 %']
    
    # Build tax analysis from items
    tax_breakdown = {}
    for item in items:
        gst_rate = item.get('gst_rate', 0)
        taxable = item.get('taxable_value', 0)
        rate_key = f"{int(gst_rate)} %"
        if rate_key not in tax_breakdown:
            tax_breakdown[rate_key] = {'taxable': 0, 'cgst': 0, 'sgst': 0, 'igst': 0, 'total': 0}
        tax_breakdown[rate_key]['taxable'] += float(taxable) if taxable else 0
        tax_amt = (float(taxable) * float(gst_rate) / 100) if taxable and gst_rate else 0
        if is_igst:
            tax_breakdown[rate_key]['igst'] += tax_amt
        else:
            tax_breakdown[rate_key]['cgst'] += tax_amt / 2
            tax_breakdown[rate_key]['sgst'] += tax_amt / 2
        tax_breakdown[rate_key]['total'] += (float(taxable) if taxable else 0) + tax_amt

    for rate in gst_rates:
        tax_line = tax_breakdown.get(rate, {})
        row = [
            Paragraph(rate, style_table_cell),
            Paragraph(safe_decimal(tax_line.get('taxable')), style_table_cell_right),
            Paragraph(safe_decimal(tax_line.get('cgst')), style_table_cell_right),
            Paragraph(safe_decimal(tax_line.get('sgst')), style_table_cell_right),
            Paragraph(safe_decimal(tax_line.get('igst')), style_table_cell_right),
            Paragraph(safe_decimal(tax_line.get('total')), style_table_cell_right),
        ]
        tax_data.append(row)

    # Totals
    taxable_total = safe_get(invoice_data, 'taxable_total', 0)
    tax_total = safe_get(invoice_data, 'tax_total', 0)
    grand_total = safe_get(invoice_data, 'grand_total', 0)
    
    total_cgst = 0
    total_sgst = 0
    total_igst = 0
    for tb in tax_breakdown.values():
        total_cgst += tb.get('cgst', 0)
        total_sgst += tb.get('sgst', 0)
        total_igst += tb.get('igst', 0)

    tax_total_row = [
        Paragraph('<b>Total</b>', style_table_header),
        Paragraph(safe_decimal(taxable_total), style_table_cell_right),
        Paragraph(safe_decimal(total_cgst) if total_cgst else "", style_table_cell_right),
        Paragraph(safe_decimal(total_sgst) if total_sgst else "", style_table_cell_right),
        Paragraph(safe_decimal(total_igst) if total_igst else "", style_table_cell_right),
        Paragraph(safe_decimal(grand_total), style_table_cell_right),
    ]
    tax_data.append(tax_total_row)
    

    tax_col_widths = [18*mm, 28*mm, 24*mm, 24*mm, 24*mm, 28*mm]  # = 148mm for tax table
    tax_table = Table(tax_data, colWidths=tax_col_widths)
    tax_table.setStyle(TableStyle([
    ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.black),
    ('LINEAFTER', (0,0), (-2,-1), 0.5, colors.black),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 1),      # Changed from 3 to 1
    ('BOTTOMPADDING', (0,0), (-1,-1), 1),   # Changed from 3 to 1
    ('LEFTPADDING', (0,0), (-1,-1), 2),
    ('RIGHTPADDING', (0,0), (-1,-1), 2),
]))

    # Summary Table - always have at least one row
    summary_data = []
    summary_data.append([
        Paragraph("", style_footer_right),
        Paragraph(safe_decimal(taxable_total), style_footer_right)
    ])
    if is_igst and total_igst:
        summary_data.append([
            Paragraph("Add : IGST", style_footer_right),
            Paragraph(safe_decimal(total_igst), style_footer_right)
        ])
    else:
        if total_cgst:
            summary_data.append([
                Paragraph("Add : CGST", style_footer_right),
                Paragraph(safe_decimal(total_cgst), style_footer_right)
            ])
        if total_sgst:
            summary_data.append([
                Paragraph("Add : SGST", style_footer_right),
                Paragraph(safe_decimal(total_sgst), style_footer_right)
            ])

    summary_table = Table(summary_data, colWidths=[20 * mm, 28 * mm])
    summary_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    
    # summary_box = RoundedTable(summary_table, radius=6)
    # tax_table_rounded = RoundedTable(tax_table, radius=6)
    
    combined_data = [[tax_table, summary_table]]
    combined_table = Table(combined_data, colWidths=[146*mm, 48*mm])  # Adjusted widths
    combined_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LINEBEFORE', (1,0), (1,0), 0.5, colors.black),  # Line between tax and summary
    ]))

    elements.append(RoundedTable(combined_table, radius=8))
    elements.append(Spacer(1, 2 * mm))

    # elements.append(Spacer(1, 2 * mm))
    # ================= 5. RUPEES IN WORDS & GRAND TOTAL ROW =================
    amt_words = number_to_words(grand_total)

    rupees_grand_data = [[
        Paragraph(f"<b>Rupees:</b> {amt_words}", style_left),
        Paragraph("<b>GRAND TOTAL</b>", style_footer_right),
        Paragraph(f"<b>{safe_decimal(grand_total)}</b>", style_footer_right)
    ]]
    rupees_grand_table = Table(rupees_grand_data, colWidths=[128 * mm, 34 * mm, 32 * mm])
    rupees_grand_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBEFORE', (1, 0), (1, 0), 0.5, colors.black),  # Vertical line before Bank Details
        ('LINEAFTER', (1, 0), (1, 0), 0.5, colors.black),   # Vertical line after Bank Details
    ]))
    
    rupees_grand_box = RoundedTable(rupees_grand_table, radius=6)
    elements.append(rupees_grand_box)
    elements.append(Spacer(1, 2 * mm))


    # ================= 6. FOOTER =================
    terms_content = [
        Paragraph("<b>Terms &amp; Conditions</b>", style_small_bold),
        Paragraph("● Goods Once sold will not be taken back or exchanged.", style_small),
        Paragraph(f"● A/c payee cheques to be drawn in favour of", style_small),
        Paragraph(f"   {s_name}", style_small),
        Paragraph("● Interest at the rate of 18% per anum will be charged", style_small),
        Paragraph("   on all bill not paid within 30 days from the bill date.", style_small),
        Paragraph("● Complaints of any nature must be communicated in", style_small),
        Paragraph("   writing within 7 days from the date of delivery", style_small),
    ]

    bank_content = [
        Paragraph("<b>Bank Details</b>", style_small_bold),
        Paragraph(f"Bank Name : {bank_name}", style_small),
        Paragraph(f"Branch       : {bank_branch}", style_small),
        Paragraph(f"Account No.: {bank_ac}", style_small),
        Paragraph(f"IFSC Code  : {bank_ifsc}", style_small),
    ]

    sig_content = [
        Paragraph("E. &amp; O.E.", style_footer_right),
        Paragraph(f"FOR {s_name.upper()}", style_footer_right_bold),
        Spacer(1, 15 * mm),
        Paragraph("<b>Authorised Signatory</b>", style_footer_right_bold),
    ]

    footer_data = [[terms_content, bank_content, sig_content]]
    footer_table = Table(footer_data, colWidths=[70 * mm, 70 * mm, 54 * mm])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBEFORE', (1, 0), (1, 0), 0.5, colors.black),  # Vertical line between buyer and invoice

    ]))
    
    footer_box = RoundedTable(footer_table, radius=8)
    elements.append(footer_box)

    # ================= 7. CERTIFICATION TEXT =================
    elements.append(Spacer(1, 2 * mm))
    cert_text = "Certified that the particulars given above are true and correct and the amount indicated represents the price actually charged and that there is no additional consideration flowing, directly or indirectly from the buyer."
    elements.append(Paragraph(cert_text, style_small))

    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf