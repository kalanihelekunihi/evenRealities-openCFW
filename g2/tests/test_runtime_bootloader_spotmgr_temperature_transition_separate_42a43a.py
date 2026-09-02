from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.test_runtime_bootloader_spotmgr_state_transition_sequence_42a2b4 import (
    reference,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "components/bootloader/core_overlay/"
    "runtime_spotmgr_temperature_transition_separate_42a43a.c"
)
SEQUENCE_SOURCE = (
    ROOT / "components/bootloader/core_overlay/"
    "runtime_spotmgr_state_transition_sequence_42a2b4.c"
)
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BOOT_BASE = 0x00410000
START = 0x0042A43A
END = 0x0042A4BC

sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


OBSERVER = ctypes.CFUNCTYPE(
    ctypes.c_uint32,
    ctypes.c_uint8,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_uint32,
    ctypes.c_void_p,
)


class BootloaderSpotmgrTemperatureTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "spot-temperature-host.dylib"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-Wall",
                "-Wextra", "-Werror", "-dynamiclib", str(SOURCE),
                str(SEQUENCE_SOURCE), "-o", str(cls.library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.function = getattr(
            cls.lib,
            "open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a",
        )
        cls.function.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            ctypes.c_uint32, OBSERVER, ctypes.c_void_p,
        ]
        cls.function.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_every_valid_start_end_pair_dispatches_each_intermediate_step(self) -> None:
        for current in range(20):
            for target in range(20):
                with self.subTest(current=current, target=target):
                    calls: list[tuple[int, int, int, int, int]] = []

                    @OBSERVER
                    def observer(sequence, seen_target, seen_current,
                                 target_ton, current_ton, _context):
                        calls.append((sequence, seen_target, seen_current,
                                      target_ton, current_ton))
                        return len(calls) * 1000 + sequence

                    status = self.function(target, current, 6, 3, observer, None)
                    states = list(range(current, target)) if target > current else list(
                        range(current, target, -1)
                    )
                    expected_sequences = []
                    for starting in states:
                        ending = starting + 1 if target > current else starting - 1
                        result, sequence = reference(ending, starting)
                        if result == 0:
                            expected_sequences.append(sequence)
                    self.assertEqual(
                        calls,
                        [(sequence, target, current, 6, 3)
                         for sequence in expected_sequences],
                    )
                    expected_status = (
                        len(calls) * 1000 + calls[-1][0] if calls else 0
                    )
                    self.assertEqual(status, expected_status)

    def test_authenticated_shared_callback_table_pointer(self) -> None:
        boot = BOOT.read_bytes()
        literal = boot[0x0042ACBC - BOOT_BASE:0x0042ACC0 - BOOT_BASE]
        self.assertEqual(int.from_bytes(literal, "little"), 0x20000158)

    def test_both_reviewed_compilers_reproduce_exact_body(self) -> None:
        stock = BOOT.read_bytes()[START - BOOT_BASE:END - BOOT_BASE]
        profiles = (
            (Path("/usr/bin/clang"), "Apple clang version 21.0.0"),
            (Path("/opt/homebrew/opt/llvm@22/bin/clang"),
             "Homebrew clang version 22.1.8"),
        )
        for clang, version in profiles:
            if not clang.exists():
                self.skipTest(f"reviewed compiler unavailable: {clang}")
            self.assertTrue(subprocess.run(
                [str(clang), "--version"], check=True, capture_output=True,
                text=True,
            ).stdout.startswith(version))
            output = Path(self.temporary.name) / f"{clang.parent.name}-temperature.o"
            subprocess.run(
                [
                    str(clang), "-target", "arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                    "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra",
                    "-Werror", "-fno-ident", "-mllvm",
                    "-enable-machine-outliner=never", "-c", str(SOURCE), "-o",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            payload, sections = apollo_overlay.parse_elf32(output)
            section = apollo_overlay.section_named(
                sections,
                ".text.open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a",
            )
            body = bytearray(payload[
                int(section["offset"]):int(section["offset"]) + int(section["size"])
            ])
            relocation_sections = [
                item for item in sections
                if int(item["type"]) == 9
                and int(item["info"]) == int(section["index"])
            ]
            self.assertEqual(
                sum(int(item["size"]) // 8 for item in relocation_sections), 2
            )
            self.assertEqual(len(body), END - START)
            self.assertEqual(
                hashlib.sha256(body).hexdigest(),
                "066596bd21489fc692537d3fb5724af2ab6ba1eecb93d78b36ce35ea3a4d44cc",
            )
            for offset in (0x28, 0x58):
                body[offset:offset + 4] = apollo_overlay.encode_thumb_bl(
                    START + offset, 0x0042A2B4
                )
            self.assertEqual(bytes(body), stock)
            self.assertEqual(
                hashlib.sha256(stock).hexdigest(),
                "1075e4055c2ef66d985f8938f881a08d43a90791be3dc0b2700ff7e0074ed107",
            )


if __name__ == "__main__":
    unittest.main()
