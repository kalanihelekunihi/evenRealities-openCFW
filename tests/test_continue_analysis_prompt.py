"""Exercise the actual embedded renderer without touching the live work queue."""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import textwrap
import unittest
import os


ROOT = Path(__file__).resolve().parents[1]


class PromptTests(unittest.TestCase):
    def render(self, item, row):
        script = (ROOT / 'continue-analysis.sh').read_text()
        source = script.split("<<'PY'\n", 1)[1].split('\nPY\n', 1)[0]
        tree = ast.parse(source)
        renderer = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'render_prompt')
        with tempfile.TemporaryDirectory() as directory:
            scope = dict(os=os, json=json, hashlib=hashlib, textwrap=textwrap,
                         ROOT=str(ROOT), STATE=directory, DEFERRED=directory,
                         ALLOW_COMMIT=False, META_GEN='test', PLAYBOOK={},
                         load_record=lambda *args: None)
            exec(compile(ast.Module(body=[renderer], type_ignores=[]), str(ROOT / 'continue-analysis.sh'), 'exec'), scope)
            return scope['render_prompt'](item, row)

    def test_assignment_keeps_gates_and_uses_bounded_durable_context(self):
        item = dict(id='AM-001', component='apollo_main', priority='P1', kind='code',
                    route='source', summary='Recover a bounded cluster',
                    start='0x00438000', end='0x00438010', bytes=16)
        rendered = self.render(item, {'status': 'todo', 'notes': 'HISTORY_SENTINEL' * 1000})
        self.assertIn('EXECUTION MODE: reconstruction', rendered)
        self.assertIn('knowledge/AM-001.json', rendered)
        self.assertIn('rejected_hypotheses', rendered)
        self.assertIn('working-tree', rendered)
        self.assertNotIn('HISTORY_SENTINEL', rendered)
        self.assertIn('CA-STATUS:', rendered)
        self.assertIn('production-routed', rendered)
        self.assertIn('lock acquire AM-001', rendered)
        self.assertIn('do not launch additional workers', rendered)
        self.assertNotIn('EXECUTION MODE: reconstruction (tooling', rendered)
        self.assertIn('do not substitute workflow improvements', rendered)
        self.assertIn('Checkpoints are intermediate saves', rendered)

    def test_tooling_item_gets_unambiguous_mode(self):
        item = dict(id='XC-001', component='cross-cutting', priority='P1', kind='tooling',
                    route='tooling', summary='Improve a gate', start='-', end='-', bytes=0)
        rendered = self.render(item, {'status': 'todo'})
        self.assertIn('EXECUTION MODE: tooling.', rendered)
        self.assertNotIn('EXECUTION MODE: reconstruction', rendered)


if __name__ == '__main__':
    unittest.main()
