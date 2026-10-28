import pytest
from warranty_claims import out_of_warranty_charge, claim_allowed, sla_status


# ---------- out_of_warranty_charge ----------
def test_within_warranty():
    assert out_of_warranty_charge("standard", 20, "defect", False) == 0


def test_unknown_plan_raises():
    with pytest.raises(ValueError, match="unknown plan"):
        out_of_warranty_charge("gold", 10, "defect", False)


def test_negative_age_raises():
    with pytest.raises(ValueError, match="invalid age"):
        out_of_warranty_charge("basic", -1, "defect", False)


def test_registered_non_premium_gets_extra_cover():
    # basic: 12 + 6 = 18 covered, excess 2, defect rate 100
    assert out_of_warranty_charge("basic", 20, "defect", True) == 200


def test_accidental_small_excess():
    # basic: 12 covered, excess 2, accidental rate 200
    assert out_of_warranty_charge("basic", 14, "accidental", False) == 400


def test_accidental_large_excess_surcharge():
    # excess 18 > 12 -> rate 200 + 50 + 25 = 275
    assert out_of_warranty_charge("basic", 30, "accidental", False) == 18 * 275


# ---------- claim_allowed ----------
def test_claim_allowed():
    assert claim_allowed(60, 1, False) is True


def test_recall_claim_allowed():
    assert claim_allowed(0, 5, True) is True


def test_claim_too_soon_after_last():
    assert claim_allowed(10, 0, False) is False


# ---------- sla_status ----------
def test_sla_on_track_hardware():
    assert sla_status(60, True, False) == "on_track"


def test_sla_at_risk_software_priority():
    # software priority cutoff = 48, at_risk window is 36..47
    assert sla_status(40, False, True) == "at_risk"


def test_sla_critical():
    assert sla_status(0, False, False) == "critical"
