# Preview validation evidence

Synthetic Data — For Demonstration Only

Project: `powerbi/vibe_dashboarding_test/vibe_dashboarding_test.pbip`.

| Check | Status | Evidence |
| --- | --- | --- |
| Six-month source schema, PK/FK, dates, conversions and revenue | PASS | `data_validation.json`; 1,200 users, 181 dates, 18,000 events |
| Additive metric reconciliation and non-additive user contracts | PASS | `reconciliation.json`; total revenue $38,037.79, 1,136 active users, 2,014 conversions, 11.1889% conversion rate |
| Monthly cohort populations by segment | PASS | `cohort_reconciliation.csv`; 42 observed cohort-age-segment cells |
| Repository and retention tests | PASS | `python -m unittest discover -s tests -v`; 14 tests |
| Supplemental project bindings, bounds, page IDs and disclosures | PASS | `../generated_validation/project_validation.json`; zero errors and overlap warnings |
| Official PBIR metadata and online JSON schemas | PASS | `pbir_validation.json`; Microsoft CLI 0.5.0, zero errors and warnings |
| TMDL parse, relationship resolution and Microsoft serializer export | PASS | `tmdl_validation.json`; TOM 19.118.3; five tables, four relationships, 11 measures |
| Vega-Lite official schema and compile | PASS | `deneb_validation.json`; Vega-Lite 5.23.0 |
| Import refresh and M source connectivity | NOT VERIFIED | No reachable Desktop bridge or live model engine |
| DAX evaluation and reconciliation in engine | NOT VERIFIED | TOM parsing does not execute DAX |
| Actual Deneb in-report rendering, interactions, slicers and navigation | NOT VERIFIED | Requires refreshed Desktop model and report rendering |
| All-page screenshot capture and review | NOT VERIFIED | CLI host discovery reports Desktop unavailable; no screenshot evidence fabricated |

Native cards have compact content sizing and companion trends within the approved KPI strip. Detail tables use native matrices with row dimensions and explicit measures to avoid the documented empty table binding issue. Filter pane colors are authored at page level because the installed validator rejects the equivalent wildcard theme keys.

Before presenting, open the PBIP in Desktop, refresh all five Import tables, compare engine measures with the reconciliation files, inspect cohort-age cells including zero and future months, test segment and month slicers, and capture/review all three pages. Python aggregates and external Vega compilation are not evidence of Power BI rendering.

Original sample data, validation docs, background image, and `vibe_dashboarding_test.pbix` were preserved. No publishing, deployment, or push was performed.

Git delivery: local commit on `codex/vibe-dashboarding-test`, authored by Alvin XY Zhang <alvinxyzhang@gmail.com>. Future GitHub destination is the account https://github.com/xiyang-zhang; no repository remote has been specified and no push was performed.

Deneb registration and property encoding follow the [official PBIR integration guide](https://deneb.guide/docs/pbir-guide).
