# Deneb integration

Read https://deneb.guide/docs/pbir-guide before integration, including property encoding and field mapping sections. Certified visual identifier: `deneb7E15AEF80B9E4D4F8E12924291ECE89A` (verified against official guide during setup).

Version specifications in `templates/deneb/`. Prefer Vega-Lite; use Vega for requirements beyond its grammar. `data.name` must be `dataset`; field names must match Deneb's nativeQueryRef/displayName names. Bind every required field in `visual.query.queryState.dataset.projections` using the canonical baseline and CLI schema metadata. Require cohort age/cohort/retention fields for heatmaps; these are not present in the default event sample until derived correctly.

`scripts/deneb.py` patches only a supplied existing Deneb visual, retains its bindings/schema/ID, verifies required field bindings, and serializes spec/config as PBIR Literal text values. It does not invent a visual or register one. Confirm registration/provider/interactions against the installed version and guide. Validate Vega-Lite with its official schema/compiler, then official PBIR validation, then actual in-report rendering. External Vega rendering is not Power BI evidence.
