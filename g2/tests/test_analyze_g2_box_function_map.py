import importlib.util
import sys
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_box_function_map.py"
S = importlib.util.spec_from_file_location("g2_box_function_map", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class BoxFunctionMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.r["rows"]}

    def test_identity(self):
        self.assertEqual(self.r["identity"]["sha256"],
                         "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374")
        self.assertEqual(self.r["identity"]["app_bytes"], 55752)
        self.assertEqual(self.r["identity"]["language"], "ARM:LE:32:Cortex")
        self.assertEqual(
            self.r["identity"]["decomp_c_sha256"],
            "63bfbc4e2a105b19953d825cb29aced1111399315eb33a1edb09200581ae3452")

    def test_map_totals(self):
        m = self.r["map"]
        self.assertEqual(m["discovered_functions"], 428)
        self.assertEqual(m["supplemental_entry_rows"], 7)
        self.assertEqual(m["discovered_function_bytes"], 40664)
        self.assertEqual(m["app_bytes_outside_discovered_functions"], 15088)
        self.assertEqual(m["category_counts"], {
            "generated_transport": 0,
            "upstream_cmsis_startup": 14,
            "upstream_freertos_kernel": 79,
            "upstream_stm32_hal": 10,
            "first_party_g2": 71,
            "device_specific_preserve": 0,
            "unresolved": 261,
        })
        self.assertEqual(m["category_bytes"], {
            "generated_transport": 0,
            "upstream_cmsis_startup": 292,
            "upstream_freertos_kernel": 5440,
            "upstream_stm32_hal": 1018,
            "first_party_g2": 16994,
            "device_specific_preserve": 0,
            "unresolved": 16920,
        })
        self.assertEqual(m["combined_category_bytes"], {
            "generated_transport": 0,
            "upstream_cmsis_startup": 484,
            "upstream_freertos_kernel": 5440,
            "upstream_stm32_hal": 1018,
            "first_party_g2": 29706,
            "device_specific_preserve": 0,
            "unresolved": 19104,
        })
        self.assertEqual(sum(m["combined_category_bytes"].values()), 55752)
        self.assertEqual(sum(m["category_bytes"].values()), 40664)

    def test_anchor_rows(self):
        anchors = {
            0x08000102: ("xPortPendSVHandler", "upstream_freertos_kernel", 62),
            0x08008420: ("systick_gate", "upstream_freertos_kernel", 20),
            0x0800C5AC: ("xPortSysTickHandler", "upstream_freertos_kernel", 32),
            0x0800CA4C: ("xTaskGetSchedulerState", "upstream_freertos_kernel", 26),
            0x0800CA78: ("xTaskIncrementTick", "upstream_freertos_kernel", 184),
            0x08005F50: ("HAL_UART_IRQHandler", "upstream_stm32_hal", 732),
            0x08008FA8: ("gls_frame_pack_l", "first_party_g2", 84),
            0x08009004: ("gls_frame_pack_r", "first_party_g2", 54),
        }
        for entry, (name, cat, size) in anchors.items():
            row = self.rows[entry]
            self.assertEqual(row["name"], name)
            self.assertEqual(row["ownership_category"], cat)
            self.assertEqual(row["size"], size)

    def test_verified_kernel_names(self):
        names = {
            0x0800C390: "vTaskSwitchContext",
            0x0800BF2C: "uxListRemove",
            0x0800C9A8: "xTaskCreate",
            0x0800B3E8: "pvPortMalloc",
            0x0800B4C0: "pxPortInitialiseStack",
            0x0800B0FC: "prvTimerTask",
            0x080000CC: "vPortStartFirstTask",
        }
        for entry, name in names.items():
            self.assertEqual(self.rows[entry]["name"], name)
            self.assertEqual(self.rows[entry]["ownership_category"],
                             "upstream_freertos_kernel")

    def test_hal_members(self):
        self.assertEqual(self.rows[0x08004B6C]["name"], "HAL_FLASH_Unlock")
        self.assertEqual(self.rows[0x08004BF4]["name"], "HAL_FLASH_OB_Unlock")
        for entry in (0x0800487A, 0x080048E6, 0x08005E6A, 0x08005E6C,
                      0x08005EFC, 0x08005EFE, 0x08005F42):
            self.assertEqual(self.rows[entry]["ownership_category"],
                             "upstream_stm32_hal")

    def test_first_party_members(self):
        self.assertEqual(self.rows[0x08009170]["name"], "g2_log_printf")
        self.assertEqual(self.rows[0x08001E94]["name"],
                         "gls_frame_validate_dispatch")
        self.assertEqual(self.rows[0x08002CC0]["name"],
                         "ota_image_be32_sum_verify")
        self.assertEqual(self.rows[0x08006968]["name"], "app_rtos_init")
        for entry, cat in ((0x08006968, "first_party_g2"),
                           (0x08002F60, "first_party_g2"),
                           (0x0800373C, "first_party_g2")):
            self.assertEqual(self.rows[entry]["ownership_category"], cat)
        # Seven entry points are outside the discovered map.
        supplemental = [r for r in self.r["rows"] if not r["discovered"]]
        self.assertEqual(len(supplemental), 7)
        for r in supplemental:
            self.assertEqual(r["ownership_category"], "first_party_g2")
            self.assertEqual(r["size"], 0)
        self.assertEqual({r["entry"] for r in supplemental},
                         {0x08009D70, 0x0800B7EC, 0x0800BB90, 0x08006E1C,
                          0x08007F2C, 0x08007200, 0x080082EC})

    def test_freertos_closure_membership(self):
        members = set(self.r["map"]["freertos_kernel_members"])
        self.assertEqual(len(members), 79)
        for required in (0x0800C390, 0x0800CA78, 0x0800C9A8, 0x0800AA48,
                         0x0800A93C, 0x0800A836, 0x0800BF2C, 0x0800B0FC,
                         0x0800B3E8, 0x0800B4C0):
            self.assertIn(required, members)
        # String-referencing app code must never enter the kernel set.
        self.assertNotIn(0x08009170, members)
        self.assertNotIn(0x08001E94, members)

    def test_gap_rows(self):
        gaps = self.r["gap_rows"]
        self.assertGreaterEqual(len(gaps), 1)
        lead = gaps[0]
        self.assertEqual(lead["start"], 0x08000000)
        self.assertEqual(lead["ownership_category"], "upstream_cmsis_startup")
        descriptor_gaps = [g for g in gaps
                           if g["ownership_category"] == "first_party_g2"
                           and "descriptor" in g["evidence"]]
        self.assertTrue(descriptor_gaps)
        gap_sum = sum(g["bytes"] for g in gaps)
        self.assertEqual(gap_sum, 15088)

    def test_resolutions(self):
        res = self.r["resolutions"]
        self.assertIn("8-bit additive sum", res["crc_verdict"])
        self.assertIn("no polynomial CRC", res["crc_verdict"])
        self.assertIn("big-endian u32 words", res["crc_verdict"])
        self.assertIn("ADR", res["log_scheme_verdict"])
        self.assertIn("no string-stripping", res["log_scheme_verdict"])
        self.assertIn("CMSIS-RTOS2", res["rtos_wrapper_verdict"])

    def test_categories(self):
        self.assertEqual(self.r["ownership_categories"], [
            "generated_transport", "upstream_cmsis_startup",
            "upstream_freertos_kernel", "upstream_stm32_hal",
            "first_party_g2", "device_specific_preserve", "unresolved",
        ])
        self.assertEqual(len(self.r["rows"]), 435)


if __name__ == "__main__":
    unittest.main()
