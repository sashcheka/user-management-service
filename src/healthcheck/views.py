from fastapi import APIRouter

router = APIRouter(tags=["Healthcheck"])


@router.get("/healthcheck/")
async def health_check():
    return {"status": "OK"}
