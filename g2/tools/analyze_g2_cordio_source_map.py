#!/usr/bin/env python3
"""Build a fail-closed Cordio source-path/function evidence map for Apollo main.

This read-only analyzer composes the authenticated embedded-source-path replay
with the existing Cordio version audit.  It deliberately maps ownership
anchors, not whole translation units or exact vendor source.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATH_ANALYZER = ROOT / "tools" / "analyze_apollo_embedded_source_paths.py"
VERSION_ANALYZER = ROOT / "tools" / "analyze_g2_cordio_version.py"
EXPECTED_PATHS = 36
EXPECTED_ANCHORED_PATHS = 32
EXPECTED_ANCHORED_FUNCTIONS = 114
EXPECTED_BOUNDARY_COUNTS = {
    "ambiq_or_product_application_layer": 9,
    "ambiq_port": 5,
    "public_packetcraft_candidate": 22,
}
EXPECTED_MAP_SHA256 = "772063dc1841dc33523e68ecca9188923e28efd5cbe6db5a22a36979c41b2623"

CALL_RE = re.compile(r"\bFUN_([0-9a-f]{8})\s*\(", re.IGNORECASE)
INTEGER_RE = re.compile(r"(?<![A-Za-z0-9_])(?:0x[0-9a-f]+|\d+)(?![A-Za-z0-9_])", re.I)


class MappingError(RuntimeError):
    """Raised when authenticated input or the closed Cordio map changes."""


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise MappingError(f"cannot load analyzer: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _function_texts(logs: list[Path], path_module: Any) -> dict[int, str]:
    functions: dict[int, str] = {}
    current: int | None = None
    lines: list[str] = []
    for log in logs:
        for line in log.read_text(encoding="utf-8", errors="strict").splitlines():
            begin = path_module.FUNCTION_BEGIN_RE.search(line)
            if begin:
                if current is not None:
                    raise MappingError("nested Ghidra function markers")
                current = int(begin.group(1), 16)
                lines = []
                continue
            end = path_module.FUNCTION_END_RE.search(line)
            if end:
                entry = int(end.group(1), 16)
                if current != entry:
                    raise MappingError(f"unbalanced Ghidra function 0x{entry:08x}")
                functions[entry] = "\n".join(lines)
                current = None
                lines = []
                continue
            if current is not None:
                lines.append(line)
    if current is not None:
        raise MappingError("unterminated Ghidra function")
    return functions


def _calls(text: str, entry: int) -> list[int]:
    calls = {int(value, 16) for value in CALL_RE.findall(text)}
    calls.discard(entry)  # discard the decompiler's function declaration
    return sorted(calls)


def _literal_constants(text: str) -> list[int]:
    values = set()
    for token in INTEGER_RE.findall(text):
        value = int(token, 0)
        # Runtime/data addresses are topology, not behavioral constants.
        if value < 0x10000:
            values.add(value)
    return sorted(values)


def _balanced_calls(text: str, target: str) -> list[str]:
    result: list[str] = []
    needle = target + "("
    cursor = 0
    while True:
        start = text.find(needle, cursor)
        if start < 0:
            return result
        depth = 1
        index = start + len(needle)
        while index < len(text) and depth:
            depth += (text[index] == "(") - (text[index] == ")")
            index += 1
        if depth:
            raise MappingError(f"unterminated call to {target}")
        result.append(text[start + len(needle) : index - 1])
        cursor = index


def _arguments(value: str) -> list[str]:
    args: list[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(value):
        depth += (char == "(") - (char == ")")
        if char == "," and depth == 0:
            args.append(value[start:index].strip())
            start = index + 1
    args.append(value[start:].strip())
    return args


def _diagnostic_lines(text: str) -> list[int]:
    lines: set[int] = set()
    for call in _balanced_calls(text, "FUN_0043d574"):
        args = _arguments(call)
        if len(args) < 5:
            # The corpus can contain the provider's own declaration as well as calls.
            continue
        token = args[4]
        if re.fullmatch(r"(?:0x[0-9a-f]+|\d+)", token, re.I):
            lines.add(int(token, 0))
    return sorted(lines)


def _boundary(relative: str) -> str:
    if "\\ble-host\\sources\\hci\\ambiq\\" in relative or "\\wsf\\sources\\port\\freertos\\" in relative:
        return "ambiq_port"
    if "\\ble-profiles\\sources\\apps\\app\\" in relative:
        return "ambiq_or_product_application_layer"
    return "public_packetcraft_candidate"


def _stable_map_digest(paths: list[dict[str, Any]]) -> str:
    payload = json.dumps(paths, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def analyze(corpus_root: Path) -> dict[str, Any]:
    path_module = _load("apollo_embedded_paths_for_cordio", PATH_ANALYZER)
    version_module = _load("g2_cordio_version_for_map", VERSION_ANALYZER)
    logs = path_module.verify_corpus(corpus_root)
    path_report = path_module.analyze(corpus_root=corpus_root)
    version_report = version_module.analyze_bytes(version_module.MAIN.read_bytes())
    texts = _function_texts(logs, path_module)

    cordio = [
        record for record in path_report["paths"]
        if record["third_party_dependency"] == "cordio"
    ]
    mapped_paths: list[dict[str, Any]] = []
    unique_functions: set[int] = set()
    boundary_counts: dict[str, int] = {}
    for record in cordio:
        boundary = _boundary(record["relative"])
        boundary_counts[boundary] = boundary_counts.get(boundary, 0) + 1
        anchors = []
        for reference in record["function_references"]:
            entry = reference["entry"]
            function = next(
                item for item in path_report["ghidra_correlation"]["functions"]
                if item["entry"] == entry
            )
            text = texts[entry]
            unique_functions.add(entry)
            anchors.append({
                "entry": entry,
                "body_start": function["body_start"],
                "body_end_inclusive": function["body_end_inclusive"],
                "path_evidence": reference["evidence"],
                "direct_callees": _calls(text, entry),
                "literal_constants_u16": _literal_constants(text),
                "diagnostic_or_assert_line_numbers": _diagnostic_lines(text),
            })
        mapped_paths.append({
            "relative": record["relative"],
            "path_run_address": record["run"],
            "pointer_cells": record["pointer_cells"],
            "ownership_boundary": boundary,
            "function_anchors": anchors,
        })

    if len(mapped_paths) != EXPECTED_PATHS:
        raise MappingError(f"Cordio path census changed: {len(mapped_paths)}")
    anchored_paths = sum(bool(item["function_anchors"]) for item in mapped_paths)
    if anchored_paths != EXPECTED_ANCHORED_PATHS:
        raise MappingError(f"anchored Cordio path census changed: {anchored_paths}")
    if len(unique_functions) != EXPECTED_ANCHORED_FUNCTIONS:
        raise MappingError(f"anchored Cordio function census changed: {len(unique_functions)}")
    if dict(sorted(boundary_counts.items())) != EXPECTED_BOUNDARY_COUNTS:
        raise MappingError(f"Cordio ownership boundary census changed: {boundary_counts!r}")
    digest = _stable_map_digest(mapped_paths)
    if digest != EXPECTED_MAP_SHA256:
        raise MappingError(f"Cordio source/function map changed: {digest}")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no hardware, signing, flashing, or firmware mutation",
        "image": path_report["image"],
        "ghidra_corpus": path_report["ghidra_correlation"]["corpus"],
        "census": {
            "retained_cordio_paths": len(mapped_paths),
            "paths_with_function_anchors": anchored_paths,
            "paths_without_function_anchors": len(mapped_paths) - anchored_paths,
            "distinct_anchored_functions": len(unique_functions),
            "ownership_boundary_path_counts": dict(sorted(boundary_counts.items())),
            "map_sha256": digest,
        },
        "authenticated_public_interval": version_report["bounded_equivalence_interval"],
        "exact_upstream_commit": version_report["exact_upstream_commit"],
        "qualification": version_report["qualification"],
        "limitations": [
            "a retained path and its diagnostic references are function ownership anchors, not whole-file coverage",
            "Ghidra direct calls and constants are mechanical decompiler evidence, not recovered source names or ABI closure",
            "diagnostic_or_assert_line_numbers are the fifth arguments of the authenticated logger/assert provider and may include trace lines",
            "Ambiq FreeRTOS/HCI ports and Ambiq/Even application glue are excluded from the public Packetcraft candidate boundary",
            "the r20.05--r20.05c interval applies only to the version analyzer's stated function/blob scope",
        ],
        "paths": mapped_paths,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.ghidra_corpus)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        census = report["census"]
        print("Apollo Cordio source/function map")
        print(f"  retained paths: {census['retained_cordio_paths']}")
        print(f"  anchored paths: {census['paths_with_function_anchors']}")
        print(f"  distinct anchored functions: {census['distinct_anchored_functions']}")
        print(f"  map SHA-256: {census['map_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
