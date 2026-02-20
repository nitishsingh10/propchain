"""
PropChain — Property Verification Scorer
==========================================
Scores extracted document data for verification confidence (0-100).
Verdicts: APPROVED (>=85) / MANUAL_REVIEW (60-84) / REJECTED (<60)
"""

from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher


@dataclass
class VerificationResult:
    score: int
    verdict: str
    flags: list[str]
    breakdown: dict
    recommendation: str
    timestamp: str


class PropertyVerificationScorer:

    def __init__(self):
        self.weights = {
            "name_consistency": 25, "document_completeness": 20,
            "encumbrance_clean": 25, "registration_validity": 20,
            "tax_compliance": 10,
        }

    def score(self, extracted_data: dict) -> VerificationResult:
        flags, breakdown = [], {}
        breakdown["name_consistency"] = self._score_name_consistency(extracted_data, flags)
        breakdown["document_completeness"] = self._score_document_completeness(extracted_data, flags)
        breakdown["encumbrance_clean"] = self._score_encumbrance_clean(extracted_data, flags)
        breakdown["registration_validity"] = self._score_registration_validity(extracted_data, flags)
        breakdown["tax_compliance"] = self._score_tax_compliance(extracted_data, flags)
        total = sum(breakdown.values())

        if total >= 85:
            verdict, rec = "APPROVED", "All documents verified. Proceed with SPV formation."
        elif total >= 60:
            verdict, rec = "MANUAL_REVIEW", f"Score {total}/100 needs review. Flags: {', '.join(flags)}"
        else:
            verdict, rec = "REJECTED", f"Score {total}/100 below threshold. Issues: {', '.join(flags)}"

        return VerificationResult(total, verdict, flags, breakdown, rec, datetime.utcnow().isoformat())

    def _score_name_consistency(self, data: dict, flags: list[str]) -> int:
        """Compare owner_name across aadhaar, sale_deed, property_tax. (25 pts)"""
        names = []
        for key, field in [("aadhaar", "name"), ("sale_deed", "owner_name"), ("property_tax", "owner_name")]:
            doc = data.get(key)
            if doc and doc.get(field):
                names.append(doc[field].strip().upper())
        if len(names) < 2:
            flags.append("WARNING: INSUFFICIENT_NAME_SOURCES"); return 10
        min_ratio = min(SequenceMatcher(None, names[i], names[j]).ratio()
                        for i in range(len(names)) for j in range(i+1, len(names)))
        if min_ratio >= 0.95: return 25
        if min_ratio >= 0.85: return 18
        if min_ratio >= 0.70:
            flags.append("WARNING: NAME_MISMATCH_PARTIAL"); return 10
        flags.append("CRITICAL: NAME_MISMATCH"); return 0

    def _score_document_completeness(self, data: dict, flags: list[str]) -> int:
        """All 4 docs present: 20pts, 3: 14pts, 2: 7pts, else: 0. (20 pts)"""
        present = sum(1 for dt in ["aadhaar", "sale_deed", "ec", "property_tax"] if data.get(dt))
        if present == 4: return 20
        if present == 3:
            flags.append("WARNING: MISSING_DOCUMENT"); return 14
        if present == 2:
            flags.append("WARNING: MISSING_DOCUMENTS"); return 7
        flags.append("CRITICAL: INSUFFICIENT_DOCUMENTS"); return 0

    def _score_encumbrance_clean(self, data: dict, flags: list[str]) -> int:
        """No mortgages/liabilities: 25pts. Active mortgage: 0pts. (25 pts)"""
        ec = data.get("ec")
        if not ec:
            flags.append("WARNING: NO_EC"); return 0
        if ec.get("mortgages"):
            flags.append("CRITICAL: EXISTING_MORTGAGE"); return 0
        if ec.get("liabilities"):
            flags.append("WARNING: EXISTING_LIABILITIES"); return 10
        if ec.get("transactions"):
            return 18
        # Check EC period
        pf, pt = ec.get("period_from"), ec.get("period_to")
        if pf and pt:
            try:
                for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
                    try:
                        fd, td = datetime.strptime(pf, fmt), datetime.strptime(pt, fmt)
                        if (td - fd).days / 365.25 < 13:
                            flags.append("WARNING: EC_PERIOD_SHORT")
                        break
                    except ValueError: continue
            except Exception: pass
        return 25

    def _score_registration_validity(self, data: dict, flags: list[str]) -> int:
        """Reg number present + valid date: 20pts. Future date: 0pts. (20 pts)"""
        sd = data.get("sale_deed")
        if not sd:
            flags.append("WARNING: NO_SALE_DEED"); return 0
        score = 0
        if sd.get("registration_number") and len(sd["registration_number"]) >= 4:
            score += 10
        else:
            flags.append("WARNING: MISSING_REGISTRATION_NUMBER")
        rd = sd.get("registration_date")
        if rd:
            for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
                try:
                    reg_date = datetime.strptime(rd, fmt)
                    if reg_date > datetime.now():
                        flags.append("CRITICAL: FUTURE_REGISTRATION"); return 0
                    if (datetime.now() - reg_date).days / 365.25 <= 30:
                        score += 5
                    break
                except ValueError: continue
        if sd.get("sub_registrar_office") and len(sd["sub_registrar_office"]) >= 3:
            score += 5
        return min(score, 20)

    def _score_tax_compliance(self, data: dict, flags: list[str]) -> int:
        """No dues: 10pts. Dues <1yr: 5pts. Dues >1yr: 0pts. (10 pts)"""
        tax = data.get("property_tax")
        if not tax:
            flags.append("WARNING: NO_TAX_RECEIPT"); return 0
        dues = tax.get("dues_pending")
        if not dues or dues == "0": return 10
        try:
            if int(dues) == 0: return 10
        except (ValueError, TypeError): pass
        lp = tax.get("last_paid_date")
        if lp:
            for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
                try:
                    pd = datetime.strptime(lp, fmt)
                    if (datetime.now() - pd).days <= 365:
                        flags.append("WARNING: TAX_DUES_MINOR"); return 5
                    flags.append("WARNING: TAX_DUES"); return 0
                except ValueError: continue
        flags.append("WARNING: TAX_DUES"); return 5


if __name__ == "__main__":
    mock_approved = {
        "aadhaar": {"name": "Rajesh Kumar Singh", "aadhaar_number": "XXXX XXXX 4567"},
        "sale_deed": {"owner_name": "Rajesh Kumar Singh", "registration_number": "BLR-2020-123456",
                      "registration_date": "12/06/2020", "sub_registrar_office": "Jayanagar"},
        "ec": {"transactions": [], "liabilities": [], "mortgages": [],
               "period_from": "01/01/2010", "period_to": "31/12/2023"},
        "property_tax": {"owner_name": "Rajesh Kumar Singh", "dues_pending": "0",
                         "last_paid_date": "15/09/2023"},
    }
    mock_rejected = {
        "aadhaar": {"name": "Rajesh Kumar Singh"},
        "sale_deed": {"owner_name": "Suresh Sharma", "registration_number": "BLR-2020-123456",
                      "registration_date": "12/06/2020", "sub_registrar_office": "Jayanagar"},
        "ec": {"mortgages": [{"date": "01/01/2022"}], "transactions": [], "liabilities": []},
        "property_tax": None,
    }
    s = PropertyVerificationScorer()
    r1 = s.score(mock_approved)
    print(f"Approved test: {r1.score}/100 → {r1.verdict} | Flags: {r1.flags}")
    assert r1.verdict == "APPROVED"
    r2 = s.score(mock_rejected)
    print(f"Rejected test: {r2.score}/100 → {r2.verdict} | Flags: {r2.flags}")
    assert r2.verdict == "REJECTED"
    print("✅ All tests passed!")
