# vibe_dashboarding_test

Synthetic Data — For Demonstration Only

Open `vibe_dashboarding_test.pbip` in Power BI Desktop, enable the PBIP/PBIR preview features if required by your Desktop version, and refresh the Import model. Before refreshing, set `pMockDataRoot` to your checkout's `data/vibe_dashboarding_test` directory. The committed default is the generic `C:/PowerBI/vibe_dashboard_2026/data/vibe_dashboarding_test` path to avoid exposing a workstation username. Keep machine-specific parameter values and validation outputs local; review exported model files before committing them. The report uses the certified AppSource Deneb visual; Desktop must be able to resolve that visual when opening the project.

Pages: **Performance**, **Engagement**, **Cohort Retention**. All pages use `template_1.jpg`, native slicers and page navigation. The first two pages include native KPI cards, companion monthly sparklines, trend and segment charts, and monthly matrices. The third page includes the Deneb retention heatmap, native cohort enrollment chart and retention population matrix.

Coverage: January 1–June 30, 2026; seed 42; 1,200 anonymous users; 18,000 events. Source schema and six metric definitions are preserved in `config/schema.yaml` and `config/metrics.yaml`. Cohort definitions and additional measures live in `config/vibe_metric_extensions.yaml`. No binary PBIX was edited.

Retention is activity during a calendar month of age, divided by all enrolled users eligible for that observed month. Age zero is not forced to 100%. Future cells are blank. The distinct-user numerator and denominator are recomputed for totals. The retention page filters signup cohorts and segments; it has no activity-month slicer. The native cohort-size chart counts enrollment independently of activity. The heatmap is intentionally not a cross-filter selection source.

## Rebuild and validate

Run from the repository root using Python with pandas/numpy and Node.js 20 or later:

```powershell
python scripts/build_vibe_data_model.py
node scripts/build_vibe_report.cjs
python scripts/validate_data.py --data data/vibe_dashboarding_test --config config/vibe_dashboarding_test.yaml --docs docs/vibe_dashboarding_test
python -m unittest discover -s tests -v
python scripts/validate_project.py
```

The report generator reads the approved `_brief/report-spec.md` and requires the official scaffold already present in this project. To create a fresh project elsewhere, use `powerbi-report-author scaffold` first. Keep existing resource registrations and page IDs.

Local optional tools are ignored by Git. Install the pinned tools from `config/vibe_authoring_tools.json` into `.tools/powerbi`, or install the official CLI on PATH. `scripts/validate_vibe_deneb.cjs` uses the local Vega-Lite and AJV packages. `scripts/validate_vibe_model.ps1` loads the Microsoft Analysis Services NuGet library from `.tools/tom/lib/net8.0`, parses the model and persists it through Microsoft's TMDL serializer. It does not run a DAX engine or refresh.

```powershell
node scripts/validate_vibe_deneb.cjs
./scripts/validate_vibe_model.ps1
powerbi-report-author validate powerbi/vibe_dashboarding_test/vibe_dashboarding_test.Report
```

See `docs/vibe_dashboarding_test/validation_report.md` for verification levels and remaining Desktop checks. The project is authored and structurally validated; stakeholder presentation remains pending actual Import refresh, DAX reconciliation, and all-page screenshot review.
