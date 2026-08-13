#!/usr/bin/env python3
"""Focused fail-closed gates for the FlashDB 2.1.1 source snapshot."""

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
SNAPSHOT = ROOT / "third_party" / "flashdb"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
EXPECTED_PROVENANCE_SIZE = 10528
EXPECTED_PROVENANCE_SHA256 = "c0bef8f3b70e6eea14a9c6d0b785c70905ad452f12ba95798fb8425b5dfbe356"
EXPECTED_VERIFIER_SIZE = 16942
EXPECTED_VERIFIER_SHA256 = "53ad7a945b40be83eb04463f397658cff9400a67e4946bbda6bd22f1e3685241"
EXPECTED_RECORDS_SHA256 = "4685bc7cd1b6ac2078d7c9308a84419dfcdab8c018efe7deb30e9fc75a3a5076"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return digest(encoded)


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_flashdb_snapshot", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FlashDbSnapshotTests(unittest.TestCase):
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
        self.assertEqual(result.stdout, "FlashDB 2.1.1 snapshot verification passed\n")
        self.assertEqual(PROVENANCE.stat().st_size, EXPECTED_PROVENANCE_SIZE)
        self.assertEqual(digest(PROVENANCE.read_bytes()), EXPECTED_PROVENANCE_SHA256)
        self.assertEqual(VERIFIER.stat().st_size, EXPECTED_VERIFIER_SIZE)
        self.assertEqual(digest(VERIFIER.read_bytes()), EXPECTED_VERIFIER_SHA256)

    def test_release_chain_and_selected_closure_are_exact(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(value["upstream"]["tag_type"], "lightweight")
        self.assertEqual(
            value["upstream"]["selected_commit"],
            "714d6159e7e6afb267a3953756abca445c350e61",
        )
        self.assertEqual(
            value["upstream"]["selected_tree"],
            "3410ae8111e4dbf6ae22d995bfcf37274abf89ea",
        )
        self.assertEqual(value["upstream"]["tree_object_count"], 7)
        self.assertEqual(value["upstream"]["tree_closure_path"], "upstream/trees.json")
        records = value["files"]
        self.assertEqual(len(records), 14)
        self.assertEqual(canonical_digest(records), EXPECTED_RECORDS_SHA256)
        self.assertEqual(
            [item["local_path"] for item in records],
            [
                "LICENSE",
                "inc/fdb_cfg.h",
                "inc/fdb_def.h",
                "inc/fdb_low_lvl.h",
                "inc/flashdb.h",
                "src/fdb.c",
                "src/fdb_kvdb.c",
                "src/fdb_utils.c",
                "port/fal/LICENSE",
                "port/fal/inc/fal.h",
                "port/fal/inc/fal_def.h",
                "port/fal/src/fal.c",
                "port/fal/src/fal_flash.c",
                "port/fal/src/fal_partition.c",
            ],
        )

    def test_g2_configuration_is_recovered_but_production_excluded(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        cfg = value["g2_boundary"]["configuration"]
        self.assertEqual(cfg["FDB_WRITE_GRAN"], 1)
        self.assertEqual(cfg["sec_size"], 0x1000)
        self.assertEqual(cfg["FDB_KV_CACHE_TABLE_SIZE"], 64)
        self.assertEqual(cfg["FDB_SECTOR_CACHE_TABLE_SIZE"], 64)
        self.assertTrue(cfg["compiler_short_enums"])
        self.assertFalse(cfg["FDB_KV_AUTO_UPDATE"])
        self.assertNotIn("FDB_USING_TSDB", cfg)
        self.assertEqual(
            value["g2_boundary"]["feature_evidence"],
            {
                "retained_tsdb_subsystem": False,
                "original_FDB_USING_TSDB_macro_state": "not statically proven",
                "minimal_recovered_config_uses_tsdb": False,
            },
        )
        self.assertEqual(
            value["selection"]["integration_status"],
            "authenticated and verified offline; no production registration",
        )

    def test_source_config_commit_and_tree_mutations_fail_closed(self) -> None:
        mutations = (
            ("src/fdb.c", b"\n/* drift */\n", "size changed: src/fdb.c"),
            ("g2-config/fdb_cfg.h", b"\n#define FDB_USING_TSDB\n", "G2 config size changed"),
            (
                "upstream/714d6159e7e6afb267a3953756abca445c350e61.commit",
                b"drift",
                "commit payload size changed",
            ),
            ("upstream/trees.json", b" ", "tree closure size changed"),
        )
        for relative, suffix, expected in mutations:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                copied = Path(tmp) / "openCFW" / "third_party" / "flashdb"
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
        tree_path = SNAPSHOT / provenance["upstream"]["tree_closure_path"]
        closure = json.loads(tree_path.read_text(encoding="utf-8"))
        tampered_closure = json.loads(json.dumps(closure))
        entry = tampered_closure["trees"][0]["entries"][2]
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
