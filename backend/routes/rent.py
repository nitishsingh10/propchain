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
    from database import get_db
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT claimable_rent FROM holdings WHERE property_id=? AND investor_address=?", (req.property_id, req.investor_address))
    row = c.fetchone()
    conn.close()
    
    claimable = row["claimable_rent"] if row else 0
    if claimable == 0:
        raise HTTPException(400, "No rent available to claim")
        
    logger.info(f"Rent claim: {req.investor_address} for property {req.property_id}")
    
    unsigned_txns = []
    from main import app_state
    import base64
    from algosdk import transaction, encoding
    from algosdk.logic import get_application_address

    client = app_state.get("algod_client")
    if client:
        try:
            sp = client.suggested_params()
            app_id = app_state["app_ids"].get("rent_distributor", 0)
            receiver = get_application_address(app_id) if app_id else req.investor_address
            # Create a 0 ALGO payment to self with note, to show up on explorer
            txn = transaction.PaymentTxn(
                sender=req.investor_address,
                sp=sp,
                receiver=req.investor_address,
                amt=0,
                note=f"PropChain: Claim Rent for Prop {req.property_id}".encode()
            )
            encoded = encoding.msgpack_encode(txn)
            unsigned_txns.append(encoded)
        except Exception as e:
            logger.error(f"Failed to build txn: {e}")
            error_msg = str(e)
    else:
        error_msg = "Algod client not initialized"

    return {
        "property_id": req.property_id,
        "investor_address": req.investor_address,
        "claimable": claimable,
        "message": "Sign transaction to claim rent",
        "unsigned_txns": unsigned_txns,
        "error": error_msg
    }

@router.post("/record_claim")
async def record_claim(req: RentClaimRequest):
    """Internal use: record a successful rent claim."""
    from database import get_db
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        UPDATE holdings 
        SET total_claimed = total_claimed + claimable_rent, claimable_rent = 0 
        WHERE property_id=? AND investor_address=?
    ''', (req.property_id, req.investor_address))
    conn.commit()
    conn.close()
    return {"success": True}


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
