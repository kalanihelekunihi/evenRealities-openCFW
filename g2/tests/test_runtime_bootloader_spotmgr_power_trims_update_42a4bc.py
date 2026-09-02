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
    "runtime_spotmgr_power_trims_update_42a4bc.c"
)
SEQUENCE_SOURCE = (
    ROOT / "components/bootloader/core_overlay/"
    "runtime_spotmgr_state_transition_sequence_42a2b4.c"
)
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BOOT_BASE = 0x00410000
START = 0x0042A4BC
END = 0x0042A546

sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


TON_HOOK = ctypes.CFUNCTYPE(None, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p)
TEMPERATURE_HOOK = ctypes.CFUNCTYPE(
    ctypes.c_uint32,
    ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
    ctypes.c_void_p,
)
SEQUENCE_HOOK = ctypes.CFUNCTYPE(
    ctypes.c_uint32,
    ctypes.c_uint8,
    ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
    ctypes.c_void_p,
)


class BootloaderSpotmgrPowerTrimsUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "spot-trims-host.dylib"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-Wall",
                "-Wextra", "-Werror", "-dynamiclib", str(SOURCE),
                str(SEQUENCE_SOURCE), "-o", str(cls.library),
            ],
            check=True, capture_output=True, text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.function = getattr(
            cls.lib, "open_cfw_bootloader_spotmgr_power_trims_update_42a4bc"
        )
        cls.function.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
            TON_HOOK, TEMPERATURE_HOOK, SEQUENCE_HOOK, ctypes.c_void_p,
        ]
        cls.function.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_all_valid_power_pairs_and_ton_change_classes(self) -> None:
        for target in range(20):
            for current in range(20):
                for target_ton, current_ton in ((3, 3), (6, 2)):
                    with self.subTest(target=target, current=current,
                                      target_ton=target_ton,
                                      current_ton=current_ton):
                        calls: list[tuple] = []

                        @TON_HOOK
                        def ton_hook(ton, power, _context):
                            calls.append(("ton", ton, power))

                        @TEMPERATURE_HOOK
                        def temperature_hook(end, start, ton, old_ton, _context):
                            calls.append(("temperature", end, start, ton, old_ton))
                            return 100 + len(calls)

                        @SEQUENCE_HOOK
                        def sequence_hook(sequence, end, start, ton, old_ton, _context):
                            calls.append(("sequence", sequence, end, start, ton, old_ton))
                            return 200 + sequence

                        status = self.function(
                            target, current, target_ton, current_ton,
                            ton_hook, temperature_hook, sequence_hook, None,
                        )

                        expected_calls: list[tuple] = []
                        expected_status = 0
                        routed_current = current
                        if target == current:
                            if target_ton != current_ton:
                                expected_calls.append(("ton", target_ton, target))
                        elif (target >> 2) == (current >> 2):
                            expected_calls.append((
                                "temperature", target, current,
                                target_ton, current_ton,
                            ))
                            expected_status = 101
                        else:
                            if (target & 3) != (current & 3):
                                routed_current = (current & ~3) | (target & 3)
                                expected_calls.append((
                                    "temperature", routed_current, current,
                                    target_ton, current_ton,
                                ))
                                expected_status = 101
                            result, sequence = reference(target, routed_current)
                            if result == 0:
                                expected_calls.append((
                                    "sequence", sequence, target, routed_current,
                                    target_ton, current_ton,
                                ))
                                expected_status = 200 + sequence
                        self.assertEqual(calls, expected_calls)
                        self.assertEqual(status, expected_status)

    def test_authenticated_callback_table_pointer(self) -> None:
        boot = BOOT.read_bytes()
        self.assertEqual(
            int.from_bytes(
                boot[0x0042ACBC - BOOT_BASE:0x0042ACC0 - BOOT_BASE], "little"
            ),
            0x20000158,
        )

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
            output = Path(self.temporary.name) / f"{clang.parent.name}-trims.o"
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
                check=True, capture_output=True, text=True,
            )
            payload, sections = apollo_overlay.parse_elf32(output)
            section = apollo_overlay.section_named(
                sections,
                ".text.open_cfw_bootloader_spotmgr_power_trims_update_42a4bc",
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
                sum(int(item["size"]) // 8 for item in relocation_sections), 4
            )
            self.assertEqual(len(body), END - START)
            self.assertEqual(
                hashlib.sha256(body).hexdigest(),
                "aed144230a794fe7b562c45bd45f9ba4afa02f2f1a9437c4635fd08402f60ec4",
            )
            targets = (
                (0x1E, 0x0042A1BC), (0x36, 0x0042A43A),
                (0x5C, 0x0042A43A), (0x68, 0x0042A2B4),
            )
            for offset, target_address in targets:
                body[offset:offset + 4] = apollo_overlay.encode_thumb_bl(
                    START + offset, target_address
                )
            self.assertEqual(bytes(body), stock)
            self.assertEqual(
                hashlib.sha256(stock).hexdigest(),
                "7bc6936adbff287072bfdcdac3b453214f98f9604c11239abef5a15f63b5e9bb",
            )


if __name__ == "__main__":
    unittest.main()
