#!/usr/bin/env python3
"""Focused fail-closed gates for the CmBacktrace compatibility snapshot."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party" / "cmbacktrace"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
README = SNAPSHOT / "README.openCFW.md"
EXPECTED_PROVENANCE_SIZE = 13064
EXPECTED_PROVENANCE_SHA256 = "2ed8ad33ae5d59f565956cb4aeadfc4897dfb690b96f26ae845132084a76af88"
EXPECTED_VERIFIER_SIZE = 31757
EXPECTED_VERIFIER_SHA256 = "112b02f435de456c86dbb31f78a8e3cbf6cf325e6b86bfae0bc3d7c11c41ecb9"
EXPECTED_README_SIZE = 4085
EXPECTED_README_SHA256 = "1c3822a19b991d8fb595e8220a9f1751f343b6dbcd8f9fa7e5e287fe320be326"
EXPECTED_RECORDS_SHA256 = "85f08955771a380589634c50fe2771aa38d0f2cc3acc5c3251c0d3b12b2184ae"
EXPECTED_PRODUCTION_RECORDS_SHA256 = "87791a565fa7d0242848ee90b0023bde03d395297c3b1f16f9dee748d5d17596"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return digest(encoded)


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_cmbacktrace_snapshot", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CmBacktraceSnapshotTests(unittest.TestCase):
    maxDiff = None

    def run_verifier(self, verifier: Path = VERIFIER) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            ["python3", str(verifier)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )

    def copy_registration_fixture(self, destination: Path) -> None:
        overlay = Path("components/apollo_main/core_overlay/overlay.json")
        manifest = Path("manifests/g2-2.2.6.10-core-source.json")
        for relative in (overlay, manifest, Path("Makefile")):
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)

    @staticmethod
    def add_json_registration(path: Path, registration: str) -> None:
        value = json.loads(path.read_text(encoding="utf-8"))
        value["_cmbacktrace_registration_mutation"] = registration
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_offline_verifier_and_metadata_are_pinned(self) -> None:
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, "CmBacktrace compatibility snapshot verification passed\n")
        self.assertEqual(PROVENANCE.stat().st_size, EXPECTED_PROVENANCE_SIZE)
        self.assertEqual(digest(PROVENANCE.read_bytes()), EXPECTED_PROVENANCE_SHA256)
        self.assertEqual(VERIFIER.stat().st_size, EXPECTED_VERIFIER_SIZE)
        self.assertEqual(digest(VERIFIER.read_bytes()), EXPECTED_VERIFIER_SHA256)
        self.assertEqual(README.stat().st_size, EXPECTED_README_SIZE)
        self.assertEqual(digest(README.read_bytes()), EXPECTED_README_SHA256)

    def test_selected_commit_is_a_qualified_compatibility_choice(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(value["schema_version"], 2)
        upstream = value["upstream"]
        selection = value["selection"]
        self.assertEqual(
            upstream["selected_commit"],
            "73714489f9d8af130aacb515586b397b604a5768",
        )
        self.assertEqual(
            upstream["selected_tree"],
            "541c20dbeb1165f9b2862e2b84cdc63b3d7c718f",
        )
        self.assertEqual(upstream["declared_library_version"], "1.4.2")
        self.assertIsNone(upstream["official_version_tag"])
        self.assertFalse(selection["exact_g2_checkout_proven"])
        self.assertEqual(
            selection["compatible_floor_commit"],
            "4abadfa0c4f86f22352aa5ab9ebbb4f687125a1c",
        )
        self.assertEqual(selection["compatible_ceiling_commit"], upstream["selected_commit"])
        self.assertEqual(len(value["files"]), 7)
        self.assertEqual(canonical_digest(value["files"]), EXPECTED_RECORDS_SHA256)

    def test_bounded_production_source_and_local_g2_adapter_are_separated(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        integration = value["production_integration"]
        baseline = integration["upstream_compatibility_baseline"]
        self.assertEqual(
            baseline,
            {
                "commit": "73714489f9d8af130aacb515586b397b604a5768",
                "source_path": "cm_backtrace/cm_backtrace.c",
                "function": "get_cur_thread_name",
                "selected_platform": "CMB_OS_PLATFORM_FREERTOS",
                "selected_branch": "return vTaskName();",
                "qualification": (
                    "This upstream branch authenticates returning the current-task-name "
                    "adapter result only; it does not define the G2 fixed address, TCB "
                    "layout, or null-TCB behavior."
                ),
            },
        )

        stock = integration["stock_g2_boundary"]
        self.assertEqual(stock["get_cur_thread_name_span"], "[0x00593AF6,0x00593AFE)")
        self.assertEqual(stock["get_cur_thread_name_hex"], "80b5c2f699fa02bd")
        self.assertEqual(stock["vtask_name_adapter_span"], "[0x0045602E,0x00456036)")
        self.assertEqual(stock["vtask_name_adapter_hex"], "0b48006834307047")
        self.assertEqual(stock["current_tcb_word_address"], "0x20074A20")
        self.assertEqual(stock["task_name_offset"], "0x34")
        self.assertEqual(stock["null_current_tcb_result"], "0x34")
        self.assertIn("not upstream CmBacktrace", stock["classification"])

        records = integration["production_files"]
        self.assertEqual(canonical_digest(records), EXPECTED_PRODUCTION_RECORDS_SHA256)
        self.assertEqual(len(records), 5)
        self.assertFalse(any("_candidate" in record["local_path"] for record in records))
        for record in records:
            with self.subTest(path=record["local_path"]):
                path = ROOT / record["local_path"]
                self.assertEqual(path.stat().st_size, record["size"])
                self.assertEqual(digest(path.read_bytes()), record["sha256"])

        candidates = integration["candidate_separation"]["candidate_paths"]
        self.assertEqual(len(candidates), 2)
        self.assertTrue(all("_candidate" in path for path in candidates))
        self.assertTrue(all((ROOT / path).is_file() for path in candidates))
        readme = README.read_text(encoding="utf-8")
        self.assertIn("snapshot directory itself remains excluded", readme)
        self.assertIn("not upstream CmBacktrace source", readme)

    def test_configuration_separates_proof_choices_and_unknowns(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        boundary = value["g2_boundary"]
        proven = boundary["proven_effective_configuration"]
        self.assertTrue(proven["CMB_USING_OS_PLATFORM"])
        self.assertEqual(proven["CMB_OS_PLATFORM_TYPE"], "CMB_OS_PLATFORM_FREERTOS")
        self.assertTrue(proven["CMB_USING_DUMP_STACK_INFO"])
        self.assertEqual(proven["CMB_NAME_MAX"], 40)
        self.assertEqual(proven["CMB_CALL_STACK_MAX_DEPTH"], 32)
        self.assertEqual(proven["CMB_DUMP_STACK_DEPTH_SIZE"], 16)
        self.assertEqual(proven["compiler_branch"], "IAR / __ICCARM__")
        self.assertEqual(
            boundary["explicit_compatibility_choices"],
            {
                "CMB_CPU_PLATFORM_TYPE": "CMB_CPU_ARM_CORTEX_M33",
                "CMB_PRINT_LANGUAGE": "CMB_PRINT_LANGUAGE_ENGLISH",
            },
        )
        self.assertIn("source-level cmb_println integration beyond its recovered dual-logging behavior", boundary["unresolved"])
        self.assertEqual(
            value["selection"]["integration_status"],
            "snapshot remains unregistered; selected commit authenticates the bounded production get_cur_thread_name source adaptation",
        )
        manifests = b"\n".join(path.read_bytes() for path in sorted((ROOT / "manifests").glob("*.json")))
        self.assertNotIn(b"third_party/cmbacktrace", manifests)

    def test_source_config_commit_and_tree_mutations_fail_closed(self) -> None:
        mutations = (
            ("cm_backtrace/cm_backtrace.c", b"\n/* drift */\n", "size changed: cm_backtrace/cm_backtrace.c"),
            ("LICENSE", b"\n", "size changed: LICENSE"),
            ("g2-config/cmb_user_cfg.h", b"\n", "G2 config size changed"),
            ("upstream/commit.json", b" ", "commit record size changed"),
            ("upstream/trees.json", b" ", "tree closure size changed"),
        )
        for relative, suffix, expected in mutations:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                copied = Path(tmp) / "openCFW" / "third_party" / "cmbacktrace"
                copied.parent.mkdir(parents=True)
                shutil.copytree(SNAPSHOT, copied)
                target = copied / relative
                target.write_bytes(target.read_bytes() + suffix)
                result = self.run_verifier(copied / "verify_snapshot.py")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(expected, result.stdout)

    def test_bounded_production_source_mutation_fails_closed(self) -> None:
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            copied_root = Path(tmp) / "openCFW"
            copied = copied_root / "third_party" / "cmbacktrace"
            copied.parent.mkdir(parents=True)
            shutil.copytree(SNAPSHOT, copied)
            for record in provenance["production_integration"]["production_files"]:
                source = ROOT / record["local_path"]
                target = copied_root / record["local_path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            for candidate in provenance["production_integration"]["candidate_separation"]["candidate_paths"]:
                source = ROOT / candidate
                target = copied_root / candidate
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

            production_source = copied_root / provenance["production_integration"]["production_files"][0]["local_path"]
            production_source.write_bytes(production_source.read_bytes() + b"\n")
            result = self.run_verifier(copied / "verify_snapshot.py")
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn(
                "size changed: components/shared/cmbacktrace/runtime_cmbacktrace_get_cur_thread_name.c",
                result.stdout,
            )

    def test_production_configuration_registration_mutations_fail_closed(self) -> None:
        verifier = load_verifier()
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        overlay = Path("components/apollo_main/core_overlay/overlay.json")
        manifest = Path("manifests/g2-2.2.6.10-core-source.json")
        mutations = (
            (
                overlay,
                "third_party/cmbacktrace/cm_backtrace/cm_backtrace.c",
                "direct CmBacktrace snapshot registration in components/apollo_main/core_overlay/overlay.json",
            ),
            (
                manifest,
                "third_party/cmbacktrace/cm_backtrace/cm_backtrace.h",
                "direct CmBacktrace snapshot registration in manifests/g2-2.2.6.10-core-source.json",
            ),
            (
                overlay,
                "third_party/./cmbacktrace/cm_backtrace/cm_backtrace.c",
                "direct CmBacktrace snapshot registration in components/apollo_main/core_overlay/overlay.json",
            ),
            (
                Path("Makefile"),
                "CMB_SOURCES += $(CMBACKTRACE_DIR)/cm_backtrace/cm_backtrace.c",
                "direct CmBacktrace snapshot registration in Makefile",
            ),
            (
                Path("Makefile"),
                "CMB_SOURCE := third_party//cmbacktrace/cm_backtrace/cm_backtrace.c",
                "direct CmBacktrace snapshot registration in Makefile",
            ),
            (
                overlay,
                "components/shared/cmbacktrace/runtime_cmbacktrace_get_cur_thread_name_candidate.c",
                "CmBacktrace candidate registration in components/apollo_main/core_overlay/overlay.json",
            ),
            (
                manifest,
                "open_cfw_cmbacktrace_get_cur_thread_name_candidate",
                "CmBacktrace candidate registration in manifests/g2-2.2.6.10-core-source.json",
            ),
            (
                Path("Makefile"),
                "CMB_FUNCTION := open_cfw_cmbacktrace_pc_task_get_name_current_candidate",
                "CmBacktrace candidate registration in Makefile",
            ),
            (
                Path("Makefile"),
                "CMB_SOURCE := components/shared/cmbacktrace/unapproved.c",
                "unapproved CmBacktrace production source path in Makefile",
            ),
            (
                Path("Makefile"),
                "CMB_SOURCE := components//shared/cmbacktrace/unapproved.c",
                "unapproved CmBacktrace production source path in Makefile",
            ),
            (
                Path("Makefile"),
                "CMB_FUNCTION := open_cfw_cmbacktrace_unapproved",
                "unapproved CmBacktrace production symbol in Makefile",
            ),
        )
        for relative, registration, expected in mutations:
            with self.subTest(relative=relative, registration=registration), tempfile.TemporaryDirectory() as tmp:
                copied_root = Path(tmp) / "openCFW"
                self.copy_registration_fixture(copied_root)
                target = copied_root / relative
                if target.suffix == ".json":
                    self.add_json_registration(target, registration)
                else:
                    target.write_text(
                        target.read_text(encoding="utf-8") + f"\n{registration}\n",
                        encoding="utf-8",
                    )
                with self.assertRaises(SystemExit) as raised:
                    verifier.verify_registration_exclusion(provenance, copied_root)
                self.assertIn(expected, str(raised.exception))

    def test_registration_scan_excludes_generated_build_directories(self) -> None:
        verifier = load_verifier()
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            copied_root = Path(tmp) / "openCFW"
            self.copy_registration_fixture(copied_root)
            for generated_name in ("build", "build-linux"):
                generated_overlay = (
                    copied_root / "components" / "probe" / generated_name / "overlay.json"
                )
                generated_manifest = (
                    copied_root / "manifests" / generated_name / "probe.json"
                )
                generated_overlay.parent.mkdir(parents=True)
                generated_manifest.parent.mkdir(parents=True)
                generated_overlay.write_text("not source-controlled JSON", encoding="utf-8")
                generated_manifest.write_text("not source-controlled JSON", encoding="utf-8")
            verifier.verify_registration_exclusion(provenance, copied_root)

    def test_reconstructed_tree_rejects_semantic_membership_tampering(self) -> None:
        verifier = load_verifier()
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        tree_path = SNAPSHOT / provenance["upstream"]["tree_closure_path"]
        closure = json.loads(tree_path.read_text(encoding="utf-8"))

        tampered_closure = json.loads(json.dumps(closure))
        entry = tampered_closure["trees"][0]["entries"][0]
        entry["oid"] = "0" + entry["oid"][1:]
        with self.assertRaises(SystemExit) as raised:
            verifier.verify_tree_closure(provenance, tampered_closure)
        self.assertIn("tree object ID mismatch", str(raised.exception))

        tampered_provenance = json.loads(json.dumps(provenance))
        selected = tampered_provenance["files"][0]
        selected["git_blob_sha1"] = "0" + selected["git_blob_sha1"][1:]
        with self.assertRaises(SystemExit) as raised:
            verifier.verify_tree_closure(tampered_provenance, closure)
        self.assertIn("tree blob mismatch: LICENSE", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
