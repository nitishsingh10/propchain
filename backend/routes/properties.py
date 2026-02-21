"""PropChain — Properties routes"""

import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Optional

from models import (
    PropertySubmitRequest, PropertyActivateRequest, SPVRegisterRequest,
    PropertyResponse, VerificationResponse, STATUS_LABELS,
)

router = APIRouter()
logger = logging.getLogger("propchain.routes.properties")


import json
from database import get_db

@router.get("/", response_model=list[dict])
async def list_properties(status: Optional[int] = None, limit: int = 50, offset: int = 0):
    """List all properties. Filter by status if provided."""
    # Read from DB
    conn = get_db()
    c = conn.cursor()
    if status is not None:
        c.execute("SELECT * FROM properties WHERE status=? LIMIT ? OFFSET ?", (status, limit, offset))
    else:
        c.execute("SELECT * FROM properties LIMIT ? OFFSET ?", (limit, offset))
    rows = c.fetchall()
    conn.close()
    
    # Parse rows back to dict
    res = []
    for r in rows:
        d = dict(r)
        if d.get("images"):
            try:
                d["images"] = json.loads(d["images"])
            except:
                d["images"] = []
        # Return dict mapping for PropertyResponse
        d["status_label"] = STATUS_LABELS.get(d.get("status", 0), "UNKNOWN")
        d["shares_available"] = d.get("total_shares", 0) - d.get("shares_sold", 0)
        res.append(d)
    return res


@router.get("/{property_id}", response_model=dict)
async def get_property(property_id: int):
    """Get a single property by ID."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM properties WHERE property_id=?", (property_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Property not found")
        
    d = dict(row)
    if d.get("images"):
        try:
            d["images"] = json.loads(d["images"])
        except:
            d["images"] = []
    
    d["status_label"] = STATUS_LABELS.get(d.get("status", 0), "UNKNOWN")
    d["shares_available"] = d.get("total_shares", 0) - d.get("shares_sold", 0)
    
    # AI Report mapping (mocked format)
    d["spv"] = {"cin": "U70100KA2023PTC18449" + str(property_id), "pan": "ABCDE1234F", "status": "PENDING" if d.get("status") == 0 else "ACTIVE"}
    d["documents"] = {"titleDeed": "✅ Verified", "taxRecords": "✅ Verified"}
    d["valuation"] = d.get("valuation", 0)
    d["sharePrice"] = d.get("share_price", 0)
    d["totalShares"] = d.get("total_shares", 0)
    d["sharesSold"] = d.get("shares_sold", 0)
    d["yield"] = d.get("yield_pct", 0.0)
    d["insuranceRate"] = d.get("insurance_rate", 1.5)
    d["minInvestment"] = d.get("min_investment", 1)
    d["maxInvestment"] = d.get("max_investment", 1000)
    d["aiScore"] = d.get("ai_score", 0)
    d["verificationStatus"] = d.get("verification_status", "PENDING")
    
    return d


@router.post("/submit")
async def submit_property(req: PropertySubmitRequest):
    """
    Submit a new property for listing.
    """
    logger.info(f"Property submission: {req.property_name}")
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO properties (owner_wallet, property_name, location_hash, valuation, total_shares, share_price, min_investment, max_investment, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (req.owner_address, req.property_name, req.location_hash, req.valuation, req.total_shares, req.share_price, req.min_investment, req.max_investment, 0))
    property_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "message": "Property submitted for verification",
        "property_id": property_id,
        "status": "PENDING_VERIFICATION",
        "next_step": "Upload documents for AI verification",
    }


@router.post("/{property_id}/verify", response_model=VerificationResponse)
async def verify_property(property_id: int, files: list[UploadFile] = File(...)):
    """
    Upload property documents for AI verification.
    Processes documents through OCR → Scorer → On-chain.
    """
    from main import app_state
    import tempfile, os

    oracle = app_state.get("oracle")
    if not oracle:
        raise HTTPException(503, "Oracle not initialized")

    # Save uploaded files to temp directory
    temp_dir = tempfile.mkdtemp(prefix="propchain_")
    file_paths = []
    for f in files:
        path = os.path.join(temp_dir, f.filename or "doc.pdf")
        with open(path, "wb") as out:
            content = await f.read()
            out.write(content)
        file_paths.append(path)

    # Run verification pipeline
    try:
        result = await oracle.verify_property(property_id, file_paths)
        return VerificationResponse(
            property_id=property_id,
            score=result.get("score", 0),
            verdict=result.get("verdict", "ERROR"),
            flags=result.get("flags", []),
            ipfs_cid=result.get("ipfs_cid"),
            txid=result.get("txid"),
            breakdown=result.get("breakdown"),
        )
    finally:
        # Cleanup temp files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


@router.post("/{property_id}/register-spv")
async def register_spv(property_id: int, req: SPVRegisterRequest):
    """Register SPV for a verified property."""
    from main import app_state
    oracle = app_state.get("oracle")
    if not oracle:
        raise HTTPException(503, "Oracle not initialized")

    result = await oracle.register_spv_on_chain(
        property_id, req.cin, req.pan, req.aoa_cid, req.cert_cid, req.deed_cid,
    )
    return result


@router.post("/{property_id}/activate")
async def activate_listing(property_id: int, req: PropertyActivateRequest):
    """Activate a property listing with security deposit."""
    return {
        "message": "Property listing activated",
        "property_id": property_id,
        "status": "ACTIVE",
        "deposit": req.security_deposit_amount,
    }
