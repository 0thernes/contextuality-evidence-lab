"""Independent brute-force and adversarial checks of the evidence engine."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from evidence import (Bet, enumerate_square, outcomes, sharp_classical_bound,
                      exact_hitting_probability, replay, validate_distribution)


class EvidenceTests(unittest.TestCase):
    def test_parity_structure(self):
        report = enumerate_square()
        self.assertEqual(report['failure_histogram'], {1: 96, 3: 320, 5: 96})
        for context, witness in report['singleton_witnesses'].items():
            self.assertEqual(outcomes(witness), tuple(i != context for i in range(6)))

    def test_sharp_bound_for_heterogeneous_distributions(self):
        rng = random.Random(43)
        for _ in range(25):
            counts = [rng.randrange(20) for _ in range(6)]
            p = tuple(F(c, sum(counts)) for c in counts)
            self.assertEqual(sharp_classical_bound(p), 1 - min(p))

    def test_every_adversarial_assignment_and_simplex_vertex(self):
        bet = Bet()
        # Vertices of the setting-distribution polytope p_i >= beta.
        for vertex in range(6):
            p = [bet.beta] * 6
            p[vertex] += 1 - 6 * bet.beta
            for assignment in range(512):
                mean = sum(pi * bet.factor(win) for pi, win in zip(p, outcomes(assignment)))
                self.assertLessEqual(mean, 1)

    def test_exceptional_mixture_budget(self):
        bet = Bet(delta=F(1, 5), q=F(29, 30))
        self.assertEqual(bet.bound, F(14, 15))
        self.assertEqual(bet.null_mean(), 1)
        # Null can win with probability 1 on the explicitly budgeted 1/5 component.
        mean = F(4, 5) * (F(11, 12) * bet.a + F(1, 12) * bet.b) + F(1, 5) * bet.a
        self.assertEqual(mean, 1)

    def test_absorption_dp_against_independent_path_enumeration(self):
        bet = Bet(beta=F(1, 6), q=F(19, 20))
        p, horizon, threshold = F(5, 6), 9, F(3, 2)
        hit = F(0)
        for path in product((False, True), repeat=horizon):
            wealth, ever = F(1), False
            for win in path:
                wealth *= bet.factor(win)
                ever |= wealth >= threshold
            if ever:
                s = sum(path)
                hit += p ** s * (1 - p) ** (horizon - s)
        self.assertEqual(exact_hitting_probability(bet, p, horizon, threshold), hit)

    def test_exact_counterexample_to_miscalibration(self):
        naive = Bet(beta=F(1, 6))
        self.assertGreater(naive.a ** 36, 100)
        self.assertGreater(F(11, 12) ** 36, F(1, 100))
        self.assertLess(Bet().a ** 36, 100)

    def test_finite_optional_stopping_bound(self):
        for bet in (Bet(), Bet(beta=F(1, 6))):
            probability = exact_hitting_probability(bet, bet.bound, 200, 20)
            self.assertLessEqual(probability, F(1, 20))

    def test_reject_unsafe_contracts(self):
        for kwargs in ({'success_factor': F(6, 5)}, {'failure_factor': -1},
                       {'beta': 0}, {'beta': F(1, 5)}, {'q': F(1, 2)}, {'delta': 1}):
            with self.assertRaises(ValueError):
                Bet(**kwargs)
        with self.assertRaises(ValueError):
            validate_distribution((F(11, 60),) * 5 + (F(1, 12),), F(1, 6))
        with self.assertRaises(ValueError):
            replay([{'success': 1}], Bet())


if __name__ == '__main__':
    unittest.main()
