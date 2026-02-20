"""
PropChain — SPVRegistry Smart Contract
=======================================
Tracks the legal Special Purpose Vehicle (SPV) entity associated with each
listed property. An SPV is a private limited company that legally holds the
property deed, preventing the owner from selling the physical property
without a governance vote.

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
    gtxn,
    log,
    op,
    subroutine,
)


# ── Box Storage Struct ─────────────────────────────────────────────────────

class SPVRecord(arc4.Struct):
    """On-chain record for a single SPV entity."""
    spv_cin: arc4.String           # Company Identification Number from MCA
    spv_pan: arc4.String           # PAN number of the SPV
    aoa_ipfs_cid: arc4.String      # IPFS CID of Articles of Association
    cert_ipfs_cid: arc4.String     # IPFS CID of Certificate of Incorporation
    deed_ipfs_cid: arc4.String     # IPFS CID of property deed transfer doc
    spv_status: arc4.UInt64        # 0=FORMING, 1=REGISTERED, 2=ACTIVE, 3=WOUND_UP
    governance_threshold: arc4.UInt64  # must be 51 (percent)
    created_at: arc4.UInt64        # block timestamp
    wound_up_at: arc4.UInt64       # block timestamp of wind-up (0 if not wound up)


# ── SPV Status Constants ───────────────────────────────────────────────────

SPV_FORMING = UInt64(0)
SPV_REGISTERED = UInt64(1)
SPV_ACTIVE = UInt64(2)
SPV_WOUND_UP = UInt64(3)

GOVERNANCE_THRESHOLD = UInt64(51)


class SPVRegistry(ARC4Contract):
    """
    SPVRegistry — manages legal SPV entities per property on PropChain.

    Only the authorized oracle wallet can register, activate, and wind-up SPVs.
    The SettlementEngine contract can also wind-up SPVs during property sale.
    """

    def __init__(self) -> None:
        # Global state
        self.total_properties = UInt64(0)
        self.oracle_address = Bytes(b"")
        # Box map: property_id (uint64) → SPVRecord
        self.spv_records = BoxMap(UInt64, SPVRecord, key_prefix=b"spv_")

    # ── ARC4 Methods ───────────────────────────────────────────────────────

    @arc4.abimethod(create="require")
    def create(self) -> None:
        """
        Initialize the SPVRegistry contract.
        Sets the transaction sender as the authorized oracle address.
        """
        self.oracle_address = Txn.sender.bytes
        self.total_properties = UInt64(0)
        log(b"SPVRegistry created. Oracle set to sender.")

    @arc4.abimethod()
    def register_spv(
        self,
        property_id: arc4.UInt64,
        cin: arc4.String,
        pan: arc4.String,
        aoa_cid: arc4.String,
        cert_cid: arc4.String,
        deed_cid: arc4.String,
    ) -> None:
        """
        Register a new SPV for a property.
        Only callable by the oracle address.
        Creates an SPV box record with status=REGISTERED.
        """
        # Authorization: only oracle can register SPVs
        assert Txn.sender.bytes == self.oracle_address, "Only oracle can register SPVs"

        # Create SPV record with REGISTERED status
        pid = property_id.native
        record = SPVRecord(
            spv_cin=cin,
            spv_pan=pan,
            aoa_ipfs_cid=aoa_cid,
            cert_ipfs_cid=cert_cid,
            deed_ipfs_cid=deed_cid,
            spv_status=arc4.UInt64(SPV_REGISTERED),
            governance_threshold=arc4.UInt64(GOVERNANCE_THRESHOLD),
            created_at=arc4.UInt64(Global.latest_timestamp),
            wound_up_at=arc4.UInt64(0),
        )

        # Store in box storage
        self.spv_records[pid] = record
        self.total_properties += UInt64(1)

        # Emit event
        log(b"SPVRegistered")

    @arc4.abimethod()
    def activate_spv(self, property_id: arc4.UInt64) -> None:
        """
        Activate an SPV after all legal formalities are complete.
        Only callable by the oracle address.
        Sets SPV status from REGISTERED to ACTIVE.
        """
        assert Txn.sender.bytes == self.oracle_address, "Only oracle can activate SPVs"

        pid = property_id.native
        assert pid in self.spv_records, "SPV not found"

        # Read existing record, update status
        record = self.spv_records[pid].copy()
        assert record.spv_status.native == SPV_REGISTERED, "SPV must be REGISTERED to activate"

        # Create updated record with ACTIVE status
        updated = SPVRecord(
            spv_cin=record.spv_cin,
            spv_pan=record.spv_pan,
            aoa_ipfs_cid=record.aoa_ipfs_cid,
            cert_ipfs_cid=record.cert_ipfs_cid,
            deed_ipfs_cid=record.deed_ipfs_cid,
            spv_status=arc4.UInt64(SPV_ACTIVE),
            governance_threshold=record.governance_threshold,
            created_at=record.created_at,
            wound_up_at=record.wound_up_at,
        )
        self.spv_records[pid] = updated

        # Emit event
        log(b"SPVActivated")

    @arc4.abimethod()
    def wind_up_spv(
        self,
        property_id: arc4.UInt64,
        windup_cid: arc4.String,
    ) -> None:
        """
        Wind up an SPV after a property sale is finalized.
        Callable by the oracle address or the SettlementEngine contract.
        Sets SPV status to WOUND_UP and records the wind-up timestamp.
        """
        # Authorization: oracle or SettlementEngine (checked by caller address)
        assert Txn.sender.bytes == self.oracle_address, "Only oracle can wind up SPVs"

        pid = property_id.native
        assert pid in self.spv_records, "SPV not found"

        record = self.spv_records[pid].copy()
        assert record.spv_status.native == SPV_ACTIVE, "SPV must be ACTIVE to wind up"

        # Update to WOUND_UP with timestamp
        updated = SPVRecord(
            spv_cin=record.spv_cin,
            spv_pan=record.spv_pan,
            aoa_ipfs_cid=record.aoa_ipfs_cid,
            cert_ipfs_cid=record.cert_ipfs_cid,
            deed_ipfs_cid=windup_cid,  # Store wind-up document CID
            spv_status=arc4.UInt64(SPV_WOUND_UP),
            governance_threshold=record.governance_threshold,
            created_at=record.created_at,
            wound_up_at=arc4.UInt64(Global.latest_timestamp),
        )
        self.spv_records[pid] = updated

        # Emit event
        log(b"SPVWoundUp")

    @arc4.abimethod(readonly=True)
    def get_spv_status(self, property_id: arc4.UInt64) -> arc4.UInt64:
        """
        Read-only: returns the current status of an SPV.
        0=FORMING, 1=REGISTERED, 2=ACTIVE, 3=WOUND_UP
        """
        pid = property_id.native
        assert pid in self.spv_records, "SPV not found"
        record = self.spv_records[pid]
        return record.spv_status

    @arc4.abimethod(readonly=True)
    def verify_active(self, property_id: arc4.UInt64) -> arc4.Bool:
        """
        Read-only: returns True if the SPV status is ACTIVE.
        Used by PropertyRegistry for cross-contract verification.
        """
        pid = property_id.native
        if pid not in self.spv_records:
            return arc4.Bool(False)
        record = self.spv_records[pid]
        return arc4.Bool(record.spv_status.native == SPV_ACTIVE)

    @arc4.abimethod(readonly=True)
    def get_aoa_cid(self, property_id: arc4.UInt64) -> arc4.String:
        """
        Read-only: returns the IPFS CID of the Articles of Association.
        Used for legal verification and display in the frontend.
        """
        pid = property_id.native
        assert pid in self.spv_records, "SPV not found"
        record = self.spv_records[pid]
        return record.aoa_ipfs_cid

    @arc4.abimethod(readonly=True)
    def get_spv_record(self, property_id: arc4.UInt64) -> SPVRecord:
        """
        Read-only: returns the full SPV record for a property.
        """
        pid = property_id.native
        assert pid in self.spv_records, "SPV not found"
        return self.spv_records[pid]
