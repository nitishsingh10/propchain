"""PropChain — Pydantic Models for request/response bodies."""

from typing import Optional
from pydantic import BaseModel


# ── Properties ─────────────────────────────────────────────────────────────

class PropertySubmitRequest(BaseModel):
    property_id: Optional[int] = None
    owner_address: str
    property_name: str
    location_hash: str
    valuation: int
    total_shares: int
    share_price: int
    min_investment: int
    max_investment: int

class PropertyActivateRequest(BaseModel):
    property_id: int
    security_deposit_amount: int

class SPVRegisterRequest(BaseModel):
    property_id: int
    cin: str
    pan: str
    aoa_cid: str
    cert_cid: str
    deed_cid: str

class PropertyResponse(BaseModel):
    property_id: int
    owner_wallet: str
    property_name: str
    location_hash: str
    valuation: int
    total_shares: int
    share_price: int
    shares_sold: int
    shares_available: int
    status: int
    status_label: str
    verified_at: int = 0
    listed_at: int = 0

class VerificationResponse(BaseModel):
    property_id: Optional[int] = None
    score: int
    verdict: str
    flags: list[str]
    ipfs_cid: Optional[str] = None
    txid: Optional[str] = None
    breakdown: Optional[dict] = None


# ── Investments ────────────────────────────────────────────────────────────

class BuySharesRequest(BaseModel):
    property_id: int
    investor_address: str
    quantity: int

class InvestorHolding(BaseModel):
    property_id: int
    property_name: str
    shares: int
    percentage: float
    current_value: int
    claimable_rent: int

class PortfolioResponse(BaseModel):
    investor_address: str
    total_invested: int
    total_properties: int
    total_claimable: int
    holdings: list[InvestorHolding]


# ── Rent ──────────────────────────────────────────────────────────────────

class RentDepositRequest(BaseModel):
    property_id: int
    owner_address: str
    amount: int

class RentClaimRequest(BaseModel):
    property_id: int
    investor_address: str

class RentStatsResponse(BaseModel):
    total_deposited: int
    deposit_count: int
    missed_deposits: int
    expected_next_deposit: int
    next_deadline_human: str


# ── Governance ─────────────────────────────────────────────────────────────

class ProposalCreateRequest(BaseModel):
    property_id: int
    proposer_address: str
    proposal_type: int  # 0=SELL, 1=RENOVATE, 2=CHANGE_RENT, 3=PENALIZE
    description: str
    proposed_value: int
    voting_days: int = 7

class VoteRequest(BaseModel):
    proposal_id: int
    voter_address: str
    vote_yes: bool

class ProposalResponse(BaseModel):
    proposal_id: int
    property_id: int
    proposal_type: int
    description: str
    proposed_value: int
    yes_weight: int
    no_weight: int
    total_shares: int
    status: int
    status_label: str
    voting_deadline: int


# ── Settlement ─────────────────────────────────────────────────────────────

class SettlementInitRequest(BaseModel):
    property_id: int

class SettlementFundRequest(BaseModel):
    property_id: int
    buyer_address: str

class SettlementStatusResponse(BaseModel):
    settlement_status: int
    status_label: str
    escrow_balance: int
    total_distributed: int
    buyer_address: Optional[str] = None


# ── Common ─────────────────────────────────────────────────────────────────

class UnsignedTxnResponse(BaseModel):
    unsigned_txn: Optional[str] = None
    unsigned_txns: Optional[list[str]] = None

class TxResponse(BaseModel):
    success: bool
    txid: Optional[str] = None
    message: Optional[str] = None

STATUS_LABELS = {
    0: "PENDING_VERIFICATION", 1: "PENDING_SPV", 2: "PENDING_LISTING",
    3: "ACTIVE", 4: "SOLD",
}
SETTLEMENT_LABELS = {
    0: "NOT_STARTED", 1: "ESCROW_FUNDED", 2: "DISTRIBUTING", 3: "COMPLETE",
}
PROPOSAL_STATUS_LABELS = {0: "ACTIVE", 1: "PASSED", 2: "FAILED", 3: "EXECUTED"}
