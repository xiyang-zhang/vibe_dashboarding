# Data dictionary

Synthetic Data — For Demonstration Only

| Table | Column | Type | Hidden |
| --- | --- | --- | --- |
| Users | UserId | int64 | True |
| Users | Segment | string | False |
| Users | SignupDate | date | False |
| Users | SignupCohort | date | False |
| Date | Date | date | False |
| Date | Year | int64 | False |
| Date | Month | int64 | False |
| Date | MonthName | string | False |
| Date | MonthStart | date | False |
| Events | EventId | int64 | True |
| Events | UserId | int64 | True |
| Events | Date | date | True |
| Events | Converted | int64 | False |
| Events | RevenueCents | int64 | False |
| Events | SessionMinutes | double | False |
| CohortActivity | UserId | int64 | True |
| CohortActivity | Age | int64 | True |
| CohortActivity | Active | int64 | True |
| CohortAge | Age | int64 | False |
