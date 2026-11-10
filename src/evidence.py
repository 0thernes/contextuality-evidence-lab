"""Exact, bias-aware evidence for the six-context Peres--Mermin value-table model.

Only the rational arithmetic and finite-model certificate are implemented here.
No transcript can certify the conditional setting-independence assumptions.
"""
from fractions import Fraction as F
from math import log10

CONTEXTS = ((0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8))
OBSERVABLES = ('XI', 'IX', 'XX', 'IZ', 'ZI', 'ZZ', 'XZ', 'ZX', 'YY')
NEGATIVE = (False, False, False, False, False, True)


def outcomes(mask, negative=NEGATIVE):
    """Success vector of one context-independent table of nine +/-1 values."""
    if not isinstance(mask, int) or not 0 <= mask < 512:
        raise ValueError('assignment must be an integer in [0, 512)')
    if len(negative) != 6:
        raise ValueError('six signs required')
    return tuple((sum((mask >> j) & 1 for j in c) % 2) == int(sign)
                 for c, sign in zip(CONTEXTS, negative))


def enumerate_square():
    hist, singleton = {}, {}
    for mask in range(512):
        wins = outcomes(mask)
        failures = tuple(i for i, win in enumerate(wins) if not win)
        hist[len(failures)] = hist.get(len(failures), 0) + 1
        if not failures:
            raise AssertionError('all-winning value table contradicts the model')
        if len(failures) == 1:
            singleton.setdefault(failures[0], mask)
    if len(singleton) != 6:
        raise AssertionError('sharpness witnesses missing')
    return {'assignments': 512, 'failure_histogram': hist,
            'singleton_witnesses': singleton}


def validate_distribution(probabilities, beta=F(0)):
    p = tuple(F(x) for x in probabilities)
    if len(p) != 6 or sum(p) != 1 or min(p) < F(beta):
        raise ValueError('distribution must sum to one and respect every floor')
    if F(beta) < 0:
        raise ValueError('negative context floor')
    return p


def sharp_classical_bound(probabilities):
    p = validate_distribution(probabilities)
    exact = max(sum(pi for pi, win in zip(p, outcomes(mask)) if win)
                for mask in range(512))
    if exact != 1 - min(p):
        raise AssertionError('enumeration disagrees with the sharp bound')
    return exact


class Bet:
    """Rational nonnegative factor certificate; q is fixed before seeing a shot.

    delta describes an explicit exceptional-trial mixture, not a measured
    disturbance or an estimate from the same test transcript.
    """
    def __init__(self, beta=F(1, 12), q=F(19, 20), delta=F(0),
                 success_factor=None, failure_factor=None):
        self.beta, self.q, self.delta = F(beta), F(q), F(delta)
        if not 0 < self.beta <= F(1, 6) or not 0 <= self.delta < 1:
            raise ValueError('require 0 < beta <= 1/6 and 0 <= delta < 1')
        self.bound = 1 - (1 - self.delta) * self.beta
        if not self.bound <= self.q <= 1:
            raise ValueError('predicted success must be at least the null bound')
        self.a = (self.q / self.bound if success_factor is None
                  else F(success_factor))
        self.b = ((1 - self.q) / (1 - self.bound) if failure_factor is None
                  else F(failure_factor))
        if not self.a >= self.b >= 0:
            raise ValueError('require success factor >= failure factor >= 0')
        if self.null_mean() > 1:
            raise ValueError('unsafe certificate: worst-case expected factor > 1')

    def null_mean(self):
        return self.bound * self.a + (1 - self.bound) * self.b

    def factor(self, success):
        if not isinstance(success, bool):
            raise ValueError('shot success must be a Boolean')
        return self.a if success else self.b

    def certificate(self):
        return {key: str(value) for key, value in (
            ('beta', self.beta), ('delta', self.delta), ('q', self.q),
            ('null_success_bound', self.bound), ('success_factor', self.a),
            ('failure_factor', self.b), ('worst_case_mean_factor', self.null_mean()))}


def replay(trials, bet, threshold=100, stride=10):
    """Check crossing with integers/Fractions. Logarithms are display only."""
    threshold = F(threshold)
    if threshold <= 1:
        raise ValueError('threshold must exceed one')
    capital, maximum, first, successes, failures = F(1), F(1), None, 0, 0
    trace = [{'trial': 0, 'log10_capital': 0.0}]
    for n, record in enumerate(trials, 1):
        success = record['success']
        if not isinstance(success, bool):
            raise ValueError('non-Boolean trial result')
        capital *= bet.factor(success)
        successes += int(success)
        failures += int(not success)
        maximum = max(maximum, capital)
        if first is None and capital >= threshold:
            first = n
        if n % stride == 0 or n == len(trials):
            trace.append({'trial': n, 'log10_capital': log_fraction(capital)})
    return {'trials': len(trials), 'successes': successes, 'failures': failures,
            'success_rate': successes / len(trials) if trials else None,
            'first_crossing': first, 'threshold': str(threshold),
            'final_log10_capital': log_fraction(capital),
            'maximum_log10_capital': log_fraction(maximum),
            'anytime_p_upper_display': min(1.0, 10 ** (-log_fraction(maximum))),
            'certificate': bet.certificate(), 'trace': trace}


def log_fraction(value):
    if value == 0:
        return float('-inf')
    return log10(value.numerator) - log10(value.denominator)


def exact_hitting_probability(bet, true_success, horizon, threshold=100):
    """Exact IID finite-horizon benchmark, absorbing on the FIRST crossing.

    All surviving paths with the same success count share capital. Integer
    path masses use a common probability denominator d**n at depth n.
    The theorem is more general than this IID benchmark.
    """
    success = F(true_success)
    if not 0 <= success <= 1 or horizon < 0 or F(threshold) <= 1:
        raise ValueError('invalid finite-horizon parameters')
    sn, d = success.numerator, success.denominator
    fn = d - sn
    an, ad = bet.a.numerator, bet.a.denominator
    bn, bd = bet.b.numerator, bet.b.denominator
    apn, apd, bpn, bpd = [1], [1], [1], [1]
    for _ in range(horizon):
        apn.append(apn[-1] * an); apd.append(apd[-1] * ad)
        bpn.append(bpn[-1] * bn); bpd.append(bpd[-1] * bd)
    target = F(threshold)
    alive, absorbed, denominator = {0: 1}, 0, 1
    for n in range(1, horizon + 1):
        nxt = {}
        absorbed *= d
        denominator *= d
        for s, mass in alive.items():
            for ns, weight in ((s + 1, sn), (s, fn)):
                if weight == 0:
                    continue
                f = n - ns
                crossing = (apn[ns] * bpn[f] * target.denominator >=
                            target.numerator * apd[ns] * bpd[f])
                if crossing:
                    absorbed += mass * weight
                else:
                    nxt[ns] = nxt.get(ns, 0) + mass * weight
        alive = nxt
    if absorbed + sum(alive.values()) != denominator:
        raise AssertionError('probability mass was lost')
    return F(absorbed, denominator)


def fraction_record(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator),
            'decimal': float(value)}
