# PropChain — Hackathon Demo Script

## 🎬 Opening (30 seconds)

> "PropChain is a decentralized real estate fractionalization protocol on Algorand.
> We're solving the problem of illiquid real estate assets by enabling anyone to
> own a piece of premium property starting at just ₹500."

## 🏗️ Architecture (1 minute)

Show architecture slide:

- **6 Smart Contracts** — SPV, Property, Token, Rent, Governance, Settlement
- **AI Oracle** — Tesseract OCR + spaCy NER for document verification
- **FastAPI Backend** — REST API with 5 route modules
- **React Frontend** — 6 pages with Pera Wallet integration

> "Every operation is on-chain. The AI oracle is the only trusted entity,
> and even that is constrained by contract-level assertions."

## 🔍 Live Demo (5 minutes)

### Step 1: Property Listing
1. Open frontend → "List Property"
2. Fill in property details
3. Upload documents (Sale Deed, EC, Tax Receipt, Aadhaar)
4. **AI Oracle processes in real-time** — show score breakdown

### Step 2: SPV Formation
> "Each property gets a legal SPV with CIN, PAN, and all docs pinned to IPFS."

### Step 3: Investment
1. Switch to Marketplace → click property
2. Use quantity slider → show cost breakdown with 1.5% insurance
3. Click "Buy Shares" → Pera Wallet popup

### Step 4: Rent Distribution
> "Owner deposits rent once. Each investor claims their proportional share."
1. Show Portfolio page → claimable amounts
2. Click "Claim" → Pera Wallet signs transaction

### Step 5: Governance
1. Navigate to Governance → show active proposal
2. Show YES/NO vote bars
3. Click "Vote YES" → demonstrate token-weighted voting

### Step 6: Settlement
> "When shareholders vote to sell, the settlement engine handles everything
> atomically: escrow, distribution, token burn, and SPV wind-up."

## 💡 Key Differentiators (30 seconds)

1. **AI-First Verification** — Not just KYC. Full document analysis.
2. **Legal Compliance** — SPV wrapper for each property.
3. **Gas-Efficient** — Pull-based rent (one deposit, many claims).
4. **True Governance** — On-chain voting with quorum checks.
5. **Atomic Settlement** — No partial states. Complete or rollback.

## 🧠 Technical Highlights

- **Box Storage** — All property, investor, and governance data in AVM boxes
- **ARC4 Methods** — Full ABI compatibility for interoperability
- **Composite Keys** — `property_id + investor_address` for O(1) lookups
- **Cross-Contract Calls** — Settlement orchestrates 4 other contracts

## 📊 Terminal Demo (Backup)

```bash
python demo/run_demo.py
```

This runs the full lifecycle with Rich-formatted output.
