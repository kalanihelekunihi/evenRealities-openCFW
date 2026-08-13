import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/analyze_g2_nvdb_sensor_caldata.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_nvdb_sensor_caldata", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AnalyzeG2NvdbSensorCaldataTests(unittest.TestCase):
    def test_authenticated_closure(self) -> None:
        report = MODULE.analyze()
        self.assertEqual(report["functions"], 8)
        self.assertEqual(report["body_bytes"], 900)
        self.assertEqual(report["entry_calls"], 10)
        self.assertEqual(report["stored_entries"], 4)
        self.assertEqual(report["strict_interior_ingress"], 0)
        self.assertEqual(report["raw_unaligned_interior_windows"], 2)
        self.assertEqual(report["primary_record"]["initialized_crc16"], "0xD886")
        self.assertEqual(report["ag_record"]["initialized_crc16"], "0x82FC")

    def test_factory_records_and_matrix(self) -> None:
        self.assertEqual(len(MODULE.PRIMARY_BOOT_RECORD), 92)
        self.assertEqual(len(MODULE.AG_BOOT_RECORD), 68)
        self.assertEqual(MODULE.AG_BOOT_RECORD[28:64].hex(), MODULE.DEFAULT_MATRIX_HEX)
        self.assertEqual(
            MODULE.sha256(bytes.fromhex(MODULE.DEFAULT_MATRIX_HEX)),
            MODULE.DEFAULT_MATRIX_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
