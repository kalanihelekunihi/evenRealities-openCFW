# SPDX-License-Identifier: MIT
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from harvest_gx8002_known_functions import prepare_processor


class ProcessorPreparationTests(unittest.TestCase):
    def test_changed_processor_rule_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            name = 'C-SKY/data/languages/32b_data.sinc'
            source = root / 'upstream' / name
            source.parent.mkdir(parents=True)
            source.write_text('unknown processor definition\n')
            with patch('harvest_gx8002_known_functions.subprocess.check_output', return_value=name+'\n'):
                with self.assertRaisesRegex(ValueError, 'processor source changed'):
                    prepare_processor(root / 'upstream', root / 'build')
            self.assertEqual(source.read_text(), 'unknown processor definition\n')


if __name__ == '__main__':
    unittest.main()
