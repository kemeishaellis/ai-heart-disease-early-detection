"""Component-level contracts for the 12 nodes in the corrected Session 5 wire diagram.

All patient/reference values are fictional. Two deliberately xfailed tests record
atomic-protocol integration gaps: approved de-identification and a validated
cardiovascular estimator. A green CI run does NOT claim clinical readiness.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest
import session11_workflow as flow


@pytest.fixture
def valid_inputs():
    return {"age": 44, "systolic_bp": 125, "total_cholesterol": 186, "resting_hr": 71}


# 1. De-identify reference cohort (atomic protocol candidate)
@pytest.mark.parametrize("identifier", ["name", "email", "phone", "patient_id", "address"])
def test_01_deidentification_strips_direct_fields(identifier):
    source = {"age": 44, "systolic_bp": 125, "total_cholesterol": 186, identifier: "SENSITIVE"}
    result = flow.deidentify_reference_records([source])
    assert identifier not in result[0]
    assert result[0]["age"] == 44
    assert identifier in source


@pytest.mark.xfail(
    strict=True,
    reason="Pending: replace field removal with a cited, approved de-identification atomic protocol and its unit tests.",
)
def test_01_atomic_deidentification_is_really_approved():
    assert callable(getattr(flow, "approved_reference_deidentification_protocol", None))


# 2. Verify reference data (disposable)
def test_02_reference_quality_keeps_valid_and_counts_bad_rows():
    rows = [{"age": 40, "systolic_bp": 122, "total_cholesterol": 175}, {"age": 55}]
    result = flow.verify_reference_data(rows)
    assert len(result["valid"]) == 1
    assert result["flag_count"] == 1


def test_02_reference_quality_keeps_unusual_values_for_separate_review():
    unusual = {"age": 250, "systolic_bp": 350, "total_cholesterol": 999}
    result = flow.verify_reference_data([unusual])
    assert result["valid"] == [unusual]


@pytest.mark.parametrize("invalid", ["high", None, True])
def test_02_reference_quality_rejects_incompatible_types(invalid):
    row = {"age": invalid, "systolic_bp": 122, "total_cholesterol": 200}
    assert flow.verify_reference_data([row])["flag_count"] == 1


# 3. Approve reference rules (disposable placeholder; demo rules only)
def test_03_rules_preserve_version_and_do_not_generate_clinical_cutoffs():
    reference = flow.verify_reference_data(flow.deidentify_reference_records(flow.DEMO_REFERENCE))
    assert flow.load_demo_standards(reference, flow.DEMO_RULES) is flow.DEMO_RULES
    assert flow.DEMO_RULES["version"] == "demo-v1"


def test_03_rules_reject_empty_reference():
    with pytest.raises(ValueError):
        flow.load_demo_standards({"valid": []}, flow.DEMO_RULES)


def test_03_rules_reject_non_demo_rule_versions():
    with pytest.raises(ValueError):
        flow.load_demo_standards({"valid": [{}]}, {"version": "unapproved"})


# 4. Authorize patient data access (disposable)
@pytest.mark.parametrize("patient_id,consent,purpose", [
    ("P-123", True, "demo"), ("SYN-001", False, "demo"),
    ("SYN-001", True, "marketing"), ("SYN-001", None, "demo"),
])
def test_04_authorization_denies_inappropriate_requests(patient_id, consent, purpose):
    assert flow.authorize_access(patient_id, consent, purpose) is False


def test_04_authorization_accepts_only_synthetic_demo_scope():
    assert flow.authorize_access("SYN-001", True, "demo") is True


# 5. Retrieve patient test and observations (disposable simulated integration)
def test_05_retrieval_returns_observations_without_identifier():
    source = {"patient_id": "SYN-002", "age": 50, "systolic_bp": 120}
    retrieved = flow.retrieve_patient_data(source, True)
    assert retrieved == {"age": 50, "systolic_bp": 120}
    assert "patient_id" in source


def test_05_retrieval_denied_without_permission():
    with pytest.raises(PermissionError):
        flow.retrieve_patient_data(flow.DEMO_PATIENT, False)


# 6. Normalize and validate patient inputs (disposable)
@pytest.mark.parametrize("field,value,expected_bucket", [
    ("age", None, "missing"), ("age", "fifty", "invalid"),
    ("age", True, "invalid"), ("systolic_bp", 999, "flags"),
    ("total_cholesterol", 0, "flags"),
])
def test_06_input_schema_flags_incomplete_invalid_and_unusual(valid_inputs, field, value, expected_bucket):
    row = {**valid_inputs, field: value}
    result = flow.verify_patient_data(row, flow.DEMO_RULES)
    assert field in result[expected_bucket]


def test_06_input_schema_accepts_complete_in_range_records(valid_inputs):
    result = flow.verify_patient_data(valid_inputs, flow.DEMO_RULES)
    assert result["flags"] == []


# 7. Estimate risk (atomic protocol candidate: demo score is not PREVENT)
def test_07_demo_index_is_deterministic_and_nonprobabilistic(valid_inputs):
    validated = flow.verify_patient_data(valid_inputs, flow.DEMO_RULES)
    first = flow.compute_demo_index(validated)
    assert first == flow.compute_demo_index(validated)
    assert isinstance(first, float) and 0 <= first <= 100


def test_07_demo_index_refuses_flagged_measurements(valid_inputs):
    validated = flow.verify_patient_data({**valid_inputs, "age": None}, flow.DEMO_RULES)
    assert flow.compute_demo_index(validated) is None


@pytest.mark.xfail(
    strict=True,
    reason="Pending: integrate a published validated risk protocol for its eligible population and required inputs; demo score is not clinical risk.",
)
def test_07_atomic_clinically_validated_risk_estimator_exists():
    assert callable(getattr(flow, "validated_cardiovascular_risk_estimator", None))


# 8. Route safety and eligibility (disposable)
def test_08_invalid_inputs_always_request_quality_review(valid_inputs):
    validated = flow.verify_patient_data({**valid_inputs, "age": None}, flow.DEMO_RULES)
    assert flow.route_for_review(validated, None, flow.DEMO_RULES) == "quality_review_required"


@pytest.mark.parametrize("bp,route", [(139, "demo_routine"), (140, "clinician_review_required"), (142, "clinician_review_required")])
def test_08_review_threshold_boundaries(valid_inputs, bp, route):
    validated = flow.verify_patient_data({**valid_inputs, "systolic_bp": bp}, flow.DEMO_RULES)
    assert flow.route_for_review(validated, flow.compute_demo_index(validated), flow.DEMO_RULES) == route


# 9. Clinician review placeholder (disposable)
@pytest.mark.parametrize("route,expected", [
    ("clinician_review_required", "awaiting_real_clinician"),
    ("quality_review_required", "awaiting_real_clinician"),
    ("demo_routine", "simulation_only"),
])
def test_09_no_fake_clinician_approval(route, expected):
    assert flow.clinician_review_placeholder(route) == expected


# 10. Explain approved assessment (disposable, simulated text)
@pytest.mark.parametrize("value", [None, 30.0, 99.0])
def test_10_explanation_has_disclaimer_and_correct_score(value):
    msg = flow.explain_result(value, "demo_routine", "simulation_only")
    assert "SYNTHETIC DEMO ONLY" in msg
    assert "Not medical advice" in msg
    assert "not calculated" in msg if value is None else f"{value}/100" in msg


# 11. Deliver summary / audit (disposable local-only output)
def test_11_audit_is_minimal_and_timestamped():
    audit = []
    result = flow.record_output("initial", "Synthetic only", audit)
    assert result == {"phase": "initial", "message": "Synthetic only"}
    assert set(audit[0]) == {"phase", "event", "synthetic", "utc"}
    assert datetime.fromisoformat(audit[0]["utc"]).tzinfo is not None


# 12. Review new wearable observations (disposable simulated device)
def test_12_followup_changes_copy_not_original():
    record = dict(flow.DEMO_PATIENT)
    changed = flow.update_from_wearable(record, True)
    assert changed["resting_hr"] == 79
    assert record["resting_hr"] == 74
    assert "observation_time" not in record


def test_12_followup_rejects_unauthorized_device_request():
    with pytest.raises(PermissionError):
        flow.update_from_wearable(flow.DEMO_PATIENT, False)


# Integration: one command produces two fictional assessments, no identity in audit.
def test_end_to_end_synthetic_only_with_usable_json(tmp_path: Path):
    out = flow.run_workflow(tmp_path)
    saved = json.loads((tmp_path / "session11_report.json").read_text(encoding="utf-8"))
    assert saved["mode"] == "synthetic_classroom_demo"
    assert saved["clinical_use"] is False
    assert [a["phase"] for a in out["assessments"]] == ["initial", "wearable_followup"]
    assert len(saved["audit"]) == 2
    assert "SYN-001" not in json.dumps(saved)
