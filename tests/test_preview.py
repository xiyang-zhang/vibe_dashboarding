import copy
import sys
import unittest
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
from previewlib import ROOT, generate, load, reconcile, validate, scenario_checks
from deneb import DENEB, literal, patch
from prepare_model import prepare

class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.cfg = load(ROOT/"config/dashboard.yaml")["generation"]
        self.schema = load(ROOT/"config/schema.yaml")
        self.tables = generate(self.cfg)

    def test_reproducible_and_integrity(self):
        again = generate(self.cfg)
        for name in self.tables:
            pd.testing.assert_frame_equal(self.tables[name], again[name])
        self.assertEqual(validate(self.tables, self.schema), [])

    def test_reject_orphan_duplicate_and_bad_conversion(self):
        for column, value in [("UserId", 9999), ("Converted", 2)]:
            broken = copy.deepcopy(self.tables)
            broken["Events"].loc[0, column] = value
            self.assertTrue(validate(broken, self.schema))
        broken = copy.deepcopy(self.tables)
        broken["Users"].loc[1, "UserId"] = 1
        self.assertTrue(validate(broken, self.schema))

    def test_reject_contradictory_revenue_and_dates(self):
        broken = copy.deepcopy(self.tables)
        broken["Events"].loc[0, ["Converted", "RevenueCents"]] = [0, 99]
        self.assertTrue(validate(broken, self.schema))
        broken = copy.deepcopy(self.tables)
        broken["Events"].loc[0, "Date"] = "2020-01-01"
        self.assertTrue(validate(broken, self.schema))

    def test_grains_reconcile_and_distinct_users(self):
        for grain in ("daily", "weekly", "monthly"):
            totals, buckets = reconcile(self.tables, grain)
            self.assertTrue(totals["additive_reconciliation"])
            self.assertLessEqual(totals["conversions"], totals["sessions"])
            self.assertLessEqual(totals["active_users"], int(buckets.ActiveUsers.sum()))
            self.assertAlmostEqual(totals["conversion_rate"], totals["conversions"]/totals["sessions"])

    def test_empty_events_and_all_null_sessions(self):
        cfg = dict(self.cfg, events=0)
        tables = generate(cfg)
        self.assertEqual(validate(tables, self.schema), [])
        totals, _ = reconcile(tables)
        self.assertIsNone(totals["conversion_rate"])
        self.assertIsNone(totals["arpu"])
        cfg = dict(self.cfg, session_null_rate=1)
        self.assertIsNone(reconcile(generate(cfg))[0]["session_length"])

    def test_bad_config(self):
        with self.assertRaises(ValueError):
            generate(dict(self.cfg, granularity="hourly"))
        with self.assertRaises(ValueError):
            generate(dict(self.cfg, growth=-5))

    def test_deneb_preserves_bindings_and_rejects_missing_fields(self):
        spec = load(ROOT/"templates/deneb/annotated-trend.json")
        visual = {"name": "stable", "visual": {"visualType": DENEB, "query": {"queryState": {"dataset": {"projections": [{"nativeQueryRef": "Date"}, {"nativeQueryRef": "Revenue"}]}}}}}
        result = patch(visual, spec)
        self.assertEqual(result["name"], visual["name"])
        self.assertEqual(result["visual"]["query"], visual["visual"]["query"])
        self.assertNotIn("objects", visual["visual"])
        with self.assertRaises(ValueError):
            patch(visual, load(ROOT/"templates/deneb/retention-heatmap.json"))
        self.assertIn("O''Brien", literal({"title": "O'Brien"})["expr"]["Literal"]["Value"])

    def test_model_inputs_typed_and_parameterized(self):
        model = prepare(self.schema, load(ROOT/"config/metrics.yaml"), Path('C:/Mock "Data"'))
        self.assertIn('""Data""', model["parameter"]["m"])
        events = next(t for t in model["tables"] if t["name"] == "Events")
        self.assertIn("pMockDataRoot", events["m"])
        self.assertIn("Int64.Type", events["m"])
        self.assertIn('"Date", type date', events["m"])
        self.assertIn("UserId", events["hidden_columns"])

    def test_scenario_checks_detect_extreme_distribution(self):
        self.assertTrue(all(c["status"] == "PASS" for c in scenario_checks(self.tables, self.cfg)))
        broken = copy.deepcopy(self.tables)
        broken["Events"]["Converted"] = 1
        self.assertTrue(any(c["status"] == "FAIL" for c in scenario_checks(broken, self.cfg)))

if __name__ == "__main__":
    unittest.main()
