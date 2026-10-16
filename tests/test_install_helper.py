import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('install_helper', Path(__file__).resolve().parents[1] / 'scripts/install_helper.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class InstallTests(unittest.TestCase):
    def test_old_node_cannot_claim_ready(self):
        with patch.object(helper, 'probe', side_effect=['ok', 'v20.19.0']):
            result = helper.status()
        self.assertFalse(result['documents_ready'])
        self.assertFalse(result['editor_ready'])

    def test_missing_packages_cannot_claim_ready(self):
        with patch.object(helper, 'probe', side_effect=[None, 'v22.0.0']):
            self.assertFalse(helper.status()['documents_ready'])

    def test_check_is_read_only_and_prefers_venv(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            python = root / 'python'
            python.touch()
            before = list(root.iterdir())
            with patch.object(helper, 'ROOT', root), patch.object(helper, 'PYTHON', python), patch.object(helper, 'probe', side_effect=['ok', 'v22.0.0']) as probe:
                result = helper.status()
            self.assertEqual(str(python), probe.call_args_list[0].args[0][0])
            self.assertTrue(result['documents_ready'])
            self.assertFalse(result['editor_ready'])
            self.assertEqual(before, list(root.iterdir()))

    def test_missing_node_stops_before_mutation(self):
        with patch.object(helper, 'status', return_value={'node22': False}), patch.object(helper, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'Node.js'):
                helper.install()
            run.assert_not_called()

    def test_failed_command_is_not_success(self):
        import io
        import subprocess
        with patch.object(helper.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1)):
            with self.assertRaises(RuntimeError):
                helper.run(['false'], io.StringIO())

    def test_rerun_reuses_environment_and_packages(self):
        import io
        with patch.object(helper, 'status', return_value={'node22': True, 'editor_ready': True}), patch.object(Path, 'exists', return_value=True), patch.object(Path, 'open', return_value=io.StringIO()), patch.object(helper, 'probe', return_value='ok'), patch.object(helper, 'run') as run:
            helper.install()
            self.assertEqual(run.call_count, 1)
            self.assertTrue(str(run.call_args.args[0][-1]).endswith('setup.mjs'))


if __name__ == '__main__':
    unittest.main()
