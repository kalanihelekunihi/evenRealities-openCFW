# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/apollo_main/liblc3_encoder"
BUILDER = COMPONENT / "build_component.py"
CONFIG = COMPONENT / "component.json"
SPEC = importlib.util.spec_from_file_location("apollo_liblc3_encoder", BUILDER)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ApolloLiblc3EncoderComponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = "/usr/bin/clang"
        cls.lld = shutil.which("ld.lld")
        if cls.lld is None or not Path(cls.clang).is_file():
            raise unittest.SkipTest("reviewed Apple Clang/LLD profile unavailable")
        config = json.loads(CONFIG.read_text())
        active = config["profiles"]["apple-clang"]
        try:
            compiler = MODULE.compiler_version(cls.clang)
            linker = MODULE._linker_version(cls.lld)
        except (OSError, MODULE.BuildError) as error:
            raise unittest.SkipTest(str(error)) from error
        if not compiler.startswith(active["reviewed_compiler_version_prefix"]) or \
                not linker.startswith(active["reviewed_linker_version_prefix"]):
            raise unittest.SkipTest("reviewed Apple Clang/LLD profile unavailable")

    def build(self, output: Path, config: Path = CONFIG):
        return MODULE.build(
            config_path=config,
            output_dir=output,
            clang=self.clang,
            lld=self.lld,
            profile="apple-clang",
        )

    def test_two_builds_have_identical_artifacts_and_reports(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-liblc3-component-") as tmp:
            first = Path(tmp) / "first"
            second = Path(tmp) / "second"
            report_a = self.build(first)
            report_b = self.build(second)
            names = {
                "build-report.json",
                "liblc3_encoder.text.bin",
                "liblc3_encoder.rodata.bin",
                "liblc3_encoder.data.bin",
                "liblc3_encoder.relocatable.o",
            }
            self.assertEqual({path.name for path in first.iterdir()}, names)
            self.assertEqual({path.name for path in second.iterdir()}, names)
            for name in names:
                self.assertEqual((first / name).read_bytes(),
                                 (second / name).read_bytes(), name)
            self.assertEqual(report_a, report_b)
            self.assertEqual(report_a["linked_object"], {
                "file": "liblc3_encoder.relocatable.o",
                "size": 145_264,
                "sha256": "5143ab77e2496cdd13de674affc22ed030a1a65e2027c4c916da72fd944cb820",
            })
            self.assertEqual(
                {name: item["size"] for name, item in report_a["artifacts"].items()},
                {"text": 43_248, "rodata": 85_088, "data": 404},
            )
            self.assertEqual(report_a["canonical_cantunwind_rows_discarded"], 87)
            self.assertEqual(report_a["global_function_count"], 35)
            self.assertEqual(report_a["relocations"]["total"], 567)
            self.assertEqual(report_a["relocations"]["by_section"],
                {".data": 92, ".rodata": 78, ".text": 397})
            self.assertEqual(report_a["routing"], {
                "stock_patch_sites": [],
                "service_audio_routed": False,
                "firmware_image_emitted": False,
            })
            self.assertFalse(report_a["placement"]["assigned"])
            self.assertFalse(report_a["hardware_operations"])

    def test_retained_import_allowlist_is_exact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-liblc3-imports-") as tmp:
            output = Path(tmp) / "out"
            report = self.build(output)
            admission = json.loads(
                (ROOT / "components/shared/liblc3/encoder_source_admission.json")
                .read_text()
            )
            self.assertEqual(report["retained_imports"],
                admission["allowed_external_runtime_relocations"])
            with self.assertRaisesRegex(MODULE.BuildError,
                                        "retained imports differ"):
                MODULE._validate_linked_object(
                    output / "liblc3_encoder.relocatable.o",
                    list(report["roots"]),
                    set(report["retained_imports"]) - {"sqrtf"},
                )

    def test_receipt_or_routing_mutation_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-liblc3-drift-") as tmp:
            temporary = Path(tmp)
            config = json.loads(CONFIG.read_text())
            bad_receipt = copy.deepcopy(config)
            bad_receipt["profiles"]["apple-clang"]["expected"]["artifacts"][
                "text"
            ]["sha256"] = "0" * 64
            bad_receipt_path = temporary / "bad-receipt.json"
            bad_receipt_path.write_text(json.dumps(bad_receipt))
            with self.assertRaisesRegex(MODULE.BuildError,
                                        "reviewed receipt"):
                self.build(temporary / "bad-receipt", bad_receipt_path)

            bad_route = copy.deepcopy(config)
            bad_route["placement"] = {"address": 0x12345678}
            bad_route_path = temporary / "bad-route.json"
            bad_route_path.write_text(json.dumps(bad_route))
            with self.assertRaisesRegex(MODULE.BuildError,
                                        "gained placement"):
                self.build(temporary / "bad-route", bad_route_path)


if __name__ == "__main__":
    unittest.main()
