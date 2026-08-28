# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "research/candidates/freetype"
ANALYZER = COMPONENT / "analyze_base_cluster_candidate.py"
ADAPTER = COMPONENT / "runtime_freetype_base_cluster_candidate.c"
HEADER = COMPONENT / "runtime_freetype_base_cluster_candidate.h"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_base_cluster_candidate", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RuntimeFreeTypeBaseClusterCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_source_admission_closes_the_83_function_census(self) -> None:
        self.assertEqual(
            self.report["baseline"], {"functions": 10, "bytes": 2_152}
        )
        self.assertEqual(
            self.report["new_direct_source_tranche"],
            {"functions": 17, "bytes": 1_294},
        )
        self.assertEqual(
            self.report["admitted_cluster"],
            {"functions": 83, "bytes": 7_874},
        )
        remaining = self.report["remaining_cluster"]
        self.assertEqual(remaining, {"functions": 0, "bytes": 0, "rows": []})
        self.assertEqual(7_874, self.analyzer.CLUSTER_BYTES)

    def test_every_direct_row_has_an_authenticated_ftl_source_identity(self) -> None:
        rows = self.report["direct_source"]
        self.assertEqual(len(rows), 17)
        self.assertEqual(sum(row["bytes"] for row in rows), 1_294)
        self.assertEqual(
            {row["classification"] for row in rows},
            {"authenticated-upstream-source"},
        )
        self.assertEqual({row["license"] for row in rows}, {"FTL"})
        self.assertEqual(
            {row["source"] for row in rows},
            {"src/base/ftobjs.c", "src/base/ftstream.c", "src/base/ftutil.c"},
        )
        for symbol in (
            "FT_Stream_Free",
            "FT_New_GlyphSlot",
            "FT_New_Size",
            "FT_Remove_Module",
            "FT_Stream_Seek",
            "FT_List_Finalize",
        ):
            self.assertIn(symbol, {row["symbol"] for row in rows})

    def test_bounded_indirect_stream_and_memory_rows_have_source_identities(self) -> None:
        self.assertEqual(
            self.report["new_indirect_source_tranche"],
            {"functions": 56, "bytes": 4_428},
        )
        rows = self.report["indirect_source"]
        self.assertEqual(len(rows), 56)
        self.assertEqual(
            {row["inherited_evidence_tier"] for row in rows},
            {"base-call-graph-indirect"},
        )
        self.assertEqual(
            {row["source"] for row in rows},
            {
                "src/base/ftgloadr.c",
                "src/base/ftobjs.c",
                "src/base/ftrfork.c",
                "src/base/ftstream.c",
                "src/base/ftutil.c",
            },
        )
        for symbol in (
            "FT_Raccess_Guess",
            "raccess_guess_darwin_newvfs",
            "raccess_guess_vfat",
            "raccess_guess_apple_generic",
            "raccess_make_file_name",
            "FT_Stream_OpenMemory",
            "FT_Stream_ReadFields",
            "ft_mem_qalloc",
            "ft_mem_qrealloc",
            "ft_mem_strdup",
            "FT_Select_Charmap",
            "FT_Lookup_Renderer",
            "Destroy_Module",
            "FT_Get_Module_Interface",
        ):
            self.assertIn(symbol, {row["symbol"] for row in rows})

    def test_final_sixteen_rows_have_exact_upstream_identities(self) -> None:
        rows = {row["entry"]: row for row in self.report["indirect_source"]}
        expected = {
            "0x00525832": "destroy_size",
            "0x00525936": "Destroy_Driver",
            "0x00525B02": "memory_stream_close",
            "0x00525B20": "new_memory_stream",
            "0x00526DA2": "FT_Select_Charmap",
            "0x00526E38": "ft_cmap_done_internal",
            "0x0052705A": "FT_Lookup_Renderer",
            "0x00527096": "ft_lookup_glyph_renderer",
            "0x005270BC": "ft_set_current_renderer",
            "0x0052716C": "ft_remove_renderer",
            "0x00527228": "FT_Render_Glyph",
            "0x0052724C": "Destroy_Module",
            "0x005273B8": "FT_Get_Module",
            "0x005273F2": "FT_Get_Module_Interface",
            "0x00528508": "raccess_guess_apple_double",
            "0x00528524": "raccess_guess_apple_single",
        }
        self.assertEqual(sum(rows[entry]["bytes"] for entry in expected), 752)
        for entry, symbol in expected.items():
            self.assertEqual(rows[entry]["symbol"], symbol)
            self.assertEqual(rows[entry]["license"], "FTL")

    def test_apple_wrappers_are_distinguished_by_authenticated_magic_words(self) -> None:
        self.assertEqual(
            self.analyzer.APPLE_WRAPPER_MAGIC_EVIDENCE,
            {
                0x00528508: (b"\x83\x4c", 0x00528718, 0x00051607),
                0x00528524: (b"\x7d\x4c", 0x0052871C, 0x00051600),
            },
        )

    def test_complete_bounded_glyph_loader_and_slot_chains_are_named(self) -> None:
        symbols = {row["symbol"] for row in self.report["indirect_source"]}
        for symbol in (
            "FT_GlyphLoader_New",
            "FT_GlyphLoader_Rewind",
            "FT_GlyphLoader_Reset",
            "FT_GlyphLoader_Done",
            "FT_GlyphLoader_Adjust_Points",
            "FT_GlyphLoader_CreateExtra",
            "FT_GlyphLoader_Adjust_Subglyphs",
            "FT_GlyphLoader_CheckPoints",
            "FT_GlyphLoader_CheckSubGlyphs",
            "FT_GlyphLoader_Prepare",
            "FT_GlyphLoader_Add",
            "ft_glyphslot_init",
            "ft_glyphslot_free_bitmap",
            "ft_glyphslot_set_bitmap",
            "ft_glyphslot_alloc_bitmap",
            "ft_glyphslot_clear",
            "ft_glyphslot_done",
        ):
            self.assertIn(symbol, symbols)

    def test_five_largest_residuals_are_exact_upstream_bodies(self) -> None:
        rows = {row["entry"]: row for row in self.report["indirect_source"]}
        expected = {
            "0x00524CD6": (306, "FT_GlyphLoader_CheckPoints"),
            "0x00525C08": (298, "ft_lookup_PS_in_sfnt_stream"),
            "0x00526E5A": (182, "FT_CMap_New"),
            "0x005252BC": (120, "ft_glyphslot_clear"),
            "0x005271C0": (104, "FT_Render_Glyph_Internal"),
        }
        self.assertEqual(sum(size for size, _symbol in expected.values()), 1_010)
        for entry, (size, symbol) in expected.items():
            self.assertEqual(rows[entry]["bytes"], size)
            self.assertEqual(rows[entry]["symbol"], symbol)
            self.assertEqual(rows[entry]["license"], "FTL")

    def test_nine_slot_fallback_is_upstream_mechanics_not_even_code(self) -> None:
        policy = self.report["fallback_policy"]
        self.assertEqual(policy["upstream_rule_count"], 9)
        self.assertEqual(policy["mechanics_functions"], 7)
        self.assertEqual(policy["mechanics_bytes"], 1_862)
        self.assertFalse(policy["even_specific_loader_code_found"])
        rows = self.report["fallback_mechanics"]
        self.assertEqual(
            {row["symbol"] for row in rows},
            {
                "open_face_PS_from_sfnt_stream",
                "Mac_Read_POST_Resource",
                "Mac_Read_sfnt_Resource",
                "IsMacResource",
                "IsMacBinary",
                "load_face_in_embedded_rfork",
                "load_mac_face",
            },
        )
        self.assertTrue(all(not row["inside_83_function_census"] for row in rows))

    def test_cli_json_is_deterministic(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(result.stdout), self.report)

    def test_policy_adapter_is_ftl_and_production_excluded(self) -> None:
        self.assertIn("SPDX-License-Identifier: FTL", ADAPTER.read_text())
        self.assertIn("SPDX-License-Identifier: FTL", HEADER.read_text())
        source = ADAPTER.read_text()
        self.assertIn("FT_OPEN_MEMORY | FT_OPEN_DRIVER", source)
        self.assertIn("FT_New_Memory_Face", source)
        overlay = ROOT / "components/apollo_main/core_overlay/overlay.json"
        self.assertNotIn("runtime_freetype_base_cluster_candidate", overlay.read_text())


if __name__ == "__main__":
    unittest.main()
