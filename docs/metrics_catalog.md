# Metric contracts

Synthetic Data — For Demonstration Only

Authoritative definitions are in config/metrics.yaml. This sample contains one row per session/event. Revenue sums integer cents then divides by 100; active users are distinct event UserIds in the current filter. Conversions count converted sessions; conversion rate divides conversions by sessions. ARPU divides revenue by distinct active users. Session length averages non-null minutes.

DAU is distinct event users for one day; WAU/MAU require a defined calendar or rolling window over event rows and cannot be computed by summing daily distinct counts. The sample does not supply retention/funnel measures: define cohort membership, eligibility, observation window and denominator before adding them. Empty denominators yield BLANK in DAX and null in the Python oracle. Keys and session/date filtering must align in both calculations.
