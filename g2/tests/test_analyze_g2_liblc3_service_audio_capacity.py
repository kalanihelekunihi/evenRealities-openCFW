#!/usr/bin/env python3
"""Regression tests for the LC3 whole-address capacity experiment."""

from __future__ import annotations

import copy
import ctypes
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from g2.tests import test_apollo_liblc3_encoder_specialization as spec_test
except ModuleNotFoundError:
    from tests import test_apollo_liblc3_encoder_specialization as spec_test


G2 = Path(__file__).resolve().parents[1]
TOOL = G2 / "tools/analyze_g2_liblc3_service_audio_capacity.py"
SPEC = importlib.util.spec_from_file_location(
    "open_cfw_liblc3_capacity_test", TOOL)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Liblc3WholeAddressCapacityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.analyze()
        cls.manifest = MODULE.read_json(MODULE.MANIFEST)
        cls.clang = os.environ.get("OPENCFW_CLANG") or "/usr/bin/clang"
        if not Path(cls.clang).is_file():
            raise unittest.SkipTest("reviewed Apple Clang unavailable")

    def test_package_plan_is_an_exact_whole_application_cover(self) -> None:
        package = self.report["package"]
        self.assertEqual(package["apollo_region_count"], 5995)
        self.assertEqual(package["runtime_bytes"], 3885636)
        self.assertTrue(package["exact_contiguous_region_cover"])
        self.assertEqual(package["largest_generated_padding_interval"], 10844)
        self.assertEqual(package["largest_generated_alignment_interval"], 2434)
        self.assertFalse(package["ota_atomic_rebuild_performed"])

    def test_oz_gc_reduces_but_retains_import_and_table_contracts(self) -> None:
        expected = {
            "apple-clang": (19360, 60480, 404, 485, 9156),
            "linux-clang": (19308, 60480, 404, 486, 9108),
        }
        for name, profile in self.report["profiles"].items():
            selected = profile["build"]["accepted"]["oz_gc"]
            values = (
                selected["sections"]["text"]["size"],
                selected["sections"]["rodata"]["size"],
                selected["sections"]["table_rodata"]["size"],
                selected["relocations"]["total"],
                selected["capacity"]["shortfall"],
            )
            self.assertEqual(values, expected[name])
            self.assertEqual(selected["imports"],
                             self.manifest["required_runtime_imports"])
            self.assertEqual(selected["relocation_application"]
                             ["input_table_code_references"], 6)
            self.assertTrue(profile["byte_reproducible_two_builds"])

    def test_gc_lto_and_constant_merging_are_fail_closed(self) -> None:
        for profile in self.report["profiles"].values():
            build = profile["build"]
            self.assertIn("retained unexpected writable data",
                          build["rejected"]["oz_without_gc"]["reason"])
            self.assertIn("pointer-table size changed",
                          build["rejected"]["oz_lto"]["reason"])
            self.assertFalse(build["selection"]["lto_selected"])
            self.assertFalse(build["selection"]["constant_merging_selected"])
            self.assertEqual(build["selection"]
                             ["constant_merging_size_delta"], 0)

    def test_whole_address_solver_stays_blocked(self) -> None:
        apple = self.report["profiles"]["apple-clang"]["placement"]
        linux = self.report["profiles"]["linux-clang"]["placement"]
        self.assertEqual((apple["append_shortfall"],
                          linux["append_shortfall"]), (9152, 9100))
        self.assertEqual((apple["linked_order_append_shortfall"],
                          linux["linked_order_append_shortfall"]),
                         (9156, 9108))
        self.assertFalse(apple["whole_address_production_fit"])
        self.assertEqual(apple["interior_intervals_admitted_for_new_ownership"], 0)
        self.assertTrue(apple["thumb_bw_range_sufficient"])
        self.assertLess(apple["maximum_veneer_displacement"], 1 << 24)
        self.assertFalse(apple["best_order_final_relocation_replay_attempted"])
        self.assertEqual(
            apple["placing_only_table_in_protected_padding_counterfactual_shortfall"],
            8752)
        self.assertTrue(apple["conditional_repack"]["oz_closure_would_fit"])
        self.assertEqual(apple["conditional_repack"]
                         ["margin_before_update_record"], 21532)
        self.assertFalse(apple["conditional_repack"]["production_authority"])
        self.assertFalse(self.report["routing"]["production_placement"])
        self.assertFalse(self.report["routing"]["firmware_image_emitted"])

    def test_hostile_promotion_and_package_geometry_reject(self) -> None:
        promoted = copy.deepcopy(self.manifest)
        promoted["routing"]["production_placement"] = True
        with tempfile.TemporaryDirectory(prefix="lc3-capacity-hostile-") as d:
            path = Path(d) / "manifest.json"
            path.write_text(json.dumps(promoted), encoding="utf-8")
            with self.assertRaisesRegex(
                    MODULE.CapacityAuditError, "gained routing"):
                MODULE.analyze(path)
        geometry = copy.deepcopy(self.manifest)
        geometry["address_contract"]["component_region_count"] -= 1
        with self.assertRaisesRegex(
                MODULE.CapacityAuditError, "region count drift"):
            MODULE._package_model(geometry)

    @staticmethod
    def _compile_host(clang: str, output: Path, optimization: str) -> None:
        command = [
            clang, "-std=c11", optimization, "-ffast-math", "-fshort-enums",
            "-DLC3_PLUS_HR=0", "-Wall", "-Wextra", "-Werror",
            "-I", str(spec_test.UPSTREAM_INCLUDE),
            "-I", str(spec_test.UPSTREAM_SRC),
            "-I", str(spec_test.SHARED_COMPONENT),
            str(spec_test.PROVIDER_SOURCE),
            *(str(path) for path in spec_test.HOST_SOURCES),
        ]
        command += (["-dynamiclib", "-o", str(output)]
                    if sys.platform == "darwin" else
                    ["-shared", "-fPIC", "-lm", "-o", str(output)])
        subprocess.run(command, check=True, capture_output=True, text=True)

    def test_host_o2_and_oz_match_complete_dynamic_grid(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lc3-capacity-host-") as d:
            suffix = ".dylib" if sys.platform == "darwin" else ".so"
            o2 = Path(d) / f"o2{suffix}"
            oz = Path(d) / f"oz{suffix}"
            self._compile_host(self.clang, o2, "-O2")
            self._compile_host(self.clang, oz, "-Oz")
            baseline = spec_test.ApolloLiblc3EncoderSpecializationTests._bind(o2)
            optimized = spec_test.ApolloLiblc3EncoderSpecializationTests._bind(oz)
            configurations = [
                spec_test.Config(
                    frame_us=duration, sample_rate_hz=rate,
                    pcm_sample_rate_hz=0, bitrate_bps=32000,
                    pcm_format=pcm_format, pcm_stride=2)
                for duration in (2500, 5000, 7500, 10000)
                for rate in (8000, 16000, 24000, 32000, 48000)
                for pcm_format in range(4)
            ]
            configurations.extend(
                spec_test.Config(
                    frame_us=10000, sample_rate_hz=16000,
                    pcm_sample_rate_hz=48000, bitrate_bps=bitrate,
                    pcm_format=0, pcm_stride=1)
                for bitrate in (16000, 32000, 64000, 128000))
            for index, config in enumerate(configurations):
                with self.subTest(index=index):
                    self.assertEqual(
                        spec_test.ApolloLiblc3EncoderSpecializationTests._run_one(
                            baseline, config),
                        spec_test.ApolloLiblc3EncoderSpecializationTests._run_one(
                            optimized, config))


if __name__ == "__main__":
    unittest.main()
