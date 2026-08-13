#!/usr/bin/env python3
"""Fail-closed, production-excluded LVGL function/source mapping audit.

This deliberately proves one function mapping, not translation-unit ownership.
It combines the authenticated embedded-path census, authenticated Ghidra corpus,
official-image bytes, and the pinned LVGL compatibility-ceiling snapshot.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATH_ANALYZER = ROOT / "tools" / "analyze_apollo_embedded_source_paths.py"
IMAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
SOURCE = ROOT / "third_party" / "lvgl" / "src" / "misc" / "lv_iter.c"
RELATIVE_PATH = r"third_party\lvgl_v9.3\LVGL\src\misc\lv_iter.c"
ENTRY = 0x005C3B00
END_EXCLUSIVE = 0x005C3BB2
SPAN_SHA256 = "847ee3dfb073799b7aeb960e5ae8bdfbcc245808186043d882931bc78f81655f"
SOURCE_SHA256 = "c645dd99be4f4247be8d9f9a4caefea257ce3458db1a952de415b9c069942ae2"
SOURCE_GIT_BLOB = "cb6377c0b50060710e5446dce5d083bfe3bed539"
SOURCE_PATH_RUN = 0x006E8794
SOURCE_POINTER_CELL = 0x005C3BC4


class AuditError(RuntimeError):
    """Raised when any member of the closed mapping changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_blob(data: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data, usedforsecurity=False
    ).hexdigest()


def _load_path_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_paths_for_lvgl", PATH_ANALYZER)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load embedded-source-path analyzer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _require_text(text: str, pattern: str, label: str) -> None:
    if re.search(pattern, text) is None:
        raise AuditError(f"lv_iter_create Ghidra topology changed: {label}")


def analyze(corpus_root: Path, image: Path = IMAGE, source: Path = SOURCE) -> dict[str, Any]:
    paths = _load_path_analyzer()
    report = paths.analyze(image, corpus_root)
    matches = [item for item in report["paths"] if item["relative"] == RELATIVE_PATH]
    if len(matches) != 1:
        raise AuditError(f"expected one retained lv_iter.c path, found {len(matches)}")
    anchor = matches[0]
    if anchor["run"] != SOURCE_PATH_RUN or anchor["pointer_cells"] != [SOURCE_POINTER_CELL]:
        raise AuditError("lv_iter.c path or pointer-cell relocation changed")
    if anchor["function_references"] != [
        {"entry": ENTRY, "evidence": ["pointer_cell"]}
    ]:
        raise AuditError("lv_iter.c no longer has the one-function anchor")

    functions = report["ghidra_correlation"]["functions"]
    mapped = [item for item in functions if item["entry"] == ENTRY]
    if len(mapped) != 1 or mapped[0]["body_start"] != ENTRY or mapped[0]["body_end_inclusive"] != END_EXCLUSIVE - 1:
        raise AuditError("lv_iter_create function boundary changed")

    logs = paths.verify_corpus(corpus_root)
    corpus_text = "\n".join(log.read_text(encoding="utf-8") for log in logs)
    begin = re.escape(
        "OPENCFW_FUNCTION_BEGIN entry=005c3b00 body_start=005c3b00 body_end=005c3bb1"
    )
    block_match = re.search(begin + r"(?P<body>.*?)OPENCFW_FUNCTION_END entry=005c3b00", corpus_text, re.S)
    if block_match is None:
        raise AuditError("authenticated lv_iter_create decompilation block missing")
    body = block_match.group("body")
    pins = {
        "object_allocation_size_28": r"FUN_0044f730\(0x1c\)",
        "malloc_assert_line_65": r"FUN_0044d25c\(3,DAT_005c3bc4,0x41,",
        "allocation_failure_line_68": r"FUN_0044d25c\(3,DAT_005c3bc4,0x44,",
        "context_allocation": r"FUN_0044f730\(param_3\)",
        "context_assert_line_79": r"FUN_0044d25c\(3,DAT_005c3bc4,0x4f,",
        "instance_offset_0": r"\*puVar1 = param_1;",
        "element_size_offset_4": r"puVar1\[1\] = param_2;",
        "context_size_offset_12": r"puVar1\[3\] = param_3;",
        "next_callback_offset_24": r"puVar1\[6\] = param_4;",
        "context_offset_8": r"puVar1\[2\] = uVar2;",
    }
    for label, pattern in pins.items():
        _require_text(body, pattern, label)
    # The closed decompilation corpus contains the definition token once and no
    # direct call token. This is not proof that indirect callers do not exist.
    if len(re.findall(r"FUN_005c3b00\(", corpus_text)) != 1:
        raise AuditError("lv_iter_create direct-call census changed")

    image_data = image.read_bytes()
    span = image_data[ENTRY - paths.LOAD_BASE : END_EXCLUSIVE - paths.LOAD_BASE]
    if len(span) != 178 or _sha256(span) != SPAN_SHA256:
        raise AuditError("lv_iter_create official bytes changed")
    source_data = source.read_bytes()
    if _sha256(source_data) != SOURCE_SHA256 or _git_blob(source_data) != SOURCE_GIT_BLOB:
        raise AuditError("vendored lv_iter.c identity changed")
    source_lines = source_data.decode("utf-8").splitlines()
    expected_lines = {61: "lv_iter_t * lv_iter_create", 64: "lv_malloc_zeroed(sizeof(lv_iter_t))", 65: "LV_ASSERT_MALLOC(iter);", 68: 'LV_LOG_ERROR("Could not allocate memory for iterator")', 79: "LV_ASSERT_MALLOC(iter->context);"}
    for number, fragment in expected_lines.items():
        if fragment not in source_lines[number - 1]:
            raise AuditError(f"vendored lv_iter.c line {number} changed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; production-excluded; no hardware or flash operation",
        "mapping": {
            "function": "lv_iter_create",
            "entry": ENTRY,
            "end_exclusive": END_EXCLUSIVE,
            "size": len(span),
            "sha256": SPAN_SHA256,
            "source": "src/misc/lv_iter.c",
            "source_sha256": SOURCE_SHA256,
            "source_git_blob": SOURCE_GIT_BLOB,
            "retained_path_run": SOURCE_PATH_RUN,
            "pointer_cell": SOURCE_POINTER_CELL,
            "assertion_lines": [65, 68, 79],
            "direct_callers_in_decompiled_corpus": [],
            "behavioral_pins": sorted(pins),
        },
        "confidence": "high-confidence function/source mapping",
        "limitations": [
            "the retained __FILE__ pointer anchors this function only; it does not assign adjacent functions or the whole translation unit",
            "no direct caller appears in the closed decompilation corpus, but indirect or data-driven reachability is not excluded",
            "compiler relocation records and a complete caller boundary are unavailable, so this is not a production source-replacement candidate",
            "the vendored source is the selected official compatibility ceiling, not proof of the exact Even/Ambiq fork checkout",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = analyze(args.ghidra_corpus, args.image, args.source)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        item = result["mapping"]
        print("G2 LVGL function/source mapping")
        print(f"  {item['function']}: 0x{item['entry']:08x}..0x{item['end_exclusive']:08x}")
        print(f"  source: {item['source']} ({item['source_git_blob']})")
        print("  production: excluded (caller/relocation closure incomplete)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
