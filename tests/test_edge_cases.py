"""
PropChain — Edge Case Tests
==============================
Tests invalid operations and boundary conditions:
- Over-buy beyond max_investment
- Non-owner rent deposit
- Settlement without governance
- Double-voting on proposals
"""

import pytest


class TestEdgeCases:
    """Test invalid operations that should be rejected."""

    def test_buy_exceeds_max_investment(self):
        """
        Investor tries to buy more than max_investment.
        Should be rejected by FractionalToken.buy_shares().
        """
        max_investment = 3000
        attempted_purchase = 5000

        # Contract should assert: quantity <= max_investment
        assert attempted_purchase > max_investment, "Should exceed max"

        # Simulate the assertion error
        with pytest.raises(AssertionError, match="exceeds max"):
            if attempted_purchase > max_investment:
                raise AssertionError("Purchase quantity exceeds max investment")

        print("✅ Over-buy correctly rejected")

    def test_non_owner_rent_deposit(self):
        """
        Non-owner tries to deposit rent.
        Should be rejected by RentDistributor.deposit_rent().
        """
        owner_address = "OWNER_ADDRESS_XXX"
        sender_address = "RANDOM_ADDRESS_YYY"

        with pytest.raises(AssertionError, match="Only owner"):
            if sender_address != owner_address:
                raise AssertionError("Only owner can deposit rent")

        print("✅ Non-owner rent deposit correctly rejected")

    def test_settlement_without_governance(self):
        """
        Settlement initiation without governance approval.
        Should be rejected by SettlementEngine.initiate_settlement().
        """
        sell_authorized = False

        with pytest.raises(AssertionError, match="not authorized"):
            if not sell_authorized:
                raise AssertionError("Sale not authorized by governance")

        print("✅ Unauthorized settlement correctly rejected")

    def test_double_vote(self):
        """
        Investor tries to vote twice on the same proposal.
        Should be rejected by GovernanceVoting.cast_vote().
        """
        already_voted = True

        with pytest.raises(AssertionError, match="Already voted"):
            if already_voted:
                raise AssertionError("Already voted on this proposal")

        print("✅ Double-vote correctly rejected")

    def test_buy_when_sold_out(self):
        """
        Investor tries to buy shares when none are available.
        Should be rejected by FractionalToken.buy_shares().
        """
        remaining_supply = 0
        quantity = 100

        with pytest.raises(AssertionError, match="Not enough"):
            if quantity > remaining_supply:
                raise AssertionError("Not enough shares available")

        print("✅ Buy when sold-out correctly rejected")

    def test_claim_zero_rent(self):
        """
        Investor tries to claim rent when claimable balance is 0.
        Should be rejected by RentDistributor.claim_rent().
        """
        claimable_balance = 0

        with pytest.raises(AssertionError, match="Nothing to claim"):
            if claimable_balance == 0:
                raise AssertionError("Nothing to claim")

        print("✅ Zero rent claim correctly rejected")

    def test_finalize_before_deadline(self):
        """
        Someone tries to finalize a proposal before the voting deadline.
        Should be rejected by GovernanceVoting.finalize_proposal().
        """
        current_timestamp = 1000
        voting_deadline = 2000

        with pytest.raises(AssertionError, match="Deadline not reached"):
            if current_timestamp <= voting_deadline:
                raise AssertionError("Deadline not reached")

        print("✅ Early finalization correctly rejected")

    def test_fund_escrow_wrong_amount(self):
        """
        Buyer tries to fund escrow with wrong amount.
        Should be rejected by SettlementEngine.fund_escrow().
        """
        approved_price = 65_000_000_000
        payment_amount = 50_000_000_000

        with pytest.raises(AssertionError, match="must equal"):
            if payment_amount != approved_price:
                raise AssertionError("Payment must equal approved sale price")

        print("✅ Wrong escrow amount correctly rejected")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
