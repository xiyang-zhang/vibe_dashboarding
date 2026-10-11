"""Reusable event-grain fixture generation and contract validation."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DISCLOSURE = "Synthetic Data — For Demonstration Only"

def load(path):
    text = Path(path).read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml
        except ImportError as exc:
            raise ValueError("Install PyYAML for non-JSON YAML configuration") from exc
        return yaml.safe_load(text)

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")

def generate(config):
    rng = np.random.default_rng(config["seed"])
    days = pd.date_range(config["start"], config["end"], freq="D")
    n, count = int(config["users"]), int(config["events"])
    if not len(days) or n < 1 or count < 0:
        raise ValueError("Require valid date range, positive users and nonnegative events")
    if config["granularity"] not in {"daily", "weekly", "monthly"}:
        raise ValueError("granularity must be daily, weekly or monthly")
    segments = config["segments"]
    names = list(segments)
    weights = np.array([segments[s]["weight"] for s in names], dtype=float)
    if np.any(weights < 0) or weights.sum() <= 0:
        raise ValueError("Segment weights must be nonnegative with a positive total")
    if any(not 0 <= segments[s]["conversion_rate"] <= 1 or segments[s]["spend_multiplier"] <= 0 for s in names):
        raise ValueError("Invalid conversion rate or spend multiplier")
    null_rate = config.get("session_null_rate", 0)
    if not 0 <= null_rate <= 1:
        raise ValueError("Invalid null rate")
    signup = rng.integers(0, len(days), n)
    signup[0] = 0  # At least one eligible user at the start.
    users = pd.DataFrame({"UserId": np.arange(1, n + 1), "Segment": rng.choice(names, n, p=weights/weights.sum()), "SignupDate": days[signup].strftime("%Y-%m-%d")})
    date = pd.DataFrame({"Date": days.strftime("%Y-%m-%d"), "Year": days.year, "Month": days.month, "MonthName": days.strftime("%B")})
    probability = (1 + np.linspace(0, config.get("growth", 0), len(days))) * np.where(days.dayofweek >= 5, config.get("weekend_multiplier", 1), 1)
    for d, factor in config.get("anomalies", {}).items():
        probability[days == pd.Timestamp(d)] *= factor
    if np.any(probability < 0) or probability.sum() <= 0:
        raise ValueError("Scenario yields invalid date probabilities")
    event_days = rng.choice(len(days), count, p=probability/probability.sum())
    ids = np.array([rng.choice(np.flatnonzero(signup <= d)) for d in event_days], dtype=int)
    segment = users.Segment.to_numpy()[ids]
    converted = np.array([rng.random() < segments[s]["conversion_rate"] for s in segment], dtype=np.int64)
    revenue = np.array([max(1, round(rng.lognormal(7.2, .45) * segments[s]["spend_multiplier"])) if c else 0 for s, c in zip(segment, converted)], dtype=np.int64)
    session = rng.lognormal(2.4, .55, count)
    session[rng.random(count) < null_rate] = np.nan
    events = pd.DataFrame({"EventId": np.arange(1, count + 1), "UserId": ids + 1, "Date": days[event_days].strftime("%Y-%m-%d"), "Converted": converted, "RevenueCents": revenue, "SessionMinutes": np.round(session, 3)})
    return {"Users": users, "Date": date, "Events": events}

def validate(tables, schema):
    errors = []
    for name, spec in schema["tables"].items():
        if name not in tables:
            errors.append(f"Missing table {name}")
            continue
        df = tables[name]
        if set(df.columns) != set(spec["columns"]):
            errors.append(f"{name}: column schema mismatch")
            continue
        pk = spec["primary_key"]
        if df[pk].isna().any() or df[pk].duplicated().any():
            errors.append(f"{name}: null/duplicate primary key")
        for col, dtype in spec["columns"].items():
            values = df[col].dropna()
            if col not in spec.get("nullable", []) and df[col].isna().any():
                errors.append(f"{name}.{col}: unexpected null")
            if dtype in {"int64", "double"}:
                numeric = pd.to_numeric(values, errors="coerce")
                if numeric.isna().any() or not np.isfinite(numeric).all() or (dtype == "int64" and (numeric % 1 != 0).any()):
                    errors.append(f"{name}.{col}: invalid {dtype}")
            elif dtype == "date":
                if pd.to_datetime(values, format="%Y-%m-%d", errors="coerce").isna().any():
                    errors.append(f"{name}.{col}: invalid date")
            elif dtype == "string":
                if not values.map(lambda value: isinstance(value, str)).all():
                    errors.append(f"{name}.{col}: invalid string")
            else:
                errors.append(f"{name}.{col}: unsupported type {dtype}")
    for rel in schema["relationships"]:
        try:
            src = tables[rel["from_table"]][rel["from_column"]]
            dst = tables[rel["to_table"]][rel["to_column"]]
            if rel["cardinality"] != "many-to-one" or dst.duplicated().any():
                errors.append("Invalid relationship cardinality")
            if not src.dropna().isin(dst).all():
                errors.append(f"Orphan foreign key {rel['from_table']}.{rel['from_column']}")
            if schema["tables"][rel["from_table"]]["columns"][rel["from_column"]] != schema["tables"][rel["to_table"]]["columns"][rel["to_column"]]:
                errors.append("Relationship type mismatch")
        except KeyError:
            errors.append("Relationship references missing objects")
    if errors:
        return errors
    e, u = tables["Events"], tables["Users"]
    if not e.Converted.isin([0, 1]).all():
        errors.append("Conversion must be binary and bounded by eligible sessions")
    if (e.RevenueCents < 0).any() or (e.loc[e.Converted == 0, "RevenueCents"] != 0).any() or (e.loc[e.Converted == 1, "RevenueCents"] <= 0).any():
        errors.append("Revenue contradicts conversion")
    if (e.SessionMinutes.dropna() <= 0).any():
        errors.append("Session lengths must be positive")
    joined = e.merge(u, on="UserId")
    if (pd.to_datetime(joined.Date) < pd.to_datetime(joined.SignupDate)).any():
        errors.append("Events precede enrollment")
    dates = pd.to_datetime(tables["Date"].Date).sort_values()
    if not dates.diff().dropna().eq(pd.Timedelta(days=1)).all():
        errors.append("Date dimension has gaps")
    signup = pd.to_datetime(u.SignupDate)
    if not signup.between(dates.min(), dates.max()).all():
        errors.append("Enrollment dates outside date dimension")
    calendar = tables["Date"]
    parsed = pd.to_datetime(calendar.Date)
    if not calendar.Year.eq(parsed.dt.year).all() or not calendar.Month.eq(parsed.dt.month).all() or not calendar.MonthName.eq(parsed.dt.strftime("%B")).all():
        errors.append("Date dimension attributes disagree with dates")
    return errors

def scenario_checks(tables, config):
    """Broad distribution checks, separate from exact metric invariants."""
    events = tables["Events"].merge(tables["Users"], on="UserId")
    checks = []
    for segment, assumption in config["segments"].items():
        sample = events[events.Segment == segment]
        n = len(sample)
        p = assumption["conversion_rate"]
        expected, observed = n * p, int(sample.Converted.sum())
        tolerance = max(5, 5 * np.sqrt(n * p * (1-p)))
        checks.append({"check": f"{segment} conversion distribution", "observations": n, "expected": expected, "actual": observed, "tolerance": float(tolerance), "status": "PASS" if abs(observed-expected) <= tolerance else "FAIL"})
    days = pd.date_range(config["start"], config["end"], freq="D")
    weights = (1 + np.linspace(0, config.get("growth", 0), len(days))) * np.where(days.dayofweek >= 5, config.get("weekend_multiplier", 1), 1)
    for day, factor in config.get("anomalies", {}).items():
        weights[days == pd.Timestamp(day)] *= factor
    weights /= weights.sum()
    counts = events.groupby("Date").size().reindex(days.strftime("%Y-%m-%d"), fill_value=0).to_numpy()
    # Check two halves against configured growth/seasonality, not monotonic daily noise.
    midpoint = max(1, len(days)//2)
    p = weights[:midpoint].sum()
    expected = len(events)*p
    tolerance = max(5, 5*np.sqrt(len(events)*p*(1-p)))
    checks.append({"check": "date trend/seasonality allocation", "expected": float(expected), "actual": int(counts[:midpoint].sum()), "tolerance": float(tolerance), "status": "PASS" if abs(counts[:midpoint].sum()-expected) <= tolerance else "FAIL"})
    return checks

def reconcile(tables, granularity="daily"):
    e = tables["Events"].copy()
    dates = pd.to_datetime(e.Date)
    if granularity == "weekly":
        e["Period"] = (dates - pd.to_timedelta(dates.dt.dayofweek, unit="D")).dt.strftime("%Y-%m-%d")
    elif granularity == "monthly":
        e["Period"] = dates.dt.to_period("M").dt.start_time.dt.strftime("%Y-%m-%d")
    elif granularity == "daily":
        e["Period"] = e.Date
    else:
        raise ValueError("Unsupported granularity")
    aggregates = e.groupby("Period").agg(Sessions=("EventId", "count"), ActiveUsers=("UserId", "nunique"), Conversions=("Converted", "sum"), RevenueCents=("RevenueCents", "sum"))
    revenue, active, conversions = int(e.RevenueCents.sum()) / 100, int(e.UserId.nunique()), int(e.Converted.sum())
    result = {"revenue": revenue, "active_users": active, "conversions": conversions, "sessions": len(e), "conversion_rate": conversions/len(e) if len(e) else None, "arpu": revenue/active if active else None, "session_length": float(e.SessionMinutes.mean()) if e.SessionMinutes.notna().any() else None,
              "additive_reconciliation": bool(aggregates.Sessions.sum() == len(e) and aggregates.RevenueCents.sum() == e.RevenueCents.sum() and aggregates.Conversions.sum() == conversions),
              "distinct_users_are_non_additive": True}
    return result, aggregates

def read_tables(root, schema):
    return {name: pd.read_csv(Path(root)/f"{name}.csv", dtype={c: "string" for c, t in spec["columns"].items() if t in {"string", "date"}}) for name, spec in schema["tables"].items()}
