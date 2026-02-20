"""
PropChain — SettlementEngine Smart Contract
=============================================
Final contract in the property lifecycle. Executes property sales only
after governance approval and handles atomic distribution to all investors.

Flow: Governance SELL passes → Oracle initiates → Buyer funds escrow →
      Oracle distributes proceeds → Oracle finalizes settlement

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
    Account,
    arc4,
    gtxn,
    itxn,
    log,
    op,
)


# ── Box Storage Struct ─────────────────────────────────────────────────────

class SettlementRecord(arc4.Struct):
    """On-chain settlement state per property."""
    approved_sale_price: arc4.UInt64    # price from governance vote
    buyer_address: arc4.Address        # address that will pay
    escrow_balance: arc4.UInt64        # funds received from buyer
    settlement_status: arc4.UInt64     # 0-3 (see constants)
    settlement_block: arc4.UInt64      # block when settlement completed
    total_distributed: arc4.UInt64     # sanity check counter
    proposal_id: arc4.UInt64           # governance proposal that authorized this


# ── Settlement Status Constants ───────────────────────────────────────────

SETTLEMENT_NOT_STARTED = UInt64(0)
SETTLEMENT_ESCROW_FUNDED = UInt64(1)
SETTLEMENT_DISTRIBUTING = UInt64(2)
SETTLEMENT_COMPLETE = UInt64(3)

# Dust tolerance for rounding errors (10 microALGO)
DUST_TOLERANCE = UInt64(10)


class SettlementEngine(ARC4Contract):
    """
    SettlementEngine — executes property sales after governance approval.

    The settlement flow is:
    1. Oracle initiates settlement (verifies governance approval)
    2. Buyer funds escrow with exact sale price
    3. Oracle distributes proceeds to all investors proportionally
    4. Oracle finalizes: burns tokens, marks property SOLD, winds up SPV
    """

    def __init__(self) -> None:
        self.property_registry_app_id = UInt64(0)
        self.fractional_token_app_id = UInt64(0)
        self.governance_app_id = UInt64(0)
        self.spv_registry_app_id = UInt64(0)
        self.oracle_address = Bytes(b"")
        # Box storage
        self.settlements = BoxMap(UInt64, SettlementRecord, key_prefix=b"stl_")

    @arc4.abimethod(create="require")
    def create(
        self,
        property_registry_app_id: arc4.UInt64,
        fractional_token_app_id: arc4.UInt64,
        governance_app_id: arc4.UInt64,
        spv_registry_app_id: arc4.UInt64,
        oracle_address: arc4.Address,
    ) -> None:
        """Initialize the SettlementEngine with all cross-contract references."""
        self.property_registry_app_id = property_registry_app_id.native
        self.fractional_token_app_id = fractional_token_app_id.native
        self.governance_app_id = governance_app_id.native
        self.spv_registry_app_id = spv_registry_app_id.native
        self.oracle_address = oracle_address.bytes
        log(b"SettlementEngine created")

    @arc4.abimethod()
    def initiate_settlement(
        self,
        property_id: arc4.UInt64,
        approved_sale_price: arc4.UInt64,
        proposal_id: arc4.UInt64,
    ) -> None:
        """
        Initiate a settlement after governance approval.
        Only callable by oracle.

        In production, this would cross-call GovernanceVoting.check_sell_authorized()
        via inner transaction. The oracle verifies this off-chain before calling.
        """
        assert Txn.sender.bytes == self.oracle_address, "Only oracle"
        pid = property_id.native

        # Create settlement record
        record = SettlementRecord(
            approved_sale_price=approved_sale_price,
            buyer_address=arc4.Address(Global.zero_address),
            escrow_balance=arc4.UInt64(0),
            settlement_status=arc4.UInt64(SETTLEMENT_NOT_STARTED),
            settlement_block=arc4.UInt64(0),
            total_distributed=arc4.UInt64(0),
            proposal_id=proposal_id,
        )
        self.settlements[pid] = record

        log(b"SettlementInitiated")

    @arc4.abimethod()
    def fund_escrow(
        self,
        property_id: arc4.UInt64,
        payment: gtxn.PaymentTransaction,
    ) -> None:
        """
        Fund the escrow with the exact sale price.
        Called by the buyer with a payment in an atomic transaction group.
        """
        pid = property_id.native
        assert pid in self.settlements, "Settlement not found"

        settlement = self.settlements[pid].copy()
        assert settlement.settlement_status.native == SETTLEMENT_NOT_STARTED, \
            "Settlement already funded"

        # Verify payment matches approved sale price
        assert payment.amount == settlement.approved_sale_price.native, \
            "Payment must equal approved sale price"

        # Update settlement
        updated = SettlementRecord(
            approved_sale_price=settlement.approved_sale_price,
            buyer_address=arc4.Address(Txn.sender),
            escrow_balance=arc4.UInt64(payment.amount),
            settlement_status=arc4.UInt64(SETTLEMENT_ESCROW_FUNDED),
            settlement_block=settlement.settlement_block,
            total_distributed=settlement.total_distributed,
            proposal_id=settlement.proposal_id,
        )
        self.settlements[pid] = updated

        log(b"EscrowFunded")

    @arc4.abimethod()
    def distribute_proceeds(
        self,
        property_id: arc4.UInt64,
        investor_address: arc4.Address,
        investor_shares: arc4.UInt64,
        total_shares: arc4.UInt64,
    ) -> None:
        """
        Distribute proceeds to a single investor.
        Called by oracle in batches (one call per investor).

        Calculates: payout = (shares / total_shares) * approved_sale_price
        Sends payment to investor via inner transaction.
        """
        assert Txn.sender.bytes == self.oracle_address, "Only oracle"
        pid = property_id.native
        assert pid in self.settlements, "Settlement not found"

        settlement = self.settlements[pid].copy()
        status = settlement.settlement_status.native
        assert status == SETTLEMENT_ESCROW_FUNDED or status == SETTLEMENT_DISTRIBUTING, \
            "Invalid settlement status"

        # Calculate payout
        shares = investor_shares.native
        total = total_shares.native
        sale_price = settlement.approved_sale_price.native

        assert total > UInt64(0), "Total shares must be > 0"
        payout = shares * sale_price / total

        # Send payment to investor
        if payout > UInt64(0):
            itxn.Payment(
                receiver=Account(investor_address.bytes),
                amount=payout,
                fee=UInt64(0),
            ).submit()

        # Update settlement
        new_distributed = settlement.total_distributed.native + payout
        updated = SettlementRecord(
            approved_sale_price=settlement.approved_sale_price,
            buyer_address=settlement.buyer_address,
            escrow_balance=settlement.escrow_balance,
            settlement_status=arc4.UInt64(SETTLEMENT_DISTRIBUTING),
            settlement_block=settlement.settlement_block,
            total_distributed=arc4.UInt64(new_distributed),
            proposal_id=settlement.proposal_id,
        )
        self.settlements[pid] = updated

        log(b"ProceedDistributed")

    @arc4.abimethod()
    def finalize_settlement(self, property_id: arc4.UInt64) -> None:
        """
        Finalize the settlement after all investors are paid.
        Only callable by oracle.

        This triggers:
        - Token burn (via FractionalToken)
        - Property marked SOLD (via PropertyRegistry)
        - SPV wind-up (via SPVRegistry)
        - Governance proposal marked EXECUTED

        In production, these are done via inner transactions to each contract.
        """
        assert Txn.sender.bytes == self.oracle_address, "Only oracle"
        pid = property_id.native
        assert pid in self.settlements, "Settlement not found"

        settlement = self.settlements[pid].copy()
        assert settlement.settlement_status.native == SETTLEMENT_DISTRIBUTING, \
            "Must be DISTRIBUTING to finalize"

        # Verify total distributed approximately equals escrow (within dust tolerance)
        diff = UInt64(0)
        if settlement.total_distributed.native > settlement.escrow_balance.native:
            diff = settlement.total_distributed.native - settlement.escrow_balance.native
        else:
            diff = settlement.escrow_balance.native - settlement.total_distributed.native
        assert diff <= DUST_TOLERANCE, "Distribution amount mismatch"

        # Mark as complete
        updated = SettlementRecord(
            approved_sale_price=settlement.approved_sale_price,
            buyer_address=settlement.buyer_address,
            escrow_balance=settlement.escrow_balance,
            settlement_status=arc4.UInt64(SETTLEMENT_COMPLETE),
            settlement_block=arc4.UInt64(Global.round),
            total_distributed=settlement.total_distributed,
            proposal_id=settlement.proposal_id,
        )
        self.settlements[pid] = updated

        # In production: cross-contract inner transactions:
        # 1. FractionalToken.burn_all_shares(property_id)
        # 2. PropertyRegistry.mark_sold(property_id)
        # 3. SPVRegistry.wind_up_spv(property_id, windup_cid)
        # 4. GovernanceVoting.mark_executed(proposal_id)
        # These are orchestrated by the oracle calling each contract separately.

        log(b"SettlementComplete")

    @arc4.abimethod()
    def emergency_refund(self, property_id: arc4.UInt64) -> None:
        """
        Emergency refund of escrow to buyer.
        Only callable by oracle if something goes wrong pre-distribution.
        """
        assert Txn.sender.bytes == self.oracle_address, "Only oracle"
        pid = property_id.native
        assert pid in self.settlements, "Settlement not found"

        settlement = self.settlements[pid].copy()
        assert settlement.settlement_status.native == SETTLEMENT_ESCROW_FUNDED, \
            "Can only refund from ESCROW_FUNDED state"

        escrow = settlement.escrow_balance.native
        assert escrow > UInt64(0), "No escrow to refund"

        # Refund to buyer
        itxn.Payment(
            receiver=Account(settlement.buyer_address.bytes),
            amount=escrow,
            fee=UInt64(0),
        ).submit()

        # Reset settlement
        updated = SettlementRecord(
            approved_sale_price=settlement.approved_sale_price,
            buyer_address=settlement.buyer_address,
            escrow_balance=arc4.UInt64(0),
            settlement_status=arc4.UInt64(SETTLEMENT_NOT_STARTED),
            settlement_block=settlement.settlement_block,
            total_distributed=settlement.total_distributed,
            proposal_id=settlement.proposal_id,
        )
        self.settlements[pid] = updated

        log(b"EmergencyRefund")

    # ── Read-Only Methods ──────────────────────────────────────────────────

    @arc4.abimethod(readonly=True)
    def get_settlement_status(self, property_id: arc4.UInt64) -> arc4.UInt64:
        """Read-only: returns the current settlement status."""
        pid = property_id.native
        if pid not in self.settlements:
            return arc4.UInt64(SETTLEMENT_NOT_STARTED)
        return self.settlements[pid].settlement_status

    @arc4.abimethod(readonly=True)
    def get_settlement(self, property_id: arc4.UInt64) -> SettlementRecord:
        """Read-only: returns the full settlement record."""
        pid = property_id.native
        assert pid in self.settlements, "Settlement not found"
        return self.settlements[pid]
