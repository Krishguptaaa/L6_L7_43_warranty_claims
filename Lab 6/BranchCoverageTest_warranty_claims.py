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


def test_age_zero_is_valid():
    assert out_of_warranty_charge("basic", 0, "defect", False) == 0


def test_exactly_at_coverage_limit_is_free():
    # excess == 0 -> `excess <= 0` boundary
    assert out_of_warranty_charge("basic", 12, "defect", False) == 0


def test_one_month_over_limit():
    assert out_of_warranty_charge("basic", 13, "defect", False) == 100


def test_registered_non_premium_gets_extra_cover():
    # basic: 12 + 6 = 18 covered, excess 2, defect rate 100
    assert out_of_warranty_charge("basic", 20, "defect", True) == 200


def test_registered_extra_cover_boundary_is_free():
    assert out_of_warranty_charge("basic", 18, "defect", True) == 0


def test_registered_premium_gets_no_extra_cover():
    # premium stays at 36 even if registered, excess 4
    assert out_of_warranty_charge("premium", 40, "defect", True) == 400


def test_unregistered_premium():
    assert out_of_warranty_charge("premium", 40, "defect", False) == 400


def test_defect_small_excess_uses_base_rate():
    assert out_of_warranty_charge("basic", 14, "defect", False) == 200


def test_accidental_small_excess():
    assert out_of_warranty_charge("basic", 14, "accidental", False) == 400


def test_excess_exactly_12_has_no_surcharge():
    # `excess > 12` is strict
    assert out_of_warranty_charge("basic", 24, "defect", False) == 12 * 100


def test_excess_13_gets_surcharge_defect():
    # rate 100 + 50
    assert out_of_warranty_charge("basic", 25, "defect", False) == 13 * 150


def test_excess_large_defect_surcharge():
    assert out_of_warranty_charge("basic", 30, "defect", False) == 18 * 150


def test_excess_large_accidental_surcharge():
    # rate 200 + 50 + 25
    assert out_of_warranty_charge("basic", 30, "accidental", False) == 18 * 275


def test_standard_plan_accidental():
    # standard 24 covered, age 30 -> excess 6, rate 200
    assert out_of_warranty_charge("standard", 30, "accidental", False) == 1200


# ---------- claim_allowed ----------
def test_claim_allowed():
    assert claim_allowed(60, 1, False) is True


def test_recall_within_limit():
    assert claim_allowed(0, 5, True) is True


def test_recall_over_limit():
    assert claim_allowed(0, 6, True) is False


def test_recall_ignores_recent_claim_gap():
    assert claim_allowed(1, 3, True) is True


def test_non_recall_too_soon():
    assert claim_allowed(29, 0, False) is False


def test_non_recall_exactly_30_days():
    assert claim_allowed(30, 2, False) is True


def test_non_recall_too_many_claims():
    assert claim_allowed(30, 3, False) is False


# ---------- sla_status ----------
def test_sla_hardware_on_track_boundary():
    assert sla_status(48, True, False) == "on_track"


def test_sla_hardware_at_risk_upper():
    assert sla_status(47, True, False) == "at_risk"


def test_sla_hardware_at_risk_lower_boundary():
    assert sla_status(36, True, False) == "at_risk"


def test_sla_hardware_critical():
    assert sla_status(35, True, False) == "critical"


def test_sla_software_on_track_boundary():
    assert sla_status(24, False, False) == "on_track"


def test_sla_software_at_risk_boundary():
    assert sla_status(12, False, False) == "at_risk"


def test_sla_software_critical():
    assert sla_status(11, False, False) == "critical"


def test_sla_hardware_priority_on_track():
    # cutoff 72
    assert sla_status(72, True, True) == "on_track"


def test_sla_hardware_priority_at_risk():
    assert sla_status(60, True, True) == "at_risk"


def test_sla_hardware_priority_critical():
    assert sla_status(59, True, True) == "critical"


def test_sla_software_priority_on_track():
    # cutoff 48
    assert sla_status(48, False, True) == "on_track"
