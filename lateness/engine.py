"""Evidence-first analysis; no dates, route outcomes or ping IDs are special-cased."""
from dataclasses import dataclass, field, asdict
from pathlib import Path
import hashlib
import math
import numpy as np
import pandas as pd


FILES = {
    'routes': ['route_id', 'route_name', 'origin_stop', 'dest_stop', 'scheduled_runtime_min', 'stops_count'],
    'stops': ['stop_id', 'stop_name', 'lat', 'lon', 'route_id', 'seq'],
    'trips': ['trip_id', 'route_id', 'vehicle_id', 'service_date', 'scheduled_start', 'scheduled_end', 'direction'],
    'bookings': ['booking_id', 'trip_id', 'rider_id', 'boarding_stop_id', 'booked_at', 'promised_eta'],
    'gps_pings': ['ping_id', 'vehicle_id', 'operator_id', 'lat', 'lon', 'speed_kmph', 'recorded_at', 'received_at'],
}


@dataclass
class Policy:
    freshness_seconds: float = 60
    materiality_minutes: float = 5
    persistence_points: int = 3
    persistence_gap_seconds: float = 30
    verification_gap_seconds: float = 300
    origin_radius_m: float = 100
    origin_duration_minutes: float = 5
    reference_gap_seconds: float = 60
    history_days: int = 2
    position_stress_m: float = 100
    excluded_operators: list = field(default_factory=list)
    contractual_reporting_requests: dict = field(default_factory=dict)

    def __post_init__(self):
        for name in ('freshness_seconds', 'materiality_minutes', 'persistence_gap_seconds',
                     'verification_gap_seconds', 'origin_radius_m', 'origin_duration_minutes',
                     'reference_gap_seconds', 'position_stress_m'):
            if not math.isfinite(getattr(self, name)) or getattr(self, name) <= 0:
                raise ValueError(f'{name} must be positive and finite')
        if self.history_days != 2 or self.persistence_points != 3:
            raise ValueError('This policy requires two historical days and three persistence points')
        if any(x.get('apply_to_operational_output', False)
               for x in self.contractual_reporting_requests.values()):
            raise ValueError('Contractual values cannot overwrite operational evidence')


def timestamp(value):
    """Never localize naive input or repair invalid clock fields."""
    try:
        result = pd.Timestamp(value)
        return result.tz_convert('Asia/Kolkata') if result.tzinfo is not None else pd.NaT
    except (TypeError, ValueError, OverflowError):
        return pd.NaT


def finite(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def distance_km(lat1, lon1, lat2, lon2):
    a, b, c, d = map(np.radians, [lat1, lon1, lat2, lon2])
    h = np.sin((c-a)/2)**2 + np.cos(a)*np.cos(c)*np.sin((d-b)/2)**2
    return float(6371 * 2 * np.arcsin(np.sqrt(np.clip(h, 0, 1))))


class Geometry:
    def __init__(self, stops):
        self.stops = stops.sort_values('seq')
        lat = np.radians(self.stops.lat.mean())
        self.scale_x = 111.195*np.cos(lat)
        self.xy = np.column_stack([self.stops.lon.to_numpy()*self.scale_x,
                                   self.stops.lat.to_numpy()*111.195])
        self.vectors = np.diff(self.xy, axis=0)
        self.lengths = np.linalg.norm(self.vectors, axis=1)
        if len(self.lengths) == 0 or (self.lengths <= 0).any():
            raise ValueError('Route needs at least two distinct sequential stops')
        self.cumulative = np.r_[0, np.cumsum(self.lengths)]
        self.length = float(self.cumulative[-1])
        self.fractions = dict(zip(self.stops.stop_id, self.cumulative/self.length))

    def project(self, lat, lon):
        point = np.array([lon*self.scale_x, lat*111.195])
        fraction = np.clip(((point-self.xy[:-1])*self.vectors).sum(axis=1)/self.lengths**2, 0, 1)
        feet = self.xy[:-1] + fraction[:, None]*self.vectors
        offsets = np.linalg.norm(point-feet, axis=1)
        k = int(offsets.argmin())
        origin = self.stops.iloc[0]
        return (float(self.cumulative[k] + fraction[k]*self.lengths[k]),
                float(offsets[k]), distance_km(lat, lon, origin.lat, origin.lon)*1000)


def load(data_dir):
    tables, manifest = {}, {}
    for name, columns in FILES.items():
        path = Path(data_dir)/(name+'.csv')
        content = path.read_bytes()
        manifest[path.name] = {'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        if list(frame.columns) != columns:
            raise ValueError(f'{path.name}: columns must be {columns}')
        frame['source_line'] = np.arange(len(frame))+2
        tables[name] = frame
    for name, key in [('routes', 'route_id'), ('stops', 'stop_id'),
                      ('trips', 'trip_id'), ('bookings', 'booking_id')]:
        if tables[name][key].eq('').any() or tables[name][key].duplicated().any():
            raise ValueError(f'{name}: blank or duplicate {key}')
    for name, columns in [('routes', ['route_id', 'scheduled_runtime_min', 'stops_count']),
                          ('stops', ['route_id', 'seq']), ('trips', ['route_id'])]:
        for c in columns:
            values = pd.to_numeric(tables[name][c], errors='raise')
            if not np.isfinite(values).all() or (values % 1 != 0).any():
                raise ValueError(f'{name}.{c}: expected finite integers')
            tables[name][c] = values.astype(int)
    for c, bound in [('lat', 90), ('lon', 180)]:
        values = pd.to_numeric(tables['stops'][c], errors='raise')
        if not np.isfinite(values).all() or (values.abs()>bound).any():
            raise ValueError('Invalid reference stop coordinates')
        tables['stops'][c] = values
    routes, stops, trips = (tables[n] for n in ['routes', 'stops', 'trips'])
    if not stops.route_id.isin(routes.route_id).all() or not trips.route_id.isin(routes.route_id).all():
        raise ValueError('Orphan stop/trip route')
    for c in ['scheduled_start', 'scheduled_end']:
        trips[c] = trips[c].map(timestamp)
        if trips[c].isna().any():
            raise ValueError('Invalid or timezone-naive trip schedule; no correction assumed')
    if (trips.scheduled_end <= trips.scheduled_start).any():
        raise ValueError('Nonpositive scheduled duration')
    if (trips.service_date != trips.scheduled_start.map(lambda x: x.date().isoformat())).any():
        raise ValueError('service_date does not match local scheduled_start')
    for _, route in routes.iterrows():
        st = stops[stops.route_id == route.route_id].sort_values('seq')
        if list(st.seq) != list(range(1, route.stops_count+1)) or route.scheduled_runtime_min <= 0:
            raise ValueError('Invalid stop sequence/count or runtime')
    return tables, manifest


def prepare_gps(raw, trips, geometries, as_of, policy):
    """The availability gate runs before payload dedup, parsing event fields or inference."""
    audit = {'raw_rows': len(raw), 'after_cutoff': 0, 'invalid_receipt': [],
             'duplicates': [], 'id_collisions': [], 'quarantined': [], 'invalid_speed': [],
             'excluded_operator_rows': [], 'location_warnings': []}
    available = []
    for row in raw.to_dict('records'):
        received = timestamp(row['received_at'])
        if pd.isna(received):
            audit['invalid_receipt'].append({'source_line': row['source_line'], 'raw_received_at': row['received_at']})
        elif received > as_of:
            audit['after_cutoff'] += 1  # No other future fields used or reported.
        else:
            available.append((row, received))
    audit['available_rows'] = len(available)
    seen, ids, candidates, operators = {}, {}, [], {}
    for row, received in available:
        provenance = {'source_line': row['source_line'], 'raw': {k: row[k] for k in FILES['gps_pings']}}
        if row['ping_id'] in ids:
            audit['id_collisions'].append({'ping_id': row['ping_id'], 'first_line': ids[row['ping_id']], 'other_line': row['source_line']})
        ids.setdefault(row['ping_id'], row['source_line'])
        payload = tuple(row[k] for k in FILES['gps_pings'] if k != 'ping_id')
        if payload in seen:
            audit['duplicates'].append({**provenance, 'retained_line': seen[payload]})
            continue
        seen[payload] = row['source_line']
        event = timestamp(row['recorded_at'])
        if pd.isna(event) or event > received:
            audit['quarantined'].append({**provenance, 'reason': 'invalid_or_future_device_time'})
            continue
        op = finite(row['operator_id'])
        if op is None or op % 1:
            audit['quarantined'].append({**provenance, 'reason': 'invalid_operator'})
            continue
        operators.setdefault(row['vehicle_id'], set()).add(int(op))
        matches = trips[(trips.vehicle_id == row['vehicle_id']) &
                        (trips.service_date == event.date().isoformat())]
        if len(matches) > 1:
            # Only unambiguous scheduled membership is accepted for multi-trip vehicles.
            matches = matches[(matches.scheduled_start <= event) & (event <= matches.scheduled_end)]
        if len(matches) != 1:
            audit['quarantined'].append({**provenance, 'reason': 'ambiguous_or_missing_trip'})
            continue
        trip = matches.iloc[0]
        if int(op) in policy.excluded_operators:
            audit['excluded_operator_rows'].append({'source_line': row['source_line'], 'trip_id': trip.trip_id, 'vehicle_id': row['vehicle_id'], 'operator_id': int(op)})
            continue
        lat, lon, speed = (finite(row[k]) for k in ['lat', 'lon', 'speed_kmph'])
        if lat is None or lon is None or abs(lat)>90 or abs(lon)>180:
            audit['quarantined'].append({**provenance, 'reason': 'invalid_coordinate'})
            continue
        progress, offset, origin = geometries[trip.route_id].project(lat, lon)
        q = dict(provenance, ping_id=row['ping_id'], vehicle_id=row['vehicle_id'], operator_id=int(op),
                 trip_id=trip.trip_id, route_id=int(trip.route_id), recorded_at=event, received_at=received,
                 lat=lat, lon=lon, speed_kmph=speed, usable_speed_kmph=speed,
                 progress_km=progress, offset_km=offset, origin_distance_m=origin,
                 elapsed_min=(event-trip.scheduled_start).total_seconds()/60,
                 event_age_s=(as_of-event).total_seconds(), receipt_age_s=(as_of-received).total_seconds())
        if speed is None or speed < 0 or speed > 120:
            q['usable_speed_kmph'] = None
            audit['invalid_speed'].append({'source_line': row['source_line'], 'ping_id': row['ping_id'], 'raw_speed': row['speed_kmph']})
        candidates.append(q)
    # Same vehicle/event time with unequal payloads: no first-row-wins guessing.
    counts = {}
    for q in candidates:
        key = (q['vehicle_id'], q['recorded_at'])
        counts[key] = counts.get(key, 0)+1
    clean, last = [], {}
    for q in sorted(candidates, key=lambda q: (q['trip_id'], q['recorded_at'], q['source_line'])):
        if counts[(q['vehicle_id'], q['recorded_at'])] > 1:
            audit['quarantined'].append({**q, 'reason': 'conflicting_same_event_time'})
            continue
        prev = last.get(q['trip_id'])
        implied = None
        if prev:
            seconds = (q['recorded_at']-prev['recorded_at']).total_seconds()
            implied = distance_km(prev['lat'], prev['lon'], q['lat'], q['lon'])/seconds*3600
        # Strong combined evidence, not an ID whitelist and not a blanket 500m rejection.
        absurd = q['offset_km'] > 50 and q['speed_kmph'] is not None and q['speed_kmph'] > 1000
        teleport = q['offset_km'] > .5 and implied is not None and implied > 1000
        if absurd or teleport:
            audit['quarantined'].append({**q, 'reason': 'impossible_position', 'implied_kmph_from_last_credible': implied})
            continue  # Do not advance the credible predecessor to a rejected point.
        q['position_uncertain'] = q['offset_km'] > .5 or (implied is not None and implied > 120)
        if q['position_uncertain']:
            audit['location_warnings'].append({'source_line': q['source_line'], 'ping_id': q['ping_id'], 'offset_km': q['offset_km'], 'implied_kmph': implied})
        else:
            last[q['trip_id']] = q
        clean.append(q)
    audit['retained_rows'] = len(clean)
    return clean, operators, audit


def crossing(points, progress, max_gap):
    hits = [(lo, hi) for lo, hi in zip(points, points[1:])
            if lo['progress_km'] <= progress <= hi['progress_km'] and hi['progress_km'] > lo['progress_km']]
    if not hits:
        return None
    lo, hi = hits[0]
    gap = (hi['recorded_at']-lo['recorded_at']).total_seconds()
    if gap > max_gap or lo['position_uncertain'] or hi['position_uncertain']:
        return None
    fraction = (progress-lo['progress_km'])/(hi['progress_km']-lo['progress_km'])
    return {'elapsed_min': lo['elapsed_min']+fraction*(hi['elapsed_min']-lo['elapsed_min']),
            'fraction': fraction, 'gap_s': gap, 'forward_crossings': len(hits),
            'lower': lo, 'upper': hi}


def numerical_action(observations, threshold):
    """Called only after eligibility; round only an eligible, persistent push."""
    deficits = [v for o in observations for v in o['deficits'].values()]
    if min(deficits) >= threshold:
        return f'PUSH_LATE {math.floor(observations[-1]["median_deficit"]+.5)} min'
    if max(deficits) < threshold:
        return 'HOLD'
    return 'NO_VERDICT'


def booking_context(bookings, trip, geometry, as_of):
    result = {'bookings': 0, 'unique_riders': 0, 'promise_warnings': [], 'invalid_bookings': []}
    riders = set()
    for row in bookings[bookings.trip_id == trip.trip_id].to_dict('records'):
        booked, promised = timestamp(row['booked_at']), timestamp(row['promised_eta'])
        if pd.isna(booked):
            result['invalid_bookings'].append({'source_line': row['source_line'], 'reason': 'unknown_booking_availability'})
            continue
        if booked > as_of:
            continue
        result['bookings'] += 1
        riders.add(row['rider_id'])
        fraction = geometry.fractions.get(row['boarding_stop_id'])
        if pd.isna(promised) or fraction is None:
            result['invalid_bookings'].append({'source_line': row['source_line'], 'booking_id': row['booking_id'], 'reason': 'invalid_promise_or_wrong_route_stop'})
            continue
        reference = trip.scheduled_start+(trip.scheduled_end-trip.scheduled_start)*fraction
        diff = (promised-reference).total_seconds()
        if abs(diff) > 2:
            result['promise_warnings'].append({'booking_id': row['booking_id'], 'rider_id': row['rider_id'],
                'boarding_stop_id': row['boarding_stop_id'], 'source_line': row['source_line'],
                'promised_eta': promised, 'schedule_reference': reference, 'offset_seconds': diff})
    result['unique_riders'] = len(riders)
    result['count_caveat'] = 'Bookings, not confirmed waiting riders; no boarding/cancellation events.'
    return result


def evaluate_trip(trip, points, trips, operators, geometry, runtime, bookings, as_of, policy):
    z = sorted([q for q in points if q['trip_id'] == trip.trip_id and not q['position_uncertain']], key=lambda q: q['recorded_at'])
    result = {'trip_id': trip.trip_id, 'vehicle_id': trip.vehicle_id, 'scheduled_start': trip.scheduled_start,
              'scheduled_end': trip.scheduled_end, 'route_id': int(trip.route_id),
              'bookings': booking_context(bookings, trip, geometry, as_of), 'latest': z[-1] if z else None,
              'observations': [], 'numerical_eligible': False, 'reference_trips': {},
              'verdict': 'NO_VERDICT', 'reason': '', 'data_state': 'unknown', 'credible_rows': len(z)}
    op = operators.get(trip.vehicle_id, set())
    result['operator_ids'] = sorted(op)
    if len(op) != 1:
        result.update(reason='Operator/vehicle attribution unavailable or conflicting', data_state='uncertain_attribution')
        return result
    if not z:
        result.update(reason='No credible pre-cutoff location; attribution/availability needs verification', data_state='no_credible_gps')
        return result
    last = z[-1]
    result['observations'] = [{'gps': q, 'references': {}, 'deficits': None, 'median_deficit': None,
                               'timetable_crosscheck': None} for q in z[-policy.persistence_points:]]
    # Consecutive origin evidence must span the configured duration, not just one late origin fix.
    origin = [q for q in z if q['elapsed_min'] >= 0]
    origin_bound = (len(origin) >= 3 and all(q['origin_distance_m'] <= policy.origin_radius_m for q in origin)
                    and (origin[-1]['recorded_at']-origin[0]['recorded_at']).total_seconds() >= policy.origin_duration_minutes*60
                    and last['elapsed_min'] >= policy.origin_duration_minutes)
    result['origin_bound'] = origin_bound
    result['origin_radius_max_m'] = max(q['origin_distance_m'] for q in origin) if origin else None
    result['event_gaps_s'] = [(hi['gps']['recorded_at']-lo['gps']['recorded_at']).total_seconds()
                              for lo, hi in zip(result['observations'], result['observations'][1:])]
    if origin_bound:
        result.update(verdict='CALL_DRIVER', data_state='origin_bound', reason='Persistent origin-bound telemetry after departure; verify bus location and tracker assignment')
        return result
    if last['event_age_s'] > policy.verification_gap_seconds:
        result.update(verdict='CALL_DRIVER', data_state='stale', reason='Usable telemetry absent for more than five minutes; verify current service/location; completion is unconfirmed')
        return result
    if last['event_age_s'] > policy.freshness_seconds:
        result.update(data_state='not_fresh', reason='Newest credible event exceeds numerical freshness limit')
        return result
    if len(z) < policy.persistence_points or any(v > policy.persistence_gap_seconds for v in result['event_gaps_s']):
        result.update(data_state='insufficient_persistence', reason='Three distinct recent observations with short gaps are not available')
        return result
    history = trips[(trips.route_id == trip.route_id) & (trips.service_date < trip.service_date)
                    & (trips.direction == trip.direction)]
    days = sorted(history.service_date.unique())[-policy.history_days:]
    references = {}
    for day in days:
        candidates = history[history.service_date == day]
        candidates = candidates[candidates.vehicle_id.map(lambda v: len(operators.get(v, set())) == 1
                                   and not operators[v].intersection(policy.excluded_operators))]
        if len(candidates) > 1:
            candidates = candidates[candidates.vehicle_id == trip.vehicle_id]
        if len(candidates) != 1:
            continue
        tid = candidates.iloc[0].trip_id
        ref = sorted([q for q in points if q['trip_id'] == tid], key=lambda q: q['recorded_at'])
        references[day] = ref
        result['reference_trips'][day] = tid
    if len(references) != policy.history_days:
        result.update(data_state='insufficient_history', reason='Two distinct earlier service dates with unambiguous eligible reference trips are required')
        return result
    for observation in result['observations']:
        q = observation['gps']
        ref = {day: crossing(zref, q['progress_km'], policy.reference_gap_seconds) for day, zref in references.items()}
        observation['references'] = ref
        if not all(ref.values()):
            result.update(data_state='unbracketed_history', reason='Current position is not credibly bracketed by both historical traces; no extrapolation')
            return result
        observation['deficits'] = {day: q['elapsed_min']-v['elapsed_min'] for day, v in ref.items()}
        observation['median_deficit'] = float(np.median(list(observation['deficits'].values())))
        observation['timetable_crosscheck'] = q['elapsed_min']-runtime*q['progress_km']/geometry.length
    result['numerical_eligible'] = True
    result['verdict'] = numerical_action(result['observations'], policy.materiality_minutes)
    # Sensitivity is evidence, not a reason to tune materiality to the desired label.
    stress_disagrees = False
    for observation in result['observations']:
        q = observation['gps']
        observation['position_sensitivity'] = []
        for shift in [-policy.position_stress_m/1000, policy.position_stress_m/1000]:
            x = q['progress_km']+shift
            rr = {day: crossing(ref, x, policy.reference_gap_seconds) for day, ref in references.items()} if 0 <= x <= geometry.length else {}
            ds = {day: q['elapsed_min']-v['elapsed_min'] for day, v in rr.items()} if rr and all(rr.values()) else None
            observation['position_sensitivity'].append({'shift_m': shift*1000, 'deficits': ds})
            if result['verdict'] == 'HOLD':
                stress_disagrees |= ds is None or max(ds.values()) >= policy.materiality_minutes
            elif result['verdict'].startswith('PUSH_LATE'):
                stress_disagrees |= ds is None or min(ds.values()) < policy.materiality_minutes
    if stress_disagrees:
        result.update(verdict='NO_VERDICT', data_state='position_sensitive',
                      reason='Plausible position perturbation changes materiality eligibility or is unbracketed')
        return result
    result['data_state'] = 'fresh_credible'
    result['reason'] = {'HOLD': 'Both references below materiality across all three observations',
                        'NO_VERDICT': 'Reference or observation disagreement across materiality threshold'}.get(result['verdict'], 'Both references at/above materiality across all three observations; rounded only after eligibility')
    return result


def analyze(data_dir, as_of, policy):
    as_of = timestamp(as_of)
    if pd.isna(as_of):
        raise ValueError('--as-of must be a valid timezone-aware timestamp')
    tables, manifest = load(data_dir)
    trips, routes, stops = (tables[n] for n in ['trips', 'routes', 'stops'])
    geometries = {rid: Geometry(st) for rid, st in stops.groupby('route_id')}
    gps, operators, audit = prepare_gps(tables['gps_pings'], trips, geometries, as_of, policy)
    report = {'as_of': as_of, 'policy': asdict(policy), 'sources': manifest, 'gps_audit': audit, 'routes': []}
    day = as_of.date().isoformat()
    for _, route in routes.sort_values('route_id').iterrows():
        current = trips[(trips.route_id == route.route_id) & (trips.service_date == day)
                        & (trips.scheduled_start <= as_of)]
        evaluated, excluded = [], []
        for _, trip in current.iterrows():
            op = operators.get(trip.vehicle_id, set())
            if len(op) == 1 and op.intersection(policy.excluded_operators):
                context = booking_context(tables['bookings'], trip, geometries[route.route_id], as_of)
                excluded.append({'trip_id': trip.trip_id, 'vehicle_id': trip.vehicle_id, 'operators': sorted(op), 'bookings': context, 'reason': 'Configured operator exclusion'})
            else:
                evaluated.append(evaluate_trip(trip, gps, trips, operators, geometries[route.route_id],
                                 route.scheduled_runtime_min, tables['bookings'], as_of, policy))
        verdicts = [x['verdict'] for x in evaluated]
        if not evaluated:
            verdict, note = 'NO_VERDICT', 'No started, included trip available for this route at as-of'
        elif 'CALL_DRIVER' in verdicts:
            verdict, note = 'CALL_DRIVER', 'Direct verification takes precedence: '+ '; '.join(x['reason'] for x in evaluated if x['verdict'] == 'CALL_DRIVER')
        elif len(evaluated) == 1:
            verdict, note = evaluated[0]['verdict'], evaluated[0]['reason']
        elif all(v == 'HOLD' for v in verdicts):
            verdict, note = 'HOLD', 'Every included trip supports HOLD'
        else:
            verdict, note = 'NO_VERDICT', 'Multiple included trips cannot be compressed into one supported numerical notification; inspect per-trip evidence'
        scope = ', '.join(x['trip_id']+'/'+x['vehicle_id'] for x in evaluated) or 'none'
        note += '. Scope: '+scope+'.'
        outside = sum(x['bookings']['bookings'] for x in excluded)
        if excluded:
            note += f' {outside} bookings outside assessment on configured excluded trips: '+', '.join(x['trip_id']+'/'+x['vehicle_id'] for x in excluded)+'.'
        warnings = sum(len(x['bookings']['promise_warnings'])+len(x['bookings']['invalid_bookings']) for x in evaluated)
        if warnings:
            note += f' {warnings} booking/promise warnings require separate ops/product reconciliation; HOLD does not certify promises.'
        conflict = policy.contractual_reporting_requests.get(str(route.route_id))
        if conflict:
            note += f' Operational evidence governs this row. {conflict["source"]} requests contractual lateness={conflict["requested_lateness_minutes"]}; override not applied.'
        report['routes'].append({'route': int(route.route_id), 'route_name': route.route_name,
            'verdict': verdict, 'note': note, 'evaluated_trips': evaluated, 'excluded_trips': excluded,
            'booking_exposure': sum(x['bookings']['bookings'] for x in evaluated), 'excluded_bookings': outside,
            'reporting_conflict': conflict})
    return report
