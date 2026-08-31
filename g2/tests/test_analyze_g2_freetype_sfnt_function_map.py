# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


G2 = Path(__file__).resolve().parents[1]
ANALYZER = G2 / "tools/analyze_g2_freetype_sfnt_function_map.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-sfnt-function-map.json"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("sfnt_function_map", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SfntFunctionMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        cls.report = cls.module.run_audit()

    def test_sfnt_is_largest_authenticated_candidate(self) -> None:
        rows = {row["module"]: row for row in self.report["selection"]["candidates"]}
        self.assertEqual(self.report["selected_module"], "sfnt")
        self.assertEqual(
            (rows["sfnt"]["source_backed_functions"], rows["sfnt"]["source_backed_bytes"]),
            (61, 16520),
        )
        self.assertEqual(
            (rows["psaux"]["source_backed_functions"], rows["psaux"]["source_backed_bytes"]),
            (57, 7114),
        )
        self.assertEqual(rows["smooth"]["direct_callback_slots"], 7)
        self.assertEqual(rows["autofit"]["direct_callback_slots"], 3)

    def test_high_rows_have_table_source_and_boundary_corroboration(self) -> None:
        high = self.report["records"]["high"]
        self.assertEqual((len(high), sum(row["bytes"] for row in high)), (75, 13164))
        interface = [row for row in high if "interface_slot" in row]
        recovered = [
            row for row in high
            if row.get("mapping_origin") == "recovered-after-initial-sfnt-map"
        ]
        table_callbacks = [
            row for row in high
            if row.get("mapping_origin") == "resolved-pointer-referenced-sfnt-frontier"
        ]
        self.assertEqual(len(interface), 31)
        self.assertEqual({row["interface_slot"] for row in interface}, set(range(31)))
        for row in interface:
            self.assertIn("stock-interface-table", row["evidence"])
            self.assertIn("stock-sfnt-name-string", row["evidence"])
            self.assertIn("freetype-2.9.1-slot-order", row["evidence"])
            self.assertTrue(
                {"pinned-ghidra-body", "adjacent-single-object-source-order"}
                & set(row["evidence"])
            )
            self.assertEqual(int(row["thumb_pointer"], 16) & ~1, int(row["start"], 16))
            self.assertFalse(row["compiler_byte_identity_claimed"])
        self.assertEqual(
            {row["symbol"] for row in recovered},
            {
                "tt_face_load_bdf_props",
                "tt_face_find_bdf_prop",
                "tt_cmap_init",
                "tt_sbit_decoder_load_bit_aligned",
            },
        )
        for row in recovered:
            self.assertIn("exact-freetype-2.9.1-source-order", row["evidence"])
            self.assertIn("complete-thumb-body-boundary", row["evidence"])
            self.assertTrue(row["source_signature"].startswith("FT_Error"))
        self.assertEqual((len(table_callbacks), sum(row["bytes"] for row in table_callbacks)), (38, 2374))
        for row in table_callbacks:
            self.assertIn("stock-table-or-function-pointer", row["evidence"])
            self.assertIn("exact-freetype-2.9.1-definition", row["evidence"])
            self.assertIn("complete-thumb-body-boundary", row["evidence"])
            self.assertIn("whole-body-sha256", row["evidence"])
            self.assertEqual(int(row["thumb_pointer"], 16) & ~1, int(row["start"], 16))
            self.assertTrue(row["source_signature"])

    def test_recovered_boundaries_hashes_and_anchor_kinds_are_exact(self) -> None:
        expected = {
            "tt_face_load_bdf_props": (
                "0x005DC290", "0x005DC38A", 250,
                "852570bd7508b5b4dc07396b385164ee540560f51e721eb6c99ed2ec6b25e9dd",
                "direct-thumb-call",
            ),
            "tt_face_find_bdf_prop": (
                "0x005DC3C4", "0x005DC53C", 376,
                "bf122132e068cb63d89aba2e2ada8c21032be643fc60ecfa96a6a9f3f6de673e",
                "stock-service-table",
            ),
            "tt_cmap_init": (
                "0x005DC53C", "0x005DC542", 6,
                "c5e328d89f53179b3ebce06235ac0e47f1d4fbfc23027d806822d57cd3f4e290",
                "stock-cmap-class-tables",
            ),
            "tt_sbit_decoder_load_bit_aligned": (
                "0x005E0A70", "0x005E0C48", 472,
                "570f4c16619b4c02a929efeb9302f4196d17955d590a41139cd4e2e376f03fac",
                "stock-sbit-loader-table",
            ),
        }
        recovered = {
            row["symbol"]: row
            for row in self.report["records"]["high"]
            if row.get("mapping_origin") == "recovered-after-initial-sfnt-map"
        }
        for symbol, (start, end, size, digest, anchor) in expected.items():
            row = recovered[symbol]
            self.assertEqual(
                (row["start"], row["end_exclusive"], row["bytes"], row["body_sha256"]),
                (start, end, size, digest),
            )
            self.assertIn(anchor, row["evidence"])

    def test_medium_and_unresolved_rows_stay_fail_closed(self) -> None:
        confidence = self.report["confidence"]
        self.assertEqual(confidence["exact"]["functions"], 0)
        self.assertEqual(confidence["high"], {"functions": 75, "bytes": 13164})
        self.assertEqual(confidence["medium"], {"functions": 61, "bytes": 16094})
        self.assertEqual(confidence["mapped_total"], {"functions": 136, "bytes": 29258})
        self.assertEqual(
            confidence["unresolved_known_candidates"],
            {"functions": 0, "bytes": 0},
        )
        self.assertEqual(
            confidence["unresolved_code"],
            {
                "pointer_referenced_entries": 0,
                "private_helper_envelopes": 0,
                "envelope_bytes": 0,
                "source_identities_complete": True,
            },
        )

    def test_pointer_frontier_has_a_total_distinct_resolution_ledger(self) -> None:
        resolution = self.report["table_pointer_resolution"]
        self.assertEqual(
            (
                resolution["input_pointer_records"],
                resolution["distinct_targets"],
                resolution["alias_pointer_records"],
            ),
            (38, 38, 0),
        )
        self.assertEqual(resolution["resolved_high"], {"functions": 38, "bytes": 2374})
        self.assertEqual(resolution["unresolved"], {"functions": 0, "bytes": 0})
        self.assertEqual(resolution["pointer_alias_groups"], [])
        rows = resolution["records"]
        self.assertEqual(len({row["reference"] for row in rows}), 38)
        self.assertEqual(len({row["target"] for row in rows}), 38)
        self.assertEqual(sum(row["body_bytes"] for row in rows), 2374)
        self.assertTrue(all(row["resolution"] == "high" for row in rows))
        self.assertEqual(
            resolution["identical_body_groups"],
            [{
                "body_sha256": "794ad98f7ef960f9da7c1648e89e44db96c22dfbcd4b3d36bf6e713537f38b4b",
                "symbols": ["tt_cmap12_init", "tt_cmap13_init"],
                "pointer_alias": False,
            }],
        )
        shared = resolution["shared_callback_aliases_outside_frontier"]
        self.assertEqual((len(shared), shared[0]["symbol"], shared[0]["pointer_records"]), (1, "tt_cmap_init", 5))

    def test_callback_boundaries_and_hashes_include_small_leaves(self) -> None:
        rows = {row["symbol"]: row for row in self.report["table_pointer_resolution"]["records"]}
        expected = {
            "sfnt_get_charset_id": ("0x005DAB3A", "0x005DAB82", 72, "c77a0e8d379683d0440eaec24c5797b97d38e45c14b1f73e7416c5e525e9d2f9"),
            "tt_cmap14_char_index": ("0x005DE576", "0x005DE57A", 4, "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4"),
            "tt_cmap14_char_next": ("0x005DE57A", "0x005DE582", 8, "e2511d9fbd2d993240467f8a546d700a027b6f6bbedc0729a648995bcb33f03e"),
            "tt_get_cmap_info": ("0x005DEE14", "0x005DEE2A", 22, "3bd085ecec387711d4ada54cf7bfced17f878632174a60056eaec0644bd7934b"),
        }
        for symbol, wanted in expected.items():
            row = rows[symbol]
            self.assertEqual(
                (row["body_start"], row["body_end_exclusive"], row["body_bytes"], row["body_sha256"]),
                wanted,
            )

    def test_private_cmap_helpers_have_independent_calls_and_semantics(self) -> None:
        resolution = self.report["private_helper_resolution"]
        self.assertEqual(resolution["input_candidates"], 2)
        self.assertEqual(resolution["resolved_high"], {"functions": 2, "bytes": 604})
        self.assertEqual(resolution["unresolved"], {"functions": 0, "bytes": 0})
        rows = {row["symbol"]: row for row in resolution["records"]}
        self.assertEqual(
            (
                rows["tt_cmap12_char_map_binary"]["start"],
                rows["tt_cmap12_char_map_binary"]["end_exclusive"],
                rows["tt_cmap12_char_map_binary"]["bytes"],
                rows["tt_cmap12_char_map_binary"]["body_sha256"],
            ),
            (
                "0x005DDD38", "0x005DDE72", 314,
                "32ad681b5d6209e28aa786de81ecff0f29d6b5de02672ef467a58262f5a5d6bb",
            ),
        )
        self.assertEqual(
            rows["tt_cmap12_char_map_binary"]["wrapper_call_sites"],
            ["0x005DDE78", "0x005DDEAE"],
        )
        self.assertEqual(
            rows["tt_cmap12_char_map_binary"]["semantic_comparison"]["glyph_mapping"],
            "start_id_plus_character_delta_with_overflow_rejection",
        )
        self.assertEqual(
            (
                rows["tt_cmap13_char_map_binary"]["start"],
                rows["tt_cmap13_char_map_binary"]["end_exclusive"],
                rows["tt_cmap13_char_map_binary"]["bytes"],
                rows["tt_cmap13_char_map_binary"]["body_sha256"],
            ),
            (
                "0x005DE0CA", "0x005DE1EC", 290,
                "ed274e27af9e48ca088daae54e334b07f8ad9aff81da6d56a9ac6e00f71e5027",
            ),
        )
        self.assertEqual(
            rows["tt_cmap13_char_map_binary"]["wrapper_call_sites"],
            ["0x005DE1F2", "0x005DE228"],
        )
        self.assertEqual(
            rows["tt_cmap13_char_map_binary"]["semantic_comparison"]["glyph_mapping"],
            "constant_group_glyph_id",
        )

    def test_every_recognized_ghidra_function_in_scope_is_mapped(self) -> None:
        scope = self.report["scope"]
        self.assertEqual(
            scope["ghidra_recognized"],
            {"functions": 75, "bytes": 21238, "unmapped_functions": 0},
        )
        residual = scope["residual_physical"]
        self.assertEqual((residual["intervals"], residual["bytes"]), (10, 354))
        self.assertEqual(residual["classification_records"], 18)
        self.assertEqual(residual["unclassified_bytes"], 0)

    def test_prior_3274_bytes_are_physically_classified_without_identity_inflation(self) -> None:
        residual = self.report["scope"]["residual_physical"]
        self.assertEqual(residual["formerly_unparsed_3274"], {
            "bytes": 3274,
            "recovered_table_callback_code": 2374,
            "recovered_private_helper_code": 604,
            "literal_constant_pool": 272,
            "function_pointer_table": 12,
            "alignment_padding": 12,
            "unclassified": 0,
        })
        self.assertEqual(residual["category_bytes"], {
            "literal-constant-pool": 328,
            "function-pointer-table": 12,
            "alignment-padding": 14,
        })
        physical = self.report["records"]["physical_classification"]
        code = [row for row in physical if row["category"] == "unresolved-callable-code"]
        self.assertEqual((len(code), sum(row["bytes"] for row in code)), (0, 0))
        self.assertEqual(sum(len(row["pointer_records"]) for row in code), 0)
        self.assertTrue(all(not row["source_identity_claimed"] for row in code))

    def test_movement_is_not_inflated_by_prior_census_rows(self) -> None:
        movement = self.report["movement"]
        self.assertEqual(movement["new_beyond_closed_census"], {"functions": 75, "bytes": 12738})
        self.assertEqual(movement["resolved_table_pointer_frontier"], {"functions": 38, "bytes": 2374})
        self.assertEqual(movement["resolved_private_cmap_helpers"], {"functions": 2, "bytes": 604})
        self.assertEqual(movement["initial_high_table_callbacks"], {"functions": 21, "bytes": 5638})
        self.assertEqual(
            movement["new_medium_private_or_outside_census"],
            {"functions": 10, "bytes": 3018},
        )
        self.assertEqual(movement["retained_census_medium"], {"functions": 51, "bytes": 13076})
        self.assertEqual(movement["recovered_named_candidates"], {"functions": 3, "bytes": 1098})
        self.assertEqual(movement["recovered_adjacent_cmap_callback"], {"functions": 1, "bytes": 6})

    def test_summary_manifest_matches_deterministic_report(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        self.assertEqual(manifest["status"], self.report["status"])
        self.assertEqual(manifest["mapping_sha256"], self.report["mapping_sha256"])
        self.assertEqual(manifest["confidence"], {
            "exact": {"functions": 0, "bytes": 0},
            "high": self.report["confidence"]["high"],
            "medium": self.report["confidence"]["medium"],
            "unresolved_known_candidates": self.report["confidence"]["unresolved_known_candidates"],
            "unresolved_code": self.report["confidence"]["unresolved_code"],
            "mapped_total": self.report["confidence"]["mapped_total"],
        })
        self.assertFalse(manifest["production_routed"])
        self.assertFalse(manifest["binary_overlay_ready"])

    def test_no_overlay_or_core_builder_routes_the_research_map(self) -> None:
        paths = (
            G2 / "components/apollo_main/core_overlay/overlay.json",
            G2 / "components/apollo_main/core_overlay/build_component.py",
        )
        production_text = "\n".join(path.read_text() for path in paths)
        self.assertNotIn("freetype_sfnt_function_map", production_text)
        self.assertNotIn("g2-freetype-sfnt-function-map", production_text)
        self.assertFalse(self.report["production_routed"])

    def test_image_tamper_fails_closed(self) -> None:
        image = bytearray(self.module.IMAGE.read_bytes())
        image[self.module.INTERFACE_TABLE - self.module.LOAD_BASE] ^= 1
        with tempfile.TemporaryDirectory() as temp:
            changed = Path(temp) / "image.bin"
            changed.write_bytes(image)
            with mock.patch.object(self.module, "IMAGE", changed):
                with self.assertRaises(self.module.MapError):
                    self.module.run_audit()

    def test_cli_is_deterministic(self) -> None:
        first = subprocess.run(
            [sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True
        ).stdout
        second = subprocess.run(
            [sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True
        ).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["mapping_sha256"], self.report["mapping_sha256"])


if __name__ == "__main__":
    unittest.main()
