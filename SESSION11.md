# Session 11: Synthetic heart disease workflow rough draft

This is an educational Python prototype for the heart disease early detection and management workflow. It is **not a clinically validated cardiovascular risk model**, and cannot be used for real patients. All data, consent, device connections and clinician-review stages are simulated. The illustrative score is not a probability.

## One-command end-to-end run

```bash
python session11_workflow.py
```

The command runs a fictional assessment, a simulated wearable update, and a second assessment. The report is saved under `artifacts/session11_report.json` (ignored by git). No external systems or credentials are involved.

## Unit tests

```bash
python -m pip install pytest==9.0.3
python -m pytest test_session11_workflow.py -v
```

GitHub Actions runs both the tests and the complete workflow automatically in `.github/workflows/session11.yml`. Verify the result under the Actions tab before checking the GitHub Actions box in the Session 11 template.

## Component coverage

1. De-identify synthetic reference records
2. Check reference-record data quality
3. Load versioned demonstration comparison rules
4. Authorize access to synthetic patient information
5. Retrieve mocked tests and observations
6. Validate individual patient inputs
7. Calculate explicitly nonclinical illustrative index
8. Route invalid or review-needed input
9. Record a simulated clinician escalation, not a real approval
10. Generate a transparent, nonclinical explanation
11. Generate local output and nonidentifying audit details
12. Simulate wearable follow-up and re-evaluate

These functions are separate for readability. The reference de-identification and clinical risk scoring functions are placeholders, **not implementations of published validated atomic protocols**. This is suitable only as a rough classroom demonstration. Actual clinical integration, validation, access controls and professional review would require separate design and oversight.

## Privacy and limitations

Do not commit protected health information, passwords, tokens, or actual patient-device records. In particular, deleting direct fields does not establish HIPAA de-identification. Simulated EHR and wearable reads are not functioning MCP servers.