from fastapi import APIRouter

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/health")
def billing_health():
    return {"service": "billing", "status": "ok"}
