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


@router.get("/", response_model=list[PropertyResponse])
async def list_properties(status: Optional[int] = None, limit: int = 50, offset: int = 0):
    """List all properties. Filter by status if provided."""
    from main import app_state
    # In production: query indexer for PropertyRegistry app transactions
    # Mock response for demo
    return []


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: int):
    """Get a single property by ID."""
    from main import app_state
    # Read property box from PropertyRegistry
    raise HTTPException(404, "Property not found (contract not deployed)")


@router.post("/submit")
async def submit_property(req: PropertySubmitRequest):
    """
    Submit a new property for listing.
    Returns unsigned transaction for the owner to sign with Pera Wallet.
    """
    from main import app_state
    logger.info(f"Property submission: {req.property_name}")
    return {
        "message": "Property submitted for verification",
        "property_id": req.property_id or 1,
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
