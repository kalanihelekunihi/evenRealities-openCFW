"""Ensure capture merging refuses incompatible or ambiguous inputs."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('merge_case_backup', Path(__file__).resolve().parents[1] / 'tools/merge_case_backup.py')
merge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(merge)


class MergeCaseBackupTests(unittest.TestCase):
    def setUp(self):
        self.raw = bytes(range(32))
        self.bank = bytearray(b'\xff' * merge.BANK_SIZE)
        self.bank[:len(self.raw)] = self.raw
        self.bank[merge.DATA_START:merge.DATA_START + 4] = b'DATA'

    def test_preserves_captured_data_and_erased_gap(self):
        result = merge.merge_bank(self.raw, bytes(self.bank))
        self.assertEqual(result, bytes(self.bank))
        self.assertEqual(result[merge.DATA_START:merge.DATA_START + 4], b'DATA')

    def test_rejects_different_application(self):
        with self.assertRaisesRegex(ValueError, 'exact backup match'):
            merge.merge_bank(b'\xff' * 32, bytes(self.bank))

    def test_rejects_unexplained_tail(self):
        self.bank[100] = 0
        with self.assertRaisesRegex(ValueError, 'non-erased'):
            merge.merge_bank(self.raw, bytes(self.bank))

    def test_rejects_device_data_overlap(self):
        with self.assertRaisesRegex(ValueError, 'overlaps'):
            merge.merge_bank(b'\xff' * (merge.DATA_START + 1), bytes(self.bank))

    def test_refuses_overwrite_but_allows_identical_rerun(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'image.bin'
            merge.write_verified(path, b'first')
            merge.write_verified(path, b'first')
            with self.assertRaisesRegex(ValueError, 'overwrite'):
                merge.write_verified(path, b'second')
            self.assertEqual(path.read_bytes(), b'first')


if __name__ == '__main__':
    unittest.main()
