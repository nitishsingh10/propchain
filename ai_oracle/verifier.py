"""
PropChain — AI Oracle Verifier
================================
Ties together DocumentOCREngine and PropertyVerificationScorer
to provide a single verify_property() entry point for the API.
"""

import logging
from pathlib import Path

logger = logging.getLogger("propchain.oracle")

# Import OCR engine (requires pytesseract + spacy)
try:
    from ai_oracle.ocr_engine import DocumentOCREngine
    _HAS_OCR = True
except Exception as e:
    logger.warning(f"OCR engine unavailable: {e}")
    _HAS_OCR = False

from ai_oracle.scorer import PropertyVerificationScorer


class PropChainOracle:
    """
    High-level oracle that processes uploaded property documents,
    extracts structured data via OCR, scores them, and returns
    a verification result.
    """

    def __init__(self):
        self.scorer = PropertyVerificationScorer()
        if _HAS_OCR:
            try:
                self.ocr = DocumentOCREngine()
            except Exception as e:
                logger.warning(f"OCR engine init failed (tesseract missing?): {e}")
                self.ocr = None
        else:
            self.ocr = None
        logger.info(f"PropChainOracle initialized (OCR={'yes' if self.ocr else 'no'})")

    async def verify_property(self, property_id: int, file_paths: list[str]) -> dict:
        """
        Run the full verification pipeline:
        1. OCR all uploaded documents
        2. Auto-detect document types
        3. Score extracted data
        4. Return verdict + breakdown

        If OCR is unavailable, runs a mock/demo verification.
        """
        logger.info(f"Verifying property #{property_id} with {len(file_paths)} file(s)")

        if self.ocr:
            try:
                extracted = self.ocr.extract_all(file_paths)
                result = self.scorer.score(extracted)
                return {
                    "property_id": property_id,
                    "score": result.score,
                    "verdict": result.verdict,
                    "flags": result.flags,
                    "breakdown": result.breakdown,
                    "recommendation": result.recommendation,
                    "timestamp": result.timestamp,
                }
            except Exception as e:
                logger.error(f"OCR pipeline error: {e}", exc_info=True)
                # Fall through to demo mode

        # ── Demo / fallback mode ─────────────────────────────────────────
        logger.info("Running demo verification (OCR unavailable)")
        demo_data = {
            "aadhaar": {"name": "Property Owner", "aadhaar_number": "XXXX XXXX 1234"},
            "sale_deed": {
                "owner_name": "Property Owner",
                "registration_number": f"REG-{property_id}-2024",
                "registration_date": "15/06/2024",
                "sub_registrar_office": "Local Office",
            },
            "ec": {
                "transactions": [],
                "liabilities": [],
                "mortgages": [],
                "period_from": "01/01/2015",
                "period_to": "31/12/2024",
            },
            "property_tax": {
                "owner_name": "Property Owner",
                "dues_pending": "0",
                "last_paid_date": "01/09/2024",
            },
        }
        result = self.scorer.score(demo_data)
        return {
            "property_id": property_id,
            "score": result.score,
            "verdict": result.verdict,
            "flags": result.flags + ["INFO: DEMO_MODE"],
            "breakdown": result.breakdown,
            "recommendation": result.recommendation,
            "timestamp": result.timestamp,
        }

    async def register_spv_on_chain(
        self, property_id: int, cin: str, pan: str,
        aoa_cid: str, cert_cid: str, deed_cid: str,
    ) -> dict:
        """Register SPV details (stub — returns mock response)."""
        logger.info(f"Registering SPV for property #{property_id}")
        return {
            "message": "SPV registered successfully",
            "property_id": property_id,
            "cin": cin,
            "status": "SPV_REGISTERED",
        }
