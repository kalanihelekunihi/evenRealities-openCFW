import importlib.util
import sys
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_box_stm32g0_platform.py"
S = importlib.util.spec_from_file_location("g2_box_stm32g0_platform", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class BoxPlatformAttributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = M.analyze()

    def test_identity(self):
        self.assertEqual(self.r["identity"], {
            "blob": "blobs/official/g2-2.2.6.10/firmware_box.bin",
            "size": 55784,
            "sha256": "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374",
            "wrapper": {
                "magic": "EVEN",
                "version": "1.2.57",
                "version_bytes": [1, 2, 57, 0],
                "length_be_u32": 55752,
                "checksum_be_u32": 0x7367642F,
                "checksum_algorithm": "additive sum of big-endian u32 words "
                                      "over the application payload, stored "
                                      "big-endian",
                "checksum_verified": True,
            },
            "app_vaddr_base": 0x08000000,
            "app_alternate_bank_vaddr": 0x08040000,
            "app_bytes": 55752,
        })

    def test_vectors(self):
        v = self.r["vectors"]
        self.assertEqual(v["word_count"], 46)
        self.assertEqual(v["peripheral_irq_count"], 30)
        self.assertEqual(v["initial_sp"], 0x20002C88)
        self.assertEqual(v["reset_handler"], 0x08000144)
        self.assertEqual(v["pendsv_handler"], 0x08000102)
        self.assertEqual(v["svc_handler"], 0x08006E18)
        self.assertEqual(v["systick_handler"], 0x08008420)
        e = v["entries"]
        # G0Bx-class discriminating handler slots (thumb-bit set values).
        self.assertEqual(e[16 + 12]["value"], 0x080006C5)   # ADC1_COMP
        self.assertEqual(e[16 + 22]["value"], 0x080084B1)   # TIM17_FDCAN_IT1
        self.assertEqual(e[16 + 27]["value"], 0x08008F99)   # USART1
        self.assertEqual(e[16 + 1]["kind"], "zero")         # PVD_VDDIO2 unused
        self.assertEqual(e[16 + 15]["kind"], "zero")        # TIM2 slot empty
        self.assertEqual(e[16 + 12]["name"], "IRQ12_ADC1_COMP")
        self.assertEqual(e[16 + 22]["name"], "IRQ22_TIM17_FDCAN_IT1")
        self.assertEqual(e[16 + 27]["name"], "IRQ27_USART1")

    def test_mcu_family(self):
        fam = self.r["mcu_family"]
        self.assertIn("STM32G0B1", fam["leading_candidate"])
        self.assertIn("STM32G030", fam["excluded"])
        self.assertIn("STM32G070/G071", fam["excluded"])
        self.assertEqual(len(fam["discriminators"]), 7)

    def test_freertos(self):
        f = self.r["freertos"]
        self.assertEqual(f["kernel_family"], "FreeRTOS")
        self.assertIn("GCC ARM_CM0", f["port"])
        p = f["pendsv_handler"]
        self.assertEqual(p["vaddr"], 0x08000102)
        self.assertEqual(p["bytes"], 62)
        self.assertEqual(
            p["sha256"],
            "6093899cb710c7c4528991e47a9fd21cc8e4099f36f51ecaebadcc5f6998309c")
        self.assertEqual(p["pxCurrentTCB_literal"], 0x20000128)
        self.assertEqual(f["kernel_statics"], {
            "pxCurrentTCB": 0x20000128,
            "xTickCount_offset": 0x0C,
            "xSchedulerRunning_offset": 0x14,
            "xPendedTicks_offset": 0x18,
            "uxSchedulerSuspended_offset": 0x30,
            "pxOverflowDelayedTaskList_offset": 0x34,
        })
        self.assertEqual(f["xPortSysTickHandler"]["scb_literal"], 0xE000ED00)
        self.assertEqual(f["xPortSysTickHandler"]["pendsvset_bit"], 0x10000000)
        self.assertEqual(f["systick_gate"]["scs_literal"], 0xE000E000)
        self.assertIn("V10", f["version_interval"])
        names = f["task_names"]["app_tasks"]
        self.assertEqual(len(names), 11)
        self.assertEqual(names["ledTask"], 0x0800D898)
        self.assertEqual(names["pwrManagerTask"], 0x0800D8A0)
        self.assertEqual(names["glsDetectTask"], 0x0800D8B0)
        self.assertEqual(names["defaultTask"], 0x0800D8C0)

    def test_hal(self):
        h = self.r["hal"]
        creds = {k: v["file_offset"] for k, v in h["flash_credentials"].items()}
        self.assertEqual(creds, {
            "FLASH_KEY1": 0x4C34, "FLASH_KEY2": 0x4C38,
            "FLASH_OPTKEY1": 0x4BAC, "FLASH_OPTKEY2": 0x4BB0,
        })
        self.assertEqual(
            h["hal_uart_irqhandler"]["head_sha256"],
            "7d8522848a8675e99ceda7d0201544437cc409a8bea91823894fa8f9eb9d0560")
        for absent in ("I2C1", "I2C2", "DMA1", "USB", "FDCAN", "RNG", "AES"):
            self.assertIn(absent, h["modules_absent_no_literals"])

    def test_peripherals(self):
        used = self.r["peripherals"]["used"]
        for name in ("RCC", "FLASH", "PWR", "RTC", "ADC1", "USART1",
                     "USART2", "USART3", "USART4", "TIM17", "GPIOB",
                     "GPIOC", "GPIOD", "SYSCFG"):
            self.assertIn(name, used)
        for name in ("I2C1", "I2C2", "USB_DRD", "FDCAN1", "RNG", "AES",
                     "UID", "FLASHSIZE", "DMA1"):
            self.assertIn(name, self.r["peripherals"]["absent"])
        self.assertEqual(used["FLASH"]["literal_sites"][0], 0x3EC4)

    def test_protocol(self):
        p = self.r["uart_update_protocol"]
        self.assertEqual(p["frame_format"]["header_bytes"],
                         [0x5A, 0xA5, 0xFF, "cmd"])
        pk = p["frame_packer"]
        self.assertEqual([i["vaddr"] for i in pk["instances"]],
                         [0x08008FA8, 0x08009004])
        self.assertEqual(
            [i["sha256"] for i in pk["instances"]],
            ["50efce392284f11d828dd64c9c1dcd693c2179ecf52aaf00036a66051b0e957a",
             "94947a9d9fc17fb90037792fc6b43f314c0dfd2d12318bc0459aca3fb0f0e7ac"])
        self.assertEqual(pk["retry_bound"], 10)
        self.assertEqual(pk["failure_fill_byte"], 0xFF)
        self.assertEqual(pk["channel_immediate"], 0x5A)
        self.assertEqual(len(p["rx_parser_timeouts"]), 6)
        self.assertIn(0x13, p["commands_from_strings"])
        self.assertIn(0x58, p["commands_from_strings"])

    def test_ota_state_machine(self):
        steps = self.r["ota_state_machine_strings"]
        self.assertEqual(len(steps), 22)
        names = [s["step"] for s in steps]
        self.assertEqual(names[:3], ["ota_check",
                                     "version_compare_nothing_new",
                                     "version_compare_new"])
        self.assertIn("copy_sn", names)
        self.assertIn("swap_bank_2_to_1", names)
        self.assertIn("ob_check_fail", names)

    def test_serial_identity(self):
        s = self.r["serial_identity"]
        self.assertFalse(s["image_contains_preserved_windows"])
        self.assertEqual(s["uid_0x1fff7590_literal_sites"], [])
        sites = s["preserved_window_literal_sites"]
        self.assertEqual(sites["0x0803f000"], [0x2FE4, 0x3834])
        self.assertEqual(sites["0x0803f800"], [0x2FA4, 0x3728])
        self.assertEqual(sites["0x0807f000"], [0x2C28])
        self.assertEqual(sites["0x0807f800"], [0x2C24])
        self.assertEqual(s["bank2_base_literal_sites"], [0x2D30, 0x2ED8])
        windows = [(w["start"], w["bytes"], w["bank"]) for w in s["preserved_windows"]]
        self.assertEqual(windows, [
            (0x0803F000, 16, 1), (0x0803F800, 8, 1),
            (0x0807F000, 16, 2), (0x0807F800, 8, 2),
        ])
        self.assertIn("never overwrite", s["preservation_rule"])

    def test_regions(self):
        regions = self.r["regions"]
        anchored = [r for r in regions if r["file_start"] is not None]
        self.assertEqual(len(anchored), 14)
        # Disjoint and inside the blob.
        spans = sorted((r["file_start"], r["file_end_exclusive"]) for r in anchored)
        for (a1, b1), (a2, b2) in zip(spans, spans[1:]):
            self.assertLessEqual(b1, a2)
        self.assertLessEqual(spans[-1][1], 55784)
        by_cat = {}
        for r in regions:
            by_cat.setdefault(r["ownership_category"], 0)
            by_cat[r["ownership_category"]] += r["bytes"]
        self.assertEqual(by_cat, {
            "generated_transport": 32,
            "upstream_cmsis_startup": 204,
            "upstream_freertos_kernel": 238,
            "upstream_stm32_hal": 208,
            "first_party_g2": 552,
            "device_specific_preserve": 0,
            "unresolved": 54550,
        })
        total = sum(r["bytes"] for r in regions)
        self.assertEqual(total, 55784)
        vec = next(r for r in anchored if r["file_start"] == 0x20)
        self.assertEqual(
            vec["sha256"],
            "019fe11fc35e0b86be9ec3c189ba57c9cd0f7fbe0f281701639f110fd7a1f3be")
        port = next(r for r in anchored if r["file_start"] == 0x114)
        self.assertEqual(
            port["sha256"],
            "63507cac5e5f3e54ea5b40c522715e061d051773e63779248cd345d8c80e6f5a")
        preserved = [r for r in regions
                     if r["ownership_category"] == "device_specific_preserve"]
        self.assertEqual(len(preserved), 4)
        for r in preserved:
            self.assertIn("never overwrite", r["evidence"])

    def test_categories_and_gates(self):
        self.assertEqual(self.r["ownership_categories"], [
            "generated_transport", "upstream_cmsis_startup",
            "upstream_freertos_kernel", "upstream_stm32_hal",
            "first_party_g2", "device_specific_preserve", "unresolved",
        ])
        self.assertEqual(len(self.r["hardware_gates"]), 3)
        self.assertTrue(any("hardware" in g for g in self.r["hardware_gates"]))
        self.assertGreaterEqual(len(self.r["unresolved"]), 6)

    def test_string_census(self):
        c = self.r["string_census"]
        self.assertEqual(c, {
            "aging": 24, "gls_uart": 7, "ota_box": 23, "pmic_chips": 27,
            "power_standby": 12, "total_ascii_strings_ge6": 308,
            "version": 2, "water_detect": 6,
        })


if __name__ == "__main__":
    unittest.main()
