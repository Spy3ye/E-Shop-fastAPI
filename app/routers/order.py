from fastapi import APIRouter, Depends
from odmantic import AIOEngine
from schemas.order import OrderOut
from services.order_services import place_order

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/place", response_model=OrderOut)
async def create_order(user_id: str, engine: AIOEngine = Depends()):
    return await place_order(engine, user_id)
