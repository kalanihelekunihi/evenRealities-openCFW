#!/usr/bin/env python3
"""Focused fail-closed gates for the Packetcraft Cordio source snapshot."""

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
SNAPSHOT = ROOT / "third_party" / "cordio"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
EXPECTED_PROVENANCE_SIZE = 20246
EXPECTED_PROVENANCE_SHA256 = "1fffca2937f4ec8f0937f947e0d6e0c14110ea36c561826be21b67d0c7bab07a"
EXPECTED_VERIFIER_SIZE = 46063
EXPECTED_VERIFIER_SHA256 = "c70e844f4f02b7e0fb32928e1ffc2a804266cabe820dc15d71122333ac67f9db"
EXPECTED_RECORDS_SHA256 = "2d9ba02bd31e3784789af3ddb3f2bbcaa9e7187f12eb76506b4b2d14a2d55d9a"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return digest(encoded)


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_cordio_snapshot", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioSnapshotTests(unittest.TestCase):
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

    def test_offline_verifier_and_metadata_are_pinned(self) -> None:
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            result.stdout,
            "Packetcraft Cordio r20.05c source-oracle snapshot verification passed\n",
        )
        self.assertEqual(PROVENANCE.stat().st_size, EXPECTED_PROVENANCE_SIZE)
        self.assertEqual(digest(PROVENANCE.read_bytes()), EXPECTED_PROVENANCE_SHA256)
        self.assertEqual(VERIFIER.stat().st_size, EXPECTED_VERIFIER_SIZE)
        self.assertEqual(digest(VERIFIER.read_bytes()), EXPECTED_VERIFIER_SHA256)

    def test_release_choice_closure_and_bounded_claim_are_exact(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        upstream = value["upstream"]
        self.assertEqual(upstream["selected_release"], "r20.05c")
        self.assertEqual(
            upstream["selected_commit"],
            "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
        )
        self.assertEqual(
            upstream["selected_tree"],
            "0a76c7dde46d3b94bb9185a4a5327d0e3f38ec97",
        )
        self.assertIsNone(upstream["tag_object"])
        self.assertFalse(value["selection"]["exact_g2_checkout_proven"])
        self.assertEqual(value["selection"]["selected_file_count"], 41)
        self.assertEqual(value["selection"]["selected_c_source_count"], 5)
        self.assertEqual(value["selection"]["selected_header_count"], 35)
        self.assertEqual(upstream["tree_object_count"], 21)
        records = value["files"]
        self.assertEqual(canonical_digest(records), EXPECTED_RECORDS_SHA256)
        releases = value["g2_boundary"]["bounded_equivalence_interval"]["releases"]
        self.assertEqual(list(releases), ["r20.05", "r20.05a", "r20.05b", "r20.05c"])
        self.assertEqual(
            value["g2_boundary"]["bounded_equivalence_interval"]["not_an_upper_bound_for"],
            "the complete G2 Cordio vendor tree",
        )

    def test_configuration_and_port_exclusions_are_fail_closed(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        config = value["g2_boundary"]["proven_configuration"]
        self.assertEqual(config["DM_CONN_MAX"], 3)
        self.assertEqual(config["ATT_client_record_stride"], 2)
        self.assertTrue(config["WSF_BUF_FREE_CHECK_ASSERT"])
        self.assertFalse(config["WSF_BUF_STATS"])
        self.assertFalse(config["WSF_BUF_STATS_HIST"])
        self.assertFalse(config["WSF_OS_DIAG"])
        self.assertEqual(config["WSF_buffer_pool_descriptor_bytes"], 12)
        port = value["g2_boundary"]["port_boundary"]
        self.assertEqual(port["g2_source_path"], "wsf/sources/port/freertos/wsf_buf.c")
        self.assertIn("comparator only", port["qualification"])
        self.assertEqual(port["ambiq_hci_port"], "excluded and unresolved")
        self.assertEqual(port["even_mram_platform_glue"], "excluded and unresolved")
        self.assertIn("APP_DB_NUM_RECS=3", value["g2_boundary"]["config_qualification"])

    def test_source_config_commit_and_tree_mutations_fail_closed(self) -> None:
        mutations = (
            ("ble-host/sources/stack/att/atts_csf.c", b"\n/* drift */\n", "size changed"),
            ("g2-config/cordio_recovered_config.h", b"\n#define DM_CONN_MAX 4\n", "G2 config size changed"),
            (
                "upstream/3656312d6b73e2a2c1c8b33ee0385bc199dd97e6.commit",
                b"drift",
                "commit payload size changed",
            ),
            ("upstream/trees.json", b" ", "tree closure size changed"),
        )
        for relative, suffix, expected in mutations:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                copied = Path(tmp) / "openCFW" / "third_party" / "cordio"
                copied.parent.mkdir(parents=True)
                shutil.copytree(SNAPSHOT, copied)
                target = copied / relative
                target.write_bytes(target.read_bytes() + suffix)
                result = self.run_verifier(copied / "verify_snapshot.py")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(expected, result.stdout)

    def test_reconstructed_tree_rejects_semantic_membership_tampering(self) -> None:
        verifier = load_verifier()
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        closure = json.loads((SNAPSHOT / "upstream" / "trees.json").read_text(encoding="utf-8"))
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
        self.assertIn("tree blob mismatch: LICENSE.md", str(raised.exception))

    def test_five_reference_translation_units_compile_and_close(self) -> None:
        compiler = shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")
        if compiler is None:
            self.skipTest("no native C compiler is available")
        include_dirs = [
            SNAPSHOT / "wsf/include",
            SNAPSHOT / "ble-host/include",
            SNAPSHOT / "ble-host/sources/stack/att",
            SNAPSHOT / "ble-host/sources/stack/cfg",
            SNAPSHOT / "ble-host/sources/stack/dm",
            SNAPSHOT / "ble-host/sources/stack/hci",
            SNAPSHOT / "ble-host/sources/stack/l2c",
            SNAPSHOT / "ble-host/sources/stack/smp",
            SNAPSHOT / "ble-profiles/include",
            SNAPSHOT / "ble-profiles/sources/af",
            SNAPSHOT / "ble-profiles/sources/services",
        ]
        common = [
            compiler,
            "-std=c99",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Wno-unused-parameter",
            "-DWSF_TRACE_ENABLED=1",
            "-include",
            str(SNAPSHOT / "g2-config/cordio_recovered_config.h"),
            *[f"-I{path}" for path in include_dirs],
        ]
        verifier = load_verifier()
        discovered: set[str] = set()
        with tempfile.TemporaryDirectory() as tmp:
            for index, relative in enumerate(verifier.ROOT_SOURCE_PATHS):
                source = SNAPSHOT / relative
                output = Path(tmp) / f"reference-{index}.o"
                with self.subTest(source=relative):
                    compiled = subprocess.run(
                        [*common, "-c", str(source), "-o", str(output)],
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    self.assertEqual(compiled.returncode, 0, compiled.stdout)
                    self.assertGreater(output.stat().st_size, 0)
                    dependencies = subprocess.run(
                        [*common, "-MM", str(source)],
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    self.assertEqual(dependencies.returncode, 0, dependencies.stdout)
                    flattened = dependencies.stdout.replace("\\\n", " ")
                    for token in flattened.split()[1:]:
                        candidate = Path(token)
                        try:
                            discovered.add(candidate.resolve().relative_to(SNAPSHOT.resolve()).as_posix())
                        except ValueError:
                            pass
        self.assertEqual(
            discovered,
            (set(verifier.EXPECTED_SOURCE_PATHS) - {"LICENSE.md"})
            | {"g2-config/cordio_recovered_config.h"},
        )

    def test_verifier_registration_is_allowed_but_production_references_fail_closed(self) -> None:
        verifier = load_verifier()
        registrations = {
            "manifests/production.json": (
                '{"source":"third_party/cordio/ble-host/sources/stack/att/atts_csf.c"}\n'
            ),
            "components/apollo_main/core_overlay/overlay.json": (
                '{"sources":[{"path":"third_party/cordio/ble-host/sources/stack/dm/dm_conn_sm.c"}]}\n'
            ),
            "components/apollo_main/core_overlay/build_component.py": (
                'CORDIO_SOURCE = "third_party/cordio/wsf/sources/targets/baremetal/wsf_buf.c"\n'
            ),
            "components/apollo_main/core_overlay/cordio_glue.c": (
                '#include "third_party/cordio/ble-host/include/att_api.h"\n'
            ),
            "tools/open_cfw.py": (
                'CORDIO_SOURCE = "third_party/cordio/ble-profiles/sources/af/common/app_db.c"\n'
            ),
        }
        old_root = verifier.ROOT
        try:
            for relative, content in registrations.items():
                with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "openCFW"
                    root.mkdir()
                    (root / "Makefile").write_text(
                        "CORDIO_DIR := third_party/cordio\n"
                        "cordio-snapshot:\n"
                        "\t$(PYTHON) $(CORDIO_DIR)/verify_snapshot.py\n",
                        encoding="utf-8",
                    )
                    verifier.ROOT = root
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
                    "CORDIO_DIR := third_party/cordio\n"
                    "cordio-snapshot:\n"
                    "\t$(PYTHON) $(CORDIO_DIR)/verify_snapshot.py\n"
                    "core-component:\n"
                    "\t$(CC) -c $(CORDIO_DIR)/ble-host/sources/stack/att/atts_csf.c\n",
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


if __name__ == "__main__":
    unittest.main()
