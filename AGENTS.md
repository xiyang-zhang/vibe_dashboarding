# Power BI preview development

Use `.agents/skills/powerbi-preview-builder/SKILL.md` for synthetic Power BI prototypes. Repository setup is already authorized; do not ask for dashboard requirements to maintain the scaffolding.

- Read installed `powerbi-report-cli` and `semantic-model-authoring` skills and relevant references before metadata edits. They are in `.agents/skills/` (canonical source: `apm_modules/microsoft/skills-for-fabric/skills/`). Reuse Microsoft's authoring CLI and modeling tools.
- Preserve existing PBIX/PBIP files and user changes. Never directly edit binary PBIX files. Start from an existing or Desktop-generated PBIP, or the official CLI scaffold.
- Keep schemas, metric contracts, layouts, and Deneb specifications in version control. Use feature branches for substantial changes; inspect Git status first. Never push, publish, or deploy without explicit approval.
- All demos must display **Synthetic Data — For Demonstration Only**. Use local synthetic data only.
- Distinct users, cohorts, and ratios are non-additive. Calculate from event/user grains and numerator/denominator contracts, never sum incompatible distinct counts.
- Validate data before model/report work. After report edits run official PBIR validation and rendered screenshot review. Mark unavailable refresh, DAX engine, schema, and rendering checks NOT VERIFIED; JSON parsing alone proves none of them.
- Run `python -m unittest discover -s tests -v` and `python scripts/validate_project.py` for scaffold changes. Do not silently overwrite a baseline or modify installed Microsoft skills.
