"""
PropChain — FastAPI Backend
==============================
Main application with CORS, routers, health check, and logging middleware.
"""

import os
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("propchain.api")
logging.basicConfig(level=logging.INFO)

# ── App State (initialized on startup) ────────────────────────────────────

app_state = {
    "algod_client": None,
    "oracle": None,
    "app_ids": {},
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Algorand client, oracle, and contract clients on startup."""
    try:
        from algosdk.v2client import algod
        algod_server = os.getenv("ALGOD_SERVER", "https://testnet-api.algonode.cloud")
        algod_token = os.getenv("ALGOD_TOKEN", "")
        app_state["algod_client"] = algod.AlgodClient(algod_token, algod_server)
    except ImportError:
        logger.warning("algosdk not installed — Algorand client unavailable")

    try:
        import sys
        # Ensure project root is on path for ai_oracle imports
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from ai_oracle.verifier import PropChainOracle
        app_state["oracle"] = PropChainOracle()
    except (ImportError, Exception) as e:
        logger.warning(f"AI Oracle unavailable: {e}")
        app_state["oracle"] = None

    def _get_app_id(key: str) -> int:
        val = os.getenv(key, "0").strip()
        return int(val) if val else 0

    app_state["app_ids"] = {
        "spv_registry": _get_app_id("APP_ID_SPV_REGISTRY"),
        "property_registry": _get_app_id("APP_ID_PROPERTY_REGISTRY"),
        "fractional_token": _get_app_id("APP_ID_FRACTIONAL_TOKEN"),
        "rent_distributor": _get_app_id("APP_ID_RENT_DISTRIBUTOR"),
        "governance": _get_app_id("APP_ID_GOVERNANCE"),
        "settlement": _get_app_id("APP_ID_SETTLEMENT"),
    }
    logger.info("PropChain API initialized")
    yield
    logger.info("PropChain API shutting down")


# ── FastAPI App ───────────────────────────────────────────────────────────

app = FastAPI(
    title="PropChain API",
    version="1.0.0",
    description="Decentralized Real Estate Fractionalization Protocol on Algorand",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Logging Middleware ─────────────────────────────────────────────

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response


# ── Global Exception Handler ──────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# ── Health Check ──────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    node_status = "disconnected"
    try:
        if app_state["algod_client"]:
            status = app_state["algod_client"].status()
            node_status = "connected"
    except Exception:
        pass

    return {
        "status": "ok",
        "algorand_node": node_status,
        "contracts": app_state["app_ids"],
        "network": "testnet",
    }


# ── Include Routers ──────────────────────────────────────────────────────

from routes.properties import router as properties_router
from routes.investments import router as investments_router
from routes.rent import router as rent_router
from routes.governance import router as governance_router
from routes.settlement import router as settlement_router

@app.post("/submit")
async def submit_transaction(req: Request):
    from pydantic import BaseModel
    class SubmitReq(BaseModel):
        signed_txn: str
    data = await req.json()
    try:
        if app_state["algod_client"]:
            # send_raw_transaction expects a base64 string natively and decodes it internally
            txid = app_state["algod_client"].send_raw_transaction(data["signed_txn"])
            return {"success": True, "txid": txid, "message": "Transaction submitted to Algorand"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    return {"success": True, "txid": "simulated_txid"}

app.include_router(properties_router, prefix="/properties", tags=["Properties"])
app.include_router(investments_router, prefix="/investments", tags=["Investments"])
app.include_router(rent_router, prefix="/rent", tags=["Rent"])
app.include_router(governance_router, prefix="/governance", tags=["Governance"])
app.include_router(settlement_router, prefix="/settlement", tags=["Settlement"])
