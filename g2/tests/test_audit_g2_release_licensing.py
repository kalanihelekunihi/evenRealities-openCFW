# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import hashlib
import importlib.util
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/audit_g2_release_licensing.py"


def load_tool():
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("audit_g2_release_licensing", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class G2ReleaseLicensingAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()
        cls.report = cls.tool.analyze()

    def test_every_core_source_package_artifact_has_an_authority_record(self) -> None:
        self.assertEqual(self.report["notice"], "NOTICE-CORE-SOURCE.md")
        notice = (ROOT / self.report["notice"]).read_text()
        self.assertIn("does not license or assert redistribution authority", notice)
        self.assertIn("research-only InvenSense ICM45608 snapshot", notice)
        self.assertNotIn("ISC", self.tool.LICENSE_TEXTS)
        invensense_root_notice = (
            ROOT / "third_party/invensense-icm45608/LICENSE"
        )
        self.assertTrue(invensense_root_notice.is_file())
        self.assertTrue(
            invensense_root_notice.read_text().startswith("BSD 3-Clause License")
        )
        rows = {row["component"]: row for row in self.report["artifacts"]}
        self.assertEqual(
            set(rows),
            {"codec", "ble_em9305", "touch", "case", "apollo_bootloader", "apollo_main"},
        )
        self.assertEqual(
            {row["redistribution_authority"] for row in rows.values()},
            {"unresolved"},
        )
        self.assertEqual(self.report["binary_authority_errors"], [])
        self.assertTrue(all(row["authority_evidence"] is None for row in rows.values()))
        self.assertEqual(rows["apollo_main"]["provider_kind"], "source_build")
        self.assertEqual(
            rows["apollo_main"]["source_availability"],
            "overlay-source-plus-retained-binary",
        )
        self.assertEqual(
            rows["codec"]["source_availability"],
            "binary-only-in-core-source-package",
        )
        self.assertEqual(rows["codec"]["provider_size"], 326_092)
        self.assertEqual(
            rows["codec"]["provider_sha256"],
            "b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0",
        )

    def test_live_overlay_source_inventory_is_content_and_license_checked(self) -> None:
        rows = self.report["source_inventory"]
        self.assertGreaterEqual(len(rows), 732)
        self.assertEqual(len(rows), self.report["summary"]["source_files"])
        self.assertTrue(all(row["sha256"] for row in rows))
        self.assertEqual(
            {row["classification"] for row in rows},
            {"upstream-licensed", "project-owned-or-adapted"},
        )
        errors = self.report["source_errors"]
        self.assertEqual(errors, [])
        cordio = next(
            row for row in rows
            if row["path"] == "components/shared/cordio/runtime_cordio_hci_tr.c"
        )
        self.assertEqual(cordio["license"], "MIT")
        paths = {row["path"] for row in rows}
        self.assertTrue(
            {
                "components/bootloader/core_overlay/runtime_littlefs_erase_421348.c",
                "components/bootloader/core_overlay/runtime_littlefs_program_421310.c",
                "components/bootloader/core_overlay/runtime_littlefs_sync_4213d4.c",
                "components/bootloader/core_overlay/runtime_memory_select_copy_4213e6.c",
            }
            <= paths
        )
        inventory = (
            ROOT / "docs/release-licensing-and-redistribution.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Older per-closure provenance manifests", inventory)
        self.assertIn("it is not a source-complete,", inventory)
        self.assertIn("redistribution-authorized claim", inventory)
        self.assertIn(
            f"inventory reference {len(rows)} unique, content-addressed",
            inventory.replace("\n", " "),
        )
        lc3_setup = next(
            row for row in rows
            if row["path"] ==
            "components/apollo_main/core_overlay/pt_protocol_lc3_setup.c"
        )
        self.assertEqual(lc3_setup["license"], "Apache-2.0")
        self.assertEqual(lc3_setup["classification"], "upstream-licensed")
        self.assertEqual(lc3_setup["upstream"], "Google/liblc3")
        self.assertEqual(
            lc3_setup["upstream_commit"],
            "96a3af0beb5487aca3b98a4b992a539a1f6d80d1",
        )
        self.assertEqual(
            lc3_setup["license_evidence"], "g2/third_party/liblc3/LICENSE"
        )
        self.assertEqual(lc3_setup["errors"], [])
        project_mit = next(
            row for row in rows
            if row["path"] == "components/shared/cordio/runtime_cordio_hci_tr.c"
        )
        self.assertEqual(project_mit["license_evidence"], "LICENSE")
        for license_id, count in Counter(row["license"] for row in rows).items():
            self.assertIn(f"| {license_id} | {count} |", inventory)

    def test_release_gate_is_fail_closed(self) -> None:
        with self.assertRaisesRegex(
            self.tool.ReleaseAuthorityError,
            "codec, ble_em9305, touch, case, apollo_bootloader, apollo_main",
        ):
            self.tool.assert_release_authorized()
        result = subprocess.run(
            [sys.executable, str(TOOL), "--release-gate"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("external release authorized: False", result.stdout)

    def test_string_only_authority_status_edits_cannot_open_gate(self) -> None:
        records = copy.deepcopy(self.tool.BINARY_AUTHORITY)
        for record in records.values():
            record["status"] = "authorized"
        report = self.tool.analyze(authority_records=records)
        self.assertFalse(report["summary"]["release_authorized"])
        self.assertEqual(
            report["summary"]["redistribution_authority_unresolved"],
            [
                "codec",
                "ble_em9305",
                "touch",
                "case",
                "apollo_bootloader",
                "apollo_main",
            ],
        )
        self.assertEqual(report["summary"]["binary_authority_errors"], 6)
        self.assertTrue(
            all("structured evidence" in error for error in report["binary_authority_errors"])
        )

    def test_structured_authority_record_authenticates_both_evidence_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-authority-") as temporary:
            root = Path(temporary)
            grant = root / "docs/release-authority/codec/license.txt"
            compliance = root / "docs/release-authority/codec/compliance.txt"
            grant.parent.mkdir(parents=True)
            grant.write_text("redistribution grant", encoding="utf-8")
            compliance.write_text("reviewed redistribution obligations", encoding="utf-8")
            record = {
                "status": "authorized",
                "reason": "authenticated test grant",
                "evidence": {
                    "grant_path": "docs/release-authority/codec/license.txt",
                    "grant_sha256": hashlib.sha256(grant.read_bytes()).hexdigest(),
                    "terms": "binary redistribution for the named payload",
                    "reference": "test-license-reference-1",
                    "compliance_path": "docs/release-authority/codec/compliance.txt",
                    "compliance_sha256": hashlib.sha256(
                        compliance.read_bytes()
                    ).hexdigest(),
                },
            }
            result = self.tool.validate_binary_authority_record(
                "codec", record, root=root
            )
            self.assertEqual(result["status"], "authorized")
            self.assertEqual(result["errors"], [])
            record["evidence"]["grant_sha256"] = "0" * 64
            changed = self.tool.validate_binary_authority_record(
                "codec", record, root=root
            )
            self.assertEqual(changed["status"], "unresolved")
            self.assertIn("grant/license artifact SHA-256 mismatch", changed["errors"][0])

    def test_authority_grant_and_compliance_must_be_distinct_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-authority-distinct-") as temporary:
            root = Path(temporary)
            evidence = root / "docs/release-authority/codec/evidence.txt"
            evidence.parent.mkdir(parents=True)
            evidence.write_bytes(b"grant and self-attested compliance\n")
            digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
            record = {
                "status": "authorized",
                "reason": "invalid self-attested authority",
                "evidence": {
                    "grant_path": "docs/release-authority/codec/evidence.txt",
                    "grant_sha256": digest,
                    "terms": "binary redistribution for the named payload",
                    "reference": "test-license-reference-distinct-1",
                    "compliance_path": (
                        "docs/release-authority/codec/evidence.txt"
                    ),
                    "compliance_sha256": digest,
                },
            }
            result = self.tool.validate_binary_authority_record(
                "codec", record, root=root
            )
            self.assertEqual(result["status"], "unresolved")
            self.assertTrue(
                any("must be distinct" in error for error in result["errors"])
            )

    def test_duplicate_source_identity_and_project_license_fail_closed(self) -> None:
        records, conflicts = self.tool._source_records({
            "sources": [
                {
                    "path": "components/example.c",
                    "size": 1,
                    "sha256": "1" * 64,
                    "license": "MIT",
                    "origin": "OpenCFW clean-room source",
                },
                {
                    "path": "components/example.c",
                    "size": 2,
                    "sha256": "2" * 64,
                    "license": "GPL-3.0-only",
                    "origin": "OpenCFW clean-room source",
                },
            ]
        })
        self.assertEqual(set(records), {"components/example.c"})
        self.assertEqual(
            conflicts,
            [
                "duplicate source metadata conflict: components/example.c: sha256",
                "duplicate source metadata conflict: components/example.c: size",
                "duplicate source metadata conflict: components/example.c: license",
            ],
        )
        self.assertEqual(
            self.tool._classify_source(records["components/example.c"]),
            "project-owned-or-adapted",
        )
        self.assertEqual(
            self.tool._project_mit_policy_error(
                "components/example.c",
                records["components/example.c"]["license"],
                {"components/example.c"},
            ),
            "project-owned source must use MIT",
        )
        self.assertEqual(
            self.tool._license_text_payload_error("MIT", b"alternate terms\n"),
            "license text identity changed: MIT",
        )
        self.assertIsNone(
            self.tool._license_text_payload_error(
                "MIT", (ROOT.parent / "LICENSE").read_bytes()
            )
        )

    def test_licensing_json_rejects_linked_inputs(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="licensing-json-safe-", dir=ROOT / "tests"
        ) as temporary:
            directory = Path(temporary)
            actual = directory / "actual.json"
            actual.write_text('{"schema_version": 1}\n', encoding="utf-8")
            linked = directory / "linked.json"
            linked.symlink_to(actual)
            with self.assertRaisesRegex(
                self.tool.ReleaseAuthorityError, "opened safely"
            ):
                self.tool._safe_json(linked, label="linked licensing input")

    def test_authority_evidence_rejects_links_and_descriptor_drift(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-authority-safe-") as temporary:
            root = Path(temporary)
            authority = root / "docs/release-authority/codec"
            authority.mkdir(parents=True)
            grant = authority / "license.txt"
            compliance = authority / "compliance.txt"
            grant.write_bytes(b"grant\n")
            compliance.write_bytes(b"compliance\n")

            def record() -> dict:
                return {
                    "status": "authorized",
                    "reason": "authenticated test grant",
                    "evidence": {
                        "grant_path": "docs/release-authority/codec/license.txt",
                        "grant_sha256": hashlib.sha256(grant.read_bytes()).hexdigest(),
                        "terms": "binary redistribution for the named payload",
                        "reference": "test-license-reference-safe-1",
                        "compliance_path": (
                            "docs/release-authority/codec/compliance.txt"
                        ),
                        "compliance_sha256": hashlib.sha256(
                            compliance.read_bytes()
                        ).hexdigest(),
                    },
                }

            hardlink = authority / "license-hardlink.txt"
            os.link(grant, hardlink)
            linked = self.tool.validate_binary_authority_record(
                "codec", record(), root=root
            )
            self.assertEqual(linked["status"], "unresolved")
            self.assertTrue(
                any("independent regular file" in error for error in linked["errors"])
            )
            hardlink.unlink()

            grant_payload = grant.read_bytes()
            grant.unlink()
            grant.symlink_to(compliance)
            symlinked = self.tool.validate_binary_authority_record(
                "codec", record(), root=root
            )
            self.assertEqual(symlinked["status"], "unresolved")
            self.assertTrue(
                any("opened safely" in error for error in symlinked["errors"])
            )
            grant.unlink()
            grant.write_bytes(grant_payload)

            real_authority = authority.with_name("codec-real")
            authority.rename(real_authority)
            authority.symlink_to(real_authority, target_is_directory=True)
            ancestor = self.tool.validate_binary_authority_record(
                "codec", {
                    **record(),
                    "evidence": {
                        **record()["evidence"],
                        "grant_sha256": hashlib.sha256(
                            (real_authority / "license.txt").read_bytes()
                        ).hexdigest(),
                        "compliance_sha256": hashlib.sha256(
                            (real_authority / "compliance.txt").read_bytes()
                        ).hexdigest(),
                    },
                }, root=root
            )
            self.assertEqual(ancestor["status"], "unresolved")
            self.assertTrue(
                any("opened safely" in error for error in ancestor["errors"])
            )
            authority.unlink()
            real_authority.rename(authority)

            real_fstat = os.fstat
            regular_calls = 0

            def drifting_fstat(descriptor: int):
                nonlocal regular_calls
                result = real_fstat(descriptor)
                if not stat.S_ISREG(result.st_mode):
                    return result
                regular_calls += 1
                if regular_calls != 2:
                    return result
                return SimpleNamespace(
                    st_dev=result.st_dev,
                    st_ino=result.st_ino,
                    st_mode=result.st_mode,
                    st_nlink=result.st_nlink,
                    st_size=result.st_size,
                    st_mtime_ns=result.st_mtime_ns,
                    st_ctime_ns=result.st_ctime_ns + 1,
                )

            with mock.patch.object(
                self.tool.os, "fstat", side_effect=drifting_fstat
            ):
                drifting = self.tool.validate_binary_authority_record(
                    "codec", record(), root=root
                )
            self.assertEqual(drifting["status"], "unresolved")
            self.assertTrue(
                any("changed during descriptor read" in error for error in drifting["errors"])
            )


if __name__ == "__main__":
    unittest.main()
