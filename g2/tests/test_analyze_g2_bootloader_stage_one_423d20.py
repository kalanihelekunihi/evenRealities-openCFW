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
ANALYZER = ROOT / "tools/analyze_g2_bootloader_stage_one_423d20.py"
CANDIDATE = ROOT / "research/admission/bootloader_stage_one_423d20"
ASSEMBLY = CANDIDATE / "runtime_bootloader_stage_one_423d20.S"
MODEL = CANDIDATE / "runtime_bootloader_stage_one_423d20_model.c"

WAIT = ctypes.CFUNCTYPE(
    ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
    ctypes.c_uint32, ctypes.c_uint32,
)
DEBUG = ctypes.CFUNCTYPE(ctypes.c_uint32)
DELAY = ctypes.CFUNCTYPE(None, ctypes.c_uint32)


class Ports(ctypes.Structure):
    _fields_ = (
        ("wait", WAIT),
        ("debug_disable", DEBUG),
        ("delay", DELAY),
        ("register_80", ctypes.POINTER(ctypes.c_uint32)),
    )


class BootloaderStageOneCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("CC") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is required")
        cls.temporary = tempfile.TemporaryDirectory(prefix="open-cfw-stage-one-")
        cls.output = Path(cls.temporary.name)
        library = cls.output / (
            "stage-one-model.dylib" if sys.platform == "darwin" else "stage-one-model.so"
        )
        command = [
            cls.clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            str(MODEL),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_bootloader_stage_one_model_configure.argtypes = [
            ctypes.POINTER(Ports)
        ]
        for name in (
            "open_cfw_bootloader_stage_one_wait_index_model",
            "open_cfw_bootloader_stage_one_wait_reg80_model",
            "open_cfw_bootloader_stage_one_status_model",
            "open_cfw_bootloader_stage_one_model",
        ):
            getattr(cls.loaded, name).restype = ctypes.c_uint32
        cls.loaded.open_cfw_bootloader_stage_one_wait_index_model.argtypes = [
            ctypes.c_uint32
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def configure(self, wait_results: list[int], debug_result: int = 3) -> None:
        self.register = ctypes.c_uint32(0xFFFFFFFF)
        self.wait_results = list(wait_results)
        self.wait_calls: list[tuple[int, int, int, int]] = []
        self.delays: list[int] = []
        self.debug_calls = 0

        @WAIT
        def wait(timeout, address, mask, expected):
            self.wait_calls.append(
                (timeout, ctypes.cast(address, ctypes.c_void_p).value or 0, mask, expected)
            )
            return self.wait_results.pop(0)

        @DEBUG
        def debug():
            self.debug_calls += 1
            return debug_result

        @DELAY
        def delay(duration):
            self.delays.append(duration)

        self.callbacks = (wait, debug, delay)
        self.ports = Ports(wait, debug, delay, ctypes.pointer(self.register))
        self.loaded.open_cfw_bootloader_stage_one_model_configure(
            ctypes.byref(self.ports)
        )

    def test_analyzer_pins_exact_dual_profile_candidate_and_blockers(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(
            report["status"],
            "exact candidate reconciled with equivalent production source",
        )
        self.assertEqual(
            report["source"],
            {
                "end": 0x00423DCE,
                "executable_bytes": 168,
                "literal_bytes": 6,
                "profiles": 2,
                "sha256": "40a472fa5f161c713a218060464481a0f2722dea60bff8b8a6a51253264481bc",
                "start": 0x00423D20,
            },
        )
        self.assertEqual(
            report["providers"]["unresolved_license_or_source"],
            ["delay_status_change", "retained_delay"],
        )
        self.assertTrue(report["production"]["equivalent_source_routed"])
        self.assertFalse(report["production"]["isolated_candidate_routed"])
        self.assertEqual(report["production"]["next_frontier"], 0x00423E40)
        self.assertEqual(report["hardware_operations"], [])

    def test_success_path_register_policy_calls_and_delay_are_exact(self) -> None:
        self.configure([0, 0, 0], debug_result=3)
        result = self.loaded.open_cfw_bootloader_stage_one_model()
        self.assertEqual(result, 0)
        self.assertEqual(self.register.value, 0xFFFFFFEE)
        register_address = ctypes.addressof(self.register)
        self.assertEqual(
            self.wait_calls,
            [
                (1000, 0xE0000000, 3, 1),
                (1000, register_address, 0x00800000, 0),
                (1000, register_address, 0, 0),
            ],
        )
        self.assertEqual(self.delays, [500])
        self.assertEqual(self.debug_calls, 1)

    def test_predicate_failures_return_four_without_delay(self) -> None:
        self.configure([7])
        self.assertEqual(self.loaded.open_cfw_bootloader_stage_one_status_model(), 4)
        self.assertEqual(self.delays, [])
        self.configure([0, 9])
        self.assertEqual(self.loaded.open_cfw_bootloader_stage_one_status_model(), 4)
        self.assertEqual(self.delays, [])

    def test_entry_wait_and_debug_status_propagate(self) -> None:
        self.configure([0, 0, 7], debug_result=3)
        self.assertEqual(self.loaded.open_cfw_bootloader_stage_one_model(), 7)
        self.assertEqual(self.debug_calls, 0)
        self.configure([0, 0, 0], debug_result=2)
        self.assertEqual(self.loaded.open_cfw_bootloader_stage_one_model(), 2)
        self.assertEqual(self.debug_calls, 1)

    def test_index_address_derivation_and_source_is_maintainable(self) -> None:
        self.configure([0])
        self.assertEqual(
            self.loaded.open_cfw_bootloader_stage_one_wait_index_model(3), 1
        )
        self.assertEqual(self.wait_calls, [(1000, 0xE000000C, 3, 1)])
        source = ASSEMBLY.read_text(encoding="utf-8")
        self.assertNotIn(".byte", source)
        self.assertNotIn(".inst", source)
        self.assertIn("SPDX-License-Identifier: MIT", source)


if __name__ == "__main__":
    unittest.main()
