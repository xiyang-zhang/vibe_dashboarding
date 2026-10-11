# Validation levels

Run `python scripts/generate_mock_data.py`, `python scripts/validate_data.py`, `python -m unittest discover -s tests -v`, and `python scripts/validate_project.py` for the shipped fixture.

Local data checks are executable and block on failures. Project checks parse JSON, inspect report-model references, page/visual identifiers, bounds and overlap, and obvious model bindings. These are supplemental checks, not a TMDL parser or DAX engine. Invoke the official CLI when installed; retain exit code/diagnostics and never convert a failed command into a pass.

Use separate evidence statuses: PASS, FAIL, NOT VERIFIED, NOT APPLICABLE. Record command, artifact path, and limitations in docs/validation_report.md. Vega schema checks need the official schema; PBIR requires Microsoft validator; TMDL/DAX need supported model tools; refresh/connectivity and rendering need Desktop or an explicitly authorized supported service host. Missing projects are NOT APPLICABLE during INIT, not valid reports. Failed checks must cause a nonzero exit.

For stakeholder previews check all pages and chart results against Python aggregates, source connectivity, metric filters, slicers, report interactions, blank visuals, clipped text, navigation and disclosure. Store only genuine screenshots. `docs/stakeholder_preview.md` must list remaining NOT VERIFIED checks before presentation.
