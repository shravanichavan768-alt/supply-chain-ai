from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.warehouse import router as warehouse_router
from app.api.v1.supplier import router as supplier_router
from app.api.v1.order import router as order_router
from app.api.v1.truck import router as truck_router
from app.api.v1.delivery import router as delivery_router
from app.api.v1.simulation import router as simulation_router

app = FastAPI(title="Supply Chain AI Platform")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(warehouse_router, prefix="/api/v1")
app.include_router(supplier_router, prefix="/api/v1")
app.include_router(order_router, prefix="/api/v1")
app.include_router(truck_router, prefix="/api/v1")
app.include_router(delivery_router, prefix="/api/v1")
app.include_router(simulation_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}