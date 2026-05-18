from fastapi import APIRouter
from pydantic import BaseModel, Field

from typing import Optional

from app.services.config_service import get_weights, set_weights, get_options, set_options


router = APIRouter(
    prefix="/api/config",
    tags=["config"],
)


class WeightsPayload(BaseModel):
    cf: int = Field(..., ge=0, le=100)
    cb: int = Field(..., ge=0, le=100)


class OptionsPayload(BaseModel):
    sentimentRerank: bool
    ragExplanation: bool


@router.get("/weights")
async def read_weights() -> dict:
    return {"weights": await get_weights()}


@router.get("/options")
async def read_options() -> dict:
    return {"options": await get_options()}


@router.post("/weights")
async def update_weights(payload: WeightsPayload) -> dict:
    total = payload.cf + payload.cb
    if total != 100 and total > 0:
        cf = round((payload.cf / total) * 100)
        cb = round((payload.cb / total) * 100)
    else:
        cf = payload.cf
        cb = payload.cb

    new = await set_weights(cf, cb)
    return {"weights": new}


@router.post("/options")
async def update_options(payload: OptionsPayload) -> dict:
    new = await set_options(payload.sentimentRerank, payload.ragExplanation)
    return {"options": new}
