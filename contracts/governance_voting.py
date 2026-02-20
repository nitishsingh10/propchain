"""
PropChain — GovernanceVoting Smart Contract
=============================================
Manages all on-chain governance decisions for PropChain properties.
The smart contract vote IS the legal board resolution for the SPV.

Token-weighted voting: each share = 1 vote.
Quorum threshold: 51% of total shares must vote YES.

Deployed on Algorand using Puya (algopy).
"""

import algopy
from algopy import (
    ARC4Contract,
    BoxMap,
    Global,
    Txn,
    UInt64,
    Bytes,
    arc4,
    log,
    op,
)


# ── Box Storage Structs ───────────────────────────────────────────────────

class ProposalRecord(arc4.Struct):
    """On-chain governance proposal."""
    property_id: arc4.UInt64
    proposer_address: arc4.Address
    proposal_type: arc4.UInt64          # 0=SELL, 1=RENOVATE, 2=CHANGE_RENT, 3=PENALIZE_OWNER
    description: arc4.String
    proposed_value: arc4.UInt64         # sale price / budget / new rent amount
    snapshot_block: arc4.UInt64         # block at which token balances snapshotted
    voting_deadline: arc4.UInt64        # timestamp
    yes_weight: arc4.UInt64             # total shares voted YES
    no_weight: arc4.UInt64              # total shares voted NO
    total_shares: arc4.UInt64           # total shares at snapshot
    quorum_threshold: arc4.UInt64       # 51
    status: arc4.UInt64                 # 0=ACTIVE, 1=PASSED, 2=FAILED, 3=EXECUTED
    authorized_action: arc4.String      # "SELL", "RENOVATE", etc.
    resolution_ipfs_cid: arc4.String    # IPFS CID of legal resolution PDF


class VoteRecord(arc4.Struct):
    """Individual vote record."""
    vote: arc4.UInt64                   # 1=YES, 0=NO
    vote_weight: arc4.UInt64            # shares held at snapshot
    voted_at: arc4.UInt64               # block timestamp


# ── Proposal Status Constants ─────────────────────────────────────────────

PROP_ACTIVE = UInt64(0)
PROP_PASSED = UInt64(1)
PROP_FAILED = UInt64(2)
PROP_EXECUTED = UInt64(3)

# Proposal Types
TYPE_SELL = UInt64(0)
TYPE_RENOVATE = UInt64(1)
TYPE_CHANGE_RENT = UInt64(2)
TYPE_PENALIZE = UInt64(3)

QUORUM = UInt64(51)

# Action strings
ACTION_SELL = "SELL"
ACTION_RENOVATE = "RENOVATE"
ACTION_CHANGE_RENT = "CHANGE_RENT"
ACTION_PENALIZE = "PENALIZE_OWNER"


class GovernanceVoting(ARC4Contract):
    """
    GovernanceVoting — token-weighted on-chain governance.

    Any shareholder with >= 1% stake can create proposals.
    All shareholders vote with weight proportional to their holdings.
    51% YES weight required to pass.
    """

    def __init__(self) -> None:
        self.property_registry_app_id = UInt64(0)
        self.fractional_token_app_id = UInt64(0)
        self.total_proposals = UInt64(0)
        self.oracle_address = Bytes(b"")
        # Box storage
        self.proposals = BoxMap(UInt64, ProposalRecord, key_prefix=b"gov_")
        # Vote records: proposal_id (8) + voter_address (32)
        self.votes = BoxMap(Bytes, VoteRecord, key_prefix=b"vot_")
        # Track latest authorized action per property
        self.authorized_actions = BoxMap(UInt64, arc4.UInt64, key_prefix=b"auth_")

    @arc4.abimethod(create="require")
    def create(
        self,
        property_registry_app_id: arc4.UInt64,
        fractional_token_app_id: arc4.UInt64,
        oracle_address: arc4.Address,
    ) -> None:
        """Initialize the GovernanceVoting contract."""
        self.property_registry_app_id = property_registry_app_id.native
        self.fractional_token_app_id = fractional_token_app_id.native
        self.oracle_address = oracle_address.bytes
        self.total_proposals = UInt64(0)
        log(b"GovernanceVoting created")

    @arc4.abimethod()
    def create_proposal(
        self,
        property_id: arc4.UInt64,
        proposal_type: arc4.UInt64,
        description: arc4.String,
        proposed_value: arc4.UInt64,
        voting_days: arc4.UInt64,
        proposer_shares: arc4.UInt64,
        total_shares: arc4.UInt64,
    ) -> arc4.UInt64:
        """
        Create a new governance proposal.
        Callable by any shareholder with >= 1% stake.

        The caller must pass their share count and total shares
        (verified off-chain by the backend before building the txn).
        """
        # Verify proposer holds >= 1% (100 basis points)
        percentage = proposer_shares.native * UInt64(10000) / total_shares.native
        assert percentage >= UInt64(100), "Need >= 1% stake to propose"

        # Validate proposal type
        ptype = proposal_type.native
        assert ptype <= TYPE_PENALIZE, "Invalid proposal type"

        # Generate proposal ID
        self.total_proposals += UInt64(1)
        proposal_id = self.total_proposals

        # Calculate voting deadline
        deadline = Global.latest_timestamp + (voting_days.native * UInt64(86400))

        # Determine action string
        action = arc4.String("")

        # Create proposal record
        proposal = ProposalRecord(
            property_id=property_id,
            proposer_address=arc4.Address(Txn.sender),
            proposal_type=proposal_type,
            description=description,
            proposed_value=proposed_value,
            snapshot_block=arc4.UInt64(Global.round),
            voting_deadline=arc4.UInt64(deadline),
            yes_weight=arc4.UInt64(0),
            no_weight=arc4.UInt64(0),
            total_shares=total_shares,
            quorum_threshold=arc4.UInt64(QUORUM),
            status=arc4.UInt64(PROP_ACTIVE),
            authorized_action=action,
            resolution_ipfs_cid=arc4.String(""),
        )
        self.proposals[proposal_id] = proposal

        log(b"ProposalCreated")
        return arc4.UInt64(proposal_id)

    @arc4.abimethod()
    def cast_vote(
        self,
        proposal_id: arc4.UInt64,
        vote_yes: arc4.Bool,
        voter_shares: arc4.UInt64,
    ) -> None:
        """
        Cast a vote on a proposal.
        Callable by any investor with shares at snapshot block.

        voter_shares: pre-verified by backend (shares held at snapshot_block).
        """
        pid = proposal_id.native
        assert pid in self.proposals, "Proposal not found"

        proposal = self.proposals[pid].copy()
        assert proposal.status.native == PROP_ACTIVE, "Proposal not active"
        assert Global.latest_timestamp <= proposal.voting_deadline.native, "Voting deadline passed"

        # Check voter hasn't voted already
        vote_key = op.itob(pid) + Txn.sender.bytes
        assert vote_key not in self.votes, "Already voted"

        # Record vote
        shares = voter_shares.native
        assert shares > UInt64(0), "Must hold shares to vote"

        vote_value = UInt64(1) if vote_yes.native else UInt64(0)

        vote_record = VoteRecord(
            vote=arc4.UInt64(vote_value),
            vote_weight=voter_shares,
            voted_at=arc4.UInt64(Global.latest_timestamp),
        )
        self.votes[vote_key] = vote_record

        # Update proposal tallies
        if vote_yes.native:
            new_yes = proposal.yes_weight.native + shares
            updated = ProposalRecord(
                property_id=proposal.property_id,
                proposer_address=proposal.proposer_address,
                proposal_type=proposal.proposal_type,
                description=proposal.description,
                proposed_value=proposal.proposed_value,
                snapshot_block=proposal.snapshot_block,
                voting_deadline=proposal.voting_deadline,
                yes_weight=arc4.UInt64(new_yes),
                no_weight=proposal.no_weight,
                total_shares=proposal.total_shares,
                quorum_threshold=proposal.quorum_threshold,
                status=proposal.status,
                authorized_action=proposal.authorized_action,
                resolution_ipfs_cid=proposal.resolution_ipfs_cid,
            )
        else:
            new_no = proposal.no_weight.native + shares
            updated = ProposalRecord(
                property_id=proposal.property_id,
                proposer_address=proposal.proposer_address,
                proposal_type=proposal.proposal_type,
                description=proposal.description,
                proposed_value=proposal.proposed_value,
                snapshot_block=proposal.snapshot_block,
                voting_deadline=proposal.voting_deadline,
                yes_weight=proposal.yes_weight,
                no_weight=arc4.UInt64(new_no),
                total_shares=proposal.total_shares,
                quorum_threshold=proposal.quorum_threshold,
                status=proposal.status,
                authorized_action=proposal.authorized_action,
                resolution_ipfs_cid=proposal.resolution_ipfs_cid,
            )

        self.proposals[pid] = updated

        log(b"VoteCast")

    @arc4.abimethod()
    def finalize_proposal(self, proposal_id: arc4.UInt64) -> None:
        """
        Finalize a proposal after voting deadline.
        Callable by anyone. Calculates result and sets status.

        Quorum: (yes_weight / total_shares) > 51%
        """
        pid = proposal_id.native
        assert pid in self.proposals, "Proposal not found"

        proposal = self.proposals[pid].copy()
        assert proposal.status.native == PROP_ACTIVE, "Already finalized"
        assert Global.latest_timestamp > proposal.voting_deadline.native, "Deadline not reached"

        # Calculate result: yes_weight * 100 / total_shares > 51
        yes_pct = proposal.yes_weight.native * UInt64(100) / proposal.total_shares.native
        passed = yes_pct > QUORUM

        # Determine action string based on proposal type
        ptype = proposal.proposal_type.native
        action_str = arc4.String("")
        if passed:
            if ptype == TYPE_SELL:
                action_str = arc4.String(ACTION_SELL)
            elif ptype == TYPE_RENOVATE:
                action_str = arc4.String(ACTION_RENOVATE)
            elif ptype == TYPE_CHANGE_RENT:
                action_str = arc4.String(ACTION_CHANGE_RENT)
            elif ptype == TYPE_PENALIZE:
                action_str = arc4.String(ACTION_PENALIZE)

        new_status = PROP_PASSED if passed else PROP_FAILED

        updated = ProposalRecord(
            property_id=proposal.property_id,
            proposer_address=proposal.proposer_address,
            proposal_type=proposal.proposal_type,
            description=proposal.description,
            proposed_value=proposal.proposed_value,
            snapshot_block=proposal.snapshot_block,
            voting_deadline=proposal.voting_deadline,
            yes_weight=proposal.yes_weight,
            no_weight=proposal.no_weight,
            total_shares=proposal.total_shares,
            quorum_threshold=proposal.quorum_threshold,
            status=arc4.UInt64(new_status),
            authorized_action=action_str,
            resolution_ipfs_cid=proposal.resolution_ipfs_cid,
        )
        self.proposals[pid] = updated

        # If passed SELL, store authorization for property
        if passed and ptype == TYPE_SELL:
            self.authorized_actions[proposal.property_id.native] = arc4.UInt64(pid)

        log(b"ProposalFinalized")

    @arc4.abimethod()
    def record_resolution_cid(
        self, proposal_id: arc4.UInt64, cid: arc4.String
    ) -> None:
        """
        Record the IPFS CID of the generated legal resolution PDF.
        Only callable by oracle.
        """
        assert Txn.sender.bytes == self.oracle_address, "Only oracle"
        pid = proposal_id.native
        assert pid in self.proposals, "Proposal not found"

        proposal = self.proposals[pid].copy()
        updated = ProposalRecord(
            property_id=proposal.property_id,
            proposer_address=proposal.proposer_address,
            proposal_type=proposal.proposal_type,
            description=proposal.description,
            proposed_value=proposal.proposed_value,
            snapshot_block=proposal.snapshot_block,
            voting_deadline=proposal.voting_deadline,
            yes_weight=proposal.yes_weight,
            no_weight=proposal.no_weight,
            total_shares=proposal.total_shares,
            quorum_threshold=proposal.quorum_threshold,
            status=proposal.status,
            authorized_action=proposal.authorized_action,
            resolution_ipfs_cid=cid,
        )
        self.proposals[pid] = updated

    @arc4.abimethod()
    def mark_executed(self, proposal_id: arc4.UInt64) -> None:
        """
        Mark a proposal as executed.
        Callable by SettlementEngine (for SELL) or oracle (for others).
        """
        pid = proposal_id.native
        assert pid in self.proposals, "Proposal not found"

        proposal = self.proposals[pid].copy()
        assert proposal.status.native == PROP_PASSED, "Must be PASSED to execute"

        updated = ProposalRecord(
            property_id=proposal.property_id,
            proposer_address=proposal.proposer_address,
            proposal_type=proposal.proposal_type,
            description=proposal.description,
            proposed_value=proposal.proposed_value,
            snapshot_block=proposal.snapshot_block,
            voting_deadline=proposal.voting_deadline,
            yes_weight=proposal.yes_weight,
            no_weight=proposal.no_weight,
            total_shares=proposal.total_shares,
            quorum_threshold=proposal.quorum_threshold,
            status=arc4.UInt64(PROP_EXECUTED),
            authorized_action=proposal.authorized_action,
            resolution_ipfs_cid=proposal.resolution_ipfs_cid,
        )
        self.proposals[pid] = updated

        log(b"ProposalExecuted")

    # ── Read-Only Methods ──────────────────────────────────────────────────

    @arc4.abimethod(readonly=True)
    def get_proposal(self, proposal_id: arc4.UInt64) -> ProposalRecord:
        """Read-only: returns full proposal details."""
        pid = proposal_id.native
        assert pid in self.proposals, "Proposal not found"
        return self.proposals[pid]

    @arc4.abimethod(readonly=True)
    def check_sell_authorized(self, property_id: arc4.UInt64) -> arc4.Bool:
        """
        Read-only: checks if a SELL action has been authorized for a property.
        Used by SettlementEngine before initiating settlement.
        """
        pid = property_id.native
        if pid not in self.authorized_actions:
            return arc4.Bool(False)

        # Get the proposal ID that authorized the action
        auth_proposal_id = self.authorized_actions[pid].native
        if auth_proposal_id not in self.proposals:
            return arc4.Bool(False)

        proposal = self.proposals[auth_proposal_id]
        return arc4.Bool(
            proposal.status.native == PROP_PASSED
            and proposal.proposal_type.native == TYPE_SELL
        )

    @arc4.abimethod(readonly=True)
    def get_authorized_sale_price(self, property_id: arc4.UInt64) -> arc4.UInt64:
        """Read-only: returns the approved sale price for a property."""
        pid = property_id.native
        assert pid in self.authorized_actions, "No authorized action"
        auth_proposal_id = self.authorized_actions[pid].native
        proposal = self.proposals[auth_proposal_id]
        return proposal.proposed_value

    @arc4.abimethod(readonly=True)
    def get_vote(
        self, proposal_id: arc4.UInt64, voter_address: arc4.Address
    ) -> VoteRecord:
        """Read-only: returns a specific vote record."""
        pid = proposal_id.native
        vote_key = op.itob(pid) + voter_address.bytes
        assert vote_key in self.votes, "Vote not found"
        return self.votes[vote_key]
