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
    Only shareholders can create proposals.
    """
    logger.info(f"Proposal for property {req.property_id}: type={req.proposal_type}")
    return {
        "proposal_id": 1,
        "property_id": req.property_id,
        "proposal_type": req.proposal_type,
        "description": req.description,
        "status": "ACTIVE",
        "voting_deadline_days": req.voting_days,
        "message": "Sign transaction to create proposal",
    }


@router.post("/vote")
async def cast_vote(req: VoteRequest):
    """Cast a vote on a governance proposal."""
    logger.info(f"Vote on proposal {req.proposal_id}: {'YES' if req.vote_yes else 'NO'}")
    return {
        "proposal_id": req.proposal_id,
        "vote": "YES" if req.vote_yes else "NO",
        "message": "Sign transaction to cast vote",
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


@router.get("/proposals/{property_id}", response_model=list[ProposalResponse])
async def list_proposals(property_id: int):
    """List all proposals for a property."""
    return []


@router.get("/proposal/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(proposal_id: int):
    """Get a specific proposal."""
    raise HTTPException(404, "Proposal not found")
