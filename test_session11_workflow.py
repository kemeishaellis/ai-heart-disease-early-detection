"""Unit and integration tests for the Session 11 synthetic workflow."""
import tempfile
from pathlib import Path
import pytest
from session11_workflow import (
    DEMO_PATIENT, DEMO_REFERENCE, DEMO_RULES, deidentify_reference_records,
    verify_reference_data, load_demo_standards, authorize_access,
    retrieve_patient_data, verify_patient_data, compute_demo_index,
    route_for_review, clinician_review_placeholder, explain_result,
    record_output, update_from_wearable, run_workflow,
)

def test_01_deidentify():
    assert "name" not in deidentify_reference_records(DEMO_REFERENCE)[0]

def test_02_reference_quality_flags_missing_rows():
    assert verify_reference_data([{"age": 54}])["flag_count"] == 1

def test_03_standards_are_demonstration_only():
    ref = verify_reference_data(deidentify_reference_records(DEMO_REFERENCE))
    assert load_demo_standards(ref, DEMO_RULES)["version"] == "demo-v1"

def test_04_authorization_requires_consent():
    assert not authorize_access("SYN-001", False, "demo")

def test_05_retrieval_blocks_unauthorized_access():
    with pytest.raises(PermissionError):
        retrieve_patient_data(DEMO_PATIENT, False)

def test_06_missing_data_is_flagged():
    assert "age" in verify_patient_data({"systolic_bp": 120}, DEMO_RULES)["missing"]

def test_07_score_is_explicitly_illustrative():
    assert isinstance(compute_demo_index(verify_patient_data(DEMO_PATIENT, DEMO_RULES)), float)

def test_08_quality_failure_blocks_scoring():
    assert compute_demo_index(verify_patient_data({"age": 50}, DEMO_RULES)) is None

def test_09_clinician_review_is_unperformed():
    assert clinician_review_placeholder("clinician_review_required") == "awaiting_real_clinician"

def test_10_explanation_disclaims_medical_advice():
    assert "Not medical advice" in explain_result(48, "demo_routine", "simulation_only")

def test_11_local_audit_omits_identifiers():
    audit = []
    record_output("initial", "synthetic", audit)
    assert "patient_id" not in str(audit)

def test_12_wearable_followup_is_simulated():
    assert update_from_wearable(DEMO_PATIENT, True)["resting_hr"] == 79

def test_13_end_to_end_two_passes():
    with tempfile.TemporaryDirectory() as folder:
        result = run_workflow(folder)
        assert len(result["assessments"]) == 2
        assert (Path(folder) / "session11_report.json").exists()
        assert not result["clinical_use"]

def test_14_route_review_for_bp_demo_trigger():
    validated = verify_patient_data(DEMO_PATIENT, DEMO_RULES)
    score = compute_demo_index(validated)
    assert route_for_review(validated, score, DEMO_RULES) == "clinician_review_required"
