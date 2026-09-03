#!/usr/bin/env python3
"""Exact dual-profile checks for the LC3 service_audio production replay."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/apollo_main/liblc3_encoder"
BUILDER_PATH = COMPONENT / "build_service_audio_production_replay.py"
MANIFEST = COMPONENT / "service_audio_production_replay.json"


def load_builder():
    specification = importlib.util.spec_from_file_location(
        "open_cfw_test_liblc3_production_replay", BUILDER_PATH)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load LC3 production replay builder")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


BUILDER = load_builder()


class Lc3ServiceAudioProductionReplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        root = Path(cls.temporary.name)
        cls.reports = {
            profile: BUILDER.build(
                manifest_path=MANIFEST,
                output_dir=root / profile,
                profile=profile,
                record=False)
            for profile in ("apple-clang", "linux-clang")
        }
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_reports_match_pinned_canonical_receipts(self) -> None:
        for profile, report in self.reports.items():
            self.assertEqual(
                BUILDER.canonical_sha256(report),
                self.manifest["profiles"][profile]["expected_report_sha256"])
            self.assertEqual(report["routing"], {
                "production_placement": True,
                "service_audio_routed": True,
                "firmware_image_emitted": True,
                "hardware_operations": False,
            })
            self.assertEqual(report["remaining_software_blockers"], [])
            self.assertEqual(report["hardware"], {
                "validation": "blocked by unavailable physical evidence",
                "qualification_complete": False,
            })

    def test_apple_replays_all_485_relocations_and_78_initializers(self) -> None:
        report = self.reports["apple-clang"]
        final = report["lc3_finalization"]
        self.assertEqual((final["input_relocations"],
                          final["output_relocations"]), (485, 0))
        self.assertTrue(final["all_input_relocations_applied"])
        self.assertEqual(final["input_relocation_contract"], {
            "by_section": {".lc3_table_rodata": 78,
                           ".rodata": 74, ".text": 333},
            "by_type": {"R_ARM_ABS32": 224, "R_ARM_THM_CALL": 238,
                        "R_ARM_THM_JUMP24": 23},
            "external_by_symbol": {
                "__aeabi_memclr": 1, "__aeabi_memclr4": 2, "fabsf": 9,
                "floorf": 1, "fmaxf": 6, "fminf": 1, "memcpy": 6,
                "memmove": 4, "memset": 1, "sqrtf": 6, "truncf": 1,
            },
            "records_sha256":
                "2eec52d62c54fb3f7922e4f8f48b00c6034634ca0f050c2bd7ee3a05c78acf15",
        })
        self.assertEqual((final["table_initializers"],
                          final["table_code_references"]), (78, 6))
        self.assertTrue(final["table_initializers_verified_word_for_word"])
        self.assertEqual(final["final_elf"], {
            "size": 137988,
            "sha256":
                "d7ffce7fe21eae34f0d2cdcc7f8f00e446528fefbb3ddaf10775d35ca34ca103",
        })
        self.assertEqual(final["artifacts"], {
            "text": {"size": 19360, "sha256":
                     "543f596aca956c36f6759ea4ee241ee0d3bc35fd911796cca8878452eda5d43f"},
            "rodata": {"size": 60480, "sha256":
                       "2b162cbd557aa106f2bfb30637fe6c620c9852858a54195a616ab52449836797"},
            "table_rodata": {"size": 404, "sha256":
                             "6f9aa167cd171d8328ca185e70ce2ada7c8bdd17440c8d7dac2f62fa0ef3f18f"},
        })

    def test_all_eleven_imports_have_exact_source_ownership(self) -> None:
        expected_symbols = {
            "__aeabi_memclr", "__aeabi_memclr4", "fabsf", "floorf",
            "fmaxf", "fminf", "memcpy", "memmove", "memset", "sqrtf",
            "truncf",
        }
        for report in self.reports.values():
            final = report["lc3_finalization"]
            ownership = {row["symbol"]: row
                         for row in final["runtime_import_ownership"]}
            self.assertEqual(set(ownership), expected_symbols)
            self.assertEqual(set(final["runtime_bindings"]), expected_symbols)
            for name, row in ownership.items():
                self.assertEqual(row["binding"],
                                 final["runtime_bindings"][name])
                self.assertEqual(row["binding"], row["runtime_address"] | 1)
                self.assertTrue(row["thumb"])
                self.assertEqual(row["symbol_type"], "STT_FUNC")
                self.assertGreater(row["consumer_relocation_count"], 0)
                if name == "sqrtf":
                    self.assertEqual(row["provider_kind"],
                                     "source-owned-core-leaf")
                    self.assertEqual(
                        row["runtime_address"],
                        0x007B42B6 if report["profile"] == "apple-clang"
                        else 0x007B4A02,
                    )
                    self.assertEqual(row["provider_size"], 28)
                    self.assertEqual(row["provider_relocation_count"], 1)
                else:
                    self.assertEqual(row["provider_kind"],
                                     "lc3-owned-target-runtime")
                    self.assertEqual(row["source"],
                                     self.manifest["sources"]["runtime"])

    def test_local_runtime_is_zero_import_zero_relocation_and_nonoverlapping(self) -> None:
        expected = {
            "apple-clang": (324, 3552, 36236,
                            "86c8bd11553a2522f243177c8d8f65f64f7a5fe460a66188e02761fa2b56183b"),
            "linux-clang": (318, 3528, 41768,
                            "6aec80aff48aff76855a01645e1300ebf204e9fc96de3efde02701c2489b5dc3"),
        }
        for profile, report in self.reports.items():
            runtime = report["target_runtime"]
            total, obj_size, elf_size, placement_hash = expected[profile]
            self.assertEqual(runtime["total_text_bytes"], total)
            self.assertEqual(runtime["object"]["size"], obj_size)
            self.assertEqual(runtime["final_elf"]["size"], elf_size)
            self.assertEqual(runtime["placement_sha256"], placement_hash)
            self.assertEqual(runtime["undefined_symbols"], [])
            self.assertEqual(runtime["output_relocations"], 0)
            intervals = sorted((row["address"],
                                row["address"] + row["size"])
                               for row in runtime["sections"])
            self.assertEqual(len(intervals), 11)
            self.assertTrue(all(left[1] <= right[0]
                                for left, right in zip(intervals,
                                                       intervals[1:])))

    def test_service_entries_use_exact_thumb_veneers_and_ram_slots(self) -> None:
        apple = self.reports["apple-clang"]
        self.assertEqual(apple["lc3_finalization"]["service_audio_veneers"], [
            {"root": "open_cfw_liblc3_service_audio_stock_encode",
             "entry": 0x0057A940, "target": 0x007FD6F0,
             "encoding_hex": "82f2d6be"},
            {"root": "open_cfw_liblc3_service_audio_stock_setup",
             "entry": 0x0057A926, "target": 0x007FD7D0,
             "encoding_hex": "82f253bf"},
        ])
        self.assertEqual(apple["suffix"]["count"], 117)
        self.assertEqual(apple["suffix"]["relocation_count"], 362)
        self.assertEqual(
            apple["component"]["sha256"],
            "fee7e5d9f7fe234f2fe49904124bb8b3a7b6248f667c92d7ab4ed6f0e032d922",
        )
        self.assertEqual(apple["lc3_finalization"]["layout"][-1]
                         ["end_exclusive"], 0x007FDFA0)
        self.assertEqual(0x007FE000 - 0x007FE000, 0)

    def _write_manifest(self, value: dict) -> Path:
        path = Path(self.temporary.name) / \
            f"hostile-{hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()}.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_fail_closed_rejects_source_pin_or_script_pin_drift(self) -> None:
        for name in ("runtime", "replay_builder", "suffix_analyzer",
                     "route_builder", "xip_finalizer"):
            mutated = copy.deepcopy(self.manifest)
            mutated["sources"][name]["sha256"] = "0" * 64
            with self.assertRaisesRegex(BUILDER.ReplayError,
                                        "source pin drift"):
                BUILDER.build(
                    manifest_path=self._write_manifest(mutated),
                    output_dir=Path(self.temporary.name) / f"drift-{name}",
                    profile="apple-clang")

    def test_fail_closed_rejects_missing_pins_or_production_authority(self) -> None:
        missing = copy.deepcopy(self.manifest)
        del missing["sources"]["route_builder"]
        with self.assertRaisesRegex(BUILDER.ReplayError,
                                    "script pins are incomplete"):
            BUILDER.build(
                manifest_path=self._write_manifest(missing),
                output_dir=Path(self.temporary.name) / "missing",
                profile="apple-clang")
        authorized = copy.deepcopy(self.manifest)
        authorized["routing"]["production_placement"] = False
        with self.assertRaisesRegex(BUILDER.ReplayError,
                                    "routing authority drift"):
            BUILDER.build(
                manifest_path=self._write_manifest(authorized),
                output_dir=Path(self.temporary.name) / "authority",
                profile="apple-clang")


if __name__ == "__main__":
    unittest.main()
