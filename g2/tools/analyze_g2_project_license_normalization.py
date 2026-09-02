#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Audit project-owned GPL labels against the MIT-where-possible policy."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import stat
from collections import Counter
from pathlib import Path

import audit_g2_release_licensing as licensing

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parent
CENSUS = ROOT / "tools/manifests/g2-project-license-normalization.tsv"
SCOPE_PATHS = (
    ROOT / "tools/manifests/g2-project-mit-normalization-scope-paths.txt"
)
ADDITIONAL_PATHS = (
    ROOT /
    "tools/manifests/g2-project-mit-normalization-research-and-wrapper.txt"
)
COMMUNITY_CONTROLLER_PATHS = (
    ROOT /
    "tools/manifests/g2-project-mit-normalization-community-controllers.txt"
)
TOUCH_SOURCE_IMAGE_PATHS = (
    ROOT /
    "tools/manifests/g2-project-mit-normalization-touch-source-image.txt"
)
CASE_SOURCE_IMAGE_PATHS = (
    ROOT /
    "tools/manifests/g2-project-mit-normalization-case-source-image.txt"
)
EM9305_SOURCE_IMAGE_PATHS = (
    ROOT /
    "tools/manifests/g2-project-mit-normalization-em9305-source-image.txt"
)
SUMMARY = ROOT / "tools/manifests/g2-project-license-normalization-summary.json"
EXPECTED_PATH_LICENSE_DIGEST = (
    "90c068286c602b912396a98ae464b87e245e2fd81525d357f0d2b07cf0a2f31c"
)
SPDX = re.compile(r"SPDX-License-Identifier:\s*([^\s*]+)")
GPL_SPDX = re.compile(
    r"SPDX-License-Identifier:\s*(GPL-3\.0-(?:only|or-later))")
DUAL_MIT_GPL = re.compile(
    r"SPDX-License-Identifier:\s*\(?MIT\s+OR\s+GPL-3\.0-(?:only|or-later)\)?")
PRESERVED_UPSTREAM_GPL_PATHS = {
    "components/apollo_main/ring_gesture/ring_gesture.c",
}
LZ4_WRAPPER = (
    "components/apollo_main/core_overlay/evenhub_lz4_upstream_adapter.c"
)
EXPECTED_SCOPE_PATH_COUNT = 749
EXPECTED_ADDITIONAL_PATH_COUNT = 22
EXPECTED_COMMUNITY_CONTROLLER_PROJECT_PATH_COUNT = 109
EXPECTED_TOUCH_SOURCE_IMAGE_PROJECT_PATH_COUNT = 9
EXPECTED_CASE_SOURCE_IMAGE_PROJECT_PATH_COUNT = 7
EXPECTED_EM9305_SOURCE_IMAGE_PROJECT_PATH_COUNT = 19
EXPECTED_PT_PROTOCOL_PROJECT_PATH_COUNT = 28
EXPECTED_PT_PROTOCOL_TOTAL_PATH_COUNT = 29
EXPECTED_DISTRIBUTED_TARGET_COUNT = 919
COMMUNITY_CONTROLLER_ROOTS = (
    ROOT / "components/shared/touch",
    ROOT / "components/shared/case",
    ROOT / "components/shared/gx8002",
    ROOT / "components/shared/em9305",
)
COMMUNITY_BUILD_ADAPTERS = {
    "g2/components/apollo_main/core_overlay/build_component.py",
    "g2/components/apollo_main/liblc3_ltpf/build_component.py",
    "g2/components/apollo_main/pt_protocol/build_component.py",
}
CANONICAL_ADMISSION_PATHS = {
    "g2/tools/apply_g2_canonical_observations.py",
    "g2/tests/test_apply_g2_canonical_observations.py",
}
COMMUNITY_TOUCH_APACHE_PATHS = {
    "g2/components/shared/touch/runtime_touch_cat2_adapters.c",
    "g2/components/shared/touch/runtime_touch_cat2_adapters.h",
    "g2/components/shared/touch/runtime_touch_critical_adapters.S",
}
TOUCH_SOURCE_IMAGE_PACKAGE_ROOT = ROOT / "components/touch/source_image"
TOUCH_SOURCE_IMAGE_SUPPORT_PATHS = {
    "g2/tools/analyze_g2_touch_source_image.py",
    "g2/tests/test_touch_source_image.py",
    "g2/tests/test_analyze_g2_touch_source_image.py",
}
CASE_SOURCE_IMAGE_PACKAGE_ROOT = ROOT / "components/case/source_image"
CASE_SOURCE_IMAGE_SUPPORT_PATHS = {
    "g2/tools/analyze_g2_case_source_image.py",
    "g2/tests/test_analyze_g2_case_source_image.py",
}
EM9305_SOURCE_IMAGE_PACKAGE_ROOTS = (
    ROOT / "components/em9305/source_image",
    ROOT / "components/em9305/source_overlay",
)
EM9305_SOURCE_IMAGE_SUPPORT_PATHS = {
    "g2/tools/analyze_em9305_record_package.py",
    "g2/tests/test_em9305_record_package.py",
    "g2/tests/test_analyze_em9305_record_package.py",
    "g2/tests/test_em9305_reconstructible_tail_overlay.py",
    "g2/tests/test_runtime_em9305_metaware_production.py",
    "g2/tests/test_runtime_em9305_reconstructible_tail.py",
    "g2/tests/fixtures/em9305_reconstructible_tail_host.c",
    "g2/tools/integrate_g2_em9305_source_overlay.py",
}
PT_PROTOCOL_SOURCE_ROOT = ROOT / "components/apollo_main/core_overlay"
PT_PROTOCOL_APACHE_PATHS = {
    "g2/components/apollo_main/core_overlay/pt_protocol_lc3_setup.c",
}
REPOSITORY_ONLY_PROJECT_PATHS = {
    "g2/components/apollo_main/core_overlay/imu_icm45608.c",
}
ROOT_POLICY_PROJECT_FILES = {
    "CODE_OF_CONDUCT.md": (
        1_345,
        "014aa1ea90839f9a3cbe565d514675ad7f286a2a68dea58823312bc2c7fb0e95",
    ),
    "CONTRIBUTING.md": (
        2_070,
        "7da57f48953f803bcbe3ce955538ebb5547dab99559fd15913e8b251ae1fe7a2",
    ),
    "SECURITY.md": (
        1_462,
        "3cd941f97fd3c94ab4154b2e77687ab646642e9812333c791ee1c6b0a83025a1",
    ),
    "SUPPORT.md": (
        1_046,
        "eeff649de7c261d264eecbd3fd0317830f571b7a7008437d15bc09f58790b145",
    ),
}
EXPECTED_ROOT_POLICY_MEMBERS = frozenset(ROOT_POLICY_PROJECT_FILES)
EXPECTED_ROOT_POLICY_CENSUS_DIGEST = (
    "3b907b120819ed924d98487c658a02ea9300423ab2348700fe08b05b061f99a8"
)
ROOT_MIT_LICENSE_IDENTITY = (
    1_077,
    "3a0f162b73b7d95cdb1de2395b4f0f4ad35eae3c8eb44f125d5c0db6bc811ea4",
)


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_regular_once(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise AuditError(f"cannot safely read project policy file: {path}") from error
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                f"project policy path is not a single-link regular file: {path}")
        chunks = []
        while True:
            chunk = os.read(descriptor, 64 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        after = os.fstat(descriptor)
        require(
            (before.st_dev, before.st_ino, before.st_size,
             before.st_mtime_ns, before.st_ctime_ns) ==
            (after.st_dev, after.st_ino, after.st_size,
             after.st_mtime_ns, after.st_ctime_ns),
            f"project policy file changed while being read: {path}",
        )
        data = b"".join(chunks)
        require(len(data) == before.st_size,
                f"project policy file read was incomplete: {path}")
        return data
    finally:
        os.close(descriptor)


def _root_policy_project_rows() -> list[dict[str, object]]:
    require(frozenset(ROOT_POLICY_PROJECT_FILES) == EXPECTED_ROOT_POLICY_MEMBERS,
            "root community-policy member census changed")
    require(all(Path(path).parts == (path,)
                for path in ROOT_POLICY_PROJECT_FILES),
            "root community-policy census contains a non-root filename")

    license_data = _read_regular_once(REPOSITORY_ROOT / "LICENSE")
    require((len(license_data), sha256(license_data)) == ROOT_MIT_LICENSE_IDENTITY,
            "root MIT license identity changed")

    rows = []
    digest_lines = []
    for repo_relative in sorted(ROOT_POLICY_PROJECT_FILES):
        expected_size, expected_sha256 = ROOT_POLICY_PROJECT_FILES[repo_relative]
        data = _read_regular_once(REPOSITORY_ROOT / repo_relative)
        actual = (len(data), sha256(data))
        require(actual == (expected_size, expected_sha256),
                f"root community-policy identity changed: {repo_relative}")
        digest_lines.append(
            f"{repo_relative}\t{expected_size}\t{expected_sha256}\tMIT\n")
        rows.append({
            "path": repo_relative,
            "size": expected_size,
            "sha256": expected_sha256,
            "license": "MIT",
            "basis": "authenticated-root-mit-ownership-scope",
            "license_evidence": {
                "path": "LICENSE",
                "size": ROOT_MIT_LICENSE_IDENTITY[0],
                "sha256": ROOT_MIT_LICENSE_IDENTITY[1],
            },
        })
    require(sha256("".join(digest_lines).encode()) ==
            EXPECTED_ROOT_POLICY_CENSUS_DIGEST,
            "root community-policy census digest changed")
    return rows


def _census() -> list[dict[str, str]]:
    require(CENSUS.is_file(), "project license normalization census missing")
    with CENSUS.open(newline="") as handle:
        rows = list(csv.DictReader(
            (line for line in handle if not line.startswith("#")),
            delimiter="\t",
        ))
    payload = "".join(
        f"{row['path']}\t{row['overlay_license']}\n" for row in rows).encode()
    require(len(rows) == 459 and sha256(payload) == EXPECTED_PATH_LICENSE_DIGEST,
            "project-owned GPL baseline census changed")
    return rows


def _path_manifest(path: Path) -> set[str]:
    require(path.is_file(), f"project MIT path manifest missing: {path.name}")
    paths = {
        line.strip() for line in path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    require(all(item.startswith("g2/") for item in paths),
            f"non-g2 path in {path.name}")
    return paths


def analyze() -> dict:
    audit = licensing.analyze()
    inventory = audit["source_inventory"]
    inventory_by_path = {row["path"]: row for row in inventory}
    census = _census()
    root_policy_rows = _root_policy_project_rows()
    root_policy_by_path = {row["path"]: row for row in root_policy_rows}

    scope_paths = _path_manifest(SCOPE_PATHS)
    additional_paths = _path_manifest(ADDITIONAL_PATHS)
    community_project_paths = _path_manifest(COMMUNITY_CONTROLLER_PATHS)
    touch_source_image_paths = _path_manifest(TOUCH_SOURCE_IMAGE_PATHS)
    case_source_image_paths = _path_manifest(CASE_SOURCE_IMAGE_PATHS)
    em9305_source_image_paths = _path_manifest(EM9305_SOURCE_IMAGE_PATHS)
    require(len(scope_paths) == EXPECTED_SCOPE_PATH_COUNT,
            "requested-scope MIT target census changed")
    require(len(additional_paths) == EXPECTED_ADDITIONAL_PATH_COUNT,
            "research/wrapper MIT target census changed")
    require(REPOSITORY_ONLY_PROJECT_PATHS <= additional_paths,
            "repository-only project source left the MIT policy census")
    require(REPOSITORY_ONLY_PROJECT_PATHS.isdisjoint(scope_paths),
            "repository-only project source re-entered the public scope census")
    require(len(community_project_paths) ==
            EXPECTED_COMMUNITY_CONTROLLER_PROJECT_PATH_COUNT,
            "community controller MIT target census changed")
    require(len(touch_source_image_paths) ==
            EXPECTED_TOUCH_SOURCE_IMAGE_PROJECT_PATH_COUNT,
            "Touch source-image MIT target census changed")
    require(len(case_source_image_paths) ==
            EXPECTED_CASE_SOURCE_IMAGE_PROJECT_PATH_COUNT,
            "Case source-image MIT target census changed")
    require(len(em9305_source_image_paths) ==
            EXPECTED_EM9305_SOURCE_IMAGE_PROJECT_PATH_COUNT,
            "EM9305 source-image MIT target census changed")
    actual_community_paths = set(COMMUNITY_BUILD_ADAPTERS)
    for controller_root in COMMUNITY_CONTROLLER_ROOTS:
        require(controller_root.is_dir(),
                f"community controller source root missing: {controller_root}")
        actual_community_paths.update(
            "g2/" + path.relative_to(ROOT).as_posix()
            for path in controller_root.rglob("*")
            if path.is_file() and path.suffix in {".c", ".h", ".S", ".s", ".py"}
        )
    require(actual_community_paths ==
            community_project_paths | COMMUNITY_TOUCH_APACHE_PATHS,
            "community controller/build-adapter source census changed")
    for repo_relative in sorted(COMMUNITY_TOUCH_APACHE_PATHS):
        source = REPOSITORY_ROOT / repo_relative
        require(source.is_file(),
                f"Touch Apache adaptation missing: {repo_relative}")
        require("SPDX-License-Identifier: Apache-2.0" in
                source.read_text(errors="replace"),
                f"Touch Apache adaptation license changed: {repo_relative}")
    require(TOUCH_SOURCE_IMAGE_PACKAGE_ROOT.is_dir(),
            "Touch source-image package root missing")
    actual_touch_source_image_paths = {
        "g2/" + path.relative_to(ROOT).as_posix()
        for path in TOUCH_SOURCE_IMAGE_PACKAGE_ROOT.rglob("*")
        if path.is_file()
    } | TOUCH_SOURCE_IMAGE_SUPPORT_PATHS
    require(actual_touch_source_image_paths == touch_source_image_paths,
            "Touch source-image distributed source census changed")
    require(CASE_SOURCE_IMAGE_PACKAGE_ROOT.is_dir(),
            "Case source-image package root missing")
    actual_case_source_image_paths = {
        "g2/" + path.relative_to(ROOT).as_posix()
        for path in CASE_SOURCE_IMAGE_PACKAGE_ROOT.rglob("*")
        if path.is_file()
    } | CASE_SOURCE_IMAGE_SUPPORT_PATHS
    require(actual_case_source_image_paths == case_source_image_paths,
            "Case source-image distributed source census changed")
    require(all(path.is_dir() for path in EM9305_SOURCE_IMAGE_PACKAGE_ROOTS),
            "EM9305 source-image or source-overlay package root missing")
    actual_em9305_source_image_paths = {
        "g2/" + path.relative_to(ROOT).as_posix()
        for package_root in EM9305_SOURCE_IMAGE_PACKAGE_ROOTS
        for path in package_root.rglob("*")
        if (
            path.is_file()
            and "build" not in path.relative_to(package_root).parts
            and "__pycache__" not in path.relative_to(package_root).parts
            and path.suffix != ".pyc"
        )
    } | EM9305_SOURCE_IMAGE_SUPPORT_PATHS
    require(actual_em9305_source_image_paths == em9305_source_image_paths,
            "EM9305 source-image distributed source census changed")
    require(all((REPOSITORY_ROOT / path).is_file()
                for path in CANONICAL_ADMISSION_PATHS),
            "canonical observation admission source is missing")
    target_paths = (scope_paths | additional_paths | community_project_paths |
                    touch_source_image_paths | case_source_image_paths |
                    em9305_source_image_paths |
                    CANONICAL_ADMISSION_PATHS |
                    set(root_policy_by_path))
    require(len(target_paths) == EXPECTED_DISTRIBUTED_TARGET_COUNT,
            "repo-wide project MIT target census changed")
    require("g2/" + LZ4_WRAPPER in target_paths,
            "project-authored LZ4 wrapper missing from MIT targets")
    require("g2/" + next(iter(PRESERVED_UPSTREAM_GPL_PATHS)) not in
            target_paths, "authenticated g2flash GPL source entered targets")
    pt_protocol_paths = {
        "g2/" + path.relative_to(ROOT).as_posix()
        for path in PT_PROTOCOL_SOURCE_ROOT.glob("pt_protocol*")
        if path.is_file() and path.suffix in {".c", ".h"}
    }
    require(len(pt_protocol_paths) == EXPECTED_PT_PROTOCOL_TOTAL_PATH_COUNT,
            "PT protocol public source census changed")
    require(PT_PROTOCOL_APACHE_PATHS <= pt_protocol_paths,
            "PT protocol Apache adaptation is missing")
    pt_protocol_project_paths = pt_protocol_paths - PT_PROTOCOL_APACHE_PATHS
    require(len(pt_protocol_project_paths) ==
            EXPECTED_PT_PROTOCOL_PROJECT_PATH_COUNT,
            "PT protocol MIT source census changed")
    require(pt_protocol_project_paths <= target_paths,
            "PT protocol project source left the MIT target census")
    require(PT_PROTOCOL_APACHE_PATHS.isdisjoint(target_paths),
            "PT protocol Apache adaptation entered the MIT target census")
    for repo_relative in sorted(PT_PROTOCOL_APACHE_PATHS):
        source = REPOSITORY_ROOT / repo_relative
        text = source.read_text(errors="replace")
        record = inventory_by_path.get(repo_relative.removeprefix("g2/"))
        require(
            text.count("SPDX-License-Identifier: Apache-2.0") == 1
            and "Copyright 2022 Google LLC" in text
            and "third_party/liblc3/src/lc3.c" in text
            and "third_party/liblc3/LICENSE" in text,
            f"PT protocol Apache provenance changed: {repo_relative}",
        )
        require(
            record is not None
            and record["license"] == "Apache-2.0"
            and record["classification"] == "upstream-licensed"
            and record.get("upstream") == "Google/liblc3"
            and record.get("upstream_commit") ==
                "96a3af0beb5487aca3b98a4b992a539a1f6d80d1",
            f"PT protocol Apache inventory changed: {repo_relative}",
        )

    rows = []
    for baseline in census:
        repo_relative = "g2/" + baseline["path"]
        record = inventory_by_path.get(baseline["path"])
        repository_only = repo_relative in REPOSITORY_ONLY_PROJECT_PATHS
        if repository_only:
            require(record is None,
                    f"repository-only source re-entered overlay inventory: "
                    f"{baseline['path']}")
        else:
            require(record is not None,
                    f"project source left the overlay inventory: "
                    f"{baseline['path']}")
            require(record["classification"] == "project-owned-or-adapted"
                    and not record.get("upstream"),
                    f"project source provenance changed: {baseline['path']}")
        source = ROOT / baseline["path"]
        require(source.is_file(), f"project source missing: {baseline['path']}")
        text = source.read_text(errors="replace")
        match = SPDX.search(text)
        source_spdx = match.group(1) if match else "missing"
        normalized = source_spdx == "MIT" and (
            repository_only or record["license"] == "MIT"
        )
        rows.append({
            "path": baseline["path"],
            "components": (
                "repository-only-research" if repository_only
                else ",".join(record["components"])
            ),
            "overlay_license": (
                "not-compiled-stock-donor-boundary" if repository_only
                else record["license"]
            ),
            "source_spdx": source_spdx,
            "upstream_record": "absent",
            "desired_license": "MIT",
            "disposition": ("normalized" if normalized else
                            "normalize_project_owned_source_and_overlay_pin"),
            "source_sha256": sha256(source.read_bytes()),
        })

    pending = [row for row in rows if row["disposition"] != "normalized"]

    wrapper_record = inventory_by_path.get(LZ4_WRAPPER)
    require(wrapper_record is not None,
            "project-authored LZ4 wrapper left overlay inventory")
    wrapper_source = ROOT / LZ4_WRAPPER
    wrapper_text = wrapper_source.read_text(errors="replace")
    wrapper_match = SPDX.search(wrapper_text)
    wrapper_spdx = wrapper_match.group(1) if wrapper_match else "missing"
    wrapper_normalized = (
        wrapper_record["license"] == "MIT" and wrapper_spdx == "MIT"
        and not wrapper_record.get("upstream")
    )
    wrapper_row = {
        "path": LZ4_WRAPPER,
        "components": ",".join(wrapper_record["components"]),
        "overlay_license": wrapper_record["license"],
        "source_spdx": wrapper_spdx,
        "upstream_record": ("absent" if not wrapper_record.get("upstream")
                            else "remove_wrapper_only_upstream_pointer"),
        "desired_license": "MIT",
        "disposition": ("normalized" if wrapper_normalized else
                        "normalize_project_wrapper_and_overlay_pin"),
        "source_sha256": sha256(wrapper_source.read_bytes()),
    }
    overlay_rows = rows + [wrapper_row]
    overlay_pending = [row for row in overlay_rows
                       if row["disposition"] != "normalized"]

    distributed_rows = []
    dual_mit_gpl = set()
    for repo_relative in sorted(target_paths):
        source = REPOSITORY_ROOT / repo_relative
        require(source.is_file(), f"project MIT target missing: {repo_relative}")
        data = (_read_regular_once(source) if repo_relative in root_policy_by_path
                else source.read_bytes())
        if repo_relative in root_policy_by_path:
            expected = root_policy_by_path[repo_relative]
            require((len(data), sha256(data)) ==
                    (expected["size"], expected["sha256"]),
                    f"root community-policy identity changed: {repo_relative}")
        text = data.decode(errors="replace")
        inline_mit_asserted = bool(re.search(
            r"SPDX-License-Identifier(?:\"|')?\s*:\s*"
            r"(?:\"|')?\(?MIT(?:\s|\)|\"|'|$)", text))
        mit_asserted = inline_mit_asserted or repo_relative in root_policy_by_path
        gpl_asserted = bool(GPL_SPDX.search(text))
        if DUAL_MIT_GPL.search(text):
            dual_mit_gpl.add(repo_relative.removeprefix("g2/"))
        distributed_rows.append({
            "path": repo_relative,
            "mit_asserted": mit_asserted,
            "mit_basis": (
                "inline-spdx" if inline_mit_asserted
                else "authenticated-root-mit-ownership-scope"
            ),
            "gpl_asserted": gpl_asserted,
            "disposition": ("normalized" if mit_asserted and not gpl_asserted
                            else "normalize_project_authored_license_to_mit"),
            "sha256": sha256(data),
        })
    distributed_pending_rows = [
        row for row in distributed_rows if row["disposition"] != "normalized"
    ]
    overlay_missing_spdx = {
        row["path"] for row in overlay_pending
        if row["source_spdx"] == "missing"
    }
    distributed_pending = {row["path"] for row in distributed_pending_rows}

    preserved_gpl = [inventory_by_path[path]
                     for path in sorted(PRESERVED_UPSTREAM_GPL_PATHS)]
    require(all(record["license"] in
                {"GPL-3.0-only", "GPL-3.0-or-later"}
                and record.get("upstream") for record in preserved_gpl),
            "authenticated g2flash GPL provenance changed")
    require(len(preserved_gpl) == 1,
            "upstream GPL preservation census changed")
    licenses = Counter(record["license"] for record in inventory)
    metrics = {
        "project_owned_normalization_targets": len(overlay_rows),
        "project_owned_records_normalized_mit": (
            len(overlay_rows) - len(overlay_pending)),
        "project_owned_gpl_records_pending_mit": len(overlay_pending),
        "project_owned_gpl_only_pending": sum(
            row["overlay_license"] == "GPL-3.0-only"
            for row in overlay_pending),
        "project_owned_gpl_or_later_pending": sum(
            row["overlay_license"] == "GPL-3.0-or-later"
            for row in overlay_pending),
        "source_spdx_missing_pending": sum(
            row["source_spdx"] == "missing" for row in overlay_pending),
        "upstream_gpl_records_preserved": len(preserved_gpl),
        "apache_records_preserved": licenses["Apache-2.0"],
        "bsd_records_preserved": (
            licenses["BSD-3-Clause"] + licenses["BSD-2-Clause"]),
        "isc_records_preserved": licenses["ISC"],
        "zlib_records_preserved": licenses["Zlib"],
        "existing_mit_records": licenses["MIT"],
        "expected_mit_records_after_normalization": (
            licenses["MIT"] + len(overlay_pending)),
        "distributed_project_mit_normalization_targets": len(target_paths),
        "distributed_project_files_normalized_mit": (
            len(target_paths) - len(distributed_pending_rows)),
        "distributed_gpl_spdx_files": (
            sum(row["gpl_asserted"] for row in distributed_rows) +
            len(PRESERVED_UPSTREAM_GPL_PATHS)),
        "distributed_upstream_gpl_files_preserved": len(
            PRESERVED_UPSTREAM_GPL_PATHS),
        "distributed_project_gpl_spdx_files_pending_mit": sum(
            row["gpl_asserted"] for row in distributed_pending_rows),
        "distributed_overlay_sources_missing_spdx_pending": len(
            overlay_missing_spdx),
        "distributed_unique_project_files_pending_normalization": len(
            distributed_pending),
        "dual_mit_or_gpl_files_already_permit_mit": len(dual_mit_gpl),
        "community_controller_and_adapter_source_files": len(
            actual_community_paths),
        "community_project_mit_compatible_source_files": len(
            community_project_paths),
        "community_touch_apache_source_files_preserved": len(
            COMMUNITY_TOUCH_APACHE_PATHS),
        "touch_source_image_project_mit_files": len(
            touch_source_image_paths),
        "touch_source_image_package_files": len(
            actual_touch_source_image_paths - TOUCH_SOURCE_IMAGE_SUPPORT_PATHS),
        "touch_source_image_support_files": len(
            TOUCH_SOURCE_IMAGE_SUPPORT_PATHS),
        "case_source_image_project_mit_files": len(
            case_source_image_paths),
        "case_source_image_package_files": len(
            actual_case_source_image_paths - CASE_SOURCE_IMAGE_SUPPORT_PATHS),
        "case_source_image_support_files": len(
            CASE_SOURCE_IMAGE_SUPPORT_PATHS),
        "em9305_source_image_project_mit_files": len(
            em9305_source_image_paths),
        "em9305_source_image_package_files": len(
            actual_em9305_source_image_paths - EM9305_SOURCE_IMAGE_SUPPORT_PATHS),
        "em9305_source_image_support_files": len(
            EM9305_SOURCE_IMAGE_SUPPORT_PATHS),
        "pt_protocol_project_mit_files": len(pt_protocol_project_paths),
        "pt_protocol_upstream_apache_files_preserved": len(
            PT_PROTOCOL_APACHE_PATHS),
        "repository_only_project_mit_files": len(
            REPOSITORY_ONLY_PROJECT_PATHS),
        "root_policy_project_mit_files": len(root_policy_rows),
        "root_policy_project_mit_census_sha256": (
            EXPECTED_ROOT_POLICY_CENSUS_DIGEST),
    }
    require(metrics["project_owned_normalization_targets"] == 460,
            "license normalization target count changed")
    require(metrics["project_owned_records_normalized_mit"] +
            metrics["project_owned_gpl_records_pending_mit"] == 460,
            "license normalization target accounting changed")
    require(metrics["upstream_gpl_records_preserved"] >= 1,
            "authenticated upstream GPL preservation changed")
    return {
        "schema_version": 1,
        "policy": "MIT for project-owned/no-upstream source; preserve authenticated upstream licenses",
        "normalization_complete": not overlay_pending and not distributed_pending,
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_blocker": "blocked by unavailable physical evidence",
        "production_files_modified": [],
        "metrics": metrics,
        "preserved_upstream_gpl": [
            {key: record[key] for key in
             ("path", "license", "upstream", "upstream_commit")}
            for record in preserved_gpl
        ],
        "rows": overlay_rows,
        "pending_rows": overlay_pending,
        "distributed_rows": distributed_rows,
        "community_project_paths": sorted(community_project_paths),
        "community_touch_apache_paths": sorted(COMMUNITY_TOUCH_APACHE_PATHS),
        "touch_source_image_paths": sorted(touch_source_image_paths),
        "case_source_image_paths": sorted(case_source_image_paths),
        "em9305_source_image_paths": sorted(em9305_source_image_paths),
        "pt_protocol_project_paths": sorted(pt_protocol_project_paths),
        "pt_protocol_upstream_apache_paths": sorted(
            PT_PROTOCOL_APACHE_PATHS),
        "repository_only_project_paths": sorted(
            REPOSITORY_ONLY_PROJECT_PATHS),
        "root_policy_project_paths": sorted(root_policy_by_path),
        "root_policy_project_rows": root_policy_rows,
        "distributed_pending_paths": sorted(distributed_pending),
        "dual_mit_or_gpl_paths": sorted(dual_mit_gpl),
    }


def write_manifests(result: dict) -> list[Path]:
    summary = {key: value for key, value in result.items()
               if key not in ("rows", "pending_rows", "distributed_rows",
                              "community_project_paths",
                              "community_touch_apache_paths",
                              "touch_source_image_paths",
                              "case_source_image_paths",
                              "em9305_source_image_paths",
                              "pt_protocol_project_paths",
                              "repository_only_project_paths",
                              "root_policy_project_paths",
                              "root_policy_project_rows",
                              "distributed_pending_paths",
                              "dual_mit_or_gpl_paths")}
    summary["target_row_count"] = len(result["rows"])
    summary["pending_row_count"] = len(result["pending_rows"])
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return [CENSUS, SUMMARY]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifests", action="store_true")
    parser.add_argument("--require-normalized", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    print(json.dumps(result["metrics"], sort_keys=True))
    if args.require_normalized and not result["normalization_complete"]:
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Project license normalization audit failed: {exc}") from exc
