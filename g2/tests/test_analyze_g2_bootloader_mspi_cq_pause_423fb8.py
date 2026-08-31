from __future__ import annotations

import ctypes
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/admission/bootloader_mspi_cq_pause_423fb8/runtime_bootloader_mspi_cq_pause_candidate.c"
FIXTURE = SOURCE.parent / "host_fixture.c"
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_bootloader_mspi_cq_pause_423fb8 as analyzer


class BootloaderMspiCqPauseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="open-cfw-cq-pause-host-")
        output = Path(cls.tmp.name) / (
            "pause.dylib" if sys.platform == "darwin" else "pause.so")
        command = ["/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                   "-Werror", str(SOURCE), str(FIXTURE)]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        subprocess.run([*command, "-o", str(output)], check=True,
                       capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(output))
        cls.loaded.open_cfw_test_mspi_cq_pause_reset.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_cq_pause_run.argtypes = [ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_cq_pause_run.restype = ctypes.c_uint32
        cls.loaded.open_cfw_test_mspi_cq_pause_value.argtypes = [ctypes.c_uint32]
        cls.loaded.open_cfw_test_mspi_cq_pause_value.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    @classmethod
    def reset(cls, mode: int, status: int = 0, delay_limit: int = 0) -> None:
        cls.loaded.open_cfw_test_mspi_cq_pause_reset(mode, status, delay_limit)

    @classmethod
    def execute(cls, module: int) -> int:
        return cls.loaded.open_cfw_test_mspi_cq_pause_run(module)

    @classmethod
    def values(cls) -> list[int]:
        return [cls.loaded.open_cfw_test_mspi_cq_pause_value(i) for i in range(11)]

    def test_analyzer_closes_identity_abi_and_both_target_profiles(self) -> None:
        report = analyzer.audit()
        self.assertEqual(report["status"],
                         "production-routed-exact-dual-profile-source")
        self.assertEqual((report["stock"]["start"], report["stock"]["end"],
                          report["stock"]["bytes"]),
                         (0x00423FB8, 0x0042403E, 134))
        self.assertEqual(report["callers"],
                         [0x004240D2, 0x00425C60, 0x00425CC8])
        self.assertEqual(set(report["profiles"]), {"apple-clang", "linux-clang"})
        for profile in report["profiles"].values():
            self.assertEqual(profile["linked_sha256"], analyzer.STOCK_SHA)
            self.assertEqual(profile["unrelocated_sha256"],
                             analyzer.UNRELOCATED_SHA)
            self.assertEqual(profile["body_size"], 134)
        self.assertEqual(report["next_frontier"], {
            "start": 0x0042403E, "end": 0x004240AA,
            "identity": "program_dma", "bytes": 108,
        })
        self.assertTrue(report["production"]["routed"])
        self.assertEqual(
            report["production"]["source_owned_bytes"]
            + report["production"]["retained_official_bytes"],
            147350,
        )
        self.assertEqual(report["production"]["next_frontier"], 0x0042403E)
        self.assertEqual(report["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(report["hardware_operations"], [])

    def test_disabled_queue_skips_poll_delay_and_checks_dma(self) -> None:
        self.reset(0, status=9)
        self.assertEqual(self.execute(2), 9)
        reads, writes, delays, checks, write_address, write_value, timeout, \
            status_address, mask, value, not_equal = self.values()
        self.assertEqual((reads, writes, delays, checks), (1, 1, 0, 1))
        self.assertEqual(write_address, 0x40060000 + 0x2000 + 0x2B4)
        self.assertEqual(write_value, 0x00800000)
        self.assertEqual((timeout, status_address, mask, value, not_equal),
                         (100000, 0x40060000 + 0x2000 + 0x104, 1, 0, 1))

    def test_designated_pause_skips_delay_and_checks_dma(self) -> None:
        self.reset(1, status=3)
        self.assertEqual(self.execute(1), 3)
        self.assertEqual(self.values()[:4], [3, 1, 0, 1])

    def test_polling_delays_until_queue_disables(self) -> None:
        self.reset(2, status=0, delay_limit=4)
        self.assertEqual(self.execute(3), 0)
        reads, writes, delays, checks = self.values()[:4]
        self.assertEqual((reads, writes, delays, checks), (9, 1, 4, 1))

    def test_timeout_performs_exactly_one_hundred_thousand_delays(self) -> None:
        self.reset(3, status=7)
        self.assertEqual(self.execute(0), 4)
        reads, writes, delays, checks = self.values()[:4]
        self.assertEqual((reads, writes, delays, checks), (200002, 1, 100000, 0))


if __name__ == "__main__":
    unittest.main()
