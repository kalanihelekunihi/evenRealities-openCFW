#!/usr/bin/env python3
"""Focused fail-closed gates for the FreeRTOS+CLI source snapshot."""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party" / "freertos-plus-cli"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
PATCH = SNAPSHOT / "g2-patches" / "0001-suppress-unknown-command-for-blank-input.patch"
EXPECTED_PROVENANCE_SIZE = 8336
EXPECTED_PROVENANCE_SHA256 = "4ccf6f4f904cff75a6d166425167aa79678083175247086597b60c9b3645547e"
EXPECTED_VERIFIER_SIZE = 21946
EXPECTED_VERIFIER_SHA256 = "dccaf4e42a653923449dac7c692391d6e432a8ff07ead279e936de0167729c30"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_freertos_plus_cli_snapshot", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeRTOSPlusCLISnapshotTests(unittest.TestCase):
    maxDiff = None

    def run_verifier(self, verifier: Path = VERIFIER) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, str(verifier)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )

    def test_offline_verifier_and_metadata_are_pinned(self) -> None:
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, "FreeRTOS+CLI source snapshot verification passed\n")
        self.assertEqual(PROVENANCE.stat().st_size, EXPECTED_PROVENANCE_SIZE)
        self.assertEqual(digest(PROVENANCE.read_bytes()), EXPECTED_PROVENANCE_SHA256)
        self.assertEqual(VERIFIER.stat().st_size, EXPECTED_VERIFIER_SIZE)
        self.assertEqual(digest(VERIFIER.read_bytes()), EXPECTED_VERIFIER_SHA256)

    def test_source_choice_is_qualified_and_vendor_glue_is_excluded(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(
            value["upstream"]["selected_commit"],
            "43defa566cc440251dbd6b48d1fcca27f88cfcdd",
        )
        self.assertEqual(
            value["upstream"]["selected_tree"],
            "1244875832c8ef8a39ee5b97a9dad657f7ea13ec",
        )
        self.assertEqual(value["upstream"]["declared_component_version"], "V1.0.4")
        self.assertFalse(value["selection"]["exact_g2_vendor_commit_proven"])
        self.assertEqual(value["selection"]["selected_file_count"], 4)
        self.assertEqual(
            value["selection"]["integration_status"],
            "authenticated and verified offline; no production registration",
        )
        glue = value["g2_boundary"]["first_party_glue"]
        self.assertFalse(glue["included"])
        self.assertEqual(glue["registered_descriptor_count"], 76)
        self.assertEqual(
            glue["descriptor_aggregate_sha256"],
            "268128313cc6da003e82e72b4341f5208a480196b3da1a1c0085b49a79d51788",
        )

    def test_selected_and_ceiling_git_objects_are_reconstructible(self) -> None:
        verifier = load_verifier()
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        trees = verifier.verify_object_closure(value)
        self.assertEqual(len(trees), 7)
        ceiling = value["upstream"]["identical_file_pair_ceiling"]
        self.assertEqual(
            ceiling["commit"],
            "1309654d6f5d1342b4a9d3d7ae0824e8fcaefaf2",
        )
        self.assertEqual(
            ceiling["tree"],
            "6d95fe580646a9f12b9cc2f37bd1e9c4d72fbad7",
        )
        self.assertEqual(ceiling["unchanged_paths"], ["FreeRTOS_CLI.c", "FreeRTOS_CLI.h"])

        closure = json.loads((SNAPSHOT / "upstream" / "objects.json").read_text(encoding="utf-8"))
        for record in closure["commits"]:
            payload = base64.b64decode(record["payload_base64"], validate=True)
            self.assertEqual(verifier.git_object_sha1("commit", payload), record["oid"])
        for record in closure["trees"]:
            payload = base64.b64decode(record["payload_base64"], validate=True)
            self.assertEqual(verifier.git_object_sha1("tree", payload), record["oid"])

    def test_recovered_abi_and_unresolved_configuration_are_exact(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        boundary = value["g2_boundary"]
        abi = boundary["recovered_abi"]
        self.assertEqual(abi["descriptor_size"], 16)
        self.assertEqual(
            abi["descriptor_offsets"],
            {
                "pcCommand": 0,
                "pcHelpString": 4,
                "pxCommandInterpreter": 8,
                "cExpectedNumberOfParameters": 12,
            },
        )
        self.assertEqual(abi["registered_list_node_size"], 8)
        self.assertEqual(abi["variable_parameter_sentinel"], -1)
        config = boundary["recovered_configuration"]
        self.assertEqual(config["effective_output_buffer_bytes"], 128)
        self.assertEqual(config["safe_nul_terminated_input_payload_max"], 127)
        self.assertEqual(config["configSUPPORT_STATIC_ALLOCATION"], "not statically proven")
        self.assertEqual(config["selected_openCFW_static_allocation_policy"], "unresolved")
        self.assertIn("not recoverable", config["configCOMMAND_INT_MAX_OUTPUT_SIZE"])
        self.assertIn("not recoverable", config["configAPPLICATION_PROVIDES_cOutputBuffer"])

    def test_blank_input_delta_is_narrow_and_matches_authenticated_span(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        patch = value["g2_boundary"]["local_patch"]
        self.assertEqual(patch["stock_instruction_range"], ["0x005848CA", "0x005848F4"])
        self.assertEqual(patch["stock_instruction_size"], 42)
        self.assertEqual(
            patch["stock_instruction_sha256"],
            "4ed35ac83ff6802181aee553929f5eadff5e6b6c797601145d1c688c88eae7c1",
        )
        text = PATCH.read_text(encoding="utf-8")
        self.assertNotIn("CLI_Command_Definition_t", text)
        self.assertNotIn("RegisterCommand", text)
        self.assertEqual(text.count("--- a/FreeRTOS_CLI.c"), 1)
        self.assertEqual(text.count("+++ b/FreeRTOS_CLI.c"), 1)

    def test_source_object_and_patch_mutations_fail_closed(self) -> None:
        mutations = (
            ("FreeRTOS_CLI.c", b"X", "source size changed: FreeRTOS_CLI.c"),
            ("upstream/objects.json", b" ", "object closure size changed"),
            (
                "g2-patches/0001-suppress-unknown-command-for-blank-input.patch",
                b" ",
                "G2 patch file size changed",
            ),
        )
        for relative, suffix, expected in mutations:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                copied = Path(tmp) / "openCFW" / "third_party" / "freertos-plus-cli"
                copied.parent.mkdir(parents=True)
                shutil.copytree(SNAPSHOT, copied)
                target = copied / relative
                target.write_bytes(target.read_bytes() + suffix)
                result = self.run_verifier(copied / "verify_snapshot.py")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(expected, result.stdout)

    def test_verifier_registration_is_allowed_but_production_references_fail_closed(self) -> None:
        verifier = load_verifier()
        registrations = {
            "manifests/production.json": '{"source":"third_party/freertos-plus-cli/FreeRTOS_CLI.c"}\n',
            "manifests/production-dot.json": '{"source":"third_party/./freertos-plus-cli/FreeRTOS_CLI.c"}\n',
            "manifests/production-double.json": '{"source":"third_party//freertos-plus-cli/FreeRTOS_CLI.c"}\n',
            "manifests/production-backslash.json": '{"source":"third_party\\\\freertos-plus-cli\\\\FreeRTOS_CLI.c"}\n',
            "components/apollo_main/core_overlay/overlay.json": (
                '{"sources":[{"path":"third_party/freertos-plus-cli/FreeRTOS_CLI.c"}]}\n'
            ),
            "components/apollo_main/core_overlay/build_component.py": (
                'CLI_SOURCE = "third_party/freertos-plus-cli/FreeRTOS_CLI.c"\n'
            ),
            "components/apollo_main/core_overlay/cli_glue.c": (
                '#include "third_party/freertos-plus-cli/FreeRTOS_CLI.h"\n'
            ),
            "tools/apollo_overlay.py": (
                'CLI_SOURCE = "third_party/freertos-plus-cli/FreeRTOS_CLI.c"\n'
            ),
        }
        old_root = verifier.ROOT
        try:
            for relative, content in registrations.items():
                with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "openCFW"
                    root.mkdir()
                    (root / "Makefile").write_text(
                        "FREERTOS_PLUS_CLI_DIR := third_party/freertos-plus-cli\n"
                        "freertos-plus-cli-snapshot:\n"
                        "\t$(PYTHON) $(FREERTOS_PLUS_CLI_DIR)/verify_snapshot.py\n",
                        encoding="utf-8",
                    )
                    verifier.ROOT = root
                    verifier.verify_production_exclusion()

                    generated = (
                        root / "components" / "apollo_main" / "core_overlay"
                        / "build-console-a" / "build-report.json"
                    )
                    generated.parent.mkdir(parents=True, exist_ok=True)
                    generated.write_text(
                        '{"source":"third_party/freertos-plus-cli/FreeRTOS_CLI.c"}\n',
                        encoding="utf-8",
                    )
                    verifier.verify_production_exclusion()

                    configured = root / relative
                    configured.parent.mkdir(parents=True, exist_ok=True)
                    configured.write_text(content, encoding="utf-8")
                    with self.assertRaisesRegex(
                        SystemExit,
                        "snapshot is production-configured",
                    ):
                        verifier.verify_production_exclusion()

            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "openCFW"
                root.mkdir()
                (root / "Makefile").write_text(
                    "FREERTOS_PLUS_CLI_DIR := third_party/freertos-plus-cli\n"
                    "freertos-plus-cli-snapshot:\n"
                    "\t$(PYTHON) $(FREERTOS_PLUS_CLI_DIR)/verify_snapshot.py\n"
                    "core-component:\n"
                    "\t$(CC) -c $(FREERTOS_PLUS_CLI_DIR)/FreeRTOS_CLI.c\n",
                    encoding="utf-8",
                )
                verifier.ROOT = root
                with self.assertRaisesRegex(
                    SystemExit,
                    "snapshot is production-configured by Makefile:5",
                ):
                    verifier.verify_production_exclusion()
        finally:
            verifier.ROOT = old_root

    def test_patch_applies_and_compiles_with_blank_input_behavior(self) -> None:
        compiler = shutil.which("cc")
        patch_tool = shutil.which("patch")
        if compiler is None or patch_tool is None:
            self.skipTest("host C compiler or patch utility is unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            build = Path(tmp)
            shutil.copy2(SNAPSHOT / "FreeRTOS_CLI.c", build / "FreeRTOS_CLI.c")
            shutil.copy2(SNAPSHOT / "FreeRTOS_CLI.h", build / "FreeRTOS_CLI.h")
            applied = subprocess.run(
                [patch_tool, "--batch", "-p1", "-i", str(PATCH)],
                cwd=build,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(applied.returncode, 0, applied.stdout)
            (build / "FreeRTOS.h").write_text(
                """#ifndef FREERTOS_H
#define FREERTOS_H
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
typedef int32_t BaseType_t;
typedef uint32_t UBaseType_t;
#define pdFALSE 0
#define pdTRUE 1
#define pdFAIL 0
#define pdPASS 1
#define configCOMMAND_INT_MAX_OUTPUT_SIZE 128
#define configAPPLICATION_PROVIDES_cOutputBuffer 0
#define configASSERT(x) do { if (!(x)) abort(); } while (0)
#define taskENTER_CRITICAL() do { } while (0)
#define taskEXIT_CRITICAL() do { } while (0)
static inline void *pvPortMalloc(size_t size) { return malloc(size); }
#endif
""",
                encoding="utf-8",
            )
            (build / "task.h").write_text(
                "#ifndef TASK_H\n#define TASK_H\n#endif\n",
                encoding="utf-8",
            )
            (build / "harness.c").write_text(
                """#include <string.h>
#include "FreeRTOS.h"
#include "FreeRTOS_CLI.h"

int main(void)
{
    char output[128];
    memset(output, 'X', sizeof(output));
    if (FreeRTOS_CLIProcessCommand("", output, sizeof(output)) != pdFALSE || output[0] != 'X') {
        return 1;
    }
    memset(output, 'Y', sizeof(output));
    if (FreeRTOS_CLIProcessCommand("\\r", output, sizeof(output)) != pdFALSE || output[0] != 'Y') {
        return 2;
    }
    memset(output, 0, sizeof(output));
    if (FreeRTOS_CLIProcessCommand("unknown", output, sizeof(output)) != pdFALSE) {
        return 3;
    }
    return strncmp(output, "Command not recognised.", 23) == 0 ? 0 : 4;
}
""",
                encoding="utf-8",
            )
            binary = build / "cli-host-test"
            compiled = subprocess.run(
                [
                    compiler,
                    "-std=c11",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-I",
                    str(build),
                    str(build / "FreeRTOS_CLI.c"),
                    str(build / "harness.c"),
                    "-o",
                    str(binary),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(compiled.returncode, 0, compiled.stdout)
            executed = subprocess.run(
                [str(binary)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(executed.returncode, 0, executed.stdout)


if __name__ == "__main__":
    unittest.main()
