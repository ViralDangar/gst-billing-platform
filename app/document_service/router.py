from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi.responses import StreamingResponse
from app.document_service.pdf.invoice_pdf import generate_invoice_pdf
from io import BytesIO
from app.core.database import get_db
from app.document_service.schemas import InvoicePreviewResponse
from app.document_service.service import get_invoice_preview

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("/health")
def documents_health():
    return {"service": "documents", "status": "ok"}

@router.get(
    "/invoices/{invoice_id}/preview",
    response_model=InvoicePreviewResponse,
)
def invoice_preview(invoice_id: UUID, db: Session = Depends(get_db)):
    try:
        return get_invoice_preview(db, invoice_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/invoices/{invoice_id}/pdf")
def invoice_pdf(invoice_id: UUID, db: Session = Depends(get_db)):
    try:
        invoice_data = get_invoice_preview(db, invoice_id)
        print("invoice_data",invoice_data)
        pdf_bytes = generate_invoice_pdf(invoice_data)

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=invoice_{invoice_id}.pdf"
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    


@router.get("/invoices/{invoice_id}/review")
def invoice_pdf(invoice_id: UUID, db: Session = Depends(get_db)):
    try:
        return get_invoice_preview(db, invoice_id)
      
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))