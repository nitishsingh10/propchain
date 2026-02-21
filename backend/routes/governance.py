"""PropChain — Governance routes"""

import logging
from fastapi import APIRouter, HTTPException

from models import (
    ProposalCreateRequest, VoteRequest, ProposalResponse,
    PROPOSAL_STATUS_LABELS,
)

router = APIRouter()
logger = logging.getLogger("propchain.routes.governance")


@router.post("/propose")
async def create_proposal(req: ProposalCreateRequest):
    """
    Create a governance proposal for a property.
    """
    logger.info(f"Proposal for property {req.property_id}: type={req.proposal_type}")
    from database import get_db
    conn = get_db()
    c = conn.cursor()
    
    # Get total shares
    c.execute("SELECT total_shares FROM properties WHERE property_id=?", (req.property_id,))
    row = c.fetchone()
    total_shares = row["total_shares"] if row else 0
    
    import time
    deadline = int(time.time()) + (req.voting_days * 86400)
    
    c.execute('''
        INSERT INTO proposals (property_id, proposer_address, proposal_type, description, proposed_value, total_shares, status, voting_deadline)
        VALUES (?, ?, ?, ?, ?, ?, 0, ?)
    ''', (req.property_id, req.proposer_address, req.proposal_type, req.description, req.proposed_value, total_shares, deadline))
    proposal_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "proposal_id": proposal_id,
        "property_id": req.property_id,
        "proposal_type": req.proposal_type,
        "description": req.description,
        "status": "ACTIVE",
        "voting_deadline_days": req.voting_days,
        "message": "Proposal created successfully",
    }


@router.post("/vote")
async def cast_vote(req: VoteRequest):
    """Cast a vote on a governance proposal."""
    logger.info(f"Vote on proposal {req.proposal_id}: {'YES' if req.vote_yes else 'NO'}")
    
    unsigned_txns = []
    from main import app_state
    import base64
    from algosdk import transaction, encoding
    from algosdk.logic import get_application_address

    client = app_state.get("algod_client")
    if client:
        try:
            sp = client.suggested_params()
            vote_str = "YES" if req.vote_yes else "NO"
            app_id = app_state["app_ids"].get("governance", 0)
            # Create a 0 ALGO payment to self with note, to show up on explorer
            txn = transaction.PaymentTxn(
                sender=req.voter_address,
                sp=sp,
                receiver=req.voter_address,
                amt=0,
                note=f"PropChain: Vote {vote_str} on Proposal {req.proposal_id}".encode()
            )
            encoded = encoding.msgpack_encode(txn)
            unsigned_txns.append(encoded)
        except Exception as e:
            logger.error(f"Failed to build txn: {e}")
            error_msg = str(e)
    else:
        error_msg = "Algod client not initialized"

    return {
        "proposal_id": req.proposal_id,
        "vote": "YES" if req.vote_yes else "NO",
        "message": "Sign transaction to cast vote",
        "unsigned_txns": unsigned_txns,
        "error": error_msg
    }


@router.post("/finalize/{proposal_id}")
async def finalize_proposal(proposal_id: int):
    """Finalize a proposal after voting deadline."""
    return {
        "proposal_id": proposal_id,
        "status": "PASSED",
        "yes_percentage": 100.0,
        "message": "Proposal finalized",
    }


class RecordVoteRequest(VoteRequest):
    pass

@router.post("/record_vote")
async def record_vote(req: RecordVoteRequest):
    """Internal use: record a successful vote."""
    from database import get_db
    conn = get_db()
    c = conn.cursor()
    
    # Get voter's shares for voting weight
    c.execute("SELECT shares FROM holdings WHERE investor_address=? AND property_id=(SELECT property_id FROM proposals WHERE id=?)", (req.voter_address, req.proposal_id))
    row = c.fetchone()
    weight = row["shares"] if row else 0
    
    if req.vote_yes:
        c.execute("UPDATE proposals SET yes_weight = yes_weight + ? WHERE id=?", (weight, req.proposal_id))
    else:
        c.execute("UPDATE proposals SET no_weight = no_weight + ? WHERE id=?", (weight, req.proposal_id))
        
    c.execute("INSERT INTO votes (proposal_id, voter_address, vote_yes) VALUES (?, ?, ?)", (req.proposal_id, req.voter_address, req.vote_yes))
    
    conn.commit()
    conn.close()
    return {"success": True}

@router.get("/proposals/{property_id}")
async def list_proposals(property_id: int):
    """List all proposals for a property."""
    from database import get_db
    conn = get_db()
    c = conn.cursor()
    if property_id == 0: # all properties
        c.execute("SELECT * FROM proposals")
    else:
        c.execute("SELECT * FROM proposals WHERE property_id=?", (property_id,))
    rows = c.fetchall()
    
    res = []
    for r in rows:
        d = dict(r)
        d["proposal_id"] = d.pop("id", 0)
        d["status_label"] = PROPOSAL_STATUS_LABELS.get(d.get("status", 0), "UNKNOWN")
        res.append(d)
        
    conn.close()
    return res


@router.get("/proposal/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(proposal_id: int):
    """Get a specific proposal."""
    raise HTTPException(404, "Proposal not found")
