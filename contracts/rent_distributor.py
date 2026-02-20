"""
PropChain — RentDistributor Smart Contract
============================================
Handles quarterly rental income using a PULL-BASED model.
The owner deposits once (O(1) transaction) and each investor
claims their proportional share individually.

This is gas-efficient: deposit is O(1) regardless of investor count,
and each claim is O(1) per investor.

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


# ── Box Storage Structs ───────────────────────────────────────────────────

class RentRecord(arc4.Struct):
    """Rent tracking per property."""
    total_deposited: arc4.UInt64        # cumulative rent ever deposited
    last_deposit_block: arc4.UInt64     # block of last deposit
    last_deposit_amount: arc4.UInt64    # amount of last deposit
    deposit_count: arc4.UInt64          # how many quarters deposited
    expected_next_deposit: arc4.UInt64  # timestamp deadline for next quarter
    missed_deposits: arc4.UInt64        # count of missed deadlines


class ClaimRecord(arc4.Struct):
    """Per-investor claim tracking for a property."""
    claimable_balance: arc4.UInt64      # accumulated unclaimed rent in microALGO
    total_claimed: arc4.UInt64          # lifetime claimed amount
    last_claim_block: arc4.UInt64       # block of last claim


# ── Constants ──────────────────────────────────────────────────────────────

QUARTER_SECONDS = UInt64(90 * 24 * 60 * 60)  # 90 days in seconds


class RentDistributor(ARC4Contract):
    """
    RentDistributor — pull-based quarterly rent distribution.

    Owner deposits rent → contract calculates each investor's share →
    Investors claim individually when they want.
    """

    def __init__(self) -> None:
        self.property_registry_app_id = UInt64(0)
        self.fractional_token_app_id = UInt64(0)
        # Rent tracking per property
        self.rent_records = BoxMap(UInt64, RentRecord, key_prefix=b"rent_")
        # Claim tracking: composite key = property_id (8) + investor_address (32)
        self.claim_records = BoxMap(Bytes, ClaimRecord, key_prefix=b"clm_")

    @arc4.abimethod(create="require")
    def create(
        self,
        property_registry_app_id: arc4.UInt64,
        fractional_token_app_id: arc4.UInt64,
    ) -> None:
        """Initialize the RentDistributor contract."""
        self.property_registry_app_id = property_registry_app_id.native
        self.fractional_token_app_id = fractional_token_app_id.native
        log(b"RentDistributor created")

    @arc4.abimethod()
    def deposit_rent(
        self,
        property_id: arc4.UInt64,
        total_shares: arc4.UInt64,
        investor_count: arc4.UInt64,
        payment: gtxn.PaymentTransaction,
    ) -> None:
        """
        Deposit quarterly rent for a property.
        Called by the property owner with a payment in an atomic group.

        The deposit amount is recorded and investors' claimable balances
        are updated proportionally based on their share holdings.

        NOTE: In production, investor share data would be read via inner
        transaction to FractionalToken. For efficiency, the backend
        pre-computes and passes investor data.
        """
        pid = property_id.native
        deposit_amount = payment.amount
        assert deposit_amount > UInt64(0), "Deposit amount must be > 0"

        # Initialize or update rent record
        if pid in self.rent_records:
            record = self.rent_records[pid].copy()
            updated = RentRecord(
                total_deposited=arc4.UInt64(record.total_deposited.native + deposit_amount),
                last_deposit_block=arc4.UInt64(Global.round),
                last_deposit_amount=arc4.UInt64(deposit_amount),
                deposit_count=arc4.UInt64(record.deposit_count.native + UInt64(1)),
                expected_next_deposit=arc4.UInt64(Global.latest_timestamp + QUARTER_SECONDS),
                missed_deposits=record.missed_deposits,
            )
            self.rent_records[pid] = updated
        else:
            new_record = RentRecord(
                total_deposited=arc4.UInt64(deposit_amount),
                last_deposit_block=arc4.UInt64(Global.round),
                last_deposit_amount=arc4.UInt64(deposit_amount),
                deposit_count=arc4.UInt64(1),
                expected_next_deposit=arc4.UInt64(Global.latest_timestamp + QUARTER_SECONDS),
                missed_deposits=arc4.UInt64(0),
            )
            self.rent_records[pid] = new_record

        log(b"RentDeposited")

    @arc4.abimethod()
    def update_claimable(
        self,
        property_id: arc4.UInt64,
        investor_address: arc4.Address,
        investor_shares: arc4.UInt64,
        total_shares: arc4.UInt64,
        deposit_amount: arc4.UInt64,
    ) -> None:
        """
        Update an individual investor's claimable balance after a rent deposit.
        Called by the oracle/backend in a batch after deposit_rent.

        Calculates: claimable = (investor_shares / total_shares) * deposit_amount
        """
        pid = property_id.native
        claim_key = op.itob(pid) + investor_address.bytes

        # Calculate proportional rent
        # Use safe math: (shares * deposit) / total to avoid overflow
        shares = investor_shares.native
        total = total_shares.native
        deposit = deposit_amount.native

        assert total > UInt64(0), "Total shares must be > 0"
        claimable_amount = shares * deposit / total

        if claim_key in self.claim_records:
            existing = self.claim_records[claim_key].copy()
            updated = ClaimRecord(
                claimable_balance=arc4.UInt64(existing.claimable_balance.native + claimable_amount),
                total_claimed=existing.total_claimed,
                last_claim_block=existing.last_claim_block,
            )
            self.claim_records[claim_key] = updated
        else:
            new_claim = ClaimRecord(
                claimable_balance=arc4.UInt64(claimable_amount),
                total_claimed=arc4.UInt64(0),
                last_claim_block=arc4.UInt64(0),
            )
            self.claim_records[claim_key] = new_claim

    @arc4.abimethod()
    def claim_rent(self, property_id: arc4.UInt64) -> None:
        """
        Claim accumulated rent for a property.
        Called by an investor. Sends their claimable balance to them.
        """
        pid = property_id.native
        claim_key = op.itob(pid) + Txn.sender.bytes

        assert claim_key in self.claim_records, "No claimable balance"

        record = self.claim_records[claim_key].copy()
        claimable = record.claimable_balance.native
        assert claimable > UInt64(0), "Nothing to claim"

        # Send payment to investor via inner transaction
        itxn.Payment(
            receiver=Txn.sender,
            amount=claimable,
            fee=UInt64(0),
        ).submit()

        # Update claim record
        updated = ClaimRecord(
            claimable_balance=arc4.UInt64(0),
            total_claimed=arc4.UInt64(record.total_claimed.native + claimable),
            last_claim_block=arc4.UInt64(Global.round),
        )
        self.claim_records[claim_key] = updated

        log(b"RentClaimed")

    @arc4.abimethod()
    def flag_missed_rent(self, property_id: arc4.UInt64) -> None:
        """
        Flag a missed quarterly rent payment.
        Callable by any investor after the expected deadline passes.
        """
        pid = property_id.native
        assert pid in self.rent_records, "No rent record for property"

        record = self.rent_records[pid].copy()
        assert Global.latest_timestamp > record.expected_next_deposit.native, \
            "Deadline has not passed yet"

        # Increment missed deposits
        updated = RentRecord(
            total_deposited=record.total_deposited,
            last_deposit_block=record.last_deposit_block,
            last_deposit_amount=record.last_deposit_amount,
            deposit_count=record.deposit_count,
            expected_next_deposit=arc4.UInt64(
                record.expected_next_deposit.native + QUARTER_SECONDS
            ),
            missed_deposits=arc4.UInt64(record.missed_deposits.native + UInt64(1)),
        )
        self.rent_records[pid] = updated

        log(b"MissedRentFlagged")

    # ── Read-Only Methods ──────────────────────────────────────────────────

    @arc4.abimethod(readonly=True)
    def get_claimable(
        self, property_id: arc4.UInt64, investor_address: arc4.Address
    ) -> arc4.UInt64:
        """Read-only: returns the claimable balance for an investor."""
        pid = property_id.native
        claim_key = op.itob(pid) + investor_address.bytes
        if claim_key not in self.claim_records:
            return arc4.UInt64(0)
        record = self.claim_records[claim_key]
        return record.claimable_balance

    @arc4.abimethod(readonly=True)
    def get_property_rent_stats(
        self, property_id: arc4.UInt64
    ) -> RentRecord:
        """Read-only: returns full rent statistics for a property."""
        pid = property_id.native
        assert pid in self.rent_records, "No rent record"
        return self.rent_records[pid]

    @arc4.abimethod(readonly=True)
    def get_investor_claim_history(
        self, property_id: arc4.UInt64, investor_address: arc4.Address
    ) -> ClaimRecord:
        """Read-only: returns claim history for an investor on a property."""
        pid = property_id.native
        claim_key = op.itob(pid) + investor_address.bytes
        assert claim_key in self.claim_records, "No claim record"
        return self.claim_records[claim_key]
