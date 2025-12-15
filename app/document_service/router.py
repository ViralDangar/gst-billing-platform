from fastapi import APIRouter

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/health")
def documents_health():
    return {"service": "documents", "status": "ok"}
