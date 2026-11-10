"""Rebuild exact benchmarks and adversarial replays; consume fresh stack shots."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from evidence import (Bet, CONTEXTS, outcomes, enumerate_square, validate_distribution,
                      sharp_classical_bound, replay, exact_hitting_probability,
                      fraction_record)


def load_native_trials(root=ROOT):
    """Bind successful execution evidence to its source and full shot records."""
    results = root / 'results'
    report = json.loads((results / 'stack_report.json').read_text(encoding='utf-8'))
    if report.get('status') != 'pass':
        raise ValueError('native stack has no successful execution report')
    for name in ('moonlab', 'qgtl', 'qrng', 'eshkol'):
        if report.get(name, {}).get('status') != 'pass':
            raise ValueError('required component did not pass: ' + name)
    required_artifacts = {'stack_trials.json', 'stack_shots.json', 'stack_tangents.json'}
    required_sources = {'scripts/run_stack.py', 'src/stack_enumeration.esk',
                        'src/stack_moonlab.mjs', 'src/stack_qrng.c'}
    if not required_artifacts <= set(report.get('artifacts_sha256', {})):
        raise ValueError('missing mandatory native artifact fingerprints')
    if not required_sources <= set(report.get('source_sha256', {})):
        raise ValueError('missing mandatory native source fingerprints')
    for name, expected in report['artifacts_sha256'].items():
        actual = hashlib.sha256((results / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('native artifact fingerprint mismatch: ' + name)
    for name, expected in report['source_sha256'].items():
        actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError('native source changed since execution: ' + name)
    trials = json.loads((results / 'stack_trials.json').read_text(encoding='utf-8'))
    shots = json.loads((results / 'stack_shots.json').read_text(encoding='utf-8'))
    if len(trials) != 6000 or len(shots) != len(trials):
        raise ValueError('expected 6000 matching native trial and shot records')
    for trial, shot in zip(trials, shots):
        c = shot['context']
        if type(c) is not int or not 0 <= c < 6:
            raise ValueError('bad native context')
        if sorted(shot['order']) != sorted(CONTEXTS[c]):
            raise ValueError('recorded measurement order is not the selected context')
        ideal, recorded, flips = shot['ideal_outcomes'], shot['recorded_outcomes'], shot['readout_flips']
        if not len(ideal) == len(recorded) == len(flips) == 3:
            raise ValueError('three outcomes and readout flags required')
        for v, r, flip in zip(ideal, recorded, flips):
            if type(v) is not int or v not in (-1, 1) or type(r) is not int or r not in (-1, 1):
                raise ValueError('outcomes must be +/-1 integers')
            if type(flip) is not bool or r != (-v if flip else v):
                raise ValueError('readout outcome disagrees with recorded flip')
        sign = -1 if c == 5 else 1
        if ideal[0] * ideal[1] * ideal[2] != sign:
            raise ValueError('ideal native parity disagrees with operator product')
        success = recorded[0] * recorded[1] * recorded[2] == sign
        if type(trial['success']) is not bool or type(shot['success']) is not bool:
            raise ValueError('success fields must be Boolean')
        if trial != {'context': c, 'success': success} or shot['success'] != success:
            raise ValueError('compact trial disagrees with recorded outcomes')
    return trials


def main():
    if not __debug__:
        raise RuntimeError('Optimized Python disables required experiment checks; run without -O')
    parser = argparse.ArgumentParser()
    parser.add_argument('--horizon', type=int, default=1000)
    args = parser.parse_args()
    results = ROOT / 'results'
    results.mkdir(exist_ok=True)
    protected, naive = Bet(), Bet(beta=F(1, 6))
    p = (F(11, 60),) * 5 + (F(1, 12),)
    validate_distribution(p, protected.beta)
    assert sharp_classical_bound(p) == F(11, 12)
    enumeration = enumerate_square()
    # Fixed, disclosed software seed: an illustrative attack replay, not physical entropy.
    generator = random.Random(20261110)
    attack = []
    for _ in range(6000):
        bucket = generator.randrange(60)
        context = bucket // 11 if bucket < 55 else 5
        attack.append({'context': context, 'success': outcomes(0)[context]})
    # An OUT-OF-MODEL context-leaking attacker changes its table after seeing the
    # setting. It wins every trial and demonstrates why the assumption matters.
    leaked = []
    witnesses = enumeration['singleton_witnesses']
    for i in range(600):
        context = i % 6
        mask = witnesses[(context + 1) % 6]
        leaked.append({'context': context, 'success': outcomes(mask)[context],
                       'assignment': mask})
    attack_results = {'naive': replay(attack, naive), 'protected': replay(attack, protected)}
    leaked_result = replay(leaked, protected)
    assert leaked_result['first_crossing'] is not None
    exact = {}
    for name, bet in [('naive', naive), ('protected', protected)]:
        hit = exact_hitting_probability(bet, F(11, 12), args.horizon)
        exact[name] = fraction_record(hit)
    assert F(int(exact['protected']['numerator']), int(exact['protected']['denominator'])) <= F(1, 100)
    assert F(int(exact['naive']['numerator']), int(exact['naive']['denominator'])) > F(1, 100)
    prefix_probability = F(11, 12) ** 36
    assert naive.a ** 36 > 100 and prefix_probability > F(1, 100)
    assert protected.a ** 36 < 100
    failures_rejected = []
    for name, operation in [
        ('unsafe_factor', lambda: Bet(success_factor=F(6, 5))),
        ('false_context_floor', lambda: validate_distribution(p, F(1, 6))),
        ('negative_factor', lambda: Bet(failure_factor=-1))]:
        try:
            operation()
        except ValueError:
            failures_rejected.append(name)
        else:
            raise AssertionError('negative control accepted: ' + name)
    # Removing the one negative operator sign destroys the parity contradiction.
    assert all(outcomes(0, negative=(False,) * 6))
    failures_rejected.append('all_positive_signs_destroy_parity')
    record = {
        'schema': 1, 'experiment': 'bias-aware finite-horizon contextuality evidence',
        'scope': 'Classical simulation and exact rational value-table model; no hardware certification.',
        'seed': 20261110, 'enumeration': enumeration,
        'context_distribution_attack': [str(x) for x in p],
        'classical_success_bound': '11/12', 'threshold': 100,
        'prefix_counterexample': {'trials': 36, 'naive_wealth': fraction_record(naive.a ** 36),
                                  'protected_wealth': fraction_record(protected.a ** 36),
                                  'classical_probability': fraction_record(prefix_probability)},
        'exact_iid_hitting': {'horizon': args.horizon, **exact},
        'classical_attack': attack_results,
        'context_leak_outside_model': leaked_result,
        'rejected_negative_controls': failures_rejected,
        'predicted_readout_success': str((1 + (1 - 2 * F(1, 100)) ** 3) / 2),
    }
    trials_path = results / 'stack_trials.json'
    if not trials_path.exists():
        raise FileNotFoundError('Run python scripts/run_stack.py first: missing fresh native stack shots')
    quantum_trials = load_native_trials()
    record['moonlab_readout'] = replay(quantum_trials, protected)
    record['stack_trials_sha256'] = hashlib.sha256(trials_path.read_bytes()).hexdigest()
    record['native_report_sha256'] = hashlib.sha256((results / 'stack_report.json').read_bytes()).hexdigest()
    record['analysis_source_sha256'] = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        for name in ('src/evidence.py', 'scripts/run_experiment.py', 'scripts/verify_artifact.py')}
    (results / 'experiment.json').write_text(json.dumps(record, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    (results / 'classical_attack_trials.json').write_text(json.dumps(attack, separators=(',', ':')) + '\n', encoding='utf-8')
    # The web demo consumes the same result, not invented chart values.
    docs = ROOT / 'docs'
    docs.mkdir(exist_ok=True)
    (docs / 'experiment.json').write_text(json.dumps(record, separators=(',', ':'), allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({
        'exact_horizon': args.horizon,
        'naive_false_rejection_probability': exact['naive']['decimal'],
        'protected_false_rejection_probability': exact['protected']['decimal'],
        'attack_first_crossing_naive': attack_results['naive']['first_crossing'],
        'attack_first_crossing_protected': attack_results['protected']['first_crossing'],
        'moonlab_first_crossing_protected': record['moonlab_readout']['first_crossing'],
        'moonlab_successes': record['moonlab_readout']['successes'],
        'negative_controls': failures_rejected}, indent=2))


if __name__ == '__main__':
    main()
