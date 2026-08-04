#!/usr/bin/env python3
"""Guard the fail-closed G2 CmBacktrace version/config recovery."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_cmbacktrace_version.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cmbacktrace_version", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CmBacktraceVersionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.data = cls.analyzer._load()
        cls.findings = cls.analyzer.audit(cls.data)

    def test_identity_and_complete_message_table_are_pinned(self) -> None:
        identity = self.findings["identity"]
        self.assertTrue(identity["definitive"])
        self.assertEqual(identity["print_info_table"], 0x006D3718)
        self.assertEqual(identity["print_info_entries"], 39)
        self.assertEqual(identity["fault_entry"], 0x005944BC)
        self.assertEqual(
            identity["vendor_addr2line_path"],
            "third_party/CmBacktrace/tools/addr2line/win64/addr2line.exe",
        )
        self.assertEqual(self.analyzer.PRINT_INFO[0][0], 0x006DA1C4)
        self.assertIn("main stack information", self.analyzer.PRINT_INFO[0][1])
        self.assertIn("-afpiC %.*s", self.analyzer.PRINT_INFO[8][1])
        self.assertIn("stack overflow (hardware check)", self.analyzer.PRINT_INFO[29][1])

    def test_narrowest_defensible_upstream_interval_is_reported(self) -> None:
        version = self.findings["version_recovery"]
        self.assertIsNone(version["exact_release_or_commit"])
        self.assertEqual(
            version["classification"],
            "untagged post-1.4.1 1.4.2-development lineage",
        )
        self.assertEqual(
            version["compatible_unmodified_upstream_interval"],
            {
                "first": "4abadfa0c4f86f22352aa5ab9ebbb4f687125a1c",
                "last": "73714489f9d8af130aacb515586b397b604a5768",
                "first_date": "2023-08-20",
                "last_date": "2024-07-03",
            },
        )
        self.assertEqual(
            version["lower_bound_evidence"],
            [
                "-afpiC %.*s addr2line format",
                "CMB_CALL_STACK_MAX_DEPTH=32",
                "CMB_DUMP_STACK_DEPTH_SIZE=16",
                "CMB_NAME_MAX+1 storage layout",
            ],
        )
        self.assertIn("55e7b69", version["upper_bound_evidence"])
        self.assertIn("compiled out", version["why_not_exact"])

    def test_effective_configuration_and_freertos_abi_are_pinned(self) -> None:
        config = self.findings["effective_configuration"]
        self.assertEqual(
            {
                key: config[key]
                for key in (
                    "CMB_USING_OS_PLATFORM",
                    "CMB_OS_PLATFORM_TYPE",
                    "CMB_USING_DUMP_STACK_INFO",
                    "CMB_CALL_STACK_MAX_DEPTH",
                    "CMB_DUMP_STACK_DEPTH_SIZE",
                    "CMB_NAME_MAX",
                    "compiler",
                    "sizeof_StackType_t",
                )
            },
            {
                "CMB_USING_OS_PLATFORM": True,
                "CMB_OS_PLATFORM_TYPE": "CMB_OS_PLATFORM_FREERTOS",
                "CMB_USING_DUMP_STACK_INFO": True,
                "CMB_CALL_STACK_MAX_DEPTH": 32,
                "CMB_DUMP_STACK_DEPTH_SIZE": 16,
                "CMB_NAME_MAX": 40,
                "compiler": "IAR (__ICCARM__ branch; .out ELF extension)",
                "sizeof_StackType_t": 4,
            },
        )
        self.assertEqual(config["main_stack_start"], 0x2007D000)
        self.assertEqual(config["main_stack_size"], 0x3000)
        self.assertEqual(config["code_start"], 0x00438400)
        self.assertEqual(config["code_size"], 0x1C1C56)
        self.assertEqual(config["name_buffers"], [0x2007351C, 0x20073548, 0x20073574])
        self.assertIn("M33-class", config["CMB_CPU_PLATFORM_BEHAVIOR"])
        self.assertIn("cannot be excluded", config["CMB_CPU_PLATFORM_TYPE"])

        adapter = self.findings["freertos_adapter"]
        self.assertEqual(adapter["current_tcb_pointer"], 0x20074A20)
        self.assertEqual(adapter["stack_base_offset"], 0x30)
        self.assertEqual(adapter["stack_depth_offset"], 0x54)
        self.assertEqual(adapter["task_name_offset"], 0x34)
        self.assertEqual(
            adapter["entries"],
            {
                "vTaskStackAddr": 0x0045601F,
                "vTaskStackSize": 0x00456027,
                "vTaskName": 0x0045602F,
            },
        )

    def test_init_arguments_and_linker_ranges_are_pinned(self) -> None:
        args = self.findings["init_arguments"]
        self.assertEqual(args["firmware_name"]["value"], "product/s200/app/Release/Exe/s200_app")
        self.assertEqual(args["hardware_version"]["value"], "V1.0.0")
        self.assertEqual(args["software_version"]["value"], "2.2.6.10")
        bodies = self.findings["pinned_bodies"]
        self.assertEqual(bodies["cm_backtrace_init"]["size"], 138)
        self.assertEqual(bodies["cm_backtrace_fault"]["size"], 786)

    def test_upstream_commits_hashes_and_mit_license_are_pinned(self) -> None:
        upstream = self.findings["upstream_provenance"]
        self.assertEqual(upstream["repository"], "https://github.com/armink/CmBacktrace.git")
        self.assertEqual(upstream["license"], "MIT")
        self.assertEqual(
            upstream["license_sha256"],
            "e8ed0e84184d2130bd1fcf5a52ce8c16b5bf338c272cab6bbd7993a9d723934e",
        )
        self.assertEqual(upstream["tag_before"]["name"], "1.4.1")
        self.assertEqual(upstream["tag_after"]["name"], "1.5.0")
        self.assertEqual(upstream["compatible_floor"]["advertised_version"], "1.4.2")
        self.assertEqual(upstream["compatible_ceiling"]["advertised_version"], "1.4.2")
        self.assertEqual(
            upstream["compatible_floor"]["files"]["cm_backtrace/Languages/en-US/cmb_en_US.h"],
            upstream["compatible_ceiling"]["files"]["cm_backtrace/Languages/en-US/cmb_en_US.h"],
        )
        self.assertIn("MIT", self.findings["license_correction"])
        self.assertIn("Apache-2.0", self.findings["license_correction"])

    def test_mutated_table_pointer_and_text_are_rejected(self) -> None:
        for run in (self.analyzer.PRINT_INFO_TABLE, self.analyzer.PRINT_INFO[8][0]):
            with self.subTest(run=f"0x{run:08x}"):
                mutated = bytearray(self.data)
                mutated[run - self.analyzer.LOAD_BASE] ^= 1
                with self.assertRaises(self.analyzer.AuditError):
                    self.analyzer.audit(bytes(mutated))

    def test_mutated_bodies_and_decisive_windows_are_rejected(self) -> None:
        runs = [
            self.analyzer.PINNED_BODIES["cm_backtrace_init"][0],
            self.analyzer.PINNED_BODIES["cm_backtrace_fault"][0] + 0x15A,
            self.analyzer.FREERTOS_ADAPTER[0],
            self.analyzer.PRE_ALIGNMENT_PATH[0],
            self.analyzer.INIT_CALLER[0],
            next(iter(self.analyzer.INIT_ARGUMENT_POINTERS)),
            next(iter(self.analyzer.INIT_LINKER_LITERALS)),
            next(iter(self.analyzer.INIT_NAME_BUFFER_LITERALS)),
            next(iter(self.analyzer.OTHER_POINTER_PINS)),
        ]
        for run in runs:
            with self.subTest(run=f"0x{run:08x}"):
                mutated = bytearray(self.data)
                mutated[run - self.analyzer.LOAD_BASE] ^= 1
                with self.assertRaises(self.analyzer.AuditError):
                    self.analyzer.audit(bytes(mutated))

    def test_cli_text_and_json_modes(self) -> None:
        text = subprocess.run(
            [sys.executable, str(ANALYZER)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertIn("4abadfa0..73714489", text)
        self.assertIn("license: MIT", text)
        parsed = json.loads(
            subprocess.run(
                [sys.executable, str(ANALYZER), "--json"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        )
        self.assertEqual(parsed["component"], "armink/CmBacktrace")
        self.assertEqual(parsed["analysis_mode"], "read-only; no hardware or flash operation")


if __name__ == "__main__":
    unittest.main()
