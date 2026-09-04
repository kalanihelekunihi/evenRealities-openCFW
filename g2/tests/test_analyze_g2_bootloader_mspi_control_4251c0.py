from __future__ import annotations

import ctypes
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_bootloader_mspi_control_4251c0 as analyzer


class BootloaderMspiControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = analyzer.audit()
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / ("control.dylib" if sys.platform == "darwin" else "control.so")
        source = ROOT / "research/admission/bootloader_mspi_control_4251c0/runtime_bootloader_mspi_control_candidate.c"
        fixture = source.parent / "host_fixture.c"
        command = ["/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(source), str(fixture)]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        subprocess.run([*command, "-o", str(library)], check=True, capture_output=True, text=True)
        cls.host = ctypes.CDLL(str(library))
        for name in ("open_cfw_test_control_run", "open_cfw_test_control_run_valid"):
            getattr(cls.host, name).restype = ctypes.c_uint32
        for name in ("open_cfw_test_control_get_core", "open_cfw_test_control_reg", "open_cfw_test_control_trace", "open_cfw_test_control_get_config"):
            getattr(cls.host, name).restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_complete_control_body_is_production_source_routed(self) -> None:
        self.assertEqual(
            self.result["status"],
            "structured-source-dual-profile / production-source-in-place / hardware-validation-blocked-by-unavailable-physical-evidence",
        )
        self.assertEqual(self.result["function"]["stock_bytes"], 4384)
        self.assertTrue(self.result["production"]["routed"])
        self.assertEqual(self.result["production"]["source_owned_bytes"], 3948)
        self.assertEqual(self.result["production"]["adapter"]["bytes"], 124)
        self.assertEqual(self.result["production"]["adapted_body"]["bytes"], 3824)
        self.assertEqual(self.result["production"]["retained_unreachable_tail"]["bytes"], 436)

    def test_both_reviewed_toolchain_profiles_are_pinned(self) -> None:
        profiles = self.result["production"]["profiles"]
        self.assertEqual(profiles["apple-clang"]["component_size"], 163840)
        self.assertEqual(profiles["linux-clang"]["component_size"], 163824)
        self.assertEqual(profiles["apple-clang"]["source_owned_bytes"], 59009)
        self.assertEqual(profiles["linux-clang"]["source_owned_bytes"], 58983)

    def test_independent_main_body_cross_check_is_exact(self) -> None:
        comparison = self.result["cross_image"]
        self.assertEqual(comparison["identical_bytes"] + comparison["address_coupled_bytes"], 4384)
        self.assertEqual(comparison["difference_runs"], 53)

    def test_all_direct_callers_are_pinned(self) -> None:
        self.assertEqual(
            self.result["callers"],
            [0x0041FF5A, 0x00420036, 0x00420EE8, 0x00420F48],
        )

    def test_literal_pool_and_hardware_policy_remain_honest(self) -> None:
        frontier = self.result["production"]["next_executable_frontier"]
        self.assertEqual((frontier["start"], frontier["end"], frontier["bytes"]),
                         (0x00426506, 0x00426536, 48))
        self.assertEqual(frontier["function"], "am_hal_mspi_interrupt_clear")
        self.assertEqual(frontier["status"], "already-source-routed")
        self.assertEqual(self.result["semantic_model"]["valid_stock_requests"], 40)
        self.assertEqual(self.result["hardware_validation"], "blocked by unavailable physical evidence")
        self.assertEqual(self.result["hardware_operations"], [])

    def reset(self) -> None:
        self.host.open_cfw_test_control_reset()

    def invoke(self, request: int, have_config: int = 1) -> int:
        return self.host.open_cfw_test_control_run(request, have_config)

    def core(self, index: int) -> int:
        return self.host.open_cfw_test_control_get_core(index)

    def reg(self, index: int) -> int:
        return self.host.open_cfw_test_control_reg(index)

    def trace(self, index: int) -> int:
        return self.host.open_cfw_test_control_trace(index)

    def set_core(self, index: int, value: int) -> None:
        self.host.open_cfw_test_control_set_core(index, value)

    def set_config(self, index: int, value: int) -> None:
        self.host.open_cfw_test_control_set_config(index, value)

    def test_all_stock_requests_and_low_byte_aliases_execute(self) -> None:
        for request in range(40):
            self.assertEqual(self.host.open_cfw_test_control_run_valid(request), 0, request)
            self.assertEqual(self.host.open_cfw_test_control_run_valid(request | 0xABCD00), 0, request)
        self.assertEqual(self.host.open_cfw_test_control_run_valid(40), 6)
        self.assertEqual(self.host.open_cfw_test_control_run_valid(255), 6)

    def test_handle_configuration_and_pointer_guards(self) -> None:
        self.reset(); self.set_core(0, 0); self.assertEqual(self.invoke(4), 2)
        self.reset(); self.set_core(1, 0); self.assertEqual(self.invoke(4), 7)
        self.reset(); self.assertEqual(self.invoke(0, 0), 6)
        self.reset(); self.assertEqual(self.invoke(4, 0), 0)
        self.reset(); self.set_config(0, 0x00E00000); self.assertEqual(self.invoke(1), 6)
        self.reset(); self.set_config(0, 8); self.assertEqual(self.invoke(2), 6)
        self.reset(); self.set_config(0, 3); self.assertEqual(self.invoke(3), 6)
        self.reset(); self.set_config(0, 5); self.set_config(1, 3); self.assertEqual(self.invoke(35), 6)

    def test_register_state_pairs_and_configuration_routes(self) -> None:
        for off, on, register in ((4, 5, 3), (6, 7, 4), (10, 11, 7), (12, 13, 8), (37, 38, 29)):
            self.reset(); self.assertEqual(self.invoke(on), 0); self.assertEqual(self.reg(register), 1)
            self.assertEqual(self.invoke(off), 0); self.assertEqual(self.reg(register), 0)
        self.reset(); self.assertEqual(self.invoke(22), 0); self.assertEqual(self.core(13), 1)
        self.assertEqual(self.invoke(23), 0); self.assertEqual(self.core(13), 0)
        self.reset(); self.set_config(0, 6); self.assertEqual(self.invoke(24), 0); self.assertEqual(self.core(10), 6)
        self.reset(); self.set_config(0, 7); self.assertEqual(self.invoke(26), 0); self.assertEqual(self.core(11), 7)

    def test_xip_clock_and_device_failures_propagate(self) -> None:
        self.reset(); self.set_core(14, 33); self.assertEqual(self.invoke(18), 33); self.assertEqual(self.trace(0), 1)
        self.reset(); self.set_core(2, 1); self.set_config(0, 0); self.assertEqual(self.invoke(25), 5)
        self.reset(); self.set_config(0, 4); self.set_config(1, 1); self.set_core(15, 34); self.assertEqual(self.invoke(25), 34)
        self.reset(); self.set_config(0, 4); self.set_config(1, 1); self.set_core(16, 35); self.assertEqual(self.invoke(25), 35)
        self.reset(); self.set_core(2, 2); self.set_config(0, 10); self.assertEqual(self.invoke(26), 5)

    def test_sequence_and_command_queue_failure_paths(self) -> None:
        self.reset(); self.set_core(3, 0); self.set_config(0, 1); self.assertEqual(self.invoke(29), 7)
        self.reset(); self.set_core(6, 1); self.set_config(0, 1); self.assertEqual(self.invoke(29), 7)
        self.reset(); self.set_core(5, 2); self.set_config(0, 1); self.set_core(9, 41); self.assertEqual(self.invoke(29), 41)
        self.reset(); self.set_core(5, 1); self.set_core(10, 42); self.assertEqual(self.invoke(30), 42)
        self.reset(); self.set_core(5, 1); self.set_core(11, 43); self.assertEqual(self.invoke(30), 43)
        self.reset(); self.set_core(5, 1); self.set_core(12, 44); self.assertEqual(self.invoke(30), 44)
        self.reset(); self.set_core(4, 0); self.assertEqual(self.invoke(34), 7)
        self.reset(); self.set_core(6, 32); self.assertEqual(self.invoke(34), 5)
        self.reset(); self.set_core(10, 45); self.assertEqual(self.invoke(34), 5)
        self.reset(); self.set_core(11, 46); self.assertEqual(self.invoke(34), 46)

    def test_high_priority_and_raw_queue_state_transitions(self) -> None:
        self.reset(); self.assertEqual(self.invoke(31), 0); self.assertEqual(self.core(7), 1)
        self.assertEqual(self.invoke(31), 7)
        self.reset(); self.assertEqual(self.invoke(32), 0); self.assertEqual(self.core(9), 1)
        self.assertEqual(self.invoke(33), 0); self.assertEqual(self.core(9), 0)
        self.reset(); self.set_config(0, 2); self.assertEqual(self.invoke(34), 0)
        self.assertEqual(self.core(6), 1); self.assertEqual(self.core(14), 1)


if __name__ == "__main__":
    unittest.main()
