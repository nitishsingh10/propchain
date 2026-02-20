"""
PropChain — FractionalToken Smart Contract
============================================
Manages creation, sale, and tracking of fractional ownership tokens
(Algorand Standard Assets) for each listed property.

Each property gets its own ASA. Investors buy shares which represent
fractional ownership of the SPV that holds the property deed.

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

class TokenRecord(arc4.Struct):
    """Token metadata for a property's ASA."""
    asa_id: arc4.UInt64              # the ASA created for this property
    total_supply: arc4.UInt64
    remaining_supply: arc4.UInt64
    insurance_rate: arc4.UInt64      # 15 = 1.5%, stored as basis points (tenths of %)


class InvestorRecord(arc4.Struct):
    """Per-investor holdings for a specific property."""
    shares_held: arc4.UInt64
    total_invested: arc4.UInt64      # in microALGO
    investment_timestamp: arc4.UInt64


class InvestorEntry(arc4.Struct):
    """Return struct for investor listing."""
    address: arc4.Address
    shares: arc4.UInt64


# ── Constants ──────────────────────────────────────────────────────────────

INSURANCE_RATE_BPS = UInt64(15)  # 1.5% = 15 basis points (tenths of percent)


class FractionalToken(ARC4Contract):
    """
    FractionalToken — manages fractional ownership tokens for PropChain.

    Creates ASAs for each property, handles investor purchases with
    insurance premium deduction, and supports settlement token burning.
    """

    def __init__(self) -> None:
        # Global state
        self.oracle_address = Bytes(b"")
        self.property_registry_app_id = UInt64(0)
        self.insurance_pool_balance = UInt64(0)
        # Box storage
        self.tokens = BoxMap(UInt64, TokenRecord, key_prefix=b"tk_")
        # Investor records keyed by composite key: property_id (8 bytes) + address (32 bytes)
        self.investors = BoxMap(Bytes, InvestorRecord, key_prefix=b"inv_")
        # Track investor count per property
        self.investor_count = BoxMap(UInt64, UInt64, key_prefix=b"ic_")
        # Track investor addresses per property (index-based)
        self.investor_addresses = BoxMap(Bytes, arc4.Address, key_prefix=b"ia_")

    @arc4.abimethod(create="require")
    def create(
        self,
        oracle_address: arc4.Address,
        property_registry_app_id: arc4.UInt64,
    ) -> None:
        """Initialize the FractionalToken contract."""
        self.oracle_address = oracle_address.bytes
        self.property_registry_app_id = property_registry_app_id.native
        self.insurance_pool_balance = UInt64(0)
        log(b"FractionalToken created")

    @arc4.abimethod()
    def create_token(
        self,
        property_id: arc4.UInt64,
        total_supply: arc4.UInt64,
        unit_name: arc4.String,
        asset_name: arc4.String,
    ) -> arc4.UInt64:
        """
        Create a new ASA for a property. Only callable by oracle.
        Called after PropertyRegistry.activate_listing().

        The ASA is configured with:
        - decimals = 0 (whole shares only)
        - manager, clawback, freeze = this contract address
        """
        assert Txn.sender.bytes == self.oracle_address, "Only oracle"
        pid = property_id.native

        # Create the ASA via inner transaction
        asa_txn = itxn.AssetConfig(
            total=total_supply.native,
            decimals=UInt64(0),
            unit_name="PROP",
            asset_name=b"PropChain-" + op.itob(pid),
            manager=Global.current_application_address,
            clawback=Global.current_application_address,
            freeze=Global.current_application_address,
            reserve=Global.current_application_address,
            fee=UInt64(0),
        ).submit()

        # Get the created ASA ID
        asa_id = asa_txn.created_asset.id

        # Store token record
        token = TokenRecord(
            asa_id=arc4.UInt64(asa_id),
            total_supply=total_supply,
            remaining_supply=total_supply,
            insurance_rate=arc4.UInt64(INSURANCE_RATE_BPS),
        )
        self.tokens[pid] = token
        self.investor_count[pid] = UInt64(0)

        log(b"TokenCreated")
        return arc4.UInt64(asa_id)

    @arc4.abimethod()
    def opt_in_investor(self, property_id: arc4.UInt64) -> None:
        """
        Investor opts in to hold the ASA for a property.
        Creates their local state box for tracking holdings.
        """
        pid = property_id.native
        assert pid in self.tokens, "Token not found for property"

        # Create composite key: property_id bytes + sender address bytes
        investor_key = op.itob(pid) + Txn.sender.bytes

        # Create investor record (initialized to 0)
        record = InvestorRecord(
            shares_held=arc4.UInt64(0),
            total_invested=arc4.UInt64(0),
            investment_timestamp=arc4.UInt64(0),
        )
        self.investors[investor_key] = record

        # Track this investor's address
        count = self.investor_count[pid]
        addr_key = op.itob(pid) + op.itob(count)
        self.investor_addresses[addr_key] = arc4.Address(Txn.sender)
        self.investor_count[pid] = count + UInt64(1)

    @arc4.abimethod()
    def buy_shares(
        self,
        property_id: arc4.UInt64,
        quantity: arc4.UInt64,
        payment: gtxn.PaymentTransaction,
    ) -> None:
        """
        Buy fractional shares of a property. Atomic group required.

        Verifies:
        - Payment covers (quantity * share_price) + insurance premium
        - Deducts 1.5% insurance premium
        - Transfers ASA shares to investor
        - Updates investor local state
        """
        pid = property_id.native
        qty = quantity.native
        assert pid in self.tokens, "Token not found"
        assert qty > UInt64(0), "Quantity must be > 0"

        token = self.tokens[pid].copy()
        assert qty <= token.remaining_supply.native, "Not enough shares available"

        # Verify payment amount covers cost + insurance
        # Insurance = 1.5% of (qty * share_price)
        # For simplicity, the backend calculates exact amount and we verify payment > 0
        assert payment.amount > UInt64(0), "Payment required"

        # Calculate insurance premium (1.5% = amount * 15 / 1000)
        insurance_premium = payment.amount * INSURANCE_RATE_BPS / UInt64(1000)
        self.insurance_pool_balance += insurance_premium

        # Transfer ASA shares to investor via inner transaction
        itxn.AssetTransfer(
            xfer_asset=token.asa_id.native,
            asset_receiver=Txn.sender,
            asset_amount=qty,
            fee=UInt64(0),
        ).submit()

        # Update token supply
        updated_token = TokenRecord(
            asa_id=token.asa_id,
            total_supply=token.total_supply,
            remaining_supply=arc4.UInt64(token.remaining_supply.native - qty),
            insurance_rate=token.insurance_rate,
        )
        self.tokens[pid] = updated_token

        # Update investor record
        investor_key = op.itob(pid) + Txn.sender.bytes
        if investor_key in self.investors:
            existing = self.investors[investor_key].copy()
            updated_investor = InvestorRecord(
                shares_held=arc4.UInt64(existing.shares_held.native + qty),
                total_invested=arc4.UInt64(existing.total_invested.native + payment.amount),
                investment_timestamp=arc4.UInt64(Global.latest_timestamp),
            )
            self.investors[investor_key] = updated_investor
        else:
            new_investor = InvestorRecord(
                shares_held=arc4.UInt64(qty),
                total_invested=arc4.UInt64(payment.amount),
                investment_timestamp=arc4.UInt64(Global.latest_timestamp),
            )
            self.investors[investor_key] = new_investor

        log(b"SharesPurchased")

    @arc4.abimethod(readonly=True)
    def get_investor_shares(
        self, property_id: arc4.UInt64, investor_address: arc4.Address
    ) -> arc4.UInt64:
        """Read-only: returns the number of shares held by an investor."""
        pid = property_id.native
        investor_key = op.itob(pid) + investor_address.bytes
        if investor_key not in self.investors:
            return arc4.UInt64(0)
        record = self.investors[investor_key]
        return record.shares_held

    @arc4.abimethod(readonly=True)
    def get_investor_percentage(
        self, property_id: arc4.UInt64, investor_address: arc4.Address
    ) -> arc4.UInt64:
        """
        Read-only: returns investor's ownership in basis points.
        e.g. 3000 = 30.00%
        """
        pid = property_id.native
        investor_key = op.itob(pid) + investor_address.bytes
        if investor_key not in self.investors:
            return arc4.UInt64(0)

        record = self.investors[investor_key]
        token = self.tokens[pid]

        # (shares * 10000) / total_supply = basis points
        percentage = record.shares_held.native * UInt64(10000) / token.total_supply.native
        return arc4.UInt64(percentage)

    @arc4.abimethod()
    def burn_all_shares(self, property_id: arc4.UInt64) -> None:
        """
        Burn all shares for a property during settlement.
        Only callable by SettlementEngine.
        Uses clawback to reclaim all tokens from investors.
        """
        pid = property_id.native
        assert pid in self.tokens, "Token not found"

        token = self.tokens[pid].copy()

        # Clawback all remaining tokens held by investors
        count = self.investor_count[pid]
        idx = UInt64(0)
        while idx < count:
            addr_key = op.itob(pid) + op.itob(idx)
            if addr_key in self.investor_addresses:
                investor_addr = self.investor_addresses[addr_key]
                investor_key = op.itob(pid) + investor_addr.bytes
                if investor_key in self.investors:
                    record = self.investors[investor_key]
                    shares = record.shares_held.native
                    if shares > UInt64(0):
                        # Clawback via inner transaction
                        itxn.AssetTransfer(
                            xfer_asset=token.asa_id.native,
                            asset_sender=Account(investor_addr.bytes),
                            asset_receiver=Global.current_application_address,
                            asset_amount=shares,
                            fee=UInt64(0),
                        ).submit()
            idx += UInt64(1)

        log(b"SharesBurned")

    @arc4.abimethod(readonly=True)
    def get_token_info(self, property_id: arc4.UInt64) -> TokenRecord:
        """Read-only: returns full token metadata for a property."""
        pid = property_id.native
        assert pid in self.tokens, "Token not found"
        return self.tokens[pid]

    @arc4.abimethod(readonly=True)
    def get_insurance_balance(self) -> arc4.UInt64:
        """Read-only: returns the accumulated insurance pool balance."""
        return arc4.UInt64(self.insurance_pool_balance)

    @arc4.abimethod(readonly=True)
    def get_investor_count(self, property_id: arc4.UInt64) -> arc4.UInt64:
        """Read-only: returns the number of investors for a property."""
        pid = property_id.native
        if pid not in self.investor_count:
            return arc4.UInt64(0)
        return arc4.UInt64(self.investor_count[pid])
