"""CSV/JSON/Markdown outputs and a disclosed operational investigation order."""
from pathlib import Path
import csv
import json
import math
import numpy as np
import pandas as pd


def plain(value):
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, np.generic):
        return plain(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if value is pd.NaT or value is pd.NA:
        return None
    return value


def num(value):
    return 'N/A' if value is None else f'{value:.6f}'


def markdown_table(headers, rows):
    def cell(v):
        return str(v).replace('|', '/').replace('\n', ' ')
    return '\n'.join(['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |'] +
                     ['| '+' | '.join(cell(v) for v in row)+' |' for row in rows])


def worry_order(report):
    """No route-specific priority: unresolved service first, then action and customer issues."""
    scored = []
    for route in report['routes']:
        trips = route['evaluated_trips']
        call = [t for t in trips if t['verdict'] == 'CALL_DRIVER']
        if call:
            # Exposure first within verification class, then duration of information/state failure.
            exposure = sum(t['bookings']['bookings'] for t in call)
            duration = max((t['latest']['elapsed_min']*60 if t.get('origin_bound') else t['latest']['event_age_s']) for t in call)
            key = (0, -exposure, -duration)
            why = f'Direct service verification; {exposure} booking records on affected included trips. Exposure breaks ties before duration ({duration:.0f}s).'
        elif route['verdict'] == 'NO_VERDICT':
            key = (1, -route['booking_exposure'], 0)
            why = 'Unresolved classification; identify missing evidence before trusting a numerical claim.'
        elif route['verdict'].startswith('PUSH_LATE'):
            key = (2, -route['booking_exposure'], 0)
            why = 'Credible persistent material progress deficit; customer communication is supported.'
        elif route['excluded_bookings'] or any(t['bookings']['promise_warnings'] or t['bookings']['invalid_bookings'] for t in trips):
            key = (3, -route['booking_exposure']-route['excluded_bookings'], 0)
            why = 'No material included-trip deficit, but promise/population issues need ops/product follow-up.'
        else:
            key = (4, -route['booking_exposure'], 0)
            why = 'Credible below-threshold operation; monitor after unresolved cases.'
        scored.append((key+(route['route'],), route, why))
    return [(r, why) for _, r, why in sorted(scored, key=lambda item: item[0])]


def write_outputs(report, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data = plain(report)
    (out_dir/'evidence.json').write_text(json.dumps(data, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    columns = ['route', 'verdict', 'note', 'trip_ids', 'vehicle_ids', 'data_state',
               'event_age_seconds', 'historical_deficits_minutes', 'median_deficit_minutes',
               'timetable_crosscheck_minutes', 'booking_exposure', 'excluded_bookings']
    with (out_dir/'verdicts.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for route in data['routes']:
            ts = route['evaluated_trips']
            last = ts[0]['observations'][-1] if len(ts) == 1 and ts[0]['observations'] else {}
            writer.writerow(dict(route=route['route'], verdict=route['verdict'], note=route['note'],
                trip_ids=';'.join(t['trip_id'] for t in ts), vehicle_ids=';'.join(t['vehicle_id'] for t in ts),
                data_state=';'.join(t['data_state'] for t in ts),
                event_age_seconds=';'.join(str(t['latest']['event_age_s']) if t['latest'] else '' for t in ts),
                historical_deficits_minutes=json.dumps(last.get('deficits')),
                median_deficit_minutes=last.get('median_deficit'), timetable_crosscheck_minutes=last.get('timetable_crosscheck'),
                booking_exposure=route['booking_exposure'], excluded_bookings=route['excluded_bookings']))
    text = ['# Operational verdicts', '', 'As-of: '+data['as_of'], '',
            'Each row covers the evaluated trips named in its note. Numbers describe historical progress-time deficit, not a guaranteed arrival ETA. Bookings are not confirmed waiting riders. No external actions were executed.', '',
            markdown_table(['route', 'verdict', 'note'], [[r['route'], r['verdict'], r['note']] for r in data['routes']]), '', '# Calculation evidence', '']
    for r in data['routes']:
        text += [f'## Route {r["route"]}', '']
        for t in r['evaluated_trips']:
            text += [f'### {t["trip_id"]} / {t["vehicle_id"]}', '',
                     f'State: {t["data_state"]}; numerical eligible: {t["numerical_eligible"]}. {t["reason"]}.', '',
                     f'Included bookings: {t["bookings"]["bookings"]}; distinct rider IDs: {t["bookings"]["unique_riders"]}. Promise warnings: {len(t["bookings"]["promise_warnings"])}. Invalid booking fields: {len(t["bookings"]["invalid_bookings"])}.', '']
            rows = []
            for o in t['observations']:
                q = o['gps']
                rows.append([q['ping_id'], q['source_line'], q['recorded_at'], q['received_at'], num(q['event_age_s']),
                             num(q['progress_km']), json.dumps(o['deficits']), num(o['median_deficit']), num(o['timetable_crosscheck'])])
            text += [markdown_table(['ping', 'source line', 'device time', 'receipt time', 'event age s', 'progress km', 'reference deficits min', 'median min', 'timetable min'], rows), '',
                     'Unrounded reference brackets, raw source provenance, quality audit and position sensitivity are in evidence.json.', '']
    (out_dir/'verdicts.md').write_text('\n'.join(text)+'\n', encoding='utf-8')
    worry = ['# Investigation priority', '', 'As-of: '+data['as_of'], '',
             'This order ranks human investigation, not necessarily notification dispatch. Priority: direct service verification, unresolved classification, supported material delay, promise/exclusion issues, then routine monitoring. Within direct verification, rank booking exposure first, then problem duration. Counts are bookings, not confirmed waiting riders. No monetary cost weights are invented.', '',
             markdown_table(['rank', 'route', 'included bookings', 'excluded bookings', 'reason'],
                            [[i, r['route'], r['booking_exposure'], r['excluded_bookings'], why]
                             for i, (r, why) in enumerate(worry_order(data), 1)]), '',
             'Tradeoff: exposure-first can place a smaller but longer or more conclusive failure later. A confirmed breakdown, independently known waiting riders, missed connection, or emergency would supersede this order; those facts are absent.']
    (out_dir/'worry_order.md').write_text('\n'.join(worry)+'\n', encoding='utf-8')


def write_sensitivity(reports, out_dir):
    rows = []
    for report in reports:
        p = report['policy']
        rows.append([p['materiality_minutes'], p['freshness_seconds']]+[r['verdict'] for r in report['routes']])
    header = ['materiality min', 'freshness s']+['route '+str(r['route']) for r in reports[0]['routes']]
    Path(out_dir, 'sensitivity.md').write_text('# Sensitivity (selected policy unchanged)\n\n'+markdown_table(header, rows)+'\n', encoding='utf-8')
