"""
PropChain — OCR Engine
========================
Extracts structured data from Indian property documents using OCR.

Handles document types:
- Aadhaar Card (identity verification)
- Sale Deed / Title Deed
- Encumbrance Certificate (EC)
- Property Tax Receipt
- Khata Certificate

Required system dependency: tesseract-ocr (install via `brew install tesseract`)
"""

import os
import re
from typing import Optional
from pathlib import Path

from PIL import Image, ImageFilter, ImageEnhance

try:
    import pytesseract
except ImportError:
    pytesseract = None  # type: ignore

try:
    import spacy
except ImportError:
    spacy = None  # type: ignore


class DocumentOCREngine:
    """
    OCR engine for extracting structured data from Indian property documents.
    Uses Tesseract OCR with Hindi + English language support and spaCy NER.
    """

    def __init__(self):
        """
        Initialize Tesseract OCR with Hindi + English language support.
        Load spaCy en_core_web_sm model for named entity recognition.
        """
        # Tesseract configuration for Hindi + English
        self.tesseract_config = "--oem 3 --psm 6"
        self.lang = "eng+hin"

        # Load spaCy model for NER (fallback if not available)
        self.nlp = None
        if spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("⚠️  spaCy en_core_web_sm not found. NER disabled.")

    # ── Core Extraction Methods ────────────────────────────────────────────

    def extract_from_pdf(self, file_path: str) -> dict:
        """
        Convert PDF pages to images and run OCR on each page.

        Args:
            file_path: Path to PDF file

        Returns:
            dict with keys: 'pages' (list of text per page), 'full_text' (combined)
        """
        try:
            # Use pdf2image to convert PDF to images
            # Requires poppler-utils system package
            from pdf2image import convert_from_path

            images = convert_from_path(file_path, dpi=300)
            pages = []
            for i, img in enumerate(images):
                # Preprocess image for better OCR
                processed = self._preprocess_image(img)
                text = self._run_ocr(processed)
                pages.append(text)

            full_text = "\n\n--- PAGE BREAK ---\n\n".join(pages)
            return {"pages": pages, "full_text": full_text}

        except ImportError:
            # Fallback: try to extract text directly
            return {"pages": [], "full_text": "", "error": "pdf2image not installed"}
        except Exception as e:
            return {"pages": [], "full_text": "", "error": str(e)}

    def extract_from_image(self, file_path: str) -> str:
        """
        Run Tesseract OCR on an image file.

        Args:
            file_path: Path to image file (PNG, JPG, TIFF)

        Returns:
            Cleaned extracted text
        """
        try:
            img = Image.open(file_path)
            processed = self._preprocess_image(img)
            text = self._run_ocr(processed)
            return self._clean_text(text)
        except Exception as e:
            return f"Error: {str(e)}"

    # ── Document Parsers ───────────────────────────────────────────────────

    def parse_aadhaar(self, text: str) -> dict:
        """
        Parse Aadhaar card OCR text.

        Returns:
            dict with: name, aadhaar_number (masked), dob, gender, address
        """
        result = {
            "name": None,
            "aadhaar_number": None,
            "dob": None,
            "gender": None,
            "address": None,
        }

        # Extract Aadhaar number (XXXX XXXX XXXX pattern)
        aadhaar_pattern = r"\b(\d{4}\s?\d{4}\s?\d{4})\b"
        match = re.search(aadhaar_pattern, text)
        if match:
            raw_number = match.group(1).replace(" ", "")
            # Mask for privacy: XXXX XXXX 1234
            result["aadhaar_number"] = f"XXXX XXXX {raw_number[-4:]}"

        # Extract Date of Birth
        dob_patterns = [
            r"DOB\s*:?\s*(\d{2}[/-]\d{2}[/-]\d{4})",
            r"Date of Birth\s*:?\s*(\d{2}[/-]\d{2}[/-]\d{4})",
            r"Year of Birth\s*:?\s*(\d{4})",
            r"\b(\d{2}/\d{2}/\d{4})\b",
        ]
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["dob"] = match.group(1)
                break

        # Extract Gender
        gender_pattern = r"\b(Male|Female|MALE|FEMALE|Transgender)\b"
        match = re.search(gender_pattern, text, re.IGNORECASE)
        if match:
            result["gender"] = match.group(1).capitalize()

        # Extract Name (usually first large text after "Government of India")
        name_patterns = [
            r"(?:Name|नाम)\s*:?\s*(.+?)(?:\n|$)",
            r"Government of India\s*\n\s*(.+?)(?:\n|$)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["name"] = match.group(1).strip()
                break

        # Use spaCy NER for name extraction fallback
        if not result["name"] and self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    result["name"] = ent.text
                    break

        # Extract Address (text after "Address" or "पता")
        addr_pattern = r"(?:Address|पता)\s*:?\s*(.+?)(?:(?:\d{4}\s?\d{4}\s?\d{4})|$)"
        match = re.search(addr_pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            result["address"] = " ".join(match.group(1).split())

        return result

    def parse_sale_deed(self, text: str) -> dict:
        """
        Parse Sale Deed / Title Deed OCR text.

        Returns:
            dict with: owner_name, co_owners, survey_number, property_address,
                       area_sqft, registration_date, registration_number,
                       sub_registrar_office, consideration_amount, seller_name
        """
        result = {
            "owner_name": None,
            "co_owners": [],
            "survey_number": None,
            "property_address": None,
            "area_sqft": None,
            "registration_date": None,
            "registration_number": None,
            "sub_registrar_office": None,
            "consideration_amount": None,
            "seller_name": None,
        }

        # Registration number
        reg_patterns = [
            r"(?:Registration|Reg\.?)\s*(?:No\.?|Number)\s*:?\s*([A-Z0-9/-]+)",
            r"Document\s*No\.?\s*:?\s*([A-Z0-9/-]+)",
        ]
        for pattern in reg_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["registration_number"] = match.group(1).strip()
                break

        # Registration date
        date_patterns = [
            r"(?:Date|Dated)\s*:?\s*(\d{2}[/-]\d{2}[/-]\d{4})",
            r"(?:registered|executed)\s*on\s*(\d{2}[/-]\d{2}[/-]\d{4})",
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["registration_date"] = match.group(1)
                break

        # Survey number
        survey_patterns = [
            r"Survey\s*(?:No\.?|Number)\s*:?\s*([A-Z0-9/]+)",
            r"Sy\.?\s*No\.?\s*:?\s*([A-Z0-9/]+)",
        ]
        for pattern in survey_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["survey_number"] = match.group(1).strip()
                break

        # Area
        area_patterns = [
            r"(\d[\d,]+)\s*(?:sq\.?\s*ft|square\s*feet|sqft)",
            r"area\s*(?:of|:)?\s*(\d[\d,]+)",
        ]
        for pattern in area_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["area_sqft"] = match.group(1).replace(",", "")
                break

        # Consideration amount
        amount_patterns = [
            r"(?:consideration|sale\s*price|amount)\s*(?:of|:)?\s*(?:Rs\.?|₹|INR)\s*([\d,]+)",
            r"(?:Rs\.?|₹|INR)\s*([\d,]+(?:\.\d{2})?)",
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["consideration_amount"] = match.group(1).replace(",", "")
                break

        # Sub-registrar office
        sr_pattern = r"Sub[\s-]?Registrar\s*(?:Office)?\s*(?:of|:)?\s*(.+?)(?:\n|$)"
        match = re.search(sr_pattern, text, re.IGNORECASE)
        if match:
            result["sub_registrar_office"] = match.group(1).strip()

        # Owner/buyer name
        buyer_patterns = [
            r"(?:Buyer|Purchaser|Vendee)\s*:?\s*(.+?)(?:\n|,|$)",
            r"(?:in\s*favour\s*of)\s*(.+?)(?:\n|,|$)",
        ]
        for pattern in buyer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["owner_name"] = match.group(1).strip()
                break

        # Seller name
        seller_patterns = [
            r"(?:Seller|Vendor)\s*:?\s*(.+?)(?:\n|,|$)",
            r"(?:sold\s*by)\s*(.+?)(?:\n|,|$)",
        ]
        for pattern in seller_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["seller_name"] = match.group(1).strip()
                break

        return result

    def parse_encumbrance_certificate(self, text: str) -> dict:
        """
        Parse Encumbrance Certificate (EC) OCR text.

        Returns:
            dict with: property_description, period_from, period_to,
                       transactions, liabilities, mortgages
        """
        result = {
            "property_description": None,
            "period_from": None,
            "period_to": None,
            "transactions": [],
            "liabilities": [],
            "mortgages": [],
        }

        # Period
        period_pattern = r"(?:Period|From)\s*:?\s*(\d{2}[/-]\d{2}[/-]\d{4})\s*(?:to|To|-)\s*(\d{2}[/-]\d{2}[/-]\d{4})"
        match = re.search(period_pattern, text, re.IGNORECASE)
        if match:
            result["period_from"] = match.group(1)
            result["period_to"] = match.group(2)

        # Property description
        desc_pattern = r"(?:Property\s*Description|Description\s*of\s*Property)\s*:?\s*(.+?)(?:\n\n|\n(?:Period|Encumbrance))"
        match = re.search(desc_pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            result["property_description"] = " ".join(match.group(1).split())

        # Check for mortgages
        mortgage_patterns = [
            r"(?:Mortgage|Hypothecation)\s*(?:Deed|Agreement)?\s*(?:dated?\s*)?\s*(\d{2}[/-]\d{2}[/-]\d{4})?",
        ]
        for pattern in mortgage_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                result["mortgages"] = [{"date": m, "type": "Mortgage"} for m in matches if m]

        # Check for "Nil Encumbrance"
        if re.search(r"(?:nil|no)\s*encumbrance", text, re.IGNORECASE):
            result["transactions"] = []
            result["liabilities"] = []

        return result

    def parse_property_tax(self, text: str) -> dict:
        """
        Parse Property Tax Receipt OCR text.

        Returns:
            dict with: property_id, owner_name, ward_number,
                       annual_tax, last_paid_date, dues_pending
        """
        result = {
            "property_id": None,
            "owner_name": None,
            "ward_number": None,
            "annual_tax": None,
            "last_paid_date": None,
            "dues_pending": None,
        }

        # Property ID / Assessment Number
        pid_patterns = [
            r"(?:Property\s*ID|Assessment\s*No|PID)\s*:?\s*([A-Z0-9/-]+)",
            r"(?:Khata\s*No)\s*:?\s*([A-Z0-9/-]+)",
        ]
        for pattern in pid_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["property_id"] = match.group(1).strip()
                break

        # Owner name
        name_pattern = r"(?:Owner|Name)\s*:?\s*(.+?)(?:\n|$)"
        match = re.search(name_pattern, text, re.IGNORECASE)
        if match:
            result["owner_name"] = match.group(1).strip()

        # Ward number
        ward_pattern = r"(?:Ward)\s*(?:No\.?)?\s*:?\s*(\d+)"
        match = re.search(ward_pattern, text, re.IGNORECASE)
        if match:
            result["ward_number"] = match.group(1)

        # Annual tax
        tax_pattern = r"(?:Annual\s*Tax|Tax\s*Amount)\s*:?\s*(?:Rs\.?|₹)?\s*([\d,]+)"
        match = re.search(tax_pattern, text, re.IGNORECASE)
        if match:
            result["annual_tax"] = match.group(1).replace(",", "")

        # Last paid date
        paid_pattern = r"(?:Last\s*Paid|Paid\s*(?:on|Date))\s*:?\s*(\d{2}[/-]\d{2}[/-]\d{4})"
        match = re.search(paid_pattern, text, re.IGNORECASE)
        if match:
            result["last_paid_date"] = match.group(1)

        # Dues pending
        dues_patterns = [
            r"(?:Dues?\s*Pending|Arrears?|Outstanding)\s*:?\s*(?:Rs\.?|₹)?\s*([\d,]+)",
            r"(?:No\s*(?:Dues?|Arrears?))",
        ]
        for pattern in dues_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result["dues_pending"] = match.group(1).replace(",", "")
                except IndexError:
                    result["dues_pending"] = "0"
                break

        return result

    # ── Auto-Detection & Batch Processing ─────────────────────────────────

    def detect_document_type(self, text: str) -> str:
        """
        Auto-detect document type from OCR text.

        Returns:
            One of: 'aadhaar', 'sale_deed', 'ec', 'property_tax', 'unknown'
        """
        text_lower = text.lower()

        # Aadhaar Card indicators
        aadhaar_keywords = ["aadhaar", "uid", "unique identification", "uidai", "आधार"]
        if any(kw in text_lower for kw in aadhaar_keywords):
            return "aadhaar"

        # Sale Deed indicators
        deed_keywords = ["sale deed", "title deed", "conveyance", "vendee", "vendor",
                         "sub registrar", "registration", "consideration"]
        if sum(1 for kw in deed_keywords if kw in text_lower) >= 2:
            return "sale_deed"

        # Encumbrance Certificate indicators
        ec_keywords = ["encumbrance", "certificate", "nil encumbrance", "mortgage",
                       "hypothecation"]
        if any(kw in text_lower for kw in ec_keywords):
            return "ec"

        # Property Tax Receipt indicators
        tax_keywords = ["property tax", "tax receipt", "assessment", "ward",
                        "annual tax", "bbmp", "municipal"]
        if sum(1 for kw in tax_keywords if kw in text_lower) >= 2:
            return "property_tax"

        return "unknown"

    def extract_all(self, files: list[str]) -> dict:
        """
        Process multiple files, auto-detect type, and return structured bundle.

        Args:
            files: List of file paths (PDF or images)

        Returns:
            dict with keys: aadhaar, sale_deed, ec, property_tax
            Each value is the parsed result dict or None
        """
        results = {
            "aadhaar": None,
            "sale_deed": None,
            "ec": None,
            "property_tax": None,
            "raw_texts": {},
        }

        for file_path in files:
            # Extract text based on file type
            ext = Path(file_path).suffix.lower()
            if ext == ".pdf":
                extraction = self.extract_from_pdf(file_path)
                text = extraction.get("full_text", "")
            elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"):
                text = self.extract_from_image(file_path)
            else:
                continue

            if not text:
                continue

            # Auto-detect and parse
            doc_type = self.detect_document_type(text)
            results["raw_texts"][file_path] = {"type": doc_type, "text": text[:500]}

            if doc_type == "aadhaar":
                results["aadhaar"] = self.parse_aadhaar(text)
            elif doc_type == "sale_deed":
                results["sale_deed"] = self.parse_sale_deed(text)
            elif doc_type == "ec":
                results["ec"] = self.parse_encumbrance_certificate(text)
            elif doc_type == "property_tax":
                results["property_tax"] = self.parse_property_tax(text)

        return results

    # ── Private Helper Methods ─────────────────────────────────────────────

    def _preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.
        Applies: grayscale, contrast enhancement, denoising, thresholding.
        """
        # Convert to grayscale
        img = img.convert("L")

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)

        # Denoise
        img = img.filter(ImageFilter.MedianFilter(size=3))

        # Threshold (binarize)
        threshold = 150
        img = img.point(lambda p: 255 if p > threshold else 0)

        return img

    def _run_ocr(self, img: Image.Image) -> str:
        """Run Tesseract OCR on a preprocessed image."""
        if pytesseract is None:
            return ""
        try:
            return pytesseract.image_to_string(
                img, lang=self.lang, config=self.tesseract_config
            )
        except Exception as e:
            return f"OCR Error: {str(e)}"

    def _clean_text(self, text: str) -> str:
        """Clean OCR output text."""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove non-printable characters
        text = "".join(c for c in text if c.isprintable() or c in "\n\t")
        return text.strip()
