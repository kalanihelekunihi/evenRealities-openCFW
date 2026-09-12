import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    'dependencies', Path(__file__).resolve().parents[1] / 'tools/continue_analysis_dependencies.py')
dependencies = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dependencies)


class DependencyTests(unittest.TestCase):
    def test_classifies_operational_failures(self):
        self.assertEqual(dependencies.analyze_failure_text(
            "You've hit your session limit; resets 4:30pm")['kind'], 'usage-limit')
        self.assertTrue(dependencies.analyze_failure_text(
            'integration lock timeout while held by AM-009')['retryable'])
        self.assertEqual(dependencies.analyze_failure_text(
            'arc-linux-gnu-gcc not installed')['kind'], 'tool')
        self.assertFalse(dependencies.analyze_failure_text(
            'authentication failed')['retryable'])
        self.assertEqual(dependencies.analyze_failure_text(
            'Not logged in · Please run /login')['kind'], 'authentication')

    def test_infers_exact_dependencies_from_historical_prose(self):
        result = {
            'blockers': ['0x0042D5CC blocked on BL-005; six spans need BL-011/BL-012'],
            'followups': ['Reconstruct after BL-005 lands'],
        }
        found = dependencies.infer_dependencies(
            result, 'BL-009', {'BL-005', 'BL-009', 'BL-011', 'BL-012'})
        self.assertEqual([item['id'] for item in found], ['BL-005', 'BL-011', 'BL-012'])

    def test_explicit_dependencies_take_precedence(self):
        result = {
            'dependencies': [{'id': 'TC-001', 'reason': 'routing target',
                              'required_for': 'completion'}],
            'followups': ['Unrelated mention of CS-001'],
        }
        found = dependencies.infer_dependencies(result, 'TC-002', {'TC-001', 'TC-002', 'CS-001'})
        self.assertEqual([item['id'] for item in found], ['TC-001'])

    def test_explicit_empty_dependencies_suppress_prose_inference(self):
        result = {'dependencies': [], 'followups': ['TC-001 may consume this later']}
        self.assertEqual(dependencies.infer_dependencies(
            result, 'TC-002', {'TC-001', 'TC-002'}), [])

    def test_record_becomes_ready_when_dependency_finishes(self):
        result = {
            'status': 'partial', 'summary': 'source complete, routing pending',
            'dependencies': [{'id': 'TC-001', 'reason': 'routing target'}],
            'remaining_segments': ['rerun production gate'],
            'blockers': ['hardware qualification unavailable'],
        }
        record = dependencies.build_record(
            result, 'TC-002', 'result.json', {'TC-001', 'TC-002'}, {'TC-001': 'failed'})
        self.assertEqual(record['pending_dependencies'], ['TC-001'])
        self.assertFalse(record['ready_for_completion'])
        record = dependencies.refresh_record(record, {'TC-001': 'done'})
        self.assertEqual(record['pending_dependencies'], [])
        self.assertTrue(record['ready_for_completion'])
        self.assertEqual(record['missing_requirements'][0]['kind'], 'hardware')

    def test_unknown_explicit_dependency_is_preserved(self):
        result = {'status': 'partial', 'dependencies': [{'id': 'BL-999', 'reason': 'needed'}]}
        record = dependencies.build_record(
            result, 'BL-009', 'result.json', {'BL-009'}, {'BL-009': 'partial'})
        self.assertEqual(record['unresolved_dependencies'], ['BL-999'])
        self.assertEqual(record['pending_dependencies'], ['BL-999'])
        self.assertEqual(record['missing_requirements'][0]['kind'], 'dependency')

    def test_record_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            record = {'id': 'AM-001', 'dependencies': [], 'pending_dependencies': []}
            dependencies.save_record(directory, record)
            self.assertEqual(dependencies.load_record(directory, 'AM-001'), record)
            self.assertEqual(json.loads((Path(directory) / 'AM-001.json').read_text()), record)

    def test_operational_failure_does_not_replace_saved_progress(self):
        record = {
            'id': 'BL-009', 'summary': '810 bytes already source-owned',
            'files_changed': ['runtime.c'],
            'dependencies': [{'id': 'BL-005', 'reason': 'needed'}],
            'unresolved_dependencies': [], 'missing_requirements': [],
        }
        issue = {'kind': 'authentication', 'retryable': False,
                 'description': 'authentication failed'}
        merged = dependencies.merge_failure(record, issue, 'failed.json', {'BL-005': 'failed'})
        self.assertEqual(merged['summary'], '810 bytes already source-owned')
        self.assertEqual(merged['files_changed'], ['runtime.c'])
        self.assertEqual(merged['pending_dependencies'], ['BL-005'])
        self.assertEqual(merged['last_failure']['kind'], 'authentication')


if __name__ == '__main__':
    unittest.main()
