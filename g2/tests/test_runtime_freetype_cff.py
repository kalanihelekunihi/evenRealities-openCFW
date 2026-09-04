# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_freetype_cff_source_admission.py"
MAP_ANALYZER = ROOT / "tools/analyze_g2_freetype_cff_function_map.py"
ROUTE_ANALYZER = ROOT / "tools/analyze_g2_freetype_cff_production_route.py"
MANIFEST = ROOT / "tools/manifests/g2-freetype-cff-source-admission.json"
MAP_MANIFEST = ROOT / "tools/manifests/g2-freetype-cff-function-map.json"
ROUTE_MANIFEST = ROOT / "tools/manifests/g2-freetype-cff-production-route.json"
COMPONENT = ROOT / "components/shared/freetype_cff"
SOURCE = COMPONENT / "runtime_freetype_cff.c"
HEADER = COMPONENT / "runtime_freetype_cff.h"
ADMISSION = COMPONENT / "source_admission.json"
SNAPSHOT = ROOT / "third_party/freetype"
RESEARCH = ROOT / "research/candidates/freetype"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("freetype_cff_admission", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RuntimeFreeTypeCffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        spec = importlib.util.spec_from_file_location(
            "freetype_cff_complete_map", MAP_ANALYZER
        )
        assert spec is not None and spec.loader is not None
        cls.mapper = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.mapper
        spec.loader.exec_module(cls.mapper)
        route_spec = importlib.util.spec_from_file_location(
            "freetype_cff_production_route", ROUTE_ANALYZER
        )
        assert route_spec is not None and route_spec.loader is not None
        cls.route = importlib.util.module_from_spec(route_spec)
        sys.modules[route_spec.name] = cls.route
        route_spec.loader.exec_module(cls.route)
        cls.report = cls.analyzer.analyze()

    def test_retained_closures_and_complete_source_inventory_are_pinned(self) -> None:
        retained = self.report["retained_source_evidence"]
        self.assertEqual(
            {key: retained[key] for key in (
                "functions", "bytes", "cff_functions", "cff_bytes",
                "base_support_functions", "base_support_bytes",
            )},
            {
                "functions": 47,
                "bytes": 12_062,
                "cff_functions": 38,
                "cff_bytes": 11_326,
                "base_support_functions": 9,
                "base_support_bytes": 736,
            },
        )
        self.assertEqual(len(retained["records"]), 47)
        self.assertEqual({row["wave"] for row in retained["records"]}, {11, 14})
        self.assertEqual(
            {row["license_status"] for row in retained["records"]}, {"FTL"}
        )
        inventory = self.report["cff_source_inventory"]
        self.assertEqual((inventory["files"], inventory["bytes"]), (17, 269_028))
        self.assertEqual(len(inventory["records"]), 17)
        stock = self.mapper.run_audit()
        self.assertEqual(stock["confidence"]["mapped_total"], {
            "functions": 101, "bytes": 16_718,
        })
        self.assertEqual(stock["scope"], {
            "module": "cff",
            "envelope_start": "0x005ABEF8",
            "envelope_end_exclusive": "0x005B0114",
            "physical_bytes": 16_924,
            "callable_bytes": 16_718,
            "residual_physical": {
                "intervals": 13,
                "bytes": 206,
                "category_bytes": {
                    "alignment-padding": 2,
                    "literal-pointer-data-pool": 204,
                },
                "unclassified_bytes": 0,
                "unresolved_callable_bytes": 0,
            },
        })
        intervals = [
            (int(row["start"], 16), int(row["end_exclusive"], 16))
            for row in stock["functions"] + stock["physical_residue"]
        ]
        cursor = 0x005ABEF8
        for start, end in sorted(intervals):
            self.assertEqual(start, cursor)
            cursor = end
        self.assertEqual(cursor, 0x005B0114)

    def test_narrow_candidate_is_distinct_from_complete_cff_map(self) -> None:
        self.assertEqual(self.mapper.run_audit()["candidate_distinction"], {
            "existing_cff_candidate_functions": 38,
            "existing_cff_candidate_bytes": 11_326,
            "existing_base_support_functions": 9,
            "existing_base_support_bytes": 736,
            "newly_mapped_cff_functions": 63,
            "newly_mapped_cff_callable_bytes": 5_392,
            "existing_candidate_scope": (
                "two retained source-identity waves plus base support; not a complete CFF physical map"
            ),
            "this_scope": "complete stock CFF callable and physical envelope",
        })

    def test_stock_consumer_and_component_route_are_authenticated(self) -> None:
        route = self.route.analyze()
        self.assertEqual(route["stock_registration"], {
            "ft_init_freetype": "0x0052431C",
            "ft_add_default_modules": "0x005242FC",
            "ft_add_module": "0x0052729C",
            "default_module_table": "0x0073EEF8",
            "cff_module_index": 2,
            "cff_driver_class": "0x006DCB74",
            "default_module_table_sha256": (
                "1b7abc38c0b16cf1e5bcff6f2a4de87fd30d38cade102b276a42ccfe1041e2b1"
            ),
        })
        self.assertEqual(route["route_state"], {
            "stock_cff_module_registered": True,
            "source_owned_lvgl_font_manager_consumer_routed": True,
            "retained_lvgl_freetype_adapter_calls": 2,
            "source_built_cff_translation_unit_placed": True,
            "source_built_cff_driver_class_registered": True,
            "cff_policy_adapter_placed": True,
            "authenticated_policy_adapter_callsite": False,
            "direct_stock_ps_property_service_callers": [],
            "canonical_component_route_enabled": True,
            "canonical_package_manifest_route_enabled": True,
            "software_production_route_permitted": True,
            "external_cff_font_payload_authenticated": False,
        })
        self.assertEqual(len(route["blockers"]), 2)
        component = route["authenticated_component_route"]
        self.assertEqual(component["module_class_patch"], {
            "address": "0x0073EF00",
            "expected_stock_little_endian_hex": "74cb6d00",
            "replacement_little_endian_hex": "14c05a00",
            "replacement_symbol": "cff_driver_class",
            "replacement_address": "0x005AC014",
        })
        self.assertEqual(
            {
                profile: (record["component"]["size"],
                          record["component"]["sha256"],
                          record["loadable_bytes"])
                for profile, record in component["profiles"].items()
            },
            {
                "apple-clang": (
                    3_956_672,
                    "7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6",
                    20_416,
                ),
                "linux-clang": (
                    3_956_672,
                    "dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6",
                    20_356,
                ),
            },
        )
        self.assertTrue(component["canonical_package_manifest_route_enabled"])
        self.assertEqual(component["canonical_package"], {
            "manifest": "manifests/g2-2.2.6.10-core-source.json",
            "profiles": {
                "apple-clang": {
                    "size": 4_750_780,
                    "sha256": (
                        "1bb3f8c84d288a30cfd252e832ec4a51ac5eca42b5de8e8817db11a938c6a771"
                    ),
                },
                "linux-clang": {
                    "size": 4_750_764,
                    "sha256": (
                        "50f2ee3722aeaa720eed1a7c65381b02ac3ec0ceabecf9eb57d661d8e060a6d0"
                    ),
                },
            },
            "apple_cff_region_rows": 22,
            "linux_profile_replacement_rows": 1,
            "highest_cff_end_exclusive": "0x0073EF04",
        })
        self.assertTrue(
            route["evidence_bounds"]["software_production_route_claimed"]
        )

    def test_recovered_policy_and_runtime_surface_fail_closed(self) -> None:
        self.assertEqual(
            self.report["recovered_policy"],
            {
                "module_index": 2,
                "module_class": "cff_driver_class",
                "module_class_run_address": "0x006DCB74",
                "old_engine": False,
                "default_and_only_admitted_hinting_engine": "Adobe",
                "darkening_parameter_validation":
                    "non-negative monotonic X; Y in [0,500]",
            },
        )
        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for symbol in self.report["runtime"]["apis"]:
            self.assertIn(symbol, source)
            self.assertIn(symbol, header)
        self.assertIn("FT_CFF_HINTING_ADOBE", source)
        self.assertIn("parameters[index + 1U] > 500", source)
        self.assertIn("SPDX-License-Identifier: FTL", source)
        self.assertIn("SPDX-License-Identifier: FTL", header)
        production = self.report["production"]
        self.assertFalse(
            production["authenticated_stock_policy_callsite_recovered"]
        )
        self.assertFalse(production["authenticated_target_placement"])
        self.assertFalse(production["stock_image_overlay_routed"])

    def test_cortex_m55_hard_float_compilation_is_warning_clean(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if clang is None:
            self.skipTest("Clang is required for target compilation")
        with tempfile.TemporaryDirectory(prefix="opencfw-cff-") as temporary:
            output = Path(temporary) / "runtime_freetype_cff.o"
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    "-mcpu=cortex-m55",
                    "-mthumb",
                    "-mfloat-abi=hard",
                    "-std=c11",
                    "-O2",
                    "-ffreestanding",
                    "-fno-builtin",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-DFT2_BUILD_LIBRARY",
                    "-DOPEN_CFW_FREETYPE_JMP_BUF_BYTES=128",
                    "-DOPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT=8",
                    "-I", str(RESEARCH / "target_compat"),
                    "-I", str(RESEARCH / "g2_config"),
                    "-I", str(SNAPSHOT / "g2-config"),
                    "-I", str(SNAPSHOT / "include"),
                    "-I", str(SNAPSHOT),
                    "-I", str(COMPONENT),
                    "-c", str(SOURCE),
                    "-o", str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertGreater(output.stat().st_size, 0)
            cff_output = Path(temporary) / "cff.o"
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    "-mcpu=cortex-m55",
                    "-mthumb",
                    "-mfloat-abi=hard",
                    "-std=c11",
                    "-O2",
                    "-fshort-enums",
                    "-ffreestanding",
                    "-fno-builtin",
                    "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-Wno-cast-function-type-mismatch",
                    "-DFT2_BUILD_LIBRARY",
                    "-DOPEN_CFW_FREETYPE_JMP_BUF_BYTES=128",
                    "-DOPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT=8",
                    "-I", str(RESEARCH / "target_compat"),
                    "-I", str(RESEARCH / "g2_config"),
                    "-I", str(SNAPSHOT / "g2-config"),
                    "-I", str(SNAPSHOT / "include"),
                    "-I", str(SNAPSHOT),
                    "-c", str(SNAPSHOT / "src/cff/cff.c"),
                    "-o", str(cff_output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertGreater(cff_output.stat().st_size, 0)

    def test_checked_in_manifest_and_cli_are_deterministic(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--check-manifest"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(result.stdout), self.report)
        self.assertEqual(json.loads(MANIFEST.read_text()), self.report)
        self.assertEqual(
            json.loads(MAP_MANIFEST.read_text()), self.mapper.run_audit()
        )
        map_result = subprocess.run(
            [sys.executable, str(MAP_ANALYZER), "--check-manifest"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(map_result.stdout), self.mapper.run_audit())
        self.assertEqual(json.loads(ROUTE_MANIFEST.read_text()), self.route.analyze())
        route_result = subprocess.run(
            [sys.executable, str(ROUTE_ANALYZER), "--check-manifest"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(route_result.stdout), self.route.analyze())

    def test_boundary_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-cff-evidence-") as temporary:
            changed = Path(temporary) / "source_boundaries.tsv"
            original = self.analyzer.WAVE_BOUNDARIES[14].read_text()
            changed.write_text(original.replace("cff_slot_load", "cff_slot_fake", 1))
            with self.assertRaisesRegex(self.analyzer.AdmissionError, "input pin drift"):
                self.analyzer.analyze(
                    wave_boundaries={
                        11: self.analyzer.WAVE_BOUNDARIES[11],
                        14: changed,
                    }
                )

    def test_complete_map_image_corpus_and_residue_mutations_are_rejected(self) -> None:
        image = bytearray(self.mapper.IMAGE.read_bytes())
        image[0x005ABEF8 - self.mapper.LOAD_BASE] ^= 1
        with tempfile.TemporaryDirectory(prefix="opencfw-cff-map-image-") as temporary:
            changed = Path(temporary) / "image.bin"
            changed.write_bytes(image)
            with mock.patch.object(self.mapper, "IMAGE", changed):
                with self.assertRaisesRegex(self.mapper.MapError, "input pin drift"):
                    self.mapper.run_audit()

        with tempfile.TemporaryDirectory(prefix="opencfw-cff-map-ghidra-") as temporary:
            changed = Path(temporary) / "functions.jsonl"
            data = bytearray(self.mapper.GHIDRA.read_bytes())
            data[100] ^= 1
            changed.write_bytes(data)
            with mock.patch.object(self.mapper, "GHIDRA", changed):
                with self.assertRaisesRegex(self.mapper.MapError, "input pin drift"):
                    self.mapper.run_audit()

        physical = list(self.mapper.PHYSICAL)
        start, end, category, _ = physical[0]
        physical[0] = (start, end, category, "0" * 64)
        with mock.patch.object(self.mapper, "PHYSICAL", tuple(physical)):
            with self.assertRaisesRegex(self.mapper.MapError,
                                        "physical residue drift"):
                self.mapper.run_audit()

    def test_production_route_call_graph_and_route_input_drift_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-cff-route-") as temporary:
            temporary_path = Path(temporary)
            ghidra = temporary_path / "functions.jsonl"
            data = bytearray(self.route.GHIDRA.read_bytes())
            data[100] ^= 1
            ghidra.write_bytes(data)
            with self.assertRaisesRegex(self.route.RouteError, "input pin drift"):
                self.route.analyze(ghidra_path=ghidra)

            for index, expected in enumerate((
                self.route.BUILDER,
                self.route.OVERLAY,
                self.route.SCATTER_BUILDER,
                self.route.SCATTER_CONFIG,
            )):
                changed = temporary_path / f"hostile-{index}-{expected.name}"
                body = bytearray(expected.read_bytes())
                body[len(body) // 2] ^= 1
                changed.write_bytes(body)
                with self.subTest(expected=expected):
                    with self.assertRaisesRegex(
                        self.route.RouteError,
                        "authenticated CFF route input pin drift",
                    ):
                        self.route.analyze(
                            route_input_overrides={expected: changed}
                        )

    def test_admission_keeps_stock_overlay_and_hardware_claims_out(self) -> None:
        admission = json.loads(ADMISSION.read_text())
        self.assertTrue(admission["build"]["community_source"])
        self.assertFalse(admission["build"]["production_overlay"])
        self.assertFalse(admission["hardware_validation"]["performed"])
        overlay = ROOT / "components/apollo_main/core_overlay/overlay.json"
        self.assertNotIn("runtime_freetype_cff", overlay.read_text())
        self.assertFalse(self.report["production"]["stock_image_overlay_routed"])
        self.assertFalse(self.report["evidence_bounds"]["hardware_operations"])


if __name__ == "__main__":
    unittest.main()
