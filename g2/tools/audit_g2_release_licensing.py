#!/usr/bin/env python3
"""Audit source licenses and binary redistribution authority for G2 release."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any, Mapping

import open_cfw


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
NOTICE = ROOT / "NOTICE-CORE-SOURCE.md"
OVERLAYS = {
    "apollo_main": ROOT / "components/apollo_main/core_overlay/overlay.json",
    "apollo_bootloader": ROOT / "components/bootloader/core_overlay/overlay.json",
}
LICENSE_TEXTS = {
    "MIT": ROOT.parent / "LICENSE",
    "GPL-3.0-only": ROOT / "components/apollo_main/ring_gesture/LICENSE",
    "GPL-3.0-or-later": ROOT / "components/apollo_main/ring_gesture/LICENSE",
    "Apache-2.0": ROOT / "third_party/cordio/LICENSE.md",
    "BSD-3-Clause": ROOT / "third_party/littlefs/LICENSE.md",
    "BSD-2-Clause": ROOT / "third_party/lz4/LICENSE",
    "Zlib": ROOT / "third_party/nanopb/LICENSE.txt",
}
LICENSE_TEXT_SHA256 = {
    "MIT": "3a0f162b73b7d95cdb1de2395b4f0f4ad35eae3c8eb44f125d5c0db6bc811ea4",
    "GPL-3.0-only": "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986",
    "GPL-3.0-or-later": "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986",
    "Apache-2.0": "682ae5978019e4ee9d439b300efb125525b2e4cc4181ebd1e676dd60dc69d7cd",
    "BSD-3-Clause": "0cb4ff1daf5fdc1359c6a6ee3116092f08fc100c9d58b1b77ab17bfd801f856d",
    "BSD-2-Clause": "8b58c446121a109ccf32edc094bba3010a3d85e4ee3702950db55e4d3e87736c",
    "Zlib": "e2f2fc8fe3faa7dcb09dbe995db48c6ec5c1f72705db915101e4a83fed44f66d",
}

# Possession of authenticated official firmware is evidence of identity, not a
# redistribution grant.  An ``authorized`` record is accepted only when both a
# grant/license artifact and a separate compliance record are checked into this
# repository and authenticated below.  Merely changing the status string cannot
# open the release gate.
BINARY_AUTHORITY = {
    "codec": {
        "status": "unresolved",
        "reason": "official Even/NationalChip-derived codec blob; no redistribution grant is recorded",
        "evidence": None,
    },
    "ble_em9305": {
        "status": "unresolved",
        "reason": "official Even/EM9305 patch blob; no redistribution grant is recorded",
        "evidence": None,
    },
    "touch": {
        "status": "unresolved",
        "reason": "official Even touch-controller blob; no redistribution grant is recorded",
        "evidence": None,
    },
    "case": {
        "status": "unresolved",
        "reason": "official Even charging-case blob; no redistribution grant is recorded",
        "evidence": None,
    },
    "apollo_bootloader": {
        "status": "unresolved",
        "reason": "source overlay retains official Even bootloader bytes without a recorded redistribution grant",
        "evidence": None,
    },
    "apollo_main": {
        "status": "unresolved",
        "reason": "source overlay retains official Even application bytes without a recorded redistribution grant",
        "evidence": None,
    },
}

AUTHORITY_EVIDENCE_FIELDS = {
    "grant_path",
    "grant_sha256",
    "terms",
    "reference",
    "compliance_path",
    "compliance_sha256",
}
SHA256_RE = re.compile(r"[0-9a-f]{64}")
MAX_AUTHORITY_EVIDENCE_SIZE = 16 * 1024 * 1024
PROJECT_LICENSE_CENSUS = (
    ROOT / "tools/manifests/g2-project-license-normalization.tsv"
)
PROJECT_LICENSE_CENSUS_ROWS = 459
PROJECT_LICENSE_CENSUS_DIGEST = (
    "90c068286c602b912396a98ae464b87e245e2fd81525d357f0d2b07cf0a2f31c"
)
class ReleaseAuthorityError(RuntimeError):
    """Raised when an external binary release is not fully authorized."""


def _evidence_snapshot_identity(metadata: os.stat_result) -> tuple[int, ...]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _read_authority_evidence_once(
    root: Path, relative: Path, *, label: str
) -> tuple[bytes | None, list[str]]:
    """Read one evidence artifact beneath ``root`` without following links."""
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    file_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptors: list[int] = []
    try:
        descriptor = os.open(root, directory_flags)
        descriptors.append(descriptor)
        for part in relative.parts[:-1]:
            descriptor = os.open(
                part, directory_flags, dir_fd=descriptors[-1]
            )
            descriptors.append(descriptor)
            if not stat.S_ISDIR(os.fstat(descriptor).st_mode):
                return None, [f"{label} parent is not a directory"]
        descriptor = os.open(
            relative.parts[-1], file_flags, dir_fd=descriptors[-1]
        )
        descriptors.append(descriptor)
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            return None, [f"{label} is not an independent regular file"]
        if before.st_size > MAX_AUTHORITY_EVIDENCE_SIZE:
            return None, [f"{label} exceeds the evidence size cap"]
        chunks: list[bytes] = []
        remaining = MAX_AUTHORITY_EVIDENCE_SIZE + 1
        while remaining:
            chunk = os.read(descriptor, min(remaining, 1024 * 1024))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        after = os.fstat(descriptor)
        if (
            len(data) > MAX_AUTHORITY_EVIDENCE_SIZE
            or len(data) != before.st_size
            or _evidence_snapshot_identity(before)
            != _evidence_snapshot_identity(after)
        ):
            return None, [f"{label} changed during descriptor read"]
        return data, []
    except OSError:
        return None, [f"{label} is missing or could not be opened safely"]
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _authenticated_evidence_path(
    value: Any,
    digest: Any,
    *,
    label: str,
    root: Path,
    component: str,
) -> tuple[str | None, list[str]]:
    errors: list[str] = []
    if not isinstance(value, str) or not value:
        return None, [f"{label} path is missing"]
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        errors.append(f"{label} SHA-256 is invalid")
    relative = Path(value)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        errors.append(f"{label} path escapes the G2 root")
        return value, errors
    required_root = Path("docs/release-authority") / component
    try:
        relative.relative_to(required_root)
    except ValueError:
        errors.append(
            f"{label} path must be below docs/release-authority/{component}"
        )
    if errors:
        return value, errors
    payload, read_errors = _read_authority_evidence_once(
        root, relative, label=f"{label} artifact"
    )
    errors.extend(read_errors)
    if payload is not None and not errors and hashlib.sha256(payload).hexdigest() != digest:
        errors.append(f"{label} artifact SHA-256 mismatch")
    return value, errors


def validate_binary_authority_record(
    component: str,
    record: Any,
    *,
    root: Path = ROOT,
) -> dict[str, Any]:
    """Validate one evidence-backed redistribution-authority record."""
    errors: list[str] = []
    if not isinstance(record, Mapping):
        return {
            "status": "unresolved",
            "reason": "binary-authority record is not a structured object",
            "evidence": None,
            "errors": [f"{component}: binary-authority record is not an object"],
        }
    status = record.get("status")
    reason = record.get("reason")
    evidence = record.get("evidence")
    if status not in {"unresolved", "authorized"}:
        errors.append(f"{component}: binary-authority status is invalid")
        status = "unresolved"
    if not isinstance(reason, str) or not reason.strip():
        errors.append(f"{component}: binary-authority reason is missing")
        reason = "binary-authority reason is missing"

    if status == "unresolved":
        if evidence is not None:
            errors.append(
                f"{component}: unresolved authority must not carry release evidence"
            )
        return {
            "status": "unresolved",
            "reason": reason,
            "evidence": None,
            "errors": errors,
        }

    if not isinstance(evidence, Mapping) or set(evidence) != AUTHORITY_EVIDENCE_FIELDS:
        errors.append(
            f"{component}: authorized status lacks the exact structured evidence record"
        )
        return {
            "status": "unresolved",
            "reason": reason,
            "evidence": None,
            "errors": errors,
        }
    for field in ("terms", "reference"):
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            errors.append(f"{component}: authority {field} is missing")
    grant_path, grant_errors = _authenticated_evidence_path(
        evidence.get("grant_path"),
        evidence.get("grant_sha256"),
        label=f"{component} grant/license",
        root=root,
        component=component,
    )
    compliance_path, compliance_errors = _authenticated_evidence_path(
        evidence.get("compliance_path"),
        evidence.get("compliance_sha256"),
        label=f"{component} compliance",
        root=root,
        component=component,
    )
    errors.extend(grant_errors)
    errors.extend(compliance_errors)
    if (
        grant_path is not None
        and compliance_path is not None
        and Path(grant_path) == Path(compliance_path)
    ):
        errors.append(
            f"{component}: grant/license and compliance evidence must be "
            "distinct independently authenticated files"
        )
    return {
        "status": "authorized" if not errors else "unresolved",
        "reason": reason,
        "evidence": dict(evidence),
        "errors": errors,
    }


def _source_records(
    overlay: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    records: dict[str, dict[str, Any]] = {}
    conflicts: list[str] = []

    def add(record: dict[str, Any]) -> None:
        path = record["path"]
        previous = records.get(path)
        if previous is not None:
            # Origins and upstream URLs may legitimately describe different
            # functions emitted from one translation unit.  Authenticated file
            # identity, license, and upstream version may not disagree.
            for field in ("sha256", "size", "license", "upstream_commit"):
                if (
                    field in previous
                    and field in record
                    and previous[field] != record[field]
                ):
                    conflicts.append(
                        f"duplicate source metadata conflict: {path}: {field}"
                    )
        records[path] = record

    def visit(value: Any, key: str | None = None) -> None:
        if isinstance(value, dict):
            if key == "source" and isinstance(value.get("path"), str):
                add(value)
            for child_key, child in value.items():
                visit(child, child_key)
        elif isinstance(value, list):
            if key == "sources":
                for record in value:
                    if isinstance(record, dict) and isinstance(
                        record.get("path"), str
                    ):
                        add(record)
            for child in value:
                visit(child, key)

    visit(overlay)
    return records, list(dict.fromkeys(conflicts))


def _classify_source(record: dict[str, Any]) -> str:
    path = record["path"]
    origin = record.get("origin", "").lower()
    if path.startswith("third_party/") or record.get("upstream"):
        return "upstream-licensed"
    if "opencfw" in origin or "clean-room" in origin or path.startswith("components/"):
        return "project-owned-or-adapted"
    return "source-ownership-unresolved"


def _project_mit_paths() -> set[str]:
    payload, errors = _read_authority_evidence_once(
        ROOT,
        PROJECT_LICENSE_CENSUS.relative_to(ROOT),
        label="project-owned MIT census",
    )
    if payload is None or errors:
        raise ReleaseAuthorityError(errors[0])
    text = payload.decode("utf-8")
    rows = list(csv.DictReader(
        (line for line in text.splitlines(True) if not line.startswith("#")),
        delimiter="\t",
    ))
    identity = "".join(
        f"{row['path']}\t{row['overlay_license']}\n" for row in rows
    ).encode()
    if (
        len(rows) != PROJECT_LICENSE_CENSUS_ROWS
        or hashlib.sha256(identity).hexdigest() != PROJECT_LICENSE_CENSUS_DIGEST
    ):
        raise ReleaseAuthorityError("project-owned MIT census identity changed")
    return {row["path"] for row in rows}


def _project_mit_policy_error(
    relative: str, license_id: Any, project_mit_paths: set[str]
) -> str | None:
    if relative in project_mit_paths and license_id != "MIT":
        return "project-owned source must use MIT"
    return None


def _license_text_payload_error(license_id: str, payload: bytes) -> str | None:
    expected = LICENSE_TEXT_SHA256.get(license_id)
    if expected is None or hashlib.sha256(payload).hexdigest() != expected:
        return f"license text identity changed: {license_id}"
    return None


def _repository_license_evidence_path(path: Path) -> str:
    """Return one canonical repository-root-relative license identity."""
    try:
        return path.relative_to(ROOT.parent).as_posix()
    except ValueError as error:
        raise ReleaseAuthorityError(
            f"license evidence escapes repository: {path}"
        ) from error


def _safe_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        relative = path.relative_to(ROOT)
    except ValueError as error:
        raise ReleaseAuthorityError(f"{label} escapes G2 root") from error
    payload, errors = _read_authority_evidence_once(ROOT, relative, label=label)
    if payload is None or errors:
        raise ReleaseAuthorityError(errors[0])
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReleaseAuthorityError(f"{label} is invalid JSON") from error
    if not isinstance(value, dict):
        raise ReleaseAuthorityError(f"{label} is not an object")
    return value


def _load_manifest_safely(
    path: Path, loading: tuple[Path, ...] = ()
) -> dict[str, Any]:
    lexical = Path(os.path.abspath(path))
    if lexical in loading:
        raise ReleaseAuthorityError("manifest inheritance cycle")
    manifest = _safe_json(lexical, label=f"release manifest {lexical.name}")
    if manifest.get("schema_version") != 1:
        raise ReleaseAuthorityError("only manifest schema version 1 is supported")
    extends = manifest.get("extends")
    if extends is not None:
        if not isinstance(extends, str) or not extends:
            raise ReleaseAuthorityError("manifest extends is invalid")
        parent = Path(os.path.abspath(lexical.parent / extends))
        try:
            parent.relative_to(lexical.parent)
        except ValueError as error:
            raise ReleaseAuthorityError(
                "manifest extends escapes manifests directory"
            ) from error
        manifest = open_cfw.merge_manifest(
            _load_manifest_safely(parent, (*loading, lexical)), manifest
        )
    if manifest.get("package", {}).get("format") != "EVENOTA":
        raise ReleaseAuthorityError("manifest does not describe EVENOTA")
    if not isinstance(manifest.get("components"), list) or not manifest["components"]:
        raise ReleaseAuthorityError("manifest component inventory is invalid")
    return manifest


def analyze(
    *,
    authority_records: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = _load_manifest_safely(MANIFEST)
    authority_records = (
        BINARY_AUTHORITY if authority_records is None else authority_records
    )
    artifacts = []
    authority_errors: list[str] = []
    for component in manifest["components"]:
        name = component["name"]
        authority = validate_binary_authority_record(
            name,
            authority_records.get(
                name,
                {
                    "status": "unresolved",
                    "reason": "component has no binary-authority record",
                    "evidence": None,
                },
            ),
        )
        authority_errors.extend(authority["errors"])
        provider = component["provider"]
        artifacts.append({
            "component": name,
            "package_filename": component["package_filename"],
            "provider_kind": provider["kind"],
            "provider_path": provider["path"],
            "provider_size": provider.get("size"),
            "provider_sha256": provider.get("sha256"),
            "provider_profiles": provider.get("profiles", {}),
            "redistribution_authority": authority["status"],
            "authority_evidence": authority["evidence"],
            "authority_evidence_errors": authority["errors"],
            "reason": authority["reason"],
            "source_availability": (
                "overlay-source-plus-retained-binary"
                if name in OVERLAYS else "binary-only-in-core-source-package"
            ),
        })

    source_by_path: dict[str, dict[str, Any]] = {}
    source_errors: list[str] = []
    try:
        project_mit_paths = _project_mit_paths()
    except (ReleaseAuthorityError, UnicodeDecodeError, csv.Error) as error:
        project_mit_paths = set()
        source_errors.append(str(error))
    license_text_errors: dict[str, str | None] = {}
    for license_id, license_path in LICENSE_TEXTS.items():
        try:
            relative = license_path.relative_to(ROOT.parent)
            payload, errors = _read_authority_evidence_once(
                ROOT.parent, relative, label=f"{license_id} license text"
            )
            if payload is None or errors:
                license_text_errors[license_id] = errors[0]
            else:
                license_text_errors[license_id] = _license_text_payload_error(
                    license_id, payload
                )
        except ValueError:
            license_text_errors[license_id] = (
                f"license text escapes repository: {license_path}"
            )
    for component, overlay_path in OVERLAYS.items():
        try:
            overlay = _safe_json(
                overlay_path, label=f"{component} licensing overlay"
            )
        except ReleaseAuthorityError as error:
            source_errors.append(str(error))
            continue
        records, duplicate_conflicts = _source_records(overlay)
        source_errors.extend(
            f"{component}: {error}" for error in duplicate_conflicts
        )
        for relative, record in sorted(records.items()):
            relative_path = Path(relative)
            if (
                relative_path.is_absolute()
                or not relative_path.parts
                or ".." in relative_path.parts
            ):
                source_errors.append(f"{component}: source escapes G2 root: {relative}")
                continue
            license_id = record.get("license")
            errors = []
            payload, read_errors = _read_authority_evidence_once(
                ROOT, relative_path, label=f"overlay source {relative}"
            )
            if payload is None or read_errors:
                errors.append("source missing or could not be opened safely")
            elif hashlib.sha256(payload).hexdigest() != record.get("sha256"):
                errors.append("source SHA-256 mismatch")
            license_evidence = record.get("license_path")
            license_evidence_sha256 = record.get("license_sha256")
            canonical_license_evidence = None
            if license_id not in LICENSE_TEXTS:
                errors.append(f"non-SPDX or unsupported license id: {license_id!r}")
            elif license_evidence is not None or license_evidence_sha256 is not None:
                if (
                    not isinstance(license_evidence, str)
                    or not license_evidence
                    or not isinstance(license_evidence_sha256, str)
                    or re.fullmatch(r"[0-9a-f]{64}", license_evidence_sha256) is None
                ):
                    errors.append("source-specific license evidence is malformed")
                else:
                    license_relative = Path(license_evidence)
                    if (
                        license_relative.is_absolute()
                        or not license_relative.parts
                        or ".." in license_relative.parts
                    ):
                        errors.append("source-specific license evidence escapes G2 root")
                    else:
                        try:
                            canonical_license_evidence = (
                                _repository_license_evidence_path(
                                    ROOT / license_relative
                                )
                            )
                        except ReleaseAuthorityError as error:
                            errors.append(str(error))
                        license_payload, license_read_errors = (
                            _read_authority_evidence_once(
                                ROOT,
                                license_relative,
                                label=f"overlay source license {relative}",
                            )
                        )
                        if license_payload is None or license_read_errors:
                            errors.append(
                                "source-specific license evidence could not be opened safely"
                            )
                        elif hashlib.sha256(license_payload).hexdigest() != (
                            license_evidence_sha256
                        ):
                            errors.append(
                                "source-specific license evidence SHA-256 mismatch"
                            )
            elif license_text_errors[license_id] is not None:
                errors.append(license_text_errors[license_id])
            else:
                try:
                    canonical_license_evidence = (
                        _repository_license_evidence_path(
                            LICENSE_TEXTS[license_id]
                        )
                    )
                except ReleaseAuthorityError as error:
                    errors.append(str(error))
            classification = _classify_source(record)
            project_policy_error = _project_mit_policy_error(
                relative, license_id, project_mit_paths
            )
            if project_policy_error is not None:
                errors.append(project_policy_error)
            row = {
                "components": [component],
                "path": relative,
                "sha256": record.get("sha256"),
                "license": license_id,
                "classification": classification,
                "upstream": record.get("upstream"),
                "upstream_commit": record.get("upstream_commit"),
                "license_evidence": canonical_license_evidence,
                "errors": errors,
            }
            previous = source_by_path.get(relative)
            if previous is None:
                source_by_path[relative] = row
            else:
                for field in ("sha256", "license", "classification", "upstream", "upstream_commit"):
                    if previous[field] != row[field]:
                        source_errors.append(
                            f"cross-component source metadata conflict: {relative}: {field}"
                        )
                if component not in previous["components"]:
                    previous["components"].append(component)
                previous["errors"].extend(
                    error for error in errors if error not in previous["errors"]
                )
            source_errors.extend(f"{component}: {relative}: {error}" for error in errors)

    source_rows = [source_by_path[path] for path in sorted(source_by_path)]
    unresolved = [row["component"] for row in artifacts
                  if row["redistribution_authority"] != "authorized"]
    if not NOTICE.is_file():
        source_errors.append("core-source NOTICE is missing")
    return {
        "schema_version": 1,
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "notice": NOTICE.relative_to(ROOT).as_posix(),
        "separation_rule": (
            "source availability and source license compliance do not establish "
            "permission to redistribute retained or binary-only firmware"
        ),
        "artifacts": artifacts,
        "source_inventory": source_rows,
        "summary": {
            "package_artifacts": len(artifacts),
            "source_files": len(source_rows),
            "source_errors": len(source_errors),
            "redistribution_authority_unresolved": unresolved,
            "binary_authority_errors": len(authority_errors),
            "release_authorized": (
                not unresolved and not authority_errors and not source_errors
            ),
        },
        "binary_authority_errors": authority_errors,
        "source_errors": source_errors,
    }


def assert_release_authorized(
    *,
    authority_records: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    report = analyze(authority_records=authority_records)
    if not report["summary"]["release_authorized"]:
        unresolved = ", ".join(
            report["summary"]["redistribution_authority_unresolved"]
        ) or "none"
        evidence = report["binary_authority_errors"]
        detail = f"; evidence errors: {evidence[0]}" if evidence else ""
        raise ReleaseAuthorityError(
            "G2 release redistribution authority is unresolved for: "
            + unresolved
            + detail
        )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--release-gate", action="store_true")
    args = parser.parse_args(argv)
    report = analyze()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        print("G2 core-source release licensing audit")
        print(f"  package artifacts: {summary['package_artifacts']}")
        print(f"  unique overlay sources: {summary['source_files']}")
        print(f"  source metadata errors: {summary['source_errors']}")
        print("  unresolved binary authority: " + ", ".join(
            summary["redistribution_authority_unresolved"]
        ))
        print(f"  external release authorized: {summary['release_authorized']}")
    return 2 if args.release_gate and not report["summary"]["release_authorized"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
