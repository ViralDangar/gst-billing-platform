from fastapi import FastAPI
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

from app.identity_service.router import router as identity_router
from app.master_data_service.router import product_router as product_router 
from app.master_data_service.router import customer_router as customer_router 
from app.billing_service.router import router as billing_router
from app.accounting_service.router import router as accounting_router
from app.document_service.router import router as documents_router
from app.tax_engine_service.router import router as tax_router

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}


# Register routers
app.include_router(identity_router)
app.include_router(product_router)
app.include_router(customer_router)
app.include_router(billing_router)
app.include_router(accounting_router)
app.include_router(documents_router)
app.include_router(tax_router)

