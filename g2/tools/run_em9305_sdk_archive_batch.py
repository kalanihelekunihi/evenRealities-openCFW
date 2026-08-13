#!/usr/bin/env python3
"""Run authenticated EM9305 SDK archive discovery scans in parallel."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Sequence


LABEL = re.compile(r"[a-z0-9][a-z0-9_.-]*")
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")


class BatchError(RuntimeError):
    """Raised when a batch input or output invariant changes."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    labels: set[str] = set()
    with path.open(newline="") as stream:
        for fields in csv.reader(stream, delimiter="\t"):
            if not fields or fields[0].startswith("#"):
                continue
            if len(fields) != 5:
                raise BatchError("manifest rows require label, path, blob, SHA-256, size")
            label, source_path, git_blob, archive_sha256, size_text = fields
            relative = Path(source_path)
            if not LABEL.fullmatch(label) or label in labels:
                raise BatchError(f"unsafe or duplicate archive label: {label}")
            if relative.is_absolute() or ".." in relative.parts or relative.suffix != ".a":
                raise BatchError(f"unsafe archive source path: {source_path}")
            if not HEX40.fullmatch(git_blob) or not HEX64.fullmatch(archive_sha256):
                raise BatchError(f"invalid archive identity: {label}")
            try:
                size = int(size_text)
            except ValueError as error:
                raise BatchError(f"invalid archive size: {label}") from error
            if size <= 0:
                raise BatchError(f"invalid archive size: {label}")
            labels.add(label)
            rows.append({
                "label": label,
                "source_path": source_path,
                "git_blob": git_blob,
                "sha256": archive_sha256,
                "size": size,
            })
    if not rows:
        raise BatchError("archive manifest is empty")
    return rows


def require_empty_output(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise BatchError(f"output directory must be absent or empty: {path}")
    path.mkdir(parents=True, exist_ok=True)


def run_archive(
    row: dict[str, Any],
    *,
    comparator: Path,
    image: Path,
    archive_root: Path,
    binutils_dir: Path,
    reports_dir: Path,
    logs_dir: Path,
    minimum_compared_bytes: int,
) -> dict[str, Any]:
    archive = archive_root / row["source_path"]
    report_path = reports_dir / f"{row['label']}.json"
    log_path = logs_dir / f"{row['label']}.log"
    command = [
        sys.executable,
        str(comparator),
        "--image", str(image),
        "--archive", str(archive),
        "--archive-kind", row["label"],
        "--archive-sha256", row["sha256"],
        "--archive-git-blob", row["git_blob"],
        "--archive-source-path", row["source_path"],
        "--binutils-dir", str(binutils_dir),
        "--minimum-compared-bytes", str(minimum_compared_bytes),
        "--json",
    ]
    started = time.time_ns()
    result = subprocess.run(command, capture_output=True, text=True)
    duration = time.time_ns() - started
    log_path.write_text(result.stderr)
    function_count = 0
    unique_count = 0
    compiler_anchors_matched = False
    report_sha256 = ""
    if result.returncode == 0:
        report_path.write_text(result.stdout)
        report = json.loads(result.stdout)
        function_count = report["function_count"]
        unique_count = len(report["unique_discovered_matches"])
        compiler_anchors_matched = report["identity"]["compiler_anchors_matched"]
        report_sha256 = sha256_file(report_path)
    else:
        log_path.write_text(result.stderr + result.stdout)
    return {
        **row,
        "exit_status": result.returncode,
        "duration_ns": duration,
        "function_count": function_count,
        "unique_match_count": unique_count,
        "compiler_anchors_matched": compiler_anchors_matched,
        "report_sha256": report_sha256,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--comparator", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--binutils-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=16)
    parser.add_argument("--minimum-compared-bytes", type=int, default=8)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.jobs < 1 or args.minimum_compared_bytes < 1:
        raise BatchError("jobs and minimum compared bytes must be positive")
    manifest = args.manifest.resolve()
    archive_root = args.archive_root.resolve()
    comparator = args.comparator.resolve()
    image = args.image.resolve()
    binutils_dir = args.binutils_dir.resolve()
    output = args.output_dir.resolve()
    for path in (manifest, comparator, image):
        if not path.is_file():
            raise BatchError(f"required file missing: {path}")
    for executable in ("ar", "objcopy", "objdump", "readelf"):
        path = binutils_dir / f"arc-linux-gnu-{executable}"
        if not path.is_file():
            raise BatchError(f"ARC binutils executable missing: {path}")
    rows = read_manifest(manifest)
    for row in rows:
        archive = archive_root / row["source_path"]
        if not archive.is_file() or archive.stat().st_size != row["size"]:
            raise BatchError(f"archive size/missing mismatch: {row['label']}")
        if sha256_file(archive) != row["sha256"]:
            raise BatchError(f"archive SHA-256 mismatch: {row['label']}")

    require_empty_output(output)
    reports = output / "reports"
    logs = output / "logs"
    reports.mkdir()
    logs.mkdir()
    config = {
        "jobs": args.jobs,
        "minimum_compared_bytes": args.minimum_compared_bytes,
        "python": sys.version.split()[0],
    }
    (output / "CONFIG.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")

    input_lines = [
        (sha256_file(Path(__file__).resolve()), "runner"),
        (sha256_file(comparator), "comparator"),
        (sha256_file(image), "firmware"),
        (sha256_file(manifest), "manifest"),
        (sha256_file(output / "CONFIG.json"), "configuration"),
    ]
    input_lines.extend((row["sha256"], f"archive:{row['label']}") for row in rows)
    (output / "INPUTS.tsv").write_text(
        "".join(f"{digest}\t{label}\n" for digest, label in input_lines)
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {
            row["label"]: executor.submit(
                run_archive,
                row,
                comparator=comparator,
                image=image,
                archive_root=archive_root,
                binutils_dir=binutils_dir,
                reports_dir=reports,
                logs_dir=logs,
                minimum_compared_bytes=args.minimum_compared_bytes,
            )
            for row in rows
        }
        results = {label: future.result() for label, future in futures.items()}

    fields = (
        "label", "source_path", "git_blob", "sha256", "size", "exit_status",
        "duration_ns", "function_count", "unique_match_count",
        "compiler_anchors_matched", "report_sha256",
    )
    with (output / "results.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results[row["label"]] for row in rows)

    checksum_paths = sorted(
        path for path in output.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    )
    (output / "SHA256SUMS").write_text("".join(
        f"{sha256_file(path)}  {path.relative_to(output)}\n" for path in checksum_paths
    ))
    failures = sum(result["exit_status"] != 0 for result in results.values())
    unique = sum(result["unique_match_count"] for result in results.values())
    print(
        f"EM9305_SDK_ARCHIVE_BATCH archives={len(rows)} failures={failures} "
        f"unique_matches={unique} jobs={args.jobs} output={output}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
