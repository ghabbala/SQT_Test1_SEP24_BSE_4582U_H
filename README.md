# SQT Practical Project Test 1 – TicketHub QA Package

Black-box QA package for `src/tickethub.py` (TicketHub Order Module v0.9).
The module under test is **unchanged** (sha256 `71e842b2…f722c4a3`; the CI pipeline verifies this).

## Run it (one command)

```bash
make install && make test
```

Without `make`: `python -m pip install -r requirements.txt && python -m pytest -v`

Requires Python 3.10+. `pyproject.toml` puts `src/` and `tests/` on the import path, so no install of the module is needed.

| Command | What it does |
|---|---|
| `make test` | Gated run. Logged defects are strict xfail → **green** while they are open. Writes `ci/junit_report.xml`. |
| `make test-raw` | Raw run (`--runxfail`): ignores the xfail markers, so all 24 failing tests are shown. Writes `ci/junit_report_raw.xml`. |
| `make ci` | Both, in the order the CI pipeline runs them. |

To re-run the same suite against a corrected build: `TICKETHUB_MODULE=<module name> python -m pytest -v`.

## Layout

```
report/       SQT_Test1_Report.docx    Parts A, B, C rationale, D summary, E
test_design/  test_cases.xlsx          72 test cases (Appendix B template) + traceability,
                                       decision table, state table, summary sheets
              cause_effect_graph.png/.dot, state_diagram.png/.dot
src/          tickethub.py             unchanged
tests/        conftest.py              module loading, TC-ID check, known-defect map
              test_pricing.py          TC-01 … TC-41  (EP, BVA, decision table, rounding)
              test_order_lifecycle.py  TC-42 … TC-70  (state transition)
              test_nonfunctional.py    TC-71, TC-72   (rewritten REQ-N1)
defects/      DEF-01.md … DEF-08.md, defect_log.md
ci/           ci.yml (copy of .github/workflows/ci.yml), run logs, JUnit XML reports
.github/workflows/ci.yml               pipeline: runs on every push
Makefile, pyproject.toml, requirements.txt
```

## Traceability conventions

* Every pytest id contains its test case ID, e.g. `test_bva_quantity_range[TC-23-qty-10]`, `test_TC_68_sequence_pay_collect_is_final`. `conftest.py` refuses to collect a test without one.
* Every failure message starts with the TC ID and requirement, e.g. `TC-26 REQ-F4: calculate_discount(5, 'PUBLIC', None) expected rate 0.05, got 0`.
* Money is compared as `Decimal("…")` built from strings, never as floats and never with `approx`, so a 1-cent rounding error fails the test.

## xfail policy

After the first raw execution, each failing test was tied to a logged defect in `KNOWN_DEFECTS` in `tests/conftest.py`, which marks it `xfail(strict=True, reason="DEF-nn (logged)")`.

Why:

1. **The pipeline stays actionable.** With 8 known defects open, a permanently red build hides any *new* failure. With the markers, the gated run is green, and any new failure turns it red.
2. **Fixes are detected.** `strict=True` turns an unexpected pass (XPASS) into a failure, so when a developer fixes a defect the build goes red until the marker is removed and the defect is closed. This was demonstrated: `ci/run3_fixed_build_check.log` runs the suite against a corrected build and all 24 marked tests fail as `XPASS(strict)`.
3. **Nothing is hidden.** The defects are still reported (24 `xfailed` with their DEF-IDs in the summary), and the CI pipeline also runs a raw `--runxfail` step whose log and `junit_report_raw.xml` show every failure.

Tests blocked by DEF-06 (REFUND_PENDING / REFUNDED cannot be reached) fail with a `BLOCKED: precondition failed` message and are marked with DEF-06.

## CI evidence

* `.github/workflows/ci.yml`: on every push and pull request, installs dependencies on Python 3.10 and 3.12, checks the module checksum, runs the raw step (allowed to fail) and the gated step, and uploads both JUnit XML reports as build artifacts.
* `ci/run1_raw_local.log`: raw run showing 24 failed, 50 passed.
* `ci/run2_gated_local.log`: gated run showing 50 passed, 24 xfailed.
* `ci/run3_fixed_build_check.log`: strict-xfail regression check against a corrected build.
* **To add:** export or screenshot of the GitHub Actions run after pushing this repository (`ci/github_actions_run.png`).
