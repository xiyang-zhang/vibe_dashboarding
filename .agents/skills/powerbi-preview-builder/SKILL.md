---
name: powerbi-preview-builder
description: Build and maintain synthetic-data Power BI dashboard previews using local data, TMDL semantic models, native PBIR visuals, Deneb, and Git-versioned PBIP projects. Use for reusable setup, dashboard prototypes, refinement, and validation.
---

# Power BI Preview Builder

Act as a senior Power BI developer, analytics engineer, visualization designer, and BI QA engineer. Deliver editable stakeholder previews, reproducible synthetic data, and evidence-based validation.

## Modes

| Mode | Action |
| --- | --- |
| INIT | Inspect repository/tools; prepare reusable config, scripts, templates, docs, and tests. No stakeholder interview or production build is required. |
| GENERATE_DATA | Read [data contracts](references/data-contracts.md); generate seeded datasets, dictionary, reconciliation, and data tests. |
| BUILD_MODEL | Read [Power BI workflow](references/powerbi-workflow.md); use semantic-model-authoring and metric contracts to build/import/export TMDL. |
| BUILD_REPORT | Read [Power BI workflow](references/powerbi-workflow.md); use powerbi-report-cli to author real native interactive visuals. |
| BUILD_DENEB | Read [Deneb integration](references/deneb.md); version the specification and bind it in the report. |
| REFINE | Inspect the existing artifact and user design; change only the relevant data, model, layout, or visuals. |
| VALIDATE | Run available checks following [QA](references/validation.md). |
| PREPARE_PREVIEW | Reconcile metrics, verify disclosure/navigation/slicers, review every affected page, and update validation and stakeholder preview docs. |

For a complete dashboard run requirements/design → data → model → report/Deneb → validation → preview. Infer requirements from supplied artifacts; ask only for missing inputs that block the requested build. Setup/sample fixtures are not a stakeholder dashboard. Honor current user authorization when applying upstream planning procedures; do not add approval gates to already authorized local setup.

## Repository resources

Run scripts from the repository root. `config/*.yaml` contains JSON-compatible YAML (no YAML parser required for shipped examples). Utilities under `scripts/` provide deterministic data generation, validation, semantic-model input preparation, CLI delegation, and Deneb encoding. Use `scripts/tooling.py doctor` to discover tools.

Read the installed `.agents/skills/powerbi-report-cli/SKILL.md` and `.agents/skills/semantic-model-authoring/SKILL.md` before their respective work. If absent, look in `apm_modules/microsoft/skills-for-fabric/skills/`; if still missing, report the dependency and continue independent data/setup work. Do not copy or reimplement Microsoft's metadata tooling.

## Invariants

- Keep every stakeholder report/page disclosure: `Synthetic Data — For Demonstration Only`.
- Preserve primary/foreign keys, metric math, star schema, date grains, and user/cohort grain. Use explicit DAX, correct context, formats, display folders, hidden technical keys, and a configurable `pMockDataRoot` M parameter.
- Prefer native visuals for conventional charts. Never replace requested interactive charts with screenshots, HTML, or SVG. Background panels are decoration, not data visuals.
- Preserve compatible schemas, stable IDs, resource/theme registrations, report/model paths, and baseline structure. Discover supported properties with `powerbi-report-author`; never guess them.
- Keep Deneb JSON separately versioned and use certified AppSource metadata from the official guide.
- JSON parsing and local checks do not establish DAX syntax, refresh success, PBIR schema compliance, or Desktop compatibility. Report each verification level separately. Do not fabricate screenshot evidence.
- Preserve user work; exclude caches/secrets; do not push, publish, or deploy without approval.
