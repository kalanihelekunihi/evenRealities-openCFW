"""Board-routing config coverage for the G2 charging-case source image.

CS-001 asked for the case source image's board-routing assumptions
(vectors, GPIO/timer bindings, bank swap) to become explicit, documented
configuration instead of unstated literals. These tests check that:

  * components/case/source_image/board_config.h agrees, macro for macro,
    with the numeric literals still duplicated (of necessity -- a linker
    script cannot #include a C header) in linker.ld and with the
    production-routed region in manifests/g2-2.2.6.10-source-only.json.
  * The four device-identity windows named in board_config.h are the exact
    same set pinned in tools/open_cfw.py's REQUIRED_PROTECTED_REGIONS, so
    the two cannot silently drift apart.
  * build_image.py actually reads its board-routing constants from
    board_config.h (not a duplicated literal) and produces vectors that
    match it.

No hardware operation is performed anywhere in this file.
"""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import re
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "components/case/source_image"
BOARD_CONFIG = CASE_DIR / "board_config.h"
LINKER = CASE_DIR / "linker.ld"
SOURCE_ONLY_MANIFEST = ROOT / "manifests/g2-2.2.6.10-source-only.json"

sys.path.insert(0, str(ROOT / "tools"))
import open_cfw as oc  # noqa: E402

sys.path.insert(0, str(CASE_DIR))
import build_image as case_builder  # noqa: E402


def _u32_macros(text: str) -> dict[str, int]:
    """Literal ``UINT32_C(0x...)`` macros plus the handful of derived ones
    board_config.h defines as ``(OTHER_MACRO)`` or ``(A + B)`` expressions
    (BANK1_BASE/BANK2_BASE) -- resolved against the literals above rather
    than duplicating the arithmetic here."""
    macros = {
        name: int(value, 16)
        for name, value in re.findall(
            r"#define (OPEN_CFW_CASE_\w+)\s+UINT32_C\((0x[0-9A-Fa-f]+)\)", text
        )
    }
    for name, expression in re.findall(
        r"#define (OPEN_CFW_CASE_\w+) \(([A-Za-z0-9_ +]+)\)", text
    ):
        if name in macros:
            continue
        terms = [term.strip() for term in expression.split("+")]
        try:
            macros[name] = sum(
                macros[term] if term in macros else int(term, 0) for term in terms
            )
        except (KeyError, ValueError):
            continue
    return macros


class BoardConfigHeaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = BOARD_CONFIG.read_text(encoding="utf-8")
        self.macros = _u32_macros(self.text)

    def test_header_exists_and_is_mit(self) -> None:
        self.assertTrue(BOARD_CONFIG.is_file())
        self.assertIn("SPDX-License-Identifier: MIT", self.text.splitlines()[0])

    def test_required_macros_are_present(self) -> None:
        required = {
            "OPEN_CFW_CASE_FLASH_BASE", "OPEN_CFW_CASE_FLASH_BANK_BYTES",
            "OPEN_CFW_CASE_SRAM_BASE", "OPEN_CFW_CASE_SRAM_BYTES",
            "OPEN_CFW_CASE_STACK_TOP", "OPEN_CFW_CASE_BANK1_BASE",
            "OPEN_CFW_CASE_BANK2_BASE", "OPEN_CFW_CASE_BANK1_IDENTITY_LIMIT",
            "OPEN_CFW_CASE_USART3_BASE", "OPEN_CFW_CASE_USART4_BASE",
        }
        self.assertTrue(required <= set(self.macros))

    def test_bank2_is_flash_base_plus_bank_bytes(self) -> None:
        # OPEN_CFW_CASE_BANK2_BASE is an arithmetic macro (not a literal
        # UINT32_C token), so recompute it the same way the header does.
        self.assertIn(
            "#define OPEN_CFW_CASE_BANK2_BASE "
            "(OPEN_CFW_CASE_FLASH_BASE + OPEN_CFW_CASE_FLASH_BANK_BYTES)",
            self.text,
        )
        flash_base = self.macros["OPEN_CFW_CASE_FLASH_BASE"]
        bank_bytes = self.macros["OPEN_CFW_CASE_FLASH_BANK_BYTES"]
        self.assertEqual(flash_base, 0x08000000)
        self.assertEqual(flash_base + bank_bytes, 0x08040000)

    def test_identity_windows_match_the_pinned_protected_regions(self) -> None:
        windows = {
            (int(start, 16), int(size))
            for start, size in re.findall(
                r"X\((0x[0-9A-Fa-f]+),\s*(\d+)\)", self.text
            )
        }
        self.assertEqual(
            windows,
            {(0x0803F000, 16), (0x0803F800, 8), (0x0807F000, 16), (0x0807F800, 8)},
        )
        pinned_case_windows = {
            (item[2], item[3] - item[2])
            for item in oc.REQUIRED_PROTECTED_REGIONS
            if item[0] == "case_stm32g0"
        }
        self.assertEqual(windows, pinned_case_windows)

    def test_identity_limit_matches_bank1_window_start(self) -> None:
        self.assertEqual(
            self.macros["OPEN_CFW_CASE_BANK1_IDENTITY_LIMIT"], 0x0803F000
        )

    def test_confirmed_irq_slots_are_named(self) -> None:
        self.assertIn("OPEN_CFW_CASE_IRQ_PVD    1", self.text)
        self.assertIn("OPEN_CFW_CASE_IRQ_TIM2   15", self.text)
        self.assertIn("OPEN_CFW_CASE_IRQ_USART1 27", self.text)
        self.assertIn("OPEN_CFW_CASE_IRQ_CEC    30", self.text)

    def test_vector_count_is_used_by_startup(self) -> None:
        startup = (CASE_DIR / "startup.c").read_text(encoding="utf-8")
        self.assertIn("OPEN_CFW_CASE_VECTOR_COUNT", startup)
        self.assertIn("#define OPEN_CFW_CASE_VECTOR_COUNT 46", self.text)

    def test_unconfirmed_defaults_are_labeled(self) -> None:
        # The whole point of this header is that assumed-but-unproven board
        # bindings are visibly marked as such, not silently asserted.
        self.assertIn("UNCONFIRMED", self.text)
        self.assertGreaterEqual(self.text.count("UNCONFIRMED"), 3)


class BoardConfigCrossFileConsistencyTests(unittest.TestCase):
    """board_config.h can't be #included by linker.ld or JSON; check by hand."""

    def setUp(self) -> None:
        self.macros = _u32_macros(BOARD_CONFIG.read_text(encoding="utf-8"))

    def test_linker_script_literals_match_board_config(self) -> None:
        text = LINKER.read_text(encoding="utf-8")
        flash_base_hex = f"{self.macros['OPEN_CFW_CASE_FLASH_BASE']:#010x}"
        self.assertIn(f"ORIGIN = {flash_base_hex}", text)
        self.assertIn("__stack_top = 0x20002C88;", text)
        self.assertEqual(self.macros["OPEN_CFW_CASE_STACK_TOP"], 0x20002C88)
        self.assertIn("ASSERT(__flash_load_end <= 0x0803F000,", text)
        self.assertEqual(
            self.macros["OPEN_CFW_CASE_BANK1_IDENTITY_LIMIT"], 0x0803F000
        )

    def test_source_only_manifest_case_region_matches_board_config(self) -> None:
        manifest = json.loads(SOURCE_ONLY_MANIFEST.read_text(encoding="utf-8"))
        case = manifest["component_overrides"]["case"]
        application = next(
            r for r in case["regions"] if r["name"] == "case_application"
        )
        self.assertEqual(
            application["target_address"], self.macros["OPEN_CFW_CASE_BANK1_BASE"]
        )
        self.assertEqual(
            application["alternate_target_addresses"],
            [self.macros["OPEN_CFW_CASE_BANK2_BASE"]],
        )
        self.assertEqual(case["provider"]["kind"], "source_build")

    def test_build_image_reads_constants_from_board_config_not_a_duplicate(
        self,
    ) -> None:
        self.assertEqual(
            case_builder.board_config_u32("OPEN_CFW_CASE_STACK_TOP"), 0x20002C88
        )
        self.assertEqual(
            case_builder.board_config_u32("OPEN_CFW_CASE_FLASH_BASE"), 0x08000000
        )
        self.assertEqual(
            case_builder.board_config_u32("OPEN_CFW_CASE_BANK1_IDENTITY_LIMIT"),
            0x0803F000,
        )
        with self.assertRaises(case_builder.BuildError):
            case_builder.board_config_u32("OPEN_CFW_CASE_DOES_NOT_EXIST")


@unittest.skipUnless(
    Path("/opt/homebrew/opt/llvm/bin/clang").is_file(),
    "ARMv6-M clang toolchain not present on this host",
)
class BuiltImageMatchesBoardConfigTests(unittest.TestCase):
    def test_built_vectors_match_board_config_defaults(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-case-board-config-") as directory:
            report = case_builder.build(Path(directory))
            raw = (Path(directory) / report["raw"]["path"]).read_bytes()
        stack, reset = struct.unpack_from("<II", raw)
        macros = _u32_macros(BOARD_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(stack, macros["OPEN_CFW_CASE_STACK_TOP"])
        flash_base = macros["OPEN_CFW_CASE_FLASH_BASE"]
        self.assertTrue(flash_base <= (reset & ~1) < flash_base + len(raw))


if __name__ == "__main__":
    unittest.main()
