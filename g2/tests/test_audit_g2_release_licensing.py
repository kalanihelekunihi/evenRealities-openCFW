# SPDX-License-Identifier: MIT

from __future__ import annotations

import copy
import hashlib
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


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
        self.assertIn("ISC:", notice)
        self.assertTrue(
            self.tool.LICENSE_TEXTS["ISC"].is_file(),
            "the InvenSense file-specific ISC grant must ship with the bundle",
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
        self.assertIn(
            f"the two overlays reference {len(rows)} unique,",
            inventory,
        )
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


if __name__ == "__main__":
    unittest.main()
