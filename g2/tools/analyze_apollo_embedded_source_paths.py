#!/usr/bin/env python3
"""Inventory retained Apollo-main build paths and map them to Ghidra functions.

The analyzer is read-only.  It authenticates the official 2.2.6.10 payload,
extracts every NUL-terminated ``__FILE__`` path rooted at the retained IAR
workspace, finds raw 32-bit pointers to each string, and can correlate those
literal-pool cells with the authenticated 64-shard Ghidra corpus.

Retained paths are lower-bound evidence: a translation unit can be linked
without leaving a path, while one path can be shared by many functions.
Consequently this tool reports ownership anchors, never whole-file byte
coverage inferred from path presence alone.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
)
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x0043_7FE0
WORKSPACE_PREFIX = b"D:\\01_workspace\\s200_ap510b_iar_git\\"
PATH_RE = re.compile(re.escape(WORKSPACE_PREFIX) + rb"[\x20-\x7e]{1,300}\.c(?=\x00)")

EXPECTED_ROOT_COUNTS = {
    "app": 98,
    "driver": 20,
    "framework": 7,
    "kernel": 1,
    "platform": 103,
    "product": 4,
    "third_party": 123,
    "utils": 1,
}
EXPECTED_THIRD_PARTY_COUNTS = {
    "EasyLogger-master": 3,
    "TinyFrame": 1,
    "cordio": 36,
    "littlefs": 2,
    "lvgl_v9.3": 78,
    "ringBuffer": 1,
    "tlsf": 2,
}
EXPECTED_PATH_COUNT = 357

# The audit-hardened Lorelei replay pins all 64 logs, statuses, configuration,
# and analyzed-template members through this manifest.  It is optional so the
# path-only audit remains reproducible without the large ephemeral corpus.
CORPUS_SHA256SUMS_SHA256 = (
    "3ff8aa908e5841823df9384cfbffca91d657816274797f332a45ff93a8aa832f"
)
LOCAL_REPLAY_CORPUS_SHA256SUMS_SHA256 = (
    "87d0befa001f042918bd6af83b0f50e13dd95aab160b0e520f2cb0bc55c6404e"
)
ACCEPTED_CORPUS_SHA256SUMS_SHA256 = frozenset(
    {CORPUS_SHA256SUMS_SHA256, LOCAL_REPLAY_CORPUS_SHA256SUMS_SHA256}
)
EXPECTED_LOG_COUNT = 64
EXPECTED_FUNCTION_COUNT = 7_370

FUNCTION_BEGIN_RE = re.compile(
    r"OPENCFW_FUNCTION_BEGIN entry=([0-9a-f]+) "
    r"body_start=([0-9a-f]+) body_end=([0-9a-f]+)",
    re.IGNORECASE,
)
FUNCTION_END_RE = re.compile(r"OPENCFW_FUNCTION_END entry=([0-9a-f]+)", re.IGNORECASE)
ADDRESS_TOKEN_RE = re.compile(r"(?<![0-9a-f])([0-9a-f]{8})(?![0-9a-f])", re.IGNORECASE)


class AuditError(RuntimeError):
    """Raised when authenticated evidence or a closed census changes."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _counter_dict(values: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _classify(relative: str) -> tuple[str, str | None]:
    parts = relative.split("\\")
    root = parts[0]
    dependency = parts[1] if root == "third_party" and len(parts) > 1 else None
    return root, dependency


def _find_all(blob: bytes, needle: bytes) -> list[int]:
    offsets: list[int] = []
    cursor = 0
    while True:
        offset = blob.find(needle, cursor)
        if offset < 0:
            return offsets
        offsets.append(offset)
        cursor = offset + 1


def extract_paths(blob: bytes) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    prefix = WORKSPACE_PREFIX.decode("ascii")
    for match in PATH_RE.finditer(blob):
        path = match.group().decode("ascii")
        if path in seen:
            raise AuditError(f"duplicate retained source path: {path}")
        seen.add(path)
        relative = path[len(prefix):]
        root, dependency = _classify(relative)
        run = LOAD_BASE + match.start()
        pointer_offsets = _find_all(blob, struct.pack("<I", run))
        records.append(
            {
                "file_offset": match.start(),
                "run": run,
                "path": path,
                "relative": relative,
                "root": root,
                "third_party_dependency": dependency,
                "pointer_cells": [LOAD_BASE + offset for offset in pointer_offsets],
            }
        )

    if len(records) != EXPECTED_PATH_COUNT:
        raise AuditError(
            f"expected {EXPECTED_PATH_COUNT} retained source paths, found {len(records)}"
        )
    root_counts = _counter_dict(record["root"] for record in records)
    if root_counts != EXPECTED_ROOT_COUNTS:
        raise AuditError(f"retained source root census changed: {root_counts!r}")
    dependency_counts = _counter_dict(
        record["third_party_dependency"]
        for record in records
        if record["third_party_dependency"] is not None
    )
    if dependency_counts != EXPECTED_THIRD_PARTY_COUNTS:
        raise AuditError(f"third-party path census changed: {dependency_counts!r}")
    return records


def _safe_manifest_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise AuditError(f"unsafe corpus manifest path: {relative}")
    resolved_root = root.resolve()
    resolved = (root / path).resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise AuditError(f"corpus manifest path escapes root: {relative}")
    return resolved


def verify_corpus(corpus_root: Path) -> list[Path]:
    sums = corpus_root / "SHA256SUMS"
    raw = sums.read_bytes()
    digest = sha256(raw)
    if digest not in ACCEPTED_CORPUS_SHA256SUMS_SHA256:
        raise AuditError(f"Ghidra corpus SHA256SUMS changed: {digest}")
    for line in raw.decode("ascii").splitlines():
        if not line:
            continue
        try:
            expected, relative = line.split("  ", 1)
        except ValueError as exc:
            raise AuditError(f"malformed SHA256SUMS line: {line!r}") from exc
        candidate = _safe_manifest_path(corpus_root, relative)
        if not candidate.is_file() or sha256(candidate.read_bytes()) != expected:
            raise AuditError(f"Ghidra corpus member failed authentication: {relative}")
    logs = sorted((corpus_root / "logs").glob("apollo-*.log"))
    if len(logs) != EXPECTED_LOG_COUNT:
        raise AuditError(f"expected {EXPECTED_LOG_COUNT} Ghidra logs, found {len(logs)}")
    return logs


def correlate_functions(
    records: list[dict[str, Any]],
    logs: list[Path],
    *,
    manifest_digest: str | None = None,
) -> dict[str, Any]:
    targets: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for index, record in enumerate(records):
        targets[record["run"]].append((index, "string"))
        for pointer_cell in record["pointer_cells"]:
            targets[pointer_cell].append((index, "pointer_cell"))

    functions: dict[int, dict[str, Any]] = {}
    path_hits: dict[int, dict[int, set[str]]] = defaultdict(lambda: defaultdict(set))
    current_entry: int | None = None
    for log in logs:
        for line in log.read_text(encoding="utf-8", errors="strict").splitlines():
            begin = FUNCTION_BEGIN_RE.search(line)
            if begin:
                entry, body_start, body_end = (int(value, 16) for value in begin.groups())
                if entry in functions:
                    raise AuditError(f"duplicate Ghidra function entry 0x{entry:08x}")
                functions[entry] = {
                    "entry": entry,
                    "body_start": body_start,
                    "body_end_inclusive": body_end,
                }
                current_entry = entry
                continue
            end = FUNCTION_END_RE.search(line)
            if end:
                entry = int(end.group(1), 16)
                if current_entry != entry:
                    raise AuditError(f"unbalanced Ghidra function marker 0x{entry:08x}")
                current_entry = None
                continue
            if current_entry is None:
                continue
            for token in ADDRESS_TOKEN_RE.findall(line):
                address = int(token, 16)
                for path_index, evidence in targets.get(address, ()):
                    path_hits[path_index][current_entry].add(evidence)
    if current_entry is not None:
        raise AuditError("unterminated Ghidra function at end of corpus")
    if len(functions) != EXPECTED_FUNCTION_COUNT:
        raise AuditError(
            f"expected {EXPECTED_FUNCTION_COUNT} Ghidra functions, found {len(functions)}"
        )

    linked_functions: dict[int, set[int]] = defaultdict(set)
    for path_index, hits in path_hits.items():
        records[path_index]["function_references"] = [
            {
                "entry": entry,
                "evidence": sorted(evidence),
            }
            for entry, evidence in sorted(hits.items())
        ]
        for entry in hits:
            linked_functions[entry].add(path_index)
    for index, record in enumerate(records):
        record.setdefault("function_references", [])

    function_records = []
    root_function_counts: Counter[str] = Counter()
    dependency_function_counts: Counter[str] = Counter()
    third_party_functions: set[int] = set()
    first_party_functions: set[int] = set()
    for entry, path_indexes in sorted(linked_functions.items()):
        roots = sorted({records[index]["root"] for index in path_indexes})
        dependencies = sorted(
            {
                records[index]["third_party_dependency"]
                for index in path_indexes
                if records[index]["third_party_dependency"] is not None
            }
        )
        for root in roots:
            root_function_counts[root] += 1
        for dependency in dependencies:
            dependency_function_counts[dependency] += 1
        if "third_party" in roots:
            third_party_functions.add(entry)
        if any(root != "third_party" for root in roots):
            first_party_functions.add(entry)
        function_records.append(
            {
                **functions[entry],
                "path_indexes": sorted(path_indexes),
                "roots": roots,
                "third_party_dependencies": dependencies,
            }
        )

    root_path_counts = _counter_dict(
        record["root"] for record in records if record["function_references"]
    )
    dependency_path_counts = _counter_dict(
        record["third_party_dependency"]
        for record in records
        if record["function_references"]
        and record["third_party_dependency"] is not None
    )
    return {
        "corpus": {
            "sha256sums_sha256": manifest_digest,
            "logs": len(logs),
            "functions": len(functions),
            "decompile_failures": 0,
        },
        "functions_with_path_references": len(linked_functions),
        "functions_without_path_references": len(functions) - len(linked_functions),
        "first_party_or_project_anchored_functions": len(first_party_functions),
        "third_party_anchored_functions": len(third_party_functions),
        "cross_root_anchored_functions": len(
            first_party_functions & third_party_functions
        ),
        "paths_with_function_references": len(path_hits),
        "paths_without_function_references": len(records) - len(path_hits),
        "root_function_counts": dict(sorted(root_function_counts.items())),
        "third_party_function_counts": dict(sorted(dependency_function_counts.items())),
        "root_path_counts": root_path_counts,
        "third_party_path_counts": dependency_path_counts,
        "functions": function_records,
    }


def analyze(image: Path = DEFAULT_IMAGE, corpus_root: Path | None = None) -> dict[str, Any]:
    blob = image.read_bytes()
    digest = sha256(blob)
    if len(blob) != IMAGE_SIZE or digest != IMAGE_SHA256:
        raise AuditError("official Apollo-main image identity mismatch")
    records = extract_paths(blob)
    root_counts = _counter_dict(record["root"] for record in records)
    dependency_counts = _counter_dict(
        record["third_party_dependency"]
        for record in records
        if record["third_party_dependency"] is not None
    )
    pointer_cell_count = sum(len(record["pointer_cells"]) for record in records)
    result: dict[str, Any] = {
        "schema_version": 1,
        "analysis_mode": "read-only; no hardware or flash operation",
        "image": {
            "path": str(image),
            "size": len(blob),
            "sha256": digest,
            "run_address_rule": "run = file_offset + 0x00437FE0",
        },
        "limitations": [
            "retained __FILE__ strings prove a compiled translation unit but their absence does not prove exclusion",
            "function references are ownership anchors, not a claim that every byte in the function is pristine upstream source",
            "path-linked function counts overlap when one function references more than one source root",
        ],
        "path_census": {
            "total_unique_paths": len(records),
            "root_counts": root_counts,
            "third_party_counts": dependency_counts,
            "third_party_unique_paths": root_counts["third_party"],
            "first_party_or_project_paths": len(records) - root_counts["third_party"],
            "raw_pointer_cells": pointer_cell_count,
        },
        "paths": records,
    }
    if corpus_root is not None:
        result["ghidra_correlation"] = correlate_functions(
            records,
            verify_corpus(corpus_root),
            manifest_digest=sha256((corpus_root / "SHA256SUMS").read_bytes()),
        )
    return result


def _text(report: dict[str, Any]) -> str:
    census = report["path_census"]
    lines = [
        "Apollo embedded source-path census",
        f"  image: {report['image']['sha256']}",
        f"  retained paths: {census['total_unique_paths']}",
        f"  third-party paths: {census['third_party_unique_paths']}",
        f"  first-party/project paths: {census['first_party_or_project_paths']}",
        f"  raw pointer cells: {census['raw_pointer_cells']}",
        "  third-party roots: "
        + ", ".join(
            f"{name}={count}" for name, count in census["third_party_counts"].items()
        ),
    ]
    correlation = report.get("ghidra_correlation")
    if correlation:
        lines.extend(
            [
                f"  authenticated Ghidra functions: {correlation['corpus']['functions']}",
                f"  functions with path anchors: {correlation['functions_with_path_references']}",
                f"  first-party/project anchored functions: {correlation['first_party_or_project_anchored_functions']}",
                f"  third-party anchored functions: {correlation['third_party_anchored_functions']}",
                f"  functions without path anchors: {correlation['functions_without_path_references']}",
                f"  paths with function anchors: {correlation['paths_with_function_references']}",
                f"  paths without function anchors: {correlation['paths_without_function_references']}",
                "  third-party anchored functions by family: "
                + ", ".join(
                    f"{name}={count}"
                    for name, count in correlation["third_party_function_counts"].items()
                ),
            ]
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument(
        "--ghidra-corpus",
        type=Path,
        help="audit-hardened 64-shard result root containing SHA256SUMS and logs/",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image, args.ghidra_corpus)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
