# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import community_distribution as distribution  # noqa: E402
import open_cfw  # noqa: E402


class CommunityDistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-community-bundle-")
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
        self.assertEqual(self.first_report["sha256"], self.second_report["sha256"])
        self.assertFalse(self.manifest["contains_official_firmware_payloads"])
        self.assertFalse(self.manifest["contains_stock_firmware_guard_bytes"])
        self.assertEqual(self.manifest["schema_version"], 4)
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
        ledger = self.manifest["source_member_license_ledger"]
        self.assertEqual({row["path"] for row in ledger}, source_like)
        self.assertEqual(
            self.manifest["source_member_license_closure"]["source_like_members"],
            len(source_like),
        )
        self.assertEqual(
            self.manifest["source_member_license_closure"]["unresolved_members"],
            0,
        )
        self.assertEqual(
            len(ledger),
            self.manifest["source_member_license_closure"]["explicit_spdx_members"]
            + self.manifest["source_member_license_closure"][
                "reviewed_upstream_scope_members"
            ],
        )
        self.assertTrue(
            all(
                row["classification"]
                in {"explicit-spdx", "reviewed-upstream-scope"}
                and row["evidence"]
                for row in ledger
            )
        )
        self.assertEqual(
            self.manifest["completion_assessment"],
            {"included": False, "repository_gate": "completion-assessment-check"},
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
            "g2/components/apollo_main/liblc3_ltpf/liblc3_ltpf_overlay.c",
            "g2/components/apollo_main/liblc3_ltpf/overlay.json",
            "g2/components/apollo_main/pt_protocol/build_component.py",
            "g2/tests/test_apollo_pt_protocol_provider.py",
            "g2/third_party/liblc3/include/lc3.h",
            "g2/components/shared/touch/runtime_touch_application_core.c",
            "g2/components/shared/touch/runtime_touch_product_orchestration.c",
            "g2/components/shared/case/runtime_case_uart_update.c",
            "g2/components/shared/gx8002/runtime_gx8002_kws_model_boundary.c",
            "g2/components/shared/em9305/runtime_controller_pawr_boundary.c",
            "g2/components/shared/touch/runtime_touch_unsigned_division.c",
            "g2/components/touch/source_image/build_image.py",
            "g2/components/touch/source_image/firmware_image.c",
            "g2/components/touch/source_image/linker.ld",
            "g2/components/case/source_image/README.md",
            "g2/components/case/source_image/build_image.py",
            "g2/components/case/source_image/compiler_runtime.c",
            "g2/components/case/source_image/linker.ld",
            "g2/components/case/source_image/startup.c",
            "g2/tools/analyze_g2_case_source_image.py",
            "g2/tools/manifests/g2-case-source-image-summary.json",
            "g2/tests/test_analyze_g2_case_source_image.py",
            "g2/tools/analyze_g2_touch_source_image.py",
            "g2/tools/manifests/g2-touch-source-image-summary.json",
            "g2/tests/test_touch_source_image.py",
            "g2/tests/test_runtime_touch_unsigned_division.py",
            "g2/tests/fixtures/touch_unsigned_division_host.c",
            "g2/tools/manifests/g2-touch-final-classification-summary.json",
            "g2/tools/manifests/g2-case-final-classification-summary.json",
            "g2/tools/manifests/gx8002-source-readiness.tsv",
        ):
            self.assertIn(relative, names)
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
        }
        self.assertEqual(len(pt_sources), 28)
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
        self.assertNotIn("g2/tools/extract_g2_pt_protocol_decomp.py", names)
        self.assertNotIn("g2/tests/test_analyze_g2_pt_protocol_source.py", names)
        self.assertNotIn("g2/tests/test_extract_g2_pt_protocol_decomp.py", names)
        self.assertFalse(
            any(
                name.startswith(
                    "g2/docs/reports/openCFW-completion-2026-08-28/"
                )
                for name in names
            )
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
        self.assertIn("LICENSE", names)
        self.assertIn("NOTICE", names)
        self.assertIn("README.md", names)
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
        public_analysis = {
            "g2/tools/analyze_g2_case_source_image.py",
            "g2/tests/test_analyze_g2_case_source_image.py",
            "g2/tools/analyze_g2_touch_source_image.py",
            "g2/tests/test_analyze_g2_touch_source_image.py",
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
                    for info in archive.infolist()
                )
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

    def test_public_policy_rejects_raw_guards_secrets_and_internal_paths(self) -> None:
        with self.assertRaisesRegex(
            distribution.CommunityBundleError,
            "raw stock-byte guard",
        ):
            distribution._verify_public_payload(
                "g2/manifests/forged.json",
                b'{"nested": [{"expected_hex": "00112233"}]}',
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
                "g2/third_party/example/restricted.h",
                (
                    b"use, reproduction, disclosure or distribution of the Software "
                    b"without an express license agreement from the vendor is strictly "
                    b"prohibited\n"
                ),
            )
        inventory = {row["path"] for row in self.manifest["files"]}
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
            distribution.CommunityBundleError, "encoded vendor-byte transcript"
        ):
            distribution._verify_public_payload(
                "g2/third_party/example/vendor_image.h",
                (b"0x36," * 16) + b"\n",
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

    def test_bundle_member_hashes_exclude_every_official_payload(self) -> None:
        official = distribution._official_provider_hashes() | {
            distribution.OFFICIAL_PACKAGE_SHA256
        }
        self.assertFalse(official & {row["sha256"] for row in self.manifest["files"]})
        with zipfile.ZipFile(self.first) as archive:
            self.assertEqual(archive.namelist()[0], "BUNDLE-MANIFEST.json")
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
        with mock.patch.object(distribution, "MAX_ARCHIVE_SIZE", 1):
            with self.assertRaisesRegex(
                distribution.CommunityBundleError, "byte-size cap"
            ):
                distribution._verify_bundle_bytes(self.first.read_bytes())

    def test_member_paths_and_source_license_ledger_are_fail_closed(self) -> None:
        distribution._validate_archive_names(
            ["BUNDLE-MANIFEST.json", "g2/source.c"]
        )
        for names in (
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

        payload = {
            "LICENSE": (distribution.REPOSITORY_ROOT / "LICENSE").read_bytes(),
            "g2/components/example/runtime.py": (
                b"# SPDX-License-Identifier: MIT\nvalue = 1\n"
            ),
        }
        ledger, closure = distribution._bundle_member_license_ledger(payload)
        self.assertEqual(closure["source_like_members"], 1)
        self.assertEqual(ledger[0]["classification"], "explicit-spdx")
        payload["g2/components/example/unlicensed.py"] = b"value = 2\n"
        with self.assertRaisesRegex(
            distribution.CommunityBundleError, "source license is unresolved"
        ):
            distribution._bundle_member_license_ledger(payload)
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
        self.assertEqual(receipt["hardware_operations"], False)
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

        def fail_second_provider(path: Path, data: bytes, *, mode: int = 0o644) -> None:
            nonlocal provider_writes, injected
            if path != receipt_path:
                provider_writes += 1
                if provider_writes == 2 and not injected:
                    injected = True
                    raise distribution.CommunityBundleError("injected hydration failure")
            real_atomic_write(path, data, mode=mode)

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


if __name__ == "__main__":
    unittest.main()
