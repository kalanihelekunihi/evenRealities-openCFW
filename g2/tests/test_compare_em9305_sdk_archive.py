#!/usr/bin/env python3
"""Guard relocation-normalized EM9305 SDK archive comparison helpers."""

from __future__ import annotations

import importlib.util
import random
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/compare_em9305_sdk_archive.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("compare_em9305_sdk_archive", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Em9305SdkArchiveComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()

    def test_stock_and_all_six_sdk_archive_identities_are_pinned(self) -> None:
        blob = self.tool.DEFAULT_IMAGE.read_bytes()
        self.assertEqual(len(blob), self.tool.IMAGE_SIZE)
        self.assertEqual(self.tool.sha256(blob), self.tool.IMAGE_SHA256)
        self.assertEqual(
            set(self.tool.SDK_ARCHIVES),
            {"qpc", "pml", "sleep_manager", "sleep_timer", "prot_timer", "unitimer"},
        )
        self.assertTrue(all(len(item["git_blob"]) == 40 for item in self.tool.SDK_ARCHIVES.values()))
        self.assertTrue(all(len(item["sha256"]) == 64 for item in self.tool.SDK_ARCHIVES.values()))
        self.assertEqual(sum(map(len, self.tool.EXPECTED_EXACT_MATCHES.values())), 98)
        self.assertEqual(sum(map(len, self.tool.EXPECTED_VENDOR_MODIFIED.values())), 3)

    def test_objdump_function_table_parser_accepts_global_weak_and_local(self) -> None:
        table = """
00000000 g     F .text.QF_run 0000002e QF_run
00000000  w    F .text.Q_onAssertExt 0000000e Q_onAssertExt
000000d2 l     F .text 0000000e SWI1WaitForInterrupt
00000000 l     F .text.QF_run 00000000 $t
00000000         *UND* 00000000 QK_onIdle
"""
        functions = self.tool.parse_functions(table)
        self.assertEqual(
            [(item["name"], item["offset"], item["size"]) for item in functions],
            [("QF_run", 0, 0x2E), ("Q_onAssertExt", 0, 0x0E), ("SWI1WaitForInterrupt", 0xD2, 0x0E)],
        )

    def test_relocation_parser_and_normalizer_mask_only_relocated_words(self) -> None:
        relocations = self.tool.parse_relocations("""
RELOCATION RECORDS FOR [.text.QF_run]:
OFFSET   TYPE              VALUE
00000004 R_ARC_32_ME       QK_attr_
0000000c R_ARC_S25W_PCREL  QK_sched_
""")
        body, masked = self.tool.normalized_body(
            bytes(range(20)),
            0,
            20,
            relocations[".text.QF_run"],
        )
        self.assertEqual(masked, tuple(range(4, 8)) + tuple(range(12, 16)))
        self.assertEqual(body[4:8], b"\0" * 4)
        self.assertEqual(body[12:16], b"\0" * 4)
        self.assertEqual(body[:4], bytes(range(4)))

    def test_expected_address_check_works_below_discovery_threshold(self) -> None:
        app = b"\x00\x01\x02\x03\x04\x05"
        self.assertTrue(self.tool.normalized_matches_at(app, b"\x02\x03", (), self.tool.APP_BASE + 2))
        self.assertFalse(self.tool.normalized_matches_at(app, b"\x02\xff", (), self.tool.APP_BASE + 2))
        self.assertTrue(self.tool.normalized_matches_at(app, b"\x02\xff", (1,), self.tool.APP_BASE + 2))

    def test_anchored_matcher_is_equivalent_to_exhaustive_halfword_scan(self) -> None:
        generator = random.Random(9305)
        for _case in range(50):
            app = bytes(generator.randrange(256) for _ in range(192))
            candidate = bytes(generator.randrange(256) for _ in range(24))
            masked = tuple(
                index for index in range(len(candidate)) if generator.randrange(5) == 0
            )
            compared = tuple(index for index in range(len(candidate)) if index not in masked)
            expected = tuple(
                self.tool.APP_BASE + offset
                for offset in range(0, len(app) - len(candidate) + 1, 2)
                if all(app[offset + index] == candidate[index] for index in compared)
            )
            self.assertEqual(
                self.tool.find_normalized_matches(
                    app, candidate, masked, minimum_compared_bytes=8
                ),
                expected,
            )

    def test_discovery_kind_accepts_explicit_identity_cli(self) -> None:
        args = self.tool.parse_args([
            "--archive", "candidate.a",
            "--archive-kind", "emb_peripheral",
            "--archive-sha256", "a" * 64,
            "--archive-git-blob", "b" * 40,
            "--archive-source-path", "libs/third_party/emb/lib_emb_peripheral.a",
            "--binutils-dir", "binutils",
        ])
        self.assertEqual(args.archive_kind, "emb_peripheral")
        self.assertEqual(args.archive_sha256, "a" * 64)

    def test_known_kind_rejects_identity_override(self) -> None:
        with self.assertRaisesRegex(self.tool.ComparisonError, "cannot use an identity override"):
            self.tool.compare(
                self.tool.DEFAULT_IMAGE,
                Path("unused.a"),
                Path("unused-binutils"),
                archive_kind="qpc",
                archive_identity_override={"path": "x", "git_blob": "b" * 40, "sha256": "a" * 64},
            )

    def test_unknown_relocation_fails_closed(self) -> None:
        with self.assertRaises(self.tool.ComparisonError):
            self.tool.parse_relocations("""
RELOCATION RECORDS FOR [.text.x]:
00000000 R_ARC_UNKNOWN symbol
""")


if __name__ == "__main__":
    unittest.main()
