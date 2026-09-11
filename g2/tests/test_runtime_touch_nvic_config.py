# SPDX-License-Identifier: MIT
"""Pin the PSoC 4000T NVIC vector-slot configuration as explicit, tested
software configuration rather than an unexplained hardware blocker.

Two things are checked independently:

* the psoc4000t_nvic.h enum matches the public psoc4000t.svd IRQ ordering
  already cross-checked in g2-touch-identity-recovery.md ("ARMv6-M
  vector-table shape"), by parsing the header text (no compiler needed);
* the linked vector table in the built ELF actually places the named
  handler at the corresponding vector index (compiler + linker needed), so
  the header and the startup code cannot silently drift apart.
"""

from __future__ import annotations

import importlib.util
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "components/touch/source_image/psoc4000t_nvic.h"
BUILDER = ROOT / "components/touch/source_image/build_image.py"

SPEC = importlib.util.spec_from_file_location("touch_source_image_nvic", BUILDER)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

# Public psoc4000t.svd external-IRQ ordering (Infineon PSoC 4000T NVIC),
# cross-checked against the shipped touch vector-table shape in
# g2/docs/research/g2-touch-identity-recovery.md. Independent of, and not
# derived from, any stock firmware byte.
EXPECTED_IRQ_ORDER = [
    "IOSS0", "IOSS1", "IOSS2", "IOSS3", "IOSS4", "SRSS_WDT", "SCB0", "SCB1",
    "MSCLP_LP", "SPCIF", "MSCLP", "TCPWM0", "TCPWM1",
]
CORE_VECTOR_COUNT = 16
# Named vectors this image actually implements a distinct handler for.
NAMED_HANDLERS = {
    "SCB1": "SCB1_IRQHandler",
    "MSCLP_LP": "MSCLP_LP_IRQHandler",
    "MSCLP": "MSCLP_IRQHandler",
}


def find_nm() -> str:
    candidate = Path("/opt/homebrew/opt/llvm/bin/llvm-nm")
    if candidate.is_file():
        return str(candidate)
    resolved = shutil.which("llvm-nm")
    if resolved:
        return resolved
    raise unittest.SkipTest("llvm-nm is not available")


class Psoc4000tNvicHeaderTests(unittest.TestCase):
    """Parse psoc4000t_nvic.h without compiling it."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = HEADER.read_text()

    def _enum_values(self) -> dict[str, int]:
        match = re.search(
            r"typedef enum open_cfw_touch_psoc4000t_irq\s*\{(.*?)\}\s*"
            r"open_cfw_touch_psoc4000t_irq;",
            self.text, re.DOTALL)
        self.assertIsNotNone(match, "IRQ enum not found")
        values: dict[str, int] = {}
        for line in match.group(1).splitlines():
            item = re.match(r"\s*OPEN_CFW_TOUCH_IRQ_(\w+)\s*=\s*(\d+)", line)
            if item:
                values[item.group(1)] = int(item.group(2))
        return values

    def test_irq_enum_matches_public_svd_order(self) -> None:
        values = self._enum_values()
        for index, name in enumerate(EXPECTED_IRQ_ORDER):
            self.assertEqual(values[name], index,
                             f"IRQ {name} must be silicon IRQ number {index}")
        self.assertEqual(values["COUNT"], len(EXPECTED_IRQ_ORDER))

    def test_core_vector_count_is_architectural(self) -> None:
        match = re.search(
            r"#define OPEN_CFW_TOUCH_CORE_VECTOR_COUNT (\d+)U", self.text)
        self.assertIsNotNone(match)
        self.assertEqual(int(match.group(1)), CORE_VECTOR_COUNT)

    def test_no_stock_byte_or_offset_is_cited(self) -> None:
        # This is silicon configuration; it must not cite a payload offset,
        # a linked stock address, or the stock blob's hash as its evidence.
        lowered = self.text.lower()
        self.assertNotIn("firmware_touch.bin", lowered)
        self.assertNotIn("0x00000000..0x00008680", lowered)


class Psoc4000tNvicLinkedTableTests(unittest.TestCase):
    """Confirm the named configuration actually reaches the linked table."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.nm = find_nm()
        cls.temp = tempfile.TemporaryDirectory(prefix="g2-touch-nvic-test-")
        cls.output = Path(cls.temp.name)
        cls.report = MODULE.build(cls.output)
        cls.elf = cls.output / cls.report["elf"]["path"]
        cls.raw = (cls.output / cls.report["raw"]["path"]).read_bytes()
        cls.symbols = cls._read_symbols()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    @classmethod
    def _read_symbols(cls) -> dict[str, int]:
        # Thumb function symbols carry the T-bit (LSB set) in their ELF
        # st_value, exactly as they appear as a called/loaded vector word.
        lines = subprocess.run(
            [cls.nm, "--defined-only", str(cls.elf)], check=True,
            text=True, capture_output=True).stdout.splitlines()
        symbols: dict[str, int] = {}
        for line in lines:
            parts = line.split()
            if len(parts) == 3:
                symbols[parts[2]] = int(parts[0], 16)
        return symbols

    @classmethod
    def _symbol_size(cls, name: str) -> int:
        lines = subprocess.run(
            [cls.nm, "-S", "--defined-only", str(cls.elf)], check=True,
            text=True, capture_output=True).stdout.splitlines()
        for line in lines:
            parts = line.split()
            if len(parts) == 4 and parts[3] == name:
                return int(parts[1], 16)
        raise AssertionError(f"symbol {name} has no recorded size")

    def _vector_word(self, index: int) -> int:
        return struct.unpack_from("<I", self.raw, index * 4)[0]

    def test_named_irq_vectors_resolve_to_their_named_handler(self) -> None:
        # Thumb code addresses are odd (T-bit set) once loaded as a
        # function-pointer vector; llvm-nm reports the even symbol value.
        for irq_name, handler in NAMED_HANDLERS.items():
            index = CORE_VECTOR_COUNT + EXPECTED_IRQ_ORDER.index(irq_name)
            self.assertEqual(self._vector_word(index), self.symbols[handler] | 1,
                             f"IRQ {irq_name} (vector {index}) must be {handler}")

    def test_unimplemented_external_irqs_fall_back_to_default_handler(self) -> None:
        default_handler = self.symbols["Default_Handler"] | 1
        for irq_name in EXPECTED_IRQ_ORDER:
            if irq_name in NAMED_HANDLERS:
                continue
            index = CORE_VECTOR_COUNT + EXPECTED_IRQ_ORDER.index(irq_name)
            self.assertEqual(self._vector_word(index), default_handler,
                             f"IRQ {irq_name} (vector {index}) must fall back "
                             "to Default_Handler")

    def test_reserved_core_slots_are_zero(self) -> None:
        for index in (4, 5, 6, 7, 8, 9, 10, 12, 13):
            self.assertEqual(self._vector_word(index), 0,
                             f"reserved core vector {index} must be zero")

    def test_vector_table_length_matches_documented_nvic_shape(self) -> None:
        # The linked array's own ELF size is the ground truth for "how many
        # vector slots exist" -- not an assumption about following bytes,
        # which are ordinary .text content, not more vector table.
        expected_length = CORE_VECTOR_COUNT + len(EXPECTED_IRQ_ORDER)
        self.assertEqual(
            self._symbol_size("open_cfw_touch_vectors"), expected_length * 4)


if __name__ == "__main__":
    unittest.main()
