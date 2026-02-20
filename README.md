# 🏗️ PropChain Protocol

**Decentralized Real Estate Fractionalization on Algorand**

PropChain enables fractional ownership of premium real estate through AI-verified smart contracts on Algorand. Own a piece of property starting at ₹500 — with on-chain governance, automated rent distribution, and atomic settlement.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Document Verification** | Tesseract OCR + spaCy NER verifies sale deeds, encumbrance certificates, tax receipts |
| 🏛️ **SPV Legal Wrapper** | Each property wrapped in an SPV with CIN, PAN, and docs on IPFS |
| 🧩 **Fractional Tokens** | ASA-based shares with insurance premium (1.5%) |
| 💰 **Automated Rent** | Pull-based distribution — one deposit, proportional claims |
| 🗳️ **On-Chain Governance** | Token-weighted voting with 51% quorum |
| ⚡ **Atomic Settlement** | Escrow → distribute → burn → wind-up in one orchestrated flow |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                       │
│  Landing │ Marketplace │ Portfolio │ Governance │ List  │
├─────────────────────────────────────────────────────────┤
│                 Pera Wallet SDK                         │
├─────────────────────────────────────────────────────────┤
│                  FastAPI Backend                        │
│  Properties │ Investments │ Rent │ Governance │ Settle  │
├─────────────────────────────────────────────────────────┤
│              AI Oracle (OCR + Scorer)                   │
├─────────────────────────────────────────────────────────┤
│             Algorand Testnet (Puya/AVM)                 │
│  SPV │ Property │ Token │ Rent │ Governance │ Settle    │
├─────────────────────────────────────────────────────────┤
│                 IPFS (Pinata)                           │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Propchain/
├── contracts/           # 6 Puya smart contracts
│   ├── spv_registry.py
│   ├── property_registry.py
│   ├── fractional_token.py
│   ├── rent_distributor.py
│   ├── governance_voting.py
│   └── settlement_engine.py
├── ai_oracle/           # AI verification pipeline
│   ├── ocr_engine.py    # Tesseract OCR + doc parsers
│   ├── scorer.py        # 5-component scoring (0-100)
│   └── verifier.py      # Oracle service + on-chain submission
├── backend/             # FastAPI REST API
│   ├── main.py
│   ├── models.py
│   ├── routes/          # 5 route modules
│   └── utils/           # Algorand + IPFS clients
├── frontend/            # React + Tailwind
│   └── src/
│       ├── pages/       # 6 pages
│       ├── components/  # Layout, UI primitives
│       └── utils/       # Wallet + API client
├── tests/               # Unit + integration tests
├── demo/                # Hackathon demo script
├── deploy.py            # Contract deployment script
└── algokit.toml         # AlgoKit configuration
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- [AlgoKit CLI](https://github.com/algorandfoundation/algokit-cli)
- Tesseract OCR: `brew install tesseract`

### 1. Clone & Install

```bash
git clone <repo-url>
cd Propchain

# Python dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Frontend
cd frontend && npm install && cd ..
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your:
# - ORACLE_MNEMONIC (25-word Algorand mnemonic)
# - PINATA_API_KEY + PINATA_SECRET
```

### 3. Deploy Smart Contracts

```bash
# Using AlgoKit (LocalNet)
algokit localnet start
python deploy.py

# Or deploy to Testnet
ALGOD_SERVER=https://testnet-api.algonode.cloud python deploy.py
```

### 4. Run Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

### 5. Run Frontend

```bash
cd frontend
npm run dev
# Opens at http://localhost:3000
```

### 6. Run Demo (Terminal)

```bash
python demo/run_demo.py
```

---

## 🧪 Testing

```bash
# Contract lifecycle tests
pytest tests/test_contracts.py -v

# Edge case tests
pytest tests/test_edge_cases.py -v

# E2E integration tests
pytest tests/test_e2e.py -v

# AI scorer unit test
python ai_oracle/scorer.py
```

---

## 📜 Smart Contracts

| Contract | Purpose | Key Methods |
|----------|---------|-------------|
| **SPVRegistry** | Legal entity management | `register_spv`, `activate_spv`, `wind_up_spv` |
| **PropertyRegistry** | Property lifecycle | `submit_property`, `verify_property`, `activate_listing` |
| **FractionalToken** | ASA creation & trading | `create_token`, `buy_shares`, `burn_all_shares` |
| **RentDistributor** | Pull-based rent | `deposit_rent`, `claim_rent`, `flag_missed_deposit` |
| **GovernanceVoting** | Token-weighted votes | `create_proposal`, `cast_vote`, `finalize_proposal` |
| **SettlementEngine** | Atomic settlement | `initiate_settlement`, `fund_escrow`, `distribute_proceeds` |

---

## 🤖 AI Verification Scoring

| Component | Weight | What It Checks |
|-----------|--------|----------------|
| Name Consistency | 25 pts | Fuzzy match across Aadhaar, deed, tax |
| Document Completeness | 20 pts | All 4 document types present |
| Encumbrance Clean | 25 pts | No mortgages or liens |
| Registration Validity | 20 pts | Valid reg number + date |
| Tax Compliance | 10 pts | No pending dues |

**Verdicts:** `≥85 = APPROVED` · `60-84 = MANUAL_REVIEW` · `<60 = REJECTED`

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/properties/` | List all properties |
| POST | `/properties/submit` | Submit new property |
| POST | `/properties/{id}/verify` | AI verification (file upload) |
| POST | `/investments/buy` | Purchase shares |
| GET | `/investments/portfolio/{addr}` | Investor portfolio |
| POST | `/rent/deposit` | Deposit quarterly rent |
| POST | `/rent/claim` | Claim rent |
| POST | `/governance/propose` | Create proposal |
| POST | `/governance/vote` | Cast vote |
| POST | `/settlement/initiate` | Start settlement |
| GET | `/settlement/status/{id}` | Settlement status |

---

## 🛠️ Tech Stack

- **Blockchain:** Algorand Testnet (AVM 10)
- **Smart Contracts:** Puya (algopy) — ARC4 compliant
- **Backend:** FastAPI + Pydantic
- **Frontend:** React 18 + Tailwind CSS 3.4
- **Wallet:** Pera Wallet SDK
- **Storage:** IPFS via Pinata
- **AI/OCR:** Tesseract + spaCy + PIL
- **Testing:** pytest + pytest-asyncio

---

## 📄 License

MIT

---

Built with 💚 on Algorand
