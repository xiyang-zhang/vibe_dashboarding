# vibe_dashboarding_test report specification

Phase: approval_pending

## Report identity and delivery
Local stakeholder preview, saved as `powerbi/vibe_dashboarding_test/vibe_dashboarding_test.pbip`, with matching Report and SemanticModel folders. Audience: stakeholders tracking performance, engagement, and retention. No publication, deployment, or push. Preserve existing `vibe_dashboarding_test.pbix` and all supplied fixtures. Git currently has an unborn `feat/powerbi-preview-builder` branch and untracked supplied files; scope the eventual commit to reviewed deliverables, excluding installed skills and binary PBIX.

## Data and model
Source contracts: `config/schema.yaml` and `config/metrics.yaml`. Generate January 1–June 30, 2026 (six complete calendar months), seed 42, 1,200 anonymous users and 18,000 events, using the existing configured segment conversion, seasonality, growth, null, and anomaly settings. Keep the original fixture by writing to `data/vibe_dashboarding_test/`. Validate all source data before metadata work.

Create a local Import star schema: Events at event grain, Users at user grain, Date at daily grain. Events[UserId] -> Users[UserId] and Events[Date] -> Date[Date], many-to-one, single direction. Hide technical keys, sort month labels chronologically, mark Date appropriately, and use `pMockDataRoot` for typed CSV imports. Report binding: byPath `../vibe_dashboarding_test.SemanticModel`.

Preserve all six contract measures verbatim: Revenue, Active Users, Conversions, Conversion Rate, ARPU, Session Length. Add a Sessions count and cohort helper fields/tables as separately versioned extensions without changing source schemas. Cohort is signup month, age is calendar months since signup, retained users are distinct cohort members with events in that age month, denominator is all enrolled cohort users. Age zero means activity during signup month, so it is not artificially forced to 100%. Unobserved future months are blank; observed months with no activity are zero. Retention totals recompute distinct numerator and cohort denominator. Segment filters apply to numerator and denominator; ordinary activity-date filters do not shrink cohort populations. Cohort page uses signup-cohort selection and the fixed June 30 observation cutoff to avoid ambiguous activity-date filtering.

## Page plan
1. Performance — executive summary: Revenue, Active Users, Conversion Rate and ARPU native cards; monthly revenue trend; revenue by segment; monthly KPI reconciliation table.
2. Engagement — analytical canvas: Sessions, Active Users, Session Length and Conversions native cards; monthly active-user trend; conversion rate by segment; monthly engagement table.
3. Cohort Retention — analytical canvas: Deneb monthly retention heatmap, cohort enrollment column chart, cohort size and age detail table. Heatmap tooltips expose cohort size, retained users and retention rate. Future ages remain unfilled.

All pages have a title, consistent native page navigation, appropriate slicers, accessible chart labels and alt text, and `Synthetic Data — For Demonstration Only`. Cross-filter native visuals within the page. Avoid cross-filtering the heatmap until its denominator behavior is verified.

## Design and tooling
Use supplied `templates/backgrounds/template_1.jpg` on every page. Preserve its aspect ratio (2560 x 1463 canvas); navy panels protect chart readability over orange dots. Segoe UI body, white labels, orange Revenue, cyan Active Users, mint Conversion Rate, lavender ARPU; retention uses a sequential luminance scale with printed percentages. No unsupported custom formatting properties: discover CLI metadata before authoring.

Installed report and modeling skills are present. `powerbi-report-author` and Python are not on PATH; Node is available. Search bundled runtimes and official CLI setup during implementation. No modeling MCP is exposed in the current tool inventory. Desktop, Import refresh, DAX evaluation, PBIR schema validation, and actual report rendering are NOT VERIFIED. Missing tools are limitations to resolve, not evidence of success.

## Canonical design contract

```yaml
{
  "Design Brief": {
    "theme": {
      "user_overrides": "Preserve supplied background asset",
      "base": "Official base theme adapted to template_1"
    },
    "accessibility": {
      "contrast_notes": "Opaque navy plot panels and white labels; numeric percentages supplement heatmap colors.",
      "alt_text_strategy": "Chart purpose, grain and filter context"
    },
    "generated_by": "powerbi-report-cli",
    "color_map": [
      {
        "measure": "Events[Revenue]",
        "color": "#FF7A45"
      },
      {
        "measure": "Events[Active Users]",
        "color": "#61D8F5"
      },
      {
        "measure": "Events[Conversion Rate]",
        "color": "#80E2BA"
      },
      {
        "measure": "Events[ARPU]",
        "color": "#C5A8FF"
      },
      {
        "measure": "Events[Sessions]",
        "color": "#F5C769"
      },
      {
        "measure": "Events[Session Length]",
        "color": "#C5A8FF"
      },
      {
        "measure": "Events[Conversions]",
        "color": "#80E2BA"
      }
    ],
    "design_identity": {
      "tone": "Stakeholder navy",
      "signature": "Orange accents on supplied particle background with readable navy panels"
    },
    "interaction_pattern": {
      "cross_filter_rules": "Native page charts filter their page; retention cohort and segment slicers filter both populations; no activity-date slicer on retention.",
      "drill_targets": []
    },
    "archetype": "Executive Summary",
    "navigation_model": "page_navigator",
    "mode": "greenfield",
    "pages": [
      {
        "page_background": "#10103E",
        "archetype": "Executive Summary",
        "role": "landing",
        "layout_contract": {
          "placements": [
            {
              "text": "Revenue and conversion across six months",
              "region": "header",
              "id": "page_title",
              "kind": "textbox"
            },
            {
              "field_bindings": "Users[Segment]",
              "kind": "slicer",
              "region": "filters",
              "id": "segment_slicer",
              "of": 2,
              "slot": 1,
              "slicer_type": "dropdown"
            },
            {
              "field_bindings": "Date[MonthStart]",
              "kind": "slicer",
              "region": "filters",
              "id": "period_slicer",
              "of": 2,
              "slot": 2,
              "slicer_type": "dropdown"
            },
            {
              "of": 2,
              "kind": "textbox",
              "region": "footer",
              "text": "Synthetic Data — For Demonstration Only",
              "id": "disclosure",
              "slot": 1
            },
            {
              "region": "footer",
              "slot": 2,
              "id": "navigation",
              "of": 2,
              "kind": "pageNavigator"
            },
            {
              "field_bindings": "Events[Revenue]",
              "kind": "cardVisual",
              "id": "kpi_0",
              "slot": 1,
              "region": "kpis",
              "purpose": "What is Revenue in the selected period?",
              "of": 4,
              "color_strategy": "measure_match"
            },
            {
              "field_bindings": "Events[Active Users]",
              "kind": "cardVisual",
              "id": "kpi_1",
              "slot": 2,
              "region": "kpis",
              "purpose": "What is Active Users in the selected period?",
              "of": 4,
              "color_strategy": "measure_match"
            },
            {
              "field_bindings": "Events[Conversion Rate]",
              "kind": "cardVisual",
              "id": "kpi_2",
              "slot": 3,
              "region": "kpis",
              "purpose": "What is Conversion Rate in the selected period?",
              "of": 4,
              "color_strategy": "measure_match"
            },
            {
              "field_bindings": "Events[ARPU]",
              "kind": "cardVisual",
              "id": "kpi_3",
              "slot": 4,
              "region": "kpis",
              "purpose": "What is ARPU in the selected period?",
              "of": 4,
              "color_strategy": "measure_match"
            },
            {
              "field_bindings": {
                "Y": "Events[Revenue]",
                "Category": "Date[MonthStart]"
              },
              "kind": "lineChart",
              "region": "trend",
              "purpose": "How does Revenue change each month?",
              "id": "monthly_trend",
              "color_strategy": "measure_match"
            },
            {
              "field_bindings": {
                "Y": "Events[Revenue]",
                "Category": "Users[Segment]"
              },
              "kind": "clusteredBarChart",
              "region": "segment",
              "purpose": "How does Revenue compare by segment?",
              "id": "segment_comparison",
              "color_strategy": "measure_match",
              "sort_policy": "value_desc"
            },
            {
              "field_bindings": [
                "Date[MonthStart]",
                "Events[Revenue]",
                "Events[Active Users]",
                "Events[Conversion Rate]",
                "Events[ARPU]"
              ],
              "kind": "tableEx",
              "region": "detail",
              "purpose": "What values reconcile the monthly charts?",
              "id": "monthly_detail",
              "sort_policy": "category_asc"
            }
          ],
          "canvas": {
            "snap": 8,
            "gutter": 24,
            "width": 2560,
            "height": 1463,
            "margin": 32
          },
          "grid": {
            "columns": 12,
            "regions": {
              "footer": [
                1,
                12,
                13,
                13
              ],
              "detail": [
                1,
                8,
                13,
                12
              ],
              "header": [
                1,
                1,
                9,
                2
              ],
              "kpis": [
                1,
                2,
                13,
                4
              ],
              "filters": [
                9,
                1,
                13,
                2
              ],
              "trend": [
                1,
                4,
                7,
                8
              ],
              "segment": [
                7,
                4,
                13,
                8
              ]
            },
            "rows": 12
          },
          "space_audit": {
            "placed_cell_count": 132,
            "unplaced_regions": [],
            "largest_region": {
              "name": "detail",
              "pct_of_content": 36.36
            },
            "empty_cell_pct": 0,
            "content_cell_count": 132,
            "balance_rationale": "Compact cards, balanced analysis charts and a full-width reconciliation table fill the template."
          }
        },
        "layout_variant": "A",
        "name": "Performance",
        "variant_rationale": "Compact cards, balanced analysis charts and a full-width reconciliation table fill the template."
      },
      {
        "page_background": "#10103E",
        "archetype": "Analytical Canvas",
        "role": "detail",
        "layout_contract": {
          "placements": [
            {
              "text": "Activity and engagement across six months",
              "region": "header",
              "id": "page_title",
              "kind": "textbox"
            },
            {
              "field_bindings": "Users[Segment]",
              "kind": "slicer",
              "region": "filters",
              "id": "segment_slicer",
              "of": 2,
              "slot": 1,
              "slicer_type": "dropdown"
            },
            {
              "field_bindings": "Date[MonthStart]",
              "kind": "slicer",
              "region": "filters",
              "id": "period_slicer",
              "of": 2,
              "slot": 2,
              "slicer_type": "dropdown"
            },
            {
              "of": 2,
              "kind": "textbox",
              "region": "footer",
              "text": "Synthetic Data — For Demonstration Only",
              "id": "disclosure",
              "slot": 1
            },
            {
              "region": "footer",
              "slot": 2,
              "id": "navigation",
              "of": 2,
              "kind": "pageNavigator"
            },
            {
              "field_bindings": "Events[Sessions]",
              "kind": "cardVisual",
              "id": "kpi_0",
              "slot": 1,
              "region": "kpis",
              "purpose": "What is Sessions in the selected period?",
              "of": 4,
              "color_strategy": "measure_match"
            },
            {
              "field_bindings": "Events[Active Users]",
              "kind": "cardVisual",
              "id": "kpi_1",
              "slot": 2,
              "region": "kpis",
              "purpose": "What is Active Users in the selected period?",
              "of": 4,
              "color_strategy": "measure_match"
            },
            {
              "field_bindings": "Events[Session Length]",
              "kind": "cardVisual",
              "id": "kpi_2",
              "slot": 3,
              "region": "kpis",
              "purpose": "What is Session Length in the selected period?",
              "of": 4,
              "color_strategy": "measure_match"
            },
            {
              "field_bindings": "Events[Conversions]",
              "kind": "cardVisual",
              "id": "kpi_3",
              "slot": 4,
              "region": "kpis",
              "purpose": "What is Conversions in the selected period?",
              "of": 4,
              "color_strategy": "measure_match"
            },
            {
              "field_bindings": {
                "Y": "Events[Active Users]",
                "Category": "Date[MonthStart]"
              },
              "kind": "lineChart",
              "region": "trend",
              "purpose": "How does Active Users change each month?",
              "id": "monthly_trend",
              "color_strategy": "measure_match"
            },
            {
              "field_bindings": {
                "Y": "Events[Conversion Rate]",
                "Category": "Users[Segment]"
              },
              "kind": "clusteredBarChart",
              "region": "segment",
              "purpose": "How does Conversion Rate compare by segment?",
              "id": "segment_comparison",
              "color_strategy": "measure_match",
              "sort_policy": "value_desc"
            },
            {
              "field_bindings": [
                "Date[MonthStart]",
                "Events[Sessions]",
                "Events[Active Users]",
                "Events[Session Length]",
                "Events[Conversions]"
              ],
              "kind": "tableEx",
              "region": "detail",
              "purpose": "What values reconcile the monthly charts?",
              "id": "monthly_detail",
              "sort_policy": "category_asc"
            }
          ],
          "canvas": {
            "snap": 8,
            "gutter": 24,
            "width": 2560,
            "height": 1463,
            "margin": 32
          },
          "grid": {
            "columns": 12,
            "regions": {
              "footer": [
                1,
                12,
                13,
                13
              ],
              "detail": [
                1,
                8,
                13,
                12
              ],
              "header": [
                1,
                1,
                9,
                2
              ],
              "kpis": [
                1,
                2,
                13,
                4
              ],
              "filters": [
                9,
                1,
                13,
                2
              ],
              "trend": [
                1,
                4,
                7,
                8
              ],
              "segment": [
                7,
                4,
                13,
                8
              ]
            },
            "rows": 12
          },
          "space_audit": {
            "placed_cell_count": 132,
            "unplaced_regions": [],
            "largest_region": {
              "name": "detail",
              "pct_of_content": 36.36
            },
            "empty_cell_pct": 0,
            "content_cell_count": 132,
            "balance_rationale": "Compact cards, balanced analysis charts and a full-width reconciliation table fill the template."
          }
        },
        "layout_variant": "A",
        "name": "Engagement",
        "variant_rationale": "Compact cards, balanced analysis charts and a full-width reconciliation table fill the template."
      },
      {
        "page_background": "#10103E",
        "archetype": "Analytical Canvas",
        "role": "detail",
        "layout_contract": {
          "placements": [
            {
              "text": "Retention by signup cohort and month of age",
              "region": "header",
              "id": "page_title",
              "kind": "textbox"
            },
            {
              "field_bindings": "Users[Segment]",
              "kind": "slicer",
              "region": "filters",
              "id": "segment_slicer",
              "of": 2,
              "slot": 1,
              "slicer_type": "dropdown"
            },
            {
              "field_bindings": "Users[SignupCohort]",
              "kind": "slicer",
              "region": "filters",
              "id": "period_slicer",
              "of": 2,
              "slot": 2,
              "slicer_type": "dropdown"
            },
            {
              "of": 2,
              "kind": "textbox",
              "region": "footer",
              "text": "Synthetic Data — For Demonstration Only",
              "id": "disclosure",
              "slot": 1
            },
            {
              "region": "footer",
              "slot": 2,
              "id": "navigation",
              "of": 2,
              "kind": "pageNavigator"
            },
            {
              "field_bindings": [
                "Users[SignupCohort]",
                "CohortAge[Age]",
                "Events[Retained Users]",
                "Users[Cohort Size]",
                "Events[Retention Rate]"
              ],
              "kind": "Deneb",
              "region": "heatmap",
              "purpose": "How does activity retention vary by cohort and age?",
              "id": "retention_heatmap",
              "color_strategy": "semantic"
            },
            {
              "field_bindings": {
                "Y": "Users[Cohort Size]",
                "Category": "Users[SignupCohort]"
              },
              "kind": "clusteredColumnChart",
              "region": "enrollment",
              "purpose": "How large is each enrollment cohort?",
              "id": "cohort_enrollment",
              "color_strategy": "unique",
              "sort_policy": "category_asc"
            },
            {
              "field_bindings": [
                "Users[SignupCohort]",
                "CohortAge[Age]",
                "Users[Cohort Size]",
                "Events[Retained Users]",
                "Events[Retention Rate]"
              ],
              "kind": "tableEx",
              "region": "detail",
              "purpose": "What numerator and denominator explain retention?",
              "id": "cohort_detail",
              "sort_policy": "natural_order"
            }
          ],
          "canvas": {
            "snap": 8,
            "gutter": 24,
            "width": 2560,
            "height": 1463,
            "margin": 32
          },
          "grid": {
            "columns": 12,
            "regions": {
              "footer": [
                1,
                12,
                13,
                13
              ],
              "enrollment": [
                9,
                2,
                13,
                7
              ],
              "detail": [
                9,
                7,
                13,
                12
              ],
              "header": [
                1,
                1,
                9,
                2
              ],
              "heatmap": [
                1,
                2,
                9,
                12
              ],
              "filters": [
                9,
                1,
                13,
                2
              ]
            },
            "rows": 12
          },
          "space_audit": {
            "placed_cell_count": 132,
            "unplaced_regions": [],
            "largest_region": {
              "name": "heatmap",
              "pct_of_content": 60.61
            },
            "empty_cell_pct": 0,
            "content_cell_count": 132,
            "balance_rationale": "Heatmap is the analytical hero; the four-column side rail keeps cohort enrollment and denominators visible."
          }
        },
        "layout_variant": "B",
        "name": "Cohort Retention",
        "variant_rationale": "Heatmap is the analytical hero; the four-column side rail keeps cohort enrollment and denominators visible."
      }
    ],
    "contract_version": 1
  }
}
```

## Validation acceptance
Data PK/FK/type/reconciliation tests; unittest discovery; project checks; official PBIR validation; Vega schema validation; model load, refresh and representative DAX; screenshots reviewed for all three pages. Record each missing check as NOT VERIFIED. Never treat JSON parsing as engine or rendering validation.
