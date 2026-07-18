from fastapi import APIRouter, Depends, Query
from typing import List
from app.schemas.simulation import SimulationDayResponse, SimulationStateResponse, RunSimulationRequest
from app.services.simulation_service import SimulationService
from app.core.deps import get_current_user, require_role
from app.models.user import UserRole

router = APIRouter(prefix="/simulation", tags=["simulation"])


def serialize_day(day: dict) -> SimulationDayResponse:
    return SimulationDayResponse(
        id=str(day["_id"]),
        day_number=day["day_number"],
        weather=day["weather"],
        traffic_level=day["traffic_level"],
        is_festival=day["is_festival"],
        demand_multiplier=day["demand_multiplier"],
        orders_generated=day["orders_generated"],
        total_revenue=day["total_revenue"],
        supplier_delays=day["supplier_delays"],
        warehouse_failures=day["warehouse_failures"],
        random_events=day["random_events"],
        created_at=day["created_at"],
    )


def serialize_state(state: dict) -> SimulationStateResponse:
    return SimulationStateResponse(
        current_day=state["current_day"],
        is_running=state["is_running"],
        total_days_target=state.get("total_days_target"),
        started_at=state.get("started_at"),
        updated_at=state["updated_at"],
    )


@router.get("/state", response_model=SimulationStateResponse)
async def get_simulation_state(current_user: dict = Depends(get_current_user)):
    state = await SimulationService.get_state()
    return serialize_state(state)


@router.post("/run", response_model=List[SimulationDayResponse])
async def run_simulation(
    data: RunSimulationRequest,
    current_user: dict = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    days = await SimulationService.run_days(data.num_days)
    return [serialize_day(d) for d in days]


@router.post("/reset", response_model=SimulationStateResponse)
async def reset_simulation(
    current_user: dict = Depends(require_role(UserRole.ADMIN)),
):
    state = await SimulationService.reset_simulation()
    return serialize_state(state)


@router.get("/days/recent", response_model=List[SimulationDayResponse])
async def get_recent_days(
    limit: int = Query(30, le=365),
    current_user: dict = Depends(get_current_user),
):
    days = await SimulationService.get_recent_days(limit)
    return [serialize_day(d) for d in days]


@router.get("/days/{day_number}", response_model=SimulationDayResponse)
async def get_day(
    day_number: int,
    current_user: dict = Depends(get_current_user),
):
    day = await SimulationService.get_day(day_number)
    return serialize_day(day)