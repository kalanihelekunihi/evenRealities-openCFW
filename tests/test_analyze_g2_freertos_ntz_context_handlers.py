#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = (
    ROOT
    / "tools"
    / "analyze_g2_freertos_ntz_context_handlers.py"
)


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_freertos_ntz_context_handlers",
        ANALYZER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load FreeRTOS NTZ handler analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeRTOSNtzContextHandlerAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.result = cls.analyzer.run_audit()

    def test_exact_stock_boundaries_hashes_and_instruction_mode(self) -> None:
        functions = self.result["functions"]
        expected = {
            "vRestoreContextOfFirstTask": (
                0x005FA058,
                0x005FA07E,
                38,
                (
                    "10edd4871b5f0c829e38618f1003ef0c"
                    "45ec3629219317e23c62a2e255b0f4f8"
                ),
            ),
            "vRaisePrivilege": (
                0x005FA07E,
                0x005FA08C,
                14,
                (
                    "29bceedf776515c291813e4eecd9a836"
                    "378b81550c42d08aee35cf15df3bd8db"
                ),
            ),
            "vStartFirstTask": (
                0x005FA08C,
                0x005FA0A4,
                24,
                (
                    "44ba0097fbbc1d0691837d5c51bee83e"
                    "6b61509c9d89efffee9c202d930e6347"
                ),
            ),
            "PendSV_Handler": (
                0x005FA0C8,
                0x005FA120,
                88,
                (
                    "d8e234bfa34805ad160e41ef54801973"
                    "c9c871b36cf7ac0f365b56fe503253e3"
                ),
            ),
            "SVC_Handler": (
                0x005FA120,
                0x005FA132,
                18,
                (
                    "d0fac197473b52d6ed466462d237ddb20"
                    "dd8096a6507ea559e75d4bd9d88da94"
                ),
            ),
        }
        self.assertEqual(set(functions), set(expected))
        for name, (start, end, size, digest) in expected.items():
            with self.subTest(function=name):
                function = functions[name]
                self.assertEqual(
                    (
                        function["start"],
                        function["end_exclusive"],
                        function["size"],
                        function["sha256"],
                    ),
                    (start, end, size, digest),
                )
                self.assertEqual(function["entry_state"], "Thumb")
                self.assertEqual(
                    function["instruction_set"],
                    "Armv8.1-M Mainline Thumb/Thumb-2, little-endian",
                )
                self.assertEqual(
                    sum(
                        instruction["size"]
                        for instruction in function["instructions"]
                    ),
                    size,
                )
                self.assertTrue(
                    all(
                        instruction["size"] in (2, 4)
                        for instruction in function["instructions"]
                    )
                )

    def test_literal_call_and_data_dependencies_are_exact(self) -> None:
        literals = self.result["literal_dependencies"]
        self.assertEqual(
            [
                (
                    item["function"],
                    item["instruction"],
                    item["literal_address"],
                    item["value"],
                    item["classification"],
                )
                for item in literals
            ],
            [
                (
                    "vRestoreContextOfFirstTask",
                    0x005FA058,
                    0x005FA134,
                    0x20074A20,
                    "pxCurrentTCB",
                ),
                (
                    "vStartFirstTask",
                    0x005FA08C,
                    0x005FA138,
                    0xE000ED08,
                    "SCB_VTOR",
                ),
                (
                    "PendSV_Handler",
                    0x005FA0E0,
                    0x005FA134,
                    0x20074A20,
                    "pxCurrentTCB",
                ),
                (
                    "PendSV_Handler",
                    0x005FA102,
                    0x005FA134,
                    0x20074A20,
                    "pxCurrentTCB",
                ),
            ],
        )

        references = self.result["references"]
        self.assertEqual(
            references["vRestoreContextOfFirstTask"]["incoming_wide"],
            [
                {
                    "address": 0x00442146,
                    "kind": "BL",
                    "target": 0x005FA058,
                    "encoding": "b7f187ff",
                }
            ],
        )
        self.assertEqual(
            references["vStartFirstTask"]["incoming_wide"],
            [
                {
                    "address": 0x00442200,
                    "kind": "BL",
                    "target": 0x005FA08C,
                    "encoding": "b7f144ff",
                }
            ],
        )
        self.assertEqual(
            references["vRaisePrivilege"]["incoming_wide"],
            [],
        )
        for function in references.values():
            self.assertEqual(function["external_interior_wide"], [])
            self.assertEqual(
                function["external_entry_or_interior_narrow"],
                [],
            )

        outgoing = self.result["outgoing_dependencies"]
        self.assertEqual(
            outgoing["PendSV_Handler"]["direct_calls"],
            [
                {
                    "address": 0x005FA0F6,
                    "kind": "BL",
                    "target": 0x004551B4,
                    "classification": "vTaskSwitchContext",
                }
            ],
        )
        self.assertEqual(
            outgoing["SVC_Handler"]["tail_branch"],
            {
                "address": 0x005FA12E,
                "kind": "B.W",
                "target": 0x00442134,
                "classification": "vPortSVCHandler_C",
            },
        )

    def test_exception_vectors_and_references_are_exact(self) -> None:
        self.assertEqual(
            self.result["vectors"],
            {
                "SVC": {
                    "index": 11,
                    "address": 0x0043802C,
                    "value": 0x005FA121,
                    "canonical_target": 0x005FA120,
                    "thumb_bit": 1,
                },
                "PendSV": {
                    "index": 14,
                    "address": 0x00438038,
                    "value": 0x005FA0C9,
                    "canonical_target": 0x005FA0C8,
                    "thumb_bit": 1,
                },
            },
        )
        references = self.result["references"]
        self.assertEqual(
            references["SVC_Handler"]["stored_entry_or_interior"],
            [
                {
                    "address": 0x0043802C,
                    "value": 0x005FA121,
                    "canonical": 0x005FA120,
                    "alignment": 0,
                }
            ],
        )
        self.assertEqual(
            references["PendSV_Handler"]["stored_entry_or_interior"],
            [
                {
                    "address": 0x00438038,
                    "value": 0x005FA0C9,
                    "canonical": 0x005FA0C8,
                    "alignment": 0,
                }
            ],
        )
        for name in (
            "vRestoreContextOfFirstTask",
            "vRaisePrivilege",
            "vStartFirstTask",
        ):
            self.assertEqual(
                references[name]["stored_entry_or_interior"],
                [],
            )

    def test_build_configuration_gaps_are_bounded(self) -> None:
        configuration = self.result["recovered_configuration"]
        for name, value in (
            ("configENABLE_MPU", 0),
            ("configENABLE_TRUSTZONE", 0),
            ("configENABLE_FPU", 1),
            ("configMAX_SYSCALL_INTERRUPT_PRIORITY", 0x30),
            ("portSVC_START_SCHEDULER", 2),
        ):
            with self.subTest(configuration=name):
                self.assertTrue(
                    configuration[name]["binary_determined"]
                )
                self.assertEqual(configuration[name]["value"], value)
        self.assertEqual(
            configuration["portable_layer"]["value"],
            "IAR/ARM_CM55_NTZ/non_secure",
        )
        self.assertTrue(
            configuration["portable_layer"]["binary_determined"]
        )
        self.assertIsNone(configuration["configENABLE_MVE"]["value"])
        self.assertFalse(
            configuration["configENABLE_MVE"]["binary_determined"]
        )
        self.assertEqual(
            configuration["configENABLE_MVE"]["upstream_default"],
            0,
        )
        self.assertIn(
            "none for these five bodies",
            configuration["configENABLE_MVE"]["emission_relevance"],
        )

        handler = self.result["support_spans"]["vPortSVCHandler_C"]
        self.assertEqual(
            handler["direct_bl"],
            [
                {"address": 0x00442142, "target": 0x004420A6},
                {"address": 0x00442146, "target": 0x005FA058},
                {"address": 0x0044214C, "target": 0x005FA0A4},
            ],
        )

    def test_upstream_release_source_blocks_and_abi_are_authenticated(
        self,
    ) -> None:
        upstream = self.result["upstream"]
        self.assertEqual(upstream["release"], "FreeRTOS-Kernel V10.5.1")
        self.assertEqual(
            upstream["commit"],
            "def7d2df2b0506d3d249334974f51e427c17a41c",
        )
        self.assertEqual(
            upstream["tree"],
            "7496dfa815c3cea2f45a090c6e92d113f494b930",
        )
        self.assertEqual(upstream["license"], "MIT")
        self.assertEqual(
            upstream["portable_layer"],
            "IAR/ARM_CM55_NTZ/non_secure",
        )
        self.assertEqual(
            upstream["portasm"]["sha256"],
            "eaa83b3867edec5560c69f2a21facd7a"
            "ff3c0f3bfcdfc5751722375ae328ee8f",
        )
        self.assertEqual(
            upstream["portasm"]["git_blob_sha1"],
            "4d02a431e1d759f12f50e70fc55a7b0b4d368e89",
        )
        self.assertEqual(
            {
                name: (
                    block["line_start"],
                    block["line_end_inclusive"],
                    block["sha256"],
                )
                for name, block in upstream["source_blocks"].items()
            },
            {
                "vRestoreContextOfFirstTask": (
                    82,
                    134,
                    (
                        "117988195a20a6173b75d012cc5b36a8"
                        "fc186685ebdd387e1074ce268d9bdfbd"
                    ),
                ),
                "vRaisePrivilege": (
                    137,
                    141,
                    (
                        "73109ec741c185e9a831a98656a1ad6b"
                        "b1fbafdc0138aff2a2f809b76c7c7ebf"
                    ),
                ),
                "vStartFirstTask": (
                    144,
                    153,
                    (
                        "d6000ef7822e3b5a9ec14d07b6b401a"
                        "bb6858a60ce0405d5a736f4cf95c2d5ed"
                    ),
                ),
                "PendSV_Handler": (
                    172,
                    251,
                    (
                        "ea3746fb4f92a56c1fcba4ec96107539"
                        "b6a74e3d7bb3d910bb6554de6478a683"
                    ),
                ),
                "SVC_Handler": (
                    254,
                    259,
                    (
                        "dbac230cb37c6e0c21cc139dfe97d4ec"
                        "f74c44e3edfe7c9fe5a5c623546f3aaa"
                    ),
                ),
            },
        )
        self.assertEqual(
            upstream["abi_declaration"],
            "naked PRIVILEGED_FUNCTION",
        )

    def test_promotion_order_is_risk_bounded_and_not_flash_authority(
        self,
    ) -> None:
        assessment = self.result["promotion_assessment"]
        self.assertEqual(
            [
                item["functions"]
                for item in assessment["safest_atomic_order"]
            ],
            [
                ["vRaisePrivilege"],
                ["vRestoreContextOfFirstTask"],
                ["vStartFirstTask", "SVC_Handler"],
                ["PendSV_Handler"],
            ],
        )
        self.assertTrue(assessment["hardware_validation_required_before_flash"])
        self.assertFalse(assessment["this_audit_authorizes_flash"])
        self.assertTrue(self.result["read_only"])
        self.assertFalse(self.result["hardware_access"])
        self.assertFalse(self.result["flash_writes"])

    def test_json_cli_is_read_only_and_machine_readable(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["read_only"])
        self.assertFalse(result["hardware_access"])
        self.assertFalse(result["flash_writes"])
        self.assertEqual(len(result["functions"]), 5)

    def test_authentication_rejects_a_mutated_package(self) -> None:
        package = bytearray(self.analyzer.DEFAULT_IMAGE.read_bytes())
        offset = (
            self.analyzer.PACKAGE_PREAMBLE_SIZE
            + self.analyzer.FUNCTION_BY_NAME[
                "vRaisePrivilege"
            ].start
            - self.analyzer.APPLICATION_BASE
        )
        package[offset] ^= 0x01
        with tempfile.TemporaryDirectory() as temporary:
            mutated = Path(temporary) / "mutated.bin"
            mutated.write_bytes(package)
            with self.assertRaisesRegex(
                self.analyzer.AuditError,
                "package SHA-256 drift",
            ):
                self.analyzer.run_audit(mutated)


if __name__ == "__main__":
    unittest.main()
