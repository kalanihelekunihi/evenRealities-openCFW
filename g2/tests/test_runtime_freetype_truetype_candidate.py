# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research/candidates/freetype"
COMPONENT = ROOT / "components/shared/freetype"
ANALYZER = RESEARCH / "analyze_truetype_candidate.py"
SOURCE = COMPONENT / "runtime_freetype_truetype.c"
HEADER = COMPONENT / "runtime_freetype_truetype.h"
DOCUMENTATION = RESEARCH / "TRUETYPE_SOURCE_ADMISSION.md"
ADMISSION = COMPONENT / "source_admission.json"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_truetype_candidate", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RuntimeFreeTypeTrueTypeCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_complete_non_null_driver_class_surface_is_admitted(self) -> None:
        self.assertEqual(self.report["module"], "truetype")
        self.assertEqual(self.report["upstream_version"], "2.9.1")
        self.assertEqual(
            self.report["class_callbacks"],
            {"functions": 13, "bytes": 1_188},
        )
        self.assertEqual(self.report["null_class_words"], [5, 17, 20])
        rows = self.report["callbacks"]
        self.assertEqual(len(rows), 13)
        self.assertEqual(sum(row["bytes"] for row in rows), 1_188)
        self.assertEqual({row["license"] for row in rows}, {"FTL"})
        self.assertEqual(
            {row["classification"] for row in rows},
            {"authenticated-upstream-class-callback"},
        )

    def test_driver_class_slots_have_exact_source_identities(self) -> None:
        rows = {row["class_word"]: row for row in self.report["callbacks"]}
        expected = {
            6: "tt_driver_init",
            7: "tt_driver_done",
            8: "tt_get_interface",
            12: "tt_face_init",
            13: "tt_face_done",
            14: "tt_size_init",
            15: "tt_size_done",
            16: "tt_slot_init",
            18: "tt_glyph_load",
            19: "tt_get_kerning",
            21: "tt_get_advances",
            22: "tt_size_request",
            23: "tt_size_select",
        }
        self.assertEqual({word: row["symbol"] for word, row in rows.items()}, expected)
        self.assertEqual(sum(row["decompiler_pinned"] for row in rows.values()), 4)
        self.assertEqual(
            {row["source"] for row in rows.values()},
            {"src/truetype/ttdriver.c", "src/truetype/ttobjs.c"},
        )

    def test_private_callback_closure_is_source_admitted(self) -> None:
        self.assertEqual(
            self.report["private_helpers"],
            {"functions": 74, "bytes": 21_900},
        )
        self.assertEqual(
            self.report["admitted_driver_graph"],
            {"functions": 248, "bytes": 38_828},
        )
        rows = {row["symbol"]: row for row in self.report["helpers"]}
        self.assertEqual(len(rows), 74)
        self.assertEqual({row["license"] for row in rows.values()}, {"FTL"})
        self.assertEqual(
            {row["source"] for row in rows.values()},
            {
                "src/truetype/ttgload.c",
                "src/truetype/ttgxvar.c",
                "src/truetype/ttinterp.c",
                "src/truetype/ttobjs.c",
                "src/truetype/ttpload.c",
            },
        )
        for symbol in (
            "TT_Load_Glyph",
            "load_truetype_glyph",
            "compute_glyph_metrics",
            "load_sbit_image",
            "tt_loader_init",
            "tt_get_metrics",
            "tt_get_metrics_incr_overrides",
            "TT_Process_Simple_Glyph",
            "TT_Process_Composite_Component",
            "TT_Process_Composite_Glyph",
            "tt_loader_set_pp",
            "ft_list_get_node_at",
            "tt_prepare_zone",
            "TT_Hint_Glyph",
            "TT_Get_HMetrics",
            "TT_Get_VMetrics",
            "TT_Set_Named_Instance",
            "TT_Get_MM_Var",
            "TT_Set_Var_Design",
            "tt_apply_mvar",
            "ft_var_get_item_delta",
            "ft_var_get_value_pointer",
            "ft_var_readpackedpoints",
            "ft_var_readpackeddeltas",
            "ft_var_load_avar",
            "ft_var_load_mvar",
            "ft_var_apply_tuple",
            "ft_var_to_normalized",
            "tt_set_mm_blend",
            "ft_var_load_item_variation_store",
            "ft_var_load_gvar",
            "ft_var_to_design",
            "TT_Vary_Apply_Glyph_Deltas",
            "tt_interpolate_deltas",
            "tt_delta_shift",
            "tt_delta_interpolate",
            "ft_var_done_item_variation_store",
            "tt_done_blend",
            "tt_loader_done",
            "TT_Done_Context",
            "TT_Load_Context",
            "TT_Goto_CodeRange",
            "TT_Set_CodeRange",
            "TT_Clear_CodeRange",
            "Update_Max",
            "TT_Save_Context",
            "TT_Run_Context",
            "TT_New_Context",
            "Init_Context",
            "tt_size_run_prep",
            "tt_size_ready_bytecode",
            "tt_size_init_bytecode",
            "tt_size_run_fpgm",
            "tt_glyphzone_new",
            "tt_face_get_device_metrics",
            "tt_glyphzone_done",
            "tt_get_sfnt_checksum",
            "tt_synth_sfnt_checksum",
            "tt_size_done_bytecode",
            "tt_size_reset",
            "tt_face_load_loca",
            "tt_face_load_cvt",
            "tt_face_load_hdmx",
            "tt_check_trickyness_sfnt_ids",
        ):
            self.assertIn(symbol, rows)

    def test_private_frontier_remains_explicit(self) -> None:
        frontier = self.report["private_frontier"]
        self.assertEqual(frontier, [])
        self.assertTrue(any(
            "direct and indirect interpreter dispatch frontiers are empty"
            in limitation
            for limitation in self.report["limitations"]
        ))

    def test_interpreter_opcode_and_callback_dispatch_is_closed(self) -> None:
        dispatch = self.report["interpreter_dispatch"]
        self.assertEqual(
            {key: dispatch[key] for key in ("functions", "bytes")},
            {"functions": 161, "bytes": 15_740},
        )
        self.assertEqual(
            dispatch["opcode_engine"],
            {
                "functions": 126,
                "bytes": 13_458,
                "direct_main_targets": 119,
                "transitive_handler_helpers": 6,
                "source_order_mapping_sha256":
                    "ee11f49b4c410aa71584a4a40009751af389aa8ab54031a98ef11a217b927f4d",
            },
        )
        opcode_rows = dispatch["opcode_bodies"]
        self.assertEqual(opcode_rows[0]["symbol"], "Ins_MPPEM")
        self.assertEqual(opcode_rows[-1]["symbol"], "TT_RunIns")
        self.assertEqual({row["license"] for row in opcode_rows}, {"FTL"})
        self.assertEqual(dispatch["unresolved_dispatch_targets"], [])

    def test_interpreter_tables_and_typed_function_pointers_are_exact(self) -> None:
        dispatch = self.report["interpreter_dispatch"]
        self.assertEqual(len(dispatch["support_bodies"]), 9)
        self.assertEqual(len(dispatch["callback_bodies"]), 26)
        self.assertEqual(len(dispatch["callback_edges"]), 27)
        self.assertEqual(
            {row["name"]: row["bytes"] for row in dispatch["tables"]},
            {"opcode_length": 256, "pop_push_count": 256},
        )
        edges = {row["symbol"]: row for row in dispatch["callback_edges"]}
        for symbol in (
            "TT_RunIns",
            "Current_Ppem",
            "Current_Ppem_Stretched",
            "Read_CVT",
            "Write_CVT",
            "Move_CVT",
            "Round_None",
            "Round_Super_45",
            "Project",
            "Dual_Project",
            "Project_x",
            "Project_y",
            "Direct_Move",
            "Direct_Move_Orig_X",
            "Direct_Move_Y",
        ):
            self.assertIn(symbol, edges)
        self.assertTrue(all(row["thumb"] for row in edges.values()))
        self.assertEqual(
            dispatch["policy_boundary"],
            {
                "name": "FT_DEBUG_HOOK_TRUETYPE",
                "candidate_default": "null",
                "fallback": "TT_RunIns",
                "status": "fail-closed; no candidate setter is exposed",
            },
        )

    def test_cli_json_is_deterministic(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(result.stdout), self.report)

    def test_ftl_adapter_is_promoted_but_overlay_remains_fail_closed(self) -> None:
        self.assertIn("SPDX-License-Identifier: FTL", SOURCE.read_text())
        self.assertIn("SPDX-License-Identifier: FTL", HEADER.read_text())
        self.assertIn("FT_Property_Set", SOURCE.read_text())
        self.assertIn("FT_Property_Get", SOURCE.read_text())
        documentation = DOCUMENTATION.read_text()
        self.assertIn("13 callbacks and 1,188 code bytes", documentation)
        self.assertIn("74 private helpers and 21,900 bytes", documentation)
        self.assertIn("161 interpreter functions and 15,740 bytes", documentation)
        overlay = ROOT / "components/apollo_main/core_overlay/overlay.json"
        self.assertNotIn("runtime_freetype_truetype", overlay.read_text())

        admission = json.loads(ADMISSION.read_text())
        self.assertEqual(admission["license"], "FTL")
        self.assertEqual(admission["evidence"]["admitted_functions"], 248)
        self.assertEqual(admission["evidence"]["admitted_bytes"], 38_828)
        self.assertEqual(admission["evidence"]["unresolved_dispatch_targets"], 0)
        self.assertTrue(admission["build"]["community_source"])
        self.assertTrue(admission["build"]["cortex_m55_zero_unresolved"])
        self.assertFalse(admission["build"]["production_overlay"])
        self.assertIn("null-only", admission["policy"]["FT_DEBUG_HOOK_TRUETYPE"])


if __name__ == "__main__":
    unittest.main()
