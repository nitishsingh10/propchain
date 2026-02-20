"""
PropChain — End-to-End Integration Test
==========================================
Tests the full stack: API endpoints, oracle verification, and contract flow.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_oracle():
    """Mock the PropChain oracle for testing."""
    with patch("ai_oracle.verifier.PropChainOracle") as mock:
        instance = MagicMock()
        instance.verify_property.return_value = {
            "success": True, "score": 92, "verdict": "APPROVED",
            "flags": [], "ipfs_cid": "QmTestCID123", "txid": "TESTTXID123",
            "breakdown": {"name": 25, "docs": 20, "ec": 25, "reg": 20, "tax": 10},
        }
        mock.return_value = instance
        yield instance


class TestAPIHealth:
    """Test API health and configuration."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        from backend.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"
            assert "contracts" in data

    @pytest.mark.asyncio
    async def test_cors_headers(self):
        from backend.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.options("/health", headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            })
            assert resp.status_code == 200


class TestPropertyEndpoints:
    """Test property-related API endpoints."""

    @pytest.mark.asyncio
    async def test_list_properties(self):
        from backend.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/properties/")
            assert resp.status_code == 200
            assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_submit_property(self):
        from backend.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/properties/submit", json={
                "owner_address": "TESTADDR123",
                "property_name": "Test Property",
                "location_hash": "QmTestHash",
                "valuation": 50000000,
                "total_shares": 10000,
                "share_price": 5000,
                "min_investment": 100,
                "max_investment": 3000,
            })
            assert resp.status_code == 200
            assert resp.json()["status"] == "PENDING_VERIFICATION"


class TestInvestmentEndpoints:
    """Test investment-related API endpoints."""

    @pytest.mark.asyncio
    async def test_buy_shares(self):
        from backend.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/investments/buy", json={
                "property_id": 1,
                "investor_address": "INVESTOR1ADDR",
                "quantity": 500,
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["quantity"] == 500
            assert "total_payment" in data

    @pytest.mark.asyncio
    async def test_portfolio(self):
        from backend.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/investments/portfolio/TESTADDR123")
            assert resp.status_code == 200
            assert "holdings" in resp.json()


class TestGovernanceEndpoints:
    """Test governance-related API endpoints."""

    @pytest.mark.asyncio
    async def test_create_proposal(self):
        from backend.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/governance/propose", json={
                "property_id": 1,
                "proposer_address": "PROPOSERADDR",
                "proposal_type": 0,
                "description": "Sell at premium",
                "proposed_value": 65000000,
            })
            assert resp.status_code == 200
            assert resp.json()["status"] == "ACTIVE"

    @pytest.mark.asyncio
    async def test_cast_vote(self):
        from backend.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/governance/vote", json={
                "proposal_id": 1,
                "voter_address": "VOTERADDR",
                "vote_yes": True,
            })
            assert resp.status_code == 200


class TestSettlementEndpoints:

    @pytest.mark.asyncio
    async def test_settlement_status(self):
        from backend.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/settlement/status/1")
            assert resp.status_code == 200
            assert resp.json()["status_label"] == "NOT_STARTED"


class TestScorerUnit:
    """Test the AI scorer directly."""

    def test_approved_documents(self):
        from ai_oracle.scorer import PropertyVerificationScorer
        scorer = PropertyVerificationScorer()
        data = {
            "aadhaar": {"name": "Rajesh Kumar Singh"},
            "sale_deed": {"owner_name": "Rajesh Kumar Singh",
                          "registration_number": "BLR-2020-123456",
                          "registration_date": "12/06/2020",
                          "sub_registrar_office": "Jayanagar"},
            "ec": {"transactions": [], "liabilities": [], "mortgages": [],
                   "period_from": "01/01/2010", "period_to": "31/12/2023"},
            "property_tax": {"owner_name": "Rajesh Kumar Singh",
                             "dues_pending": "0", "last_paid_date": "15/09/2023"},
        }
        result = scorer.score(data)
        assert result.verdict == "APPROVED"
        assert result.score >= 85

    def test_rejected_mortgage(self):
        from ai_oracle.scorer import PropertyVerificationScorer
        scorer = PropertyVerificationScorer()
        data = {
            "aadhaar": {"name": "Rajesh"},
            "sale_deed": {"owner_name": "Suresh", "registration_number": "X",
                          "registration_date": "12/06/2020",
                          "sub_registrar_office": "Y"},
            "ec": {"mortgages": [{"date": "2022"}], "transactions": [], "liabilities": []},
            "property_tax": None,
        }
        result = scorer.score(data)
        assert result.verdict == "REJECTED"
        assert "CRITICAL: EXISTING_MORTGAGE" in result.flags


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
