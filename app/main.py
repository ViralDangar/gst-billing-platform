from fastapi import FastAPI
from app.core.config import settings

from app.identity_service.router import router as identity_router
from app.master_data_service.router import router as masters_router
from app.billing_service.router import router as billing_router
from app.accounting_service.router import router as accounting_router
from app.document_service.router import router as documents_router

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}


# Register routers
app.include_router(identity_router)
app.include_router(masters_router)
app.include_router(billing_router)
app.include_router(accounting_router)
app.include_router(documents_router)
