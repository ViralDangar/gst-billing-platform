from fastapi import APIRouter

router = APIRouter(prefix="/masters", tags=["Master Data"])


@router.get("/health")
def masters_health():
    return {"service": "master-data", "status": "ok"}
