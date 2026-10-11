# Data dictionary

Synthetic Data — For Demonstration Only

| Table | Column | Type | Nullable | Key |
| --- | --- | --- | --- | --- |
| Users | UserId | int64 | False | PK |
| Users | Segment | string | False |  |
| Users | SignupDate | date | False |  |
| Date | Date | date | False | PK |
| Date | Year | int64 | False |  |
| Date | Month | int64 | False |  |
| Date | MonthName | string | False |  |
| Events | EventId | int64 | False | PK |
| Events | UserId | int64 | False |  |
| Events | Date | date | False |  |
| Events | Converted | int64 | False |  |
| Events | RevenueCents | int64 | False |  |
| Events | SessionMinutes | double | True |  |
