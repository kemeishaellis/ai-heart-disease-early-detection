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

The API credential reported read-only repository permissions, but subsequent Git HTTPS pushes succeeded. Both assignment branches are now published. The user created the pull requests through GitHub. No protection changes have been made by the agent.

The user saved a protection rule for `main`. The branch API now reports `protected: true`. After deliberate failure commit `b1a41dd8b9acbd86e208d469dfefee80b5c714bf`, both automated runs failed and PR #4's API reported `mergeable_state: blocked`. The user's screenshot shows both failed checks marked **Required** and a disabled **Merge pull request** button. This verifies that failing required tests prevented merging into `main`. The protection-details endpoint remains unavailable to the API credential (HTTP 404); individual rule settings were not read through that endpoint.

| Remote evidence | Result |
| --- | --- |
| Successful workflow run URL | [CI setup push run: success](https://github.com/kemeishaellis/ai-heart-disease-early-detection/actions/runs/42519901862), commit `3eb4978` |
| Failed workflow run URL | [Deliberate failure on push](https://github.com/kemeishaellis/ai-heart-disease-early-detection/actions/runs/42527740163) and [on pull request](https://github.com/kemeishaellis/ai-heart-disease-early-detection/actions/runs/42528626417): both completed with failure for `3e0af06` |
| Recovery workflow run URL | Correction `6a8fe1a`: [push run](https://github.com/kemeishaellis/ai-heart-disease-early-detection/actions/runs/42529943153) and [PR run](https://github.com/kemeishaellis/ai-heart-disease-early-detection/actions/runs/42529947114) both completed successfully |
| Pull request URL | [CI setup PR #3](https://github.com/kemeishaellis/ai-heart-disease-early-detection/pull/3) and [demonstration PR #4](https://github.com/kemeishaellis/ai-heart-disease-early-detection/pull/4), both open |
| Failed required checks block merging | Verified for `b1a41dd` on PR #4: [failed PR run](https://github.com/kemeishaellis/ai-heart-disease-early-detection/actions/runs/42537726653), [failed push run](https://github.com/kemeishaellis/ai-heart-disease-early-detection/actions/runs/42537723115); API state `blocked` and user screenshot showing required failures and disabled merge button |
| Recovery after protected-branch demonstration | Correction `0c4d9fadf0b595f64169fc17693960ebaf31de04` removed the temporary failure; 14 passed locally, exit 0; [PR run](https://github.com/kemeishaellis/ai-heart-disease-early-detection/actions/runs/42538030244) and [push run](https://github.com/kemeishaellis/ai-heart-disease-early-detection/actions/runs/42538026704) both completed successfully |
| Actual weekly run | Not observed |

The initial failure and recovery demonstrated CI detection before protection was configured. After the user saved protection, a new commit (`b1a41dd`, `test: demonstrate failing required check after protecting main`) restored the same temporary assertion. Both GitHub runs failed. The user captured the required-check failures and disabled merge button. Only after that evidence was captured, correction `0c4d9fa` (`test: restore passing suite after protected-branch demonstration`) removed the temporary file and was pushed normally. All original tests remain unchanged. No PR has been merged or branch deleted.

Automatic approval review rejected a credential-authenticated validator download from an unrelated repository. The stated concern was unauthorized credential use for a public download. Validation was completed using a public download without credentials; no approval is needed for that completed alternative.

## Remaining manual steps (repository writer / administrator)

1. Capture the final recovery run and remaining screenshots below. Keep the blocked-merge screenshot already supplied by the user. Do not merge or delete the demonstration branch without the owner's approval.
2. After the owner approves merging CI setup PR #3, verify the `main` badge and a successful `main` run. Confirm manual dispatch is available. After the Monday schedule executes, record its actual run URL and `schedule` event. Do not claim weekly execution before observing it.
3. Add the final badge and schedule evidence when available.

The repository is public, and the user's GitHub settings page confirms its Free plan can enforce protection here. Protection is now saved and merge blocking has been demonstrated.

## Submission screenshot checklist

- [ ] Workflow configuration showing push, PR, Monday cron, installation, and test command.
- [ ] Successful GitHub Actions run showing all 14 existing tests passing and its commit.
- [ ] Failed GitHub Actions run for `3e0af06` showing the intentional assertion error.
- [ ] Demonstration PR showing the failed **required** check and blocked merge panel; include saved `main` protection settings as supporting evidence.
- [ ] README rendering the actual workflow badge after publication to `main`.
- [ ] Optional supporting evidence: corrected commit `6a8fe1a` and its successful run; actual scheduled run when available.
