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
    from database import get_db
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT share_price, insurance_rate FROM properties WHERE property_id=?", (req.property_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(404, "Property not found")
        
    share_price = row["share_price"]
    insurance_rate = row["insurance_rate"]
    
    logger.info(f"Buy {req.quantity} shares of property {req.property_id}")
    total_cost = req.quantity * share_price
    insurance = int(total_cost * (insurance_rate / 100))
    
    unsigned_txns = []
    from main import app_state
    import base64
    from algosdk import transaction, encoding
    from algosdk.logic import get_application_address

    error_msg = None
    client = app_state.get("algod_client")
    if client:
        try:
            sp = client.suggested_params()
            app_id = app_state["app_ids"].get("fractional_token", 0)
            receiver = get_application_address(app_id) if app_id else req.investor_address
            # Create a real payment transaction to show on testnet explorer
            txn = transaction.PaymentTxn(
                sender=req.investor_address,
                sp=sp,
                receiver=receiver,
                amt=total_cost + insurance,
                note=f"PropChain: Buy {req.quantity} shares of Prop {req.property_id}".encode()
            )
            
            # msgpack_encode returns a string (base64) so we need to encode it properly.
            # Actually, `encoding.msgpack_encode(txn)` is already a base64 string in algosdk! 
            # We don't need to wrap it in base64.b64encode
            encoded = encoding.msgpack_encode(txn)
            unsigned_txns.append(encoded)
        except Exception as e:
            logger.error(f"Failed to build txn: {e}")
            error_msg = str(e)
    else:
        error_msg = "Algod client not initialized"

    return {
        "property_id": req.property_id,
        "quantity": req.quantity,
        "share_price": share_price,
        "total_cost": total_cost,
        "insurance_premium": insurance,
        "total_payment": total_cost + insurance,
        "message": "Sign transaction with Pera Wallet to complete purchase",
        "unsigned_txns": unsigned_txns,
        "error": error_msg
    }


@router.get("/portfolio/{address}")
async def get_portfolio(address: str):
    """Get investor portfolio summary."""
    from database import get_db
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT h.*, p.property_name, p.share_price, p.total_shares 
        FROM holdings h 
        JOIN properties p ON h.property_id = p.property_id 
        WHERE h.investor_address=?
    ''', (address,))
    rows = c.fetchall()
    
    holdings = []
    total_value = 0
    total_claimable = 0
    
    for r in rows:
        val = r["shares"] * r["share_price"]
        total_value += val
        total_claimable += r["claimable_rent"]
        
        holdings.append({
            "property_id": r["property_id"],
            "name": r["property_name"],
            "shares": r["shares"],
            "percentage": (r["shares"] / r["total_shares"] * 100) if r["total_shares"] else 0,
            "current_value": val,
            "claimable_rent": r["claimable_rent"],
            "total_claimed": r["total_claimed"],
            "share_price": r["share_price"],
            "yield": 8.5 # mock yield initially
        })
        
    conn.close()
    
    return {
        "investor_address": address,
        "total_invested": total_value,
        "total_properties": len(holdings),
        "total_claimable": total_claimable,
        "holdings": holdings,
    }

@router.get("/holdings/{property_id}/{address}")
async def get_holdings(property_id: int, address: str):
    """Get investor's holdings for a specific property."""
    from database import get_db
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM holdings WHERE property_id=? AND investor_address=?", (property_id, address))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return {
            "property_id": property_id,
            "investor_address": address,
            "shares": 0,
            "percentage": 0.0,
            "current_value": 0,
        }
    return dict(row)

class RecordBuyRequest(BuySharesRequest):
    pass

@router.post("/record_buy")
async def record_buy(req: RecordBuyRequest):
    """Internal use: record a successful purchase after on-chain TX confirmation."""
    from database import get_db
    conn = get_db()
    c = conn.cursor()
    
    # Check if holding exists
    c.execute("SELECT id, shares FROM holdings WHERE property_id=? AND investor_address=?", (req.property_id, req.investor_address))
    row = c.fetchone()
    if row:
        c.execute("UPDATE holdings SET shares = shares + ? WHERE id=?", (req.quantity, row["id"]))
    else:
        c.execute("INSERT INTO holdings (property_id, investor_address, shares) VALUES (?, ?, ?)", 
                  (req.property_id, req.investor_address, req.quantity))
                  
    # Update property stats
    c.execute("UPDATE properties SET shares_sold = shares_sold + ? WHERE property_id=?", (req.quantity, req.property_id))
    
    conn.commit()
    conn.close()
    return {"success": True}
