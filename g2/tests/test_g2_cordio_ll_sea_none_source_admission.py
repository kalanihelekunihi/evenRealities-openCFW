# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
ADMISSION = G2 / "research/admission/cordio_ll_sea_none"
ANALYZER = G2 / "tools/analyze_g2_cordio_ll_sea_none_source_admission.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("none_source_admission", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class NoneSourceAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().run_audit()

    def test_all_198_census_rows_have_one_licensed_provider(self) -> None:
        census = self.report["census"]
        self.assertEqual((census["functions"], census["bytes"]), (198, 33644))
        self.assertEqual(census["unclassified"], {"functions": 0, "bytes": 0})
        self.assertEqual(
            census["mapping_sha256"],
            "6fb586837c60efec60ac5dc603315cfc25bab6809cda67b90fece419658beb56",
        )
        rows = census["records"]
        self.assertEqual(len({row["start"] for row in rows}), 198)
        self.assertEqual(
            {row["license"] for row in rows},
            {"FTL", "LicenseRef-SEGGER-RTT-Redistributable"},
        )

    def test_provider_and_upstream_license_pins_are_closed(self) -> None:
        providers = self.report["providers"]
        ft = providers["freetype"]
        self.assertEqual((ft["functions"], ft["bytes"]), (192, 33124))
        self.assertEqual(ft["version"], "2.9.1")
        self.assertEqual(ft["license"], "FTL")
        self.assertTrue(ft["adobe_file_notice_and_patent_grant_retained"])
        self.assertEqual(len(ft["module_pins"]), 19)
        rtt = providers["segger_rtt"]
        self.assertEqual((rtt["functions"], rtt["bytes"]), (6, 520))
        self.assertEqual(rtt["version"], "6.18a")
        self.assertTrue(rtt["source_materialized"])
        self.assertEqual(len(rtt["local_file_pins"]), 4)
        self.assertEqual(
            rtt["license_path"], "external/segger_rtt/license/license.txt"
        )

    def test_four_non_census_boundaries_are_typed_and_sha_pinned(self) -> None:
        boundaries = self.report["typed_non_census_boundaries"]
        self.assertEqual((boundaries["clusters"], boundaries["bytes"]), (4, 1118))
        self.assertEqual(boundaries["unclassified"], {"clusters": 0, "bytes": 0})
        self.assertEqual(
            {row["status"] for row in boundaries["records"]},
            {"typed-external-not-callable"},
        )
        self.assertTrue(all(len(row["body_sha256"]) == 64 for row in boundaries["records"]))

    def test_binary_overlay_remains_fail_closed(self) -> None:
        self.assertTrue(self.report["source_admission_record_ready"])
        self.assertTrue(self.report["redistributable_source_bundle_ready"])
        self.assertFalse(self.report["binary_overlay_admission_ready"])
        self.assertFalse(self.report["production_routed"])
        self.assertGreaterEqual(len(self.report["binary_admission_blockers"]), 6)
        production_text = "\n".join(
            path.read_text(errors="ignore")
            for path in (G2 / "components").rglob("*")
            if path.is_file()
        )
        self.assertNotIn("runtime_none_source_admission", production_text)
        self.assertNotIn("cordio_ll_sea_none_source_admission", production_text)

    def test_host_harness_links_and_runs(self) -> None:
        compiler = shutil.which("cc") or shutil.which("clang")
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            main = temp_path / "main.c"
            main.write_text(
                '#include "runtime_none_source_admission.h"\n'
                "int main(void) { return open_cfw_none_source_admission_validate() ? 0 : 1; }\n"
            )
            output = temp_path / "host-harness"
            subprocess.run(
                [
                    compiler,
                    "-std=c11",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-I",
                    str(ADMISSION),
                    str(ADMISSION / "runtime_none_source_admission.c"),
                    str(main),
                    "-o",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run([str(output)], check=True, capture_output=True, text=True)

    def test_cortex_m55_freestanding_harness_compiles(self) -> None:
        clang = shutil.which("clang")
        self.assertIsNotNone(clang)
        flags = [
            "--target=arm-none-eabi",
            "-mcpu=cortex-m55",
            "-mthumb",
            "-std=c11",
            "-O2",
            "-ffreestanding",
            "-fno-builtin",
            "-ffunction-sections",
            "-fdata-sections",
            "-fno-unwind-tables",
            "-fno-asynchronous-unwind-tables",
            "-Wall",
            "-Wextra",
            "-Werror",
        ]
        with tempfile.TemporaryDirectory() as temp:
            objects = []
            sources = (
                ADMISSION / "runtime_none_source_admission.c",
                ADMISSION / "cortex_m55_harness.c",
                ADMISSION / "segger_rtt_6_18a/SEGGER_RTT.c",
                ADMISSION / "target_compat/string.c",
            )
            for source in sources:
                target = Path(temp) / (source.stem + ".o")
                extra = []
                if source.name == "SEGGER_RTT.c":
                    extra = [
                        "-DSEGGER_RTT_CONF_H",
                        "-DSEGGER_RTT_MAX_NUM_UP_BUFFERS=3",
                        "-DSEGGER_RTT_MAX_NUM_DOWN_BUFFERS=3",
                        "-I",
                        str(ADMISSION / "target_compat"),
                        "-I",
                        str(ADMISSION / "segger_rtt_6_18a"),
                    ]
                subprocess.run(
                    [clang, *flags, *extra, "-c", str(source), "-o", str(target)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                objects.append(target)
            self.assertTrue(all(obj.stat().st_size > 0 for obj in objects))
            descriptions = "\n".join(
                subprocess.run(
                    ["file", str(obj)], check=True, capture_output=True, text=True
                ).stdout
                for obj in objects
            )
            self.assertIn("ARM", descriptions)
            nm = shutil.which("nm")
            self.assertIsNotNone(nm)
            symbols = "\n".join(
                subprocess.run(
                    [nm, str(obj)], check=True, capture_output=True, text=True
                ).stdout
                for obj in objects
            )
            for symbol in ("memcpy", "strcpy", "strlen"):
                self.assertIn(f" T {symbol}", symbols)

    def test_cli_is_deterministic(self) -> None:
        first = subprocess.run(
            [sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True
        ).stdout
        second = subprocess.run(
            [sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True
        ).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["census"]["functions"], 198)


if __name__ == "__main__":
    unittest.main()
