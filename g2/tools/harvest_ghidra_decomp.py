#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Harvest per-function decompilation evidence from an analyzed Ghidra project.

This is the ingest side of the transparent-source pipeline.  It runs headless
Ghidra over an already-analyzed project, exports every defined function's
decompiled C together with its bounds, signature, callees and body hash, and
files the result as a deterministic corpus that
``tools/build_transparent_function_db.py`` can consume.

The project itself is not modified: each parallel worker runs against its own
copy, so a harvest never mutates the evidence it reads.

Usage:
    tools/harvest_ghidra_decomp.py \\
        --project /var/tmp/opencfw-quicklist-ghidra.qCdBNM \\
        --project-name apollo_main_template \\
        --program ota_s200_firmware_ota.bin \\
        --output research/corpus/apollo-main/ghidra/decomp \\
        --jobs 8

Ghidra and a JDK are located from ``--ghidra-home``/``--java-home`` or the
matching environment variables; both default to the reviewed Homebrew paths.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = REPO_ROOT / "tools" / "ghidra_scripts"
EXPORT_SCRIPT = "ExportAllFunctionDecomp.java"
CENSUS_SCRIPT = "ReportProgramCensus.java"

DEFAULT_GHIDRA_HOME = "/opt/homebrew/Cellar/ghidra/12.1.2/libexec"
DEFAULT_JAVA_HOME = "/opt/homebrew/opt/openjdk"

#: Decompilation shards are written as concatenated C bundles rather than one
#: file per function, matching the existing ``g2-box-ghidra-decomp.c`` layout.
SHARD_BUNDLES = 16


class HarvestError(RuntimeError):
    """Raised when the harvest cannot produce authenticated evidence."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_ghidra(ghidra_home: str | None) -> Path:
    root = Path(ghidra_home or os.environ.get("GHIDRA_HOME", DEFAULT_GHIDRA_HOME))
    headless = root / "support" / "analyzeHeadless"
    if not headless.is_file():
        raise HarvestError(
            f"analyzeHeadless not found under {root}; pass --ghidra-home"
        )
    return headless


def resolve_java(java_home: str | None) -> Path:
    root = Path(java_home or os.environ.get("JAVA_HOME", DEFAULT_JAVA_HOME))
    if not (root / "bin" / "java").is_file():
        raise HarvestError(f"no JDK at {root}; pass --java-home")
    return root


def ghidra_environment(java_home: Path) -> dict[str, str]:
    environment = dict(os.environ)
    environment["JAVA_HOME"] = str(java_home)
    environment["PATH"] = f"{java_home / 'bin'}:{environment.get('PATH', '')}"
    return environment


def run_headless(
    headless: Path,
    environment: dict[str, str],
    project_dir: Path,
    project_name: str,
    program: str | None,
    script: str,
    script_args: list[str],
) -> str:
    command = [
        str(headless),
        str(project_dir),
        project_name,
        "-process",
    ]
    if program:
        command.append(program)
    command += [
        "-noanalysis",
        "-scriptPath",
        str(SCRIPT_DIR),
        "-postScript",
        script,
        *script_args,
    ]
    completed = subprocess.run(
        command,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise HarvestError(
            f"headless Ghidra failed ({completed.returncode}):\n"
            f"{completed.stdout[-4000:]}\n{completed.stderr[-4000:]}"
        )
    return completed.stdout


def parse_census(output: str) -> dict[str, str]:
    for line in output.splitlines():
        if "CENSUS " not in line:
            continue
        payload = line.split("CENSUS ", 1)[1]
        payload = payload.replace("(GhidraScript)", "").strip()
        census: dict[str, str] = {}
        for field in payload.split():
            if "=" not in field:
                continue
            key, value = field.split("=", 1)
            census[key] = value
        return census
    raise HarvestError("census script produced no CENSUS line")


def harvest_shard(
    headless: Path,
    environment: dict[str, str],
    source_project: Path,
    project_name: str,
    program: str | None,
    work_root: Path,
    output_root: Path,
    shard_index: int,
    shard_count: int,
) -> dict[str, Any]:
    """Copy the project and export one shard of its functions."""
    worker_project = work_root / f"worker-{shard_index:03d}"
    if worker_project.exists():
        shutil.rmtree(worker_project)
    shutil.copytree(source_project, worker_project)

    shard_output = work_root / f"out-{shard_index:03d}"
    shard_output.mkdir(parents=True, exist_ok=True)

    started = time.monotonic()
    output = run_headless(
        headless,
        environment,
        worker_project,
        project_name,
        program,
        EXPORT_SCRIPT,
        [str(shard_output), str(shard_index), str(shard_count)],
    )
    elapsed = time.monotonic() - started

    exported = failed = 0
    for line in output.splitlines():
        if "EXPORTED " in line:
            fields = line.split("EXPORTED ", 1)[1].split()
            exported = int(fields[0])
            failed = int(fields[2])

    shutil.rmtree(worker_project, ignore_errors=True)
    return {
        "shard": shard_index,
        "exported": exported,
        "failed": failed,
        "seconds": round(elapsed, 3),
        "output": str(shard_output),
    }


def collect(work_root: Path, shard_count: int) -> list[dict[str, Any]]:
    """Merge every worker's JSONL records, attaching decompiled bodies."""
    records: list[dict[str, Any]] = []
    for shard_index in range(shard_count):
        shard_output = work_root / f"out-{shard_index:03d}"
        record_path = shard_output / f"functions-{shard_index:03d}.jsonl"
        if not record_path.is_file():
            continue
        decomp_root = shard_output / "decomp"
        with record_path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                body_path = decomp_root / f"{record['entry']}.c"
                if body_path.is_file():
                    record["decomp_text"] = body_path.read_text(encoding="utf-8")
                records.append(record)
    records.sort(key=lambda record: int(record["entry"], 16))
    return records


def write_corpus(
    records: list[dict[str, Any]],
    output_root: Path,
    census: dict[str, str],
    harvest_meta: dict[str, Any],
) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    bundle_root = output_root / "bundles"
    if bundle_root.exists():
        shutil.rmtree(bundle_root)
    bundle_root.mkdir(parents=True)

    bundles: dict[int, list[str]] = {index: [] for index in range(SHARD_BUNDLES)}
    decompiled = 0
    for position, record in enumerate(records):
        text = record.pop("decomp_text", None)
        if text is None:
            continue
        decompiled += 1
        bundle_index = position * SHARD_BUNDLES // max(len(records), 1)
        bundle_index = min(bundle_index, SHARD_BUNDLES - 1)
        header = (
            f"/* FUN 0x{record['entry']} {record['name']} "
            f"bytes={record['body_bytes']} "
            f"sha256={record.get('body_sha256')} */\n"
        )
        bundles[bundle_index].append(header + text.rstrip() + "\n")

    bundle_digests: dict[str, str] = {}
    for index, chunks in bundles.items():
        name = f"apollo-decomp-{index:02d}.c"
        path = bundle_root / name
        body = (
            "/* Generated by tools/harvest_ghidra_decomp.py -- do not edit.\n"
            " * Ghidra decompiler output, unmodified, for identification and\n"
            " * source-recovery review.  Not compilable as-is and not firmware.\n"
            " */\n\n" + "\n".join(chunks)
        )
        path.write_text(body, encoding="utf-8")
        bundle_digests[name] = sha256_file(path)

    records_path = output_root / "functions.jsonl"
    with records_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")))
            handle.write("\n")

    summary = {
        "schema_version": 1,
        "generator": "tools/harvest_ghidra_decomp.py",
        "census": census,
        "harvest": harvest_meta,
        "counts": {
            "functions": len(records),
            "decompiled": decompiled,
            "not_decompiled": len(records) - decompiled,
            "function_body_bytes": sum(
                int(record.get("body_bytes") or 0) for record in records
            ),
        },
        "artifacts": {
            "functions.jsonl": sha256_file(records_path),
            **{f"bundles/{name}": digest for name, digest in bundle_digests.items()},
        },
    }
    summary_path = output_root / "HARVEST.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    sums_path = output_root / "SHA256SUMS"
    lines = [f"{digest}  {name}" for name, digest in sorted(summary["artifacts"].items())]
    lines.append(f"{sha256_file(summary_path)}  HARVEST.json")
    sums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--project-name", default="apollo_main_template")
    parser.add_argument("--program", default=None)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--ghidra-home", default=None)
    parser.add_argument("--java-home", default=None)
    parser.add_argument("--work-dir", default=None, type=Path)
    parser.add_argument(
        "--expect-executable-sha256",
        default=None,
        help="fail unless the analyzed program hashes to this value",
    )
    args = parser.parse_args(argv)

    try:
        headless = resolve_ghidra(args.ghidra_home)
        java_home = resolve_java(args.java_home)
    except HarvestError as failure:
        print(f"error: {failure}", file=sys.stderr)
        return 2

    environment = ghidra_environment(java_home)
    source_project = args.project.resolve()
    if not source_project.is_dir():
        print(f"error: project {source_project} not found", file=sys.stderr)
        return 2

    work_root = (
        args.work_dir.resolve()
        if args.work_dir
        else Path(tempfile.mkdtemp(prefix="opencfw-harvest-"))
    )
    work_root.mkdir(parents=True, exist_ok=True)

    census_project = work_root / "census"
    if census_project.exists():
        shutil.rmtree(census_project)
    shutil.copytree(source_project, census_project)
    census = parse_census(
        run_headless(
            headless,
            environment,
            census_project,
            args.project_name,
            args.program,
            CENSUS_SCRIPT,
            [],
        )
    )
    shutil.rmtree(census_project, ignore_errors=True)

    if args.expect_executable_sha256:
        actual = census.get("executable_sha256")
        if actual != args.expect_executable_sha256:
            print(
                "error: analyzed program hash mismatch\n"
                f"  expected {args.expect_executable_sha256}\n"
                f"  actual   {actual}",
                file=sys.stderr,
            )
            return 3

    print(
        f"harvesting {census.get('functions')} functions from "
        f"{census.get('program')} across {args.jobs} workers",
        file=sys.stderr,
    )

    shard_reports: list[dict[str, Any]] = []
    started = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [
            pool.submit(
                harvest_shard,
                headless,
                environment,
                source_project,
                args.project_name,
                args.program,
                work_root,
                args.output,
                shard_index,
                args.jobs,
            )
            for shard_index in range(args.jobs)
        ]
        for future in concurrent.futures.as_completed(futures):
            report = future.result()
            shard_reports.append(report)
            print(
                f"  shard {report['shard']:03d}: {report['exported']} exported, "
                f"{report['failed']} failed, {report['seconds']}s",
                file=sys.stderr,
            )
    elapsed = time.monotonic() - started

    records = collect(work_root, args.jobs)
    summary = write_corpus(
        records,
        args.output.resolve(),
        census,
        {
            "source_project": str(source_project),
            "project_name": args.project_name,
            "program": args.program,
            "jobs": args.jobs,
            "wall_seconds": round(elapsed, 3),
            "shards": sorted(shard_reports, key=lambda report: report["shard"]),
            "ghidra_home": str(headless.parent.parent),
            "java_home": str(java_home),
        },
    )

    print(
        f"wrote {summary['counts']['functions']} functions "
        f"({summary['counts']['decompiled']} decompiled) to {args.output}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
