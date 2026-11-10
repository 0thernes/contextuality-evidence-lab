"""Build and exercise all four pinned Tsotchke components, failing closed.

python scripts/run_stack.py [--seed 20261110] [--trials 6000]
Set ESHKOL_RUN when eshkol-run is not on PATH. GCC, Node and NumPy required.
These are classical simulations and executable checks, not hardware evidence.
"""
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BUILD, RESULTS = ROOT / 'build', ROOT / 'results'


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(command, label, env=None):
    result = subprocess.run([str(x) for x in command], cwd=ROOT, env=env,
                            text=True, encoding='utf-8', errors='replace',
                            capture_output=True, timeout=180)
    (RESULTS / ('stack_' + label + '.log')).write_text(
        result.stdout + result.stderr, encoding='utf-8')
    require(result.returncode == 0, '%s failed (%s): %s' % (
        label, result.returncode, (result.stdout + result.stderr)[-2500:]))
    return result.stdout


def qgtl(cc):
    dll = BUILD / ('stack_diffgeo.dll' if os.name == 'nt' else 'stack_diffgeo.so')
    command = [cc, '-O2', '-std=gnu11', '-shared', '-fPIC',
               '-Ithird_party/qgtl/include', '-Ithird_party/qgtl/stub',
               'third_party/qgtl/src/quantum_geometric/distributed/differential_geometry.c',
               '-o', dll, '-lm']
    run(command, 'qgtl_build')
    dll_directory = None
    if os.name == 'nt':
        dll_directory = os.add_dll_directory(str(Path(shutil.which(cc)).parent))
    lib = ct.CDLL(str(dll))
    lib.diffgeo_engine_create.restype = ct.c_void_p
    lib.diffgeo_engine_destroy.argtypes = [ct.c_void_p]
    for name in ('diffgeo_compute_fubini_study', 'diffgeo_compute_berry_curvature'):
        fn = getattr(lib, name)
        fn.argtypes = [ct.c_void_p, ct.c_void_p, ct.c_size_t, ct.c_void_p,
                       ct.c_size_t, ct.c_void_p]
        fn.restype = ct.c_bool
    engine = lib.diffgeo_engine_create()
    require(engine, 'QGTL allocation failed')

    def kernels(state, tangents):
        state = np.ascontiguousarray(state, dtype=np.complex128)
        tangents = np.ascontiguousarray(tangents, dtype=np.complex128)
        require(abs(np.vdot(state, state) - 1) < 1e-12,
                'QGTL caller must supply normalized state')
        n = len(tangents)
        g, f = np.zeros((n, n)), np.zeros((n, n))
        for name, out in [('diffgeo_compute_fubini_study', g),
                          ('diffgeo_compute_berry_curvature', f)]:
            require(getattr(lib, name)(engine, state.ctypes.data, state.size,
                                      tangents.ctypes.data, n, out.ctypes.data),
                    name + ' returned false')
        return g, f

    try:
        data = json.loads((RESULTS / 'stack_tangents.json').read_text())
        state = np.array(data['state']) @ np.array([1, 1j])
        tangents = np.array(data['tangents']) @ np.array([1, 1j])
        g, f = kernels(state, tangents)
        overlaps = tangents.conj() @ state
        q = tangents.conj() @ tangents.T - np.outer(overlaps, overlaps.conj())
        g_ref, f_ref = q.real, -2 * q.imag
        analytic_g, analytic_f = np.zeros((4, 4)), np.zeros((4, 4))
        for j, theta in enumerate(data['parameters'][:2]):
            analytic_g[j, j] = 0.25
            analytic_g[j+2, j+2] = np.sin(theta)**2 / 4
            analytic_f[j, j+2] = -np.sin(theta) / 2
            analytic_f[j+2, j] = np.sin(theta) / 2
        reference_error = float(max(np.max(abs(g-g_ref)), np.max(abs(f-f_ref))))
        analytic_error = float(max(np.max(abs(g-analytic_g)), np.max(abs(f-analytic_f))))
        require(reference_error < 1e-12, 'QGTL independent inner-product mismatch')
        require(analytic_error < 1e-9, 'Moonlab/QGTL analytic product-sphere mismatch')
        shifted = tangents + 1j * np.arange(1, 5)[:, None] * state[None, :]
        phase = np.exp(0.713j)
        gg, ff = kernels(phase*state, phase*shifted)
        gauge_error = float(max(np.max(abs(gg-g)), np.max(abs(ff-f))))
        require(gauge_error < 1e-11, 'QGTL phase gauge invariance failed')
        wrong_sign_error = float(np.max(abs(f+analytic_f)))
        require(wrong_sign_error > 0.9, 'wrong Berry sign mutation not detected')
        return {'status': 'pass', 'state_dimension': 4, 'parameters': 4,
                'source': 'Pinned actual Tsotchke differential_geometry.c',
                'kernels': ['diffgeo_compute_fubini_study', 'diffgeo_compute_berry_curvature'],
                'family': 'Two native Moonlab Ry(theta)Rz(phi) preparations then fixed CNOT',
                'tangents': 'Central differences of native Moonlab amplitudes',
                'difference_step': data['step'],
                'curvature_convention': 'F_ij = -2 Im Q_ij',
                'max_direct_inner_product_error': reference_error,
                'max_analytic_error': analytic_error, 'max_gauge_error': gauge_error,
                'wrong_berry_sign_error': wrong_sign_error,
                'metric': g.tolist(), 'berry_curvature': f.tolist(),
                'binary_sha256': sha(dll),
                'build_command': [str(x) for x in command],
                'scope': 'Normalized pure-state geometry kernels only; no GPU or distributed execution.'}
    finally:
        lib.diffgeo_engine_destroy(engine)


def verify_eshkol(result):
    contexts = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                (0, 3, 6), (1, 4, 7), (2, 5, 8)]
    hist, witnesses, maxima = [0]*7, [-1]*6, [0]*6
    for mask in range(512):
        signs = []
        for j, context in enumerate(contexts):
            product = -1 if j == 5 else 1
            for i in context:
                product *= -1 if mask & (1 << i) else 1
            signs.append(product)
        failed = [j for j, sign in enumerate(signs) if sign == -1]
        hist[len(failed)] += 1
        if len(failed) == 1 and witnesses[failed[0]] == -1:
            witnesses[failed[0]] = mask
        for j in range(6):
            win = sum((5 if i == j else 11) for i in range(6) if signs[i] == 1)
            maxima[j] = max(maxima[j], win)
    require(result.get('pass') is True, 'Eshkol self-check returned false')
    require(result['violation_histogram'] == hist == [0,96,0,320,0,96,0],
            'Eshkol histogram differs from independent Python enumeration')
    require(result['singleton_witness_masks'] == witnesses and min(witnesses) >= 0,
            'Eshkol singleton witnesses differ')
    require(result['biased_distribution_max_win_numerators'] == maxima == [55]*6,
            'Biased-setting extremizers differ')
    require(result['minimum_violations'] == 1 and result['classical_win_cap_numerator'] == 11,
            'Incorrect bias floor bound')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=20261110)
    parser.add_argument('--trials', type=int, default=6000)
    parser.add_argument('--eshkol-run', default=os.environ.get('ESHKOL_RUN'))
    parser.add_argument('--cc', default=os.environ.get('CC', 'gcc'))
    args = parser.parse_args()
    require(0 <= args.seed < 2**53-1, 'seed must permit exact JS replay plus seed+1')
    require(1 <= args.trials <= 100000, 'trials must be 1..100000')
    BUILD.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    report_path = RESULTS / 'stack_report.json'
    report_path.write_text(json.dumps({'status': 'running'})+'\n', encoding='utf-8')
    started = time.monotonic()
    try:
        pins = json.loads((ROOT/'third_party/SHA256SUMS.json').read_text())
        for rel, expected in pins.items():
            require(sha(ROOT/'third_party'/rel) == expected, 'Pinned file changed: '+rel)
        exe = BUILD / ('stack_qrng.exe' if os.name == 'nt' else 'stack_qrng')
        run([args.cc, '-O2', '-std=gnu11', 'src/stack_qrng.c',
             'third_party/quantum_rng/src/quantum_rng/quantum_rng.c',
             '-Ithird_party/quantum_rng/src/quantum_rng', '-o', exe, '-lm'], 'qrng_build')
        first = run([exe, args.seed, 4096], 'qrng_first')
        repeat = run([exe, args.seed, 4096], 'qrng_repeat')
        different = run([exe, args.seed+1, 4096], 'qrng_other_seed')
        require(first == repeat and first != different and len(bytes.fromhex(first)) == 4096,
                'QRNG same-build seeded replay failed')
        print('PASS QRNG native seeded software stream and replay', flush=True)
        run(['node', 'src/stack_moonlab.mjs', args.seed, args.trials], 'moonlab_run')
        moonlab = json.loads((RESULTS/'stack_moonlab.json').read_text())
        trials = json.loads((RESULTS/'stack_trials.json').read_text())
        shots = json.loads((RESULTS/'stack_shots.json').read_text())
        require(len(trials) == len(shots) == args.trials, 'Incomplete shot log')
        for trial, shot in zip(trials, shots):
            require(trial == {'context': shot['context'], 'success': shot['success']},
                    'Trial projection disagrees with auditable shot log')
            parity = np.prod(shot['recorded_outcomes'])
            sign = -1 if trial['context'] == 5 else 1
            require(bool(parity == sign) == trial['success'], 'Outcome parity mismatch')
            require(all(b == (-a if flip else a) for a, b, flip in zip(
                shot['ideal_outcomes'], shot['recorded_outcomes'], shot['readout_flips'])),
                'Injected noise does not match recorded outcomes')
        print('PASS Moonlab sequential Pauli measurements and %d auditable noisy trials' % args.trials, flush=True)
        geometry = qgtl(args.cc)
        print('PASS QGTL analytic geometry, gauge invariance and wrong-sign control', flush=True)
        eshkol = args.eshkol_run or shutil.which('eshkol-run')
        if not eshkol and os.name == 'nt':
            local = Path('Z:/Tools/eshkol/current/bin/eshkol-run.exe')
            if local.is_file():
                eshkol = str(local)
        require(eshkol and Path(eshkol).is_file(), 'ESHKOL_RUN or --eshkol-run required')
        env = os.environ.copy()
        if os.name == 'nt' and Path('Z:/Tools/LLVM-21/bin/clang++.exe').is_file():
            env.update(ESHKOL_CXX_COMPILER='Z:/Tools/LLVM-21/bin/clang++.exe',
                       LLVM_HOME='Z:/Tools/LLVM-21',
                       ESHKOL_CUDA_LIBRARY_PATH='Z:/Tools/cuda-12.9-redist/lib/x64',
                       CUDA_HOME='Z:/Tools/cuda-12.9-redist')
            env['PATH'] = 'Z:/Tools/cuda-12.9-redist/bin;' + env['PATH']
        output = run([eshkol, '-r', 'src/stack_enumeration.esk'], 'eshkol', env)
        exact = json.loads(next(line for line in output.splitlines() if line.startswith('{')))
        verify_eshkol(exact)
        print('PASS Eshkol exhaustive assignments, singleton witnesses and biased extrema', flush=True)
        sources = sorted(list((ROOT/'third_party').rglob('*')) +
                         list((ROOT/'src').glob('stack_*')) + [Path(__file__).resolve()])
        report = {'status': 'pass', 'classification': 'Classical software experiment; no quantum hardware or certified entropy',
                  'elapsed_seconds': time.monotonic()-started,
                  'platform': platform.platform(), 'python': sys.version.split()[0], 'numpy': np.__version__,
                  'node': run(['node', '--version'], 'node_version').strip(),
                  'gcc': run([args.cc, '--version'], 'gcc_version').splitlines()[0],
                  'verified_vendor_files': len(pins),
                  'qrng': {'status': 'pass', 'seed': args.seed, 'same_build_replay_identical': True,
                           'different_seed_differs': True, 'stream_4096_sha256': hashlib.sha256(bytes.fromhex(first)).hexdigest(),
                           'binary_sha256': sha(exe)},
                  'moonlab': moonlab, 'qgtl': geometry,
                  'eshkol': {'status': 'pass', 'version': run([eshkol, '--version'], 'eshkol_version', env).strip(),
                             'executable_sha256': sha(eshkol), 'exact_enumeration': exact},
                  'artifacts_sha256': {p.name: sha(p) for p in [RESULTS/'stack_trials.json', RESULTS/'stack_shots.json', RESULTS/'stack_tangents.json']},
                  'source_sha256': {str(p.relative_to(ROOT)).replace('\\','/'): sha(p) for p in sources if p.is_file()}}
        report_path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print('ALL FOUR TSOTCHKE COMPONENTS PASSED', flush=True)
    except Exception as exc:
        report_path.write_text(json.dumps({'status': 'fail', 'error_type': type(exc).__name__, 'error': str(exc)}, indent=2)+'\n', encoding='utf-8')
        raise


if __name__ == '__main__':
    main()
