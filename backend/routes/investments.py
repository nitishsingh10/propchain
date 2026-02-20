"""PropChain — Investments routes"""

import logging
from fastapi import APIRouter, HTTPException

from models import BuySharesRequest, PortfolioResponse, InvestorHolding

router = APIRouter()
logger = logging.getLogger("propchain.routes.investments")


@router.post("/buy")
async def buy_shares(req: BuySharesRequest):
    """
    Purchase fractional shares of a property.
    Returns unsigned transaction for investor to sign with Pera Wallet.
    """
    logger.info(f"Buy {req.quantity} shares of property {req.property_id}")
    share_price = 5_000_000  # Would be read from contract
    insurance_rate = 0.015
    total_cost = req.quantity * share_price
    insurance = int(total_cost * insurance_rate)

    return {
        "property_id": req.property_id,
        "quantity": req.quantity,
        "share_price": share_price,
        "total_cost": total_cost,
        "insurance_premium": insurance,
        "total_payment": total_cost + insurance,
        "message": "Sign transaction with Pera Wallet to complete purchase",
    }


@router.get("/portfolio/{address}", response_model=PortfolioResponse)
async def get_portfolio(address: str):
    """Get investor portfolio summary."""
    # In production: query FractionalToken, RentDistributor contracts
    return PortfolioResponse(
        investor_address=address,
        total_invested=0,
        total_properties=0,
        total_claimable=0,
        holdings=[],
    )


@router.get("/holdings/{property_id}/{address}")
async def get_holdings(property_id: int, address: str):
    """Get investor's holdings for a specific property."""
    return {
        "property_id": property_id,
        "investor_address": address,
        "shares": 0,
        "percentage": 0.0,
        "current_value": 0,
    }
