from __future__ import annotations

import ctypes
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/admission/bootloader_mspi_sched_hiprio_4240aa/runtime_bootloader_mspi_sched_hiprio_candidate.c"
FIXTURE = SOURCE.parent / "host_fixture.c"
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_bootloader_mspi_sched_hiprio_4240aa as analyzer


class BootloaderMspiSchedHiprioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="open-cfw-sched-hiprio-host-")
        output = Path(cls.tmp.name) / (
            "sched_hiprio.dylib" if sys.platform == "darwin" else "sched_hiprio.so")
        command = ["/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                   "-Werror", str(SOURCE), str(FIXTURE)]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        subprocess.run([*command, "-o", str(output)], check=True,
                       capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(output))
        cls.loaded.open_cfw_test_mspi_sched_reset.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_sched_run.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        cls.loaded.open_cfw_test_mspi_sched_run.restype = ctypes.c_uint32
        cls.loaded.open_cfw_test_mspi_sched_value.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_sched_value.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def reset(self, token: int = 0xA5A55A5A, pause: int = 0,
              program: int = 0, read_value: int = 0x12) -> None:
        self.loaded.open_cfw_test_mspi_sched_reset(token, pause, program,
                                                  read_value)

    def invoke(self, module: int = 2, transaction_interrupt: int = 0x55,
               active: int = 0, pending: int = 0,
               transaction_count: int = 3) -> tuple[int, list[int]]:
        state = (ctypes.c_uint32 * 3)()
        status = self.loaded.open_cfw_test_mspi_sched_run(
            module, transaction_interrupt, active, pending, transaction_count,
            state)
        return status, list(state)

    def value(self, selector: int, index: int = 0) -> int:
        return self.loaded.open_cfw_test_mspi_sched_value(selector, index)

    def test_analyzer_closes_exact_source_and_hardware_block(self) -> None:
        report = analyzer.audit()
        self.assertEqual(
            report["status"],
            "production-routed-exact-dual-profile-source / hardware-validation-blocked-by-unavailable-physical-evidence")
        self.assertEqual((report["stock"]["start"], report["stock"]["end"],
                          report["stock"]["bytes"]),
                         (0x004240AA, 0x00424120, 118))
        self.assertEqual(report["callers"], [0x00425F92])
        self.assertEqual(set(report["profiles"]), {"apple-clang", "linux-clang"})
        self.assertTrue(report["production"]["routed"])
        self.assertEqual(
            report["production"]["source_owned_bytes"]
            + report["production"]["retained_official_bytes"],
            147350,
        )
        self.assertEqual(report["production"]["next_frontier"], 0x00424120)
        self.assertEqual(report["next_frontier"], {
            "start": 0x00424120, "end": 0x0042488E,
            "identity": "mspi_device_configure", "bytes": 1902,
        })
        self.assertEqual(report["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(report["hardware_operations"], [])

    def test_empty_queue_starts_dma_in_exact_effect_order(self) -> None:
        self.reset(read_value=0x12)
        status, state = self.invoke()
        self.assertEqual(status, 0)
        self.assertEqual(state, [0, 1, 3])
        self.assertEqual((self.value(0), self.value(1), self.value(2)),
                         (1, 1, 0xA5A55A5A))
        self.assertEqual((self.value(3), self.value(4), self.value(6),
                          self.value(9)), (1, 1, 2, 1))
        base = 0x40062000
        self.assertEqual(self.value(5), base + 0x200)
        self.assertEqual([self.value(7, index) for index in range(2)],
                         [base + 0x208, base + 0x200])
        self.assertEqual([self.value(8, index) for index in range(2)],
                         [0x40, 0x52])
        self.assertEqual([self.value(11, index) for index in range(7)],
                         [1, 2, 3, 4, 5, 6, 7])

    def test_nonempty_queue_only_updates_pending_count(self) -> None:
        self.reset()
        status, state = self.invoke(transaction_interrupt=0x44, active=1,
                                    pending=5, transaction_count=7)
        self.assertEqual((status, state), (0, [0x44, 1, 12]))
        self.assertEqual((self.value(0), self.value(1), self.value(3),
                          self.value(4), self.value(6), self.value(9)),
                         (1, 1, 0, 0, 0, 0))
        self.assertEqual([self.value(11, index) for index in range(2)], [1, 2])

    def test_pause_failure_short_circuits_mmio_and_dma(self) -> None:
        self.reset(pause=7)
        status, state = self.invoke(transaction_interrupt=0x66,
                                    transaction_count=4)
        self.assertEqual((status, state), (7, [0x66, 0, 4]))
        self.assertEqual((self.value(3), self.value(4), self.value(6),
                          self.value(9)), (1, 0, 0, 0))

    def test_dma_failure_is_propagated_after_state_and_mmio_commit(self) -> None:
        self.reset(program=11, read_value=0x80)
        status, state = self.invoke(transaction_interrupt=0x77,
                                    transaction_count=1)
        self.assertEqual((status, state), (11, [0, 1, 1]))
        self.assertEqual((self.value(6), self.value(9)), (2, 1))
        self.assertEqual(self.value(8, 1), 0xC0)

    def test_pending_count_preserves_uint32_wrap(self) -> None:
        self.reset()
        status, state = self.invoke(pending=0xFFFFFFFE, transaction_count=3)
        self.assertEqual((status, state[2]), (0, 1))
        self.assertEqual((self.value(3), self.value(6), self.value(9)),
                         (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
