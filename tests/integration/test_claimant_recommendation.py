from types import SimpleNamespace

from mediguard.ai.agents import recommend_next_steps
from mediguard.ui.claim_pages import _claimant_outcome_status, _claimant_recommendations


def test_possible_discrepancy_recommendation_points_to_comparison_and_appeal():
    comparison = SimpleNamespace(status="possible_discrepancy", possible_difference=2700)
    recommendations = _claimant_recommendations(
        {"status": "partially_approved"}, {"status": "partially_approved"}, comparison
    )
    assert recommendations[0] == (
        "The settlement differs from the policy-based estimate by INR 2,700.00. "
        "Review the Settlement comparison below and check the appeal draft."
    )
    assert not any("No action is needed" in item for item in recommendations)


def test_current_manual_comparison_overrides_claimant_headline():
    comparison = SimpleNamespace(status="manual_review")
    assert _claimant_outcome_status(
        {"status": "partially_approved", "amount_excluded_or_limited": 12000},
        comparison,
    ) == "manual_review"


def test_possible_discrepancy_comparison_overrides_coverage_headline():
    comparison = SimpleNamespace(status="possible_discrepancy")
    assert _claimant_outcome_status(
        {"status": "partially_approved", "amount_excluded_or_limited": 12000},
        comparison,
    ) == "possible_discrepancy"


def test_no_discrepancy_headline_reflects_policy_limits():
    comparison = SimpleNamespace(status="no_discrepancy")
    limited = {
        "status": "partially_approved",
        "amount_billed": 47000,
        "amount_excluded_or_limited": 12000,
    }
    fully_eligible = {
        "status": "approved",
        "amount_billed": 47000,
        "amount_excluded_or_limited": 0,
    }
    assert _claimant_outcome_status(limited, comparison) == "partially_approved"
    assert _claimant_outcome_status(fully_eligible, comparison) == "approved"


def test_rejection_guidance_uses_only_the_current_claim_rejection():
    similar_claim_flag = {
        "status": "partially_approved",
        "history_flags": [{"note": "a different claim was rejected"}],
    }
    current_rejection = {"status": "rejected"}
    recommendations = recommend_next_steps(
        {"status": "partially_approved"}, similar_claim_flag
    )
    assert not any("past rejected claim" in item for item in recommendations)

    recommendations = recommend_next_steps(
        {"status": "rejected"}, current_rejection
    )
    assert any("past rejected claim" in item for item in recommendations)

    recommendations = recommend_next_steps(
        {"status": "partially_approved"},
        {"status": "partially_approved", "rejection_record": {"status": "denied"}},
    )
    assert any("past rejected claim" in item for item in recommendations)
