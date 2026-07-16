from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.warehouse import router as warehouse_router

app = FastAPI(title="Supply Chain AI Platform")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(warehouse_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}