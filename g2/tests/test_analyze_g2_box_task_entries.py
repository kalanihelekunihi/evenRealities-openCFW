# SPDX-License-Identifier: MIT
import importlib.util
import sys
import unittest
from pathlib import Path


P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_box_function_map.py"
S = importlib.util.spec_from_file_location("g2_box_task_entries", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class BoxTaskEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.bodies = {body["entry"]: body for body in cls.result["task_bodies"]}
        cls.helpers = {
            helper["entry"]: helper for helper in cls.result["task_helpers"]
        }

    def test_all_unseeded_entries_have_closed_cfgs(self):
        self.assertEqual(set(self.bodies), set(M.SUPPLEMENTAL_TASK_LIMITS))
        for entry, expected in M.SUPPLEMENTAL_TASK_EXPECTED.items():
            body = self.bodies[entry]
            self.assertEqual(body["instruction_count"], expected[0])
            self.assertEqual(body["instruction_bytes"], expected[1])
            self.assertEqual(body["instruction_sha256"], expected[2])
            self.assertTrue(body["spans"])
            self.assertEqual(body["spans"][0]["start"], entry)

    def test_thread_three_is_split_by_authenticated_data_pools(self):
        body = self.bodies[0x08007200]
        self.assertEqual(body["role"], "thread_entry")
        self.assertEqual(
            [(s["start"], s["end"]) for s in body["spans"]],
            [
                (0x08007200, 0x0800748C),
                (0x0800748E, 0x080075E6),
                (0x08007780, 0x08007B50),
                (0x08007E10, 0x08007EE4),
            ],
        )
        self.assertEqual(body["instruction_bytes"], 2184)
        self.assertEqual(body["previously_unmapped_instruction_bytes"], 432)

    def test_other_six_entries_are_contiguous_instruction_bodies(self):
        expected = {
            0x08009D70: (0x08009DB2, 66),
            0x0800B7EC: (0x0800B942, 342),
            0x0800BB90: (0x0800BD08, 374),
            0x08006E1C: (0x08007132, 790),
            0x08007F2C: (0x08008194, 616),
            0x080082EC: (0x080083B4, 200),
        }
        for entry, (end, size) in expected.items():
            spans = self.bodies[entry]["spans"]
            if entry == 0x0800BB90:
                # 0x0800bc88 is an unreachable two-byte branch island.
                self.assertEqual(len(spans), 2)
                self.assertEqual(spans[-1]["end"], end)
            else:
                self.assertEqual(len(spans), 1)
                self.assertEqual(spans[0]["end"], end)
            self.assertEqual(self.bodies[entry]["instruction_bytes"], size)

    def test_cmsis_rtos2_task_helpers_are_resolved_upstream(self):
        expected = {
            0x0800A7B0: "osDelay",
            0x0800A7D2: "osEventFlagsClear",
            0x0800A816: "osEventFlagsGet",
            0x0800A888: "osEventFlagsSet",
            0x0800AA24: "osThreadTerminate",
            0x0800AAF0: "osTimerStart",
            0x0800AB26: "osTimerStop",
        }
        for entry, name in expected.items():
            helper = self.helpers[entry]
            self.assertEqual(helper["name"], name)
            self.assertEqual(
                helper["ownership_category"], "upstream_freertos_kernel"
            )

    def test_task_helper_opacity_is_explicit(self):
        unresolved = {
            entry
            for entry, helper in self.helpers.items()
            if helper["ownership_category"] == "unresolved"
        }
        self.assertEqual(len(self.helpers), 59)
        self.assertEqual(len(unresolved), 0)
        self.assertNotIn(0x08006B80, unresolved)
        self.assertNotIn(0x08006B98, unresolved)
        self.assertNotIn(0x08003848, unresolved)
        self.assertNotIn(0x0800502C, unresolved)
        self.assertNotIn(0x0800598C, unresolved)


if __name__ == "__main__":
    unittest.main()
