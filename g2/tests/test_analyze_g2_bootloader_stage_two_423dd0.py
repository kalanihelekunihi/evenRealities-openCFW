from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_bootloader_stage_two_423dd0.py"
CANDIDATE = ROOT / "research/admission/bootloader_stage_two_423dd0"
ASSEMBLY = CANDIDATE / "runtime_bootloader_stage_two_423dd0.S"
MODEL = CANDIDATE / "runtime_bootloader_stage_two_423dd0_model.c"

SAVE = ctypes.CFUNCTYPE(ctypes.c_uint32)
RESTORE = ctypes.CFUNCTYPE(None, ctypes.c_uint32)
DEBUG = ctypes.CFUNCTYPE(ctypes.c_uint32)


class Ports(ctypes.Structure):
    _fields_ = (
        ("critical_save", SAVE),
        ("critical_restore", RESTORE),
        ("debug_disable", DEBUG),
        ("guard", ctypes.POINTER(ctypes.c_uint8)),
        ("counter", ctypes.POINTER(ctypes.c_uint8)),
    )


class BootloaderStageTwoCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("CC") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is required")
        cls.temporary = tempfile.TemporaryDirectory(prefix="open-cfw-stage-two-")
        cls.output = Path(cls.temporary.name)
        library = cls.output / (
            "stage-two-model.dylib" if sys.platform == "darwin" else "stage-two-model.so"
        )
        command = [
            cls.clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            str(MODEL),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_bootloader_stage_two_model_configure.argtypes = [
            ctypes.POINTER(Ports)
        ]
        cls.loaded.open_cfw_bootloader_stage_two_status_model.restype = ctypes.c_uint32
        cls.loaded.open_cfw_bootloader_stage_two_mode_flags_model.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32
        ]
        cls.loaded.open_cfw_bootloader_stage_two_mode_flags_model.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def configure(self, counter: int, guard: int, debug_result: int) -> None:
        self.counter = ctypes.c_uint8(counter)
        self.guard = ctypes.c_uint8(guard)
        self.saved = 0
        self.restores: list[int] = []
        self.debug_calls = 0

        @SAVE
        def save():
            self.saved += 1
            return 0xA5

        @RESTORE
        def restore(mask):
            self.restores.append(mask)

        @DEBUG
        def debug():
            self.debug_calls += 1
            return debug_result

        self.callbacks = (save, restore, debug)
        self.ports = Ports(
            save, restore, debug, ctypes.pointer(self.guard), ctypes.pointer(self.counter)
        )
        self.loaded.open_cfw_bootloader_stage_two_model_configure(ctypes.byref(self.ports))

    def test_analyzer_pins_exact_candidate_admission_boundary_and_next_frontier(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(
            report["status"],
            "exact candidate reconciled with production source / admissible leaf",
        )
        self.assertEqual(report["source"]["executable_bytes"], 104)
        self.assertEqual(report["source"]["literal_bytes"], 8)
        self.assertEqual(report["source"]["profiles"], 2)
        self.assertEqual(
            report["source"]["sha256"],
            "b6f037077c2577f042a56ca31101ce7c6734eda572bf1d613195bb3967064c12",
        )
        self.assertEqual(
            report["functions"]["stage_two_status"],
            "exact-MIT-candidate / equivalent-MIT-production-source-routed",
        )
        self.assertEqual(
            report["functions"]["stage_two_mode_flags"],
            "exact-MIT-candidate / equivalent-MIT-production-source-routed",
        )
        self.assertEqual(
            report["providers"]["unresolved_license_or_source"], ["critical_save"]
        )
        self.assertTrue(report["production"]["equivalent_stage_two_source_routed"])
        self.assertFalse(report["production"]["isolated_candidate_routed"])
        self.assertTrue(report["production"]["equivalent_mode_flags_source_routed"])
        self.assertEqual(report["production"]["next_frontier"], 0x00423E40)
        self.assertEqual(report["hardware_operations"], [])

    def test_nonzero_counter_decrements_and_defers_debug_disable(self) -> None:
        self.configure(counter=4, guard=9, debug_result=1)
        self.assertEqual(self.loaded.open_cfw_bootloader_stage_two_status_model(), 3)
        self.assertEqual(self.counter.value, 3)
        self.assertEqual(self.guard.value, 9)
        self.assertEqual(self.debug_calls, 0)
        self.assertEqual(self.saved, 1)
        self.assertEqual(self.restores, [0xA5])

    def test_counter_transition_clears_guard_and_normalizes_debug_three(self) -> None:
        self.configure(counter=1, guard=7, debug_result=3)
        self.assertEqual(self.loaded.open_cfw_bootloader_stage_two_status_model(), 0)
        self.assertEqual(self.counter.value, 0)
        self.assertEqual(self.guard.value, 0)
        self.assertEqual(self.debug_calls, 1)
        self.assertEqual(self.restores, [0xA5])

    def test_zero_counter_propagates_nonthree_debug_status_and_restores_mask(self) -> None:
        self.configure(counter=0, guard=7, debug_result=6)
        self.assertEqual(self.loaded.open_cfw_bootloader_stage_two_status_model(), 6)
        self.assertEqual(self.counter.value, 0)
        self.assertEqual(self.guard.value, 0)
        self.assertEqual(self.debug_calls, 1)
        self.assertEqual(self.restores, [0xA5])

    def test_provider_free_mode_flag_branches_match_exact_body(self) -> None:
        mode = ctypes.c_uint32(1)
        self.assertEqual(
            self.loaded.open_cfw_bootloader_stage_two_mode_flags_model(
                ctypes.byref(mode), 0x15
            ),
            0x40B5,
        )
        self.assertEqual(mode.value, 2)

        mode.value = 2
        self.assertEqual(
            self.loaded.open_cfw_bootloader_stage_two_mode_flags_model(
                ctypes.byref(mode), 0xFFFFFFFF
            ),
            0x4000,
        )
        self.assertEqual(mode.value, 2)

        mode.value = 9
        self.assertEqual(
            self.loaded.open_cfw_bootloader_stage_two_mode_flags_model(
                ctypes.byref(mode), 0x21
            ),
            0x40A1,
        )
        self.assertEqual(mode.value, 9)

    def test_candidate_uses_mnemonic_source_and_typed_sections(self) -> None:
        source = ASSEMBLY.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", source)
        self.assertNotIn(".byte", source)
        self.assertNotIn(".inst", source)
        self.assertIn("msr primask, r0", source)
        self.assertIn(".text.open_cfw_bootloader_stage_two_mode_flags_423e14", source)


if __name__ == "__main__":
    unittest.main()
