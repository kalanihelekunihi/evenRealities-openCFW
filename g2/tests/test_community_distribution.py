# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import community_distribution as distribution  # noqa: E402
import open_cfw  # noqa: E402

REQUIRE_SOURCE_CAPTURE_UNCHANGED = (
    distribution._require_source_capture_unchanged
)


class CommunityDistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="opencfw-community-bundle-",
            dir=distribution._physical_temporary_root(),
        )
        root = Path(cls.temporary.name)
        cls.first = root / "first.zip"
        cls.second = root / "second.zip"
        cls.first_report = distribution.create_bundle(cls.first)
        cls.second_report = distribution.create_bundle(cls.second)
        cls.manifest = distribution.verify_bundle(cls.first)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_bundle_is_deterministic_and_contains_only_source_material(self) -> None:
        self.assertEqual(self.first.read_bytes(), self.second.read_bytes())
        self.assertEqual(stat.S_IMODE(self.first.stat().st_mode), 0o644)
        self.assertEqual(stat.S_IMODE(self.second.stat().st_mode), 0o644)
        self.assertEqual(self.first_report["sha256"], self.second_report["sha256"])
        self.assertFalse(self.manifest["contains_official_firmware_payloads"])
        self.assertFalse(self.manifest["contains_stock_firmware_guard_bytes"])
        self.assertEqual(self.manifest["schema_version"], 5)
        self.assertEqual(
            self.manifest["archive_encoding"], "zip-stored-fixed-metadata"
        )
        self.assertTrue(self.manifest["license_closure"]["normalization_complete"])
        self.assertEqual(self.manifest["license_closure"]["pending_project_files"], 0)
        self.assertEqual(
            self.manifest["license_closure"]["distributed_project_files"],
            self.manifest["license_closure"]["normalized_project_files"],
        )
        source_like = {
            row["path"]
            for row in self.manifest["files"]
            if distribution._source_like_archive_path(row["path"])
        }
        ledger = self.manifest["member_license_ledger"]
        self.assertEqual(
            {row["path"] for row in ledger},
            {row["path"] for row in self.manifest["files"]},
        )
        self.assertEqual(
            self.manifest["member_license_closure"]["total_members"],
            len(self.manifest["files"]),
        )
        self.assertEqual(
            self.manifest["member_license_closure"]["source_like_members"],
            len(source_like),
        )
        self.assertEqual(
            self.manifest["member_license_closure"]["unresolved_members"],
            0,
        )
        self.assertEqual(
            len(source_like),
            self.manifest["member_license_closure"]["explicit_spdx_members"]
            + self.manifest["member_license_closure"][
                "reviewed_upstream_scope_members"
            ],
        )
        self.assertTrue(
            all(
                set(row) == {
                    "path", "size", "sha256", "license", "member_class",
                    "basis", "evidence",
                }
                and row["evidence"]
                for row in ledger
            )
        )
        self.assertEqual(
            self.manifest["completion_assessment"]["included"], True,
        )
        self.assertEqual(
            self.manifest["completion_assessment"]["repository_gate"],
            "completion-assessment-check",
        )
        self.assertEqual(
            [
                row["path"]
                for row in self.manifest["completion_assessment"]["members"]
            ],
            list(distribution.COMPLETION_REPORT_MEMBERS),
        )
        self.assertEqual(
            self.first_report["source_capture_sha256"],
            self.second_report["source_capture_sha256"],
        )
        self.assertEqual(
            self.manifest["stock_guard_representation"],
            "size-and-sha256-authenticated-local-base",
        )
        self.assertGreater(len(self.manifest["files"]), 1_000)
        names = {row["path"] for row in self.manifest["files"]}
        self.assertIn("g2/components/apollo_main/core_overlay/overlay.json", names)
        self.assertIn("g2/components/bootloader/core_overlay/overlay.json", names)
        for relative in (
            "g2/components/apollo_main/liblc3_ltpf/build_component.py",
            "g2/components/apollo_main/core_overlay/LICENSE-mpaland-MIT",
            "g2/components/apollo_main/liblc3_ltpf/liblc3_ltpf_overlay.c",
            "g2/components/apollo_main/liblc3_ltpf/overlay.json",
            "g2/components/apollo_main/pt_protocol/build_component.py",
            "g2/tests/test_apollo_pt_protocol_provider.py",
            "g2/third_party/liblc3/include/lc3.h",
            "g2/third_party/ring-buffer/LICENSE",
            "g2/components/shared/touch/runtime_touch_application_core.c",
            "g2/components/shared/touch/runtime_touch_product_orchestration.c",
            "g2/components/shared/case/runtime_case_uart_update.c",
            "g2/components/shared/gx8002/runtime_gx8002_kws_model_boundary.c",
            "g2/components/shared/em9305/runtime_controller_pawr_boundary.c",
            "g2/components/shared/touch/runtime_touch_unsigned_division.c",
            "g2/components/touch/source_image/build_image.py",
            "g2/tools/analyze_g2_dual_profile_ownership.py",
            "g2/tools/manifests/g2-dual-profile-ownership.json",
            "g2/tests/test_analyze_g2_dual_profile_ownership.py",
            "g2/components/touch/source_image/firmware_image.c",
            "g2/components/touch/source_image/linker.ld",
            "g2/components/case/source_image/README.md",
            "g2/components/case/source_image/build_image.py",
            "g2/components/case/source_image/compiler_runtime.c",
            "g2/components/case/source_image/linker.ld",
            "g2/components/case/source_image/startup.c",
            "g2/components/em9305/source_image/README.md",
            "g2/components/em9305/source_image/build_image.py",
            "g2/components/em9305/source_image/record_package.py",
            "g2/tools/analyze_em9305_record_package.py",
            "g2/tools/manifests/em9305-record-package-summary.json",
            "g2/tests/test_analyze_em9305_record_package.py",
            "g2/tests/test_em9305_record_package.py",
            "g2/tools/analyze_g2_case_source_image.py",
            "g2/tools/manifests/g2-case-source-image-summary.json",
            "g2/tests/test_analyze_g2_case_source_image.py",
            "g2/tools/analyze_g2_touch_source_image.py",
            "g2/tools/manifests/g2-touch-source-image-summary.json",
            "g2/tests/test_touch_source_image.py",
            "g2/tests/test_runtime_touch_unsigned_division.py",
            "g2/tests/fixtures/touch_unsigned_division_host.c",
            "g2/tools/manifests/g2-touch-final-classification-summary.json",
            "g2/tools/manifests/g2-touch-final-source-candidate-provenance.tsv",
            "g2/tools/manifests/g2-case-final-classification-summary.json",
            "g2/tools/manifests/gx8002-source-readiness.tsv",
        ):
            self.assertIn(relative, names)
        proof = self.manifest["dual_profile_ownership_proof"]
        self.assertTrue(proof["checked_at_creation"])
        self.assertFalse(proof["private_observation_artifacts_included"])
        self.assertFalse(proof["independently_rerunnable_from_source_bundle"])
        self.assertEqual(
            [row["path"] for row in proof["members"]],
            list(distribution.DUAL_PROFILE_PROOF_MEMBERS),
        )
        pt_sources = {
            f"g2/components/apollo_main/core_overlay/pt_protocol{suffix}.{extension}"
            for suffix in (
                "_handlers_audio",
                "_handlers_basic",
                "_handlers_config",
                "_handlers_data",
                "_handlers_display",
                "_handlers_sensors",
                "_handlers_services",
                "_handlers_transfer",
                "_board_backend",
                "_board_leaf_candidates",
                "_platform_adapter",
                "_procsr",
                "_production_entry",
                "_service",
            )
            for extension in ("c", "h")
        } | {
            "g2/components/apollo_main/core_overlay/pt_protocol_lc3_setup.c"
        }
        self.assertEqual(len(pt_sources), 29)
        self.assertTrue(pt_sources <= names)
        self.assertEqual(
            {
                name
                for name in names
                if name.startswith(
                    "g2/components/apollo_main/core_overlay/pt_protocol"
                )
                and Path(name).suffix in {".c", ".h"}
            },
            pt_sources,
        )
        pt_runtime_tests = {
            f"g2/tests/test_runtime_pt_protocol_{area}.py"
            for area in (
                "audio_handlers",
                "basic_handlers",
                "board_backend",
                "board_leaf_candidates",
                "config_handlers",
                "core",
                "data_handlers",
                "display_handlers",
                "platform_adapter",
                "production_entry",
                "sensor_handlers",
                "service_handlers",
                "transfer_handlers",
            )
        }
        self.assertEqual(len(pt_runtime_tests), 13)
        self.assertTrue(pt_runtime_tests <= names)
        self.assertTrue(
            {
                "g2/tests/fixtures/pt_protocol_basic_handlers_host.c",
                "g2/tests/fixtures/pt_protocol_board_backend_host.c",
                "g2/tests/fixtures/pt_protocol_board_leaf_candidates_host.c",
                "g2/tests/fixtures/pt_protocol_core_host.c",
                "g2/tests/fixtures/pt_protocol_platform_adapter_host.c",
                "g2/tests/fixtures/pt_protocol_production_entry_host.c",
                "g2/tools/manifests/g2-pt-protocol-source-summary.json",
            }
            <= names
        )
        self.assertFalse(
            any("research" in Path(name).parts or "corpus" in Path(name).parts for name in names)
        )
        self.assertNotIn("g2/tools/analyze_g2_pt_protocol_source.py", names)
        self.assertNotIn("g2/tools/analyze_g2_clkmgr_divider_candidate.py", names)
        self.assertNotIn("g2/tools/extract_g2_pt_protocol_decomp.py", names)
        self.assertNotIn("g2/tests/test_analyze_g2_pt_protocol_source.py", names)
        self.assertNotIn("g2/tests/test_extract_g2_pt_protocol_decomp.py", names)
        self.assertEqual(
            {
                name for name in names
                if name.startswith(
                    "g2/docs/reports/openCFW-completion-2026-08-28/"
                )
            },
            set(distribution.COMPLETION_REPORT_MEMBERS),
        )
        self.assertTrue(
            {
                "g2/components/shared/case/runtime_case_semantic_leaves.c",
                "g2/components/shared/case/runtime_case_semantic_leaves.h",
                "g2/components/shared/case/runtime_case_pure_helpers.c",
                "g2/components/shared/case/runtime_case_pure_helpers.h",
                "g2/components/shared/case/runtime_case_register_policies.c",
                "g2/components/shared/case/runtime_case_register_policies.h",
                "g2/tests/test_runtime_case_semantic_leaves.py",
                "g2/tests/test_runtime_case_pure_helpers.py",
                "g2/tests/test_runtime_case_register_policies.py",
                "g2/tests/fixtures/runtime_case_semantic_leaves_host.c",
                "g2/tests/fixtures/runtime_case_pure_helpers_host.c",
                "g2/tests/fixtures/runtime_case_register_policies_host.c",
                "g2/tools/manifests/g2-case-semantic-leaves-admission-summary.json",
                "g2/tools/manifests/g2-case-semantic-leaves-admission.tsv",
                "g2/tools/manifests/g2-case-pure-helpers-admission-summary.json",
                "g2/tools/manifests/g2-case-pure-helpers-admission.tsv",
                "g2/tools/manifests/g2-case-register-policies-admission-summary.json",
                "g2/tools/manifests/g2-case-register-policies-admission.tsv",
                "g2/tools/manifests/g2-case-final-classification-summary.json",
                "g2/tools/manifests/g2-case-final-function-frontier.tsv",
                "g2/tools/manifests/g2-case-final-gap-frontier.tsv",
                "g2/tools/manifests/g2-case-final-physical-byte-buckets.tsv",
                "g2/components/shared/lvgl/runtime_nemavg_stroke_caps_candidate.c",
                "g2/components/shared/lvgl/runtime_nemavg_stroke_caps_candidate.h",
                "g2/tools/manifests/g2-nemavg-stroke-caps-candidate-summary.json",
                "g2/tools/manifests/g2-clkmgr-divider-candidate-summary.json",
                "g2/tests/test_runtime_nemavg_stroke_caps_candidate.py",
                "g2/tests/fixtures/runtime_nemavg_stroke_caps_host.c",
                "g2/tests/test_runtime_clkmgr_divider_candidate.py",
                "g2/tests/fixtures/runtime_clkmgr_divider_candidate_host.c",
                "g2/tools/verify_g2_clkmgr_divider_public.py",
                "g2/tools/apply_g2_canonical_observations.py",
                "g2/tests/test_apply_g2_canonical_observations.py",
                "g2/docs/community-source-distribution.md",
            }
            <= names
        )
        self.assertNotIn("g2/tools/extract_g2_case_final_decomp.py", names)
        self.assertNotIn("g2/tests/test_extract_g2_case_final_decomp.py", names)
        self.assertNotIn("g2/tools/analyze_g2_case_semantic_leaves.py", names)
        self.assertNotIn("g2/tests/test_analyze_g2_case_semantic_leaves.py", names)
        self.assertNotIn("g2/tools/analyze_g2_case_pure_helpers.py", names)
        self.assertNotIn("g2/tests/test_analyze_g2_case_pure_helpers.py", names)
        self.assertNotIn("g2/tools/analyze_g2_case_register_policies.py", names)
        self.assertNotIn("g2/tests/test_analyze_g2_case_register_policies.py", names)
        for relative in (
            "DERIVATION.patch",
            "LICENSE",
            "NOTICE.md",
            "PROVENANCE.json",
            "overlay.json",
            "ring_gesture.c",
            "upstream/gesture_fwd.c",
            "verify_provenance.py",
        ):
            self.assertIn(
                f"g2/components/apollo_main/ring_gesture/{relative}",
                names,
            )
        self.assertIn("g2/tests/test_ring_gesture_provenance.py", names)
        self.assertIn("g2/tools/community_distribution.py", names)
        self.assertIn("g2/NOTICE-CORE-SOURCE.md", names)
        self.assertNotIn("g2/research/candidates/freertos_scheduler_port_trio.h", names)
        self.assertTrue(
            {
                "g2/components/apollo_main/core_overlay/freertos_scheduler_port_trio.c",
                "g2/components/apollo_main/core_overlay/freertos_scheduler_port_trio.h",
            }
            <= names
        )
        self.assertIn(".gitignore", names)
        self.assertIn("LICENSE", names)
        self.assertIn("NOTICE", names)
        self.assertIn("README.md", names)
        self.assertIn("Makefile", names)
        self.assertIn("make.sh", names)
        for license_path in distribution.audit_g2_release_licensing.LICENSE_TEXTS.values():
            self.assertIn(
                license_path.relative_to(distribution.REPOSITORY_ROOT).as_posix(),
                names,
            )
        self.assertFalse(any("/blobs/" in name or "/build/" in name for name in names))
        self.assertFalse(
            any(
                distribution._forbidden_directory_part(part)
                for name in names
                for part in Path(name).parts[:-1]
            )
        )
        self.assertFalse(any(name.endswith("/build-report.json") for name in names))
        self.assertFalse(any(Path(name).name in distribution.FORBIDDEN_FILENAMES for name in names))
        self.assertFalse(any(Path(name).suffix.lower() in distribution.FORBIDDEN_SUFFIXES for name in names))
        self.assertFalse(
            any(
                Path(name).name.lower() in distribution.FORBIDDEN_SECRET_FILENAMES
                or Path(name).suffix.lower() in distribution.FORBIDDEN_SECRET_SUFFIXES
                for name in names
            )
        )
        shared = {
            path.relative_to(distribution.REPOSITORY_ROOT).as_posix()
            for path in (distribution.ROOT / "components/shared").rglob("*")
            if path.is_file() and distribution._allowed_source_file(path)
        }
        bundled_shared = {
            name for name in names if name.startswith("g2/components/shared/")
        }
        self.assertEqual(bundled_shared, shared)
        self.assertTrue(
            {
                "g2/tests/test_runtime_nemavg_stroke_caps_candidate.py",
                "g2/tests/fixtures/runtime_nemavg_stroke_caps_host.c",
            }
            <= names
        )
        case_source_image = {
            path.relative_to(distribution.REPOSITORY_ROOT).as_posix()
            for path in (distribution.ROOT / "components/case/source_image").rglob("*")
            if path.is_file() and distribution._allowed_source_file(path)
        }
        bundled_case_source_image = {
            name
            for name in names
            if name.startswith("g2/components/case/source_image/")
        }
        self.assertEqual(len(case_source_image), 5)
        self.assertEqual(bundled_case_source_image, case_source_image)
        em9305_source_image = {
            path.relative_to(distribution.REPOSITORY_ROOT).as_posix()
            for path in (distribution.ROOT /
                          "components/em9305/source_image").rglob("*")
            if path.is_file() and distribution._allowed_source_file(path)
        }
        bundled_em9305_source_image = {
            name for name in names
            if name.startswith("g2/components/em9305/source_image/")
        }
        self.assertEqual(len(em9305_source_image), 3)
        self.assertEqual(bundled_em9305_source_image, em9305_source_image)
        public_analysis = {
            *distribution.TOUCH_PUBLIC_ANALYZER_MEMBERS,
            "g2/tools/analyze_g2_case_source_image.py",
            "g2/tests/test_analyze_g2_case_source_image.py",
            "g2/tools/analyze_em9305_record_package.py",
            "g2/tests/test_analyze_em9305_record_package.py",
            "g2/tools/analyze_g2_touch_source_image.py",
            "g2/tests/test_analyze_g2_touch_source_image.py",
            "g2/tools/analyze_g2_dual_profile_ownership.py",
            "g2/tests/test_analyze_g2_dual_profile_ownership.py",
        }
        self.assertFalse(
            {
                name
                for name in names
                if (
                    name.startswith("g2/tools/analyze_")
                    or name.startswith("g2/tests/test_analyze_")
                )
                and name not in public_analysis
            }
        )
        self.assertFalse(
            any(
                name.startswith("g2/tools/extract_")
                or name.startswith("g2/tests/test_extract_")
                for name in names
            )
        )
        with zipfile.ZipFile(self.first) as archive:
            self.assertTrue(
                all(
                    info.compress_type == zipfile.ZIP_STORED
                    and info.compress_size == info.file_size
                    and info.date_time == (1980, 1, 1, 0, 0, 0)
                    and info.create_system == 3
                    and info.create_version == 20
                    and info.extract_version == 20
                    and info.flag_bits == 0
                    and info.extra == b""
                    and info.comment == b""
                    for info in archive.infolist()
                )
            )
            self.assertEqual(
                archive.read(".gitignore"),
                (distribution.REPOSITORY_ROOT / ".gitignore").read_bytes(),
            )
            self.assertEqual(
                archive.read("LICENSE"),
                (distribution.REPOSITORY_ROOT / "LICENSE").read_bytes(),
            )
            self.assertEqual(
                archive.read("NOTICE"),
                (distribution.REPOSITORY_ROOT / "NOTICE").read_bytes(),
            )
            self.assertFalse(
                any(
                    distribution.LONG_HEX_BODY.search(archive.read(name))
                    for name in archive.namelist()[1:]
                )
            )
            self.assertFalse(
                any(
                    distribution.PRIVATE_KEY_BLOCK.search(archive.read(name))
                    for name in archive.namelist()[1:]
                )
            )
            for name in archive.namelist()[1:]:
                if Path(name).suffix == ".json":
                    self.assertEqual(
                        distribution._raw_stock_guard_paths(
                            json.loads(archive.read(name))
                        ),
                        [],
                        name,
                    )

    def test_public_evidence_closure_is_exact_hashed_and_licensed(self) -> None:
        names = {row["path"] for row in self.manifest["files"]}
        with zipfile.ZipFile(self.first) as archive:
            summary = json.loads(
                archive.read(distribution.TOUCH_FINAL_CLASSIFICATION_RECEIPT)
            )
        touch_inputs = distribution._touch_public_analysis_inputs_from_summary(
            summary
        )
        self.assertEqual(len(touch_inputs), 68)
        self.assertTrue(set(touch_inputs) <= names)
        self.assertEqual(
            {
                path for path in touch_inputs
                if path.startswith("g2/tools/analyze_")
                and path.endswith(".py")
            },
            set(distribution.TOUCH_PUBLIC_ANALYZER_MEMBERS),
        )
        self.assertNotIn(
            f"g2/{distribution.TOUCH_OFFICIAL_DONOR_INPUT}", names
        )
        self.assertTrue(
            distribution.PUBLIC_EVIDENCE_RECEIPT_MEMBERS <= names
        )
        self.assertEqual(
            {
                path for path in names
                if path.startswith("g2/tools/manifests/g2-touch-")
                and path.endswith(".tsv")
                and (
                    "-admission" in PurePosixPath(path).name
                    or PurePosixPath(path).name
                    == "g2-touch-software-readiness-functions.tsv"
                )
            },
            set(distribution.TOUCH_ADMISSION_RECEIPT_MEMBERS),
        )
        ledger = {
            row["path"]: row
            for row in self.manifest["member_license_ledger"]
        }
        for path in distribution.PUBLIC_EVIDENCE_RECEIPT_MEMBERS:
            with self.subTest(receipt=path):
                self.assertEqual(ledger[path]["license"], "MIT")
                self.assertEqual(
                    ledger[path]["member_class"],
                    "project_generated_receipt",
                )
        for path in distribution.TOUCH_PUBLIC_ANALYZER_MEMBERS:
            with self.subTest(analyzer=path):
                self.assertEqual(ledger[path]["license"], "MIT")
                self.assertEqual(ledger[path]["member_class"], "code_source")
        file_rows = {row["path"]: row for row in self.manifest["files"]}
        completion = self.manifest["completion_assessment"]
        self.assertTrue(completion["included"])
        self.assertEqual(
            [row["path"] for row in completion["members"]],
            list(distribution.COMPLETION_REPORT_MEMBERS),
        )
        for row in completion["members"]:
            self.assertEqual(row, file_rows[row["path"]])

    def test_public_policy_rejects_raw_guards_secrets_and_internal_paths(self) -> None:
        invensense_root = (
            distribution.ROOT / "third_party/invensense-icm45608"
        )
        detected_invensense_risks = set()
        for path in invensense_root.rglob("*"):
            if not path.is_file():
                continue
            data = path.read_bytes()
            if (
                distribution.DENSE_BYTE_TRANSCRIPT.search(data)
                or distribution.ESCAPED_BYTE_TRANSCRIPT.search(data)
                or distribution.BASE64_BODY.search(data)
                or distribution.RESTRICTED_SOURCE_NOTICE.search(data)
            ):
                detected_invensense_risks.add(
                    path.relative_to(distribution.REPOSITORY_ROOT).as_posix()
                )
        self.assertEqual(len(detected_invensense_risks), 15)
        self.assertEqual(
            detected_invensense_risks,
            distribution.FORBIDDEN_INVENSENSE_EDMP_MEMBERS,
        )
        for path in distribution.FORBIDDEN_INVENSENSE_EDMP_MEMBERS:
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "forbidden InvenSense EDMP member",
            ):
                distribution._verify_public_payload(path, b"/* benign replacement */\n")
        forbidden_source = min(distribution.FORBIDDEN_INVENSENSE_EDMP_MEMBERS)
        with (
            mock.patch.object(distribution, "collect_files", return_value=[]),
            mock.patch.object(
                distribution,
                "RELOCATED_PUBLIC_SOURCES",
                {forbidden_source: "g2/components/example/benign.h"},
            ),
        ):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "forbidden InvenSense EDMP source selected",
            ):
                distribution._selected_records()
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "raw stock-byte guard",
        ):
            distribution._verify_public_payload(
                "g2/manifests/forged.json",
                b'{"nested": [{"expected_hex": "00112233"}]}',
            )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "raw encoded byte array"
        ):
            distribution._verify_public_payload(
                "g2/manifests/forged.json",
                json.dumps({"payload": list(range(16))}).encode(),
            )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "embedded base64 body"
        ):
            distribution._verify_public_payload(
                "g2/docs/forged.txt", b"A" * 172
            )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "encoded vendor-byte transcript"
        ):
            distribution._verify_public_payload(
                "g2/docs/forged.txt", b"0x00," * 16
            )
        for path in (
            "g2/config/.env",
            "g2/config/owner-private.key",
            "g2/research/candidates/private.c",
        ):
            self.assertFalse(distribution._allowed_archive_file(Path(path)))
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "private-key material",
        ):
            distribution._verify_public_payload(
                "g2/docs/forged.txt",
                b"-----BEGIN " + b"PRIVATE KEY-----\nnot-a-real-key\n",
            )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "restricted vendor source notice"
        ):
            distribution._verify_public_payload(
                "g2/docs/forged-restricted-notice.txt",
                (
                    b"use, reproduction, disclosure or distribution of the Software "
                    b"without an express license agreement from the vendor is strictly "
                    b"prohibited\n"
                ),
            )
        inventory = {row["path"] for row in self.manifest["files"]}
        self.assertEqual(
            inventory & distribution.FORBIDDEN_INVENSENSE_EDMP_MEMBERS,
            set(),
        )
        self.assertEqual(
            {
                path for path in inventory
                if "invensense" in path.lower() or "imu_icm45608" in path
            },
            {"g2/third_party/invensense-icm45608/LICENSE"},
        )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "forbidden InvenSense EDMP member selected",
        ):
            distribution._verify_public_inventory(
                inventory
                | {min(distribution.FORBIDDEN_INVENSENSE_EDMP_MEMBERS)}
            )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "internal analysis artifact",
        ):
            distribution._verify_public_inventory(
                inventory | {"g2/tools/analyze_private_decomp.py"}
            )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "required community source is absent",
        ):
            distribution._verify_public_inventory(
                inventory - {"g2/tests/test_runtime_pt_protocol_core.py"}
            )

    def test_apollo_stock_byte_guards_are_distributed_only_as_hashes(self) -> None:
        raw = json.loads(
            (
                distribution.REPOSITORY_ROOT
                / distribution.SANITIZED_APOLLO_OVERLAY
            ).read_text(encoding="utf-8")
        )
        with zipfile.ZipFile(self.first) as archive:
            bundled = json.loads(archive.read(distribution.SANITIZED_APOLLO_OVERLAY))
        raw_sites = {
            site["name"]: site
            for site in raw["patch_sites"]
            if "expected_hex" in site
        }
        bundled_sites = {site["name"]: site for site in bundled["patch_sites"]}
        self.assertGreater(len(raw_sites), 1)
        self.assertFalse(
            any("expected_hex" in site for site in bundled["patch_sites"])
        )
        for name, raw_site in raw_sites.items():
            expected = bytes.fromhex(raw_site["expected_hex"])
            bundled_site = bundled_sites[name]
            self.assertEqual(bundled_site["expected_size"], len(expected))
            self.assertEqual(
                bundled_site["expected_sha256"], hashlib.sha256(expected).hexdigest()
            )
        raw_literals = [
            relocation
            for leaf in raw["in_place_leaves"]
            for relocation in leaf.get("relocations", [])
            if "target_expected_hex" in relocation
        ]
        bundled_literals = [
            relocation
            for leaf in bundled["in_place_leaves"]
            for relocation in leaf.get("relocations", [])
            if "target_expected_size" in relocation
        ]
        self.assertGreater(len(raw_literals), 1)
        self.assertEqual(len(bundled_literals), len(raw_literals))
        self.assertFalse(
            any(
                "target_expected_hex" in relocation
                for leaf in bundled["in_place_leaves"]
                for relocation in leaf.get("relocations", [])
            )
        )
        expected_literal_pins = {
            (
                relocation["target_address"],
                len(bytes.fromhex(relocation["target_expected_hex"])),
                hashlib.sha256(
                    bytes.fromhex(relocation["target_expected_hex"])
                ).hexdigest(),
            )
            for relocation in raw_literals
        }
        bundled_literal_pins = {
            (
                relocation["target_address"],
                relocation["target_expected_size"],
                relocation["target_expected_sha256"],
            )
            for relocation in bundled_literals
        }
        self.assertEqual(bundled_literal_pins, expected_literal_pins)
        forged = json.loads(json.dumps(bundled))
        forged["patch_sites"][0]["expected_hex"] = "00000000"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "stock bytes remain embedded",
        ):
            distribution._verify_sanitized_apollo_overlay(forged)

        malformed = json.loads(json.dumps(bundled))
        malformed["patch_sites"][0].pop("expected_sha256")
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "hash contract",
        ):
            distribution._verify_sanitized_apollo_overlay(malformed)

    def test_liblc3_stock_callsite_guard_is_distributed_only_as_a_hash(self) -> None:
        raw = json.loads(
            (distribution.REPOSITORY_ROOT / distribution.SANITIZED_LIBLC3_OVERLAY)
            .read_text(encoding="utf-8")
        )
        with zipfile.ZipFile(self.first) as archive:
            bundled = json.loads(archive.read(distribution.SANITIZED_LIBLC3_OVERLAY))
        expected = bytes.fromhex(raw["patch_site"]["expected_hex"])
        self.assertNotIn("expected_hex", bundled["patch_site"])
        self.assertEqual(bundled["patch_site"]["expected_size"], len(expected))
        self.assertEqual(
            bundled["patch_site"]["expected_sha256"],
            hashlib.sha256(expected).hexdigest(),
        )
        distribution._verify_sanitized_liblc3_overlay(bundled)

    def test_ring_stock_callsites_are_distributed_only_as_hashes(self) -> None:
        raw = json.loads(
            (distribution.REPOSITORY_ROOT / distribution.SANITIZED_RING_OVERLAY)
            .read_text(encoding="utf-8")
        )
        with zipfile.ZipFile(self.first) as archive:
            bundled = json.loads(archive.read(distribution.SANITIZED_RING_OVERLAY))
        self.assertEqual(len(bundled["patch_sites"]), len(raw["patch_sites"]))
        for raw_site, bundled_site in zip(raw["patch_sites"], bundled["patch_sites"]):
            expected = bytes.fromhex(raw_site["expected_hex"])
            self.assertNotIn("expected_hex", bundled_site)
            self.assertEqual(bundled_site["expected_size"], len(expected))
            self.assertEqual(
                bundled_site["expected_sha256"], hashlib.sha256(expected).hexdigest()
            )
        distribution._verify_sanitized_ring_overlay(bundled)

    def test_raw_executable_transcript_directives_are_rejected(self) -> None:
        for directive in (
            b".byte 0x00\n",
            b'".short 0xe7fe\\n"',
            b".hword 0xbf00\n",
        ):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "raw executable transcript directive",
            ):
                distribution._reject_raw_executable_transcript(
                    "g2/components/example/runtime_transcript.c", directive
                )
        distribution._reject_raw_executable_transcript(
            "g2/components/example/runtime_literal.c",
            b".word 0x20000518\n",
        )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "raw executable transcript directive",
        ):
            distribution._verify_public_payload(
                "g2/third_party/example/raw_payload.S", b".byte 0x00\n"
            )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "encoded vendor-byte transcript"
        ):
            distribution._verify_public_payload(
                "g2/third_party/example/vendor_image.h",
                (b"0x36," * 16) + b"\n",
            )
        numeric_array = (
            b"static const unsigned char payload[] = {"
            + b", ".join(str(value).encode() for value in range(16))
            + b"};\n"
        )
        for path in (
            "g2/components/example/vendor_image.c",
            "g2/components/example/vendor_image.cpp",
            "g2/components/example/vendor_image.inc",
        ):
            with self.subTest(numeric_array_path=path), self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "unreviewed numeric byte array",
            ):
                distribution._verify_public_payload(path, numeric_array)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "raw executable transcript directive"
        ):
            distribution._verify_public_payload(
                "g2/components/example/vendor_image.S",
                b".byte " + b", ".join(str(value).encode() for value in range(16)),
            )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "split encoded vendor-byte transcript",
        ):
            distribution._verify_public_payload(
                "g2/components/example/vendor_image.c",
                b'const char payload[] = "' + b"A" * 86 + b'" "'
                + b"A" * 86 + b'";\n',
            )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "encoded vendor-byte transcript"
        ):
            distribution._verify_public_payload(
                "g2/components/example/vendor_image.c",
                b"const char payload[] = " + b'"\\000" ' * 16 + b";\n",
            )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "literal executable encoding constructor",
        ):
            distribution._verify_public_payload(
                "g2/components/example/vendor_image.py",
                b"payload = [" + b", ".join(
                    str(value).encode() for value in range(16)
                ) + b"]\n",
            )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "raw encoded byte array"
        ):
            distribution._verify_public_payload(
                "g2/components/example/vendor_image.json",
                json.dumps({"chunks": [list(range(8)), list(range(8, 16))]}).encode(),
            )
        for encoded in (
            b'payload = bytes.fromhex("36f0" "c3fe")\n',
            b'payload = binascii.unhexlify(b"36f0c3fe")\n',
            b'payload = base64.b64decode("NvDD/g==")\n',
            b'payload = b"\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07'
            b'\\x08\\x09\\x0a\\x0b\\x0c\\x0d\\x0e\\x0f"\n',
            b"payload = bytes([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])\n",
        ):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "literal executable encoding constructor",
            ):
                distribution._reject_raw_executable_transcript(
                    "g2/components/example/build_component.py", encoded
                )

        hex_chunks = [
            "".join(f"{(chunk * 64 + index) & 0xFF:02x}" for index in range(64))
            for chunk in range(8)
        ]
        escaped_chunks = [
            "".join(f"\\x{(chunk * 15 + index) & 0xFF:02x}" for index in range(15))
            for chunk in range(8)
        ]
        adversarial_encodings = {
            "c-comment-split-hex": (
                "g2/components/example/vendor_image.c",
                (
                    "static const char payload[] = "
                    + "/* split */".join(f'"{chunk}"' for chunk in hex_chunks)
                    + ";\n"
                ).encode(),
            ),
            "c-comment-split-escapes": (
                "g2/components/example/vendor_image.c",
                (
                    "static const char payload[] = "
                    + "/* split */".join(
                        f'"{chunk}"' for chunk in escaped_chunks
                    )
                    + ";\n"
                ).encode(),
            ),
            "c-macro-wrapped-array": (
                "g2/components/example/vendor_image.c",
                (
                    "#define BYTE(value) value\n"
                    "static const unsigned char payload[] = {"
                    + ",".join(f"BYTE(0x{value:02x})" for value in range(32))
                    + "};\n"
                ).encode(),
            ),
            "cpp-character-array": (
                "g2/components/example/vendor_image.cpp",
                (
                    "static const unsigned char payload[] = {"
                    + ",".join(f"'\\x{value:02x}'" for value in range(32))
                    + "};\n"
                ).encode(),
            ),
            "assembly-wide-directive": (
                "g2/components/example/vendor_image.S",
                (
                    ".word "
                    + ",".join(f"0x{value:08x}" for value in range(64))
                    + "\n"
                ).encode(),
            ),
            "python-concatenated-fromhex": (
                "g2/components/example/vendor_image.py",
                (
                    "payload = bytes.fromhex("
                    + " + ".join(repr(chunk) for chunk in hex_chunks)
                    + ")\n"
                ).encode(),
            ),
            "python-generator-fromhex": (
                "g2/components/example/vendor_image.py",
                (
                    'payload = b"".join(bytes.fromhex(chunk) for chunk in '
                    + repr(hex_chunks)
                    + ")\n"
                ).encode(),
            ),
            "json-encoded-chunks": (
                "g2/components/example/vendor_image.json",
                json.dumps({"encoding": "hex", "chunks": hex_chunks}).encode(),
            ),
        }
        for label, (path, encoded) in adversarial_encodings.items():
            with self.subTest(adversarial_encoding=label), self.assertRaises(
                distribution.CommunityBundleError
            ):
                distribution._verify_public_payload(path, encoded)

        legitimate_controls = {
            "single-address-word": (
                "g2/components/example/runtime_pointer.S",
                b".word 0x20000518\n",
            ),
            "dynamic-decoder": (
                "g2/components/example/build_component.py",
                b"def decode(value):\n    return bytes.fromhex(value)\n",
            ),
            "short-semantic-array": (
                "g2/components/example/runtime_table.c",
                b"static const unsigned char values[] = {1, 2, 3, 4};\n",
            ),
            "json-hash-list": (
                "g2/manifests/hash_receipt.json",
                json.dumps({"sha256": ["a" * 64, "b" * 64]}).encode(),
            ),
        }
        for label, (path, encoded) in legitimate_controls.items():
            with self.subTest(legitimate_control=label):
                distribution._verify_public_payload(path, encoded)

    def test_reviewed_semantic_numeric_tables_are_exactly_receipted(self) -> None:
        for archive_path, expected in sorted(
            distribution.REVIEWED_PUBLIC_NUMERIC_ARRAYS.items()
        ):
            with self.subTest(path=archive_path):
                data = (distribution.REPOSITORY_ROOT / archive_path).read_bytes()
                self.assertEqual(
                    distribution._c_numeric_array_receipts(data), expected
                )
                distribution._reject_raw_executable_transcript(archive_path, data)

        archive_path = (
            "g2/components/shared/gx8002/"
            "runtime_gx8002_backup_runtime_boundary.c"
        )
        data = (distribution.REPOSITORY_ROOT / archive_path).read_bytes()
        mutated = data.replace(b"0xcdU", b"0xceU", 1)
        self.assertNotEqual(mutated, data)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "unreviewed numeric byte array"
        ):
            distribution._reject_raw_executable_transcript(archive_path, mutated)

    def test_bundle_member_hashes_exclude_every_official_payload(self) -> None:
        official = distribution._official_provider_hashes() | {
            distribution.OFFICIAL_PACKAGE_SHA256
        }
        self.assertEqual(len(distribution.OFFICIAL_PAYLOAD_SHA256), 6)
        self.assertEqual(
            official,
            distribution.FORBIDDEN_OFFICIAL_FIRMWARE_SHA256,
        )
        self.assertFalse(official & {row["sha256"] for row in self.manifest["files"]})
        with zipfile.ZipFile(self.first) as archive:
            self.assertEqual(archive.namelist()[0], "BUNDLE-MANIFEST.json")
            self.assertEqual(
                archive.read("README.md"),
                (distribution.ROOT / "docs/community-archive-README.md").read_bytes(),
            )
            self.assertNotEqual(
                archive.read("README.md"),
                (distribution.REPOSITORY_ROOT / "README.md").read_bytes(),
            )
            self.assertEqual(
                (archive.getinfo("make.sh").external_attr >> 16) & 0o777,
                0o755,
            )
            self.assertEqual(
                (archive.getinfo("Makefile").external_attr >> 16) & 0o777,
                0o644,
            )
            self.assertEqual(
                (archive.getinfo("g2/make.sh").external_attr >> 16) & 0o777,
                0o755,
            )
            self.assertEqual(
                (archive.getinfo("g2/Makefile").external_attr >> 16) & 0o777,
                0o644,
            )

    def test_bundled_ring_gesture_provenance_is_self_verifying(self) -> None:
        extraction = Path(self.temporary.name) / "ring-provenance-extraction"
        with zipfile.ZipFile(self.first) as archive:
            archive.extractall(extraction)
        verifier_path = (
            extraction
            / "g2/components/apollo_main/ring_gesture/verify_provenance.py"
        )
        spec = importlib.util.spec_from_file_location(
            "bundled_ring_gesture_provenance",
            verifier_path,
        )
        verifier = importlib.util.module_from_spec(spec)
        self.assertIsNotNone(spec.loader)
        spec.loader.exec_module(verifier)
        report = verifier.verify()
        self.assertEqual(
            report["upstream_blob"],
            "4997b81d4afa1ede5bd15c79957509f65ec75828",
        )
        self.assertFalse(report["network_used"])
        self.assertFalse(report["hardware_used"])

    def test_verifier_rejects_a_false_manifest_envelope(self) -> None:
        forged = Path(self.temporary.name) / "forged.zip"
        with zipfile.ZipFile(self.first) as source:
            members = [(info, source.read(info.filename)) for info in source.infolist()]
        info, manifest_data = members[0]
        manifest = json.loads(manifest_data)
        manifest["contains_official_firmware_payloads"] = True
        members[0] = (info, (json.dumps(manifest, sort_keys=True) + "\n").encode())
        with zipfile.ZipFile(forged, "w") as destination:
            for member, data in members:
                destination.writestr(member, data)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "manifest envelope"
        ):
            distribution.verify_bundle(forged)

    def test_verifier_requires_the_exact_top_level_manifest_schema(self) -> None:
        with zipfile.ZipFile(self.first) as source:
            members = [(info, source.read(info.filename)) for info in source.infolist()]
        info, manifest_data = members[0]
        original = json.loads(manifest_data)
        self.assertEqual(set(original), distribution.BUNDLE_MANIFEST_FIELDS)

        mutations = {
            "extra": lambda value: value.update({"release_authorized": True}),
            "missing": lambda value: value.pop("archive_encoding"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                manifest = dict(original)
                mutate(manifest)
                forged = Path(self.temporary.name) / f"manifest-{label}.zip"
                forged_members = list(members)
                forged_members[0] = (
                    info,
                    (json.dumps(manifest, sort_keys=True) + "\n").encode(),
                )
                with zipfile.ZipFile(forged, "w") as destination:
                    for member, data in forged_members:
                        destination.writestr(member, data)
                with self.assertRaisesRegex(
                    distribution.CommunityBundleError, "manifest envelope"
                ):
                    distribution.verify_bundle(forged)

    def test_verifier_rejects_tampered_dual_profile_proof_binding(self) -> None:
        forged = Path(self.temporary.name) / "dual-proof-tampered.zip"
        with zipfile.ZipFile(self.first) as source:
            members = [(info, source.read(info.filename)) for info in source.infolist()]
        info, manifest_data = members[0]
        manifest = json.loads(manifest_data)
        manifest["dual_profile_ownership_proof"]["members"][0]["sha256"] = "0" * 64
        members[0] = (
            info, (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
        )
        with zipfile.ZipFile(forged, "w") as destination:
            for member, data in members:
                destination.writestr(member, data)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "dual-profile ownership proof binding changed",
        ):
            distribution.verify_bundle(forged)

    def test_verifier_rejects_malformed_manifest_json(self) -> None:
        forged = Path(self.temporary.name) / "malformed.zip"
        with zipfile.ZipFile(self.first) as source:
            members = [(info, source.read(info.filename)) for info in source.infolist()]
        members[0] = (members[0][0], b"{")
        with zipfile.ZipFile(forged, "w") as destination:
            for member, data in members:
                destination.writestr(member, data)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "not valid JSON"
        ):
            distribution.verify_bundle(forged)

    def test_archive_caps_and_single_snapshot_verification_are_fail_closed(self) -> None:
        class SingleRead:
            def __init__(self, payload: bytes) -> None:
                self.payload = payload
                self.reads = 0

            def read_bytes(self) -> bytes:
                self.reads += 1
                if self.reads > 1:
                    raise AssertionError("bundle path was reopened")
                return self.payload

        source = SingleRead(self.first.read_bytes())
        distribution.verify_bundle(source)  # type: ignore[arg-type]
        self.assertEqual(source.reads, 1)
        symlink = Path(self.temporary.name) / "bundle-link.zip"
        symlink.symlink_to(self.first)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "path is a symlink"
        ):
            distribution.verify_bundle(symlink)
        hardlink = Path(self.temporary.name) / "bundle-hardlink.zip"
        os.link(self.first, hardlink)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "independent regular file"
        ):
            distribution.verify_bundle(hardlink)
        hardlink.unlink()
        with mock.patch.object(distribution, "MAX_ARCHIVE_SIZE", 1):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError, "byte-size cap"
            ):
                distribution.verify_bundle(self.first)
        with mock.patch.object(distribution, "MAX_ARCHIVE_MEMBERS", 1):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError, "order or uniqueness"
            ):
                distribution.verify_bundle(self.first)
        with mock.patch.object(distribution, "MAX_ARCHIVE_MEMBER_SIZE", 1):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError, "unsafe bundle member"
            ):
                distribution.verify_bundle(self.first)

        real_fstat = os.fstat
        regular_fstat_calls = 0

        def drifting_fstat(descriptor: int):
            nonlocal regular_fstat_calls
            result = real_fstat(descriptor)
            if not stat.S_ISREG(result.st_mode):
                return result
            regular_fstat_calls += 1
            if regular_fstat_calls != 2:
                return result
            return SimpleNamespace(
                st_mode=result.st_mode,
                st_nlink=result.st_nlink,
                st_size=result.st_size,
                st_dev=result.st_dev,
                st_ino=result.st_ino,
                st_mtime_ns=result.st_mtime_ns,
                st_ctime_ns=result.st_ctime_ns + 1,
            )

        with mock.patch.object(distribution.os, "fstat", side_effect=drifting_fstat):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError, "changed during read"
            ):
                distribution.verify_bundle(self.first)

        source = distribution.REPOSITORY_ROOT / "g2/tools/community_distribution.py"
        source_data = source.read_bytes()
        records = [(source, "g2/tools/community_distribution.py")]
        raw_by_path = {source.resolve(): source_data}
        capture_digest = distribution._source_capture_digest(records, raw_by_path)
        real_source_read = distribution._read_regular_source_once

        def changed_source(path: Path) -> bytes:
            if path == source:
                return source_data + b"\n"
            return real_source_read(path)

        with (
            mock.patch.object(distribution, "_selected_records", return_value=records),
            mock.patch.object(
                distribution, "_read_regular_source_once", changed_source
            ),
        ):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "source bytes changed during capture",
            ):
                REQUIRE_SOURCE_CAPTURE_UNCHANGED(
                    records, raw_by_path, capture_digest
                )

    def test_source_capture_is_single_descriptor_nofollow_and_stable(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="opencfw-community-source-safe-"
        ) as temporary:
            repository = Path(temporary)
            source_dir = repository / "sources"
            source_dir.mkdir()
            source = source_dir / "source.c"
            source.write_bytes(b"original source\n")
            with mock.patch.object(distribution, "REPOSITORY_ROOT", repository):
                self.assertEqual(
                    distribution._read_regular_source_once(source),
                    b"original source\n",
                )

                hardlink = source_dir / "source-hardlink.c"
                os.link(source, hardlink)
                with self.assertRaisesRegex(
                    distribution.CommunityBundleError,
                    "independent regular file",
                ):
                    distribution._read_regular_source_once(source)
                hardlink.unlink()

                leaf_link = source_dir / "leaf-link.c"
                leaf_link.symlink_to(source)
                with self.assertRaisesRegex(
                    distribution.CommunityBundleError, "opened safely"
                ):
                    distribution._read_regular_source_once(leaf_link)

                parent_link = repository / "source-link"
                parent_link.symlink_to(source_dir, target_is_directory=True)
                with self.assertRaisesRegex(
                    distribution.CommunityBundleError, "opened safely"
                ):
                    distribution._read_regular_source_once(
                        parent_link / "source.c"
                    )

                replacement = source_dir / "replacement.c"
                replacement.write_bytes(b"replacement source\n")
                real_open = os.open
                swapped = False

                def swapping_open(path, flags, *args, **kwargs):
                    nonlocal swapped
                    descriptor = real_open(path, flags, *args, **kwargs)
                    if path == "source.c" and not swapped:
                        swapped = True
                        os.replace(replacement, source)
                    return descriptor

                with mock.patch.object(
                    distribution.os, "open", side_effect=swapping_open
                ):
                    with self.assertRaisesRegex(
                        distribution.CommunityBundleError,
                        "independent regular file",
                    ):
                        distribution._read_regular_source_once(source)
                self.assertEqual(source.read_bytes(), b"replacement source\n")

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
                    distribution.os, "fstat", side_effect=drifting_fstat
                ):
                    with self.assertRaisesRegex(
                        distribution.CommunityBundleError,
                        "changed during descriptor read",
                    ):
                        distribution._read_regular_source_once(source)

    def test_member_paths_and_source_license_ledger_are_fail_closed(self) -> None:
        distribution._validate_archive_names(
            ["BUNDLE-MANIFEST.json", "g2/source.c"]
        )
        for names in (
            ["BUNDLE-MANIFEST.json", "g2/source.c", "g2/source.c"],
            ["BUNDLE-MANIFEST.json", "g2/source.c", "G2/source.c"],
            ["BUNDLE-MANIFEST.json", "g2/source.c", "g2/source.c/child.h"],
        ):
            with self.assertRaises(distribution.CommunityBundleError):
                distribution._validate_archive_names(names)
        unsafe = zipfile.ZipInfo("g2/source\n.c", (1980, 1, 1, 0, 0, 0))
        unsafe.create_system = 3
        unsafe.external_attr = (0o100644 << 16)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "unsafe bundle member"
        ):
            distribution._validate_archive_info(unsafe)
        for unsafe_name in ("/absolute.c", "../escape.c", "g2\\escape.c"):
            unsafe = zipfile.ZipInfo(unsafe_name, (1980, 1, 1, 0, 0, 0))
            unsafe.create_system = 3
            unsafe.external_attr = (0o100644 << 16)
            with self.assertRaisesRegex(
                distribution.CommunityBundleError, "unsafe bundle member"
            ):
                distribution._validate_archive_info(unsafe)
        special = zipfile.ZipInfo("g2/symlink.c", (1980, 1, 1, 0, 0, 0))
        special.create_system = 3
        special.external_attr = (0o120777 << 16)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "unsafe bundle member"
        ):
            distribution._validate_archive_info(special)

        payload = {
            "LICENSE": (distribution.REPOSITORY_ROOT / "LICENSE").read_bytes(),
            "g2/components/example/runtime.py": (
                b"# SPDX-License-Identifier: MIT\nvalue = 1\n"
            ),
        }
        ledger, closure = distribution._bundle_member_license_ledger(payload)
        self.assertEqual(closure["source_like_members"], 1)
        source_row = next(
            row for row in ledger if row["path"].endswith("runtime.py")
        )
        self.assertEqual(source_row["member_class"], "code_source")
        self.assertEqual(source_row["basis"], "direct-spdx-marker")
        payload["g2/components/example/unlicensed.py"] = b"value = 2\n"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "member license is unresolved"
        ):
            distribution._bundle_member_license_ledger(payload)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "member license is unresolved"
        ):
            distribution._bundle_member_license_ledger({
                "g2/third_party/invensense-icm45608/LICENSE": (
                    distribution.REPOSITORY_ROOT
                    / "g2/third_party/invensense-icm45608/LICENSE"
                ).read_bytes(),
                "g2/third_party/invensense-icm45608/src/imu/benign.c": (
                    b"int apparently_benign_vendor_source;\n"
                ),
            })
        with mock.patch.object(distribution, "MAX_ARCHIVE_UNCOMPRESSED_SIZE", 1):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError, "uncompressed-size cap"
            ):
                distribution._verify_bundle_bytes(self.first.read_bytes())

    def test_create_directly_requires_current_assessment_and_license_closure(self) -> None:
        output = Path(self.temporary.name) / "must-not-publish.zip"
        with mock.patch.object(
            distribution,
            "_require_completion_assessment_current",
            side_effect=distribution.CommunityBundleError("stale assessment"),
        ):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError, "stale assessment"
            ):
                distribution.create_bundle(output)
        self.assertFalse(output.exists())

        rollback_output = Path(self.temporary.name) / "rollback.zip"
        prior_output = b"prior community archive\n"
        rollback_output.write_bytes(prior_output)
        source = distribution.REPOSITORY_ROOT / "LICENSE"
        source_data = source.read_bytes()
        records = [(source, "LICENSE")]
        raw_by_path = {source.resolve(): source_data}
        capture_digest = distribution._source_capture_digest(records, raw_by_path)
        license_receipt = {
            "policy": "MIT-where-project-owned-and-upstream-terms-otherwise",
            "normalization_complete": True,
            "overlay_source_files": 1,
            "overlay_source_errors": 0,
            "distributed_project_files": 1,
            "normalized_project_files": 1,
            "pending_project_files": 0,
            "upstream_gpl_files_preserved": 1,
            "receipt_sha256": "0" * 64,
        }
        real_atomic_write = distribution._atomic_write_unique
        publication_calls = 0

        def publish_then_fail(
            path: Path,
            data: bytes,
            *,
            mode: int = 0o644,
            expected_prior: bytes | None | object = distribution._UNCONSTRAINED_PRIOR,
        ) -> None:
            nonlocal publication_calls
            publication_calls += 1
            real_atomic_write(
                path,
                data,
                mode=mode,
                expected_prior=expected_prior,
            )
            if publication_calls == 1:
                raise OSError("injected publication failure")

        with (
            mock.patch.object(
                distribution, "_require_completion_assessment_current"
            ),
            mock.patch.object(
                distribution, "_license_closure", return_value=license_receipt
            ),
            mock.patch.object(
                distribution, "_official_provider_hashes", return_value=set()
            ),
            mock.patch.object(
                distribution,
                "_capture_selected_records",
                return_value=(records, raw_by_path, capture_digest),
            ),
            mock.patch.object(
                distribution, "_require_source_capture_unchanged"
            ),
            mock.patch.object(
                distribution,
                "_dual_profile_proof_binding",
                return_value={"test": True},
            ),
            mock.patch.object(distribution, "_verify_public_evidence_receipts"),
            mock.patch.object(distribution, "_verify_markdown_link_closure"),
            mock.patch.object(
                distribution, "_verify_license_evidence_member_census"
            ),
            mock.patch.object(
                distribution,
                "_bundle_member_license_ledger",
                return_value=([], {"test": True}),
            ),
            mock.patch.object(
                distribution,
                "_completion_assessment_binding",
                return_value={"test": True},
            ),
            mock.patch.object(distribution, "_verify_bundle_bytes"),
            mock.patch.object(
                distribution, "_atomic_write_unique", side_effect=publish_then_fail
            ),
        ):
            with self.assertRaisesRegex(OSError, "injected publication failure"):
                distribution.create_bundle(rollback_output)
        self.assertEqual(rollback_output.read_bytes(), prior_output)
        self.assertEqual(
            list(rollback_output.parent.glob(f".{rollback_output.name}.*.tmp")),
            [],
        )
        with (
            mock.patch.object(
                distribution, "_require_completion_assessment_current"
            ),
            mock.patch.object(
                distribution,
                "_license_closure",
                side_effect=distribution.CommunityBundleError(
                    "license closure failed"
                ),
            ),
        ):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError, "license closure failed"
            ):
                distribution.create_bundle(output)
        self.assertFalse(output.exists())

    def test_local_official_package_must_match_complete_authenticated_identity(self) -> None:
        manifest, _, payloads = open_cfw.verify_manifest(distribution.BASE_MANIFEST)
        image, _ = open_cfw.assemble_evenota(manifest, payloads)
        self.assertEqual(len(image), distribution.OFFICIAL_PACKAGE_SIZE)
        self.assertEqual(hashlib.sha256(image).hexdigest(), distribution.OFFICIAL_PACKAGE_SHA256)
        package = Path(self.temporary.name) / "official.evenota"
        package.write_bytes(image)
        extracted = distribution.authenticate_official_package(package)
        self.assertEqual(len(extracted), 6)
        self.assertEqual(
            {hashlib.sha256(data).hexdigest() for data in extracted.values()},
            distribution._official_provider_hashes(),
        )
        forged_manifest = json.loads(distribution.BASE_MANIFEST.read_text())
        forged_manifest["components"][0]["provider"]["path"] = (
            "tools/community_distribution.py"
        )
        forged_manifest_path = Path(self.temporary.name) / "forged-provider.json"
        forged_manifest_path.write_text(json.dumps(forged_manifest), encoding="utf-8")
        with mock.patch.object(
            distribution, "BASE_MANIFEST", forged_manifest_path
        ), self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "provider name/path/identity contract changed",
        ):
            distribution.authenticate_official_package(package)
        package_symlink = Path(self.temporary.name) / "official-link.evenota"
        package_symlink.symlink_to(package)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "path is a symlink"
        ):
            distribution.authenticate_official_package(package_symlink)
        package_hardlink = Path(self.temporary.name) / "official-hardlink.evenota"
        os.link(package, package_hardlink)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "independent regular file"
        ):
            distribution.authenticate_official_package(package_hardlink)
        package_hardlink.unlink()
        extraction_root = Path(self.temporary.name) / "workspace"
        with zipfile.ZipFile(self.first) as archive:
            archive.extractall(extraction_root)
        workspace = extraction_root / "g2"
        prepared = distribution.prepare_local_workspace(package, workspace)
        self.assertEqual(prepared["providers"], 6)
        self.assertGreater(prepared["include_directories"], 1)
        for relative in distribution._configured_include_dir_names(workspace):
            self.assertTrue((workspace / relative).is_dir())
        for relative, expected in extracted.items():
            self.assertEqual((workspace / relative).read_bytes(), expected)
        receipt_path = workspace / distribution.HYDRATION_RECEIPT
        self.assertTrue(receipt_path.is_file())
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(receipt["hardware_operations"], [])
        self.assertNotIsInstance(receipt["hardware_operations"], bool)
        self.assertEqual(
            receipt["hardware_validation"],
            distribution.DEFERRED_HARDWARE_VALIDATION,
        )
        self.assertEqual(
            distribution._software_only_operation_receipt(),
            {
                "hardware_operations": [],
                "hardware_validation": "blocked by unavailable physical evidence",
            },
        )
        self.assertEqual(
            receipt["official_package"],
            {
                "size": distribution.OFFICIAL_PACKAGE_SIZE,
                "sha256": distribution.OFFICIAL_PACKAGE_SHA256,
            },
        )
        self.assertEqual(len(receipt["providers"]), 6)
        self.assertEqual(
            prepared["receipt_sha256"],
            hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        )
        linked_provider_relative = sorted(extracted)[0]
        linked_provider = workspace / linked_provider_relative
        external_provider_link = Path(self.temporary.name) / "provider-hardlink.bin"
        os.link(linked_provider, external_provider_link)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "independent regular file"
        ):
            distribution.prepare_local_workspace(package, workspace)
        external_provider_link.unlink()
        prior = {}
        for index, relative in enumerate(sorted(extracted)):
            marker = f"prior-provider-{index}".encode()
            target = workspace / relative
            target.write_bytes(marker)
            prior[relative] = marker
        receipt_path.write_text("stale receipt\n", encoding="utf-8")
        real_atomic_write = distribution._atomic_write_unique
        provider_writes = 0
        injected = False

        def fail_second_provider(
            path: Path,
            data: bytes,
            *,
            mode: int = 0o644,
            expected_prior: bytes | None | object = distribution._UNCONSTRAINED_PRIOR,
        ) -> None:
            nonlocal provider_writes, injected
            if path != receipt_path:
                provider_writes += 1
                if provider_writes == 2 and not injected:
                    injected = True
                    raise distribution.CommunityBundleError("injected hydration failure")
            real_atomic_write(
                path, data, mode=mode, expected_prior=expected_prior
            )

        with mock.patch.object(
            distribution, "_atomic_write_unique", side_effect=fail_second_provider
        ):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError, "injected hydration failure"
            ):
                distribution.prepare_local_workspace(package, workspace)
        self.assertFalse(receipt_path.exists())
        for relative, expected in prior.items():
            self.assertEqual((workspace / relative).read_bytes(), expected)

        def fail_receipt(
            path: Path,
            data: bytes,
            *,
            mode: int = 0o644,
            expected_prior: bytes | None | object = distribution._UNCONSTRAINED_PRIOR,
        ) -> None:
            if path == receipt_path:
                raise distribution.CommunityBundleError(
                    "injected receipt publication failure"
                )
            real_atomic_write(
                path, data, mode=mode, expected_prior=expected_prior
            )

        with mock.patch.object(
            distribution, "_atomic_write_unique", side_effect=fail_receipt
        ):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "injected receipt publication failure",
            ):
                distribution.prepare_local_workspace(package, workspace)
        self.assertFalse(receipt_path.exists())
        for relative, expected in prior.items():
            self.assertEqual((workspace / relative).read_bytes(), expected)

        distribution.prepare_local_workspace(package, workspace)
        victim_relative = sorted(extracted)[0]
        victim = workspace / victim_relative
        victim.unlink()
        victim.symlink_to(workspace / sorted(extracted)[1])
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "traverses a symlink"
        ):
            distribution.prepare_local_workspace(package, workspace)
        victim.unlink()
        corrupted = Path(self.temporary.name) / "corrupt.evenota"
        damaged = bytearray(image)
        damaged[-1] ^= 1
        corrupted.write_bytes(damaged)
        with self.assertRaisesRegex(distribution.CommunityBundleError, "not authenticated"):
            distribution.authenticate_official_package(corrupted)


class PublicExportPreflightTests(unittest.TestCase):
    def test_repository_index_tracks_no_g2_temp_artifacts(self) -> None:
        repository = distribution.REPOSITORY_ROOT.resolve()
        probe = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=repository,
            text=True,
            capture_output=True,
            check=False,
        )
        if (
            probe.returncode != 0
            or Path(probe.stdout.strip()).resolve() != repository
        ):
            self.skipTest("history-free extracted archive has no repository index")
        tracked = subprocess.run(
            ["git", "ls-files", "-z", "--", "g2"],
            cwd=repository,
            capture_output=True,
            check=True,
        ).stdout.split(b"\0")
        leaked = []
        for encoded in tracked:
            if not encoded:
                continue
            path = PurePosixPath(encoded.decode("utf-8"))
            if (
                len(path.parts) >= 2
                and path.parts[0] == "g2"
                and path.parts[1].startswith(".tmp-")
            ):
                leaked.append(path.as_posix())
        self.assertEqual(leaked, [], "tracked G2 temporary artifacts returned")

    def test_nemavg_public_inventory_contains_complete_route_and_evidence(self) -> None:
        inventory = {
            destination for _, destination in distribution._selected_records()
        }
        self.assertEqual(
            {path for path in inventory if "nemavg" in path.casefold()},
            set(distribution.NEMAVG_PUBLIC_MEMBERS),
        )
        distribution._verify_public_inventory(inventory)

        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "required community source is absent",
        ):
            distribution._verify_public_inventory(
                inventory - {distribution.NEMAVG_PRODUCTION_SOURCE_MEMBER}
            )
        for path in distribution.NEMAVG_FORBIDDEN_PUBLIC_MEMBERS:
            with self.subTest(path=path), self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "unsafe NemaVG endpoint/integrator member selected",
            ):
                distribution._verify_public_inventory(inventory | {path})
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "NemaVG community member census changed",
        ):
            distribution._verify_public_inventory(
                inventory
                | {
                    "g2/components/shared/lvgl/"
                    "runtime_nemavg_unreviewed_endpoint.c"
                }
            )

    def test_nemavg_sanitized_overlay_contains_exact_complete_route(self) -> None:
        raw = (
            distribution.REPOSITORY_ROOT
            / distribution.SANITIZED_APOLLO_OVERLAY
        ).read_bytes()
        overlay = json.loads(distribution._sanitize_apollo_overlay(raw))
        distribution._verify_sanitized_apollo_overlay(overlay)
        nema_sites = [
            site for site in overlay["patch_sites"]
            if site.get("runtime_address")
            in (
                distribution.NEMAVG_ENDPOINT_ENTRIES
                | {distribution.NEMAVG_COORDINATOR_PATCH["runtime_address"]}
            )
            or site.get("target_function")
            in distribution.NEMAVG_ROUTE_TARGET_FUNCTIONS
        ]
        self.assertEqual(nema_sites, list(distribution.NEMAVG_PRODUCTION_PATCHES))

        endpoint_route = json.loads(json.dumps(overlay))
        endpoint_route["patch_sites"].append({
            **distribution.NEMAVG_COORDINATOR_PATCH,
            "name": "unsafe_start_endpoint",
            "runtime_address": min(distribution.NEMAVG_ENDPOINT_ENTRIES),
            "target_function": "open_cfw_nemavg_draw_start_cap_endpoint",
        })
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "NemaVG production patch route changed",
        ):
            distribution._verify_sanitized_apollo_overlay(endpoint_route)

        endpoint_function = json.loads(json.dumps(overlay))
        endpoint_function["functions"].append(
            "open_cfw_nemavg_draw_end_cap_endpoint"
        )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "NemaVG production function census changed",
        ):
            distribution._verify_sanitized_apollo_overlay(endpoint_function)

        candidate_route = json.loads(json.dumps(overlay))
        coordinator_leaf = next(
            leaf for leaf in candidate_route["relocated_leaves"]
            if leaf.get("function") == distribution.NEMAVG_COORDINATOR_FUNCTION
        )
        coordinator_leaf["source"]["path"] = (
            "components/shared/lvgl/runtime_nemavg_stroke_caps_candidate.c"
        )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "NemaVG nonproduction candidate source is production-routed",
        ):
            distribution._verify_sanitized_apollo_overlay(candidate_route)

        endpoint_source = json.loads(json.dumps(overlay))
        endpoint_source["relocated_leaves"].append({
            "function": "unrelated_name",
            "source": {
                "path": (
                    "components/apollo_main/core_overlay/"
                    "runtime_nemavg_stroke_cap_endpoints.c"
                )
            },
        })
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "NemaVG production source route census changed",
        ):
            distribution._verify_sanitized_apollo_overlay(endpoint_source)

    def test_nemavg_public_source_and_routed_evidence_are_cross_bound(self) -> None:
        payload = {
            path: (distribution.REPOSITORY_ROOT / path).read_bytes()
            for path in distribution.NEMAVG_PUBLIC_MEMBERS
        }
        overlay = json.loads(distribution._sanitize_apollo_overlay(
            (
                distribution.REPOSITORY_ROOT
                / distribution.SANITIZED_APOLLO_OVERLAY
            ).read_bytes()
        ))
        distribution._verify_nemavg_public_boundary(payload, overlay)

        changed_source = dict(payload)
        changed_source[distribution.NEMAVG_PRODUCTION_SOURCE_MEMBER] += b"\n"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "reviewed production source identity changed",
        ):
            distribution._verify_nemavg_public_boundary(changed_source, overlay)

        changed_summary = dict(payload)
        summary = json.loads(
            changed_summary[distribution.NEMAVG_CANDIDATE_SUMMARY_MEMBER]
        )
        summary["candidate"]["production_routed"] = False
        changed_summary[distribution.NEMAVG_CANDIDATE_SUMMARY_MEMBER] = (
            json.dumps(summary).encode()
        )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "candidate boundary semantics changed",
        ):
            distribution._verify_nemavg_public_boundary(changed_summary, overlay)

    def test_public_docs_pin_exact_private_history_payloads(self) -> None:
        root_readme = (distribution.REPOSITORY_ROOT / "README.md").read_text(
            encoding="utf-8"
        )
        community_guide = (
            distribution.ROOT / "docs/community-source-distribution.md"
        ).read_text(encoding="utf-8")
        archive_readme = (
            distribution.ROOT / "docs/community-archive-README.md"
        ).read_text(encoding="utf-8")
        documents = (root_readme, community_guide, archive_readme)
        normalized_documents = tuple(
            " ".join(
                line.removeprefix("> ").strip()
                for line in document.splitlines()
            )
            for document in documents
        )
        required = (
            "history-free public artifact",
            "52 `g2/.tmp-*` paths and descendants",
            "108,601,986 bytes",
            "official-derived firmware variants",
            "g2/.tmp-pt-working-base.bin",
            "g2/.tmp-pt-working-base-linux.bin",
            "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
        )
        for document in normalized_documents:
            with self.subTest(document=document[:64]):
                for text in required:
                    self.assertIn(text, document)
        root_flat, community_flat, archive_flat = normalized_documents
        self.assertIn("must not be published, mirrored", community_flat)
        self.assertIn("requires separate authorization", root_flat)
        self.assertIn("separately authorized history rewrite", archive_flat)

    def test_local_temp_and_hydration_state_is_ignored(self) -> None:
        ignore = (distribution.REPOSITORY_ROOT / ".gitignore").read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertIn("/g2/.tmp-*", ignore)
        self.assertIn("/g2/.open-cfw-local-hydration.json", ignore)

    def test_public_archive_gitignore_is_exact_mit_infrastructure_member(self) -> None:
        gitignore_path = distribution.REPOSITORY_ROOT / ".gitignore"
        gitignore = gitignore_path.read_bytes()
        self.assertIn(".gitignore", distribution.EXPLICIT_REPOSITORY_FILES)
        self.assertIn(".gitignore", distribution.PROJECT_INFRASTRUCTURE_MIT_MEMBERS)
        self.assertTrue(distribution._allowed_source_file(gitignore_path))
        self.assertTrue(
            distribution._allowed_archive_file(PurePosixPath(".gitignore"))
        )
        self.assertFalse(
            distribution._allowed_archive_file(PurePosixPath("g2/.gitignore"))
        )
        archive_info = zipfile.ZipInfo(".gitignore", (1980, 1, 1, 0, 0, 0))
        archive_info.create_system = 3
        archive_info.compress_type = zipfile.ZIP_STORED
        archive_info.external_attr = (0o100644 << 16)
        distribution._validate_archive_info(archive_info)
        self.assertEqual(distribution._bundle_payload(gitignore_path, gitignore), gitignore)
        distribution._preflight_public_export_member(".gitignore", gitignore)
        distribution._verify_public_payload(".gitignore", gitignore)

        base_payload = {
            path: (distribution.REPOSITORY_ROOT / path).read_bytes()
            for path in distribution.EXPLICIT_REPOSITORY_FILES
            if path != ".gitignore"
        }
        base_ledger, base_closure = distribution._bundle_member_license_ledger(
            base_payload
        )
        payload = {**base_payload, ".gitignore": gitignore}
        ledger, closure = distribution._bundle_member_license_ledger(payload)
        repeated_ledger, repeated_closure = (
            distribution._bundle_member_license_ledger(payload)
        )
        self.assertEqual(len(payload), len(base_payload) + 1)
        self.assertEqual(len(ledger), len(base_ledger) + 1)
        self.assertEqual(ledger, repeated_ledger)
        self.assertEqual(closure, repeated_closure)
        self.assertEqual(
            closure["project_infrastructure_mit_members"],
            base_closure["project_infrastructure_mit_members"] + 1,
        )
        row = next(item for item in ledger if item["path"] == ".gitignore")
        self.assertEqual(row["sha256"], hashlib.sha256(gitignore).hexdigest())
        self.assertEqual(row["license"], "MIT")
        self.assertEqual(row["member_class"], "project_infrastructure")
        self.assertEqual(
            row["basis"],
            "authenticated-root-mit-project-infrastructure-scope",
        )

    def test_extracted_archive_gitignore_blocks_local_stock_and_build_state(self) -> None:
        official_provider_paths = (
            "g2/blobs/official/g2-2.2.6.10/firmware_codec.bin",
            "g2/blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin",
            "g2/blobs/official/g2-2.2.6.10/firmware_touch.bin",
            "g2/blobs/official/g2-2.2.6.10/firmware_box.bin",
            "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin",
            "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin",
        )
        ignored_paths = (
            *official_provider_paths,
            f"g2/{distribution.HYDRATION_RECEIPT}",
            "g2/build/source/openCFW-g2.evenota",
            "g2/build-linux-probe/source/openCFW-g2.evenota",
            "g2/manifests/.tmp-canonical-observation.json",
            "g2/components/apollo_main/.tmp-profile/object.o",
            "g2/manifests/.open-cfw-canonical-output-ring.lock",
            "g2/components/.open-cfw-canonical-apply.lock",
        )
        addable_paths = (
            ".gitignore",
            "SECURITY.md",
            "g2/tools/open_cfw.py",
            "g2/blobs/official/g2-2.2.6.10/PROVENANCE.md",
        )
        with tempfile.TemporaryDirectory(prefix="opencfw-public-ignore-") as temporary:
            extracted = Path(temporary)
            (extracted / ".gitignore").write_bytes(
                (distribution.REPOSITORY_ROOT / ".gitignore").read_bytes()
            )
            for relative in (*ignored_paths, *addable_paths[1:]):
                target = extracted / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b"representative local state\n")
            subprocess.run(
                ["git", "init", "-q", str(extracted)],
                check=True,
                capture_output=True,
            )

            ignored = subprocess.run(
                [
                    "git", "-C", str(extracted), "check-ignore", "--no-index",
                    "--stdin",
                ],
                input="\n".join(ignored_paths) + "\n",
                text=True,
                check=True,
                capture_output=True,
            )
            self.assertEqual(ignored.stdout.splitlines(), list(ignored_paths))
            addable = subprocess.run(
                [
                    "git", "-C", str(extracted), "check-ignore", "--no-index",
                    "--stdin",
                ],
                input="\n".join(addable_paths) + "\n",
                text=True,
                check=False,
                capture_output=True,
            )
            self.assertEqual(addable.returncode, 1)
            self.assertEqual(addable.stdout, "")
            dry_run = subprocess.run(
                ["git", "-C", str(extracted), "add", "--dry-run", "--", *addable_paths],
                text=True,
                check=True,
                capture_output=True,
            )
            for relative in addable_paths:
                self.assertIn(f"add '{relative}'", dry_run.stdout)

    def test_rejects_temp_binary_and_hydration_paths(self) -> None:
        for unsafe_path, message in (
            ("g2/.tmp-observation/renamed.md", "temporary/build path"),
            ("g2/docs/.tmp-renamed.md", "temporary/build path"),
            ("g2/docs/firmware.exe", "executable/binary suffix"),
            ("g2/docs/firmware.bin", "executable/binary suffix"),
            (
                f"g2/{distribution.HYDRATION_RECEIPT}",
                "local hydration receipt",
            ),
        ):
            with self.subTest(path=unsafe_path):
                with self.assertRaisesRegex(
                    distribution.CommunityBundleError, message
                ):
                    distribution._preflight_public_export_member(
                        unsafe_path, b"SPDX-License-Identifier: MIT\n"
                    )
        self.assertFalse(
            distribution._allowed_source_file(
                distribution.ROOT / distribution.HYDRATION_RECEIPT
            )
        )

    def test_rejects_all_official_hashes_when_renamed(self) -> None:
        for digest in distribution.FORBIDDEN_OFFICIAL_FIRMWARE_SHA256:
            with self.subTest(digest=digest):
                with self.assertRaisesRegex(
                    distribution.CommunityBundleError,
                    "official firmware payload embedded",
                ):
                    distribution._preflight_public_export_member(
                        "g2/docs/innocent-renamed-source.md",
                        b"not used when exercising an authenticated digest",
                        digest=digest,
                    )

    def test_official_hash_denylist_cannot_drift_with_mutable_manifest(self) -> None:
        manifest = {
            "components": [
                {
                    "name": name,
                    "provider": {
                        "kind": kind,
                        "path": path,
                        "size": size,
                        "sha256": digest,
                    },
                }
                for name, kind, path, size, digest
                in distribution.OFFICIAL_COMPONENT_CONTRACT
            ]
        }
        with mock.patch.object(
            distribution.open_cfw, "load_manifest", return_value=manifest
        ):
            self.assertEqual(
                distribution._official_provider_hashes(),
                set(distribution.OFFICIAL_PAYLOAD_SHA256),
            )
        manifest["components"][0]["provider"]["sha256"] = "0" * 64
        with mock.patch.object(
            distribution.open_cfw, "load_manifest", return_value=manifest
        ):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "provider name/path/identity contract changed",
            ):
                distribution._official_provider_hashes()

    def test_public_docs_state_the_history_binary_and_hardware_boundaries(self) -> None:
        community = (
            distribution.ROOT / "docs/community-source-distribution.md"
        ).read_text(encoding="utf-8")
        licensing = (
            distribution.ROOT / "docs/release-licensing-and-redistribution.md"
        ).read_text(encoding="utf-8")
        community_flat = " ".join(
            line.removeprefix("> ").strip()
            for line in community.splitlines()
        )
        licensing_flat = " ".join(licensing.split())
        for required in (
            "official-payload-free, history-free public artifact",
            "52 `g2/.tmp-*` paths and descendants totaling 108,601,986 bytes",
            "including official-derived firmware variants",
            "contains the now-deleted exact official-payload copies",
            "Once a recipient hydrates an extracted tree",
            "Hardware qualification is blocked by unavailable physical evidence",
        ):
            self.assertIn(required, community_flat)
        for required in (
            "Only the deterministic source ZIP",
            "existing full Git history is not safe to publish or mirror",
            "Public binary redistribution remains unauthorized by this project",
            "Hardware qualification is separately blocked by unavailable physical evidence",
        ):
            self.assertIn(required, licensing_flat)

    def test_json_include_and_atomic_paths_reject_links(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="community-path-safety-", dir=distribution.ROOT / "tests"
        ) as temporary:
            root = Path(temporary)
            real_json = root / "real.json"
            real_json.write_text('{"ok": true}\n', encoding="utf-8")
            json_link = root / "link.json"
            json_link.symlink_to(real_json)
            with self.assertRaisesRegex(
                distribution.CommunityBundleError, "opened safely|stabilize"
            ):
                distribution._read_json_path(json_link)

            header = root / "real.h"
            header.write_text("#define VALUE 1\n", encoding="utf-8")
            (root / "alias.h").symlink_to(header)
            source = root / "source.c"
            source.write_text('#include "alias.h"\n', encoding="utf-8")
            with self.assertRaisesRegex(
                distribution.CommunityBundleError, "opened safely"
            ):
                distribution._local_include_closure({source})

            target = root / "target.txt"
            target.write_bytes(b"preserve\n")
            output = root / "output.txt"
            output.symlink_to(target)
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "atomic write target could not be opened safely",
            ):
                distribution._atomic_write_unique(output, b"replacement\n")
            self.assertEqual(target.read_bytes(), b"preserve\n")

            output.unlink()
            alias = root / "target-hardlink.txt"
            os.link(target, alias)
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "not an independent regular file",
            ):
                distribution._atomic_write_unique(target, b"replacement\n")
            self.assertEqual(target.read_bytes(), b"preserve\n")

            alias.unlink()
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "appeared before publication",
            ):
                distribution._atomic_write_unique(
                    target, b"replacement\n", expected_prior=None
                )
            self.assertEqual(target.read_bytes(), b"preserve\n")
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "changed before publication",
            ):
                distribution._atomic_write_unique(
                    target, b"replacement\n", expected_prior=b"older\n"
                )
            self.assertEqual(target.read_bytes(), b"preserve\n")


class CommunitySmokeImportClosureTests(unittest.TestCase):
    """Keep smoke entry points importable without private repository inputs."""

    def test_local_preflight_reports_an_exact_reviewed_environment(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="community-preflight-",
            dir=distribution._physical_temporary_root(),
        ) as temporary:
            include = Path(temporary) / "resource/include"
            include.mkdir(parents=True)

            def locate(command):
                return {
                    "/reviewed/clang": "/reviewed/clang",
                    "gmake": "/reviewed/gmake",
                }.get(command)

            def run(command, **_kwargs):
                if command == ["/reviewed/gmake", "--version"]:
                    return SimpleNamespace(
                        returncode=0, stdout="GNU Make 4.4.1\n", stderr=""
                    )
                if command == ["/reviewed/clang", "--version"]:
                    return SimpleNamespace(
                        returncode=0,
                        stdout="Apple clang version 21.0.0 (reviewed)\n",
                        stderr="",
                    )
                if command == [
                    "/reviewed/clang", "--no-default-config",
                    "-print-resource-dir",
                ]:
                    return SimpleNamespace(
                        returncode=0,
                        stdout=f"{include.parent}\n",
                        stderr="",
                    )
                self.fail(f"unexpected preflight command: {command}")

            with (
                mock.patch.object(distribution.shutil, "which", side_effect=locate),
                mock.patch.object(distribution.subprocess, "run", side_effect=run),
            ):
                report = distribution.preflight_local_environment(
                    "/reviewed/clang", "apple-clang", "gmake"
                )
            self.assertEqual(report["toolchain_profile"], "apple-clang")
            self.assertEqual(report["make"]["version"], "GNU Make 4.4.1")
            self.assertEqual(report["clang"]["resource_include"], str(include))
            self.assertEqual(report["hardware_operations"], [])

    def test_preflight_rejects_profile_mismatch_and_non_gnu_make(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="community-preflight-reject-",
            dir=distribution._physical_temporary_root(),
        ) as temporary:
            include = Path(temporary) / "resource/include"
            include.mkdir(parents=True)

            def locate(command):
                return command if command in ("/clang", "/make") else None

            def run(command, **_kwargs):
                if command == ["/make", "--version"]:
                    return SimpleNamespace(
                        returncode=0, stdout="GNU Make 4.4\n", stderr=""
                    )
                if command == ["/clang", "--version"]:
                    return SimpleNamespace(
                        returncode=0,
                        stdout="Apple clang version 21.0.0\n",
                        stderr="",
                    )
                return SimpleNamespace(
                    returncode=0, stdout=f"{include.parent}\n", stderr=""
                )

            with (
                mock.patch.object(distribution.shutil, "which", side_effect=locate),
                mock.patch.object(distribution.subprocess, "run", side_effect=run),
            ):
                with self.assertRaisesRegex(
                    distribution.CommunityBundleError,
                    "does not match linux-clang",
                ):
                    distribution.preflight_local_environment(
                        "/clang", "linux-clang", "/make"
                    )

            def bsd_run(command, **_kwargs):
                return SimpleNamespace(
                    returncode=0, stdout="BSD make 20260829\n", stderr=""
                )

            with (
                mock.patch.object(distribution.shutil, "which", side_effect=locate),
                mock.patch.object(distribution.subprocess, "run", side_effect=bsd_run),
            ):
                with self.assertRaisesRegex(
                    distribution.CommunityBundleError, "requires GNU make"
                ):
                    distribution.preflight_local_environment(
                        "/clang", "apple-clang", "/make"
                    )

    def test_smoke_commands_propagate_compiler_and_profile(self) -> None:
        commands = distribution._community_smoke_commands(
            "/reviewed/python",
            clang="/reviewed/clang",
            toolchain_profile="linux-clang",
        )
        for command in commands[1:3]:
            self.assertEqual(command[-4:], [
                "--clang", "/reviewed/clang",
                "--toolchain-profile", "linux-clang",
            ])
        self.assertEqual(commands[3][-1], "linux-clang")
        self.assertEqual(commands[5][-1], "linux-clang")

    def test_make_recipe_propagates_selected_compiler_and_profile(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        recipe = makefile.split("community-local-build:", 1)[1].split(
            "\ncommunity-source-bundle:", 1
        )[0]
        self.assertIn("community-local-preflight", makefile)
        self.assertEqual(recipe.count('--clang "$(OPENCFW_CLANG)"'), 2)
        self.assertEqual(
            recipe.count('--toolchain-profile "$(OPENCFW_TOOLCHAIN_PROFILE)"'),
            4,
        )

    def test_internal_temp_root_has_no_symlinked_lexical_prefix(self) -> None:
        root = distribution._physical_temporary_root()
        self.assertEqual(root, Path(tempfile.gettempdir()).resolve(strict=True))
        cursor = root
        while cursor != cursor.parent:
            self.assertFalse(cursor.is_symlink())
            cursor = cursor.parent

    def test_extracted_gate_and_smoke_test_modules_have_exact_parity(self) -> None:
        expected = (
            "tests.test_analyze_g2_case_source_image",
            "tests.test_analyze_em9305_record_package",
            "tests.test_em9305_record_package",
            "tests.test_runtime_nemavg_stroke_caps_candidate",
            "tests.test_runtime_clkmgr_divider_candidate",
            "tests.test_apply_g2_canonical_observations",
            "tests.test_core_canonical_recorder_security",
        )
        self.assertEqual(
            distribution.COMMUNITY_LOCAL_BUILD_TEST_MODULES, expected
        )
        self.assertEqual(len(set(expected)), len(expected))

        smoke_test_command = distribution._community_smoke_commands(
            "/reviewed/python"
        )[0]
        self.assertEqual(
            smoke_test_command,
            ["/reviewed/python", "-m", "unittest", "-v", *expected],
        )

        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        recipe = makefile.split("community-local-build:", 1)[1]
        recipe = recipe.split(
            "\n\t$(PYTHON) components/bootloader/core_overlay/build_component.py",
            1,
        )[0]
        make_modules = tuple(
            token
            for token in recipe.replace("\\\n", " ").split()
            if token.startswith("tests.")
        )
        self.assertEqual(make_modules, expected)
        self.assertEqual(len(set(make_modules)), len(make_modules))

        expected_entries = {
            f"g2/{module.replace('.', '/')}.py" for module in expected
        }
        smoke_test_entries = {
            path
            for path in distribution.SMOKE_PYTHON_IMPORT_CLOSURE
            if path.startswith("g2/tests/")
        }
        self.assertEqual(smoke_test_entries, expected_entries)

    @staticmethod
    def payload() -> dict[str, bytes]:
        paths = set(distribution.SMOKE_PYTHON_IMPORT_CLOSURE)
        paths.update(
            dependency
            for contract in
            distribution.SMOKE_PYTHON_IMPORT_CLOSURE.values()
            for dependency in contract["local"].values()
        )
        return {
            path: (distribution.REPOSITORY_ROOT / path).read_bytes()
            for path in paths
        }

    def test_public_smoke_import_closure_is_complete(self) -> None:
        distribution._verify_smoke_python_import_closure(self.payload())

    def test_missing_public_smoke_dependency_fails_closed(self) -> None:
        payload = self.payload()
        dependency = next(
            dependency
            for contract in distribution.SMOKE_PYTHON_IMPORT_CLOSURE.values()
            for dependency in contract["local"].values()
        )
        del payload[dependency]
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "community smoke Python dependency is absent",
        ):
            distribution._verify_smoke_python_import_closure(payload)

    def test_unlisted_smoke_import_fails_closed(self) -> None:
        payload = self.payload()
        entry = "g2/tests/test_runtime_nemavg_stroke_caps_candidate.py"
        payload[entry] += b"\nimport open_cfw\n"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "community smoke Python import contract changed",
        ):
            distribution._verify_smoke_python_import_closure(payload)

    def test_function_local_unlisted_smoke_import_fails_closed(self) -> None:
        payload = self.payload()
        entry = "g2/tests/test_runtime_nemavg_stroke_caps_candidate.py"
        payload[entry] += b"\ndef hidden_dependency():\n    import open_cfw\n"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "community smoke Python import contract changed",
        ):
            distribution._verify_smoke_python_import_closure(payload)

    def test_smoke_import_contract_drift_fails_closed(self) -> None:
        payload = self.payload()
        entry = "g2/tests/test_runtime_clkmgr_divider_candidate.py"
        payload[entry] = payload[entry].replace(
            b"import verify_g2_clkmgr_divider_public as verifier",
            b"import json as verifier",
        )
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "community smoke Python import contract changed",
        ):
            distribution._verify_smoke_python_import_closure(payload)


class CommunityPublicEvidenceStaticTests(unittest.TestCase):
    """Bind public evidence without creating a persistent archive."""

    @staticmethod
    def evidence_payload() -> dict[str, bytes]:
        members = distribution._repository_public_evidence_members()
        return {
            path: (distribution.REPOSITORY_ROOT / path).read_bytes()
            for path in members
        }

    def test_touch_direct_input_and_receipt_censuses_are_exact(self) -> None:
        payload = self.evidence_payload()
        distribution._verify_public_evidence_receipts(payload)
        summary = json.loads(
            payload[distribution.TOUCH_FINAL_CLASSIFICATION_RECEIPT]
        )
        touch_members, touch_digests = (
            distribution._touch_admission_members_from_summary(summary)
        )
        public_inputs = (
            distribution._touch_public_analysis_inputs_from_summary(summary)
        )
        self.assertEqual(len(touch_members), 26)
        self.assertEqual(len(public_inputs), 68)
        self.assertEqual(
            set(touch_members), set(distribution.TOUCH_ADMISSION_RECEIPT_MEMBERS)
        )
        self.assertTrue(set(touch_members) <= set(public_inputs))
        self.assertTrue(
            all(touch_digests[path] == public_inputs[path] for path in touch_members)
        )
        self.assertNotIn(
            f"g2/{distribution.TOUCH_OFFICIAL_DONOR_INPUT}", payload
        )
        self.assertFalse(
            any(path.endswith("-unavailable.tsv") for path in payload)
        )

    def test_public_evidence_omission_drift_and_unavailable_fail_closed(self) -> None:
        payload = self.evidence_payload()
        missing = dict(payload)
        missing.pop(next(iter(distribution.COMPLETION_REPORT_MEMBERS)))
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "public evidence receipt is absent",
        ):
            distribution._verify_public_evidence_receipts(missing)

        missing_input = dict(payload)
        missing_input.pop(distribution.TOUCH_PUBLIC_ANALYZER_MEMBERS[0])
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "Touch public direct-input identity changed",
        ):
            distribution._verify_public_evidence_receipts(missing_input)

        drifted = dict(payload)
        admission = distribution.TOUCH_ADMISSION_RECEIPT_MEMBERS[0]
        drifted[admission] += b"\n"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "Touch admission receipt identity changed",
        ):
            distribution._verify_public_evidence_receipts(drifted)

        unavailable = dict(payload)
        unavailable[
            "g2/tools/manifests/g2-touch-cat2-source-admission5-unavailable.tsv"
        ] = b"status\tunavailable\n"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "excluded Touch unavailable receipt",
        ):
            distribution._verify_public_evidence_receipts(unavailable)

    def test_every_evidence_receipt_is_mit_generated_or_rejected(self) -> None:
        payload = {
            "LICENSE": (distribution.REPOSITORY_ROOT / "LICENSE").read_bytes(),
            **{
                path: (distribution.REPOSITORY_ROOT / path).read_bytes()
                for path in distribution.PUBLIC_EVIDENCE_RECEIPT_MEMBERS
            },
        }
        ledger, closure = distribution._bundle_member_license_ledger(payload)
        rows = {row["path"]: row for row in ledger}
        for path in distribution.PUBLIC_EVIDENCE_RECEIPT_MEMBERS:
            self.assertEqual(rows[path]["license"], "MIT")
            self.assertEqual(
                rows[path]["member_class"], "project_generated_receipt"
            )
        self.assertEqual(
            rows[distribution.EM9305_PREDECISION_INPUT_MEMBER]["basis"],
            "authenticated-root-mit-generated-pre-decision-input-scope",
        )
        for path in distribution.EM9305_FINAL_READINESS_IDENTITIES:
            self.assertEqual(
                rows[path]["basis"],
                "authenticated-root-mit-generated-receipt-scope",
            )
        self.assertEqual(
            closure["project_generated_receipt_members"],
            len(distribution.PUBLIC_EVIDENCE_RECEIPT_MEMBERS),
        )

        target = distribution.COMPLETION_REPORT_MEMBERS[0]
        reduced = set(distribution.PROJECT_GENERATED_RECEIPT_MEMBERS)
        reduced.remove(target)
        with mock.patch.object(
            distribution, "PROJECT_GENERATED_RECEIPT_MEMBERS", reduced
        ):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "member license is unresolved",
            ):
                distribution._bundle_member_license_ledger({
                    "LICENSE": payload["LICENSE"],
                    target: payload[target],
                })

    def test_final_em9305_receipts_are_exact_and_semantically_current(self) -> None:
        payload = self.evidence_payload()
        distribution._verify_em9305_public_readiness_receipts(payload)
        for path, (size, digest) in (
            distribution.EM9305_FINAL_READINESS_IDENTITIES.items()
        ):
            self.assertIn(path, distribution.PUBLIC_EVIDENCE_RECEIPT_MEMBERS)
            self.assertEqual(len(payload[path]), size)
            self.assertEqual(hashlib.sha256(payload[path]).hexdigest(), digest)
        self.assertIn(
            distribution.EM9305_PREDECISION_INPUT_MEMBER,
            distribution.PUBLIC_EVIDENCE_RECEIPT_MEMBERS,
        )
        summary_path = (
            "g2/tools/manifests/em9305-final-source-readiness-summary.json"
        )
        summary = json.loads(payload[summary_path])
        self.assertEqual(summary["hardware_operations"], [])
        self.assertNotIsInstance(summary["hardware_operations"], bool)
        self.assertEqual(summary["unclassified_bytes"], 0)
        self.assertEqual(summary["residual_span_count"], 175)
        self.assertFalse(summary["source_complete"])
        self.assertFalse(summary["release"])
        self.assertTrue(
            summary["metaware_runtime_audit"]["arcv2_em_target_compiled"]
        )
        self.assertEqual(
            summary["metaware_runtime_audit"]
            ["arcv2_em_forbidden_runtime_imports"],
            [],
        )
        self.assertEqual(
            summary["qpc_hook_provider_audit"]["software_provider_gaps"],
            [],
        )
        self.assertTrue(
            summary["qpc_hook_provider_audit"]
            ["software_provider_source_available"],
        )
        self.assertEqual(
            summary["qpc_hook_provider_audit"]["hardware_dependent_providers"],
            ["PalUartResume", "VoltMon_DoMeasurement"],
        )
        self.assertTrue(
            summary["qpc_supporting_audit"]["arcv2_em_target_linked"]
        )
        self.assertEqual(
            summary["qpc_supporting_audit"]["arcv2_em_undefined_symbols"],
            [],
        )
        self.assertTrue(
            summary["deployment_package_audit"]
            ["stock_roundtrip_byte_exact"]
        )
        self.assertTrue(
            summary["deployment_package_audit"]
            ["software_package_complete"]
        )
        self.assertFalse(
            summary["deployment_package_audit"]["source_image_complete"]
        )
        self.assertFalse(
            summary["deployment_package_audit"]["production_routed"]
        )
        arc_receipt = payload[distribution.EM9305_ARC_BUILD_RECEIPT]
        self.assertEqual(
            (len(arc_receipt), hashlib.sha256(arc_receipt).hexdigest()),
            distribution.EM9305_ARC_BUILD_RECEIPT_IDENTITY,
        )
        qpc_receipt = payload[distribution.EM9305_QPC_BUILD_RECEIPT]
        self.assertEqual(
            (len(qpc_receipt), hashlib.sha256(qpc_receipt).hexdigest()),
            distribution.EM9305_QPC_BUILD_RECEIPT_IDENTITY,
        )
        package_receipt = payload[
            distribution.EM9305_RECORD_PACKAGE_RECEIPT]
        self.assertEqual(
            (len(package_receipt),
             hashlib.sha256(package_receipt).hexdigest()),
            distribution.EM9305_RECORD_PACKAGE_RECEIPT_IDENTITY,
        )

        mutated = dict(payload)
        summary["hardware_operations"] = True
        mutated_data = (
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        ).encode()
        mutated[summary_path] = mutated_data
        identities = dict(distribution.EM9305_FINAL_READINESS_IDENTITIES)
        identities[summary_path] = (
            len(mutated_data), hashlib.sha256(mutated_data).hexdigest()
        )
        with mock.patch.object(
            distribution, "EM9305_FINAL_READINESS_IDENTITIES", identities
        ):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError,
                "final EM9305 readiness semantics changed",
            ):
                distribution._verify_em9305_public_readiness_receipts(mutated)

        mutated = dict(payload)
        current_touch = (
            "g2/tools/manifests/"
            "g2-touch-current-source-readiness-summary.json"
        )
        touch_summary = json.loads(mutated[current_touch])
        touch_summary["hardware_operations"] = False
        mutated[current_touch] = json.dumps(touch_summary).encode()
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "public current summary exposes boolean hardware_operations",
        ):
            distribution._verify_em9305_public_readiness_receipts(mutated)


class CommunityCompletionAssessmentStaticTests(unittest.TestCase):
    @staticmethod
    def payload() -> dict[str, bytes]:
        return {
            path: (distribution.REPOSITORY_ROOT / path).read_bytes()
            for path in distribution.COMPLETION_REPORT_MEMBERS
        }

    @staticmethod
    def json_value(payload: dict[str, bytes], path: str) -> dict:
        return json.loads(payload[path])

    @staticmethod
    def replace_json(
        payload: dict[str, bytes], path: str, value: dict
    ) -> None:
        payload[path] = (
            json.dumps(value, indent=2, sort_keys=True) + "\n"
        ).encode()

    def test_triplet_semantics_and_hash_binding_are_exact(self) -> None:
        payload = self.payload()
        binding = distribution._completion_assessment_binding(payload)
        distribution._verify_completion_assessment_binding(payload, binding)
        assessment = self.json_value(
            payload, distribution.COMPLETION_REPORT_MEMBERS[0]
        )
        artifact = self.json_value(
            payload, distribution.COMPLETION_REPORT_MEMBERS[1]
        )
        self.assertEqual(artifact["gate_snapshot"], assessment["gates"])
        self.assertEqual(assessment["hardware_operations"], [])
        self.assertEqual(artifact["hardware_operations"], [])
        self.assertEqual(
            set(assessment["licensing"]["unresolved_binary_authority"]),
            {
                "apollo_main", "apollo_bootloader", "codec",
                "ble_em9305", "touch", "case",
            },
        )
        self.assertTrue(assessment["source_inputs"])
        self.assertEqual(
            len({row["path"] for row in assessment["source_inputs"]}),
            len(assessment["source_inputs"]),
        )
        self.assertFalse(assessment["touch_admission"]["production_routed"])

    def test_triplet_omission_and_byte_drift_fail_closed(self) -> None:
        payload = self.payload()
        binding = distribution._completion_assessment_binding(payload)
        for path in distribution.COMPLETION_REPORT_MEMBERS:
            with self.subTest(missing=path):
                missing = dict(payload)
                missing.pop(path)
                with self.assertRaises(distribution.CommunityBundleError):
                    distribution._completion_assessment_binding(missing)
        drifted_report = dict(payload)
        drifted_report[distribution.COMPLETION_REPORT_MEMBERS[2]] += b"\n"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "completion artifact member identity changed",
        ):
            distribution._verify_completion_assessment_binding(
                drifted_report, binding
            )

    def test_release_hardware_authority_and_touch_mutations_fail_closed(self) -> None:
        assessment_path, artifact_path, _report_path = (
            distribution.COMPLETION_REPORT_MEMBERS
        )
        base = self.payload()

        mutations: dict[str, list[tuple[str, dict]]] = {}
        assessment = self.json_value(base, assessment_path)
        assessment["gates"]["release_authorized"] = True
        artifact = self.json_value(base, artifact_path)
        artifact["gate_snapshot"] = dict(assessment["gates"])
        mutations["release gate"] = [
            (assessment_path, assessment),
            (artifact_path, artifact),
        ]

        assessment = self.json_value(base, assessment_path)
        assessment["hardware_operations"] = ["flash"]
        mutations["hardware policy"] = [(assessment_path, assessment)]

        assessment = self.json_value(base, assessment_path)
        assessment["licensing"]["unresolved_binary_authority"].pop()
        mutations["authority.*census"] = [(assessment_path, assessment)]

        assessment = self.json_value(base, assessment_path)
        assessment["source_inputs"].append(dict(assessment["source_inputs"][0]))
        mutations["source-input paths"] = [(assessment_path, assessment)]

        assessment = self.json_value(base, assessment_path)
        assessment["touch_admission"]["production_routed"] = True
        mutations["Touch provenance"] = [(assessment_path, assessment)]

        artifact = self.json_value(base, artifact_path)
        artifact["gate_snapshot"]["source_complete"] = True
        mutations["gate snapshot"] = [(artifact_path, artifact)]

        for expected, changes in mutations.items():
            with self.subTest(mutation=expected):
                payload = dict(base)
                for path, value in changes:
                    self.replace_json(payload, path, value)
                with self.assertRaisesRegex(
                    distribution.CommunityBundleError, expected
                ):
                    distribution._completion_assessment_binding(payload)


class CommunityLicenseEvidenceStaticTests(unittest.TestCase):
    """Authenticate license texts independently of a generated bundle."""

    @staticmethod
    def license_payload() -> dict[str, bytes]:
        return {
            path: (distribution.REPOSITORY_ROOT / path).read_bytes()
            for path in distribution.LICENSE_EVIDENCE_MEMBERS
        }

    def test_every_included_license_text_has_an_external_exact_pin(self) -> None:
        payload = self.license_payload()
        distribution._verify_license_evidence_member_census(payload)
        ledger, closure = distribution._bundle_member_license_ledger(payload)
        self.assertEqual(len(ledger), len(payload))
        self.assertEqual(closure["license_evidence_members"], len(payload))
        for row in ledger:
            self.assertEqual(row["basis"], "externally-pinned-license-text")
            self.assertEqual(
                row["sha256"],
                distribution.LICENSE_EVIDENCE_MEMBER_SHA256[row["path"]],
            )

    def test_touch_candidate_provenance_is_required_and_mit_ledgered(self) -> None:
        relative = (
            "tools/manifests/"
            "g2-touch-final-source-candidate-provenance.tsv"
        )
        archive_path = f"g2/{relative}"
        self.assertIn(relative, distribution.EXPLICIT_FILES)
        self.assertIn(
            archive_path, distribution.PROJECT_GENERATED_RECEIPT_MEMBERS
        )
        payload = {
            "LICENSE": (distribution.REPOSITORY_ROOT / "LICENSE").read_bytes(),
            archive_path: (
                b"# SPDX-License-Identifier: MIT\ncategory\tbytes\n"
            ),
        }
        ledger, closure = distribution._bundle_member_license_ledger(payload)
        row = next(item for item in ledger if item["path"] == archive_path)
        self.assertEqual(row["license"], "MIT")
        self.assertEqual(row["member_class"], "project_generated_receipt")
        self.assertEqual(
            row["basis"],
            "authenticated-root-mit-generated-receipt-scope",
        )
        self.assertEqual(closure["project_generated_receipt_members"], 1)

    def test_freetype_cff_component_and_admission_receipt_are_public(self) -> None:
        manifest_relative = (
            "tools/manifests/g2-freetype-cff-source-admission.json"
        )
        manifest_path = f"g2/{manifest_relative}"
        admission_path = (
            "g2/components/shared/freetype_cff/source_admission.json"
        )
        readme_path = "g2/components/shared/freetype_cff/README.md"
        source_paths = {
            "g2/components/shared/freetype_cff/runtime_freetype_cff.c",
            "g2/components/shared/freetype_cff/runtime_freetype_cff.h",
        }
        self.assertIn(manifest_relative, distribution.EXPLICIT_FILES)
        self.assertIn(
            manifest_path, distribution.PROJECT_GENERATED_RECEIPT_MEMBERS
        )
        self.assertIn(
            admission_path, distribution.PROJECT_GENERATED_RECEIPT_MEMBERS
        )
        self.assertIn(readme_path, distribution.PROJECT_ROOT_MIT_MEMBERS)

        selected = {
            path.relative_to(distribution.REPOSITORY_ROOT).as_posix()
            for path in distribution.collect_files()
        }
        self.assertTrue(
            {manifest_path, admission_path, readme_path, *source_paths}
            <= selected
        )
        payload_paths = {
            "LICENSE",
            "g2/third_party/freetype/LICENSE",
            manifest_path,
            admission_path,
            readme_path,
            *source_paths,
        }
        payload = {
            path: (distribution.REPOSITORY_ROOT / path).read_bytes()
            for path in payload_paths
        }
        ledger, closure = distribution._bundle_member_license_ledger(payload)
        rows = {row["path"]: row for row in ledger}
        for path in (manifest_path, admission_path):
            self.assertEqual(rows[path]["license"], "MIT")
            self.assertEqual(
                rows[path]["member_class"], "project_generated_receipt"
            )
        self.assertEqual(rows[readme_path]["license"], "MIT")
        self.assertEqual(
            rows[readme_path]["member_class"], "project_document_or_data"
        )
        for path in source_paths:
            self.assertEqual(rows[path]["license"], "FTL")
            self.assertEqual(rows[path]["member_class"], "code_source")
            self.assertEqual(rows[path]["basis"], "direct-spdx-marker")
        self.assertEqual(closure["unresolved_members"], 0)

        report = json.loads(payload[manifest_path])
        retained = report["retained_source_evidence"]
        self.assertEqual(
            (retained["functions"], retained["bytes"]), (47, 12_062)
        )
        production = report["production"]
        self.assertFalse(production["stock_image_overlay_routed"])
        self.assertFalse(
            production["authenticated_stock_policy_callsite_recovered"]
        )
        self.assertFalse(production["authenticated_target_placement"])
        self.assertFalse(report["evidence_bounds"]["hardware_operations"])

    def test_all_new_freetype_admission_documents_are_license_ledgered(self) -> None:
        modules = {
            "freetype_autofit", "freetype_base", "freetype_psaux",
            "freetype_pshinter", "freetype_psnames", "freetype_sfnt",
            "freetype_smooth", "freetype_truetype_map",
        }
        readmes = {
            f"g2/components/shared/{module}/README.md" for module in modules
        }
        admissions = {
            f"g2/components/shared/{module}/source_admission.json"
            for module in modules
        }
        admissions.add(
            "g2/components/shared/liblc3/encoder_source_admission.json"
        )
        self.assertTrue(readmes <= distribution.PROJECT_ROOT_MIT_MEMBERS)
        self.assertTrue(
            admissions <= distribution.PROJECT_GENERATED_RECEIPT_MEMBERS
        )
        payload = {
            "LICENSE": (distribution.REPOSITORY_ROOT / "LICENSE").read_bytes(),
            **{
                path: (distribution.REPOSITORY_ROOT / path).read_bytes()
                for path in readmes | admissions
            },
        }
        ledger, closure = distribution._bundle_member_license_ledger(payload)
        rows = {row["path"]: row for row in ledger}
        self.assertTrue(all(
            rows[path]["member_class"] == "project_document_or_data"
            for path in readmes
        ))
        self.assertTrue(all(
            rows[path]["member_class"] == "project_generated_receipt"
            for path in admissions
        ))
        self.assertEqual(closure["unresolved_members"], 0)

    def test_mutated_and_unrecognized_license_texts_fail_closed(self) -> None:
        payload = self.license_payload()
        invensense = "g2/third_party/invensense-icm45608/LICENSE"
        payload[invensense] += b"\nunauthenticated alternate terms\n"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "bundled license evidence changed",
        ):
            distribution._bundle_member_license_ledger(payload)

        payload = self.license_payload()
        payload["g2/third_party/example/COPYING"] = b"alternate terms\n"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "license evidence member census changed",
        ):
            distribution._verify_license_evidence_member_census(payload)

    def test_cmsis_queue_adapters_bind_their_own_apache_license(self) -> None:
        payload = self.license_payload()
        source_path = (
            "g2/components/bootloader/core_overlay/"
            "runtime_queue_get_416920.c"
        )
        payload[source_path] = (
            distribution.REPOSITORY_ROOT / source_path
        ).read_bytes()
        ledger, _closure = distribution._bundle_member_license_ledger(payload)
        row = next(item for item in ledger if item["path"] == source_path)
        self.assertIn("reviewed-upstream-license", row["basis"])
        self.assertEqual(
            row["evidence"],
            [{
                "path": "g2/third_party/cmsis-freertos/CMSIS_5/LICENSE.txt",
                "sha256": (
                    "b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1"
                ),
            }],
        )

    def test_pt_lc3_setup_binds_the_exact_google_liblc3_license(self) -> None:
        source_path = (
            "g2/components/apollo_main/core_overlay/pt_protocol_lc3_setup.c"
        )
        license_path = "g2/third_party/liblc3/LICENSE"
        expected_sha256 = (
            "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
        )
        self.assertEqual(
            distribution.EXPLICIT_LICENSE_EVIDENCE_SCOPES[source_path],
            ("Apache-2.0", license_path, expected_sha256),
        )
        payload = self.license_payload()
        payload[source_path] = (
            distribution.REPOSITORY_ROOT / source_path
        ).read_bytes()
        ledger, _closure = distribution._bundle_member_license_ledger(payload)
        row = next(item for item in ledger if item["path"] == source_path)
        self.assertEqual(row["license"], "Apache-2.0")
        self.assertEqual(
            row["basis"],
            f"direct-spdx-marker+reviewed-upstream-license:{license_path}",
        )
        self.assertEqual(
            row["evidence"],
            [{"path": license_path, "sha256": expected_sha256}],
        )

    def test_ring_buffer_and_mpaland_sources_bind_exact_upstream_mit_texts(self) -> None:
        ring_license = "g2/third_party/ring-buffer/LICENSE"
        mpaland_license = (
            "g2/components/apollo_main/core_overlay/LICENSE-mpaland-MIT"
        )
        self.assertEqual(
            {
                ring_license:
                    "d96c4b746ca4a4b8a901e8e0b4ff2ae87026055d2799dcfc58632cd02f422825",
                mpaland_license:
                    "34a89d27aa3cc583d0c5fbb4017864f1ea9bc38c73388c0ae8a912a9cdb82c41",
            },
            {
                path: distribution.LICENSE_EVIDENCE_MEMBER_SHA256[path]
                for path in (ring_license, mpaland_license)
            },
        )
        source_scopes = {
            path: scope
            for path, scope in distribution.EXPLICIT_LICENSE_EVIDENCE_SCOPES.items()
            if scope[1] in {ring_license, mpaland_license}
        }
        self.assertEqual(len(source_scopes), 9)
        self.assertEqual(
            {scope[1] for scope in source_scopes.values()},
            {ring_license, mpaland_license},
        )
        payload = self.license_payload()
        payload.update({
            path: (distribution.REPOSITORY_ROOT / path).read_bytes()
            for path in source_scopes
        })
        ledger, closure = distribution._bundle_member_license_ledger(payload)
        rows = {row["path"]: row for row in ledger}
        self.assertEqual(closure["license_evidence_members"], 18)
        for path, scope in source_scopes.items():
            row = rows[path]
            self.assertEqual(row["license"], "MIT")
            self.assertEqual(
                row["basis"],
                f"direct-spdx-marker+reviewed-upstream-license:{scope[1]}",
            )
            self.assertEqual(
                row["evidence"],
                [{"path": scope[1], "sha256": scope[2]}],
            )

        omitted = self.license_payload()
        omitted.pop(ring_license)
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "included license evidence member census changed",
        ):
            distribution._verify_license_evidence_member_census(omitted)

        mutated = dict(payload)
        mutated[mpaland_license] += b"\nmutated terms\n"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "bundled license evidence changed",
        ):
            distribution._bundle_member_license_ledger(mutated)

        baseline_ledger, baseline_closure = (
            distribution._bundle_member_license_ledger(payload)
        )
        ring_source = "g2/components/shared/ring_buffer/runtime_ring_buffer.c"
        wrong_scope = {
            ring_source: (
                "MIT",
                "LICENSE",
                distribution.LICENSE_EVIDENCE_MEMBER_SHA256["LICENSE"],
            )
        }
        with mock.patch.dict(
            distribution.EXPLICIT_LICENSE_EVIDENCE_SCOPES,
            wrong_scope,
        ), self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "bundle member license ledger changed",
        ):
            distribution._verify_bundle_member_license_ledger(
                payload, baseline_ledger, baseline_closure
            )

    def test_root_community_policy_docs_are_mit_ledger_members(self) -> None:
        self.assertEqual(
            distribution.COMMUNITY_POLICY_MEMBERS,
            {
                "CODE_OF_CONDUCT.md",
                "CONTRIBUTING.md",
                "SECURITY.md",
                "SUPPORT.md",
            },
        )
        self.assertLessEqual(
            distribution.COMMUNITY_POLICY_MEMBERS,
            set(distribution.EXPLICIT_REPOSITORY_FILES),
        )
        payload = {
            "LICENSE": (distribution.REPOSITORY_ROOT / "LICENSE").read_bytes(),
            **{
                path: (distribution.REPOSITORY_ROOT / path).read_bytes()
                for path in distribution.COMMUNITY_POLICY_MEMBERS
            },
        }
        ledger, closure = distribution._bundle_member_license_ledger(payload)
        self.assertEqual(closure["total_members"], 5)
        self.assertEqual(closure["project_root_mit_members"], 4)
        self.assertEqual(closure["license_evidence_members"], 1)
        for row in ledger:
            if row["path"] in distribution.COMMUNITY_POLICY_MEMBERS:
                self.assertEqual(row["license"], "MIT")
                self.assertEqual(
                    row["basis"], "authenticated-root-mit-ownership-scope"
                )


class CanonicalMaintainerWorkflowDocsTests(unittest.TestCase):
    """Keep the public canonical workflow aligned with strict admission."""

    COMMUNITY_DOC = ROOT / "docs/community-source-distribution.md"
    ARCHIVE_README = ROOT / "docs/community-archive-README.md"
    LINUX_DOC = ROOT / "docs/linux-reproducible-build.md"
    ROOT_README = ROOT.parent / "README.md"
    ROOT_BUILD_DOC = ROOT.parent / "docs/build.md"
    TOOLS_README = ROOT / "tools/README.md"
    LVGL_README = ROOT / "components/shared/lvgl/README.md"

    def test_public_claim_and_external_input_wording_match_enforcement(self) -> None:
        community = self.COMMUNITY_DOC.read_text(encoding="utf-8")
        archive = self.ARCHIVE_README.read_text(encoding="utf-8")
        root = self.ROOT_README.read_text(encoding="utf-8")
        boundary_docs = (
            community,
            archive,
            root,
            self.ROOT_BUILD_DOC.read_text(encoding="utf-8"),
            self.TOOLS_README.read_text(encoding="utf-8"),
            self.LVGL_README.read_text(encoding="utf-8"),
        )
        for text in boundary_docs:
            self.assertIn("official-payload-free", text)
            self.assertNotIn("vendor-byte-free", text)
        for required in (
            "no complete official\npackage or component",
            "no unreviewed raw or encoded retained executable-byte\ntranscript",
            "reviewed semantic source tables",
        ):
            self.assertIn(required, community)
        self.assertIn("All eighteen included license-text members", community)
        self.assertNotIn("The repository is self-contained", root)
        self.assertIn("Inputs deliberately excluded for licensing remain", root)
        self.assertIn("locally authorized official payloads", root)
        self.assertIn("separately fetched, pinned vendor roots", root)

    def test_apple_compiler_review_copy_is_single_link_and_byte_authenticated(self) -> None:
        text = self.COMMUNITY_DOC.read_text(encoding="utf-8")
        section = text.split("## Maintainer canonical-observation workflow", 1)[1]
        section = section.split("## Extracted-tree smoke build", 1)[0]
        for required in (
            "### Isolate the reviewed Apple compiler",
            'APPLE_CLANG_SOURCE="$(xcrun --find clang)"',
            'APPLE_REVIEW_ROOT="$PWD/build/canonical-toolchain/apple-clang-review"',
            'test ! -e "$APPLE_REVIEW_ROOT"',
            '/bin/cp -p "$APPLE_CLANG_SOURCE" "$APPLE_CLANG_REVIEW"',
            '"$APPLE_CLANG_REVIEW" --no-default-config -print-resource-dir',
            '/bin/cp -R "$APPLE_RESOURCE_SOURCE/include"',
            "metadata.st_nlink != 1",
            "review_metadata.st_nlink != 1",
            "review compiler bytes differ from selected Apple clang",
            "review compiler resource-header closure differs",
            "compiler_sha256=",
            "resource_header_closure_sha256=",
            "outside the enumerated firmware\nsource closure",
            "does not authorize a source-closure or artifact change",
            "not a committed\nmachine-path pin",
        ):
            self.assertIn(required, section)
        self.assertEqual(
            section.count('OPENCFW_CLANG="$APPLE_CLANG_REVIEW"'), 2
        )
        self.assertNotIn("OPENCFW_CLANG=/path/to/reviewed/apple-clang", section)
        for machine_path in ("/Applications/", "/Library/Developer/", "/Users/"):
            self.assertNotIn(machine_path, section)

    def test_linux_workflow_requires_the_same_isolated_apple_review_copy(self) -> None:
        text = self.LINUX_DOC.read_text(encoding="utf-8")
        section = text.split("Apollo core-source pin changes", 1)[1]
        section = section.split("## What reproduces on Linux today", 1)[0]
        for required in (
            "community-source-distribution.md#isolate-the-reviewed-apple-compiler",
            "byte-identical, isolated, single-link regular-file copy",
            "compiler-derived builtin\nresource `include` closure",
            "resource-header closure SHA-256/count/size",
            "absolute path is local receipt\nevidence",
            "outside the enumerated firmware source\nclosure",
            "does not authorize source,\ncompiler-version, builtin-header, or artifact drift",
        ):
            self.assertIn(required, section)
        self.assertEqual(
            section.count('OPENCFW_CLANG="$APPLE_CLANG_REVIEW"'), 2
        )
        self.assertNotIn("OPENCFW_CLANG=/path/to/reviewed/apple-clang", section)
        for machine_path in ("/Applications/", "/Library/Developer/", "/Users/"):
            self.assertNotIn(machine_path, section)

    def test_postapply_dual_profile_reconstruction_is_exact_and_local(self) -> None:
        snippets = []
        for doc in (self.COMMUNITY_DOC, self.LINUX_DOC):
            text = doc.read_text(encoding="utf-8")
            section = text.split(
                "### Rebuild post-apply dual-profile evidence", 1
            )[1]
            section = section.split("## ", 1)[0]
            for required in (
                "--output-dir components/apollo_main/core_overlay/build",
                "--output-dir .tmp-postapply-core-linux",
                "manifests/.tmp-g2-linux-postapply.json",
                '"build/canonical-provider/linux-clang/apollo_bootloader/"',
                '"ota_s200_bootloader.bin"',
                '".tmp-postapply-core-linux/ota_s200_firmware_ota.bin"',
                'overrides = candidate.get("component_overrides")',
                'audit_rows = audit["component_overrides"]',
                'if audit != original:',
                'raise SystemExit("scratch manifest changed a field other than two paths")',
                "--output-dir build/postapply-package-apple",
                "--output-dir build/postapply-package-linux",
                "make dual-profile-ownership-write",
                "build/canonical-observation/{apple-a,apple-b,linux-a,linux-b}/",
                "ignored, private local\nevidence",
                "not Git inputs or community-archive members",
                "no network access,\nsigning, flashing, or hardware operation",
            ):
                self.assertIn(required, section)
            self.assertEqual(
                section.count("python3 tools/open_cfw.py build \\"), 2
            )
            self.assertEqual(
                section.count("python3 tools/open_cfw.py verify \\"), 2
            )
            self.assertEqual(
                section.count("python3 tools/open_cfw.py verify-artifacts \\"), 2
            )
            self.assertLess(
                section.rindex("python3 tools/open_cfw.py verify-artifacts"),
                section.index("make dual-profile-ownership-write"),
            )
            snippets.append(
                section.split(
                    "manifests/.tmp-g2-linux-postapply.json <<'PY'\n", 1
                )[1].split("\nPY\n", 1)[0]
            )

        self.assertEqual(snippets[0], snippets[1])
        with tempfile.TemporaryDirectory(prefix="opencfw-postapply-doc-") as tmp:
            temporary = Path(tmp)
            source = temporary / "g2-2.2.6.10-core-source.json"
            destination = temporary / ".tmp-g2-linux-postapply.json"
            original = json.loads(
                (ROOT / "manifests/g2-2.2.6.10-core-source.json").read_text(
                    encoding="utf-8"
                )
            )
            source.write_text(
                json.dumps(original, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [sys.executable, "-", str(source), str(destination)],
                input=snippets[0],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            observed = json.loads(destination.read_text(encoding="utf-8"))

        expected = json.loads(json.dumps(original))
        expected_paths = {
            "apollo_bootloader": (
                "components/bootloader/core_overlay/build/ota_s200_bootloader.bin",
                "build/canonical-provider/linux-clang/apollo_bootloader/"
                "ota_s200_bootloader.bin",
            ),
            "apollo_main": (
                "components/apollo_main/core_overlay/build/"
                "ota_s200_firmware_ota.bin",
                ".tmp-postapply-core-linux/ota_s200_firmware_ota.bin",
            ),
        }
        for name, (old_path, new_path) in expected_paths.items():
            provider = expected["component_overrides"][name]["provider"]
            self.assertEqual(provider["path"], old_path)
            provider["path"] = new_path
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
