# Session 8: GitHub Actions assignment evidence

## Repository inspection

- Repository: `kemeishaellis/ai-heart-disease-early-detection`.
- URL: https://github.com/kemeishaellis/ai-heart-disease-early-detection
- Default branch: `main`, confirmed using `git ls-remote --symref origin HEAD` and the GitHub API. Remote baseline: `ccb3d9a0a8f6f8f057d716d851068b5c9f45445f`.
- Existing tracked structure: `.gitignore`, `README.md`, `requirements.txt`, `test_your_protocol.py`, and `docs/wire_diagram.png`. No existing GitHub Actions or other tracked CI configuration was present.
- This is a Python educational design project with pytest tests of scikit-learn KMeans; no web framework or separate application implementation was found.
- Existing dependencies are unchanged: pytest 9.0.3, NumPy 2.4.6, SciPy 1.18.0, and scikit-learn 1.9.0, installed using `requirements.txt`.
- Original checkout: `add-wire-diagram`. Implementation branch: `ci/unit-tests`, created from current `origin/main`. Existing untracked file `tatus` was left untouched.

## Existing tests and commands

All 14 existing tests are in `test_your_protocol.py`:

```text
test_two_clear_clusters
test_output_array_shape_dtype
test_cluster_centers
test_fit_returns_self
test_predict_new_points
test_single_cluster
test_duplicate_records
test_single_feature
test_synthetic_healthcare_metrics
test_empty_input_raises
test_nan_input_raises
test_non_numeric_input_raises
test_too_many_clusters_raises
test_predict_before_fit_raises
```

The assignment's example `test_deidentify.py` does not exist here.

```bash
python -m pip install -r requirements.txt
python -m pytest -v
```

Local PowerShell verification used the existing environment explicitly:

```powershell
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m pytest -v
& .\.venv\Scripts\python.exe -m pip check
```

Runtime: Python 3.14.8 on Windows. The system Python initially lacked scikit-learn; the existing virtual environment has the exact required packages and passes `pip check`. No dependencies or test expectations needed changing. Pytest emitted a nonfatal warning because it could not write the pre-existing `.pytest_cache` directory; test results and exit codes were unaffected.

## Workflow and README

Workflow: [`.github/workflows/tests.yml`](.github/workflows/tests.yml), named `Unit tests`.

| Requirement | Implementation |
| --- | --- |
| Every push | Unfiltered `push` trigger |
| Pull requests to default branch | `pull_request` with `branches: [main]` |
| Weekly execution | `0 6 * * 1`: every Monday |
| Manual execution | `workflow_dispatch` |
| Runtime and installation | Ubuntu 24.04, Python 3.14, pip installs existing `requirements.txt` |
| Complete suite and failure propagation | `python -m pytest -v`; no failure suppression or test exclusions |
| Security | `contents: read`, official actions pinned to full commit SHAs, checkout credentials not persisted, 10-minute timeout |

The workflow passes actionlint 1.7.12 with exit code 0 and no diagnostics. The public validator archive was downloaded without credentials and checked against its published SHA-256 checksum. Official action references were resolved using `git ls-remote`. `git diff --check` passed.

The status badge is immediately below the title in [README.md](README.md), line 3. It uses the actual owner, repository, `tests.yml`, and `main`:

```markdown
[![Unit tests](https://github.com/kemeishaellis/ai-heart-disease-early-detection/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/kemeishaellis/ai-heart-disease-early-detection/actions/workflows/tests.yml?query=branch%3Amain)
```

The URL components and target were checked; a rendered passing badge is not yet verified. It requires publishing the workflow to `main` and a completed run there.

Scheduled workflows execute from the default branch, so this schedule becomes active after an approved merge to `main`. A valid cron expression does not prove a scheduled run occurred. No scheduled execution was observed; verify an actual `schedule` event in Actions after GitHub runs it. GitHub may delay scheduled runs. Manual dispatch also requires the workflow to be present on the default branch.

References: [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

## Local failure and recovery evidence

| Stage | Branch / commit | Observed local result |
| --- | --- | --- |
| Passing baseline and CI setup | `ci/unit-tests`, `8a52e0d` | 14 passed, exit 0 |
| Deliberate broken commit | `test/intentional-ci-failure`, `3e0af063183e54a742488e42dbc423e808cd0fdb` | 1 failed, 14 passed, exit 1 |
| Correction on same branch | `test/intentional-ci-failure`, `6a8fe1a6be69b9541eb72a7c1bbf06a22aa4fc27` | 14 passed, exit 0 |

Broken commit message: `test: deliberately fail CI to demonstrate required checks`.

The temporary `test_intentional_ci_failure.py` added this clearly identified test:

```python
def test_intentional_ci_failure():
    assert False, "Intentional CI failure: verify required checks block merging."
```

Exact failure:

```text
AssertionError: Intentional CI failure: verify required checks block merging.
test_intentional_ci_failure.py:5: AssertionError
```

Correction message: `test: remove deliberate CI failure after demonstration`. The temporary test was removed; all original tests are unchanged. Both commits remain available in local branch history. Neither commit was merged into `main`. Final working branch is `ci/unit-tests`.

## GitHub verification and limitations

GitHub API access using the stored credential reported `pull: true`, `push: false`, `admin: false`, `maintain: false`, and `triage: false`. Consequently no branches were published and no PR or protection changes were attempted with this read-only credential.

The `main` branch API reported `protected: false`; the protection-details endpoint returned HTTP 404. Required checks do **not currently protect main** according to the observed branch state. This assignment's merge-blocking requirement remains incomplete until an administrator configures and verifies it.

| Remote evidence | Result |
| --- | --- |
| Successful workflow run URL | Not verified; workflow has not been published by this session |
| Failed workflow run URL | Not verified; intentional failure was demonstrated locally only |
| Recovery workflow run URL | Not verified |
| Pull request URL | No PR created |
| Failed required checks block merging | Not configured or demonstrated remotely |
| Actual weekly run | Not observed |

No workflow run URLs, PR URLs, screenshots, or hosted success results have been fabricated. The implementation and demonstration commits are local.

Automatic approval review rejected a credential-authenticated validator download from an unrelated repository. The stated concern was unauthorized credential use for a public download. Validation was completed using a public download without credentials; no approval is needed for that completed alternative.

## Remaining manual steps (repository writer / administrator)

1. Authenticate an account with write access to this repository and permission to publish workflow files. For an HTTPS classic token, the `workflow` scope is needed in addition to the applicable repository access. An administrator is needed for branch protection; never paste tokens into this evidence file or chat.
2. Publish the implementation branch:

   ```bash
   git push -u origin ci/unit-tests
   ```

   In GitHub, open a PR with base `main` and compare `ci/unit-tests`. Wait for `Unit tests (Python 3.14)` to succeed, then record its actual run URL. Leave the PR unmerged pending the owner's approval.
3. Configure protection: repository **Settings > Branches > Add branch protection rule**, branch name pattern `main`. Enable **Require a pull request before merging**, **Require status checks to pass before merging**, select the exact check **Unit tests (Python 3.14)** from GitHub Actions, and enable **Require branches to be up to date before merging**. Enable **Do not allow bypassing the above settings** so administrators are also covered. Keep force pushes and deletions disabled. Save, preserving any other existing restrictions. If the check is not listed, first complete a CI run, then return to select it. Re-read the saved rule to verify enforcement.
4. Publish the already-created broken commit first, without resetting a local branch or force-pushing:

   ```bash
   git push origin 3e0af063183e54a742488e42dbc423e808cd0fdb:refs/heads/test/intentional-ci-failure
   ```

   This assumes the demonstration branch does not already exist remotely. If it does, inspect its history before proceeding; do not force-push. Open a PR with base `main` and compare `test/intentional-ci-failure`. Wait for the pull-request test job to fail, record the actual run URL and error, and capture the failed required check and blocked merge panel. Verify the failure itself is a required blocker; do not click merge or bypass protection.
5. Only after capturing failure evidence, publish the existing correction as a normal fast-forward update:

   ```bash
   git push origin test/intentional-ci-failure:refs/heads/test/intentional-ci-failure
   ```

   Wait for the new push and PR runs to pass and record the recovery URL. Do not merge or delete the demonstration branch without the owner's approval.
6. After the owner approves merging the implementation PR, verify the `main` badge and a successful `main` run. Confirm manual dispatch is available. After the next Monday schedule executes, record its actual run URL and `schedule` event. Do not claim weekly execution before observing it.
7. Replace the unverified entries above with the observed URLs/results and capture the screenshots below.

GitHub documents protected branches as available for public repositories on GitHub Free; private repositories require an eligible paid plan. If settings are unavailable, ask the repository owner to configure the rule and check the plan. This session's confirmed limitation is the credential's lack of write/admin permission, rather than a verified plan limitation.

## Submission screenshot checklist

- [ ] Workflow configuration showing push, PR, Monday cron, installation, and test command.
- [ ] Successful GitHub Actions run showing all 14 existing tests passing and its commit.
- [ ] Failed GitHub Actions run for `3e0af06` showing the intentional assertion error.
- [ ] Demonstration PR showing the failed **required** check and blocked merge panel; include saved `main` protection settings as supporting evidence.
- [ ] README rendering the actual workflow badge after publication to `main`.
- [ ] Optional supporting evidence: corrected commit `6a8fe1a` and its successful run; actual scheduled run when available.
