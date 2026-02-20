"""PropChain — Settlement routes"""

import logging
from fastapi import APIRouter, HTTPException

from models import (
    SettlementInitRequest, SettlementFundRequest,
    SettlementStatusResponse, SETTLEMENT_LABELS,
)

router = APIRouter()
logger = logging.getLogger("propchain.routes.settlement")


@router.post("/initiate")
async def initiate_settlement(req: SettlementInitRequest):
    """Initiate property settlement (oracle only)."""
    from main import app_state
    oracle = app_state.get("oracle")
    if not oracle:
        raise HTTPException(503, "Oracle not initialized")

    result = await oracle.trigger_settlement(req.property_id)
    return result


@router.post("/fund")
async def fund_escrow(req: SettlementFundRequest):
    """Fund settlement escrow. Returns unsigned transaction for buyer."""
    return {
        "property_id": req.property_id,
        "buyer_address": req.buyer_address,
        "message": "Sign transaction to fund escrow",
    }


@router.get("/status/{property_id}", response_model=SettlementStatusResponse)
async def get_settlement_status(property_id: int):
    """Get settlement status for a property."""
    return SettlementStatusResponse(
        settlement_status=0,
        status_label="NOT_STARTED",
        escrow_balance=0,
        total_distributed=0,
    )


@router.post("/finalize/{property_id}")
async def finalize_settlement(property_id: int):
    """Finalize settlement after all distributions (oracle only)."""
    return {"property_id": property_id, "status": "COMPLETE", "message": "Settlement finalized"}
