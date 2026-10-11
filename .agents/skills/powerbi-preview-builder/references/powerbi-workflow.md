# Power BI authoring

Before metadata work read the installed Microsoft skills. For models read `references/modeling-guidelines.md`, `tmdl-guidelines.md`, `dax-guidelines.md`, and `pbip.md`. Prefer registered modeling MCP; use local TMDL fallback only when the upstream tool selection permits it. `scripts/prepare_model.py` produces structured authoring inputs and correctly typed CSV Power Query expressions, not a purported processed model.

Use existing PBIP as baseline. Otherwise `scripts/tooling.py scaffold <output> --name <name>` delegates to Microsoft's `powerbi-report-author scaffold`; do not hand-invent report JSON. Export the semantic model into the referenced SemanticModel/definition folder, and preserve definition.pbism, definition.pbir, project shortcut, versions and registered resources.

For reports read upstream `references/authoring.md` and relevant topic references end to end. Use CLI capabilities/formatting/schema metadata before authoring. Bind each visual to real model fields; check columns, measures, filters, sorting, tooltips, interactions, slicer behavior and stable IDs. Layout templates are design contracts, not PBIR definitions. Native shape/text background containers may intentionally overlap charts; document those intentional overlaps rather than hiding all overlap warnings.

Register provided image backgrounds and themes using upstream resource guidance. Respect supplied design templates. Sample canvas is 1280×720 with header, four KPI cards, trend, segmentation and breakdown panels, and disclosure footer. Adapt fonts/contrast/titles/navigation to actual audience and data.

Run `scripts/tooling.py validate <report>` after logical batches. Before Desktop preview read upstream preview and screenshot lifecycle references. Check unsaved host state before open/reload; never discard user work. Model reload is not refresh: actually process/refresh Import partitions and execute representative DAX queries. Capture and inspect affected pages (all pages for report-wide edits). Record unavailable host/CLI/model checks as NOT VERIFIED.

No production dashboard is created by setup. `powerbi/` intentionally contains only guidance until a canonical scaffold is available.
