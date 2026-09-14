import argparse
from dataclasses import replace
import json
from pathlib import Path
from .engine import Policy, analyze
from .reporting import write_outputs, write_sensitivity


def main():
    parser = argparse.ArgumentParser(description='Offline, evidence-based route-progress verdicts')
    parser.add_argument('--data-dir', required=True, type=Path)
    parser.add_argument('--as-of', required=True, help='Timezone-aware ISO timestamp')
    parser.add_argument('--policy', type=Path, default=Path(__file__).resolve().parents[1]/'policy.json')
    parser.add_argument('--out-dir', type=Path, default=Path('results'))
    parser.add_argument('--sensitivity', action='store_true', help='Also evaluate 3/5/7 min and 30/60/120s; never retune selected policy')
    args = parser.parse_args()
    data, out = args.data_dir.resolve(), args.out_dir.resolve()
    if out == data or data in out.parents:
        parser.error('--out-dir must be outside the input data directory')
    try:
        policy = Policy(**json.loads(args.policy.read_text(encoding='utf-8')))
        report = analyze(data, args.as_of, policy)
        write_outputs(report, out)
        if args.sensitivity:
            reports = [analyze(data, args.as_of, replace(policy, materiality_minutes=m, freshness_seconds=s))
                       for m in [3, 5, 7] for s in [30, 60, 120]]
            write_sensitivity(reports, out)
    except (ValueError, OSError, KeyError) as exc:
        parser.error(str(exc))
    for row in report['routes']:
        print(f'{row["route"]}: {row["verdict"]}')
    print(f'Wrote {out}')


if __name__ == '__main__':
    main()
