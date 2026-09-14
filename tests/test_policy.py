import copy
import csv
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
import pandas as pd
from lateness.engine import Policy, analyze, numerical_action, timestamp
from lateness.reporting import plain, write_outputs


PROJECT = Path(__file__).resolve().parents[1]


def fixture(directory):
    """Different route IDs/dates and synthetic timings; not June's expected labels."""
    rows = {
        'routes': [dict(route_id=101, route_name='Synthetic', origin_stop='A', dest_stop='B', scheduled_runtime_min=10, stops_count=2)],
        'stops': [dict(stop_id='a', stop_name='A', lat=19, lon=72.8, route_id=101, seq=1),
                  dict(stop_id='b', stop_name='B', lat=19.01, lon=72.8, route_id=101, seq=2)],
        'trips': [], 'bookings': [], 'gps_pings': []}
    for day in range(1, 4):
        date = f'2026-01-0{day}'
        rows['trips'].append(dict(trip_id=f't{day}', route_id=101, vehicle_id='bus', service_date=date,
                                  scheduled_start=f'{date}T07:00:00+05:30', scheduled_end=f'{date}T07:10:00+05:30', direction='inbound'))
        rows['bookings'].append(dict(booking_id=f'b{day}', trip_id=f't{day}', rider_id=f'r{day}', boarding_stop_id='b',
                                    booked_at=f'2025-12-31T12:00:00+05:30', promised_eta=f'{date}T07:10:00+05:30'))
        pairs = [(i*20, i/30) for i in range(31)] if day < 3 else [(0, 0), (720, .48), (740, .49), (760, .50)]
        for i, (seconds, fraction) in enumerate(pairs):
            event = pd.Timestamp(f'{date}T07:00:00+05:30')+pd.Timedelta(seconds=seconds)
            rows['gps_pings'].append(dict(ping_id=f'p{day}_{i}', vehicle_id='bus', operator_id=5,
                lat=19+.01*fraction, lon=72.8, speed_kmph=5,
                recorded_at=event.isoformat(), received_at=(event+pd.Timedelta(seconds=2)).isoformat()))
    save(directory, rows)
    return rows


def save(directory, tables):
    from lateness.engine import FILES
    for name, rows in tables.items():
        with Path(directory, name+'.csv').open('w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=FILES[name]);w.writeheader();w.writerows(rows)


class ConsequentialRules(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)
        self.rows = fixture(self.path)
        self.policy = Policy(excluded_operators=[7])
        self.asof = '2026-01-03T07:12:45+05:30'

    def tearDown(self):
        self.temp.cleanup()

    def run_case(self, policy=None, asof=None):
        save(self.path, self.rows)
        return analyze(self.path, asof or self.asof, policy or self.policy)

    def test_generic_dates_reference_anchor_and_persistence(self):
        report = self.run_case()
        trip = report['routes'][0]['evaluated_trips'][0]
        self.assertEqual(trip['reference_trips'], {'2026-01-01':'t1', '2026-01-02':'t2'})
        self.assertEqual(report['routes'][0]['verdict'], 'PUSH_LATE 8 min')
        self.assertAlmostEqual(trip['observations'][-1]['median_deficit'], 7+2/3, places=7)
        # Remove the first live origin ping. First observed GPS becomes 07:12, not the clock anchor.
        self.rows['gps_pings'] = [r for r in self.rows['gps_pings'] if r['ping_id'] != 'p3_0']
        rerun = self.run_case()['routes'][0]['evaluated_trips'][0]
        self.assertAlmostEqual(rerun['observations'][-1]['median_deficit'], 7+2/3, places=7)

    def test_future_payload_cannot_change_live_output(self):
        before = plain(self.run_case()['routes'])
        future = dict(self.rows['gps_pings'][-1], ping_id='future', operator_id=7, lat=80, speed_kmph=9000,
                      recorded_at='2026-01-03T07:12:40+05:30', received_at='2026-01-03T07:12:46+05:30')
        self.rows['gps_pings'].append(future)
        self.assertEqual(before, plain(self.run_case()['routes']))

    def test_receipt_boundary_is_inclusive(self):
        self.rows['gps_pings'][-1]['received_at'] = self.asof
        trip = self.run_case()['routes'][0]['evaluated_trips'][0]
        self.assertEqual(trip['latest']['raw']['received_at'], self.asof)

    def test_reused_id_retains_distinct_event(self):
        self.rows['gps_pings'][-1]['ping_id'] = self.rows['gps_pings'][1]['ping_id']
        report = self.run_case()
        self.assertEqual(len(report['gps_audit']['id_collisions']), 1)
        self.assertEqual(report['gps_audit']['retained_rows'], 66)
        self.assertEqual(report['routes'][0]['verdict'], 'PUSH_LATE 8 min')

    def test_duplicate_payload_removed_without_manufacturing_support(self):
        duplicate = dict(self.rows['gps_pings'][-1], ping_id='another-id')
        self.rows['gps_pings'].append(duplicate)
        report = self.run_case()
        self.assertEqual(len(report['gps_audit']['duplicates']), 1)
        self.assertEqual(report['gps_audit']['retained_rows'], 66)
        self.assertEqual(len(report['routes'][0]['evaluated_trips'][0]['observations']), 3)

    def test_malformed_clock_not_corrected(self):
        self.rows['gps_pings'][1]['recorded_at'] = '2026-01-01T06:60:20+05:30'
        report = self.run_case()
        bad = [r for r in report['gps_audit']['quarantined'] if r['reason']=='invalid_or_future_device_time']
        self.assertEqual(len(bad), 1)
        self.assertEqual(bad[0]['raw']['recorded_at'], '2026-01-01T06:60:20+05:30')
        self.assertTrue(pd.isna(timestamp('2026-01-03T07:12:00')))

    def test_teleport_rejected_valid_return_survives(self):
        self.rows['gps_pings'].append(dict(self.rows['gps_pings'][-1], ping_id='jump', lat=20, lon=73.8, speed_kmph=9000,
             recorded_at='2026-01-03T07:12:30+05:30', received_at='2026-01-03T07:12:32+05:30'))
        report = self.run_case()
        rejected = [r for r in report['gps_audit']['quarantined'] if r['reason']=='impossible_position']
        self.assertEqual([r['ping_id'] for r in rejected], ['jump'])
        self.assertEqual(report['routes'][0]['evaluated_trips'][0]['latest']['ping_id'], 'p3_3')
        self.assertEqual(report['routes'][0]['verdict'], 'PUSH_LATE 8 min')

    def test_negative_speed_retains_coordinate(self):
        self.rows['gps_pings'][-1]['speed_kmph'] = -3
        report = self.run_case()
        q = report['routes'][0]['evaluated_trips'][0]['latest']
        self.assertIsNone(q['usable_speed_kmph'])
        self.assertEqual(q['ping_id'], 'p3_3')
        self.assertEqual(report['routes'][0]['verdict'], 'PUSH_LATE 8 min')

    def test_stale_precedes_possible_historical_number(self):
        report = self.run_case(asof='2026-01-03T07:19:00+05:30')
        trip = report['routes'][0]['evaluated_trips'][0]
        self.assertEqual(trip['verdict'], 'CALL_DRIVER')
        self.assertIsNone(trip['observations'][-1]['deficits'])

    def test_short_staleness_withholds_number_without_driver_call(self):
        trip = self.run_case(asof='2026-01-03T07:14:00+05:30')['routes'][0]['evaluated_trips'][0]
        self.assertEqual(trip['verdict'], 'NO_VERDICT')
        self.assertFalse(trip['numerical_eligible'])

    def test_freshness_boundary_and_broken_persistence(self):
        self.assertEqual(self.run_case(asof='2026-01-03T07:13:40+05:30')['routes'][0]['verdict'], 'PUSH_LATE 8 min')
        self.assertEqual(self.run_case(asof='2026-01-03T07:13:41+05:30')['routes'][0]['verdict'], 'NO_VERDICT')
        self.rows['gps_pings'] = [r for r in self.rows['gps_pings'] if r['ping_id'] != 'p3_2']
        self.assertEqual(self.run_case()['routes'][0]['verdict'], 'NO_VERDICT')

    def test_only_excluded_trip_still_has_route_row(self):
        for row in self.rows['gps_pings']:
            row['operator_id'] = 7
        report = self.run_case()
        self.assertEqual(len(report['routes']), 1)
        self.assertEqual(report['routes'][0]['verdict'], 'NO_VERDICT')
        self.assertEqual(report['routes'][0]['excluded_bookings'], 1)

    def test_origin_bound_call_requires_observed_duration(self):
        for row in self.rows['gps_pings']:
            if row['recorded_at'].startswith('2026-01-03'):
                row['lat'] = 19
        trip = self.run_case()['routes'][0]['evaluated_trips'][0]
        self.assertEqual(trip['verdict'], 'CALL_DRIVER')
        self.assertTrue(trip['origin_bound'])
        self.assertIsNone(trip['observations'][-1]['median_deficit'])

    def test_operator_exclusion_retains_route_and_exposure(self):
        self.rows['trips'].append(dict(self.rows['trips'][-1], trip_id='excluded', vehicle_id='other-bus'))
        self.rows['bookings'].append(dict(self.rows['bookings'][-1], booking_id='outside', trip_id='excluded', rider_id='outside-rider'))
        self.rows['gps_pings'].extend([dict(q, vehicle_id='other-bus', operator_id=7, ping_id='x'+q['ping_id'])
                                      for q in list(self.rows['gps_pings']) if q['recorded_at'].startswith('2026-01-03')])
        report = self.run_case()
        self.assertEqual(len(report['routes']), 1)
        route = report['routes'][0]
        self.assertEqual([t['trip_id'] for t in route['evaluated_trips']], ['t3'])
        self.assertEqual(route['excluded_bookings'], 1)
        self.assertEqual(route['verdict'], 'PUSH_LATE 8 min')

    def test_contractual_request_is_annotation_not_evidence(self):
        configured = replace(self.policy, contractual_reporting_requests={'101': {'source':'test contract','requested_lateness_minutes':0,'apply_to_operational_output':False}})
        report = self.run_case(policy=configured)
        self.assertEqual(report['routes'][0]['verdict'], 'PUSH_LATE 8 min')
        self.assertIn('override not applied', report['routes'][0]['note'])

    def test_threshold_persistence_and_rounding_order(self):
        def observations(values):
            return [{'deficits':{'day1':x,'day2':x}, 'median_deficit':x} for x in values]
        self.assertEqual(numerical_action(observations([4.99]*3), 5), 'HOLD')
        self.assertEqual(numerical_action(observations([4.99,5.5,5.5]), 5), 'NO_VERDICT')
        self.assertEqual(numerical_action(observations([5.5]*3), 5), 'PUSH_LATE 6 min')
        self.assertEqual(numerical_action(observations([5.0]*3), 5), 'PUSH_LATE 5 min')

    def test_missing_reference_does_not_become_zero(self):
        self.rows['gps_pings'] = [r for r in self.rows['gps_pings'] if not r['recorded_at'].startswith('2026-01-01')]
        trip = self.run_case()['routes'][0]['evaluated_trips'][0]
        self.assertEqual(trip['verdict'], 'NO_VERDICT')
        self.assertFalse(trip['numerical_eligible'])

    def test_multiple_eligible_trips_do_not_get_arbitrary_numeric_route_push(self):
        self.rows['trips'].append(dict(self.rows['trips'][-1], trip_id='second', vehicle_id='second-bus'))
        self.rows['gps_pings'].extend([dict(q, vehicle_id='second-bus', ping_id='s'+q['ping_id']) for q in list(self.rows['gps_pings']) if q['recorded_at'].startswith('2026-01-03')])
        self.assertEqual(self.run_case()['routes'][0]['verdict'], 'NO_VERDICT')


class AcceptedExtractRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = Policy(**json.loads((PROJECT/'policy.json').read_text()))
        cls.report = analyze(PROJECT/'data', '2026-06-17T07:45:00+05:30', cls.policy)

    def test_expected_actions_and_unrounded_calculations(self):
        expected = {9:('HOLD',-1.3004542202477722,-.6898439524889639,.3778129921035358),
                    11:('CALL_DRIVER',None,None,None),
                    12:('PUSH_LATE 9 min',8.928876281620322,9.180711030620074,10.035137278859047),
                    14:('CALL_DRIVER',None,None,None),17:('CALL_DRIVER',None,None,None),
                    21:('HOLD',-1.7792086093570632,.4634702274766873,-.2824442153782556)}
        for route in self.report['routes']:
            verdict, d1, d2, cross = expected[route['route']]
            self.assertEqual(route['verdict'], verdict)
            o = route['evaluated_trips'][0]['observations'][-1]
            if d1 is None:
                self.assertIsNone(o['deficits'])
            else:
                for actual, want in zip(o['deficits'].values(), [d1, d2]):self.assertAlmostEqual(actual, want, places=8)
                self.assertAlmostEqual(o['timetable_crosscheck'], cross, places=8)
        route21 = next(r for r in self.report['routes'] if r['route']==21)
        self.assertEqual(route21['excluded_bookings'], 6)
        self.assertEqual([t['trip_id'] for t in route21['evaluated_trips']], ['TRIP_018'])

    def test_audit_and_all_consumed_evidence_respect_cutoff(self):
        audit = self.report['gps_audit']
        self.assertEqual(audit['available_rows'], 3814)
        self.assertEqual(len(audit['duplicates']), 1)
        self.assertEqual(len([r for r in audit['quarantined'] if r['reason']=='impossible_position']), 3)
        self.assertEqual(len(audit['excluded_operator_rows']), 40)
        asof = self.report['as_of']
        def walk(value):
            if isinstance(value, dict):
                if isinstance(value.get('received_at'), pd.Timestamp):self.assertLessEqual(value['received_at'], asof)
                for v in value.values():walk(v)
            elif isinstance(value, list):
                for v in value:walk(v)
        walk(self.report['routes'])

    def test_output_has_exactly_one_row_per_route(self):
        with tempfile.TemporaryDirectory() as directory:
            write_outputs(self.report, directory)
            with Path(directory, 'verdicts.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
            self.assertEqual(len(rows), 6)
            self.assertEqual(len(set(r['route'] for r in rows)), 6)
            self.assertTrue(all(r['note'] for r in rows))


if __name__ == '__main__':
    unittest.main()
