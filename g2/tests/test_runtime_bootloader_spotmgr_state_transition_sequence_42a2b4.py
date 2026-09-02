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
SOURCE = (
    ROOT / "components/bootloader/core_overlay/"
    "runtime_spotmgr_state_transition_sequence_42a2b4.c"
)
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BOOT_BASE = 0x00410000
START = 0x0042A2B4
END = 0x0042A43A
TABLE_POINTER = 0x0042ACB4
TABLE_ADDRESS = 0x00433498
TABLE = (
    (25, 0, 1, 26, 0),
    (2, 25, 26, 3, 3),
    (4, 26, 25, 5, 26),
    (26, 6, 7, 25, 8),
    (2, 9, 26, 10, 25),
)

sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


def reference(target: int, current: int) -> tuple[int, int]:
    sequence = TABLE[current >> 2][target >> 2]
    if sequence == 26:
        return 7, sequence
    if current == 0 and target == 8:
        sequence = 21
    elif current == 8 and target == 0:
        sequence = 22
    if (current, target) in ((8, 12), (12, 8)):
        sequence = 23
    if sequence != 25:
        return 0, sequence

    group_current = current >> 2
    group_target = target >> 2
    current_temp = current & 3
    target_temp = target & 3
    current_gt50 = current_temp == 0 and group_current <= 4
    current_le50 = current_temp > 0 and group_current <= 4
    target_gt50 = target_temp == 0 and group_target <= 4
    target_le50 = target_temp > 0 and group_target <= 4
    current_gt0 = current_temp <= 1 and group_current <= 4
    current_le0 = current_temp >= 2 and group_current <= 4
    target_gt0 = target_temp <= 1 and group_target <= 4
    target_le0 = target_temp >= 2 and group_target <= 4

    if current_le50 and target_gt50:
        sequence = 11 if (current, target) == (9, 8) else (
            12 if (current, target) == (1, 0) else 24
        )
    elif current_gt50 and target_le50:
        sequence = 13 if (current, target) == (8, 9) else (
            14 if (current, target) == (0, 1) else 24
        )
    elif current_le0 and target_gt0:
        sequence = 15 if (current, target) in ((2, 1), (10, 9)) else 16
    elif current_gt0 and target_le0:
        sequence = 17 if (current, target) == (9, 10) else (
            18 if (current, target) == (1, 2) else 19
        )
    elif (current, target) in ((10, 11), (11, 10)):
        sequence = 20
    else:
        sequence = 24
    return 0, sequence


class BootloaderSpotmgrStateTransitionSequenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temporary.name) / "spot-sequence-host.dylib"
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-Wall",
                "-Wextra", "-Werror", "-dynamiclib", str(SOURCE), "-o",
                str(cls.library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.function = getattr(
            cls.lib,
            "open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4",
        )
        cls.function.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint8),
        ]
        cls.function.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_all_valid_power_state_pairs(self) -> None:
        for current in range(20):
            for target in range(20):
                with self.subTest(current=current, target=target):
                    sequence = ctypes.c_uint8(0xA5)
                    status = self.function(target, current, ctypes.byref(sequence))
                    self.assertEqual((status, sequence.value), reference(target, current))

    def test_authenticated_table_and_literal_indirection(self) -> None:
        boot = BOOT.read_bytes()
        literal = boot[
            TABLE_POINTER - BOOT_BASE:TABLE_POINTER - BOOT_BASE + 4
        ]
        self.assertEqual(int.from_bytes(literal, "little"), TABLE_ADDRESS)
        table = boot[TABLE_ADDRESS - BOOT_BASE:TABLE_ADDRESS - BOOT_BASE + 28]
        self.assertEqual(tuple(table[:25]), tuple(value for row in TABLE for value in row))
        self.assertEqual(table[25:], b"\0\0\0")
        self.assertEqual(
            hashlib.sha256(table).hexdigest(),
            "d83c73b1f5370cc6063489aedc4f0701bdec2ca34a492233caa521c0cf2ea5e8",
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
            observed = subprocess.run(
                [str(clang), "--version"], check=True, capture_output=True,
                text=True,
            ).stdout
            self.assertTrue(observed.startswith(version))
            output = Path(self.temporary.name) / f"{clang.parent.name}-sequence.o"
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
                ".text.open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4",
            )
            body = bytearray(
                payload[int(section["offset"]):
                        int(section["offset"]) + int(section["size"])]
            )
            relocations = [
                item for item in sections
                if int(item["type"]) == 9
                and int(item["info"]) == int(section["index"])
            ]
            self.assertEqual(sum(int(item["size"]) // 8 for item in relocations), 1)
            self.assertEqual(len(body), END - START)
            self.assertEqual(
                hashlib.sha256(body).hexdigest(),
                "e0fad5fe49ce4fde2b8a7371bc7a03824d8a273e9003c735317b3bb7075a7cf7",
            )
            body[18:22] = apollo_overlay.encode_thumb_bl(
                START + 18, 0x004156AC
            )
            self.assertEqual(bytes(body), stock)
            self.assertEqual(
                hashlib.sha256(stock).hexdigest(),
                "c02ca4144181ebe16c3dffc47e1bec89a89fbb832fa8bb134b38dd8bf287444f",
            )


if __name__ == "__main__":
    unittest.main()
