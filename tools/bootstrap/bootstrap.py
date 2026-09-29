#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fetch and verify the pinned openCFW analysis tools.

Every tool is listed in versions.json. Downloads go to an absolute prefix of
your choice (default: $OPENCFW_TOOLS). An artifact is accepted only if its
SHA-256 matches the pinned value. An unpinned artifact (sha256 null) is
refused unless you run --record, which downloads it, prints its hash, and
writes the hash back into versions.json for review and commit.

Licensed compilers are never downloaded. --licensed detects any installed
ones and writes their version output and binary hash to
build/toolchains.local.json, which is gitignored.

Examples:
    tools/bootstrap/bootstrap.py --list
    tools/bootstrap/bootstrap.py --prefix /opt/opencfw-tools --group ghidra
    tools/bootstrap/bootstrap.py --record objdiff-cli
    tools/bootstrap/bootstrap.py --licensed
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
LOCK = HERE / "versions.json"


def load_lock() -> dict:
    return json.loads(LOCK.read_text())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_suffix(dest.suffix + ".partial")
    with urllib.request.urlopen(url) as response, partial.open("wb") as out:
        shutil.copyfileobj(response, out)
    partial.replace(dest)


def artifact_path(prefix: Path, tool: dict) -> Path:
    name = tool["url"].rstrip("/").rsplit("/", 1)[-1] or tool["id"]
    return prefix / "downloads" / tool["id"] / name


def fetch(tool: dict, prefix: Path, record: bool) -> str | None:
    if not tool.get("url"):
        return (
            f"{tool['id']}: built from source {tool.get('source_repository')} "
            f"@ {tool.get('source_commit')}; no download step"
        )
    if "{" in tool["url"]:
        raise SystemExit(f"{tool['id']}: url contains a placeholder; confirm it in versions.json first")
    dest = artifact_path(prefix, tool)
    if not dest.exists():
        print(f"downloading {tool['id']} {tool['version']}", file=sys.stderr)
        download(tool["url"], dest)
    actual = sha256_file(dest)
    pinned = tool.get("sha256")
    if pinned is None:
        if not record:
            dest.unlink()
            raise SystemExit(f"{tool['id']}: no pinned sha256; review the source and rerun with --record")
        tool["sha256"] = actual
        return f"{tool['id']}: recorded sha256 {actual}"
    if actual != pinned:
        dest.unlink()
        raise SystemExit(f"{tool['id']}: sha256 mismatch (expected {pinned}, got {actual}); artifact removed")
    return f"{tool['id']}: ok {actual}"


def detect_licensed(lock: dict) -> None:
    results = []
    for entry in lock.get("licensed", []):
        exe = shutil.which(entry["detect"][0])
        record = {"id": entry["id"], "expected": entry["expected"], "found": bool(exe)}
        if exe:
            proc = subprocess.run(entry["detect"], capture_output=True, text=True)
            record.update(
                path=exe,
                sha256=sha256_file(Path(exe)),
                version_output=(proc.stdout + proc.stderr).strip()[:2000],
            )
        results.append(record)
        state = "found" if exe else "not installed"
        print(f"{entry['id']:<10} {state:<14} expected {entry['expected']}")
    out = REPO / "build" / "toolchains.local.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2) + "\n")
    print(f"wrote {out.relative_to(REPO)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prefix", default=os.environ.get("OPENCFW_TOOLS"))
    parser.add_argument("--group", action="append", help="limit to a group (repeatable)")
    parser.add_argument("--list", action="store_true", help="print the pinned tool table")
    parser.add_argument("--record", metavar="ID", action="append", help="download ID and write its sha256 into versions.json")
    parser.add_argument("--licensed", action="store_true", help="detect locally installed licensed compilers")
    args = parser.parse_args()
    lock = load_lock()

    if args.list:
        for tool in lock["tools"]:
            pin = tool.get("sha256") or "UNPINNED"
            print(f"{tool['group']:<10} {tool['id']:<28} {tool['version']:<28} {pin[:16]}")
        return 0
    if args.licensed:
        detect_licensed(lock)
        return 0
    if not args.prefix or not os.path.isabs(args.prefix):
        parser.error("--prefix (or $OPENCFW_TOOLS) must be an absolute path")
    prefix = Path(args.prefix)

    selected = [
        tool for tool in lock["tools"]
        if (args.record and tool["id"] in args.record)
        or (not args.record and (not args.group or tool["group"] in args.group))
    ]
    if args.record and len(selected) != len(set(args.record)):
        parser.error("unknown tool id in --record")
    for tool in selected:
        print(fetch(tool, prefix, record=bool(args.record)))
    if args.record:
        LOCK.write_text(json.dumps(lock, indent=2) + "\n")
        print(f"updated {LOCK.relative_to(REPO)}; review and commit the new hashes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
