"""Synthetic-only Session 11 heart-disease workflow, NOT for clinical use."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

DEMO_PATIENT = {"patient_id": "SYN-001", "age": 54, "systolic_bp": 142,
                "total_cholesterol": 208, "resting_hr": 74}
DEMO_REFERENCE = [
    {"name": "Fictional A", "age": 52, "systolic_bp": 120, "total_cholesterol": 186},
    {"name": "Fictional B", "age": 67, "systolic_bp": 151, "total_cholesterol": 225},
]
DEMO_RULES = {"version": "demo-v1", "required": ["age", "systolic_bp", "total_cholesterol"],
              "review_bp": 140, "plausible": {"age": (18, 120), "systolic_bp": (60, 250),
                                            "total_cholesterol": (70, 500)}}

# 1: De-identification placeholder (not an approved HIPAA protocol).
def deidentify_reference_records(rows):
    banned = {"name", "email", "phone", "patient_id", "address"}
    return [{k: v for k, v in row.items() if k not in banned} for row in rows]

# 2: Reference-quality screening; do not silently remove unusual values.
def verify_reference_data(rows):
    required = DEMO_RULES["required"]
    def valid(r):
        return all(isinstance(r.get(k), (int, float)) and
                   not isinstance(r.get(k), bool) for k in required)
    return {"valid": [r for r in rows if valid(r)],
            "flag_count": sum(not valid(r) for r in rows)}

# 3: Versioned demonstration standards, never LLM-created medical thresholds.
def load_demo_standards(reference, rules):
    if not reference["valid"] or not rules["version"].startswith("demo-"):
        raise ValueError("Synthetic reference or rules missing")
    return rules

# 4: Restrict tool access to consented synthetic-only test context.
def authorize_access(patient_id, consent, purpose):
    return patient_id.startswith("SYN-") and consent is True and purpose == "demo"

# 5: Simulated EHR retrieval (no network access, credentials or real records).
def retrieve_patient_data(patient, authorized):
    if not authorized:
        raise PermissionError("Synthetic data access denied")
    return {k: v for k, v in patient.items() if k != "patient_id"}

# 6: Validate patient records and flag incomplete, invalid or unusual data.
def verify_patient_data(observations, rules):
    missing = [k for k in rules["required"] if observations.get(k) is None]
    invalid = [k for k in rules["required"] if k not in missing and
               (isinstance(observations[k], bool) or
                not isinstance(observations[k], (int, float)))]
    unusual = [k for k, (low, high) in rules["plausible"].items()
               if isinstance(observations.get(k), (int, float))
               and not isinstance(observations.get(k), bool)
               and not low <= observations[k] <= high]
    return {"values": observations, "flags": missing + invalid + unusual,
            "missing": missing, "invalid": invalid}

# 7: Nonclinical illustrative arithmetic index (not validated or a probability).
def compute_demo_index(validated):
    if validated["flags"]:
        return None
    x = validated["values"]
    return round(min(100, max(0, .5 * x["age"] + .18 * x["systolic_bp"]
                              + .06 * x["total_cholesterol"])), 1)

# 8: Deterministic safety and eligibility decision point.
def route_for_review(validated, score, rules):
    if score is None:
        return "quality_review_required"
    if validated["values"]["systolic_bp"] >= rules["review_bp"]:
        return "clinician_review_required"
    return "demo_routine"

# 9: Human-review placeholder, not a clinician's actual authorization.
def clinician_review_placeholder(route):
    return "awaiting_real_clinician" if route != "demo_routine" else "simulation_only"

# 10: Accessible explanation with clear clinical-use restriction.
def explain_result(score, route, review):
    value = "not calculated" if score is None else str(score) + "/100 (not a probability)"
    return (f"SYNTHETIC DEMO ONLY. Illustrative index: {value}. Route: {route}. "
            f"Review: {review}. Not medical advice.")

# 11: Local output and audit entry without patient identifiers.
def record_output(phase, message, audit):
    audit.append({"phase": phase, "event": "demo_completed", "synthetic": True,
                  "utc": datetime.now(timezone.utc).isoformat()})
    return {"phase": phase, "message": message}

# 12: Synthetic wearable update that feeds back into patient validation.
def update_from_wearable(patient, authorized):
    if not authorized:
        raise PermissionError("Wearable mock access denied")
    return {**patient, "resting_hr": 79, "observation_time": "2026-11-23T00:00:00Z"}

def run_workflow(output_dir=None):
    """Run all twelve stages with initial and mock wearable assessments."""
    reference = verify_reference_data(deidentify_reference_records(DEMO_REFERENCE))
    rules = load_demo_standards(reference, DEMO_RULES)
    authorized = authorize_access(DEMO_PATIENT["patient_id"], True, "demo")
    audit, assessments = [], []
    for phase, patient in (("initial", DEMO_PATIENT),
                           ("wearable_followup", update_from_wearable(DEMO_PATIENT, authorized))):
        observations = retrieve_patient_data(patient, authorized)
        validated = verify_patient_data(observations, rules)
        score = compute_demo_index(validated)
        route = route_for_review(validated, score, rules)
        review = clinician_review_placeholder(route)
        assessments.append(record_output(phase, explain_result(score, route, review), audit))
    result = {"mode": "synthetic_classroom_demo", "clinical_use": False,
              "assessments": assessments, "audit": audit,
              "reference_flags": reference["flag_count"]}
    if output_dir is not None:
        folder = Path(output_dir)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "session11_report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts")
    args = parser.parse_args()
    result = run_workflow(args.output_dir)
    print(f"OK: {len(result['assessments'])} synthetic assessment stages completed")
