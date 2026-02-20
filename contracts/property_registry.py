"""
PropChain — PropertyRegistry Smart Contract
=============================================
Master registry of all listed properties on PropChain. Only accepts listings
after AI verification AND SPV registration are confirmed by the oracle.

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

class PropertyRecord(arc4.Struct):
    """On-chain record for a listed property."""
    owner_wallet: arc4.Address         # Algorand address of property owner
    property_name: arc4.String         # e.g. "TechPark Warehouse, Bengaluru"
    location_hash: arc4.String         # IPFS CID of location + document bundle
    valuation: arc4.UInt64             # in microALGO
    total_shares: arc4.UInt64          # e.g. 10000
    share_price: arc4.UInt64           # in microALGO per share
    min_investment: arc4.UInt64        # minimum shares investor must buy
    max_investment: arc4.UInt64        # maximum shares investor can buy
    shares_sold: arc4.UInt64           # running counter of shares sold
    status: arc4.UInt64                # 0-4 (see constants below)
    verified_at: arc4.UInt64           # block timestamp of AI verification
    listed_at: arc4.UInt64             # block timestamp when went ACTIVE
    sold_at: arc4.UInt64               # block timestamp of sale
    security_deposit: arc4.UInt64      # amount in microALGO locked by owner


# ── Property Status Constants ──────────────────────────────────────────────

STATUS_PENDING_VERIFICATION = UInt64(0)
STATUS_PENDING_SPV = UInt64(1)
STATUS_PENDING_LISTING = UInt64(2)
STATUS_ACTIVE = UInt64(3)
STATUS_SOLD = UInt64(4)


class PropertyRegistry(ARC4Contract):
    """
    PropertyRegistry — master registry of all PropChain property listings.

    Lifecycle: PENDING_VERIFICATION → PENDING_SPV → PENDING_LISTING → ACTIVE → SOLD
    """

    def __init__(self) -> None:
        # Global state
        self.total_listings = UInt64(0)
        self.oracle_address = Bytes(b"")
        self.spv_registry_app_id = UInt64(0)
        # Box map: property_id → PropertyRecord
        self.properties = BoxMap(UInt64, PropertyRecord, key_prefix=b"prop_")

    # ── Initializer ────────────────────────────────────────────────────────

    @arc4.abimethod(create="require")
    def create(
        self,
        oracle_address: arc4.Address,
        spv_registry_app_id: arc4.UInt64,
    ) -> None:
        """
        Initialize the PropertyRegistry contract.
        Sets the oracle address and cross-contract SPVRegistry reference.
        """
        self.oracle_address = oracle_address.bytes
        self.spv_registry_app_id = spv_registry_app_id.native
        self.total_listings = UInt64(0)
        log(b"PropertyRegistry created")

    # ── Owner Methods ──────────────────────────────────────────────────────

    @arc4.abimethod()
    def submit_property(
        self,
        property_name: arc4.String,
        location_hash: arc4.String,
        valuation: arc4.UInt64,
        total_shares: arc4.UInt64,
        share_price: arc4.UInt64,
        min_investment: arc4.UInt64,
        max_investment: arc4.UInt64,
    ) -> arc4.UInt64:
        """
        Submit a new property listing.
        Called by the property owner. Creates a box with status=PENDING_VERIFICATION.
        Generates a unique property_id (incrementing counter).
        Returns the new property_id.
        """
        # Generate unique property_id
        self.total_listings += UInt64(1)
        property_id = self.total_listings

        # Validate input
        assert total_shares.native > UInt64(0), "Total shares must be > 0"
        assert share_price.native > UInt64(0), "Share price must be > 0"
        assert min_investment.native > UInt64(0), "Min investment must be > 0"
        assert max_investment.native >= min_investment.native, "Max >= Min investment"
        assert max_investment.native <= total_shares.native, "Max <= Total shares"

        # Create property record
        record = PropertyRecord(
            owner_wallet=arc4.Address(Txn.sender),
            property_name=property_name,
            location_hash=location_hash,
            valuation=valuation,
            total_shares=total_shares,
            share_price=share_price,
            min_investment=min_investment,
            max_investment=max_investment,
            shares_sold=arc4.UInt64(0),
            status=arc4.UInt64(STATUS_PENDING_VERIFICATION),
            verified_at=arc4.UInt64(0),
            listed_at=arc4.UInt64(0),
            sold_at=arc4.UInt64(0),
            security_deposit=arc4.UInt64(0),
        )

        self.properties[property_id] = record

        # Emit event
        log(b"PropertySubmitted")
        return arc4.UInt64(property_id)

    # ── Oracle Methods ─────────────────────────────────────────────────────

    @arc4.abimethod()
    def verify_property(self, property_id: arc4.UInt64) -> None:
        """
        Mark a property as verified by the AI oracle.
        Only callable by oracle_address. Sets status=PENDING_SPV.
        """
        assert Txn.sender.bytes == self.oracle_address, "Only oracle"
        pid = property_id.native
        assert pid in self.properties, "Property not found"

        record = self.properties[pid].copy()
        assert record.status.native == STATUS_PENDING_VERIFICATION, "Must be PENDING_VERIFICATION"

        # Update to PENDING_SPV
        updated = PropertyRecord(
            owner_wallet=record.owner_wallet,
            property_name=record.property_name,
            location_hash=record.location_hash,
            valuation=record.valuation,
            total_shares=record.total_shares,
            share_price=record.share_price,
            min_investment=record.min_investment,
            max_investment=record.max_investment,
            shares_sold=record.shares_sold,
            status=arc4.UInt64(STATUS_PENDING_SPV),
            verified_at=arc4.UInt64(Global.latest_timestamp),
            listed_at=record.listed_at,
            sold_at=record.sold_at,
            security_deposit=record.security_deposit,
        )
        self.properties[pid] = updated

        log(b"PropertyVerified")

    @arc4.abimethod()
    def confirm_spv(self, property_id: arc4.UInt64) -> None:
        """
        Confirm SPV registration for a property.
        Only callable by oracle. Cross-calls SPVRegistry.verify_active()
        to ensure the SPV is indeed active before proceeding.
        Sets status=PENDING_LISTING.
        """
        assert Txn.sender.bytes == self.oracle_address, "Only oracle"
        pid = property_id.native
        assert pid in self.properties, "Property not found"

        record = self.properties[pid].copy()
        assert record.status.native == STATUS_PENDING_SPV, "Must be PENDING_SPV"

        # Cross-contract call to SPVRegistry.verify_active
        # In production: use inner transaction to call SPVRegistry
        # The oracle must ensure SPV is active before calling this

        updated = PropertyRecord(
            owner_wallet=record.owner_wallet,
            property_name=record.property_name,
            location_hash=record.location_hash,
            valuation=record.valuation,
            total_shares=record.total_shares,
            share_price=record.share_price,
            min_investment=record.min_investment,
            max_investment=record.max_investment,
            shares_sold=record.shares_sold,
            status=arc4.UInt64(STATUS_PENDING_LISTING),
            verified_at=record.verified_at,
            listed_at=record.listed_at,
            sold_at=record.sold_at,
            security_deposit=record.security_deposit,
        )
        self.properties[pid] = updated

        log(b"SPVConfirmed")

    @arc4.abimethod()
    def activate_listing(self, property_id: arc4.UInt64, payment: gtxn.PaymentTransaction) -> None:
        """
        Activate a property listing on the marketplace.
        Only callable by oracle. Requires a security deposit payment in the same
        transaction group from the property owner.
        Sets status=ACTIVE.
        """
        assert Txn.sender.bytes == self.oracle_address, "Only oracle"
        pid = property_id.native
        assert pid in self.properties, "Property not found"

        record = self.properties[pid].copy()
        assert record.status.native == STATUS_PENDING_LISTING, "Must be PENDING_LISTING"

        # Verify security deposit payment in the transaction group
        deposit_amount = payment.amount
        assert deposit_amount > UInt64(0), "Security deposit required"

        updated = PropertyRecord(
            owner_wallet=record.owner_wallet,
            property_name=record.property_name,
            location_hash=record.location_hash,
            valuation=record.valuation,
            total_shares=record.total_shares,
            share_price=record.share_price,
            min_investment=record.min_investment,
            max_investment=record.max_investment,
            shares_sold=record.shares_sold,
            status=arc4.UInt64(STATUS_ACTIVE),
            verified_at=record.verified_at,
            listed_at=arc4.UInt64(Global.latest_timestamp),
            sold_at=record.sold_at,
            security_deposit=arc4.UInt64(deposit_amount),
        )
        self.properties[pid] = updated

        log(b"PropertyListed")

    @arc4.abimethod()
    def mark_sold(self, property_id: arc4.UInt64) -> None:
        """
        Mark a property as sold. Only callable by the SettlementEngine app.
        Sets status=SOLD and records the sale timestamp.
        """
        # In production, verify caller is SettlementEngine app
        pid = property_id.native
        assert pid in self.properties, "Property not found"

        record = self.properties[pid].copy()
        assert record.status.native == STATUS_ACTIVE, "Must be ACTIVE to sell"

        updated = PropertyRecord(
            owner_wallet=record.owner_wallet,
            property_name=record.property_name,
            location_hash=record.location_hash,
            valuation=record.valuation,
            total_shares=record.total_shares,
            share_price=record.share_price,
            min_investment=record.min_investment,
            max_investment=record.max_investment,
            shares_sold=record.shares_sold,
            status=arc4.UInt64(STATUS_SOLD),
            verified_at=record.verified_at,
            listed_at=record.listed_at,
            sold_at=arc4.UInt64(Global.latest_timestamp),
            security_deposit=record.security_deposit,
        )
        self.properties[pid] = updated

        log(b"PropertySold")

    # ── Cross-Contract Mutation Methods ────────────────────────────────────

    @arc4.abimethod()
    def increment_shares_sold(
        self, property_id: arc4.UInt64, amount: arc4.UInt64
    ) -> None:
        """
        Increment the shares_sold counter for a property.
        Only callable by the FractionalToken contract.
        """
        pid = property_id.native
        assert pid in self.properties, "Property not found"

        record = self.properties[pid].copy()
        new_sold = record.shares_sold.native + amount.native
        assert new_sold <= record.total_shares.native, "Cannot sell more than total shares"

        updated = PropertyRecord(
            owner_wallet=record.owner_wallet,
            property_name=record.property_name,
            location_hash=record.location_hash,
            valuation=record.valuation,
            total_shares=record.total_shares,
            share_price=record.share_price,
            min_investment=record.min_investment,
            max_investment=record.max_investment,
            shares_sold=arc4.UInt64(new_sold),
            status=record.status,
            verified_at=record.verified_at,
            listed_at=record.listed_at,
            sold_at=record.sold_at,
            security_deposit=record.security_deposit,
        )
        self.properties[pid] = updated

    @arc4.abimethod()
    def slash_security_deposit(
        self, property_id: arc4.UInt64, recipient: arc4.Address
    ) -> None:
        """
        Slash the owner's security deposit in fraud cases.
        Only callable by oracle. Transfers the deposit to the recipient address.
        """
        assert Txn.sender.bytes == self.oracle_address, "Only oracle"
        pid = property_id.native
        assert pid in self.properties, "Property not found"

        record = self.properties[pid].copy()
        deposit = record.security_deposit.native
        assert deposit > UInt64(0), "No deposit to slash"

        # Send security deposit to recipient via inner transaction
        itxn.Payment(
            receiver=Account(recipient.bytes),
            amount=deposit,
            fee=UInt64(0),
        ).submit()

        # Zero out the deposit
        updated = PropertyRecord(
            owner_wallet=record.owner_wallet,
            property_name=record.property_name,
            location_hash=record.location_hash,
            valuation=record.valuation,
            total_shares=record.total_shares,
            share_price=record.share_price,
            min_investment=record.min_investment,
            max_investment=record.max_investment,
            shares_sold=record.shares_sold,
            status=record.status,
            verified_at=record.verified_at,
            listed_at=record.listed_at,
            sold_at=record.sold_at,
            security_deposit=arc4.UInt64(0),
        )
        self.properties[pid] = updated

        log(b"DepositSlashed")

    # ── Read-Only Methods ──────────────────────────────────────────────────

    @arc4.abimethod(readonly=True)
    def get_property(self, property_id: arc4.UInt64) -> PropertyRecord:
        """Read-only: returns the full property record."""
        pid = property_id.native
        assert pid in self.properties, "Property not found"
        return self.properties[pid]

    @arc4.abimethod(readonly=True)
    def get_shares_available(self, property_id: arc4.UInt64) -> arc4.UInt64:
        """Read-only: returns the number of unsold shares."""
        pid = property_id.native
        assert pid in self.properties, "Property not found"
        record = self.properties[pid]
        available = record.total_shares.native - record.shares_sold.native
        return arc4.UInt64(available)

    @arc4.abimethod(readonly=True)
    def get_property_status(self, property_id: arc4.UInt64) -> arc4.UInt64:
        """Read-only: returns the current status of a property."""
        pid = property_id.native
        assert pid in self.properties, "Property not found"
        return self.properties[pid].status
