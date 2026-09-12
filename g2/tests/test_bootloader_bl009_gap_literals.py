"""Host verifier for the BL-009 gap-literal closure.

Pins the fourteen in-place data groups that route understood scalar cells
of the retained 0x0042B9BA..0x00430470 spans: stock bytes equal the
documented constants, float cells decode to the documented values, every
routed cell has at least one original literal-load referent in the stock
image, and overlay.json carries matching pins and placements.

Evidence: g2/docs/research/g2-bootloader-bl009-gap-literals-source-closure.md
"""
from __future__ import annotations

import hashlib
import json
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMPONENT = ROOT / "components" / "bootloader" / "core_overlay"
CONFIG_PATH = COMPONENT / "overlay.json"
OFFICIAL_PATH = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_bootloader.bin"
)
RUN_BASE = 0x00410000

# symbol -> (source file, [(runtime_address, size, expected_hex)])
GROUPS = {
    "open_cfw_bootloader_bl009_gap_42bf4e": (
        "runtime_bl009_hw_state_gap_42bf4e.c",
        [(0x0042BF4E, 6, "000014ed00e0")],
    ),
    "open_cfw_bootloader_bl009_gap_42c6e4": (
        "runtime_bl009_status_route_gap_42c6e4.c",
        [(0x0042C6E4, 20, "00000000000005400100000802000008efbeadde")],
    ),
    "open_cfw_bootloader_bl009_gap_42c980": (
        "runtime_bl009_clock_gap_42c980.c",
        [(0x0042C980, 8, "00d8b80590d00300")],
    ),
    "open_cfw_bootloader_bl009_gap_42d0f2": (
        "runtime_bl009_state_gap_42d0f2.c",
        [(0x0042D0F2, 18, "000000000c42008088c30000484200007a44")],
    ),
    "open_cfw_bootloader_bl009_gap_42e50e": (
        "runtime_bl009_dispatch_gap_42e50e.c",
        [(0x0042E50E, 6, "000040010008")],
    ),
    "open_cfw_bootloader_bl009_gap_42e534": (
        "runtime_bl009_terminal_gap_42e534.c",
        [(0x0042E534, 8, "0800004004000040")],
    ),
    "open_cfw_bootloader_bl009_gap_42e8c8": (
        "runtime_bl009_cleanup_gap_42e8c8.c",
        [(0x0042E8C8, 8, "0840014024400140")],
    ),
    "open_cfw_bootloader_bl009_gap_42edf6": (
        "runtime_bl009_norm_gap_42edf6.c",
        [(0x0042EDF6, 2, "0000"), (0x0042EDFC, 4, "00009143")],
    ),
    "open_cfw_bootloader_bl009_gap_42f014": (
        "runtime_bl009_handle_gap_42f014.c",
        [(0x0042F014, 4, "00007ac4")],
    ),
    "open_cfw_bootloader_bl009_gap_42cdb0": (
        "runtime_bl009_config_gap_42cdb0.c",
        [
            (0x0042CDB0, 4, "56341201"),
            (0x0042CDB8, 28, "563412004000800000000540fefbffff00000540016cdc0240420f00"),
            (0x0042CDD8, 8, "a0860100801a0600"),
        ],
    ),
    "open_cfw_bootloader_bl009_gap_42bfa4": (
        "runtime_bl009_hwstate_pool_42bfa4.c",
        [
            (0x0042BFAC, 12, "00100240ff0ff000fffc0f00"),
            (0x0042BFBC, 16, "0ff00f00011001000120010008110240"),
            (0x0042BFD0, 4, "0d60011f"),
            (0x0042BFD8, 16, "08100240101002401810024028100240"),
            (0x0042BFF4, 24, "008088c30000a0c10000b0c1000048420000404200007a44"),
            (0x0042C01C, 24, "7c0302408000024088000240b0010240bc010240e0830040"),
        ],
    ),
    "open_cfw_bootloader_bl009_gap_42f14e": (
        "runtime_bl009_register_gap_42f14e.c",
        [
            (0x0042F14E, 2, "0000"),
            (0x0042F158, 4, "0d60011f"),
            (0x0042F164, 12, "00c095437498833fa1478cbb"),
            (0x0042F174, 4, "0c010240"),
            (0x0042F17C, 4, "afafaf01"),
            (0x0042F180, 24, "008003400c800340408003402c8003403080034034800340"),
            (0x0042F19C, 8, "000091c300820340"),
            (
                0x0042F1A4,
                36,
                "3c8003401080034014800340188003401c80034020800340248003402880034008800340",
            ),
        ],
    ),
    "open_cfw_bootloader_bl009_gap_4301f4": (
        "runtime_bl009_bringup_gap_4301f4.c",
        [
            (0x004301F4, 4, "00000000"),
            (0x004301F8, 4, "00000000"),
            (0x00430210, 4, "79e9f6c2"),
            (0x00430230, 4, "38800340"),
        ],
    ),
    "open_cfw_bootloader_bl009_gap_align": (
        "runtime_bl009_gap_align.c",
        [(0x0042E642, 2, "0000"), (0x0042FFFE, 2, "0000")],
    ),
}

# (address, struct format, expected value) for float/int meaning pins.
VALUE_PINS = [
    (0x0042BF50, "<I", 0xE000ED14),
    (0x0042C980, "<I", 0x05B8D800),
    (0x0042C984, "<I", 0x0003D090),
    (0x0042D0F4, "<f", 35.0),
    (0x0042D0F8, "<f", -273.0),
    (0x0042D0FC, "<f", 50.0),
    (0x0042D100, "<f", 1000.0),
    (0x0042EDFC, "<f", 290.0),
    (0x0042F014, "<f", -1000.0),
    (0x0042C6F4, "<I", 0xDEADBEEF),
    (0x0042CDD0, "<I", 1000000),
    (0x0042CDD8, "<I", 100000),
    (0x0042CDDC, "<I", 400000),
    (0x004301F8, "<f", 0.0),
]


def _literal_targets(blob: bytes) -> dict[int, int]:
    """Map Thumb literal-load targets to referent counts (byte patterns)."""
    targets: dict[int, int] = {}
    n = len(blob)

    def note(addr: int, tgt: int) -> None:
        if 0 <= tgt - RUN_BASE < n:
            targets[tgt] = targets.get(tgt, 0) + 1

    i = 0
    while i < n:
        addr = RUN_BASE + i
        b0 = blob[i]
        b1 = blob[i + 1] if i + 1 < n else 0
        hw = b0 | (b1 << 8)
        if (hw & 0xF800) in (0x4800, 0xA000):
            note(addr, ((addr + 4) & ~3) + (hw & 0xFF) * 4)
            i += 2
            continue
        if i + 3 < n:
            hw1 = hw
            hw2 = blob[i + 2] | (blob[i + 3] << 8)
            if hw1 in (
                0xF8DF, 0xF85F, 0xF89F, 0xF81F, 0xF8BF, 0xF83F,
                0xF99F, 0xF91F, 0xF9BF, 0xF93F,
            ):
                imm = hw2 & 0xFFF
                off = imm if (hw1 >> 7) & 1 else -imm
                note(addr, ((addr + 4) & ~3) + off)
                i += 4
                continue
            if hw1 in (
                0xED1F, 0xED3F, 0xEC1F, 0xEC3F, 0xED9F, 0xEDBF,
                0xEC9F, 0xECBF,
            ):
                imm = (hw2 & 0xFF) * 4
                off = imm if (hw1 >> 7) & 1 else -imm
                note(addr, ((addr + 4) & ~3) + off)
                i += 4
                continue
        i += 2
    return targets


class Bl009GapLiteralsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.official = OFFICIAL_PATH.read_bytes()
        cls.config = json.loads(CONFIG_PATH.read_text())
        cls.by_symbol = {
            entry["symbol"]: entry for entry in cls.config["in_place_data"]
        }
        cls.targets = _literal_targets(cls.official)

    def _stock(self, address: int, size: int) -> bytes:
        return self.official[address - RUN_BASE:address - RUN_BASE + size]

    def test_stock_bytes_match_documented_constants(self) -> None:
        for symbol, (_, places) in GROUPS.items():
            for address, size, expected_hex in places:
                with self.subTest(symbol=symbol, address=hex(address)):
                    self.assertEqual(self._stock(address, size).hex(), expected_hex)

    def test_value_pins_decode(self) -> None:
        for address, fmt, expected in VALUE_PINS:
            with self.subTest(address=hex(address)):
                (actual,) = struct.unpack(fmt, self._stock(address, 4))
                self.assertEqual(actual, expected)

    def test_every_routed_cell_has_original_referent(self) -> None:
        for symbol, (_, places) in GROUPS.items():
            for address, size, _ in places:
                with self.subTest(symbol=symbol, address=hex(address)):
                    if size == 2:
                        # Two-byte cells are alignment pads: zero-filled
                        # with no original referent by design.
                        self.assertEqual(
                            self._stock(address, size), b"\x00\x00"
                        )
                        continue
                    start = address + ((-address) % 4)
                    for word in range(start, address + size, 4):
                        cell = self._stock(word, 4)
                        if cell == b"\x00\x00\x00\x00":
                            # Zero cells are alignment padding: no
                            # original referent by design.
                            continue
                        self.assertGreater(
                            self.targets.get(word, 0),
                            0,
                            f"{symbol} cell {word:#x} has no original "
                            "literal referent",
                        )

    def test_overlay_registers_matching_pins(self) -> None:
        for symbol, (filename, places) in GROUPS.items():
            with self.subTest(symbol=symbol):
                entry = self.by_symbol[symbol]
                source = entry["source"]
                raw = (COMPONENT / filename).read_bytes()
                self.assertEqual(
                    source["path"],
                    f"components/bootloader/core_overlay/{filename}",
                )
                self.assertEqual(source["size"], len(raw))
                self.assertEqual(
                    source["sha256"], hashlib.sha256(raw).hexdigest()
                )
                self.assertEqual(source["license"], "MIT")
                cursor = 0
                total = sum(size for _, size, _ in places)
                self.assertEqual(entry["expected"]["size"], total)
                self.assertEqual(len(entry["placements"]), len(places))
                for placement, (address, size, _) in zip(
                    entry["placements"], places
                ):
                    self.assertEqual(placement["runtime_address"], address)
                    self.assertEqual(placement["source_offset"], cursor)
                    self.assertEqual(placement["size"], size)
                    stock = self._stock(address, size)
                    self.assertEqual(
                        placement["stock_sha256"],
                        hashlib.sha256(stock).hexdigest(),
                    )
                    cursor += size


if __name__ == "__main__":
    unittest.main()
