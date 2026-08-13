#!/usr/bin/env python3
"""Authenticate an official AmbiqSuite WSF timer archive without extracting it.

The selected source is proprietary and is never printed or written.  This
tool verifies the archive, timer source/header/license identities, Git blob
OID, the 2.5.1 discriminator, and the recorded per-function source spans.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = ROOT / "tools" / "manifests" / "ambiqsuite-cordio-wsf-timer-provenance.tsv"
FUNCTION_MAP = ROOT / "tools" / "manifests" / "ambiqsuite-cordio-wsf-timer-function-map.tsv"


class VerificationError(RuntimeError):
    """Raised when a restricted archive or one of its identities changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_blob(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _read_tsv(path: Path) -> list[dict[str, str]]:
    lines = [
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    return list(csv.DictReader(lines, delimiter="\t"))


def verify(archive: Path, release: str) -> dict[str, Any]:
    rows = {row["release"]: row for row in _read_tsv(PROVENANCE)}
    if release not in rows:
        raise VerificationError(f"unsupported release: {release}")
    expected = rows[release]
    if archive.stat().st_size != int(expected["archive_bytes"]):
        raise VerificationError("archive size changed")
    if _sha256_file(archive) != expected["archive_sha256"]:
        raise VerificationError("archive SHA-256 changed")

    prefix = f"AmbiqSuite-R{release}/"
    with zipfile.ZipFile(archive) as bundle:
        source = bundle.read(prefix + expected["source_path"])
        header = bundle.read(prefix + expected["header_path"])
        license_pdf = bundle.read(prefix + expected["license_path"])

    if len(source) != int(expected["source_bytes"]):
        raise VerificationError("timer source size changed")
    if _sha256(source) != expected["source_sha256"]:
        raise VerificationError("timer source SHA-256 changed")
    if _git_blob(source) != expected["source_git_blob"]:
        raise VerificationError("timer source Git blob changed")
    if _sha256(header) != expected["header_sha256"]:
        raise VerificationError("timer header SHA-256 changed")
    if _sha256(license_pdf) != expected["license_sha256"]:
        raise VerificationError("SDK license SHA-256 changed")
    for marker in (
        b"ARM Ltd. confidential and proprietary",
        b"Software License Agreement",
    ):
        if marker not in source:
            raise VerificationError("proprietary source license marker changed")

    discriminator = b"g_ui32LastTime = xTaskGetTickCount();"
    has_saved_tick_init = discriminator in source
    if has_saved_tick_init != (release == "2.5.1"):
        raise VerificationError("saved-tick release discriminator changed")

    mapped_functions = 0
    if release == "2.5.1":
        source_lines = source.splitlines(keepends=True)
        for mapped in _read_tsv(FUNCTION_MAP):
            start = int(mapped["ambiq_source_start_line"])
            end = int(mapped["ambiq_source_end_line"])
            span = b"".join(source_lines[start - 1 : end])
            if len(span) != int(mapped["ambiq_source_span_bytes"]):
                raise VerificationError(f"source span size changed for {mapped['stock_name']}")
            if _sha256(span) != mapped["ambiq_source_span_sha256"]:
                raise VerificationError(f"source span SHA-256 changed for {mapped['stock_name']}")
            mapped_functions += 1

    return {
        "schema_version": 1,
        "release": release,
        "archive": str(archive),
        "archive_sha256": expected["archive_sha256"],
        "source_path": expected["source_path"],
        "source_bytes": len(source),
        "source_sha256": expected["source_sha256"],
        "source_git_blob": expected["source_git_blob"],
        "header_sha256": expected["header_sha256"],
        "license_sha256": expected["license_sha256"],
        "license": expected["license_classification"],
        "saved_tick_init": has_saved_tick_init,
        "mapped_function_spans": mapped_functions,
        "source_redistributed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--release", choices=("2.4.2", "2.5.1"), required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = verify(args.archive, args.release)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"AmbiqSuite {args.release}: authenticated; "
            f"source={report['source_sha256']}; spans={report['mapped_function_spans']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
