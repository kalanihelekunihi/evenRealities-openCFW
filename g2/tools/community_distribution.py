#!/usr/bin/env python3
"""Build and hydrate the vendor-byte-free G2 community source bundle."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import io
import json
import os
import re
import stat
import struct
import subprocess
import sys
import tempfile
import time
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
MAX_ARCHIVE_MEMBERS = 4_096
MAX_ARCHIVE_MEMBER_SIZE = 32 * 1024 * 1024
MAX_ARCHIVE_UNCOMPRESSED_SIZE = 256 * 1024 * 1024
MAX_ARCHIVE_SIZE = 256 * 1024 * 1024
HYDRATION_RECEIPT = ".open-cfw-local-hydration.json"
COMPLETION_ASSESSMENT_CHECK = ROOT / "tools/generate_g2_completion_report.py"


def _read_json_path(path: Path) -> Any:
    """Read a concurrently generated JSON input only from a stable snapshot."""
    last_error: Exception | None = None
    for _attempt in range(20):
        try:
            first = path.read_bytes()
            second = path.read_bytes()
            if first != second:
                time.sleep(0.01)
                continue
            return json.loads(first)
        except (OSError, json.JSONDecodeError) as error:
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
FORBIDDEN_SUFFIXES = {".bin", ".evenota", ".elf", ".o", ".a", ".hex", ".uf2"}
FORBIDDEN_FILENAMES = {"EVIDENCE.md"}
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
SOURCE_CODE_SUFFIXES = {".c", ".h", ".S", ".s", ".inc", ".ld", ".lds", ".py", ".mk"}
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
    "components/touch/source_image",
)
COMMUNITY_PUBLIC_SOURCE_GLOBS = (
    ("components/apollo_main/core_overlay/pt_protocol*.c", 14),
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
    "tools/detect_toolchain.py",
    "tools/audit_g2_release_licensing.py",
    "tools/community_distribution.py",
    "tools/analyze_g2_touch_source_image.py",
    "tools/analyze_g2_case_source_image.py",
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
    "tools/manifests/gx8002-source-readiness.tsv",
    "tools/manifests/g2-touch-source-image-summary.json",
    "tools/manifests/g2-case-source-image-summary.json",
    "tools/manifests/g2-nemavg-stroke-caps-candidate-summary.json",
    "tools/manifests/g2-clkmgr-divider-candidate-summary.json",
    "tools/manifests/g2-pt-protocol-source-summary.json",
    "tests/test_ring_gesture_provenance.py",
    "tests/test_analyze_g2_touch_source_image.py",
    "tests/test_analyze_g2_case_source_image.py",
    "tests/test_touch_source_image.py",
    "tests/test_runtime_nemavg_stroke_caps_candidate.py",
    "tests/fixtures/runtime_nemavg_stroke_caps_host.c",
    "tests/test_runtime_clkmgr_divider_candidate.py",
    "tests/fixtures/runtime_clkmgr_divider_candidate_host.c",
    "tests/test_apollo_pt_protocol_provider.py",
)
EXPLICIT_REPOSITORY_FILES = (
    "LICENSE",
    "NOTICE",
    "README.md",
)
EXECUTABLE_ARCHIVE_PATHS = {"g2/make.sh"}
REVIEWED_GENERATED_HEX_CONSTRUCTORS = {
    # Four fixed FWPK format/version bytes, not donor executable content.
    "g2/components/touch/source_image/build_image.py",
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
    ("g2/third_party/invensense-icm45608/", "BSD-3-Clause", "g2/third_party/invensense-icm45608/LICENSE", "68bed9c72222b77b8744add292f524000661c6537d960adeaf740722b0b2637f"),
    ("g2/third_party/liblc3/", "Apache-2.0", "g2/third_party/liblc3/LICENSE", "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"),
    ("g2/third_party/lz4/", "BSD-2-Clause", "g2/third_party/lz4/LICENSE", "8b58c446121a109ccf32edc094bba3010a3d85e4ee3702950db55e4d3e87736c"),
    ("g2/third_party/tinyframe/", "MIT", "g2/third_party/tinyframe/LICENSE", "eb7b9df3ca390100d31f9aac23f2d8dfe0183a63987112675fc58af9a42f6874"),
    ("g2/third_party/tlsf/", "BSD-3-Clause", "g2/third_party/tlsf/tlsf.h", "f7f73c48810ba60203095667c226e5a600a6ea0f69afba48efff6efbaa628d4f"),
    ("g2/components/apollo_main/core_overlay/runtime_easylogger_", "MIT", "g2/third_party/easylogger/LICENSE", "4a7be67e9701d0344c62d1b92eed8f40b874d00d64a9ee6b3853eb47ef4ea7f9"),
    ("g2/components/apollo_main/core_overlay/runtime_tinyframe_", "MIT", "g2/third_party/tinyframe/LICENSE", "eb7b9df3ca390100d31f9aac23f2d8dfe0183a63987112675fc58af9a42f6874"),
    ("g2/components/apollo_main/ring_gesture/upstream/", "GPL-3.0-only", "g2/components/apollo_main/ring_gesture/LICENSE", "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"),
    ("g2/components/shared/cmbacktrace/", "MIT", "g2/third_party/cmbacktrace/LICENSE", "e8ed0e84184d2130bd1fcf5a52ce8c16b5bf338c272cab6bbd7993a9d723934e"),
    ("g2/components/shared/cordio/", "Apache-2.0", "g2/third_party/cordio/LICENSE.md", "682ae5978019e4ee9d439b300efb125525b2e4cc4181ebd1e676dd60dc69d7cd"),
    ("g2/components/shared/easylogger/", "MIT", "g2/third_party/easylogger/LICENSE", "4a7be67e9701d0344c62d1b92eed8f40b874d00d64a9ee6b3853eb47ef4ea7f9"),
    ("g2/components/shared/nanopb/", "Zlib", "g2/third_party/nanopb/LICENSE.txt", "e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d"),
)
LOCAL_INCLUDE = re.compile(
    rb'^\s*#\s*include\s*[<"]([^">\r\n]+)[">]',
    re.MULTILINE,
)
LONG_HEX_BODY = re.compile(rb"(?<![0-9A-Fa-f])[0-9A-Fa-f]{256,}(?![0-9A-Fa-f])")
DENSE_BYTE_TRANSCRIPT = re.compile(rb"(?:0x[0-9A-Fa-f]{1,2}\s*,\s*){16,}")
ESCAPED_BYTE_TRANSCRIPT = re.compile(
    rb"(?:\\x[0-9A-Fa-f]{2}(?:[\"']?\s*[\"']?)?){16,}"
)
BASE64_BODY = re.compile(
    rb"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{172,}={0,2}(?![A-Za-z0-9+/])"
)
RAW_EXECUTABLE_DIRECTIVE = re.compile(rb"\.(?:byte|short|hword)\s+")
LITERAL_HEX_CONSTRUCTOR = re.compile(
    rb"(?:bytes\.fromhex|binascii\.unhexlify)\(\s*[rubfRUBF]*"
    rb"[\"'][0-9A-Fa-f\s]{8,}[\"']\s*\)"
)
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
    rb"use, reproduction, disclosure or distribution[\s\S]{0,240}"
    rb"without an express license agreement[\s\S]{0,120}strictly prohibited",
    re.IGNORECASE,
)
SANITIZED_APOLLO_OVERLAY = "g2/components/apollo_main/core_overlay/overlay.json"
SANITIZED_LIBLC3_OVERLAY = "g2/components/apollo_main/liblc3_ltpf/overlay.json"
SANITIZED_RING_OVERLAY = "g2/components/apollo_main/ring_gesture/overlay.json"
RELOCATED_PUBLIC_SOURCES = {
    "g2/research/candidates/freertos_scheduler_port_trio.c": (
        "g2/components/apollo_main/core_overlay/freertos_scheduler_port_trio.c"
    ),
    "g2/research/candidates/freertos_scheduler_port_trio.h": (
        "g2/components/apollo_main/core_overlay/freertos_scheduler_port_trio.h"
    ),
}


class CommunityBundleError(RuntimeError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


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
    if any(_forbidden_directory_part(part) for part in relative.parts[:-1]):
        return False
    if path.name in FORBIDDEN_FILENAMES or path.name.lower() in FORBIDDEN_SECRET_FILENAMES:
        return False
    if path.suffix.lower() in FORBIDDEN_SUFFIXES | FORBIDDEN_SECRET_SUFFIXES:
        return False
    return (
        path.suffix in SOURCE_SUFFIXES
        or path.name in {"Makefile", "make.sh", "LICENSE", "NOTICE"}
        or path.name.startswith("LICENSE")
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
    directories = [(ROOT / relative).resolve() for relative in _configured_include_dir_names()]
    missing = [path for path in directories if not path.is_dir()]
    if missing:
        raise CommunityBundleError(
            f"configured include directory is unavailable: {missing[0]}"
        )
    return directories


def _source_include_contexts() -> dict[Path, set[tuple[Path, ...]]]:
    """Map compiled source records to their exact ordered include paths."""
    contexts: dict[Path, set[tuple[Path, ...]]] = {}

    def include_context(toolchain: Any, profile: Any = None) -> tuple[Path, ...]:
        names = toolchain.get("include_dirs", []) if isinstance(toolchain, dict) else []
        if isinstance(profile, dict) and "include_dirs" in profile:
            names = profile["include_dirs"]
        if not isinstance(names, list) or any(not isinstance(name, str) for name in names):
            raise CommunityBundleError("source toolchain include_dirs is invalid")
        return tuple((ROOT / name).resolve() for name in names)

    def add(source: Any, owner: dict[str, Any]) -> None:
        if not isinstance(source, dict) or not isinstance(source.get("path"), str):
            return
        path = (ROOT / source["path"]).resolve()
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
        for context in (source_contexts.get(source.resolve()) or {()})
    ]
    visited: set[tuple[Path, tuple[Path, ...]]] = set()
    while pending:
        source, include_dirs = pending.pop()
        visit_key = (source.resolve(), include_dirs)
        if visit_key in visited:
            continue
        visited.add(visit_key)
        if source.suffix not in SOURCE_SUFFIXES:
            continue
        for raw_name in LOCAL_INCLUDE.findall(source.read_bytes()):
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
                candidate = unresolved.resolve()
                try:
                    candidate.relative_to(REPOSITORY_ROOT.resolve())
                except ValueError:
                    continue
                if not candidate.is_file():
                    continue
                if not _allowed_source_file(candidate):
                    raise CommunityBundleError(
                        f"quoted source dependency is forbidden: {candidate}"
                    )
                if candidate not in selected:
                    selected.add(candidate)
                pending.append((candidate, include_dirs))
                break
    return selected


def collect_files() -> list[Path]:
    files = {ROOT / relative for relative in EXPLICIT_FILES}
    files.update(REPOSITORY_ROOT / relative for relative in EXPLICIT_REPOSITORY_FILES)
    files.update(audit_g2_release_licensing.LICENSE_TEXTS.values())
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


def _official_provider_hashes() -> set[str]:
    manifest = open_cfw.load_manifest(BASE_MANIFEST)
    return {component["provider"]["sha256"] for component in manifest["components"]}


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


def _bundle_payload(path: Path, data: bytes | None = None) -> bytes:
    data = path.read_bytes() if data is None else data
    archive_path = path.relative_to(REPOSITORY_ROOT).as_posix()
    if archive_path == SANITIZED_APOLLO_OVERLAY:
        return _sanitize_apollo_overlay(data)
    if archive_path == SANITIZED_LIBLC3_OVERLAY:
        return _sanitize_liblc3_overlay(data)
    if archive_path == SANITIZED_RING_OVERLAY:
        return _sanitize_ring_overlay(data)
    return data


def _reject_raw_executable_transcript(archive_path: str, data: bytes) -> None:
    pure = PurePosixPath(archive_path)
    if (
        len(pure.parts) >= 3
        and pure.parts[:2] == ("g2", "components")
        and pure.suffix in {".c", ".h", ".S", ".s", ".asm"}
        and RAW_EXECUTABLE_DIRECTIVE.search(data)
    ):
        raise CommunityBundleError(
            f"raw executable transcript directive selected: {archive_path}"
        )
    if (
        len(pure.parts) >= 3
        and pure.parts[:2] == ("g2", "components")
        and pure.suffix == ".py"
        and archive_path not in REVIEWED_GENERATED_HEX_CONSTRUCTORS
    ):
        try:
            tree = ast.parse(data.decode("utf-8"), filename=archive_path)
        except (SyntaxError, UnicodeDecodeError) as error:
            raise CommunityBundleError(
                f"component Python source is invalid: {archive_path}"
            ) from error
        literal_decoders = {"fromhex", "unhexlify", "b64decode", "decodebytes"}
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, bytes)
                and len(node.value) >= 16
                and sum(32 <= byte < 127 for byte in node.value)
                < (len(node.value) * 3) // 4
            ):
                raise CommunityBundleError(
                    f"literal executable encoding constructor selected: {archive_path}"
                )
            if not isinstance(node, ast.Call) or not node.args:
                continue
            function = node.func
            name = (
                function.attr
                if isinstance(function, ast.Attribute)
                else function.id
                if isinstance(function, ast.Name)
                else ""
            )
            argument = node.args[0]
            if (
                name in literal_decoders
                and isinstance(argument, ast.Constant)
                and isinstance(argument.value, (str, bytes))
            ):
                raise CommunityBundleError(
                    f"literal executable encoding constructor selected: {archive_path}"
                )
            if (
                name in {"bytes", "bytearray"}
                and isinstance(argument, (ast.List, ast.Tuple))
                and len(argument.elts) >= 16
                and all(
                    isinstance(element, ast.Constant)
                    and isinstance(element.value, int)
                    and not isinstance(element.value, bool)
                    and 0 <= element.value <= 255
                    for element in argument.elts
                )
            ):
                raise CommunityBundleError(
                    f"literal executable encoding constructor selected: {archive_path}"
                )
        if LITERAL_HEX_CONSTRUCTOR.search(data):
            raise CommunityBundleError(
                f"literal executable encoding constructor selected: {archive_path}"
            )


def _allowed_archive_file(path: PurePosixPath) -> bool:
    return (
        SAFE_ARCHIVE_PATH.fullmatch(path.as_posix()) is not None
        and not any(_forbidden_directory_part(part) for part in path.parts[:-1])
        and path.name not in FORBIDDEN_FILENAMES
        and path.name.lower() not in FORBIDDEN_SECRET_FILENAMES
        and path.suffix.lower() not in FORBIDDEN_SUFFIXES | FORBIDDEN_SECRET_SUFFIXES
        and (
            path.suffix in SOURCE_SUFFIXES
            or path.name in {"Makefile", "make.sh", "LICENSE", "NOTICE"}
            or path.name.startswith("LICENSE")
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


def _verify_public_payload(archive_path: str, data: bytes) -> None:
    pure = PurePosixPath(archive_path)
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
    if (
        len(pure.parts) >= 3
        and pure.parts[0] == "g2"
        and pure.parts[1] in {"components", "third_party"}
        and pure.suffix in {".c", ".h", ".S", ".s", ".inc"}
        and RESTRICTED_SOURCE_NOTICE.search(data)
    ):
        raise CommunityBundleError(
            f"restricted vendor source notice selected: {archive_path}"
        )
    if LONG_HEX_BODY.search(data):
        raise CommunityBundleError(
            f"long embedded hexadecimal body forbidden: {archive_path}"
        )
    if (
        len(pure.parts) >= 3
        and pure.parts[0] == "g2"
        and pure.parts[1] in {"components", "third_party"}
        and pure.suffix in {".c", ".h", ".S", ".s", ".inc"}
        and (
            DENSE_BYTE_TRANSCRIPT.search(data)
            or ESCAPED_BYTE_TRANSCRIPT.search(data)
            or BASE64_BODY.search(data)
        )
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


def _verify_public_inventory(paths: set[str]) -> None:
    pt_sources = {
        f"g2/components/apollo_main/core_overlay/pt_protocol{suffix}.{extension}"
        for suffix in PT_PROTOCOL_SOURCE_SUFFIXES
        for extension in ("c", "h")
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
    required = (
        pt_sources
        | pt_tests
        | pt_fixtures
        | case_files
        | case_source_image_files
        | {
            *RELOCATED_PUBLIC_SOURCES.values(),
            "g2/tools/manifests/g2-pt-protocol-source-summary.json",
            "g2/components/apollo_main/pt_protocol/build_component.py",
            "g2/tools/manifests/g2-case-final-classification-summary.json",
            "g2/tests/test_runtime_nemavg_stroke_caps_candidate.py",
            "g2/tests/fixtures/runtime_nemavg_stroke_caps_host.c",
            "g2/tools/manifests/g2-clkmgr-divider-candidate-summary.json",
            "g2/tests/test_runtime_clkmgr_divider_candidate.py",
            "g2/tests/fixtures/runtime_clkmgr_divider_candidate_host.c",
            "g2/docs/community-source-distribution.md",
        }
    )
    missing = sorted(required - paths)
    if missing:
        raise CommunityBundleError(f"required community source is absent: {missing[0]}")
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
        "g2/tools/analyze_g2_case_source_image.py",
        "g2/tests/test_analyze_g2_case_source_image.py",
        "g2/tools/analyze_g2_touch_source_image.py",
        "g2/tests/test_analyze_g2_touch_source_image.py",
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
        resolved = path.resolve()
        data = raw_by_path[resolved]
        rows.append({
            "archive_path": destination,
            "source_path": path.relative_to(REPOSITORY_ROOT).as_posix(),
            "size": len(data),
            "sha256": _sha256(data),
        })
    return _sha256(
        (json.dumps(rows, sort_keys=True, separators=(",", ":")) + "\n").encode()
    )


def _require_regular_source(path: Path) -> None:
    try:
        relative = path.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise CommunityBundleError(f"community source escapes repository: {path}") from error
    cursor = REPOSITORY_ROOT
    for part in relative.parts:
        cursor = cursor / part
        metadata = cursor.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise CommunityBundleError(f"community source traverses a symlink: {path}")
    metadata = path.stat()
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise CommunityBundleError(
            f"community source is not an independent regular file: {path}"
        )
    try:
        path.resolve(strict=True).relative_to(REPOSITORY_ROOT.resolve(strict=True))
    except ValueError as error:
        raise CommunityBundleError(f"community source escapes repository: {path}") from error


def _capture_selected_records() -> tuple[
    list[tuple[Path, str]], dict[Path, bytes], str
]:
    records = _selected_records()
    raw_by_path: dict[Path, bytes] = {}
    for path, _destination in records:
        resolved = path.resolve()
        _require_regular_source(path)
        raw_by_path.setdefault(resolved, path.read_bytes())
    digest = _source_capture_digest(records, raw_by_path)
    _require_source_capture_unchanged(records, raw_by_path, digest)
    return records, raw_by_path, digest


def _require_source_capture_unchanged(
    records: list[tuple[Path, str]], raw_by_path: dict[Path, bytes], digest: str
) -> None:
    current_records = _selected_records()
    expected_identity = [
        (path.resolve(), destination) for path, destination in records
    ]
    current_identity = [
        (path.resolve(), destination) for path, destination in current_records
    ]
    if current_identity != expected_identity:
        raise CommunityBundleError("community source inventory changed during capture")
    observed: dict[Path, bytes] = {}
    for path, _destination in current_records:
        _require_regular_source(path)
        resolved = path.resolve()
        observed.setdefault(resolved, path.read_bytes())
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
) -> tuple[str, list[dict[str, str]]] | None:
    matches = [scope for scope in LICENSE_INHERITANCE_SCOPES if path.startswith(scope[0])]
    if len(matches) > 1:
        raise CommunityBundleError(f"overlapping upstream license scopes: {path}")
    if not matches:
        return None
    _prefix, license_id, evidence_path, expected_sha256 = matches[0]
    evidence_data = payload_by_path.get(evidence_path)
    if evidence_data is None or _sha256(evidence_data) != expected_sha256:
        raise CommunityBundleError(
            f"bundled upstream license evidence changed: {evidence_path}"
        )
    return license_id, [{"path": evidence_path, "sha256": expected_sha256}]


def _bundle_member_license_ledger(
    payload_by_path: dict[str, bytes]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ledger: list[dict[str, Any]] = []
    unresolved: list[str] = []
    explicit = 0
    inherited = 0
    for path in sorted(payload_by_path):
        if not _source_like_archive_path(path):
            continue
        try:
            text = payload_by_path[path].decode("utf-8")
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
            classification = "explicit-spdx"
            evidence = _license_evidence_rows(license_expression, payload_by_path)
            explicit += 1
        else:
            inherited_license = _inherited_license(path, payload_by_path)
            if inherited_license is None:
                unresolved.append(path)
                continue
            license_expression, evidence = inherited_license
            classification = "reviewed-upstream-scope"
            inherited += 1
        ledger.append({
            "path": path,
            "sha256": _sha256(payload_by_path[path]),
            "license": license_expression,
            "classification": classification,
            "evidence": evidence,
        })
    if unresolved:
        raise CommunityBundleError(
            f"bundled source license is unresolved ({len(unresolved)} files): "
            f"{unresolved[0]}"
        )
    closure = {
        "source_like_members": len(ledger),
        "explicit_spdx_members": explicit,
        "reviewed_upstream_scope_members": inherited,
        "unresolved_members": 0,
        "ledger_sha256": _sha256(
            (json.dumps(ledger, sort_keys=True, separators=(",", ":")) + "\n").encode()
        ),
    }
    return ledger, closure


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


def create_bundle(output: Path) -> dict[str, Any]:
    _require_completion_assessment_current()
    license_closure = _license_closure()
    official_hashes = _official_provider_hashes()
    rows = []
    payloads: list[tuple[str, bytes]] = []
    selected_records, raw_by_path, source_capture_sha256 = (
        _capture_selected_records()
    )
    for path, archive_path in selected_records:
        data = _bundle_payload(path, raw_by_path[path.resolve()])
        digest = _sha256(data)
        if digest in official_hashes or digest == OFFICIAL_PACKAGE_SHA256:
            raise CommunityBundleError(f"official firmware payload selected: {path}")
        _verify_public_payload(archive_path, data)
        if len(data) > MAX_ARCHIVE_MEMBER_SIZE:
            raise CommunityBundleError(f"community source exceeds member cap: {path}")
        rows.append({"path": archive_path, "size": len(data), "sha256": digest})
        payloads.append((archive_path, data))
    payload_by_path = dict(payloads)
    source_license_ledger, source_license_closure = (
        _bundle_member_license_ledger(payload_by_path)
    )
    payload_inventory_sha256 = _sha256(
        (json.dumps(rows, sort_keys=True, separators=(",", ":")) + "\n").encode()
    )
    manifest = {
        "schema_version": 4,
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
            "literal component encodings, dense byte transcripts, and raw "
            "executable directives rejected"
        ),
        "completion_assessment": {
            "included": False,
            "repository_gate": "completion-assessment-check",
        },
        "license_closure": license_closure,
        "source_member_license_closure": source_license_closure,
        "source_member_license_ledger": source_license_ledger,
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
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.is_symlink() or (output.exists() and not output.is_file()):
        raise CommunityBundleError("community archive output is not a regular file")
    prior_output = (
        (output.read_bytes(), stat.S_IMODE(output.stat().st_mode))
        if output.exists()
        else None
    )
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
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
        candidate = temporary.read_bytes()
        if len(candidate) > MAX_ARCHIVE_SIZE:
            raise CommunityBundleError("community archive byte-size cap exceeded")
        _verify_bundle_bytes(candidate)
        _require_source_capture_unchanged(
            selected_records, raw_by_path, source_capture_sha256
        )
        if _license_closure() != license_closure:
            raise CommunityBundleError("community license closure changed during capture")
        _require_completion_assessment_current()
        if temporary.read_bytes() != candidate:
            raise CommunityBundleError("community archive changed before publication")
        try:
            os.replace(temporary, output)
            if output.read_bytes() != candidate:
                raise CommunityBundleError(
                    "published community archive readback changed"
                )
            _fsync_directory(output.parent)
        except Exception:
            if prior_output is None:
                output.unlink(missing_ok=True)
            else:
                _atomic_write_unique(
                    output, prior_output[0], mode=prior_output[1]
                )
            raise
    finally:
        temporary.unlink(missing_ok=True)
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
        parents = pure.parents[:-1]
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
    official_hashes = _official_provider_hashes() | {OFFICIAL_PACKAGE_SHA256}
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
            or
            manifest.get("schema_version") != 4
            or manifest.get("format") != "openCFW-g2-community-source-bundle"
            or manifest.get("archive_encoding") != "zip-stored-fixed-metadata"
            or manifest.get("contains_official_firmware_payloads") is not False
            or manifest.get("contains_stock_firmware_guard_bytes") is not False
            or manifest.get("stock_guard_representation")
            != "size-and-sha256-authenticated-local-base"
            or manifest.get("stock_guard_scope") != (
                "known overlay patch guards and component-builder donor ingress; "
                "literal component encodings, dense byte transcripts, and raw "
                "executable directives rejected"
            )
            or manifest.get("completion_assessment") != {
                "included": False,
                "repository_gate": "completion-assessment-check",
            }
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
            _verify_public_payload(name, data)
            digest = _sha256(data)
            row = expected[name]
            if len(data) != row["size"] or digest != row["sha256"]:
                raise CommunityBundleError(f"bundle member identity changed: {name}")
            if digest in official_hashes:
                raise CommunityBundleError(f"official firmware payload embedded: {name}")
        _verify_bundle_member_license_ledger(
            payload_by_path,
            manifest.get("source_member_license_ledger"),
            manifest.get("source_member_license_closure"),
        )
        try:
            overlay = json.loads(archive.read(SANITIZED_APOLLO_OVERLAY))
        except (KeyError, json.JSONDecodeError, UnicodeDecodeError) as error:
            raise CommunityBundleError("sanitized Apollo overlay is unavailable") from error
        _verify_sanitized_apollo_overlay(overlay)
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
    return _verify_bundle_bytes(bundle.read_bytes())


def authenticate_official_package(path: Path) -> dict[str, bytes]:
    image = path.read_bytes()
    if len(image) != OFFICIAL_PACKAGE_SIZE or _sha256(image) != OFFICIAL_PACKAGE_SHA256:
        raise CommunityBundleError("local official G2 package identity is not authenticated")
    manifest = open_cfw.load_manifest(BASE_MANIFEST)
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


def _atomic_write_unique(path: Path, data: bytes, *, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        if temporary.read_bytes() != data:
            raise CommunityBundleError(f"atomic write readback changed: {path}")
        os.replace(temporary, path)
        if path.read_bytes() != data:
            raise CommunityBundleError(f"published atomic write changed: {path}")
        _fsync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


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
    try:
        target.resolve(strict=False).relative_to(workspace.resolve(strict=True))
    except ValueError as error:
        raise CommunityBundleError(
            f"local workspace path escapes workspace: {relative}"
        ) from error
    return target


def prepare_local_workspace(official_package: Path, workspace: Path) -> dict[str, Any]:
    payloads = authenticate_official_package(official_package)
    if workspace.is_symlink() or not workspace.is_dir():
        raise CommunityBundleError("workspace is not an independent directory")
    manifest_path = _safe_workspace_target(workspace, "manifests/g2-2.2.6.10.json")
    if not manifest_path.is_file():
        raise CommunityBundleError("workspace is not an extracted community source bundle")
    receipt_path = _safe_workspace_target(workspace, HYDRATION_RECEIPT)
    receipt_path.unlink(missing_ok=True)
    include_directories = _configured_include_dir_names(workspace)
    for relative in include_directories:
        target = _safe_workspace_target(workspace, relative, require_directory=True)
        target.mkdir(parents=True, exist_ok=True)
    targets: dict[str, Path] = {
        relative: _safe_workspace_target(workspace, relative)
        for relative in payloads
    }
    originals = {
        relative: (
            (target.read_bytes(), stat.S_IMODE(target.stat().st_mode))
            if target.exists()
            else None
        )
        for relative, target in targets.items()
    }
    try:
        for relative, payload in payloads.items():
            _atomic_write_unique(targets[relative], payload)
        provider_rows = []
        for relative, payload in sorted(payloads.items()):
            observed = targets[relative].read_bytes()
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
            "hardware_operations": False,
        }
        receipt_data = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
        _atomic_write_unique(receipt_path, receipt_data)
    except Exception:
        receipt_path.unlink(missing_ok=True)
        rollback_errors: list[str] = []
        for relative, target in reversed(list(targets.items())):
            original = originals[relative]
            try:
                if original is None:
                    target.unlink(missing_ok=True)
                else:
                    _atomic_write_unique(target, original[0], mode=original[1])
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


def smoke_build(bundle: Path, official_package: Path) -> dict[str, Any]:
    """Exercise the recipient hydration and source-build workflow in isolation."""
    bundle_data = bundle.read_bytes()
    _verify_bundle_bytes(bundle_data)
    with tempfile.TemporaryDirectory(prefix="opencfw-community-smoke-") as temporary:
        extraction_root = Path(temporary)
        with zipfile.ZipFile(io.BytesIO(bundle_data)) as archive:
            for info in archive.infolist():
                target = extraction_root / PurePosixPath(info.filename)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(info))
                os.chmod(
                    target,
                    0o755
                    if info.filename in EXECUTABLE_ARCHIVE_PATHS
                    else 0o644,
                )
        workspace = extraction_root / "g2"
        prepare_local_workspace(official_package, workspace)
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        commands = (
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.test_analyze_g2_case_source_image",
                "tests.test_runtime_nemavg_stroke_caps_candidate",
                "tests.test_runtime_clkmgr_divider_candidate",
            ],
            [sys.executable, "components/bootloader/core_overlay/build_component.py"],
            [sys.executable, "components/apollo_main/core_overlay/build_component.py"],
            [
                sys.executable,
                "tools/open_cfw.py",
                "build",
                "--manifest",
                "manifests/g2-2.2.6.10-core-source.json",
                "--output-dir",
                "build/source",
                "--toolchain-profile",
                "apple-clang",
            ],
            [
                sys.executable,
                "tools/open_cfw.py",
                "verify",
                "--manifest",
                "manifests/g2-2.2.6.10-core-source.json",
            ],
            [
                sys.executable,
                "tools/open_cfw.py",
                "verify-artifacts",
                "--manifest",
                "manifests/g2-2.2.6.10-core-source.json",
                "--output-dir",
                "build/source",
                "--toolchain-profile",
                "apple-clang",
            ],
        )
        for command in commands:
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
        flash_plan = json.loads(
            (workspace / "build/source/flash-plan.json").read_text(encoding="utf-8")
        )
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
            "package_size": package.stat().st_size,
            "package_sha256": _sha256(package.read_bytes()),
            "bundle_sha256": _sha256(bundle_data),
            "flash_plan_counts": counts,
            "hardware_operations": False,
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
    smoke = subparsers.add_parser("smoke-build")
    smoke.add_argument("bundle", type=Path)
    smoke.add_argument("official_package", type=Path)
    args = parser.parse_args(argv)
    if args.command == "create":
        print(json.dumps(create_bundle(args.output), sort_keys=True))
    elif args.command == "verify":
        manifest = verify_bundle(args.bundle)
        print(f"Verified community bundle: {len(manifest['files'])} source files")
    elif args.command == "prepare-local":
        print(json.dumps(prepare_local_workspace(args.official_package, args.workspace), sort_keys=True))
    else:
        print(json.dumps(smoke_build(args.bundle, args.official_package), sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CommunityBundleError, open_cfw.OpenCFWError, OSError, zipfile.BadZipFile) as error:
        print(f"community distribution: error: {error}")
        raise SystemExit(1)
