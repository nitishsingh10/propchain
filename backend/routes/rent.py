"""PropChain — Rent routes"""

import logging
from fastapi import APIRouter, HTTPException

from models import RentDepositRequest, RentClaimRequest, RentStatsResponse

router = APIRouter()
logger = logging.getLogger("propchain.routes.rent")


@router.post("/deposit")
async def deposit_rent(req: RentDepositRequest):
    """
    Owner deposits quarterly rent for a property.
    Returns unsigned transaction for owner to sign.
    """
    logger.info(f"Rent deposit: {req.amount} microALGO for property {req.property_id}")
    return {
        "property_id": req.property_id,
        "amount": req.amount,
        "message": "Sign transaction to deposit rent",
    }


@router.post("/claim")
async def claim_rent(req: RentClaimRequest):
    """
    Investor claims available rent for a property.
    Returns unsigned transaction for investor to sign.
    """
    logger.info(f"Rent claim: {req.investor_address} for property {req.property_id}")
    return {
        "property_id": req.property_id,
        "investor_address": req.investor_address,
        "claimable": 0,
        "message": "No rent available to claim",
    }


@router.get("/stats/{property_id}", response_model=RentStatsResponse)
async def rent_stats(property_id: int):
    """Get rent deposit statistics for a property."""
    return RentStatsResponse(
        total_deposited=0,
        deposit_count=0,
        missed_deposits=0,
        expected_next_deposit=0,
        next_deadline_human="N/A",
    )


@router.get("/history/{property_id}")
async def rent_history(property_id: int, limit: int = 20):
    """Get rent deposit and claim history for a property."""
    return {"property_id": property_id, "deposits": [], "claims": []}
