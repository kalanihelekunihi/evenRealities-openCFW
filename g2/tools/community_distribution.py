#!/usr/bin/env python3
"""Build and hydrate the official-payload-free G2 community source bundle."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import ast
import base64
import errno
import hashlib
import importlib
import io
import json
import os
import posixpath
import re
import secrets
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import time
import urllib.parse
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import audit_g2_release_licensing
import open_cfw


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parent
BASE_MANIFEST = ROOT / "manifests/g2-2.2.6.10.json"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
OFFICIAL_PACKAGE_SHA256 = "f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa"
OFFICIAL_PACKAGE_SIZE = 4_301_227
# These immutable public-release denials must not be derived only from a
# mutable manifest.  They identify the six official s200_v2.2.6.10 payloads
# even if a local file, archive member, or manifest row has been renamed.
OFFICIAL_PAYLOAD_SHA256 = frozenset({
    "b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0",
    "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9",
    "0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d",
    "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374",
    "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5",
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
})
OFFICIAL_COMPONENT_CONTRACT = (
    (
        "codec",
        "official_blob",
        "blobs/official/g2-2.2.6.10/firmware_codec.bin",
        326_092,
        "b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0",
    ),
    (
        "ble_em9305",
        "official_blob",
        "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin",
        211_948,
        "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9",
    ),
    (
        "touch",
        "official_blob",
        "blobs/official/g2-2.2.6.10/firmware_touch.bin",
        34_464,
        "0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d",
    ),
    (
        "case",
        "official_blob",
        "blobs/official/g2-2.2.6.10/firmware_box.bin",
        55_784,
        "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374",
    ),
    (
        "apollo_bootloader",
        "official_blob",
        "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin",
        148_599,
        "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5",
    ),
    (
        "apollo_main",
        "official_blob",
        "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin",
        3_523_396,
        "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
    ),
)
FORBIDDEN_OFFICIAL_FIRMWARE_SHA256 = (
    OFFICIAL_PAYLOAD_SHA256 | {OFFICIAL_PACKAGE_SHA256}
)
MAX_ARCHIVE_MEMBERS = 4_096
MAX_ARCHIVE_MEMBER_SIZE = 32 * 1024 * 1024
MAX_ARCHIVE_UNCOMPRESSED_SIZE = 256 * 1024 * 1024
MAX_ARCHIVE_SIZE = 256 * 1024 * 1024
MAX_JSON_INPUT_SIZE = 64 * 1024 * 1024
HYDRATION_RECEIPT = ".open-cfw-local-hydration.json"
DEFERRED_HARDWARE_VALIDATION = "blocked by unavailable physical evidence"
MINIMUM_PYTHON = (3, 9)
TOOLCHAIN_CONFIGS = (
    ROOT / "components/bootloader/core_overlay/overlay.json",
    ROOT / "components/apollo_main/core_overlay/overlay.json",
)
COMPLETION_ASSESSMENT_CHECK = ROOT / "tools/generate_g2_completion_report.py"
BUNDLE_MANIFEST_FIELDS = frozenset({
    "archive_encoding",
    "completion_assessment",
    "contains_official_firmware_payloads",
    "contains_stock_firmware_guard_bytes",
    "dual_profile_ownership_proof",
    "files",
    "format",
    "license_closure",
    "member_license_closure",
    "member_license_ledger",
    "official_package_required_locally",
    "payload_inventory_sha256",
    "schema_version",
    "source_capture_sha256",
    "stock_guard_representation",
    "stock_guard_scope",
})


def _read_json_path(path: Path) -> Any:
    """Read a concurrently generated JSON input only from a stable snapshot."""
    last_error: Exception | None = None
    for _attempt in range(20):
        try:
            payload = _read_regular_path_once(
                path,
                maximum_size=MAX_JSON_INPUT_SIZE,
                label=f"community JSON input {path}",
            )
            return json.loads(payload)
        except (CommunityBundleError, json.JSONDecodeError, UnicodeDecodeError) as error:
            last_error = error
            time.sleep(0.01)
    raise CommunityBundleError(
        f"community JSON input did not stabilize: {path}: {last_error}"
    )
FORBIDDEN_PARTS = {
    "blobs",
    "build",
    "corpus",
    "research",
    "__pycache__",
    ".git",
}
FORBIDDEN_SUFFIXES = {
    ".a",
    ".axf",
    ".bin",
    ".dll",
    ".dylib",
    ".elf",
    ".evenota",
    ".exe",
    ".hex",
    ".img",
    ".o",
    ".obj",
    ".out",
    ".rom",
    ".so",
    ".uf2",
}
FORBIDDEN_FILENAMES = {"EVIDENCE.md", HYDRATION_RECEIPT}
FORBIDDEN_SECRET_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".jks", ".keystore"}
FORBIDDEN_SECRET_FILENAMES = {
    ".env",
    ".netrc",
    "credentials.json",
    "secrets.json",
    "id_ed25519",
    "id_rsa",
}
SOURCE_SUFFIXES = {".c", ".h", ".S", ".s", ".inc", ".ld", ".lds", ".py", ".json", ".html", ".md", ".patch", ".txt", ".tsv", ".csv", ".mk"}
SOURCE_CODE_SUFFIXES = {
    ".c", ".h", ".S", ".s", ".inc", ".ld", ".lds", ".py", ".mk", ".patch"
}
BUILD_OVERLAY_RECIPES = (
    "components/apollo_main/core_overlay/overlay.json",
    "components/apollo_main/liblc3_ltpf/overlay.json",
    "components/bootloader/core_overlay/overlay.json",
)
COMMUNITY_SOURCE_TREES = (
    # Candidate and boundary source remains useful community firmware work
    # even before it is production-routed into the Apollo or boot providers.
    "components/shared",
    "components/case/source_image",
    "components/em9305/source_image",
    "components/touch/source_image",
)
COMMUNITY_PUBLIC_SOURCE_GLOBS = (
    ("components/apollo_main/core_overlay/pt_protocol*.c", 15),
    ("components/apollo_main/core_overlay/pt_protocol*.h", 14),
)
PT_PROTOCOL_AREAS = (
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
PT_PROTOCOL_SOURCE_SUFFIXES = (
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
PT_PROTOCOL_FIXTURES = (
    "basic_handlers",
    "board_backend",
    "board_leaf_candidates",
    "core",
    "platform_adapter",
    "production_entry",
)
CASE_PUBLIC_AREAS = (
    "semantic_leaves",
    "pure_helpers",
    "register_policies",
)
COMMUNITY_CANDIDATE_TEST_GLOBS = (
    "tests/test_runtime_touch_*.py",
    "tests/fixtures/touch_*_host.c",
    "tests/test_runtime_case_*.py",
    "tests/fixtures/case_*_host.c",
    "tests/fixtures/runtime_case_*_host.c",
    "tests/test_runtime_pt_protocol_*.py",
    "tests/fixtures/pt_protocol_*_host.c",
)
EXPLICIT_FILES = (
    "Makefile",
    "make.sh",
    "NOTICE-CORE-SOURCE.md",
    "components/apollo_main/core_overlay/LICENSE-mpaland-MIT",
    "components/apollo_main/core_overlay/build_component.py",
    "components/apollo_main/core_overlay/overlay.json",
    "components/apollo_main/liblc3_ltpf/NOTICE.md",
    "components/apollo_main/liblc3_ltpf/README.md",
    "components/apollo_main/liblc3_ltpf/build_component.py",
    "components/apollo_main/liblc3_ltpf/liblc3_ltpf_overlay.c",
    "components/apollo_main/liblc3_ltpf/overlay.json",
    "components/apollo_main/pt_protocol/build_component.py",
    "components/apollo_main/ring_gesture/DERIVATION.patch",
    "components/apollo_main/ring_gesture/NOTICE.md",
    "components/apollo_main/ring_gesture/PROVENANCE.json",
    "components/apollo_main/ring_gesture/overlay.json",
    "components/apollo_main/ring_gesture/upstream/gesture_fwd.c",
    "components/apollo_main/ring_gesture/verify_provenance.py",
    "components/bootloader/core_overlay/build_component.py",
    "components/bootloader/core_overlay/overlay.json",
    "docs/release-licensing-and-redistribution.md",
    "docs/community-source-distribution.md",
    "manifests/g2-2.2.6.10.json",
    "manifests/g2-2.2.6.10-core-source.json",
    "tools/open_cfw.py",
    "tools/apollo_overlay.py",
    "tools/apply_g2_canonical_observations.py",
    "tools/detect_toolchain.py",
    "tools/audit_g2_release_licensing.py",
    "tools/community_distribution.py",
    "tools/verify_g2_clkmgr_divider_public.py",
    "tools/analyze_g2_touch_source_image.py",
    "tools/analyze_g2_case_source_image.py",
    "tools/analyze_em9305_record_package.py",
    "tests/test_apply_g2_canonical_observations.py",
    "tests/test_core_canonical_recorder_security.py",
    "tests/test_community_markdown_link_closure.py",
    "tools/analyze_g2_dual_profile_ownership.py",
    "tools/manifests/g2-dual-profile-ownership.json",
    "tests/test_analyze_g2_dual_profile_ownership.py",
    "tools/manifests/g2-case-final-classification-summary.json",
    "tools/manifests/g2-case-final-function-frontier.tsv",
    "tools/manifests/g2-case-final-gap-frontier.tsv",
    "tools/manifests/g2-case-final-physical-byte-buckets.tsv",
    "tools/manifests/g2-case-semantic-leaves-admission-summary.json",
    "tools/manifests/g2-case-semantic-leaves-admission.tsv",
    "tools/manifests/g2-case-pure-helpers-admission-summary.json",
    "tools/manifests/g2-case-pure-helpers-admission.tsv",
    "tools/manifests/g2-case-register-policies-admission-summary.json",
    "tools/manifests/g2-case-register-policies-admission.tsv",
    "tools/manifests/g2-touch-final-classification-summary.json",
    "tools/manifests/g2-touch-final-frontier.tsv",
    "tools/manifests/g2-touch-final-physical-byte-buckets.tsv",
    "tools/manifests/g2-touch-final-source-candidate-provenance.tsv",
    "tools/manifests/gx8002-source-readiness.tsv",
    "tools/manifests/g2-touch-source-image-summary.json",
    "tools/manifests/g2-case-source-image-summary.json",
    "tools/manifests/g2-nemavg-stroke-caps-candidate-summary.json",
    "tools/manifests/g2-clkmgr-divider-candidate-summary.json",
    "tools/manifests/g2-freetype-cff-source-admission.json",
    "tools/manifests/g2-pt-protocol-source-summary.json",
    "tests/test_ring_gesture_provenance.py",
    "tests/test_analyze_g2_touch_source_image.py",
    "tests/test_analyze_g2_case_source_image.py",
    "tests/test_analyze_em9305_record_package.py",
    "tests/test_em9305_record_package.py",
    "tests/test_touch_source_image.py",
    "tests/test_runtime_nemavg_stroke_caps_candidate.py",
    "tests/fixtures/runtime_nemavg_stroke_caps_host.c",
    "tests/test_runtime_clkmgr_divider_candidate.py",
    "tests/fixtures/runtime_clkmgr_divider_candidate_host.c",
    "tests/test_apollo_pt_protocol_provider.py",
    "third_party/invensense-icm45608/LICENSE",
    "third_party/ring-buffer/LICENSE",
)
DUAL_PROFILE_PROOF_MEMBERS = (
    "g2/tools/analyze_g2_dual_profile_ownership.py",
    "g2/tools/manifests/g2-dual-profile-ownership.json",
    "g2/tests/test_analyze_g2_dual_profile_ownership.py",
    "g2/docs/community-source-distribution.md",
)
TOUCH_FINAL_CLASSIFICATION_RECEIPT = (
    "g2/tools/manifests/g2-touch-final-classification-summary.json"
)
TOUCH_OFFICIAL_DONOR_INPUT = (
    "blobs/official/g2-2.2.6.10/firmware_touch.bin"
)
TOUCH_OFFICIAL_DONOR_SHA256 = (
    "0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d"
)
TOUCH_PUBLIC_ANALYZER_MEMBERS = (
    "g2/tools/analyze_g2_touch_final_frontier.py",
    "g2/tools/analyze_g2_touch_identity.py",
    "g2/tools/analyze_g2_touch_platform_completion_admission.py",
    "g2/tools/analyze_g2_touch_prefix_function_map.py",
    "g2/tools/analyze_g2_touch_relocated_partition.py",
    "g2/tools/analyze_g2_touch_relocated_semantics.py",
    "g2/tools/analyze_g2_touch_software_readiness.py",
    "g2/tools/analyze_g2_touch_source_image.py",
)
TOUCH_ADMISSION_RECEIPT_FILENAMES = (
    "g2-touch-software-readiness-functions.tsv",
    "g2-touch-application-core-admission.tsv",
    "g2-touch-application-packet-pipeline-admission.tsv",
    "g2-touch-application-state-pipeline-admission.tsv",
    "g2-touch-application-upstream-admission.tsv",
    "g2-touch-cat2-source-admission2.tsv",
    "g2-touch-cat2-source-admission3.tsv",
    "g2-touch-cat2-source-admission4.tsv",
    "g2-touch-cat2-source-admission5.tsv",
    "g2-touch-clock-application-wrappers-admission.tsv",
    "g2-touch-closed-record-pipeline-admission.tsv",
    "g2-touch-configuration-bootstrap-admission.tsv",
    "g2-touch-configuration-start-pipeline-admission.tsv",
    "g2-touch-deferred-work-admission.tsv",
    "g2-touch-emeeprom-clean-room-admission.tsv",
    "g2-touch-flash-row-admission.tsv",
    "g2-touch-leaf-primitives-admission.tsv",
    "g2-touch-platform-completion-admission.tsv",
    "g2-touch-platform-wrappers-admission.tsv",
    "g2-touch-product-orchestration-admission.tsv",
    "g2-touch-record-primitives-admission.tsv",
    "g2-touch-selection-update-pipeline-admission.tsv",
    "g2-touch-source-admission.tsv",
    "g2-touch-startup-closed-admission.tsv",
    "g2-touch-storage-adapters-admission.tsv",
    "g2-touch-terminal-wrappers-admission.tsv",
)
TOUCH_ADMISSION_RECEIPT_MEMBERS = tuple(
    f"g2/tools/manifests/{name}"
    for name in TOUCH_ADMISSION_RECEIPT_FILENAMES
)
COMPLETION_REPORT_MEMBERS = (
    "g2/docs/reports/openCFW-completion-2026-08-28/assessment-data.json",
    "g2/docs/reports/openCFW-completion-2026-08-28/artifact.json",
    "g2/docs/reports/openCFW-completion-2026-08-28/report.html",
)
EM9305_PREDECISION_INPUT_MEMBER = (
    "g2/tools/manifests/em9305-residual-provenance-map.tsv"
)
EM9305_FINAL_READINESS_IDENTITIES = {
    "g2/tools/manifests/em9305-final-source-readiness-summary.json": (
        4_882,
        "3fa764455494d542f04d0a71236e9d52f7a116eab8867a1bffc82e20f3e0907e",
    ),
    "g2/tools/manifests/em9305-final-source-readiness.tsv": (
        33_152,
        "cfda63c68a73d27235af204f01ee6c848db9495d0294d55faf70096b7ab08bf9",
    ),
}
EM9305_ARC_BUILD_RECEIPT = (
    "g2/tools/manifests/em9305-arc-candidate-build-summary.json"
)
EM9305_ARC_BUILD_RECEIPT_IDENTITY = (
    4_214,
    "8173f8938d5be6c9d0ed551840f05dbdc02839476908a3eebf8083c3142341b6",
)
EM9305_QPC_BUILD_RECEIPT = (
    "g2/tools/manifests/em9305-qpc-component-build-summary.json"
)
EM9305_QPC_BUILD_RECEIPT_IDENTITY = (
    6_604,
    "e65a1b51eea5065bff760a3e20f1cd17b2f86718da561dbfd55afac35bb17f79",
)
EM9305_RECORD_PACKAGE_RECEIPT = (
    "g2/tools/manifests/em9305-record-package-summary.json"
)
EM9305_RECORD_PACKAGE_RECEIPT_IDENTITY = (
    2_606,
    "947bd35ff79c88e3f7386a4966ab50173589223efc76f1ce1b6bbec42df03b19",
)
PUBLIC_EVIDENCE_RECEIPT_MEMBERS = frozenset({
    *TOUCH_ADMISSION_RECEIPT_MEMBERS,
    TOUCH_FINAL_CLASSIFICATION_RECEIPT,
    "g2/tools/manifests/g2-touch-current-source-readiness-summary.json",
    "g2/tools/manifests/g2-case-register-primitives-admission-summary.json",
    "g2/tools/manifests/g2-case-register-primitives-admission.tsv",
    "g2/tools/manifests/g2-case-register-transforms-admission-summary.json",
    "g2/tools/manifests/g2-case-register-transforms-admission.tsv",
    "g2/tools/manifests/g2-apollo-origin-accounting.json",
    EM9305_PREDECISION_INPUT_MEMBER,
    *EM9305_FINAL_READINESS_IDENTITIES,
    EM9305_ARC_BUILD_RECEIPT,
    EM9305_QPC_BUILD_RECEIPT,
    EM9305_RECORD_PACKAGE_RECEIPT,
    "g2/tools/manifests/g2-project-license-normalization-summary.json",
    "g2/tools/manifests/g2-project-license-normalization.tsv",
    "g2/tools/manifests/g2-project-mit-normalization-case-source-image.txt",
    "g2/tools/manifests/g2-project-mit-normalization-community-controllers.txt",
    "g2/tools/manifests/g2-project-mit-normalization-em9305-source-image.txt",
    "g2/tools/manifests/g2-project-mit-normalization-research-and-wrapper.txt",
    "g2/tools/manifests/g2-project-mit-normalization-scope-paths.txt",
    "g2/tools/manifests/g2-project-mit-normalization-touch-source-image.txt",
    "g2/tools/manifests/g2-production-raw-encoding-quality-summary.json",
    *COMPLETION_REPORT_MEMBERS,
})
COMMUNITY_LOCAL_BUILD_TEST_MODULES = (
    "tests.test_analyze_g2_case_source_image",
    "tests.test_analyze_em9305_record_package",
    "tests.test_em9305_record_package",
    "tests.test_runtime_nemavg_stroke_caps_candidate",
    "tests.test_runtime_clkmgr_divider_candidate",
    "tests.test_apply_g2_canonical_observations",
    "tests.test_core_canonical_recorder_security",
)
SMOKE_PYTHON_IMPORT_CLOSURE = {
    "g2/tests/test_analyze_em9305_record_package.py": {
        "imports": frozenset({
            "__future__", "importlib.util", "json", "pathlib", "sys",
            "unittest",
        }),
        "local": {},
    },
    "g2/tests/test_em9305_record_package.py": {
        "imports": frozenset({
            "__future__", "hashlib", "importlib.util", "json", "pathlib",
            "struct", "subprocess", "sys", "tempfile", "unittest",
        }),
        "local": {},
    },
    "g2/tests/test_analyze_g2_case_source_image.py": {
        "imports": frozenset({
            "__future__", "importlib.util", "json", "pathlib", "sys",
            "tempfile", "unittest",
        }),
        "local": {},
    },
    "g2/tests/test_runtime_nemavg_stroke_caps_candidate.py": {
        "imports": frozenset({
            "__future__", "pathlib", "shutil", "subprocess", "tempfile",
            "unittest",
        }),
        "local": {},
    },
    "g2/tests/test_runtime_clkmgr_divider_candidate.py": {
        "imports": frozenset({
            "__future__", "pathlib", "shutil", "subprocess", "sys",
            "tempfile", "unittest", "verify_g2_clkmgr_divider_public",
        }),
        "local": {
            "verify_g2_clkmgr_divider_public":
                "g2/tools/verify_g2_clkmgr_divider_public.py",
        },
    },
    "g2/tests/test_apply_g2_canonical_observations.py": {
        "imports": frozenset({
            "__future__", "copy", "hashlib", "importlib.util", "inspect",
            "json", "os", "pathlib", "sys", "tempfile", "unittest",
        }),
        "local": {},
    },
    "g2/tests/test_core_canonical_recorder_security.py": {
        "imports": frozenset({
            "__future__", "fcntl", "importlib.util", "json", "os",
            "pathlib", "select", "tempfile", "unittest",
        }),
        "local": {},
    },
    "g2/components/bootloader/core_overlay/build_component.py": {
        "imports": frozenset({
            "__future__", "apollo_overlay", "argparse", "hashlib", "json",
            "os", "pathlib", "struct", "sys", "tempfile", "typing",
        }),
        "local": {"apollo_overlay": "g2/tools/apollo_overlay.py"},
    },
    "g2/components/apollo_main/core_overlay/build_component.py": {
        "imports": frozenset({
            "__future__", "apollo_overlay", "argparse", "contextlib", "copy",
            "fcntl", "importlib.util", "json", "os", "pathlib", "secrets",
            "stat", "sys", "tempfile", "threading", "typing",
        }),
        "local": {"apollo_overlay": "g2/tools/apollo_overlay.py"},
    },
    "g2/tools/open_cfw.py": {
        "imports": frozenset({
            "__future__", "argparse", "contextlib", "copy", "dataclasses",
            "fcntl", "hashlib", "json", "os", "pathlib", "shutil", "stat",
            "struct", "sys", "tempfile", "threading", "typing", "zlib",
        }),
        "local": {},
    },
}
COMMUNITY_POLICY_MEMBERS = frozenset({
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "SUPPORT.md",
})
EXPLICIT_REPOSITORY_FILES = (
    ".gitignore",
    "LICENSE",
    "NOTICE",
    *sorted(COMMUNITY_POLICY_MEMBERS),
)
EXECUTABLE_ARCHIVE_PATHS = {"make.sh", "g2/make.sh"}
REVIEWED_GENERATED_HEX_CONSTRUCTORS = {
    # Four fixed FWPK format/version bytes, not donor executable content.
    "g2/components/touch/source_image/build_image.py",
    # Four fixed EM9305 record-container magic bytes, not donor payload.
    "g2/components/em9305/source_image/record_package.py",
}
LICENSE_EVIDENCE = {
    "MIT": ("LICENSE", "3a0f162b73b7d95cdb1de2395b4f0f4ad35eae3c8eb44f125d5c0db6bc811ea4"),
    "Apache-2.0": ("g2/third_party/cordio/LICENSE.md", "682ae5978019e4ee9d439b300efb125525b2e4cc4181ebd1e676dd60dc69d7cd"),
    "BSD-3-Clause": ("g2/third_party/littlefs/LICENSE.md", "0cb4ff1daf5fdc1359c6a6ee3116092f08fc100c9d58b1b77ab17bfd801f856d"),
    "BSD-2-Clause": ("g2/third_party/lz4/LICENSE", "8b58c446121a109ccf32edc094bba3010a3d85e4ee3702950db55e4d3e87736c"),
    "GPL-3.0-only": ("g2/components/apollo_main/ring_gesture/LICENSE", "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"),
    "FTL": ("g2/third_party/freetype/LICENSE", "08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1"),
    "Zlib": ("g2/third_party/nanopb/LICENSE.txt", "e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d"),
}
# Files without a direct SPDX marker may inherit terms only through one of
# these reviewed upstream scopes.  Each scope is bound to an exact vendored
# license artifact; project-owned paths are intentionally absent.
LICENSE_INHERITANCE_SCOPES = (
    ("g2/third_party/ambiqsuite-apollo510/", "BSD-3-Clause", "g2/third_party/ambiqsuite-apollo510/LICENSE", "0770df5c1956b75715604d5788804eabfc293fc61d5dbbec498c6d379a63755f"),
    ("g2/third_party/cJSON/", "MIT", "g2/third_party/cJSON/LICENSE", "a36dda207c36db5818729c54e7ad4e8b0c6fba847491ba64f372c1a2037b6d5c"),
    ("g2/third_party/cordio/", "Apache-2.0", "g2/third_party/cordio/LICENSE.md", "682ae5978019e4ee9d439b300efb125525b2e4cc4181ebd1e676dd60dc69d7cd"),
    ("g2/third_party/liblc3/", "Apache-2.0", "g2/third_party/liblc3/LICENSE", "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"),
    ("g2/third_party/lz4/", "BSD-2-Clause", "g2/third_party/lz4/LICENSE", "8b58c446121a109ccf32edc094bba3010a3d85e4ee3702950db55e4d3e87736c"),
    ("g2/third_party/tinyframe/", "MIT", "g2/third_party/tinyframe/LICENSE", "eb7b9df3ca390100d31f9aac23f2d8dfe0183a63987112675fc58af9a42f6874"),
    ("g2/third_party/tlsf/", "BSD-3-Clause", "g2/third_party/tlsf/tlsf.h", "f7f73c48810ba60203095667c226e5a600a6ea0f69afba48efff6efbaa628d4f"),
    ("g2/components/apollo_main/core_overlay/runtime_easylogger_", "MIT", "g2/third_party/easylogger/LICENSE", "4a7be67e9701d0344c62d1b92eed8f40b874d00d64a9ee6b3853eb47ef4ea7f9"),
    ("g2/components/apollo_main/core_overlay/runtime_tinyframe_", "MIT", "g2/third_party/tinyframe/LICENSE", "eb7b9df3ca390100d31f9aac23f2d8dfe0183a63987112675fc58af9a42f6874"),
    ("g2/components/bootloader/core_overlay/runtime_mspi_control_4251c0.c", "BSD-3-Clause", "g2/third_party/ambiqsuite-apollo510/LICENSE", "0770df5c1956b75715604d5788804eabfc293fc61d5dbbec498c6d379a63755f"),
    ("g2/components/apollo_main/ring_gesture/upstream/", "GPL-3.0-only", "g2/components/apollo_main/ring_gesture/LICENSE", "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"),
    ("g2/components/apollo_main/ring_gesture/DERIVATION.patch", "GPL-3.0-only", "g2/components/apollo_main/ring_gesture/LICENSE", "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"),
    ("g2/components/shared/cmbacktrace/", "MIT", "g2/third_party/cmbacktrace/LICENSE", "e8ed0e84184d2130bd1fcf5a52ce8c16b5bf338c272cab6bbd7993a9d723934e"),
    ("g2/components/shared/cordio/", "Apache-2.0", "g2/third_party/cordio/LICENSE.md", "682ae5978019e4ee9d439b300efb125525b2e4cc4181ebd1e676dd60dc69d7cd"),
    ("g2/components/shared/easylogger/", "MIT", "g2/third_party/easylogger/LICENSE", "4a7be67e9701d0344c62d1b92eed8f40b874d00d64a9ee6b3853eb47ef4ea7f9"),
    ("g2/components/shared/nanopb/", "Zlib", "g2/third_party/nanopb/LICENSE.txt", "e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d"),
    ("g2/components/shared/freertos/g2-tcb-v10.5.1.patch", "MIT", "g2/third_party/freertos-kernel/LICENSE.md", "508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1"),
)
LICENSE_EVIDENCE_MEMBERS = {
    "LICENSE": "MIT",
    "g2/components/apollo_main/core_overlay/LICENSE-mpaland-MIT": "MIT",
    "g2/components/apollo_main/ring_gesture/LICENSE": "GPL-3.0-only",
    "g2/third_party/ambiqsuite-apollo510/LICENSE": "BSD-3-Clause",
    "g2/third_party/cJSON/LICENSE": "MIT",
    "g2/third_party/cmbacktrace/LICENSE": "MIT",
    "g2/third_party/cordio/LICENSE.md": "Apache-2.0",
    "g2/third_party/cmsis-freertos/CMSIS_5/LICENSE.txt": "Apache-2.0",
    "g2/third_party/easylogger/LICENSE": "MIT",
    "g2/third_party/freertos-kernel/LICENSE.md": "MIT",
    "g2/third_party/freetype/LICENSE": "FTL",
    "g2/third_party/invensense-icm45608/LICENSE": "BSD-3-Clause",
    "g2/third_party/liblc3/LICENSE": "Apache-2.0",
    "g2/third_party/littlefs/LICENSE.md": "BSD-3-Clause",
    "g2/third_party/lz4/LICENSE": "BSD-2-Clause",
    "g2/third_party/nanopb/LICENSE.txt": "Zlib",
    "g2/third_party/ring-buffer/LICENSE": "MIT",
    "g2/third_party/tinyframe/LICENSE": "MIT",
}
LICENSE_EVIDENCE_MEMBER_SHA256 = {
    "LICENSE": "3a0f162b73b7d95cdb1de2395b4f0f4ad35eae3c8eb44f125d5c0db6bc811ea4",
    "g2/components/apollo_main/core_overlay/LICENSE-mpaland-MIT": "34a89d27aa3cc583d0c5fbb4017864f1ea9bc38c73388c0ae8a912a9cdb82c41",
    "g2/components/apollo_main/ring_gesture/LICENSE": "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986",
    "g2/third_party/ambiqsuite-apollo510/LICENSE": "0770df5c1956b75715604d5788804eabfc293fc61d5dbbec498c6d379a63755f",
    "g2/third_party/cJSON/LICENSE": "a36dda207c36db5818729c54e7ad4e8b0c6fba847491ba64f372c1a2037b6d5c",
    "g2/third_party/cmbacktrace/LICENSE": "e8ed0e84184d2130bd1fcf5a52ce8c16b5bf338c272cab6bbd7993a9d723934e",
    "g2/third_party/cordio/LICENSE.md": "682ae5978019e4ee9d439b300efb125525b2e4cc4181ebd1e676dd60dc69d7cd",
    "g2/third_party/cmsis-freertos/CMSIS_5/LICENSE.txt": "b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1",
    "g2/third_party/easylogger/LICENSE": "4a7be67e9701d0344c62d1b92eed8f40b874d00d64a9ee6b3853eb47ef4ea7f9",
    "g2/third_party/freertos-kernel/LICENSE.md": "508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1",
    "g2/third_party/freetype/LICENSE": "08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1",
    "g2/third_party/invensense-icm45608/LICENSE": "68bed9c72222b77b8744add292f524000661c6537d960adeaf740722b0b2637f",
    "g2/third_party/liblc3/LICENSE": "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "g2/third_party/littlefs/LICENSE.md": "0cb4ff1daf5fdc1359c6a6ee3116092f08fc100c9d58b1b77ab17bfd801f856d",
    "g2/third_party/lz4/LICENSE": "8b58c446121a109ccf32edc094bba3010a3d85e4ee3702950db55e4d3e87736c",
    "g2/third_party/nanopb/LICENSE.txt": "e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d",
    "g2/third_party/ring-buffer/LICENSE": "d96c4b746ca4a4b8a901e8e0b4ff2ae87026055d2799dcfc58632cd02f422825",
    "g2/third_party/tinyframe/LICENSE": "eb7b9df3ca390100d31f9aac23f2d8dfe0183a63987112675fc58af9a42f6874",
}
EXPLICIT_LICENSE_EVIDENCE_SCOPES = {
    **{
        f"g2/components/apollo_main/core_overlay/{name}": (
            "MIT",
            "g2/components/apollo_main/core_overlay/LICENSE-mpaland-MIT",
            "34a89d27aa3cc583d0c5fbb4017864f1ea9bc38c73388c0ae8a912a9cdb82c41",
        )
        for name in (
            "runtime_etoa.c",
            "runtime_format_out_reverse.c",
            "runtime_ftoa.c",
            "runtime_ntoa_format.c",
            "runtime_ntoa_integer.c",
            "runtime_printf_wrappers.c",
            "runtime_strnlen_s.c",
            "runtime_vsnprintf.c",
        )
    },
    "g2/components/shared/ring_buffer/runtime_ring_buffer.c": (
        "MIT",
        "g2/third_party/ring-buffer/LICENSE",
        "d96c4b746ca4a4b8a901e8e0b4ff2ae87026055d2799dcfc58632cd02f422825",
    ),
    "g2/components/apollo_main/core_overlay/pt_protocol_lc3_setup.c": (
        "Apache-2.0",
        "g2/third_party/liblc3/LICENSE",
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    ),
    "g2/components/bootloader/core_overlay/runtime_queue_get_416920.c": (
        "Apache-2.0",
        "g2/third_party/cmsis-freertos/CMSIS_5/LICENSE.txt",
        "b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1",
    ),
    "g2/components/bootloader/core_overlay/runtime_queue_put_4168a2.c": (
        "Apache-2.0",
        "g2/third_party/cmsis-freertos/CMSIS_5/LICENSE.txt",
        "b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1",
    ),
}
PROJECT_GENERATED_RECEIPT_MEMBERS = {
    *PUBLIC_EVIDENCE_RECEIPT_MEMBERS,
    "g2/tools/manifests/g2-dual-profile-ownership.json",
    "g2/components/shared/freetype/source_admission.json",
    "g2/components/shared/freetype_autofit/source_admission.json",
    "g2/components/shared/freetype_base/source_admission.json",
    "g2/components/shared/freetype_cff/source_admission.json",
    "g2/components/shared/freetype_psaux/source_admission.json",
    "g2/components/shared/freetype_pshinter/source_admission.json",
    "g2/components/shared/freetype_psnames/source_admission.json",
    "g2/components/shared/freetype_sfnt/source_admission.json",
    "g2/components/shared/freetype_smooth/source_admission.json",
    "g2/components/shared/freetype_truetype_map/source_admission.json",
    "g2/tools/manifests/g2-freetype-cff-source-admission.json",
    "g2/components/shared/liblc3/encoder_source_admission.json",
    "g2/components/shared/liblc3/ltpf_source_admission.json",
    "g2/tools/manifests/g2-case-final-classification-summary.json",
    "g2/tools/manifests/g2-case-final-function-frontier.tsv",
    "g2/tools/manifests/g2-case-final-gap-frontier.tsv",
    "g2/tools/manifests/g2-case-final-physical-byte-buckets.tsv",
    "g2/tools/manifests/g2-case-pure-helpers-admission-summary.json",
    "g2/tools/manifests/g2-case-pure-helpers-admission.tsv",
    "g2/tools/manifests/g2-case-register-policies-admission-summary.json",
    "g2/tools/manifests/g2-case-register-policies-admission.tsv",
    "g2/tools/manifests/g2-case-semantic-leaves-admission-summary.json",
    "g2/tools/manifests/g2-case-semantic-leaves-admission.tsv",
    "g2/tools/manifests/g2-case-source-image-summary.json",
    "g2/tools/manifests/g2-clkmgr-divider-candidate-summary.json",
    "g2/tools/manifests/g2-nemavg-stroke-caps-candidate-summary.json",
    "g2/tools/manifests/g2-pt-protocol-source-summary.json",
    "g2/tools/manifests/g2-touch-final-classification-summary.json",
    "g2/tools/manifests/g2-touch-final-frontier.tsv",
    "g2/tools/manifests/g2-touch-final-physical-byte-buckets.tsv",
    "g2/tools/manifests/g2-touch-final-source-candidate-provenance.tsv",
    "g2/tools/manifests/g2-touch-source-image-summary.json",
    "g2/tools/manifests/gx8002-source-readiness.tsv",
}
PROJECT_PREDECISION_RECEIPT_MEMBERS = {
    EM9305_PREDECISION_INPUT_MEMBER,
}
PROJECT_ROOT_MIT_MEMBERS = {
    "NOTICE",
    "README.md",
    *COMMUNITY_POLICY_MEMBERS,
    "g2/NOTICE-CORE-SOURCE.md",
    "g2/components/apollo_main/core_overlay/overlay.json",
    "g2/components/apollo_main/liblc3_ltpf/NOTICE.md",
    "g2/components/apollo_main/liblc3_ltpf/README.md",
    "g2/components/apollo_main/liblc3_ltpf/overlay.json",
    "g2/components/apollo_main/ring_gesture/NOTICE.md",
    "g2/components/apollo_main/ring_gesture/overlay.json",
    "g2/components/bootloader/core_overlay/overlay.json",
    "g2/components/case/source_image/README.md",
    "g2/components/em9305/source_image/README.md",
    "g2/components/shared/freertos/README.g2-tcb-patch.md",
    "g2/components/shared/freetype/README.md",
    "g2/components/shared/freetype_autofit/README.md",
    "g2/components/shared/freetype_base/README.md",
    "g2/components/shared/freetype_cff/README.md",
    "g2/components/shared/freetype_psaux/README.md",
    "g2/components/shared/freetype_pshinter/README.md",
    "g2/components/shared/freetype_psnames/README.md",
    "g2/components/shared/freetype_sfnt/README.md",
    "g2/components/shared/freetype_smooth/README.md",
    "g2/components/shared/freetype_truetype_map/README.md",
    "g2/components/shared/liblc3/README.md",
    "g2/components/shared/lvgl/README.md",
    "g2/components/touch/source_image/README.md",
    "g2/docs/community-source-distribution.md",
    "g2/docs/release-licensing-and-redistribution.md",
    "g2/manifests/g2-2.2.6.10-core-source.json",
    "g2/manifests/g2-2.2.6.10.json",
}
PROJECT_INFRASTRUCTURE_MIT_MEMBERS = {
    ".gitignore",
}
UPSTREAM_DATA_MEMBERS = {
    "g2/components/apollo_main/ring_gesture/PROVENANCE.json": "GPL-3.0-only",
}
FORBIDDEN_INVENSENSE_EDMP_MEMBERS = {
    "g2/third_party/invensense-icm45608/src/imu/edmp_prgm_ram_dispatch.h",
    "g2/third_party/invensense-icm45608/src/imu/edmp_prgm_ram_dispatch_over_gaf.h",
    "g2/third_party/invensense-icm45608/src/imu/edmp_prgm_ram_patch_calmag.h",
    "g2/third_party/invensense-icm45608/src/imu/edmp_prgm_ram_selftest.h",
    "g2/third_party/invensense-icm45608/src/imu/edmp_ram_aid_image.h",
    "g2/third_party/invensense-icm45608/src/imu/edmp_ram_aid_over_gaf_image.h",
    "g2/third_party/invensense-icm45608/src/imu/edmp_ram_all_quat_image.h",
    "g2/third_party/invensense-icm45608/src/imu/edmp_ram_b2s_image.h",
    "g2/third_party/invensense-icm45608/src/imu/edmp_ram_b2s_over_gaf_image.h",
    "g2/third_party/invensense-icm45608/src/imu/edmp_ram_mrm_image.h",
    "g2/third_party/invensense-icm45608/src/imu/inv_imu_edmp_all_quat_patch_key_offsets.h",
    "g2/third_party/invensense-icm45608/src/imu/inv_imu_edmp_calmag_defs.h",
    "g2/third_party/invensense-icm45608/src/imu/inv_imu_edmp_defs.h",
    "g2/third_party/invensense-icm45608/src/imu/inv_imu_edmp_patch_key_offsets.h",
    "g2/third_party/invensense-icm45608/src/imu/inv_imu_edmp_patches_defs.h",
}
LOCAL_INCLUDE = re.compile(
    rb'^\s*#\s*include\s*[<"]([^">\r\n]+)[">]',
    re.MULTILINE,
)
LONG_HEX_BODY = re.compile(rb"(?<![0-9A-Fa-f])[0-9A-Fa-f]{256,}(?![0-9A-Fa-f])")
DENSE_BYTE_TRANSCRIPT = re.compile(rb"(?:0x[0-9A-Fa-f]{1,2}\s*,\s*){16,}")
ESCAPED_BYTE_TRANSCRIPT = re.compile(
    rb"(?:\\x[0-9A-Fa-f]{2}(?:[\"']?\s*[\"']?)?){16,}"
)
OCTAL_ESCAPED_BYTE_TRANSCRIPT = re.compile(
    rb"(?:\\[0-7]{1,3}(?:[\"']?\s*[\"']?)?){16,}"
)
BASE64_BODY = re.compile(
    rb"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{172,}={0,2}(?![A-Za-z0-9+/])"
)
ADJACENT_C_STRING_RUN = re.compile(
    rb'(?:[LuU8]*"(?:\\.|[^"\\])*"\s*){2,}'
)
C_STRING_LITERAL_BODY = re.compile(rb'[LuU8]*"((?:\\.|[^"\\])*)"')
C_BRACE_BODY = re.compile(rb"\{([^{}]{1,262144})\}", re.DOTALL)
C_INTEGER_TOKEN = re.compile(
    rb"(?:0[xX][0-9A-Fa-f]+|0[bB][01]+|0[0-7]+|[0-9]+)[uUlL]*"
)
C_NUMERIC_ARRAY_SUFFIXES = frozenset({
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".S", ".s", ".asm", ".inc",
})
RAW_EXECUTABLE_DIRECTIVE = re.compile(rb"\.(?:byte|short|hword)\s+")
RAW_WIDE_EXECUTABLE_DIRECTIVE = re.compile(
    rb"(?mi)^\s*\.(word|long|4byte|quad|8byte)\s+([^\r\n;]+)"
)
LITERAL_HEX_CONSTRUCTOR = re.compile(
    rb"(?:bytes\.fromhex|binascii\.unhexlify)\(\s*[rubfRUBF]*"
    rb"[\"'][0-9A-Fa-f\s]{8,}[\"']\s*\)"
)

# These are reviewed semantic source tables, not retained executable payloads.
# Bind every accepted table to its exact byte-value sequence so any new table,
# omission, or mutation fails closed at public-export preflight.
REVIEWED_PUBLIC_NUMERIC_ARRAYS = {
    "g2/components/apollo_main/core_overlay/cordio_smp_legacy_sm.c": frozenset({
        (705, "3f64e85789a57cd89df7ab2430791d143db0567a016cf0632d76ff32af16728e"),
    }),
    "g2/components/apollo_main/core_overlay/cordio_smp_sc_sm.c": frozenset({
        (1495, "9438c7c72904056d2d0f6e9a4ce322cb1e52198738aef88558b35d5281bda801"),
    }),
    "g2/components/apollo_main/core_overlay/pt_protocol_procsr.c": frozenset({
        (66, "bbffa6eea2d387f0f2cee4c31f67703bdc3382d936ab432a9a86cb4d795ff61d"),
    }),
    "g2/components/apollo_main/core_overlay/runtime_style_prop_lookup_flags.c": frozenset({
        (138, "cd298adbcb31fff3ec4d1e90648c34b2d4c84536f5c6f9eb0b615b7dd9f970c5"),
    }),
    "g2/components/shared/cordio/runtime_ancc_profile_core.c": frozenset({
        (19, "e74402c56d8a56059b6a6b8b4cd67df2e5fb7e546c2a391fe6a4dad02375f1de"),
    }),
    "g2/components/shared/cordio/runtime_cordio_dm_main.c": frozenset({
        (90, "6a01e464d577fb127d88ad65cc81002de6041494b34f3a3784abb6fc716e528f"),
        (92, "e426e5a4c53400511a23c5898cee9703b727b7d7d68e9c40815d9a070678cb28"),
    }),
    "g2/components/shared/gx8002/runtime_gx8002_backup_runtime_boundary.c": frozenset({
        (32, "1b040007013340e070c9db184c2ad248c5f8abc206009e38e8f16acf2f67e766"),
    }),
    "g2/components/shared/gx8002/runtime_gx8002_image_a_sram_data_boundary.c": frozenset({
        (32, "f5c06c9c9722bfe9c6b7307398e48af1f3f1d261a33a757360d656ea86bce257"),
    }),
    "g2/components/shared/gx8002/runtime_gx8002_image_a_sram_text_boundary.c": frozenset({
        (32, "482126c5de33f7c819b56ae29ae8bfa9f91427db6ffeca9db410d1748f135c95"),
    }),
    "g2/components/shared/gx8002/runtime_gx8002_image_a_stage1_boundary.c": frozenset({
        (32, "77ab60663c9497a83f7a5e18f48baf89396ac8fd08851702adda0aee16ced8a6"),
    }),
    "g2/components/shared/gx8002/runtime_gx8002_image_a_xip_boundary.c": frozenset({
        (32, "cbf96377a30bafc6b19f8aa331af397a8466230c2d5f68e0b633d78abdf04593"),
    }),
    "g2/components/shared/gx8002/runtime_gx8002_image_b_sram_data_boundary.c": frozenset({
        (32, "ce8aa5f85aeada7c688becb5e0b41799af8a8fc45104f14380bb80c7bf2763c3"),
    }),
    "g2/components/shared/gx8002/runtime_gx8002_image_b_stage1_boundary.c": frozenset({
        (32, "211ba02a7b7496688fd6093fe025a63d2a4ddcff50f2adc2dec80c4d224ee6f0"),
    }),
    "g2/components/shared/gx8002/runtime_gx8002_kws_command_boundary.c": frozenset({
        (32, "f71bf9b5f3f7e2de359e867adba1b7786694819fff08a7c0d54708dcd9851e80"),
    }),
    "g2/components/shared/gx8002/runtime_gx8002_kws_model_boundary.c": frozenset({
        (32, "8cfe78654a9cca9efa9faa7de3aa2a3e6bbcad87e2e1e33e877e6c80074e2300"),
    }),
    "g2/components/shared/gx8002/runtime_gx8002_uart_boot_stage1_boundary.c": frozenset({
        (32, "4d543a88bb963991d3381ab4ba5bebba4bf55a7d3c4ea2c69bd73118b01ae064"),
    }),
    "g2/components/shared/gx8002/runtime_gx8002_uart_boot_stage2_boundary.c": frozenset({
        (32, "3071e67df6cf82c97bd556bebc9903652c46585332a7ba86be1c85c740caa111"),
    }),
    "g2/tests/fixtures/pt_protocol_board_backend_host.c": frozenset({
        (21, "776285c2deb40fbb9d78f96273fb22eb15e231c20c4025fe33db5773b40c97c2"),
    }),
    "g2/tests/fixtures/runtime_case_semantic_leaves_host.c": frozenset({
        (16, "3969faf4ef02f8128027952e93e455ee50f3d698ad6144e2aeecef0637501b26"),
    }),
    "g2/third_party/lz4/lz4.c": frozenset({
        (128, "14c30dfcb73a41002efe72d5e14bf3170d0514fd0bb3ce0699e6e29e19b448fe"),
    }),
}
SPDX_COMMENT = re.compile(
    r"(?m)^\s*(?:\#|//|/\*+|\*)[^\r\n]*?SPDX-License-Identifier:\s*"
    r"([A-Za-z0-9.+-]+(?:\s+(?:OR|AND|WITH)\s+[A-Za-z0-9.+-]+)*)"
    r"\s*(?:\*/)?\s*$"
)
SAFE_ARCHIVE_PATH = re.compile(r"[A-Za-z0-9._/+@-]+")
PRIVATE_KEY_BLOCK = re.compile(
    rb"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
)
RESTRICTED_SOURCE_NOTICE = re.compile(
    # Split signature words so this detector's own source does not contain the
    # complete restricted notice it is required to reject from every member.
    b"use, reproduction, disclosure or distri" + b"bution[\\s\\S]{0,240}"
    + b"without an express license agree" + b"ment[\\s\\S]{0,120}strictly prohibited",
    re.IGNORECASE,
)
SANITIZED_APOLLO_OVERLAY = "g2/components/apollo_main/core_overlay/overlay.json"
SANITIZED_LIBLC3_OVERLAY = "g2/components/apollo_main/liblc3_ltpf/overlay.json"
SANITIZED_RING_OVERLAY = "g2/components/apollo_main/ring_gesture/overlay.json"
NEMAVG_COORDINATOR_FUNCTION = "open_cfw_nemavg_draw_caps_dispatch"
NEMAVG_COORDINATOR_SOURCE_MEMBER = (
    "g2/components/apollo_main/core_overlay/"
    "runtime_nemavg_draw_caps_dispatch.c"
)
NEMAVG_COORDINATOR_SOURCE_IDENTITY = {
    "evidence": "docs/research/g2-nemavg-stroke-caps-source-candidate.md",
    "license": "MIT",
    "origin": (
        "clean-room NemaVG draw_caps coordinator over authenticated retained "
        "draw_start_cap, draw_end_cap, and NemaVG error-provider ABIs"
    ),
    "path": (
        "components/apollo_main/core_overlay/"
        "runtime_nemavg_draw_caps_dispatch.c"
    ),
    "sha256": "aa27ae41426f34111174d9520812c795ec59b0915aa474672978eccaa66c9966",
    "size": 2_304,
}
NEMAVG_COORDINATOR_PATCH = {
    "branch": "b_w",
    "expected_sha256": (
        "7487038aa5bf05ee5c13296625a2ddf2c7ea592f5dc975661b7f6e0c7a3c1c27"
    ),
    "expected_size": 3_306,
    "name": "replace_nemavg_stroke_caps_03",
    "runtime_address": 0x0051C5EC,
    "target_function": NEMAVG_COORDINATOR_FUNCTION,
}
NEMAVG_ENDPOINT_PATCHES = (
    {
        "branch": "b_w",
        "expected_sha256":
            "549fd3c4e21f1074d6f2b04309e72283b3f85b575f41bd31fc4718f7a63e3382",
        "expected_size": 1_668,
        "name": "replace_nemavg_stroke_caps_01",
        "runtime_address": 0x0051B8F0,
        "target_function": "open_cfw_nemavg_draw_start_cap_endpoint",
    },
    {
        "branch": "b_w",
        "expected_sha256":
            "d022571f745517bf7494d69d79e5c1ba934faf8dc65c0cb6f465d4f36fb81d56",
        "expected_size": 1_640,
        "name": "replace_nemavg_stroke_caps_02",
        "runtime_address": 0x0051BF7C,
        "target_function": "open_cfw_nemavg_draw_end_cap_endpoint",
    },
)
NEMAVG_PRODUCTION_PATCHES = (*NEMAVG_ENDPOINT_PATCHES, NEMAVG_COORDINATOR_PATCH)
NEMAVG_ENDPOINT_ENTRIES = frozenset({0x0051B8F0, 0x0051BF7C})
NEMAVG_ENDPOINT_TARGET_FUNCTIONS = frozenset({
    "open_cfw_nemavg_draw_start_cap_endpoint",
    "open_cfw_nemavg_draw_end_cap_endpoint",
    "open_cfw_nemavg_draw_start_cap",
    "open_cfw_nemavg_draw_end_cap",
    "open_cfw_nemavg_draw_caps",
})
NEMAVG_ROUTE_TARGET_FUNCTIONS = (
    NEMAVG_ENDPOINT_TARGET_FUNCTIONS | {NEMAVG_COORDINATOR_FUNCTION}
)
NEMAVG_PRODUCTION_FUNCTIONS = frozenset({
    "open_cfw_nemavg_draw_start_cap_endpoint",
    "open_cfw_nemavg_draw_end_cap_endpoint",
    NEMAVG_COORDINATOR_FUNCTION,
})
NEMAVG_PRODUCTION_SOURCE_MEMBER = (
    "g2/components/apollo_main/core_overlay/"
    "runtime_nemavg_stroke_cap_endpoints.c"
)
NEMAVG_PRODUCTION_SOURCE_IDENTITY = {
    "evidence": "docs/research/g2-nemavg-stroke-caps-source-candidate.md",
    "license": "MIT",
    "origin": (
        "clean-room NemaVG 1.1.8 stroke-cap geometry over authenticated G2 "
        "context layout and retained public NemaGFX raster-provider ABIs"
    ),
    "path": (
        "components/apollo_main/core_overlay/"
        "runtime_nemavg_stroke_cap_endpoints.c"
    ),
    "sha256": "33c9292bb52e276982e9b6c4c51bc02d9381eec98f50f223c876c7f691a986a4",
    "size": 15_166,
}
NEMAVG_CANDIDATE_SUMMARY_MEMBER = (
    "g2/tools/manifests/g2-nemavg-stroke-caps-candidate-summary.json"
)
NEMAVG_CANDIDATE_SOURCE_MEMBERS = frozenset({
    "g2/components/shared/lvgl/runtime_nemavg_stroke_caps_candidate.c",
    "g2/components/shared/lvgl/runtime_nemavg_stroke_caps_candidate.h",
})
NEMAVG_PUBLIC_MEMBERS = frozenset({
    NEMAVG_PRODUCTION_SOURCE_MEMBER,
    *NEMAVG_CANDIDATE_SOURCE_MEMBERS,
    NEMAVG_CANDIDATE_SUMMARY_MEMBER,
    "g2/tests/test_runtime_nemavg_stroke_caps_candidate.py",
    "g2/tests/fixtures/runtime_nemavg_stroke_caps_host.c",
})
NEMAVG_FORBIDDEN_PUBLIC_MEMBERS = frozenset({
    "g2/tools/integrate_g2_nemavg_draw_caps_dispatch.py",
    "g2/tests/test_integrate_g2_nemavg_draw_caps_dispatch.py",
})
RELOCATED_PUBLIC_SOURCES = {
    "g2/community/Makefile": "Makefile",
    "g2/community/make.sh": "make.sh",
    "g2/docs/community-archive-README.md": "README.md",
    "g2/research/candidates/freertos_scheduler_port_trio.c": (
        "g2/components/apollo_main/core_overlay/freertos_scheduler_port_trio.c"
    ),
    "g2/research/candidates/freertos_scheduler_port_trio.h": (
        "g2/components/apollo_main/core_overlay/freertos_scheduler_port_trio.h"
    ),
}


class CommunityBundleError(RuntimeError):
    pass


_UNCONSTRAINED_PRIOR = object()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fsync_directory(path: Path) -> None:
    descriptor = _open_directory_path(path)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _open_directory_path(path: Path, *, create: bool = False) -> int:
    """Open an absolute directory chain without following any component link."""
    absolute = Path(os.path.abspath(path))
    parts = absolute.parts
    if not parts or not absolute.anchor:
        raise CommunityBundleError(f"directory path is not absolute: {path}")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(absolute.anchor, flags)
    try:
        for part in parts[1:]:
            try:
                child = os.open(part, flags, dir_fd=descriptor)
            except FileNotFoundError:
                if not create:
                    raise
                try:
                    os.mkdir(part, 0o755, dir_fd=descriptor)
                except FileExistsError:
                    pass
                child = os.open(part, flags, dir_fd=descriptor)
            metadata = os.fstat(child)
            if not stat.S_ISDIR(metadata.st_mode):
                os.close(child)
                raise CommunityBundleError(
                    f"directory path component is not a directory: {path}"
                )
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _ensure_safe_directory_path(path: Path, *, create: bool = False) -> Path:
    absolute = Path(os.path.abspath(path))
    try:
        descriptor = _open_directory_path(absolute, create=create)
    except OSError as error:
        raise CommunityBundleError(
            f"directory path could not be opened safely: {path}"
        ) from error
    os.close(descriptor)
    return absolute


def _physical_temporary_root() -> Path:
    """Return the platform temp root without a symlinked lexical prefix.

    macOS exposes its default per-user temporary directory below ``/var``,
    while ``/var`` itself is a system symlink to ``/private/var``.  Internal
    temporary workspaces must use the physical path so the normal no-follow
    directory walk does not reject the platform default before doing any work.
    User-supplied archive, package, and workspace paths remain subject to the
    strict lexical no-symlink policy.
    """
    try:
        root = Path(tempfile.gettempdir()).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise CommunityBundleError(
            "platform temporary directory could not be resolved safely"
        ) from error
    return _ensure_safe_directory_path(root)


def _toolchain_profile_contract() -> dict[str, str]:
    """Return profile/version contracts shared by both community builders."""
    shared: dict[str, str] | None = None
    for path in TOOLCHAIN_CONFIGS:
        config = _read_json_path(path)
        if not isinstance(config, dict):
            raise CommunityBundleError(
                f"community toolchain config is invalid: {path}"
            )
        canonical = config.get("toolchain")
        alternates = config.get("toolchain_profiles")
        if not isinstance(canonical, dict) or not isinstance(alternates, dict):
            raise CommunityBundleError(
                f"community toolchain profiles are unavailable: {path}"
            )
        profiles = {
            "apple-clang": canonical.get("reviewed_version_prefix"),
            **{
                str(name): row.get("reviewed_version_prefix")
                for name, row in alternates.items()
                if isinstance(row, dict)
            },
        }
        if (
            not profiles
            or any(
                not isinstance(prefix, str) or not prefix
                for prefix in profiles.values()
            )
        ):
            raise CommunityBundleError(
                f"community toolchain profile contract is invalid: {path}"
            )
        if shared is None:
            shared = profiles
        elif profiles != shared:
            raise CommunityBundleError(
                "bootloader and Apollo-main toolchain profiles differ"
            )
    if shared is None:
        raise CommunityBundleError("community toolchain profile contract is empty")
    return shared


def _dependency_executable(command: str, label: str) -> str:
    if not isinstance(command, str) or not command.strip():
        raise CommunityBundleError(f"{label} executable is not configured")
    resolved = shutil.which(command)
    if resolved is None:
        raise CommunityBundleError(f"{label} executable is unavailable: {command}")
    return resolved


def _dependency_output(command: list[str], label: str) -> str:
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise CommunityBundleError(f"cannot run {label}") from error
    output = result.stdout.strip()
    if result.returncode or not output:
        detail = (result.stderr or result.stdout).strip()
        raise CommunityBundleError(
            f"{label} preflight failed" + (f": {detail}" if detail else "")
        )
    return output


def preflight_local_environment(
    clang: str | None = None,
    toolchain_profile: str | None = None,
    make_executable: str = "make",
) -> dict[str, Any]:
    """Fail quickly when the extracted-tree software prerequisites are absent."""
    if sys.version_info < MINIMUM_PYTHON:
        raise CommunityBundleError(
            "community build requires Python "
            f"{MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]} or newer"
        )
    if os.name != "posix":
        raise CommunityBundleError("community build requires a POSIX host")
    make_path = _dependency_executable(make_executable, "GNU make")
    make_version = _dependency_output([make_path, "--version"], "GNU make")
    make_line = make_version.splitlines()[0]
    if not make_line.startswith("GNU Make "):
        raise CommunityBundleError(
            f"community build requires GNU make, found: {make_line}"
        )

    compiler = clang or os.environ.get("OPENCFW_CLANG")
    if not compiler:
        for candidate in (
            "/usr/bin/clang",
            "/home/linuxbrew/.linuxbrew/opt/llvm/bin/clang",
            "clang",
        ):
            compiler = shutil.which(candidate)
            if compiler:
                break
    clang_path = _dependency_executable(compiler or "", "reviewed Clang")
    clang_version = _dependency_output(
        [clang_path, "--version"], "reviewed Clang"
    ).splitlines()[0]
    profiles = _toolchain_profile_contract()
    matching = [
        name for name, prefix in profiles.items()
        if clang_version.startswith(prefix)
    ]
    if toolchain_profile is None:
        if len(matching) != 1:
            raise CommunityBundleError(
                f"no unique reviewed toolchain profile matches {clang_version!r}"
            )
        toolchain_profile = matching[0]
    if toolchain_profile not in profiles:
        raise CommunityBundleError(
            f"unknown reviewed toolchain profile: {toolchain_profile}"
        )
    if toolchain_profile not in matching:
        raise CommunityBundleError(
            f"compiler version does not match {toolchain_profile}: {clang_version}"
        )
    resource_dir = _dependency_output(
        [clang_path, "--no-default-config", "-print-resource-dir"],
        "Clang resource directory",
    ).splitlines()[-1]
    resource_include = Path(resource_dir) / "include"
    if not resource_include.is_dir():
        raise CommunityBundleError(
            f"Clang builtin include directory is unavailable: {resource_include}"
        )
    return {
        "python": {
            "executable": sys.executable,
            "version": platform_python_version(),
        },
        "make": {"executable": make_path, "version": make_line},
        "clang": {
            "executable": clang_path,
            "version": clang_version,
            "resource_include": str(resource_include),
        },
        "toolchain_profile": toolchain_profile,
        **_software_only_operation_receipt(),
    }


def platform_python_version() -> str:
    return ".".join(str(item) for item in sys.version_info[:3])


def _forbidden_directory_part(part: str) -> bool:
    return (
        part in FORBIDDEN_PARTS
        or part.startswith("build-")
        or part.startswith("_test")
        or part.startswith(".tmp")
    )


def _allowed_source_file(path: Path) -> bool:
    if path.is_symlink():
        return False
    relative = path.relative_to(REPOSITORY_ROOT)
    if any(_forbidden_directory_part(part) for part in relative.parts):
        return False
    if path.name in FORBIDDEN_FILENAMES or path.name.lower() in FORBIDDEN_SECRET_FILENAMES:
        return False
    if path.suffix.lower() in FORBIDDEN_SUFFIXES | FORBIDDEN_SECRET_SUFFIXES:
        return False
    return (
        path.suffix in SOURCE_SUFFIXES
        or path.name in {"Makefile", "make.sh", "LICENSE", "NOTICE"}
        or path.name.startswith("LICENSE")
        or relative.as_posix() == ".gitignore"
    )


def _configured_include_dir_names(root: Path = ROOT) -> list[str]:
    directories: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "include_dirs" and isinstance(child, list):
                    for relative in child:
                        if not isinstance(relative, str):
                            continue
                        pure = PurePosixPath(relative)
                        if (
                            pure.is_absolute()
                            or pure.as_posix() != relative
                            or ".." in pure.parts
                            or not pure.parts
                        ):
                            raise CommunityBundleError(
                                f"unsafe configured include directory: {relative!r}"
                            )
                        directories.add(relative)
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for relative in BUILD_OVERLAY_RECIPES:
        try:
            visit(_read_json_path(root / relative))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise CommunityBundleError(
                f"overlay include-directory recipe is invalid: {relative}"
            ) from error
    return sorted(directories)


def _configured_include_dirs() -> list[Path]:
    return [
        _ensure_safe_directory_path(ROOT / relative)
        for relative in _configured_include_dir_names()
    ]


def _source_include_contexts() -> dict[Path, set[tuple[Path, ...]]]:
    """Map compiled source records to their exact ordered include paths."""
    contexts: dict[Path, set[tuple[Path, ...]]] = {}

    def include_context(toolchain: Any, profile: Any = None) -> tuple[Path, ...]:
        names = toolchain.get("include_dirs", []) if isinstance(toolchain, dict) else []
        if isinstance(profile, dict) and "include_dirs" in profile:
            names = profile["include_dirs"]
        if not isinstance(names, list) or any(not isinstance(name, str) for name in names):
            raise CommunityBundleError("source toolchain include_dirs is invalid")
        return tuple(
            _ensure_safe_directory_path(ROOT / name) for name in names
        )

    def add(source: Any, owner: dict[str, Any]) -> None:
        if not isinstance(source, dict) or not isinstance(source.get("path"), str):
            return
        path = Path(os.path.abspath(ROOT / source["path"]))
        try:
            path.relative_to(ROOT)
        except ValueError as error:
            raise CommunityBundleError(
                f"source include context escapes G2 root: {source['path']}"
            ) from error
        # Main/boot overlays nest include_dirs under ``toolchain``; bounded
        # post-link providers such as liblc3 keep them at recipe top level.
        base_toolchain = owner.get("toolchain", owner)
        contexts.setdefault(path, set()).add(include_context(base_toolchain))
        profiles = owner.get("toolchain_profiles", {})
        if isinstance(profiles, dict):
            for profile in profiles.values():
                contexts[path].add(include_context(base_toolchain, profile))

    for relative in BUILD_OVERLAY_RECIPES:
        config = _read_json_path(ROOT / relative)
        for source in config.get("sources", []):
            add(source, config)

        def visit(value: Any) -> None:
            if isinstance(value, dict):
                if "source" in value:
                    add(value.get("source"), value)
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(config)
    return contexts


def _local_include_closure(initial: set[Path]) -> set[Path]:
    """Add every repository-local C/assembly include needed by build sources."""
    selected = set(initial)
    source_contexts = _source_include_contexts()
    pending = [
        (source, context)
        for source in initial
        for context in (
            source_contexts.get(Path(os.path.abspath(source))) or {()}
        )
    ]
    visited: set[tuple[Path, tuple[Path, ...]]] = set()
    while pending:
        source, include_dirs = pending.pop()
        visit_key = (Path(os.path.abspath(source)), include_dirs)
        if visit_key in visited:
            continue
        visited.add(visit_key)
        if source.suffix not in SOURCE_SUFFIXES:
            continue
        source_data = _read_regular_source_once(source)
        for raw_name in LOCAL_INCLUDE.findall(source_data):
            try:
                name = raw_name.decode("utf-8")
            except UnicodeDecodeError as error:
                raise CommunityBundleError(
                    f"non-UTF-8 quoted include in {source}"
                ) from error
            for unresolved in (
                source.parent / name,
                *(directory / name for directory in include_dirs),
                ROOT / name,
            ):
                candidate = Path(os.path.abspath(unresolved))
                try:
                    candidate.relative_to(REPOSITORY_ROOT)
                except ValueError:
                    continue
                if not os.path.lexists(candidate):
                    continue
                # Authenticate the lexical path now.  Resolving an include
                # alias would silently add only its symlink target to the ZIP,
                # leaving the extracted build with a missing dependency.
                _read_regular_source_once(candidate)
                if not _allowed_source_file(candidate):
                    raise CommunityBundleError(
                        f"quoted source dependency is forbidden: {candidate}"
                    )
                if candidate not in selected:
                    selected.add(candidate)
                pending.append((candidate, include_dirs))
                break
    return selected


def _touch_admission_members_from_summary(
    summary: Any,
) -> tuple[tuple[str, ...], dict[str, str]]:
    """Return the exact authenticated public Touch admission receipt census."""
    if (
        not isinstance(summary, dict)
        or summary.get("schema_version") != 2
        or summary.get("classification_complete") is not True
    ):
        raise CommunityBundleError(
            "Touch final-classification receipt is invalid"
        )
    rows = summary.get("admission_manifests")
    if not isinstance(rows, list) or len(rows) != 26:
        raise CommunityBundleError("Touch admission receipt census changed")
    names: list[str] = []
    entry_count = 0
    for row in rows:
        if (
            not isinstance(row, dict)
            or set(row) != {"entries", "manifest"}
            or not isinstance(row["entries"], int)
            or isinstance(row["entries"], bool)
            or row["entries"] < 1
            or not isinstance(row["manifest"], str)
        ):
            raise CommunityBundleError("Touch admission receipt row is invalid")
        name = row["manifest"]
        pure = PurePosixPath(name)
        if (
            pure.name != name
            or pure.suffix != ".tsv"
            or not name.startswith("g2-touch-")
            or name.endswith("-unavailable.tsv")
        ):
            raise CommunityBundleError(
                "Touch admission receipt path is not public"
            )
        names.append(name)
        entry_count += row["entries"]
    if (
        tuple(names) != TOUCH_ADMISSION_RECEIPT_FILENAMES
        or len(set(names)) != len(names)
        or summary.get("admission_entry_count") != entry_count
    ):
        raise CommunityBundleError("Touch admission receipt census changed")
    analysis_inputs = summary.get("analysis_inputs")
    generation = summary.get("generation_receipt")
    generation_inputs = (
        generation.get("analysis_inputs")
        if isinstance(generation, dict)
        else None
    )
    if (
        not isinstance(analysis_inputs, dict)
        or not isinstance(analysis_inputs.get("path_sha256"), dict)
        or generation_inputs != analysis_inputs
    ):
        raise CommunityBundleError(
            "Touch admission receipt authentication is invalid"
        )
    path_sha256 = analysis_inputs["path_sha256"]
    digests: dict[str, str] = {}
    for member in TOUCH_ADMISSION_RECEIPT_MEMBERS:
        relative = member.removeprefix("g2/")
        digest = path_sha256.get(relative)
        if (
            not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        ):
            raise CommunityBundleError(
                f"Touch admission receipt identity is missing: {member}"
            )
        digests[member] = digest
    return TOUCH_ADMISSION_RECEIPT_MEMBERS, digests


def _touch_public_analysis_inputs_from_summary(
    summary: Any,
) -> dict[str, str]:
    """Map the 68 authenticated non-donor Touch inputs to archive paths."""
    _touch_admission_members_from_summary(summary)
    analysis_inputs = summary["analysis_inputs"]
    path_sha256 = analysis_inputs["path_sha256"]
    if (
        analysis_inputs.get("path_count") != 69
        or len(path_sha256) != 69
        or path_sha256.get(TOUCH_OFFICIAL_DONOR_INPUT)
        != TOUCH_OFFICIAL_DONOR_SHA256
    ):
        raise CommunityBundleError(
            "Touch direct-input receipt census changed"
        )
    safe: dict[str, str] = {}
    for relative, digest in path_sha256.items():
        if relative == TOUCH_OFFICIAL_DONOR_INPUT:
            continue
        if (
            not isinstance(relative, str)
            or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        ):
            raise CommunityBundleError("Touch direct-input row is invalid")
        pure = PurePosixPath(relative)
        archive_path = f"g2/{relative}"
        if (
            pure.is_absolute()
            or pure.as_posix() != relative
            or ".." in pure.parts
            or not pure.parts
            or not _allowed_archive_file(PurePosixPath(archive_path))
        ):
            raise CommunityBundleError(
                f"Touch direct input is not public-safe: {relative}"
            )
        safe[archive_path] = digest
    if len(safe) != 68:
        raise CommunityBundleError(
            "Touch non-donor direct-input census changed"
        )
    analyzers = tuple(sorted(
        path for path in safe
        if path.startswith("g2/tools/analyze_") and path.endswith(".py")
    ))
    if analyzers != tuple(sorted(TOUCH_PUBLIC_ANALYZER_MEMBERS)):
        raise CommunityBundleError(
            "Touch public analyzer-chain census changed"
        )
    return dict(sorted(safe.items()))


def _repository_public_evidence_members() -> frozenset[str]:
    summary = _read_json_path(
        REPOSITORY_ROOT / TOUCH_FINAL_CLASSIFICATION_RECEIPT
    )
    members, digests = _touch_admission_members_from_summary(summary)
    public_inputs = _touch_public_analysis_inputs_from_summary(summary)
    for member, expected_digest in public_inputs.items():
        data = _read_regular_source_once(REPOSITORY_ROOT / member)
        if _sha256(data) != expected_digest:
            raise CommunityBundleError(
                f"Touch public direct-input identity changed: {member}"
            )
    if any(digests[member] != public_inputs[member] for member in members):
        raise CommunityBundleError(
            "Touch admission and direct-input identities conflict"
        )
    return frozenset(PUBLIC_EVIDENCE_RECEIPT_MEMBERS | set(public_inputs))


def _verify_em9305_public_readiness_receipts(
    payload_by_path: dict[str, bytes],
) -> None:
    for path, (expected_size, expected_digest) in (
        EM9305_FINAL_READINESS_IDENTITIES.items()
    ):
        data = payload_by_path.get(path)
        if (
            not isinstance(data, bytes)
            or len(data) != expected_size
            or _sha256(data) != expected_digest
        ):
            raise CommunityBundleError(
                f"final EM9305 readiness receipt identity changed: {path}"
            )
    if EM9305_PREDECISION_INPUT_MEMBER not in payload_by_path:
        raise CommunityBundleError(
            "EM9305 pre-decision provenance input is absent"
        )
    summary_path = (
        "g2/tools/manifests/em9305-final-source-readiness-summary.json"
    )
    ledger_path = "g2/tools/manifests/em9305-final-source-readiness.tsv"
    try:
        summary = json.loads(payload_by_path[summary_path])
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise CommunityBundleError(
            "final EM9305 readiness summary is invalid"
        ) from error
    if not isinstance(summary, dict):
        raise CommunityBundleError(
            "final EM9305 readiness summary shape is invalid"
        )
    expected_ledger_size, expected_ledger_digest = (
        EM9305_FINAL_READINESS_IDENTITIES[ledger_path]
    )
    if summary.get("ledger") != {
        "path": PurePosixPath(ledger_path).name,
        "size": expected_ledger_size,
        "sha256": expected_ledger_digest,
    }:
        raise CommunityBundleError(
            "final EM9305 readiness ledger binding changed"
        )
    buckets = summary.get("completion_buckets")
    if (
        summary.get("schema_version") != 7
        or summary.get("status")
        != "accounting-complete-source-incomplete"
        or summary.get("component_bytes") != 212_984
        or summary.get("residual_span_count") != 175
        or summary.get("residual_bytes") != 33_658
        or summary.get("unclassified_spans") != 0
        or summary.get("unclassified_bytes") != 0
        or summary.get("source_complete") is not False
        or summary.get("release") is not False
        or summary.get("candidate_production_routed") is not True
        or summary.get("hardware_operations") != []
        or isinstance(summary.get("hardware_operations"), bool)
        or summary.get("hardware_validation")
        != "blocked by unavailable physical evidence"
        or buckets != {
            "production_source": 1_174,
            "generated_or_reconstructible": 1_226,
            "candidate_source_not_routed": 0,
            "typed_retained_or_external": 210_584,
            "unclassified": 0,
        }
        or sum(buckets.values()) != 212_984
    ):
        raise CommunityBundleError(
            "final EM9305 readiness semantics changed"
        )
    arc_audit = summary.get("metaware_runtime_audit")
    if arc_audit != {
        "additive_to_residual_accounting": False,
        "arcv2_em_build_receipt":
            "tools/manifests/em9305-arc-candidate-build-summary.json",
        "arcv2_em_forbidden_runtime_imports": [],
        "arcv2_em_target_compiled": True,
        "arcv2_em_undefined_symbols": [],
        "candidate_production_routed": True,
        "candidate_source_bytes": 980,
        "hardware_validation": "blocked by unavailable physical evidence",
        "remaining_software_blockers": [],
        "status": "production-routed",
    }:
        raise CommunityBundleError(
            "final EM9305 ARCv2 EM audit semantics changed"
        )
    qpc_audit = summary.get("qpc_supporting_audit")
    if qpc_audit != {
        "additive_to_residual_accounting": False,
        "arcv2_em_build_receipt":
            "tools/manifests/em9305-qpc-component-build-summary.json",
        "arcv2_em_forbidden_runtime_imports": [],
        "arcv2_em_linked_object_sha256":
            "c1aa5370945e41afcb29750174fd4531def9a887d37a0f620461eeabad587ad9",
        "arcv2_em_target_linked": True,
        "arcv2_em_translation_units": 10,
        "arcv2_em_undefined_symbols": [],
        "cluster_partition_complete": True,
        "exact_vendor_checkout_proven": False,
        "hardware_validation": "blocked by unavailable physical evidence",
        "hook_pointer_count": 9,
        "install_placement_resolved": False,
        "portable_function_bytes": 2_450,
        "portable_function_count": 22,
        "production_routed": False,
        "required_hardware_providers": [
            "critical_entry", "critical_exit", "interrupt_disable",
            "interrupt_enable", "isr_context", "PalUartResume",
            "VoltMon_DoMeasurement",
        ],
        "selected_release_tag": "v6.5.1",
    }:
        raise CommunityBundleError(
            "final EM9305 QP/C target-link semantics changed"
        )
    qpc_hook_audit = summary.get("qpc_hook_provider_audit")
    if qpc_hook_audit != {
        "additive_to_residual_accounting": False,
        "candidate_production_routed": False,
        "exact_provider_source_available": False,
        "hardware_dependent_providers": [
            "PalUartResume", "VoltMon_DoMeasurement",
        ],
        "hardware_validation": "blocked by unavailable physical evidence",
        "named_providers": [
            "PalUartResume", "VoltMon_DoMeasurement", "wsfOsRunIdleTasks",
        ],
        "redistribution_authority_resolved": False,
        "software_provider_gaps": [],
        "software_provider_source_available": True,
        "status": "candidate-qualified-software-provider-two-hardware",
        "unresolved_providers": [],
        "wsf_idle_semantics": {
            "callback_capacity": 3,
            "callback_count_offset": 12,
            "clean_room_header":
                "components/shared/em9305/runtime_wsf_idle_tasks.h",
            "clean_room_source":
                "components/shared/em9305/runtime_wsf_idle_tasks.c",
            "pending_offset": 13,
            "production_routed": False,
            "result": "ordered_nonnull_callback_bit0_or",
            "stock_bytes": 58,
            "stock_entry": 0x00333D7C,
        },
    }:
        raise CommunityBundleError(
            "final EM9305 QP/C provider semantics changed"
        )
    deployment_audit = summary.get("deployment_package_audit")
    if deployment_audit != {
        "additive_to_residual_accounting": False,
        "authenticated_stock_sha256":
            "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9",
        "authenticated_stock_size": 211_948,
        "build_receipt":
            "components/em9305/source_overlay/build/build-report.json",
        "erase_sector_count": 29,
        "hardware_operations": [],
        "hardware_validation": "blocked by unavailable physical evidence",
        "production_routed": True,
        "provider_sha256":
            "1a4ccc61cae6e9b90d0eb3d694179d726c935171788167d28ea45060d7431c42",
        "provider_size": 212_984,
        "record_count": 4,
        "remaining_software_blockers": [],
        "remaining_source_completeness_blockers": [
            "210584 typed retained or external provider bytes require unavailable exact provider source and redistribution authority",
        ],
        "software_package_complete": True,
        "software_wrapper_complete": True,
        "source_image_complete": False,
        "source_records_complete": False,
        "status": "mixed-provider-production-routed-source-incomplete",
        "stock_roundtrip_byte_exact": True,
    }:
        raise CommunityBundleError(
            "final EM9305 deployment-package semantics changed"
        )
    arc_receipt = payload_by_path.get(EM9305_ARC_BUILD_RECEIPT)
    arc_size, arc_digest = EM9305_ARC_BUILD_RECEIPT_IDENTITY
    if (
        not isinstance(arc_receipt, bytes)
        or len(arc_receipt) != arc_size
        or _sha256(arc_receipt) != arc_digest
    ):
        raise CommunityBundleError(
            "final EM9305 ARCv2 EM build receipt identity changed"
        )
    qpc_receipt = payload_by_path.get(EM9305_QPC_BUILD_RECEIPT)
    qpc_size, qpc_digest = EM9305_QPC_BUILD_RECEIPT_IDENTITY
    if (
        not isinstance(qpc_receipt, bytes)
        or len(qpc_receipt) != qpc_size
        or _sha256(qpc_receipt) != qpc_digest
    ):
        raise CommunityBundleError(
            "final EM9305 QP/C build receipt identity changed"
        )
    package_receipt = payload_by_path.get(EM9305_RECORD_PACKAGE_RECEIPT)
    package_size, package_digest = EM9305_RECORD_PACKAGE_RECEIPT_IDENTITY
    if (
        not isinstance(package_receipt, bytes)
        or len(package_receipt) != package_size
        or _sha256(package_receipt) != package_digest
    ):
        raise CommunityBundleError(
            "final EM9305 record-package receipt identity changed"
        )

    def reject_boolean_operations(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "hardware_operations" and isinstance(child, bool):
                    raise CommunityBundleError(
                        "public current summary exposes boolean "
                        f"hardware_operations: {path}"
                    )
                reject_boolean_operations(child, path)
        elif isinstance(value, list):
            for child in value:
                reject_boolean_operations(child, path)

    for path in sorted(PUBLIC_EVIDENCE_RECEIPT_MEMBERS):
        if not path.endswith("summary.json"):
            continue
        data = payload_by_path.get(path)
        if not isinstance(data, bytes):
            continue
        try:
            value = json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise CommunityBundleError(
                f"public current summary is invalid: {path}"
            ) from error
        reject_boolean_operations(value, path)


def _verify_public_evidence_receipts(
    payload_by_path: dict[str, bytes],
) -> None:
    missing = sorted(PUBLIC_EVIDENCE_RECEIPT_MEMBERS - set(payload_by_path))
    if missing:
        raise CommunityBundleError(
            f"public evidence receipt is absent: {missing[0]}"
        )
    _verify_em9305_public_readiness_receipts(payload_by_path)
    unavailable = sorted(
        path for path in payload_by_path
        if path.startswith("g2/tools/manifests/g2-touch-")
        and path.endswith("-unavailable.tsv")
    )
    if unavailable:
        raise CommunityBundleError(
            f"excluded Touch unavailable receipt selected: {unavailable[0]}"
        )
    actual_touch_admissions = {
        path for path in payload_by_path
        if path.startswith("g2/tools/manifests/g2-touch-")
        and path.endswith(".tsv")
        and (
            "-admission" in PurePosixPath(path).name
            or PurePosixPath(path).name
            == "g2-touch-software-readiness-functions.tsv"
        )
    }
    if actual_touch_admissions != set(TOUCH_ADMISSION_RECEIPT_MEMBERS):
        raise CommunityBundleError(
            "bundled Touch admission receipt census changed"
        )
    try:
        summary = json.loads(
            payload_by_path[TOUCH_FINAL_CLASSIFICATION_RECEIPT]
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise CommunityBundleError(
            "bundled Touch final-classification receipt is invalid"
        ) from error
    members, digests = _touch_admission_members_from_summary(summary)
    public_inputs = _touch_public_analysis_inputs_from_summary(summary)
    for member in members:
        data = payload_by_path.get(member)
        if not isinstance(data, bytes) or _sha256(data) != digests[member]:
            raise CommunityBundleError(
                f"bundled Touch admission receipt identity changed: {member}"
            )
    donor_archive_path = f"g2/{TOUCH_OFFICIAL_DONOR_INPUT}"
    if donor_archive_path in payload_by_path:
        raise CommunityBundleError(
            "official Touch donor input selected for public evidence"
        )
    for member, expected_digest in public_inputs.items():
        data = payload_by_path.get(member)
        if (
            not isinstance(data, bytes)
            or _sha256(data) != expected_digest
        ):
            raise CommunityBundleError(
                f"bundled Touch public direct-input identity changed: {member}"
            )


def collect_files() -> list[Path]:
    files = {ROOT / relative for relative in EXPLICIT_FILES}
    files.update(
        REPOSITORY_ROOT / relative
        for relative in _repository_public_evidence_members()
    )
    files.update(REPOSITORY_ROOT / relative for relative in EXPLICIT_REPOSITORY_FILES)
    files.update(audit_g2_release_licensing.LICENSE_TEXTS.values())
    files.update(
        REPOSITORY_ROOT / relative for relative in LICENSE_EVIDENCE_MEMBERS
    )
    files.update(
        REPOSITORY_ROOT / evidence_path
        for evidence_path, _digest in LICENSE_EVIDENCE.values()
    )
    files.update(
        REPOSITORY_ROOT / evidence_path
        for _prefix, _license_id, evidence_path, _digest
        in LICENSE_INHERITANCE_SCOPES
    )
    for relative in BUILD_OVERLAY_RECIPES:
        config = _read_json_path(ROOT / relative)
        for source in config.get("sources", []):
            if isinstance(source, dict) and isinstance(source.get("path"), str):
                files.add(ROOT / source["path"])
    for relative in COMMUNITY_SOURCE_TREES:
        for path in (ROOT / relative).rglob("*"):
            if path.is_file() and _allowed_source_file(path):
                files.add(path)
    for pattern, expected_count in COMMUNITY_PUBLIC_SOURCE_GLOBS:
        matches = [path for path in ROOT.glob(pattern) if _allowed_source_file(path)]
        if len(matches) != expected_count:
            raise CommunityBundleError(
                f"community public-source pattern census changed: {pattern} "
                f"({len(matches)} != {expected_count})"
            )
        files.update(matches)
    for pattern in COMMUNITY_CANDIDATE_TEST_GLOBS:
        matches = list(ROOT.glob(pattern))
        if not matches:
            raise CommunityBundleError(
                f"community candidate-test pattern became empty: {pattern}"
            )
        files.update(path for path in matches if _allowed_source_file(path))
    for row in audit_g2_release_licensing.analyze()["source_inventory"]:
        path = ROOT / row["path"]
        # The license inventory intentionally covers private research too. A
        # license-clean research candidate is not automatically public-release
        # material, so only add rows that satisfy the distribution policy.
        if _allowed_source_file(path):
            files.add(path)
    files = _local_include_closure(files)
    missing = sorted(path for path in files if not path.is_file())
    if missing:
        raise CommunityBundleError(f"bundle source missing: {missing[0]}")
    rejected = sorted(path for path in files if not _allowed_source_file(path))
    if rejected:
        raise CommunityBundleError(f"bundle source is forbidden: {rejected[0]}")
    return sorted(files, key=lambda path: path.relative_to(REPOSITORY_ROOT).as_posix())


def _official_provider_hashes(manifest: dict[str, Any] | None = None) -> set[str]:
    if manifest is None:
        manifest = open_cfw.load_manifest(BASE_MANIFEST)
    components = manifest.get("components")
    if not isinstance(components, list) or len(components) != 6:
        raise CommunityBundleError(
            "official payload identity census changed from the reviewed six"
        )
    observed_contract = []
    for component in components:
        if not isinstance(component, dict) or not isinstance(
            component.get("provider"), dict
        ):
            raise CommunityBundleError("official provider contract is invalid")
        provider = component["provider"]
        observed_contract.append((
            component.get("name"),
            provider.get("kind"),
            provider.get("path"),
            provider.get("size"),
            provider.get("sha256"),
        ))
    if tuple(observed_contract) != OFFICIAL_COMPONENT_CONTRACT:
        raise CommunityBundleError(
            "official provider name/path/identity contract changed"
        )
    hashes = {row[4] for row in observed_contract}
    if hashes != OFFICIAL_PAYLOAD_SHA256:
        raise CommunityBundleError(
            "official payload identities differ from the immutable public-export denylist"
        )
    return set(OFFICIAL_PAYLOAD_SHA256)


def _preflight_public_export_member(
    archive_path: str,
    data: bytes,
    *,
    digest: str | None = None,
) -> str:
    """Reject release-local paths and official firmware by exact identity.

    The digest denial is independent of the member name and suffix.  This is
    intentionally separate from source-format validation so a renamed payload
    cannot bypass the public export boundary.
    """
    pure = PurePosixPath(archive_path)
    forbidden_part = next(
        (part for part in pure.parts if _forbidden_directory_part(part)), None
    )
    if forbidden_part is not None:
        raise CommunityBundleError(
            f"temporary/build path forbidden in public export: {archive_path}"
        )
    if pure.name == HYDRATION_RECEIPT:
        raise CommunityBundleError(
            f"local hydration receipt forbidden in public export: {archive_path}"
        )
    if pure.suffix.lower() in FORBIDDEN_SUFFIXES:
        raise CommunityBundleError(
            f"executable/binary suffix forbidden in public export: {archive_path}"
        )
    observed = _sha256(data) if digest is None else digest
    if observed in FORBIDDEN_OFFICIAL_FIRMWARE_SHA256:
        raise CommunityBundleError(
            f"official firmware payload embedded under public path: {archive_path}"
        )
    return observed


def _sanitize_apollo_overlay(data: bytes) -> bytes:
    """Replace exact stock-byte guards with authenticated hash contracts."""
    try:
        config = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise CommunityBundleError("Apollo overlay recipe is not valid JSON") from error
    if not isinstance(config, dict) or not isinstance(config.get("patch_sites"), list):
        raise CommunityBundleError("Apollo overlay recipe shape changed")
    relocated_sources = 0

    def relocate(value: Any) -> None:
        nonlocal relocated_sources
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "path" and isinstance(child, str):
                    repository_path = f"g2/{child}"
                    if repository_path in RELOCATED_PUBLIC_SOURCES:
                        value[key] = RELOCATED_PUBLIC_SOURCES[repository_path][3:]
                        relocated_sources += 1
                else:
                    relocate(child)
        elif isinstance(value, list):
            for child in value:
                relocate(child)

    relocate(config)
    if relocated_sources != 3:
        raise CommunityBundleError(
            "Apollo production-source relocation census unexpectedly changed"
        )
    patch_guards = 0
    for site in config["patch_sites"]:
        if not isinstance(site, dict) or "expected_hex" not in site:
            continue
        expected_hex = site.pop("expected_hex")
        if (
            not isinstance(expected_hex, str)
            or not expected_hex
            or len(expected_hex) % 2
            or re.fullmatch(r"[0-9a-fA-F]+", expected_hex) is None
            or "expected_size" in site
            or "expected_sha256" in site
        ):
            raise CommunityBundleError("Apollo patch-site stock-byte guard is invalid")
        expected = bytes.fromhex(expected_hex)
        site["expected_size"] = len(expected)
        site["expected_sha256"] = _sha256(expected)
        patch_guards += 1
    literal_guards = 0
    leaves = config.get("in_place_leaves")
    if not isinstance(leaves, list):
        raise CommunityBundleError("Apollo in-place leaf recipe shape changed")
    for leaf in leaves:
        if not isinstance(leaf, dict):
            continue
        relocations = leaf.get("relocations", [])
        if not isinstance(relocations, list):
            raise CommunityBundleError("Apollo in-place relocation recipe shape changed")
        for relocation in relocations:
            if not isinstance(relocation, dict) or "target_expected_hex" not in relocation:
                continue
            expected_hex = relocation.pop("target_expected_hex")
            if (
                not isinstance(expected_hex, str)
                or re.fullmatch(r"[0-9a-fA-F]{8}", expected_hex) is None
                or "target_expected_size" in relocation
                or "target_expected_sha256" in relocation
            ):
                raise CommunityBundleError("Apollo literal stock-byte guard is invalid")
            expected = bytes.fromhex(expected_hex)
            relocation["target_expected_size"] = len(expected)
            relocation["target_expected_sha256"] = _sha256(expected)
            literal_guards += 1
    if patch_guards < 1 or literal_guards < 1:
        raise CommunityBundleError("Apollo stock-byte guard census unexpectedly changed")
    _verify_sanitized_apollo_overlay(config)
    return (json.dumps(config, indent=2, sort_keys=True) + "\n").encode()


def _sanitize_liblc3_overlay(data: bytes) -> bytes:
    """Remove the final bounded provider's exact stock call-site body."""
    try:
        config = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise CommunityBundleError("liblc3 overlay recipe is not valid JSON") from error
    patch = config.get("patch_site") if isinstance(config, dict) else None
    if not isinstance(patch, dict) or set(patch) & {"expected_size", "expected_sha256"}:
        raise CommunityBundleError("liblc3 patch-site stock-byte guard is invalid")
    expected_hex = patch.pop("expected_hex", None)
    if (
        not isinstance(expected_hex, str)
        or re.fullmatch(r"[0-9a-fA-F]{8}", expected_hex) is None
    ):
        raise CommunityBundleError("liblc3 patch-site stock-byte guard is invalid")
    expected = bytes.fromhex(expected_hex)
    patch["expected_size"] = len(expected)
    patch["expected_sha256"] = _sha256(expected)
    return (json.dumps(config, indent=2, sort_keys=True) + "\n").encode()


def _sanitize_ring_overlay(data: bytes) -> bytes:
    """Replace the GPL ring overlay's stock call-site bodies with hashes."""
    try:
        config = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise CommunityBundleError("ring overlay recipe is not valid JSON") from error
    sites = config.get("patch_sites") if isinstance(config, dict) else None
    if not isinstance(sites, list) or not sites:
        raise CommunityBundleError("ring overlay patch-site census is invalid")
    for site in sites:
        if (
            not isinstance(site, dict)
            or set(site) & {"expected_size", "expected_sha256"}
        ):
            raise CommunityBundleError("ring patch-site stock-byte guard is invalid")
        expected_hex = site.pop("expected_hex", None)
        if (
            not isinstance(expected_hex, str)
            or not expected_hex
            or len(expected_hex) % 2
            or re.fullmatch(r"[0-9a-fA-F]+", expected_hex) is None
        ):
            raise CommunityBundleError("ring patch-site stock-byte guard is invalid")
        expected = bytes.fromhex(expected_hex)
        site["expected_size"] = len(expected)
        site["expected_sha256"] = _sha256(expected)
    return (json.dumps(config, indent=2, sort_keys=True) + "\n").encode()


def _bundle_payload(path: Path, data: bytes) -> bytes:
    archive_path = path.relative_to(REPOSITORY_ROOT).as_posix()
    if archive_path == SANITIZED_APOLLO_OVERLAY:
        return _sanitize_apollo_overlay(data)
    if archive_path == SANITIZED_LIBLC3_OVERLAY:
        return _sanitize_liblc3_overlay(data)
    if archive_path == SANITIZED_RING_OVERLAY:
        return _sanitize_ring_overlay(data)
    return data


def _strip_c_comments(data: bytes) -> bytes:
    """Remove C/C++ comments without interpreting comment markers in literals."""
    output = bytearray()
    index = 0
    quote: int | None = None
    while index < len(data):
        byte = data[index]
        if quote is not None:
            output.append(byte)
            if byte == ord("\\") and index + 1 < len(data):
                index += 1
                output.append(data[index])
            elif byte == quote:
                quote = None
            index += 1
            continue
        if byte in (ord('"'), ord("'")):
            quote = byte
            output.append(byte)
            index += 1
            continue
        if byte == ord("/") and index + 1 < len(data):
            following = data[index + 1]
            if following == ord("/"):
                output.extend(b"  ")
                index += 2
                while index < len(data) and data[index] not in (10, 13):
                    output.append(ord(" "))
                    index += 1
                continue
            if following == ord("*"):
                output.extend(b"  ")
                index += 2
                while index < len(data):
                    if (
                        data[index] == ord("*")
                        and index + 1 < len(data)
                        and data[index + 1] == ord("/")
                    ):
                        output.extend(b"  ")
                        index += 2
                        break
                    output.append(data[index] if data[index] in (10, 13) else ord(" "))
                    index += 1
                continue
        output.append(byte)
        index += 1
    return bytes(output)


def _c_numeric_array_receipts(data: bytes) -> frozenset[tuple[int, str]]:
    receipts: set[tuple[int, str]] = set()
    source = _strip_c_comments(data)
    for match in C_BRACE_BODY.finditer(source):
        body = match.group(1)
        tokens = C_INTEGER_TOKEN.findall(body)
        if len(tokens) < 16:
            continue
        residual = C_INTEGER_TOKEN.sub(b"", body)
        if re.sub(rb"[\s,]", b"", residual):
            continue
        values: list[int] = []
        for token in tokens:
            literal = re.sub(rb"[uUlL]+$", b"", token).decode("ascii")
            if literal.lower().startswith("0x"):
                value = int(literal, 16)
            elif literal.lower().startswith("0b"):
                value = int(literal, 2)
            elif len(literal) > 1 and literal.startswith("0"):
                value = int(literal, 8)
            else:
                value = int(literal, 10)
            values.append(value)
        if all(0 <= value <= 255 for value in values):
            receipts.add((len(values), _sha256(bytes(values))))
    return frozenset(receipts)


def _c_has_unreviewed_byte_initializer(data: bytes) -> bool:
    """Detect byte-bearing initializers that evade the canonical table parser."""
    source = _strip_c_comments(data)
    char_literal = re.compile(rb"'((?:\\.|[^'\\])*)'")
    any_literal = re.compile(
        rb'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''
    )

    def char_byte(body: bytes) -> int | None:
        if len(body) == 1:
            return body[0]
        if re.fullmatch(rb"\\x[0-9A-Fa-f]{2}", body):
            return int(body[2:], 16)
        if re.fullmatch(rb"\\[0-7]{1,3}", body):
            value = int(body[1:], 8)
            return value if value <= 255 else None
        escapes = {
            b"\\0": 0, b"\\a": 7, b"\\b": 8, b"\\t": 9,
            b"\\n": 10, b"\\v": 11, b"\\f": 12, b"\\r": 13,
            b"\\\\": 92, b"\\'": 39, b'\\"': 34,
        }
        return escapes.get(body)

    for match in C_BRACE_BODY.finditer(source):
        prefix = source[max(0, match.start() - 512):match.start()]
        if re.search(rb"=\s*$", prefix) is None:
            continue
        body = match.group(1)
        tokens = C_INTEGER_TOKEN.findall(body)
        residual = C_INTEGER_TOKEN.sub(b"", body)
        if len(tokens) >= 16 and not re.sub(rb"[\s,]", b"", residual):
            # Canonical pure numeric tables are handled by the exact receipt map.
            continue
        declaration = re.split(rb"[;{}\r\n]", prefix)[-1]
        if re.search(
            rb"(?i)(?:\bchar\b|\b(?:u?int8_t|std::byte|byte)\b)",
            declaration,
        ) is None:
            continue
        literal_values = [
            value
            for value in (char_byte(item) for item in char_literal.findall(body))
            if value is not None
        ]
        without_literals = any_literal.sub(b" ", body)
        integer_values = []
        for token in C_INTEGER_TOKEN.findall(without_literals):
            literal = re.sub(rb"[uUlL]+$", b"", token).decode("ascii")
            try:
                value = int(literal, 0)
            except ValueError:
                continue
            if 0 <= value <= 255:
                integer_values.append(value)
        if len(literal_values) + len(integer_values) >= 16:
            return True
    return False


def _static_python_literal(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant) and isinstance(
        node.value, (str, bytes, list, tuple)
    ):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple)):
        values = [_static_python_literal(element) for element in node.elts]
        if any(value is None for value in values):
            return None
        return values if isinstance(node, ast.List) else tuple(values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _static_python_literal(node.left)
        right = _static_python_literal(node.right)
        if isinstance(left, type(right)) and isinstance(left, (str, bytes, list, tuple)):
            return left + right
    return None


def _python_decoder_name(node: ast.Call) -> str:
    return (
        node.func.attr
        if isinstance(node.func, ast.Attribute)
        else node.func.id
        if isinstance(node.func, ast.Name)
        else ""
    )


def _decode_literal_bytes(name: str, value: Any) -> bytes | None:
    if not isinstance(value, (str, bytes)):
        return None
    try:
        if name in {"fromhex", "unhexlify"}:
            text = value.decode("ascii") if isinstance(value, bytes) else value
            return bytes.fromhex(text)
        encoded = value.encode("ascii") if isinstance(value, str) else value
        if name in {"b64decode", "standard_b64decode", "decodebytes"}:
            return base64.b64decode(encoded)
        if name == "urlsafe_b64decode":
            return base64.urlsafe_b64decode(encoded)
        if name == "a85decode":
            return base64.a85decode(encoded)
        if name == "b85decode":
            return base64.b85decode(encoded)
    except (UnicodeError, ValueError):
        return None
    return None


def _raw_encoded_string_paths(value: Any, prefix: str = "$") -> list[str]:
    """Find explicitly encoded JSON string chunks after structural parsing."""
    paths: list[str] = []
    if isinstance(value, dict):
        encoding = value.get("encoding")
        decoder = ""
        if isinstance(encoding, str):
            normalized = encoding.lower().replace("-", "").replace("_", "")
            decoder = {
                "hex": "fromhex", "base16": "fromhex",
                "base64": "b64decode", "b64": "b64decode",
                "base85": "b85decode", "b85": "b85decode",
                "ascii85": "a85decode", "a85": "a85decode",
            }.get(normalized, "")
        for key, child in value.items():
            child_path = f"{prefix}.{key}"
            child_decoder = decoder
            normalized_key = str(key).lower().replace("-", "_")
            if not child_decoder and normalized_key in {
                "binary", "blob", "body", "bytes", "chunks", "content",
                "data", "firmware", "image", "payload",
            }:
                child_decoder = "fromhex"
            if child_decoder and isinstance(child, list) and child and all(
                isinstance(item, (str, bytes)) for item in child
            ):
                joined = b"".join(
                    item.encode("ascii") if isinstance(item, str) else item
                    for item in child
                )
                decoded = _decode_literal_bytes(child_decoder, joined)
                if decoded is None and not decoder:
                    decoded = _decode_literal_bytes("b64decode", joined)
                if decoded is not None and len(decoded) >= 16:
                    paths.append(child_path)
            paths.extend(_raw_encoded_string_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_raw_encoded_string_paths(child, f"{prefix}[{index}]"))
    return paths


def _reject_raw_executable_transcript(archive_path: str, data: bytes) -> None:
    pure = PurePosixPath(archive_path)
    component_python = (
        len(pure.parts) >= 3
        and pure.parts[:2] == ("g2", "components")
        and pure.suffix == ".py"
    )
    if pure.suffix in C_NUMERIC_ARRAY_SUFFIXES:
        if RAW_EXECUTABLE_DIRECTIVE.search(data):
            raise CommunityBundleError(
                f"raw executable transcript directive selected: {archive_path}"
            )
        observed = _c_numeric_array_receipts(data)
        expected = REVIEWED_PUBLIC_NUMERIC_ARRAYS.get(archive_path, frozenset())
        if observed != expected:
            raise CommunityBundleError(
                f"unreviewed numeric byte array selected: {archive_path}"
            )
        if _c_has_unreviewed_byte_initializer(data):
            raise CommunityBundleError(
                f"unreviewed numeric byte array selected: {archive_path}"
            )
        comment_free = _strip_c_comments(data)
        for run in ADJACENT_C_STRING_RUN.findall(comment_free):
            joined = b"".join(C_STRING_LITERAL_BODY.findall(run))
            if (
                LONG_HEX_BODY.search(joined)
                or BASE64_BODY.search(joined)
                or ESCAPED_BYTE_TRANSCRIPT.search(joined)
                or OCTAL_ESCAPED_BYTE_TRANSCRIPT.search(joined)
            ):
                raise CommunityBundleError(
                    f"split encoded vendor-byte transcript forbidden: {archive_path}"
                )
    if pure.suffix in {".S", ".s", ".asm"}:
        emitted = 0
        widths = {b"word": 4, b"long": 4, b"4byte": 4, b"quad": 8, b"8byte": 8}
        for match in RAW_WIDE_EXECUTABLE_DIRECTIVE.finditer(data):
            emitted += widths[match.group(1).lower()] * len(
                C_INTEGER_TOKEN.findall(match.group(2))
            )
        if emitted >= 16:
            raise CommunityBundleError(
                f"raw executable transcript directive selected: {archive_path}"
            )
    if pure.suffix == ".py":
        try:
            tree = ast.parse(data.decode("utf-8"), filename=archive_path)
        except (SyntaxError, UnicodeDecodeError) as error:
            raise CommunityBundleError(
                f"public Python source is invalid: {archive_path}"
            ) from error
        literal_decoders = {
            "fromhex",
            "unhexlify",
            "b64decode",
            "standard_b64decode",
            "urlsafe_b64decode",
            "decodebytes",
            "a85decode",
            "b85decode",
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
                literal = (
                    node.value.encode("utf-8")
                    if isinstance(node.value, str)
                    else node.value
                )
                if (
                    len(literal) >= 16
                    and isinstance(node.value, bytes)
                    and sum(32 <= byte < 127 for byte in literal)
                    < (len(literal) * 3) // 4
                ) or LONG_HEX_BODY.search(literal) or BASE64_BODY.search(literal):
                    raise CommunityBundleError(
                        f"literal executable encoding constructor selected: {archive_path}"
                    )
            if (
                isinstance(node, (ast.List, ast.Tuple))
                and len(node.elts) >= 16
                and all(
                    isinstance(element, ast.Constant)
                    and isinstance(element.value, int)
                    and not isinstance(element.value, bool)
                    and 0 <= element.value <= 255
                    for element in node.elts
                )
            ):
                raise CommunityBundleError(
                    f"literal executable encoding constructor selected: {archive_path}"
                )
            if not isinstance(node, ast.Call) or not node.args:
                continue
            name = _python_decoder_name(node)
            argument = node.args[0]
            if (
                component_python
                and archive_path not in REVIEWED_GENERATED_HEX_CONSTRUCTORS
                and name in literal_decoders
                and _decode_literal_bytes(
                    name, _static_python_literal(argument)
                ) is not None
            ):
                raise CommunityBundleError(
                    f"literal executable encoding constructor selected: {archive_path}"
                )
        if component_python and archive_path not in REVIEWED_GENERATED_HEX_CONSTRUCTORS:
            for expression in ast.walk(tree):
                if not isinstance(expression, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
                    continue
                if not isinstance(expression.elt, ast.Call) or not expression.elt.args:
                    continue
                name = _python_decoder_name(expression.elt)
                if name not in literal_decoders or len(expression.generators) != 1:
                    continue
                generator = expression.generators[0]
                argument = expression.elt.args[0]
                values = _static_python_literal(generator.iter)
                if (
                    isinstance(generator.target, ast.Name)
                    and isinstance(argument, ast.Name)
                    and argument.id == generator.target.id
                    and isinstance(values, (list, tuple))
                    and values
                    and all(_decode_literal_bytes(name, value) is not None for value in values)
                ):
                    raise CommunityBundleError(
                        f"literal executable encoding constructor selected: {archive_path}"
                    )
        if (
            component_python
            and archive_path not in REVIEWED_GENERATED_HEX_CONSTRUCTORS
            and LITERAL_HEX_CONSTRUCTOR.search(data)
        ):
            raise CommunityBundleError(
                f"literal executable encoding constructor selected: {archive_path}"
            )


def _allowed_archive_file(path: PurePosixPath) -> bool:
    return (
        SAFE_ARCHIVE_PATH.fullmatch(path.as_posix()) is not None
        and not any(_forbidden_directory_part(part) for part in path.parts)
        and path.name not in FORBIDDEN_FILENAMES
        and path.name.lower() not in FORBIDDEN_SECRET_FILENAMES
        and path.suffix.lower() not in FORBIDDEN_SUFFIXES | FORBIDDEN_SECRET_SUFFIXES
        and (
            path.suffix in SOURCE_SUFFIXES
            or path.name in {"Makefile", "make.sh", "LICENSE", "NOTICE"}
            or path.name.startswith("LICENSE")
            or path.as_posix() == ".gitignore"
        )
    )


def _raw_stock_guard_paths(value: Any, prefix: str = "$") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{prefix}.{key}"
            if key in {"expected_hex", "target_expected_hex"}:
                paths.append(child_path)
            paths.extend(_raw_stock_guard_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_raw_stock_guard_paths(child, f"{prefix}[{index}]"))
    return paths


def _raw_encoded_byte_paths(value: Any, prefix: str = "$") -> list[str]:
    def flattened_bytes(candidate: Any) -> list[int] | None:
        if (
            isinstance(candidate, int)
            and not isinstance(candidate, bool)
            and 0 <= candidate <= 255
        ):
            return [candidate]
        if not isinstance(candidate, list) or not candidate:
            return None
        flattened: list[int] = []
        for item in candidate:
            child = flattened_bytes(item)
            if child is None:
                return None
            flattened.extend(child)
        return flattened

    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            paths.extend(_raw_encoded_byte_paths(child, f"{prefix}.{key}"))
    elif isinstance(value, list):
        flattened = flattened_bytes(value)
        if flattened is not None and len(flattened) >= 16:
            paths.append(prefix)
        else:
            for index, child in enumerate(value):
                paths.extend(_raw_encoded_byte_paths(child, f"{prefix}[{index}]"))
    return paths


def _verify_public_payload(archive_path: str, data: bytes) -> None:
    if archive_path in FORBIDDEN_INVENSENSE_EDMP_MEMBERS:
        raise CommunityBundleError(
            f"forbidden InvenSense EDMP member selected: {archive_path}"
        )
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CommunityBundleError(
            f"non-text public source material selected: {archive_path}"
        ) from error
    if b"\0" in data:
        raise CommunityBundleError(
            f"NUL-bearing public source material selected: {archive_path}"
        )
    if PRIVATE_KEY_BLOCK.search(data):
        raise CommunityBundleError(f"private-key material selected: {archive_path}")
    if RESTRICTED_SOURCE_NOTICE.search(data):
        raise CommunityBundleError(
            f"restricted vendor source notice selected: {archive_path}"
        )
    if LONG_HEX_BODY.search(data):
        raise CommunityBundleError(
            f"long embedded hexadecimal body forbidden: {archive_path}"
        )
    if BASE64_BODY.search(data):
        raise CommunityBundleError(
            f"long embedded base64 body forbidden: {archive_path}"
        )
    if (
        DENSE_BYTE_TRANSCRIPT.search(data)
        or ESCAPED_BYTE_TRANSCRIPT.search(data)
        or OCTAL_ESCAPED_BYTE_TRANSCRIPT.search(data)
    ):
        raise CommunityBundleError(
            f"encoded vendor-byte transcript forbidden: {archive_path}"
        )
    _reject_raw_executable_transcript(archive_path, data)
    if PurePosixPath(archive_path).suffix == ".json":
        try:
            value = json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise CommunityBundleError(
                f"public JSON source is invalid: {archive_path}"
            ) from error
        paths = _raw_stock_guard_paths(value)
        if paths:
            raise CommunityBundleError(
                f"raw stock-byte guard remains in {archive_path}: {paths[0]}"
            )
        encoded_paths = _raw_encoded_byte_paths(value)
        if encoded_paths:
            raise CommunityBundleError(
                f"raw encoded byte array remains in {archive_path}: "
                f"{encoded_paths[0]}"
            )
        encoded_string_paths = _raw_encoded_string_paths(value)
        if encoded_string_paths:
            raise CommunityBundleError(
                f"raw encoded string chunks remain in {archive_path}: "
                f"{encoded_string_paths[0]}"
            )


def _verify_public_inventory(paths: set[str]) -> None:
    touch_summary = _read_json_path(
        REPOSITORY_ROOT / TOUCH_FINAL_CLASSIFICATION_RECEIPT
    )
    touch_public_inputs = set(
        _touch_public_analysis_inputs_from_summary(touch_summary)
    )
    forbidden_invensense = sorted(paths & FORBIDDEN_INVENSENSE_EDMP_MEMBERS)
    if forbidden_invensense:
        raise CommunityBundleError(
            f"forbidden InvenSense EDMP member selected: {forbidden_invensense[0]}"
        )
    forbidden_nemavg = sorted(paths & NEMAVG_FORBIDDEN_PUBLIC_MEMBERS)
    if forbidden_nemavg:
        raise CommunityBundleError(
            "unsafe NemaVG endpoint/integrator member selected: "
            f"{forbidden_nemavg[0]}"
        )
    pt_sources = {
        f"g2/components/apollo_main/core_overlay/pt_protocol{suffix}.{extension}"
        for suffix in PT_PROTOCOL_SOURCE_SUFFIXES
        for extension in ("c", "h")
    } | {
        "g2/components/apollo_main/core_overlay/pt_protocol_lc3_setup.c"
    }
    pt_tests = {
        f"g2/tests/test_runtime_pt_protocol_{area}.py"
        for area in PT_PROTOCOL_AREAS
    }
    pt_fixtures = {
        f"g2/tests/fixtures/pt_protocol_{area}_host.c"
        for area in PT_PROTOCOL_FIXTURES
    }
    case_files = {
        relative
        for area in CASE_PUBLIC_AREAS
        for relative in (
            f"g2/components/shared/case/runtime_case_{area}.c",
            f"g2/components/shared/case/runtime_case_{area}.h",
            f"g2/tests/test_runtime_case_{area}.py",
            f"g2/tests/fixtures/runtime_case_{area}_host.c",
            f"g2/tools/manifests/g2-case-{area.replace('_', '-')}-admission-summary.json",
            f"g2/tools/manifests/g2-case-{area.replace('_', '-')}-admission.tsv",
        )
    }
    case_source_image_files = {
        "g2/components/case/source_image/README.md",
        "g2/components/case/source_image/build_image.py",
        "g2/components/case/source_image/compiler_runtime.c",
        "g2/components/case/source_image/linker.ld",
        "g2/components/case/source_image/startup.c",
        "g2/tools/analyze_g2_case_source_image.py",
        "g2/tests/test_analyze_g2_case_source_image.py",
        "g2/tools/manifests/g2-case-source-image-summary.json",
    }
    em9305_source_image_files = {
        "g2/components/em9305/source_image/README.md",
        "g2/components/em9305/source_image/build_image.py",
        "g2/components/em9305/source_image/record_package.py",
        "g2/tools/analyze_em9305_record_package.py",
        "g2/tests/test_analyze_em9305_record_package.py",
        "g2/tests/test_em9305_record_package.py",
        "g2/tools/manifests/em9305-record-package-summary.json",
    }
    required = (
        pt_sources
        | pt_tests
        | pt_fixtures
        | case_files
        | case_source_image_files
        | em9305_source_image_files
        | touch_public_inputs
        | {
            *PUBLIC_EVIDENCE_RECEIPT_MEMBERS,
            *RELOCATED_PUBLIC_SOURCES.values(),
            "g2/tools/manifests/g2-pt-protocol-source-summary.json",
            "g2/components/apollo_main/pt_protocol/build_component.py",
            "g2/tools/manifests/g2-case-final-classification-summary.json",
            *NEMAVG_PUBLIC_MEMBERS,
            "g2/tools/manifests/g2-clkmgr-divider-candidate-summary.json",
            "g2/tests/test_runtime_clkmgr_divider_candidate.py",
            "g2/tests/fixtures/runtime_clkmgr_divider_candidate_host.c",
            "g2/tools/verify_g2_clkmgr_divider_public.py",
            "g2/tools/apply_g2_canonical_observations.py",
            "g2/tests/test_apply_g2_canonical_observations.py",
            "g2/tests/test_core_canonical_recorder_security.py",
            "g2/tests/test_community_markdown_link_closure.py",
            *DUAL_PROFILE_PROOF_MEMBERS,
            "g2/docs/community-source-distribution.md",
            "Makefile",
            "README.md",
            "make.sh",
        }
    )
    missing = sorted(required - paths)
    if missing:
        raise CommunityBundleError(f"required community source is absent: {missing[0]}")
    actual_nemavg = {
        path for path in paths if "nemavg" in path.casefold()
    }
    if actual_nemavg != set(NEMAVG_PUBLIC_MEMBERS):
        raise CommunityBundleError("NemaVG community member census changed")
    unavailable_touch_receipts = sorted(
        path for path in paths
        if path.startswith("g2/tools/manifests/g2-touch-")
        and path.endswith("-unavailable.tsv")
    )
    if unavailable_touch_receipts:
        raise CommunityBundleError(
            "excluded Touch unavailable receipt selected: "
            f"{unavailable_touch_receipts[0]}"
        )
    actual_touch_admissions = {
        path for path in paths
        if path.startswith("g2/tools/manifests/g2-touch-")
        and path.endswith(".tsv")
        and (
            "-admission" in PurePosixPath(path).name
            or PurePosixPath(path).name
            == "g2-touch-software-readiness-functions.tsv"
        )
    }
    if actual_touch_admissions != set(TOUCH_ADMISSION_RECEIPT_MEMBERS):
        raise CommunityBundleError("Touch admission receipt census changed")
    actual_pt_sources = {
        path
        for path in paths
        if path.startswith("g2/components/apollo_main/core_overlay/pt_protocol")
        and PurePosixPath(path).suffix in {".c", ".h"}
    }
    if actual_pt_sources != pt_sources:
        raise CommunityBundleError("PT protocol public-source census changed")
    actual_pt_tests = {
        path
        for path in paths
        if path.startswith("g2/tests/test_runtime_pt_protocol_")
        and path.endswith(".py")
    }
    if actual_pt_tests != pt_tests:
        raise CommunityBundleError("PT protocol runtime-test census changed")
    actual_pt_fixtures = {
        path
        for path in paths
        if path.startswith("g2/tests/fixtures/pt_protocol_")
        and path.endswith("_host.c")
    }
    if actual_pt_fixtures != pt_fixtures:
        raise CommunityBundleError("PT protocol fixture census changed")
    public_analysis = {
        *TOUCH_PUBLIC_ANALYZER_MEMBERS,
        "g2/tools/analyze_g2_case_source_image.py",
        "g2/tests/test_analyze_g2_case_source_image.py",
        "g2/tools/analyze_em9305_record_package.py",
        "g2/tests/test_analyze_em9305_record_package.py",
        "g2/tools/analyze_g2_touch_source_image.py",
        "g2/tests/test_analyze_g2_touch_source_image.py",
        "g2/tools/analyze_g2_dual_profile_ownership.py",
        "g2/tests/test_analyze_g2_dual_profile_ownership.py",
    }
    for path in paths:
        pure = PurePosixPath(path)
        if not _allowed_archive_file(pure):
            raise CommunityBundleError(f"forbidden public-source path selected: {path}")
        if (
            (
                path.startswith("g2/tools/analyze_")
                or path.startswith("g2/tests/test_analyze_")
            )
            and path not in public_analysis
        ) or path.startswith("g2/tools/extract_") or path.startswith(
            "g2/tests/test_extract_"
        ):
            raise CommunityBundleError(f"internal analysis artifact selected: {path}")


def _verify_smoke_python_import_closure(
    payload_by_path: dict[str, bytes],
) -> None:
    """Bind local imports used by extracted-tree smoke entry points."""
    for entry, contract in SMOKE_PYTHON_IMPORT_CLOSURE.items():
        entry_data = payload_by_path.get(entry)
        if not isinstance(entry_data, bytes):
            raise CommunityBundleError(
                f"community smoke Python entry is absent: {entry}"
            )
        try:
            tree = ast.parse(entry_data.decode("utf-8"), filename=entry)
        except (UnicodeDecodeError, SyntaxError) as error:
            raise CommunityBundleError(
                f"community smoke Python entry is invalid: {entry}"
            ) from error
        nodes = tuple(ast.walk(tree))
        imports = {
            alias.name
            for node in nodes
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module
            for node in nodes
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        if imports != contract["imports"]:
            raise CommunityBundleError(
                f"community smoke Python import contract changed: {entry}"
            )
        for module, dependency in contract["local"].items():
            dependency_data = payload_by_path.get(dependency)
            if not isinstance(dependency_data, bytes):
                raise CommunityBundleError(
                    f"community smoke Python dependency is absent: {dependency}"
                )
            try:
                ast.parse(dependency_data.decode("utf-8"), filename=dependency)
            except (UnicodeDecodeError, SyntaxError) as error:
                raise CommunityBundleError(
                    f"community smoke Python dependency is invalid: {dependency}"
                ) from error


MARKDOWN_INLINE_LINK = re.compile(
    r"!?\[[^\]\r\n]*\]\(\s*(<[^>\r\n]+>|[^\s)]+)(?:\s+[^)]*)?\)"
)
MARKDOWN_REFERENCE_LINK = re.compile(
    r"^\s*\[[^\]\r\n]+\]:\s*(<[^>\r\n]+>|\S+)", re.MULTILINE
)
MARKDOWN_HTML_LINK = re.compile(
    r"\b(?:href|src)\s*=\s*([\"'])([^\"']+)\1", re.IGNORECASE
)


def _markdown_local_target(source_path: str, raw_target: str) -> str | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = urllib.parse.unquote(target)
    parsed = urllib.parse.urlsplit(target)
    if parsed.scheme or parsed.netloc or target.startswith("//"):
        return None
    if not parsed.path:
        # Fragment-only links are intra-document. Anchor spelling is deliberately
        # normalized away; this gate authenticates the local file closure.
        return None
    if parsed.path.startswith("/") or "\\" in parsed.path:
        raise CommunityBundleError(
            f"unsafe local Markdown link in {source_path}: {raw_target}"
        )
    combined = posixpath.normpath(
        posixpath.join(posixpath.dirname(source_path), parsed.path)
    )
    if combined in {"", ".", ".."} or combined.startswith("../"):
        raise CommunityBundleError(
            f"local Markdown link escapes archive in {source_path}: {raw_target}"
        )
    return combined


def _verify_markdown_link_closure(payload_by_path: dict[str, bytes]) -> None:
    members = set(payload_by_path)
    for source_path in sorted(members):
        if PurePosixPath(source_path).suffix.lower() != ".md":
            continue
        try:
            markdown = payload_by_path[source_path].decode("utf-8")
        except UnicodeDecodeError as error:
            raise CommunityBundleError(
                f"Markdown member is not UTF-8: {source_path}"
            ) from error
        targets = [match.group(1) for match in MARKDOWN_INLINE_LINK.finditer(markdown)]
        targets.extend(
            match.group(1) for match in MARKDOWN_REFERENCE_LINK.finditer(markdown)
        )
        targets.extend(match.group(2) for match in MARKDOWN_HTML_LINK.finditer(markdown))
        for raw_target in targets:
            target = _markdown_local_target(source_path, raw_target)
            if target is None or target in members:
                continue
            index = f"{target.rstrip('/')}/README.md"
            if index in members:
                continue
            raise CommunityBundleError(
                f"dangling local Markdown link in {source_path}: "
                f"{raw_target} -> {target}"
            )


def _verify_sanitized_apollo_overlay(config: Any) -> None:
    if not isinstance(config, dict) or not isinstance(config.get("patch_sites"), list):
        raise CommunityBundleError("sanitized Apollo overlay shape is invalid")
    if not config["patch_sites"]:
        raise CommunityBundleError("sanitized Apollo patch-site census is empty")
    serialized = json.dumps(config, sort_keys=True)
    if "research/candidates/freertos_scheduler_port_trio" in serialized:
        raise CommunityBundleError("Apollo private research source path remains embedded")
    relocated = serialized.count(
        "components/apollo_main/core_overlay/freertos_scheduler_port_trio.c"
    )
    if relocated != 3:
        raise CommunityBundleError("Apollo public source relocation census is invalid")
    for site in config["patch_sites"]:
        if not isinstance(site, dict) or "expected_hex" in site:
            raise CommunityBundleError("Apollo patch-site stock bytes remain embedded")
        size = site.get("expected_size")
        digest = site.get("expected_sha256")
        if (
            not isinstance(size, int)
            or isinstance(size, bool)
            or size < 1
            or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        ):
            raise CommunityBundleError("Apollo patch-site hash contract is invalid")
    leaves = config.get("in_place_leaves")
    if not isinstance(leaves, list):
        raise CommunityBundleError("sanitized Apollo in-place census is invalid")
    literal_guards = 0
    for leaf in leaves:
        if not isinstance(leaf, dict) or not isinstance(leaf.get("relocations", []), list):
            raise CommunityBundleError("sanitized Apollo relocation census is invalid")
        for relocation in leaf.get("relocations", []):
            if not isinstance(relocation, dict) or "target_expected_hex" in relocation:
                raise CommunityBundleError("Apollo literal stock bytes remain embedded")
            if "target_expected_size" not in relocation:
                continue
            if (
                relocation.get("target_expected_size") != 4
                or not isinstance(relocation.get("target_expected_sha256"), str)
                or re.fullmatch(
                    r"[0-9a-f]{64}", relocation["target_expected_sha256"]
                )
                is None
            ):
                raise CommunityBundleError("Apollo literal hash contract is invalid")
            literal_guards += 1
    if literal_guards < 1:
        raise CommunityBundleError("sanitized Apollo literal guard census is empty")

    functions = config.get("functions")
    relocated_leaves = config.get("relocated_leaves")
    if not isinstance(functions, list) or not isinstance(relocated_leaves, list):
        raise CommunityBundleError("sanitized Apollo source census is invalid")
    routed_functions = [
        function for function in functions
        if function in NEMAVG_ROUTE_TARGET_FUNCTIONS
    ]
    if (
        set(routed_functions) != NEMAVG_PRODUCTION_FUNCTIONS
        or len(routed_functions) != len(NEMAVG_PRODUCTION_FUNCTIONS)
    ):
        raise CommunityBundleError(
            "NemaVG production function census changed"
        )

    nema_sites = [
        site for site in config["patch_sites"]
        if (
            site.get("runtime_address")
            in (
                NEMAVG_ENDPOINT_ENTRIES
                | {NEMAVG_COORDINATOR_PATCH["runtime_address"]}
            )
            or site.get("target_function") in NEMAVG_ROUTE_TARGET_FUNCTIONS
        )
    ]
    if nema_sites != list(NEMAVG_PRODUCTION_PATCHES):
        raise CommunityBundleError(
            "NemaVG production patch route changed"
        )

    serialized = json.dumps(config, sort_keys=True)
    forbidden_routed_sources = {
        member.removeprefix("g2/") for member in NEMAVG_CANDIDATE_SOURCE_MEMBERS
    } | {
        member.removeprefix("g2/")
        for member in NEMAVG_FORBIDDEN_PUBLIC_MEMBERS
        if member.endswith((".c", ".h"))
    }
    if any(
        json.dumps(path) in serialized for path in forbidden_routed_sources
    ):
        raise CommunityBundleError(
            "NemaVG nonproduction candidate source is production-routed"
        )

    nema_leaves: list[tuple[str, dict[str, Any]]] = []
    for kind, source_leaves in (
        ("relocated", relocated_leaves),
        ("in-place", leaves),
    ):
        for leaf in source_leaves:
            if not isinstance(leaf, dict):
                raise CommunityBundleError(
                    "sanitized Apollo source leaf census is invalid"
                )
            source = leaf.get("source")
            source_path = source.get("path") if isinstance(source, dict) else None
            if (
                leaf.get("function") in NEMAVG_ROUTE_TARGET_FUNCTIONS
                or isinstance(source_path, str)
                and "nemavg" in source_path.casefold()
            ):
                nema_leaves.append((kind, leaf))
    if (
        len(nema_leaves) != 3
        or any(kind != "relocated" for kind, _leaf in nema_leaves)
        or {leaf.get("function") for _kind, leaf in nema_leaves}
        != NEMAVG_PRODUCTION_FUNCTIONS
    ):
        raise CommunityBundleError(
            "NemaVG production source route census changed"
        )
    if any(
        leaf.get("source") != NEMAVG_PRODUCTION_SOURCE_IDENTITY
        or leaf.get("strict_relocation_contract") is not True
        for _kind, leaf in nema_leaves
    ) or serialized.count(
        json.dumps(NEMAVG_PRODUCTION_SOURCE_IDENTITY["path"])
    ) != 3:
        raise CommunityBundleError(
            "NemaVG reviewed production source identity changed"
        )


def _verify_nemavg_public_boundary(
    payload_by_path: dict[str, bytes], config: Any
) -> None:
    """Bind the complete reviewed route to its exact public source/evidence."""
    _verify_sanitized_apollo_overlay(config)
    forbidden = sorted(set(payload_by_path) & NEMAVG_FORBIDDEN_PUBLIC_MEMBERS)
    if forbidden:
        raise CommunityBundleError(
            "unsafe NemaVG endpoint/integrator member selected: "
            f"{forbidden[0]}"
        )
    missing = sorted(NEMAVG_PUBLIC_MEMBERS - set(payload_by_path))
    if missing:
        raise CommunityBundleError(
            f"required NemaVG public evidence is absent: {missing[0]}"
        )

    production_source = payload_by_path[NEMAVG_PRODUCTION_SOURCE_MEMBER]
    if (
        len(production_source) != NEMAVG_PRODUCTION_SOURCE_IDENTITY["size"]
        or _sha256(production_source)
        != NEMAVG_PRODUCTION_SOURCE_IDENTITY["sha256"]
    ):
        raise CommunityBundleError(
            "NemaVG reviewed production source identity changed"
        )

    try:
        summary = json.loads(payload_by_path[NEMAVG_CANDIDATE_SUMMARY_MEMBER])
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise CommunityBundleError(
            "NemaVG candidate boundary summary is invalid"
        ) from error
    if not isinstance(summary, dict):
        raise CommunityBundleError("NemaVG candidate boundary summary is invalid")
    candidate = summary.get("candidate")
    stock = summary.get("stock")
    records = stock.get("records") if isinstance(stock, dict) else None
    if (
        summary.get("status")
        != "nemavg-stroke-caps-production-source-routed"
        or summary.get("hardware_operations") != []
        or summary.get("hardware_validation") != DEFERRED_HARDWARE_VALIDATION
        or not isinstance(candidate, dict)
        or candidate.get("production_routed") is not True
        or candidate.get("production_routed_functions") != 3
        or candidate.get("production_routed_physical_bytes") != 6_614
        or candidate.get("remaining_candidate_functions") != 0
        or candidate.get("remaining_candidate_physical_bytes") != 0
        or candidate.get("endpoint_stock_entries_unpatched") is not False
        or candidate.get("production_source")
        != {
            "path": NEMAVG_PRODUCTION_SOURCE_IDENTITY["path"],
            "sha256": NEMAVG_PRODUCTION_SOURCE_IDENTITY["sha256"],
            "size": NEMAVG_PRODUCTION_SOURCE_IDENTITY["size"],
        }
        or not isinstance(stock, dict)
        or stock.get("functions") != 3
        or stock.get("physical_bytes") != 6_614
        or not isinstance(records, list)
        or len(records) != 3
        or any(
            not isinstance(record, dict)
            or record.get("production_routed") is not True
            for record in records
        )
        or tuple(
            (
                record.get("symbol"),
                record.get("entry"),
                record.get("physical_bytes"),
                record.get("production_routed"),
                record.get("source_status"),
            )
            for record in records
        )
        != (
            (
                "draw_start_cap",
                "0x0051B8F0",
                1_668,
                True,
                "production-source",
            ),
            (
                "draw_end_cap",
                "0x0051BF7C",
                1_640,
                True,
                "production-source",
            ),
            (
                "draw_caps",
                "0x0051C5EC",
                3_306,
                True,
                "production-source",
            ),
        )
    ):
        raise CommunityBundleError("NemaVG candidate boundary semantics changed")


def _verify_sanitized_liblc3_overlay(config: Any) -> None:
    patch = config.get("patch_site") if isinstance(config, dict) else None
    if not isinstance(patch, dict) or "expected_hex" in patch:
        raise CommunityBundleError("liblc3 patch-site stock bytes remain embedded")
    if (
        patch.get("expected_size") != 4
        or not isinstance(patch.get("expected_sha256"), str)
        or re.fullmatch(r"[0-9a-f]{64}", patch["expected_sha256"]) is None
    ):
        raise CommunityBundleError("liblc3 patch-site hash contract is invalid")


def _verify_sanitized_ring_overlay(config: Any) -> None:
    sites = config.get("patch_sites") if isinstance(config, dict) else None
    if not isinstance(sites, list) or not sites:
        raise CommunityBundleError("sanitized ring patch-site census is invalid")
    for site in sites:
        if not isinstance(site, dict) or "expected_hex" in site:
            raise CommunityBundleError("ring patch-site stock bytes remain embedded")
        if (
            not isinstance(site.get("expected_size"), int)
            or isinstance(site.get("expected_size"), bool)
            or site["expected_size"] < 1
            or not isinstance(site.get("expected_sha256"), str)
            or re.fullmatch(r"[0-9a-f]{64}", site["expected_sha256"]) is None
        ):
            raise CommunityBundleError("ring patch-site hash contract is invalid")


def _selected_records() -> list[tuple[Path, str]]:
    selected = collect_files()
    records = [
        (path, path.relative_to(REPOSITORY_ROOT).as_posix())
        for path in selected
    ]
    for source, destination in RELOCATED_PUBLIC_SOURCES.items():
        records.append((REPOSITORY_ROOT / source, destination))
    records.sort(key=lambda record: record[1])
    source_paths = {
        path.relative_to(REPOSITORY_ROOT).as_posix() for path, _ in records
    }
    forbidden_sources = sorted(
        source_paths & FORBIDDEN_INVENSENSE_EDMP_MEMBERS
    )
    if forbidden_sources:
        raise CommunityBundleError(
            "forbidden InvenSense EDMP source selected: "
            f"{forbidden_sources[0]}"
        )
    destinations = {destination for _, destination in records}
    if len(destinations) != len(records):
        raise CommunityBundleError("community public-source relocation collides")
    _verify_public_inventory(destinations)
    return records


def _source_capture_digest(
    records: list[tuple[Path, str]], raw_by_path: dict[Path, bytes]
) -> str:
    rows = []
    for path, destination in records:
        lexical = Path(os.path.abspath(path))
        data = raw_by_path[lexical]
        rows.append({
            "archive_path": destination,
            "source_path": path.relative_to(REPOSITORY_ROOT).as_posix(),
            "size": len(data),
            "sha256": _sha256(data),
        })
    return _sha256(
        (json.dumps(rows, sort_keys=True, separators=(",", ":")) + "\n").encode()
    )


def _source_snapshot_identity(metadata: os.stat_result) -> tuple[int, ...]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _read_regular_source_once(path: Path) -> bytes:
    """Read a repository source through one stable, no-follow descriptor."""
    try:
        relative = path.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise CommunityBundleError(f"community source escapes repository: {path}") from error
    if not relative.parts or ".." in relative.parts:
        raise CommunityBundleError(f"community source escapes repository: {path}")

    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    file_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptors: list[int] = []
    try:
        descriptor = os.open(REPOSITORY_ROOT, directory_flags)
        descriptors.append(descriptor)
        for part in relative.parts[:-1]:
            descriptor = os.open(
                part, directory_flags, dir_fd=descriptors[-1]
            )
            descriptors.append(descriptor)
            metadata = os.fstat(descriptor)
            if not stat.S_ISDIR(metadata.st_mode):
                raise CommunityBundleError(
                    f"community source parent is not a directory: {path}"
                )
        descriptor = os.open(
            relative.parts[-1], file_flags, dir_fd=descriptors[-1]
        )
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise CommunityBundleError(
                f"community source is not an independent regular file: {path}"
            )
        if before.st_size > MAX_ARCHIVE_MEMBER_SIZE:
            raise CommunityBundleError(
                f"community source exceeds member cap: {path}"
            )
        chunks: list[bytes] = []
        remaining = MAX_ARCHIVE_MEMBER_SIZE + 1
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        after = os.fstat(descriptor)
        if (
            len(data) > MAX_ARCHIVE_MEMBER_SIZE
            or len(data) != before.st_size
            or _source_snapshot_identity(before)
            != _source_snapshot_identity(after)
        ):
            raise CommunityBundleError(
                f"community source changed during descriptor read: {path}"
            )
        return data
    except CommunityBundleError:
        raise
    except OSError as error:
        raise CommunityBundleError(
            f"community source could not be opened safely: {path}"
        ) from error
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _capture_selected_records() -> tuple[
    list[tuple[Path, str]], dict[Path, bytes], str
]:
    records = _selected_records()
    raw_by_path: dict[Path, bytes] = {}
    for path, _destination in records:
        lexical = Path(os.path.abspath(path))
        raw_by_path.setdefault(lexical, _read_regular_source_once(path))
    digest = _source_capture_digest(records, raw_by_path)
    _require_source_capture_unchanged(records, raw_by_path, digest)
    return records, raw_by_path, digest


def _require_source_capture_unchanged(
    records: list[tuple[Path, str]], raw_by_path: dict[Path, bytes], digest: str
) -> None:
    current_records = _selected_records()
    expected_identity = [
        (Path(os.path.abspath(path)), destination) for path, destination in records
    ]
    current_identity = [
        (Path(os.path.abspath(path)), destination)
        for path, destination in current_records
    ]
    if current_identity != expected_identity:
        raise CommunityBundleError("community source inventory changed during capture")
    observed: dict[Path, bytes] = {}
    for path, _destination in current_records:
        lexical = Path(os.path.abspath(path))
        observed.setdefault(lexical, _read_regular_source_once(path))
    if (
        any(observed[path] != data for path, data in raw_by_path.items())
        or _source_capture_digest(current_records, observed) != digest
    ):
        raise CommunityBundleError("community source bytes changed during capture")


def _source_like_archive_path(path: str) -> bool:
    pure = PurePosixPath(path)
    return pure.suffix in SOURCE_CODE_SUFFIXES or pure.name in {"Makefile", "make.sh"}


def _license_evidence_rows(
    license_expression: str, payload_by_path: dict[str, bytes]
) -> list[dict[str, str]]:
    identifiers = license_expression.split(" OR ")
    rows: list[dict[str, str]] = []
    for identifier in identifiers:
        evidence = LICENSE_EVIDENCE.get(identifier)
        if evidence is None:
            raise CommunityBundleError(
                f"unsupported bundled SPDX license: {license_expression}"
            )
        evidence_path, expected_sha256 = evidence
        evidence_data = payload_by_path.get(evidence_path)
        if evidence_data is None or _sha256(evidence_data) != expected_sha256:
            raise CommunityBundleError(
                f"bundled license evidence changed: {evidence_path}"
            )
        rows.append({
            "path": evidence_path,
            "sha256": expected_sha256,
        })
    return rows


def _inherited_license(
    path: str, payload_by_path: dict[str, bytes]
) -> tuple[str, list[dict[str, str]], str] | None:
    matches = [scope for scope in LICENSE_INHERITANCE_SCOPES if path.startswith(scope[0])]
    if len(matches) > 1:
        raise CommunityBundleError(f"overlapping upstream license scopes: {path}")
    if not matches:
        return None
    prefix, license_id, evidence_path, expected_sha256 = matches[0]
    evidence_data = payload_by_path.get(evidence_path)
    if evidence_data is None or _sha256(evidence_data) != expected_sha256:
        raise CommunityBundleError(
            f"bundled upstream license evidence changed: {evidence_path}"
        )
    return (
        license_id,
        [{"path": evidence_path, "sha256": expected_sha256}],
        prefix,
    )


def _explicit_license_evidence(
    path: str,
    license_expression: str,
    payload_by_path: dict[str, bytes],
) -> tuple[list[dict[str, str]], str]:
    scope = EXPLICIT_LICENSE_EVIDENCE_SCOPES.get(path)
    if scope is None:
        return (
            _license_evidence_rows(license_expression, payload_by_path),
            "direct-spdx-marker",
        )
    expected_license, evidence_path, expected_sha256 = scope
    if license_expression != expected_license:
        raise CommunityBundleError(
            f"explicit upstream license scope changed: {path}"
        )
    evidence_data = payload_by_path.get(evidence_path)
    if evidence_data is None or _sha256(evidence_data) != expected_sha256:
        raise CommunityBundleError(
            f"bundled upstream license evidence changed: {evidence_path}"
        )
    return (
        [{"path": evidence_path, "sha256": expected_sha256}],
        f"direct-spdx-marker+reviewed-upstream-license:{evidence_path}",
    )


def _bundle_member_license_ledger(
    payload_by_path: dict[str, bytes]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ledger: list[dict[str, Any]] = []
    unresolved: list[str] = []
    explicit = 0
    inherited = 0
    project_root = 0
    generated = 0
    license_evidence = 0
    project_infrastructure = 0
    upstream_data = 0
    for path in sorted(payload_by_path):
        data = payload_by_path[path]
        size = len(data)
        digest = _sha256(data)
        member_class: str
        basis: str
        license_expression: str
        evidence: list[dict[str, str]]
        if not _source_like_archive_path(path):
            if path in LICENSE_EVIDENCE_MEMBERS:
                expected_digest = LICENSE_EVIDENCE_MEMBER_SHA256.get(path)
                if expected_digest is None or digest != expected_digest:
                    raise CommunityBundleError(
                        f"bundled license evidence changed: {path}"
                    )
                license_expression = LICENSE_EVIDENCE_MEMBERS[path]
                member_class = "license_evidence"
                basis = "externally-pinned-license-text"
                evidence = [{"path": path, "sha256": expected_digest}]
                license_evidence += 1
            elif path in PROJECT_PREDECISION_RECEIPT_MEMBERS:
                license_expression = "MIT"
                member_class = "project_generated_receipt"
                basis = (
                    "authenticated-root-mit-generated-pre-decision-input-scope"
                )
                evidence = _license_evidence_rows("MIT", payload_by_path)
                generated += 1
            elif path in PROJECT_GENERATED_RECEIPT_MEMBERS:
                license_expression = "MIT"
                member_class = "project_generated_receipt"
                basis = "authenticated-root-mit-generated-receipt-scope"
                evidence = _license_evidence_rows("MIT", payload_by_path)
                generated += 1
            elif path in PROJECT_INFRASTRUCTURE_MIT_MEMBERS:
                license_expression = "MIT"
                member_class = "project_infrastructure"
                basis = "authenticated-root-mit-project-infrastructure-scope"
                evidence = _license_evidence_rows("MIT", payload_by_path)
                project_infrastructure += 1
            elif path in PROJECT_ROOT_MIT_MEMBERS:
                license_expression = "MIT"
                member_class = "project_document_or_data"
                basis = "authenticated-root-mit-ownership-scope"
                evidence = _license_evidence_rows("MIT", payload_by_path)
                project_root += 1
            elif path in UPSTREAM_DATA_MEMBERS:
                license_expression = UPSTREAM_DATA_MEMBERS[path]
                member_class = "upstream_provenance_data"
                basis = "authenticated-component-provenance-scope"
                evidence = _license_evidence_rows(
                    license_expression, payload_by_path
                )
                upstream_data += 1
            else:
                unresolved.append(path)
                continue
            ledger.append({
                "path": path,
                "size": size,
                "sha256": digest,
                "license": license_expression,
                "member_class": member_class,
                "basis": basis,
                "evidence": evidence,
            })
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise CommunityBundleError(
                f"source-license member is not UTF-8: {path}"
            ) from error
        markers = set(SPDX_COMMENT.findall(text))
        if len(markers) > 1:
            raise CommunityBundleError(
                f"conflicting bundled SPDX markers: {path}"
            )
        if markers:
            license_expression = next(iter(markers))
            member_class = "code_source"
            evidence, basis = _explicit_license_evidence(
                path, license_expression, payload_by_path
            )
            explicit += 1
        else:
            inherited_license = _inherited_license(path, payload_by_path)
            if inherited_license is None:
                unresolved.append(path)
                continue
            license_expression, evidence, scope = inherited_license
            member_class = "code_source"
            basis = f"reviewed-upstream-license-scope:{scope}"
            inherited += 1
        ledger.append({
            "path": path,
            "size": size,
            "sha256": digest,
            "license": license_expression,
            "member_class": member_class,
            "basis": basis,
            "evidence": evidence,
        })
    if unresolved:
        raise CommunityBundleError(
            f"bundled member license is unresolved ({len(unresolved)} files): "
            f"{unresolved[0]}"
        )
    closure = {
        "total_members": len(ledger),
        "source_like_members": explicit + inherited,
        "explicit_spdx_members": explicit,
        "reviewed_upstream_scope_members": inherited,
        "project_root_mit_members": project_root,
        "project_generated_receipt_members": generated,
        "project_infrastructure_mit_members": project_infrastructure,
        "license_evidence_members": license_evidence,
        "upstream_provenance_data_members": upstream_data,
        "unresolved_members": 0,
        "ledger_sha256": _sha256(
            (json.dumps(ledger, sort_keys=True, separators=(",", ":")) + "\n").encode()
        ),
    }
    return ledger, closure


def _verify_license_evidence_member_census(
    payload_by_path: dict[str, bytes],
) -> None:
    if set(LICENSE_EVIDENCE_MEMBERS) != set(LICENSE_EVIDENCE_MEMBER_SHA256):
        raise CommunityBundleError("license evidence pin census changed")
    actual = {
        path for path in payload_by_path
        if PurePosixPath(path).name.upper().startswith(
            ("LICENSE", "LICENCE", "COPYING")
        )
    }
    expected = set(LICENSE_EVIDENCE_MEMBERS)
    if actual != expected:
        raise CommunityBundleError(
            "included license evidence member census changed"
        )


def _verify_bundle_member_license_ledger(
    payload_by_path: dict[str, bytes], ledger: Any, closure: Any
) -> None:
    if not isinstance(ledger, list) or not isinstance(closure, dict):
        raise CommunityBundleError("bundle member license ledger is invalid")
    expected_ledger, expected_closure = _bundle_member_license_ledger(payload_by_path)
    if ledger != expected_ledger or closure != expected_closure:
        raise CommunityBundleError("bundle member license ledger changed")


def _license_closure() -> dict[str, Any]:
    audit = audit_g2_release_licensing.analyze()
    if audit["source_errors"]:
        raise CommunityBundleError("source-license metadata is not closed")
    try:
        normalization = importlib.import_module(
            "analyze_g2_project_license_normalization"
        ).analyze()
    except (ImportError, OSError, ValueError) as error:
        raise CommunityBundleError(
            f"community MIT/upstream license closure is unavailable: {error}"
        ) from error
    if not normalization.get("normalization_complete"):
        raise CommunityBundleError("community MIT/upstream license closure is not complete")
    metrics = normalization.get("metrics")
    if not isinstance(metrics, dict):
        raise CommunityBundleError("community license metrics are unavailable")
    distributed = int(metrics.get("distributed_project_mit_normalization_targets", -1))
    normalized = int(metrics.get("distributed_project_files_normalized_mit", -2))
    pending = int(metrics.get("distributed_unique_project_files_pending_normalization", -1))
    upstream_gpl = int(metrics.get("distributed_upstream_gpl_files_preserved", -1))
    if distributed < 1 or normalized != distributed or pending != 0 or upstream_gpl != 1:
        raise CommunityBundleError("community MIT/upstream license metrics are not closed")
    receipt_rows = {
        "overlay": [
            {
                "path": row["path"],
                "sha256": row["sha256"],
                "license": row["license"],
                "classification": row["classification"],
                "errors": row["errors"],
            }
            for row in audit["source_inventory"]
        ],
        "distributed": [
            {
                "path": row["path"],
                "source_sha256": row.get("source_sha256", row.get("sha256")),
                "disposition": row["disposition"],
            }
            for row in normalization["distributed_rows"]
        ],
    }
    for group in receipt_rows.values():
        for row in group:
            digest = row.get("sha256", row.get("source_sha256"))
            if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise CommunityBundleError("community license receipt identity is invalid")
    return {
        "policy": "MIT-where-project-owned-and-upstream-terms-otherwise",
        "normalization_complete": True,
        "overlay_source_files": len(audit["source_inventory"]),
        "overlay_source_errors": 0,
        "distributed_project_files": distributed,
        "normalized_project_files": normalized,
        "pending_project_files": pending,
        "upstream_gpl_files_preserved": upstream_gpl,
        "receipt_sha256": _sha256(
            (json.dumps(receipt_rows, sort_keys=True, separators=(",", ":")) + "\n").encode()
        ),
    }


def _verify_license_closure(closure: Any) -> None:
    if not isinstance(closure, dict) or set(closure) != {
        "policy",
        "normalization_complete",
        "overlay_source_files",
        "overlay_source_errors",
        "distributed_project_files",
        "normalized_project_files",
        "pending_project_files",
        "upstream_gpl_files_preserved",
        "receipt_sha256",
    }:
        raise CommunityBundleError("bundle license closure is invalid")
    if (
        closure["policy"]
        != "MIT-where-project-owned-and-upstream-terms-otherwise"
        or closure["normalization_complete"] is not True
        or not isinstance(closure["overlay_source_files"], int)
        or closure["overlay_source_files"] < 1
        or closure["overlay_source_errors"] != 0
        or not isinstance(closure["distributed_project_files"], int)
        or closure["distributed_project_files"] < 1
        or closure["normalized_project_files"]
        != closure["distributed_project_files"]
        or closure["pending_project_files"] != 0
        or closure["upstream_gpl_files_preserved"] != 1
        or not isinstance(closure["receipt_sha256"], str)
        or re.fullmatch(r"[0-9a-f]{64}", closure["receipt_sha256"]) is None
    ):
        raise CommunityBundleError("bundle license closure is not complete")


def _require_completion_assessment_current() -> None:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, str(COMPLETION_ASSESSMENT_CHECK), "--check"],
        cwd=ROOT,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        raise CommunityBundleError(
            "public completion assessment is stale; run completion-assessment-check:\n"
            + result.stdout
        )


def _completion_assessment_binding(
    payload_by_path: dict[str, bytes],
) -> dict[str, Any]:
    assessment_path, artifact_path, report_path = COMPLETION_REPORT_MEMBERS
    try:
        assessment = json.loads(payload_by_path[assessment_path])
        artifact = json.loads(payload_by_path[artifact_path])
    except KeyError as error:
        raise CommunityBundleError(
            f"completion assessment member is missing: {error.args[0]}"
        ) from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise CommunityBundleError(
            "completion assessment JSON is invalid"
        ) from error
    if not isinstance(assessment, dict) or not isinstance(artifact, dict):
        raise CommunityBundleError("completion assessment shape is invalid")
    try:
        report = payload_by_path[report_path]
        gates = assessment["gates"]
        licensing = assessment["licensing"]
        touch = assessment["touch_admission"]
        source_inputs = assessment["source_inputs"]
    except KeyError as error:
        raise CommunityBundleError(
            f"completion assessment field is missing: {error.args[0]}"
        ) from error
    if not isinstance(gates, dict) or artifact.get("gate_snapshot") != gates:
        raise CommunityBundleError(
            "completion artifact gate snapshot differs from assessment"
        )
    deferred = "blocked by unavailable physical evidence"
    if (
        assessment.get("hardware_operations") != []
        or assessment.get("hardware_validation") != deferred
        or gates.get("hardware_operations") != []
        or gates.get("hardware_validation") != deferred
        or gates.get("hardware_blocker") != deferred
        or artifact.get("hardware_operations") != []
        or artifact.get("hardware_validation") != deferred
    ):
        raise CommunityBundleError(
            "completion assessment hardware policy changed"
        )
    for flag in (
        "source_complete",
        "release_authorized",
        "binary_redistribution_authority_resolved",
    ):
        if gates.get(flag) is not False:
            raise CommunityBundleError(
                f"completion assessment release gate changed: {flag}"
            )
    expected_authorities = {
        "apollo_main",
        "apollo_bootloader",
        "codec",
        "ble_em9305",
        "touch",
        "case",
    }
    unresolved = (
        licensing.get("unresolved_binary_authority")
        if isinstance(licensing, dict)
        else None
    )
    authority_rows = (
        licensing.get("binary_redistribution_authority")
        if isinstance(licensing, dict)
        else None
    )
    if (
        not isinstance(unresolved, list)
        or len(unresolved) != 6
        or set(unresolved) != expected_authorities
        or not isinstance(authority_rows, list)
        or len(authority_rows) != 6
        or {
            row.get("component_id") for row in authority_rows
            if isinstance(row, dict)
            and row.get("redistribution_authority") == "unresolved"
        }
        != expected_authorities
    ):
        raise CommunityBundleError(
            "completion unresolved-authority census changed"
        )
    if not isinstance(source_inputs, list) or not source_inputs:
        raise CommunityBundleError("completion source-input ledger is empty")
    source_paths: list[str] = []
    for row in source_inputs:
        if (
            not isinstance(row, dict)
            or set(row) != {"path", "sha256", "size"}
            or not isinstance(row["path"], str)
            or not row["path"]
            or not isinstance(row["size"], int)
            or isinstance(row["size"], bool)
            or row["size"] < 0
            or not isinstance(row["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is None
        ):
            raise CommunityBundleError(
                "completion source-input row is invalid"
            )
        source_paths.append(row["path"])
    if len(set(source_paths)) != len(source_paths):
        raise CommunityBundleError(
            "completion source-input paths are not unique"
        )
    provenance = (
        touch.get("candidate_provenance")
        if isinstance(touch, dict)
        else None
    )
    if (
        not isinstance(touch, dict)
        or touch.get("production_routed") is not False
        or not isinstance(provenance, dict)
        or provenance.get("production_elf_ownership") is not False
        or provenance.get("nonproduction_source_image_production_routed")
        is not False
    ):
        raise CommunityBundleError(
            "completion Touch provenance production boundary changed"
        )
    artifact_files = artifact.get("files")
    if (
        not isinstance(artifact_files, dict)
        or set(artifact_files) != {"assessment-data.json", "report.html"}
    ):
        raise CommunityBundleError(
            "completion artifact file binding is invalid"
        )
    expected_artifact_files = {
        "assessment-data.json": {
            "size": len(payload_by_path[assessment_path]),
            "sha256": _sha256(payload_by_path[assessment_path]),
        },
        "report.html": {
            "size": len(report),
            "sha256": _sha256(report),
        },
    }
    if artifact_files != expected_artifact_files:
        raise CommunityBundleError(
            "completion artifact member identity changed"
        )
    records = []
    for path in COMPLETION_REPORT_MEMBERS:
        data = payload_by_path.get(path)
        if not isinstance(data, bytes):
            raise CommunityBundleError(
                f"completion assessment member is missing: {path}"
            )
        records.append({
            "path": path,
            "size": len(data),
            "sha256": _sha256(data),
        })
    return {
        "included": True,
        "repository_gate": "completion-assessment-check",
        "members": records,
    }


def _verify_completion_assessment_binding(
    payload_by_path: dict[str, bytes], binding: Any
) -> None:
    if binding != _completion_assessment_binding(payload_by_path):
        raise CommunityBundleError("completion assessment binding changed")


def _dual_profile_proof_binding(
    payload_by_path: dict[str, bytes],
) -> dict[str, Any]:
    records = []
    for path in DUAL_PROFILE_PROOF_MEMBERS:
        data = payload_by_path.get(path)
        if not isinstance(data, bytes):
            raise CommunityBundleError(
                f"dual-profile ownership proof member is missing: {path}"
            )
        records.append({"path": path, "size": len(data), "sha256": _sha256(data)})
    return {
        "checked_at_creation": True,
        "private_observation_artifacts_included": False,
        "independently_rerunnable_from_source_bundle": False,
        "scope": (
            "checked companion, analyzer source, adversarial verification test, and "
            "public interpretation guide; private canonical observations and built "
            "packages are intentionally absent"
        ),
        "members": records,
    }


def create_bundle(output: Path) -> dict[str, Any]:
    _require_completion_assessment_current()
    license_closure = _license_closure()
    _official_provider_hashes()
    rows = []
    payloads: list[tuple[str, bytes]] = []
    selected_records, raw_by_path, source_capture_sha256 = (
        _capture_selected_records()
    )
    for path, archive_path in selected_records:
        data = _bundle_payload(path, raw_by_path[Path(os.path.abspath(path))])
        digest = _sha256(data)
        _preflight_public_export_member(archive_path, data, digest=digest)
        _verify_public_payload(archive_path, data)
        if len(data) > MAX_ARCHIVE_MEMBER_SIZE:
            raise CommunityBundleError(f"community source exceeds member cap: {path}")
        rows.append({"path": archive_path, "size": len(data), "sha256": digest})
        payloads.append((archive_path, data))
    payload_by_path = dict(payloads)
    _verify_public_evidence_receipts(payload_by_path)
    _verify_markdown_link_closure(payload_by_path)
    _verify_license_evidence_member_census(payload_by_path)
    source_license_ledger, source_license_closure = (
        _bundle_member_license_ledger(payload_by_path)
    )
    payload_inventory_sha256 = _sha256(
        (json.dumps(rows, sort_keys=True, separators=(",", ":")) + "\n").encode()
    )
    manifest = {
        "schema_version": 5,
        "format": "openCFW-g2-community-source-bundle",
        "archive_encoding": "zip-stored-fixed-metadata",
        "official_package_required_locally": {
            "size": OFFICIAL_PACKAGE_SIZE,
            "sha256": OFFICIAL_PACKAGE_SHA256,
        },
        "contains_official_firmware_payloads": False,
        "contains_stock_firmware_guard_bytes": False,
        "stock_guard_representation": "size-and-sha256-authenticated-local-base",
        "stock_guard_scope": (
            "known overlay patch guards and component-builder donor ingress; "
            "direct literal decoder calls, long/dense/split encoded byte bodies, "
            "unreviewed numeric byte arrays, and raw executable directives rejected"
        ),
        "completion_assessment": _completion_assessment_binding(
            payload_by_path
        ),
        "dual_profile_ownership_proof": _dual_profile_proof_binding(payload_by_path),
        "license_closure": license_closure,
        "member_license_closure": source_license_closure,
        "member_license_ledger": source_license_ledger,
        "source_capture_sha256": source_capture_sha256,
        "payload_inventory_sha256": payload_inventory_sha256,
        "files": rows,
    }
    manifest_data = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    if len(payloads) + 1 > MAX_ARCHIVE_MEMBERS:
        raise CommunityBundleError("community archive member cap exceeded")
    if len(manifest_data) > MAX_ARCHIVE_MEMBER_SIZE:
        raise CommunityBundleError("community manifest exceeds member cap")
    if len(manifest_data) + sum(len(data) for _, data in payloads) > \
            MAX_ARCHIVE_UNCOMPRESSED_SIZE:
        raise CommunityBundleError("community archive uncompressed-size cap exceeded")
    output = Path(os.path.abspath(output))
    _ensure_safe_directory_path(output.parent, create=True)
    prior_output = (
        _read_regular_path_snapshot(
            output,
            maximum_size=MAX_ARCHIVE_SIZE,
            label="existing community archive",
        )
        if os.path.lexists(output)
        else None
    )
    try:
        with tempfile.TemporaryFile(mode="w+b") as temporary:
            with zipfile.ZipFile(
                temporary, "w", compression=zipfile.ZIP_STORED
            ) as archive:
                for archive_path, data in [
                    ("BUNDLE-MANIFEST.json", manifest_data), *payloads
                ]:
                    info = zipfile.ZipInfo(archive_path, (1980, 1, 1, 0, 0, 0))
                    info.create_system = 3
                    info.compress_type = zipfile.ZIP_STORED
                    permissions = (
                        0o755 if archive_path in EXECUTABLE_ARCHIVE_PATHS else 0o644
                    )
                    info.external_attr = (0o100000 | permissions) << 16
                    archive.writestr(info, data)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary.seek(0)
            candidate = temporary.read(MAX_ARCHIVE_SIZE + 1)
            if temporary.read(1):
                raise CommunityBundleError(
                    "community archive byte-size cap exceeded"
                )
        if len(candidate) > MAX_ARCHIVE_SIZE:
            raise CommunityBundleError("community archive byte-size cap exceeded")
        _verify_bundle_bytes(candidate)
        _require_source_capture_unchanged(
            selected_records, raw_by_path, source_capture_sha256
        )
        if _license_closure() != license_closure:
            raise CommunityBundleError("community license closure changed during capture")
        _require_completion_assessment_current()
        if prior_output is None:
            if os.path.lexists(output):
                raise CommunityBundleError(
                    "community archive output appeared before publication"
                )
        elif _read_regular_path_snapshot(
            output,
            maximum_size=MAX_ARCHIVE_SIZE,
            label="existing community archive",
        ) != prior_output:
            raise CommunityBundleError(
                "existing community archive changed before publication"
            )
        try:
            _atomic_write_unique(
                output,
                candidate,
                mode=0o644,
                expected_prior=(prior_output[0] if prior_output else None),
            )
        except Exception:
            published = None
            try:
                published = _read_regular_path_snapshot(
                    output,
                    maximum_size=MAX_ARCHIVE_SIZE,
                    label="failed community archive publication",
                )
            except CommunityBundleError:
                pass
            if published is not None and published[0] == candidate:
                try:
                    if prior_output is None:
                        output.unlink(missing_ok=True)
                    else:
                        _atomic_write_unique(
                            output,
                            prior_output[0],
                            mode=prior_output[1],
                            expected_prior=candidate,
                        )
                except (OSError, CommunityBundleError) as rollback_error:
                    raise CommunityBundleError(
                        "community archive publication rollback failed: "
                        f"{rollback_error}"
                    ) from rollback_error
            raise
    finally:
        pass
    return {
        "path": str(output),
        "size": len(candidate),
        "sha256": _sha256(candidate),
        "files": len(rows),
        "source_capture_sha256": source_capture_sha256,
        "license_closure_sha256": license_closure["receipt_sha256"],
    }


def _validate_archive_names(names: list[str]) -> None:
    canonical = [name.casefold() for name in names]
    if (
        not names
        or names[0] != "BUNDLE-MANIFEST.json"
        or len(names) != len(set(names))
        or len(canonical) != len(set(canonical))
        or len(names) > MAX_ARCHIVE_MEMBERS
    ):
        raise CommunityBundleError("bundle member order or uniqueness is invalid")
    members = set(names)
    for name in names:
        pure = PurePosixPath(name)
        if len(name) > 512 or any(len(part) > 255 for part in pure.parts):
            raise CommunityBundleError(f"unsafe bundle member: {name}")
        # ``PurePath.parents`` gained slice support after Python 3.9.  Convert
        # explicitly so verification also works with the repository's Apple
        # Python toolchain while still excluding the terminal ``.`` parent.
        parents = tuple(pure.parents)[:-1]
        if any(parent.as_posix() in members for parent in parents):
            raise CommunityBundleError(f"bundle file/parent collision: {name}")


def _validate_archive_info(info: zipfile.ZipInfo) -> None:
    name = info.filename
    pure = PurePosixPath(name)
    expected_permissions = 0o755 if name in EXECUTABLE_ARCHIVE_PATHS else 0o644
    expected_external_attr = (0o100000 | expected_permissions) << 16
    if (
        pure.is_absolute()
        or pure.as_posix() != name
        or "\\" in name
        or ".." in pure.parts
        or not _allowed_archive_file(pure)
        or info.is_dir()
        or info.create_system != 3
        or info.create_version != 20
        or info.extract_version != 20
        or info.reserved != 0
        or info.flag_bits != 0
        or info.volume != 0
        or info.internal_attr != 0
        or info.external_attr != expected_external_attr
        or info.date_time != (1980, 1, 1, 0, 0, 0)
        or info.compress_type != zipfile.ZIP_STORED
        or info.file_size > MAX_ARCHIVE_MEMBER_SIZE
        or info.compress_size != info.file_size
        or info.extra
        or info.comment
    ):
        raise CommunityBundleError(f"unsafe bundle member: {name}")


def _verify_bundle_bytes(bundle_data: bytes) -> dict[str, Any]:
    if len(bundle_data) > MAX_ARCHIVE_SIZE:
        raise CommunityBundleError("community archive byte-size cap exceeded")
    _official_provider_hashes()
    with zipfile.ZipFile(io.BytesIO(bundle_data)) as archive:
        names = archive.namelist()
        _validate_archive_names(names)
        if archive.comment:
            raise CommunityBundleError("bundle archive comment is forbidden")
        preflight_total = 0
        for info in archive.infolist():
            _validate_archive_info(info)
            preflight_total += info.file_size
            if preflight_total > MAX_ARCHIVE_UNCOMPRESSED_SIZE:
                raise CommunityBundleError(
                    "community archive uncompressed-size cap exceeded"
                )
        try:
            manifest = json.loads(archive.read(names[0]))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise CommunityBundleError("bundle manifest is not valid JSON") from error
        if (
            not isinstance(manifest, dict)
            or set(manifest) != BUNDLE_MANIFEST_FIELDS
            or
            manifest.get("schema_version") != 5
            or manifest.get("format") != "openCFW-g2-community-source-bundle"
            or manifest.get("archive_encoding") != "zip-stored-fixed-metadata"
            or manifest.get("contains_official_firmware_payloads") is not False
            or manifest.get("contains_stock_firmware_guard_bytes") is not False
            or manifest.get("stock_guard_representation")
            != "size-and-sha256-authenticated-local-base"
            or manifest.get("stock_guard_scope") != (
                "known overlay patch guards and component-builder donor ingress; "
                "direct literal decoder calls, long/dense/split encoded byte bodies, "
                "unreviewed numeric byte arrays, and raw executable directives rejected"
            )
            or not isinstance(manifest.get("completion_assessment"), dict)
            or set(manifest["completion_assessment"])
            != {"included", "repository_gate", "members"}
            or manifest["completion_assessment"].get("included") is not True
            or manifest["completion_assessment"].get("repository_gate")
            != "completion-assessment-check"
            or not isinstance(
                manifest["completion_assessment"].get("members"), list
            )
            or not isinstance(manifest.get("dual_profile_ownership_proof"), dict)
            or manifest.get("official_package_required_locally") != {
                "size": OFFICIAL_PACKAGE_SIZE,
                "sha256": OFFICIAL_PACKAGE_SHA256,
            }
            or not isinstance(manifest.get("source_capture_sha256"), str)
            or re.fullmatch(r"[0-9a-f]{64}", manifest["source_capture_sha256"])
            is None
            or not isinstance(manifest.get("payload_inventory_sha256"), str)
            or re.fullmatch(r"[0-9a-f]{64}", manifest["payload_inventory_sha256"])
            is None
        ):
            raise CommunityBundleError("bundle manifest envelope is invalid")
        _verify_license_closure(manifest.get("license_closure"))
        rows = manifest.get("files")
        if not isinstance(rows, list):
            raise CommunityBundleError("bundle file inventory is invalid")
        for row in rows:
            if (
                not isinstance(row, dict)
                or set(row) != {"path", "size", "sha256"}
                or not isinstance(row["path"], str)
                or not row["path"]
                or not isinstance(row["size"], int)
                or isinstance(row["size"], bool)
                or row["size"] < 0
                or row["size"] > MAX_ARCHIVE_MEMBER_SIZE
                or not isinstance(row["sha256"], str)
                or len(row["sha256"]) != 64
                or any(character not in "0123456789abcdef" for character in row["sha256"])
            ):
                raise CommunityBundleError("bundle file record is invalid")
        expected_order = [row["path"] for row in rows]
        expected = {row["path"]: row for row in rows}
        if len(expected) != len(rows) or names[1:] != expected_order:
            raise CommunityBundleError("bundle manifest/member set differs")
        if _sha256(
            (json.dumps(rows, sort_keys=True, separators=(",", ":")) + "\n").encode()
        ) != manifest["payload_inventory_sha256"]:
            raise CommunityBundleError("bundle payload inventory receipt changed")
        _verify_public_inventory(set(expected))
        total_uncompressed = 0
        payload_by_path: dict[str, bytes] = {}
        for info in archive.infolist():
            name = info.filename
            _validate_archive_info(info)
            total_uncompressed += info.file_size
            if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_SIZE:
                raise CommunityBundleError(
                    "community archive uncompressed-size cap exceeded"
                )
            if name == "BUNDLE-MANIFEST.json":
                continue
            data = archive.read(name)
            payload_by_path[name] = data
            digest = _preflight_public_export_member(name, data)
            _verify_public_payload(name, data)
            row = expected[name]
            if len(data) != row["size"] or digest != row["sha256"]:
                raise CommunityBundleError(f"bundle member identity changed: {name}")
        _verify_public_evidence_receipts(payload_by_path)
        _verify_smoke_python_import_closure(payload_by_path)
        _verify_markdown_link_closure(payload_by_path)
        _verify_license_evidence_member_census(payload_by_path)
        _verify_bundle_member_license_ledger(
            payload_by_path,
            manifest.get("member_license_ledger"),
            manifest.get("member_license_closure"),
        )
        _verify_completion_assessment_binding(
            payload_by_path, manifest["completion_assessment"]
        )
        if (
            manifest["dual_profile_ownership_proof"]
            != _dual_profile_proof_binding(payload_by_path)
        ):
            raise CommunityBundleError(
                "dual-profile ownership proof binding changed"
            )
        try:
            overlay = json.loads(archive.read(SANITIZED_APOLLO_OVERLAY))
        except (KeyError, json.JSONDecodeError, UnicodeDecodeError) as error:
            raise CommunityBundleError("sanitized Apollo overlay is unavailable") from error
        _verify_nemavg_public_boundary(payload_by_path, overlay)
        try:
            liblc3_overlay = json.loads(archive.read(SANITIZED_LIBLC3_OVERLAY))
        except (KeyError, json.JSONDecodeError, UnicodeDecodeError) as error:
            raise CommunityBundleError("sanitized liblc3 overlay is unavailable") from error
        _verify_sanitized_liblc3_overlay(liblc3_overlay)
        try:
            ring_overlay = json.loads(archive.read(SANITIZED_RING_OVERLAY))
        except (KeyError, json.JSONDecodeError, UnicodeDecodeError) as error:
            raise CommunityBundleError("sanitized ring overlay is unavailable") from error
        _verify_sanitized_ring_overlay(ring_overlay)
    return manifest


def verify_bundle(bundle: Path) -> dict[str, Any]:
    """Verify one immutable snapshot of a community archive path."""
    return _verify_bundle_bytes(_read_bundle_path_once(bundle))


def _read_bundle_path_once(bundle: Any) -> bytes:
    """Read one stable, independent regular-file snapshot with a pre-read cap."""
    try:
        path = Path(os.fspath(bundle))
    except TypeError:
        # Focused tests use a one-shot reader to prove that verification never
        # reopens its input. Production CLI arguments always enter the path arm.
        return bundle.read_bytes()
    return _read_regular_path_once(
        path,
        maximum_size=MAX_ARCHIVE_SIZE,
        label="community archive",
    )


def _read_regular_path_once(
    path: Path,
    *,
    maximum_size: int,
    label: str,
    expected_size: int | None = None,
) -> bytes:
    """Read a no-follow regular path through one stable file descriptor."""
    return _read_regular_path_snapshot(
        path,
        maximum_size=maximum_size,
        label=label,
        expected_size=expected_size,
    )[0]


def _read_regular_path_snapshot(
    path: Path,
    *,
    maximum_size: int,
    label: str,
    expected_size: int | None = None,
) -> tuple[bytes, int]:
    """Return stable bytes/mode through a no-follow absolute descriptor chain."""
    absolute = Path(os.path.abspath(path))
    parent_descriptor: int | None = None
    try:
        parent_descriptor = _open_directory_path(absolute.parent)
    except OSError as error:
        if parent_descriptor is not None:
            os.close(parent_descriptor)
        raise CommunityBundleError(
            f"{label} path could not be opened safely"
        ) from error
    try:
        return _read_regular_at_snapshot(
            parent_descriptor,
            absolute.name,
            maximum_size=maximum_size,
            label=label,
            expected_size=expected_size,
        )
    finally:
        os.close(parent_descriptor)


def _read_regular_at_snapshot(
    parent_descriptor: int,
    name: str,
    *,
    maximum_size: int,
    label: str,
    expected_size: int | None = None,
) -> tuple[bytes, int]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(name, flags, dir_fd=parent_descriptor)
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise CommunityBundleError(f"{label} path is a symlink") from error
        raise CommunityBundleError(
            f"{label} path could not be opened safely"
        ) from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise CommunityBundleError(
                f"{label} path is not an independent regular file"
            )
        if before.st_size > maximum_size:
            raise CommunityBundleError(f"{label} byte-size cap exceeded")
        if expected_size is not None and before.st_size != expected_size:
            raise CommunityBundleError(f"{label} size is not authenticated")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            data = handle.read(maximum_size + 1)
        after = os.fstat(descriptor)
        identity_before = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        identity_after = (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if (
            len(data) > maximum_size
            or len(data) != before.st_size
            or identity_before != identity_after
        ):
            raise CommunityBundleError(f"{label} changed during read")
        return data, stat.S_IMODE(before.st_mode)
    finally:
        os.close(descriptor)


def authenticate_official_package(path: Path) -> dict[str, bytes]:
    image = _read_regular_path_once(
        path,
        maximum_size=OFFICIAL_PACKAGE_SIZE,
        expected_size=OFFICIAL_PACKAGE_SIZE,
        label="local official G2 package",
    )
    if len(image) != OFFICIAL_PACKAGE_SIZE or _sha256(image) != OFFICIAL_PACKAGE_SHA256:
        raise CommunityBundleError("local official G2 package identity is not authenticated")
    manifest = open_cfw.load_manifest(BASE_MANIFEST)
    _official_provider_hashes(manifest)
    open_cfw.validate_evenota_image(image, manifest)
    payloads: dict[str, bytes] = {}
    count = struct.unpack_from("<I", image, 8)[0]
    for index, component in enumerate(manifest["components"]):
        if index >= count:
            raise CommunityBundleError("official package component count changed")
        _, body_offset, body_size, _ = struct.unpack_from(
            "<IIII", image, open_cfw.EVENOTA_TOC_OFFSET + index * open_cfw.EVENOTA_TOC_ENTRY_SIZE
        )
        start = body_offset + open_cfw.EVENOTA_COMPONENT_HEADER_SIZE
        payload = image[start:body_offset + body_size]
        provider = component["provider"]
        if len(payload) != provider["size"] or _sha256(payload) != provider["sha256"]:
            raise CommunityBundleError(f"official component identity changed: {component['name']}")
        payloads[provider["path"]] = payload
    return payloads


def _atomic_write_unique(
    path: Path,
    data: bytes,
    *,
    mode: int = 0o644,
    expected_prior: bytes | None | object = _UNCONSTRAINED_PRIOR,
) -> None:
    absolute = Path(os.path.abspath(path))
    parent_descriptor = _open_directory_path(absolute.parent, create=True)
    temporary_name = f".{absolute.name}.{secrets.token_hex(16)}.tmp"
    flags = (
        os.O_RDWR
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(
            temporary_name, flags, mode, dir_fd=parent_descriptor
        )
    except Exception:
        os.close(parent_descriptor)
        raise
    try:
        with os.fdopen(descriptor, "w+b", closefd=False) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
            os.fchmod(handle.fileno(), mode)
            handle.seek(0)
            if handle.read(len(data) + 1) != data:
                raise CommunityBundleError(f"atomic write readback changed: {path}")
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise CommunityBundleError(f"atomic write readback changed: {path}")
        try:
            existing = os.open(
                absolute.name,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=parent_descriptor,
            )
        except FileNotFoundError:
            existing = None
        except OSError as error:
            raise CommunityBundleError(
                f"atomic write target could not be opened safely: {path}"
            ) from error
        if existing is not None:
            try:
                metadata = os.fstat(existing)
                if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                    raise CommunityBundleError(
                        f"atomic write target is not an independent regular file: {path}"
                    )
                if expected_prior is None:
                    raise CommunityBundleError(
                        f"atomic write target appeared before publication: {path}"
                    )
                if expected_prior is not _UNCONSTRAINED_PRIOR:
                    if not isinstance(expected_prior, bytes):
                        raise CommunityBundleError(
                            f"atomic write prior constraint is invalid: {path}"
                        )
                    with os.fdopen(existing, "rb", closefd=False) as handle:
                        observed_prior = handle.read(len(expected_prior) + 1)
                    after = os.fstat(existing)
                    if (
                        observed_prior != expected_prior
                        or _source_snapshot_identity(metadata)
                        != _source_snapshot_identity(after)
                    ):
                        raise CommunityBundleError(
                            f"atomic write target changed before publication: {path}"
                        )
            finally:
                os.close(existing)
        elif expected_prior not in (_UNCONSTRAINED_PRIOR, None):
            raise CommunityBundleError(
                f"atomic write target disappeared before publication: {path}"
            )
        os.replace(
            temporary_name,
            absolute.name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
        )
        if _read_regular_at_snapshot(
            parent_descriptor,
            absolute.name,
            maximum_size=len(data),
            expected_size=len(data),
            label=f"published atomic write {absolute}",
        )[0] != data:
            raise CommunityBundleError(f"published atomic write changed: {path}")
        os.fsync(parent_descriptor)
    finally:
        os.close(descriptor)
        try:
            os.unlink(temporary_name, dir_fd=parent_descriptor)
        except FileNotFoundError:
            pass
        os.close(parent_descriptor)


def _safe_workspace_target(
    workspace: Path, relative: str, *, require_directory: bool = False
) -> Path:
    pure = PurePosixPath(relative)
    if (
        pure.is_absolute()
        or pure.as_posix() != relative
        or ".." in pure.parts
        or not pure.parts
        or SAFE_ARCHIVE_PATH.fullmatch(relative) is None
    ):
        raise CommunityBundleError(f"unsafe local workspace path: {relative!r}")
    workspace = _ensure_safe_directory_path(workspace)
    target = workspace.joinpath(*pure.parts)
    cursor = workspace
    for index, part in enumerate(pure.parts):
        cursor = cursor / part
        if not cursor.exists() and not cursor.is_symlink():
            continue
        metadata = cursor.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise CommunityBundleError(
                f"local workspace path traverses a symlink: {relative}"
            )
        if index < len(pure.parts) - 1 and not stat.S_ISDIR(metadata.st_mode):
            raise CommunityBundleError(
                f"local workspace parent is not a directory: {relative}"
            )
        if index == len(pure.parts) - 1:
            expected = stat.S_ISDIR if require_directory else stat.S_ISREG
            if not expected(metadata.st_mode):
                raise CommunityBundleError(
                    f"local workspace target type changed: {relative}"
                )
            if not require_directory and metadata.st_nlink != 1:
                raise CommunityBundleError(
                    f"local workspace target is not an independent regular file: "
                    f"{relative}"
                )
    return target


def prepare_local_workspace(official_package: Path, workspace: Path) -> dict[str, Any]:
    payloads = authenticate_official_package(official_package)
    workspace = _ensure_safe_directory_path(workspace)
    manifest_path = _safe_workspace_target(workspace, "manifests/g2-2.2.6.10.json")
    if not manifest_path.is_file():
        raise CommunityBundleError("workspace is not an extracted community source bundle")
    receipt_path = _safe_workspace_target(workspace, HYDRATION_RECEIPT)
    receipt_path.unlink(missing_ok=True)
    include_directories = _configured_include_dir_names(workspace)
    for relative in include_directories:
        target = _safe_workspace_target(workspace, relative, require_directory=True)
        _ensure_safe_directory_path(target, create=True)
    targets: dict[str, Path] = {
        relative: _safe_workspace_target(workspace, relative)
        for relative in payloads
    }
    originals = {
        relative: (
            _read_regular_path_snapshot(
                target,
                maximum_size=OFFICIAL_PACKAGE_SIZE,
                label=f"existing hydrated provider {relative}",
            )
            if target.exists()
            else None
        )
        for relative, target in targets.items()
    }
    published_relatives: list[str] = []
    try:
        for relative, payload in payloads.items():
            original = originals[relative]
            _atomic_write_unique(
                targets[relative],
                payload,
                expected_prior=(original[0] if original else None),
            )
            published_relatives.append(relative)
        provider_rows = []
        for relative, payload in sorted(payloads.items()):
            observed = _read_regular_path_once(
                targets[relative],
                maximum_size=len(payload),
                expected_size=len(payload),
                label=f"hydrated official provider {relative}",
            )
            if observed != payload:
                raise CommunityBundleError(
                    f"hydrated official provider readback changed: {relative}"
                )
            provider_rows.append({
                "path": relative,
                "size": len(observed),
                "sha256": _sha256(observed),
            })
        receipt = {
            "schema_version": 1,
            "format": "openCFW-local-official-hydration",
            "official_package": {
                "size": OFFICIAL_PACKAGE_SIZE,
                "sha256": OFFICIAL_PACKAGE_SHA256,
            },
            "providers": provider_rows,
            "include_directories": include_directories,
            **_software_only_operation_receipt(),
        }
        receipt_data = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
        _atomic_write_unique(receipt_path, receipt_data, expected_prior=None)
    except Exception:
        receipt_path.unlink(missing_ok=True)
        rollback_errors: list[str] = []
        for relative in reversed(published_relatives):
            target = targets[relative]
            original = originals[relative]
            try:
                if original is None:
                    target.unlink(missing_ok=True)
                else:
                    _atomic_write_unique(
                        target,
                        original[0],
                        mode=original[1],
                        expected_prior=payloads[relative],
                    )
            except (OSError, CommunityBundleError) as error:
                rollback_errors.append(f"{relative}: {error}")
        if rollback_errors:
            raise CommunityBundleError(
                f"local hydration rollback failed: {rollback_errors[0]}"
            )
        raise
    return {
        "providers": len(payloads),
        "include_directories": len(include_directories),
        "workspace": str(workspace),
        "receipt": str(receipt_path),
        "receipt_sha256": _sha256(receipt_data),
    }


def _community_smoke_commands(
    python_executable: str = sys.executable,
    *,
    clang: str | None = None,
    toolchain_profile: str = "apple-clang",
) -> tuple[list[str], ...]:
    """Return the exact command sequence used by the extracted-tree smoke."""
    toolchain_arguments = (
        ["--clang", clang, "--toolchain-profile", toolchain_profile]
        if clang is not None
        else []
    )
    return (
        [
            python_executable,
            "-m",
            "unittest",
            "-v",
            *COMMUNITY_LOCAL_BUILD_TEST_MODULES,
        ],
        [
            python_executable,
            "components/bootloader/core_overlay/build_component.py",
            *toolchain_arguments,
        ],
        [
            python_executable,
            "components/apollo_main/core_overlay/build_component.py",
            *toolchain_arguments,
        ],
        [
            python_executable,
            "tools/open_cfw.py",
            "build",
            "--manifest",
            "manifests/g2-2.2.6.10-core-source.json",
            "--output-dir",
            "build/source",
            "--toolchain-profile",
            toolchain_profile,
        ],
        [
            python_executable,
            "tools/open_cfw.py",
            "verify",
            "--manifest",
            "manifests/g2-2.2.6.10-core-source.json",
        ],
        [
            python_executable,
            "tools/open_cfw.py",
            "verify-artifacts",
            "--manifest",
            "manifests/g2-2.2.6.10-core-source.json",
            "--output-dir",
            "build/source",
            "--toolchain-profile",
            toolchain_profile,
        ],
    )


def _software_only_operation_receipt() -> dict[str, Any]:
    return {
        "hardware_operations": [],
        "hardware_validation": DEFERRED_HARDWARE_VALIDATION,
    }


def smoke_build(
    bundle: Path,
    official_package: Path,
    *,
    clang: str | None = None,
    toolchain_profile: str | None = None,
    make_executable: str = "make",
) -> dict[str, Any]:
    """Exercise the recipient hydration and source-build workflow in isolation."""
    preflight = preflight_local_environment(
        clang, toolchain_profile, make_executable
    )
    bundle_data = _read_bundle_path_once(bundle)
    _verify_bundle_bytes(bundle_data)
    with tempfile.TemporaryDirectory(
        prefix="opencfw-community-smoke-",
        dir=_physical_temporary_root(),
    ) as temporary:
        extraction_root = Path(temporary)
        with zipfile.ZipFile(io.BytesIO(bundle_data)) as archive:
            for info in archive.infolist():
                target = extraction_root / PurePosixPath(info.filename)
                _ensure_safe_directory_path(target.parent, create=True)
                _atomic_write_unique(
                    target,
                    archive.read(info),
                    mode=(
                        0o755
                        if info.filename in EXECUTABLE_ARCHIVE_PATHS
                        else 0o644
                    ),
                    expected_prior=None,
                )
        workspace = extraction_root / "g2"
        prepare_local_workspace(official_package, workspace)
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        for command in _community_smoke_commands(
            clang=preflight["clang"]["executable"],
            toolchain_profile=preflight["toolchain_profile"],
        ):
            result = subprocess.run(
                command,
                cwd=workspace,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if result.returncode:
                raise CommunityBundleError(
                    f"community smoke command failed ({' '.join(command)}):\n"
                    f"{result.stdout}"
                )
        package = (
            workspace
            / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
        )
        package_data = _read_regular_path_once(
            package,
            maximum_size=MAX_ARCHIVE_SIZE,
            label="community smoke package",
        )
        flash_plan = json.loads(_read_regular_path_once(
            workspace / "build/source/flash-plan.json",
            maximum_size=MAX_ARCHIVE_SIZE,
            label="community smoke flash plan",
        ))
        counts = {
            key: len(flash_plan[key])
            for key in (
                "flash_regions",
                "unresolved_flash_regions",
                "container_only_regions",
                "protected_regions",
            )
        }
        return {
            "package_size": len(package_data),
            "package_sha256": _sha256(package_data),
            "bundle_sha256": _sha256(bundle_data),
            "toolchain_profile": preflight["toolchain_profile"],
            "flash_plan_counts": counts,
            **_software_only_operation_receipt(),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("output", type=Path)
    verify = subparsers.add_parser("verify")
    verify.add_argument("bundle", type=Path)
    prepare = subparsers.add_parser("prepare-local")
    prepare.add_argument("official_package", type=Path)
    prepare.add_argument("workspace", type=Path)
    preflight = subparsers.add_parser("preflight-local")
    preflight.add_argument("--clang")
    preflight.add_argument("--toolchain-profile")
    preflight.add_argument("--make", default="make", dest="make_executable")
    smoke = subparsers.add_parser("smoke-build")
    smoke.add_argument("bundle", type=Path)
    smoke.add_argument("official_package", type=Path)
    smoke.add_argument("--clang")
    smoke.add_argument("--toolchain-profile")
    smoke.add_argument("--make", default="make", dest="make_executable")
    args = parser.parse_args(argv)
    if args.command == "create":
        print(json.dumps(create_bundle(args.output), sort_keys=True))
    elif args.command == "verify":
        manifest = verify_bundle(args.bundle)
        print(f"Verified community bundle: {len(manifest['files'])} source files")
    elif args.command == "prepare-local":
        print(json.dumps(prepare_local_workspace(args.official_package, args.workspace), sort_keys=True))
    elif args.command == "preflight-local":
        print(json.dumps(preflight_local_environment(
            args.clang, args.toolchain_profile, args.make_executable
        ), sort_keys=True))
    else:
        print(json.dumps(smoke_build(
            args.bundle,
            args.official_package,
            clang=args.clang,
            toolchain_profile=args.toolchain_profile,
            make_executable=args.make_executable,
        ), sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CommunityBundleError, open_cfw.OpenCFWError, OSError, zipfile.BadZipFile) as error:
        print(f"community distribution: error: {error}")
        raise SystemExit(1)
