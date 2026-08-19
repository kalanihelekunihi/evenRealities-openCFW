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

    def test_production_routed(self) -> None:
        production = MODULE.analyze()["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 900)
        self.assertEqual(production["retained_stock_noncode_bytes"], 96)
        self.assertEqual(production["toolchain_profiles"], ["apple-clang"])
        self.assertEqual(production["relocated_leaves"], [
            "open_cfw_nvdb_sensor_caldata_ag_default_initialize",
            "open_cfw_nvdb_sensor_caldata_ag_load_and_migrate",
            "open_cfw_nvdb_sensor_caldata_ag_read",
            "open_cfw_nvdb_sensor_caldata_ag_update",
            "open_cfw_nvdb_sensor_caldata_check",
            "open_cfw_nvdb_sensor_caldata_default_initialize",
            "open_cfw_nvdb_sensor_caldata_load_and_migrate",
            "open_cfw_nvdb_sensor_caldata_update",
        ])
        self.assertEqual(production["patch_sites"], [
            "replace_nvdb_sensor_caldata_ag_default_initialize",
            "replace_nvdb_sensor_caldata_ag_load_and_migrate",
            "replace_nvdb_sensor_caldata_ag_read",
            "replace_nvdb_sensor_caldata_ag_update",
            "replace_nvdb_sensor_caldata_check",
            "replace_nvdb_sensor_caldata_default_initialize",
            "replace_nvdb_sensor_caldata_load_and_migrate",
            "replace_nvdb_sensor_caldata_update",
        ])


if __name__ == "__main__":
    unittest.main()
