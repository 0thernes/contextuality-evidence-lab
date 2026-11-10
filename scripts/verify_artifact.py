"""Independent exact replay: deliberately does not import the experiment engine."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_replay(trials, report):
    spec = report['certificate']
    floor = Fraction(spec['beta'])
    delta = Fraction(spec['delta'])
    bound = 1 - (1 - delta) * floor
    a, b = Fraction(spec['success_factor']), Fraction(spec['failure_factor'])
    assert 0 < floor <= Fraction(1, 6) and 0 <= delta < 1
    assert a >= b >= 0 and bound * a + (1 - bound) * b <= 1
    numerator = denominator = 1
    first = None
    successes = 0
    for index, trial in enumerate(trials, 1):
        assert type(trial['success']) is bool
        factor = a if trial['success'] else b
        numerator *= factor.numerator
        denominator *= factor.denominator
        successes += int(trial['success'])
        if first is None and numerator >= int(report['threshold']) * denominator:
            first = index
    assert first == report['first_crossing']
    assert successes == report['successes']
    assert len(trials) == report['trials']


def main():
    if not __debug__:
        raise RuntimeError('Optimized Python disables verification; run without -O')
    report = json.loads((ROOT / 'results/experiment.json').read_text())
    for name, expected in report['analysis_source_sha256'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
    assert hashlib.sha256((ROOT / 'results/stack_report.json').read_bytes()).hexdigest() == report['native_report_sha256']
    native_path = ROOT / 'results/stack_trials.json'
    native = json.loads(native_path.read_text())
    assert hashlib.sha256(native_path.read_bytes()).hexdigest() == report['stack_trials_sha256']
    check_replay(native, report['moonlab_readout'])
    attack = json.loads((ROOT / 'results/classical_attack_trials.json').read_text())
    check_replay(attack, report['classical_attack']['naive'])
    check_replay(attack, report['classical_attack']['protected'])
    for shot in attack:
        assert shot['success'] == (shot['context'] != 5)
    # Separate signed-product enumeration, not bit parity code from evidence.py.
    witness = {}
    counts = {1: 0, 3: 0, 5: 0}
    for word in range(512):
        values = [1 if word & (1 << bit) == 0 else -1 for bit in range(9)]
        products = [values[3*r] * values[3*r+1] * values[3*r+2] for r in range(3)]
        products += [values[c] * values[c+3] * values[c+6] for c in range(3)]
        broken = [i for i, value in enumerate(products) if value != (-1 if i == 5 else 1)]
        counts[len(broken)] += 1
        if len(broken) == 1:
            witness[broken[0]] = word
    assert counts == {1: 96, 3: 320, 5: 96} and len(witness) == 6
    assert Fraction(57, 50)**36 > 100
    assert Fraction(11, 12)**36 > Fraction(1, 100)
    assert Fraction(57, 55)**36 < 100
    result = {'status': 'passed', 'assignment_checks': 512,
              'exact_trial_replays': len(native) + 2*len(attack),
              'replayed_sources': ['Moonlab noisy', 'classical naive', 'classical protected'],
              'scope': 'Independent signed-product enumeration, certificate arithmetic, exact threshold replay and transcript hash. Does not certify empirical independence or recompute the 1000-step DP.'}
    (ROOT / 'results/independent_verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
