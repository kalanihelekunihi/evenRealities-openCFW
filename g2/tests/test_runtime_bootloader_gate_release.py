from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
FIXTURE = ROOT / "tests/fixtures/bootloader_gate_release_host.c"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_gate_release.c"


class BootloaderGateReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "dylib" if sys.platform == "darwin" else "so"
        cls.library = Path(cls.temporary.name) / f"boot-gate-release.{suffix}"
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(cls.library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.open_cfw_test_gate_release_set.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
        cls.lib.open_cfw_bootloader_gate_release.restype = ctypes.c_int
        for name in (
            "gate", "critical_calls", "state_calls", "transition_calls",
            "complete_calls", "order",
        ):
            getattr(cls.lib, f"open_cfw_test_gate_release_{name}").restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_case(self, critical: int, state: int, gate: int) -> tuple[int, ...]:
        self.lib.open_cfw_test_gate_release_set(critical, state, gate)
        result = self.lib.open_cfw_bootloader_gate_release()
        values = tuple(
            getattr(self.lib, f"open_cfw_test_gate_release_{name}")()
            for name in (
                "gate", "critical_calls", "state_calls", "transition_calls",
                "complete_calls", "order",
            )
        )
        return (result, *values)

    def test_authenticated_complete_stock_entry_and_caller(self) -> None:
        image = OFFICIAL.read_bytes()
        body = image[0x60B0:0x60E8]
        self.assertEqual((len(body), hashlib.sha256(body).hexdigest()), (
            56,
            "e5df2dd5abb60c81887e7754bca2eef18621d559e28482dcce5ffaf887993678",
        ))
        # The sole direct call is the release path in the later runtime wrapper.
        self.assertEqual(image[0x1E3C4:0x1E3C8].hex(), "e7f774fe")

    def test_release_contract_and_order(self) -> None:
        self.assertEqual(self.run_case(1, 1, 1), (-6, 1, 1, 0, 0, 0, 0))
        self.assertEqual(self.run_case(0, 0, 1), (-1, 1, 1, 1, 0, 0, 0))
        self.assertEqual(self.run_case(0, 1, 0), (-1, 0, 1, 1, 0, 0, 0))
        self.assertEqual(self.run_case(0, 1, 2), (-1, 2, 1, 1, 0, 0, 0))
        self.assertEqual(self.run_case(0, 1, 1), (0, 2, 1, 1, 1, 1, 12))

    def test_freestanding_target_compiles(self) -> None:
        output = Path(self.temporary.name) / "gate-release.o"
        subprocess.run(
            [
                "/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
