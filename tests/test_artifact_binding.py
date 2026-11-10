"""Adversarial mutations must not be accepted as successful native evidence."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from run_experiment import load_native_trials


class ArtifactBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((ROOT / 'results/stack_report.json').read_text())

    def fixture(self, root):
        (root / 'results').mkdir()
        shutil.copy2(ROOT / 'results/stack_report.json', root / 'results/stack_report.json')
        for name in self.report['artifacts_sha256']:
            shutil.copy2(ROOT / 'results' / name, root / 'results' / name)
        for name in self.report['source_sha256']:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)

    def test_current_artifact_and_stale_failure_rejected(self):
        self.assertEqual(len(load_native_trials()), 6000)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            report = dict(self.report, status='fail')
            (root / 'results/stack_report.json').write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, 'successful execution'):
                load_native_trials(root)

    def test_changed_transcript_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            path = root / 'results/stack_trials.json'
            data = json.loads(path.read_text())
            data[0]['success'] = not data[0]['success']
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'fingerprint mismatch'):
                load_native_trials(root)

    def test_changed_source_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            with (root / 'src/stack_moonlab.mjs').open('a') as out:
                out.write('\n// changed after the run\n')
            with self.assertRaisesRegex(ValueError, 'source changed'):
                load_native_trials(root)


if __name__ == '__main__':
    unittest.main()
