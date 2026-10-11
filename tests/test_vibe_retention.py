"""Cohort semantics: observed zero, future blank, distinct event duplicates."""
import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from build_vibe_data_model import cohort_activity

class CohortRetentionTests(unittest.TestCase):
    def setUp(self):
        self.users = pd.DataFrame({'UserId':[1,2,3], 'SignupDate':['2026-01-02','2026-01-20','2026-03-01'], 'Segment':['Standard','Premium','Standard']})
        self.events = pd.DataFrame({'UserId':[1,1,2,3], 'Date':['2026-02-02','2026-02-03','2026-01-25','2026-03-03']})
        self.activity = cohort_activity(self.users, self.events, '2026-03-31')

    def test_duplicates_count_one_retained_user(self):
        jan_age_one = self.activity[(self.activity.UserId.isin([1,2])) & (self.activity.Age==1)]
        self.assertEqual(jan_age_one.Active.sum(),1)
        self.assertEqual(jan_age_one.UserId.nunique(),2)
        self.assertEqual(jan_age_one.Active.sum()/jan_age_one.UserId.nunique(),0.5)

    def test_observed_inactive_population_is_zero(self):
        self.assertEqual(self.activity.loc[(self.activity.UserId==2)&(self.activity.Age==2),'Active'].item(),0)

    def test_future_cells_are_absent(self):
        self.assertEqual(self.activity.loc[self.activity.UserId==3,'Age'].tolist(),[0])

    def test_segment_filters_both_populations(self):
        selected=self.activity.merge(self.users,on='UserId')
        selected=selected[(selected.Segment=='Standard') & (selected.Age==1)]
        self.assertEqual(selected.UserId.nunique(),1)
        self.assertEqual(selected.loc[selected.Active==1,'UserId'].nunique(),1)

    def test_totals_recompute_distinct_populations(self):
        self.assertEqual(self.activity.UserId.nunique(),3)
        self.assertEqual(self.activity.loc[self.activity.Active==1,'UserId'].nunique(),3)
        self.assertGreater(len(self.activity),3)

if __name__ == '__main__': unittest.main()
