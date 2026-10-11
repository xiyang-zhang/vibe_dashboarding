# Metrics catalog

Synthetic Data — For Demonstration Only

| Table | Measure | Format | Contract |
| --- | --- | --- | --- |
| Events | Revenue | $#,##0.00 | Sum event revenue cents / 100; zero for nonconversion |
| Events | Active Users | #,##0 | Distinct event users in current filter; non-additive |
| Events | Conversions | #,##0 | Converted eligible sessions |
| Events | Conversion Rate | 0.0% | Converted sessions / eligible sessions; blank if no sessions |
| Events | ARPU | $0.00 | Revenue / distinct active users; blank if no active users |
| Events | Session Length | 0.0 | Mean non-null session minutes |
| Events | Sessions | #,##0 | Eligible event sessions in current filter. |
| Users | Cohort Size | #,##0 | All enrolled users in selected cohort and segment. |
| CohortActivity | Eligible Cohort Users | #,##0 | Distinct enrolled users with an observed age cell; excludes future cohort-age combinations. |
| CohortActivity | Retained Users | #,##0 | Distinct cohort users active in observed age months; zero if observed but inactive, blank if future. |
| CohortActivity | Retention Rate | 0.0% | Distinct retained population / distinct eligible cohort population; totals recompute both sets. |
