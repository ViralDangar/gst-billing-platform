from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from io import BytesIO

from app.document_service.pdf.styles import styles


def generate_invoice_pdf(invoice: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    elements = []

    # 🧾 HEADER
    elements.append(Paragraph(
        f"<b>{invoice['seller_name']}</b>", styles["Title"]
    ))
    elements.append(Spacer(1, 6))

    elements.append(Paragraph(
        f"GSTIN: {invoice['seller_gstin']}", styles["Normal"]
    ))

    elements.append(Spacer(1, 10))

    # 🧑 CUSTOMER
    elements.append(Paragraph(
        f"<b>Bill To:</b> {invoice['customer_name']}", styles["Normal"]
    ))
    elements.append(Paragraph(
        invoice["customer_address"], styles["Normal"]
    ))
    elements.append(Spacer(1, 10))

    # 📦 ITEM TABLE
    table_data = [
        ["Sr", "Description", "HSN", "Qty", "Rate", "Amount"]
    ]

    for idx, item in enumerate(invoice["items"], start=1):
        table_data.append([
            idx,
            item["product_name"],
            item["hsn_sac"] or "",
            item["quantity"],
            item["rate"],
            item["taxable_value"],
        ])

    table = Table(table_data, colWidths=[20, 120, 50, 40, 50, 60])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 10))

    # 🧮 TAX SUMMARY
    tax_data = [
        ["Taxable Total", invoice["taxable_total"]],
    ]

    for tax in invoice["taxes"]:
        tax_data.append(
            [f"{tax['tax_type']} @ {tax['tax_rate']}%", tax["tax_amount"]]
        )

    tax_data.extend([
        ["Round Off", invoice["round_off"]],
        ["GRAND TOTAL", invoice["grand_total"]],
    ])

    tax_table = Table(tax_data, colWidths=[300, 100])
    tax_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
    ]))

    elements.append(tax_table)

    # ✍ FOOTER
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "For <b>{}</b>".format(invoice["seller_name"]),
        styles["Normal"]
    ))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Authorized Signatory", styles["Normal"]))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    return pdf
