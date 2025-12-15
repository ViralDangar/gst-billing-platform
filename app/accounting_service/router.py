from fastapi import APIRouter

router = APIRouter(prefix="/accounting", tags=["Accounting"])


@router.get("/health")
def accounting_health():
    return {"service": "accounting", "status": "ok"}
