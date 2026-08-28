#!/usr/bin/env python3
"""Audit source licenses and binary redistribution authority for G2 release."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import json
import re
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
    "ISC": ROOT / "third_party/invensense-icm45608/LICENSE",
    "Zlib": ROOT / "third_party/nanopb/LICENSE.txt",
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


class ReleaseAuthorityError(RuntimeError):
    """Raised when an external binary release is not fully authorized."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    unresolved = root / value
    candidate = unresolved.resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{label} path escapes the G2 root")
        return value, errors
    required_root = (root / "docs/release-authority" / component).resolve()
    try:
        candidate.relative_to(required_root)
    except ValueError:
        errors.append(
            f"{label} path must be below docs/release-authority/{component}"
        )
    if unresolved.is_symlink() or not candidate.is_file():
        errors.append(f"{label} artifact is missing or not a regular file")
    elif not errors and _sha256(candidate) != digest:
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
    _, grant_errors = _authenticated_evidence_path(
        evidence.get("grant_path"),
        evidence.get("grant_sha256"),
        label=f"{component} grant/license",
        root=root,
        component=component,
    )
    _, compliance_errors = _authenticated_evidence_path(
        evidence.get("compliance_path"),
        evidence.get("compliance_sha256"),
        label=f"{component} compliance",
        root=root,
        component=component,
    )
    errors.extend(grant_errors)
    errors.extend(compliance_errors)
    return {
        "status": "authorized" if not errors else "unresolved",
        "reason": reason,
        "evidence": dict(evidence),
        "errors": errors,
    }


def _source_records(overlay: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}

    def visit(value: Any, key: str | None = None) -> None:
        if isinstance(value, dict):
            if key == "source" and isinstance(value.get("path"), str):
                records[value["path"]] = value
            for child_key, child in value.items():
                visit(child, child_key)
        elif isinstance(value, list):
            if key == "sources":
                for record in value:
                    if isinstance(record, dict) and isinstance(
                        record.get("path"), str
                    ):
                        records[record["path"]] = record
            for child in value:
                visit(child, key)

    visit(overlay)
    return records


def _classify_source(record: dict[str, Any]) -> str:
    path = record["path"]
    origin = record.get("origin", "").lower()
    if path.startswith("third_party/") or record.get("upstream"):
        return "upstream-licensed"
    if "opencfw" in origin or "clean-room" in origin or path.startswith("components/"):
        return "project-owned-or-adapted"
    return "source-ownership-unresolved"


def analyze(
    *,
    authority_records: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = open_cfw.load_manifest(MANIFEST)
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
    for component, overlay_path in OVERLAYS.items():
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
        for relative, record in sorted(_source_records(overlay).items()):
            path = (ROOT / relative).resolve()
            try:
                path.relative_to(ROOT.resolve())
            except ValueError:
                source_errors.append(f"{component}: source escapes G2 root: {relative}")
                continue
            license_id = record.get("license")
            errors = []
            if not path.is_file():
                errors.append("source missing")
            elif _sha256(path) != record.get("sha256"):
                errors.append("source SHA-256 mismatch")
            if license_id not in LICENSE_TEXTS:
                errors.append(f"non-SPDX or unsupported license id: {license_id!r}")
            elif not LICENSE_TEXTS[license_id].is_file():
                errors.append(f"license text missing: {LICENSE_TEXTS[license_id]}")
            row = {
                "components": [component],
                "path": relative,
                "sha256": record.get("sha256"),
                "license": license_id,
                "classification": _classify_source(record),
                "upstream": record.get("upstream"),
                "upstream_commit": record.get("upstream_commit"),
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
