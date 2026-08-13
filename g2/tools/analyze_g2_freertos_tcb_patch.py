#!/usr/bin/env python3
"""Authenticate the minimal G2 FreeRTOS V10.5.1 TCB/tasks delta."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from capstone import CS_ARCH_ARM, CS_MODE_MCLASS, CS_MODE_THUMB, Cs
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit("capstone is required for the G2 TCB audit") from exc


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10" /
    "ota_s200_firmware_ota.bin"
)
DEFAULT_PATCH = (
    ROOT / "components" / "shared" / "freertos" /
    "g2-tcb-v10.5.1.patch"
)
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_HEADER = (
    ROOT / "third_party" / "freertos-kernel" / "include" / "FreeRTOS.h"
)

PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
PREAMBLE = 32
APPLICATION_BASE = 0x0043_8000
UPSTREAM_COMMIT = "def7d2df2b0506d3d249334974f51e427c17a41c"
UPSTREAM_TREE = "7496dfa815c3cea2f45a090c6e92d113f494b930"
TASKS_SIZE = 223_695
TASKS_SHA256 = "14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463"
HEADER_SIZE = 51_577
HEADER_SHA256 = "03e9c94aba57e3cf7f4f73bc2d3eb4a96ae38f3425eedb5450622ca286475a0b"


@dataclass(frozen=True)
class Span:
    name: str
    start: int
    end: int
    sha256: str


SPANS = (
    Span(
        "xTaskCreateStatic", 0x0045_4820, 0x0045_48BA,
        "21c10ddaf25950d84acbcf302f2de18d3471dd5321c4cd7aa50dcc8a6f29debe",
    ),
    Span(
        "xTaskCreate", 0x0045_48BA, 0x0045_4938,
        "d4210ea6c22d8fb0aee4d89d3a1666874a489e77516041d6946bef9a05058b21",
    ),
    Span(
        "prvInitialiseNewTask", 0x0045_4938, 0x0045_49FC,
        "54a87da84dbcdf7871563962b44490d635a2a924225fed68b99ccce811b397b2",
    ),
    Span(
        "prvAddNewTaskToReadyList", 0x0045_49FC, 0x0045_4AAE,
        "4e765b4faa584167eb8aa1e91ab46fb3383dbfb24ebe4adbd5a4909943706ff4",
    ),
)

PATCH_MARKERS = (
    "diff --git a/tasks.c b/tasks.c",
    "diff --git a/include/FreeRTOS.h b/include/FreeRTOS.h",
    "+    uint32_t ulG2StackDepth;",
    "+    pxNewTCB->ulG2StackDepth = ulStackDepth;",
    "+    uint32_t ulDummyG2StackDepth;",
    "The original vendor identifier is not observable in the binary.",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def app_slice(application: bytes, start: int, end: int) -> bytes:
    first = start - APPLICATION_BASE
    last = end - APPLICATION_BASE
    if first < 0 or first >= last or last > len(application):
        raise AssertionError(f"span outside image: 0x{start:08X}..0x{end:08X}")
    return application[first:last]


def instructions(application: bytes, span: Span) -> tuple[tuple[int, str], ...]:
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    return tuple(
        (item.address, f"{item.mnemonic} {item.op_str}".strip().lower())
        for item in decoder.disasm(app_slice(application, span.start, span.end), span.start)
    )


def require_fragment(items: tuple[tuple[int, str], ...], fragment: str) -> int:
    matches = [address for address, text in items if fragment in text]
    if not matches:
        raise AssertionError(f"missing instruction signature: {fragment}")
    return matches[0]


def verify_sources(patch_path: Path) -> dict[str, object]:
    tasks = UPSTREAM_TASKS.read_bytes()
    header = UPSTREAM_HEADER.read_bytes()
    if len(tasks) != TASKS_SIZE or sha256(tasks) != TASKS_SHA256:
        raise AssertionError("authenticated V10.5.1 tasks.c changed")
    if len(header) != HEADER_SIZE or sha256(header) != HEADER_SHA256:
        raise AssertionError("authenticated V10.5.1 FreeRTOS.h changed")

    pristine = (tasks + header).decode("utf-8")
    for forbidden in ("ulG2StackDepth", "ulDummyG2StackDepth"):
        if forbidden in pristine:
            raise AssertionError(f"vendor field unexpectedly exists upstream: {forbidden}")

    patch = patch_path.read_text(encoding="utf-8")
    for marker in PATCH_MARKERS:
        if patch.count(marker) != 1:
            raise AssertionError(f"patch marker is not unique: {marker}")
    if patch.count("uint32_t ulG2StackDepth") != 1:
        raise AssertionError("patch adds more than one concrete TCB field")
    return {
        "commit": UPSTREAM_COMMIT,
        "tree": UPSTREAM_TREE,
        "tasks_sha256": TASKS_SHA256,
        "header_sha256": HEADER_SHA256,
        "patch_size": patch_path.stat().st_size,
        "patch_sha256": sha256(patch_path.read_bytes()),
    }


def verify_binary(image_path: Path) -> dict[str, object]:
    package = image_path.read_bytes()
    if len(package) != PACKAGE_SIZE:
        raise AssertionError(
            f"package size mismatch: expected {PACKAGE_SIZE}, got {len(package)}"
        )
    package_digest = sha256(package)
    if package_digest != PACKAGE_SHA256:
        raise AssertionError("official package SHA-256 mismatch")
    application = package[PREAMBLE:]

    decoded: dict[str, tuple[tuple[int, str], ...]] = {}
    for span in SPANS:
        body = app_slice(application, span.start, span.end)
        if sha256(body) != span.sha256:
            raise AssertionError(f"{span.name} stock span changed")
        decoded[span.name] = instructions(application, span)

    static = decoded["xTaskCreateStatic"]
    require_fragment(static, "movs r0, #0x70")
    require_fragment(static, "cmp r0, #0x70")
    require_fragment(static, "movs r1, #0x70")
    require_fragment(static, "str r4, [r5, #0x30]")
    require_fragment(static, "strb.w r0, [r5, #0x6d]")

    dynamic = decoded["xTaskCreate"]
    if sum("movs r0, #0x70" in text for _, text in dynamic) != 1:
        raise AssertionError("dynamic creator TCB allocation size changed")
    require_fragment(dynamic, "movs r1, #0x70")
    require_fragment(dynamic, "str r5, [r4, #0x30]")
    require_fragment(dynamic, "strb.w r0, [r4, #0x6d]")

    initialise = decoded["prvInitialiseNewTask"]
    depth_store = require_fragment(initialise, "str.w sb, [r6, #0x54]")
    name_store = require_fragment(initialise, "strb.w r0, [r2, #0x34]")
    name_terminator = require_fragment(initialise, "strb.w r0, [r6, #0x53]")
    base_priority = require_fragment(initialise, "str.w sb, [r6, #0x60]")
    if not depth_store < name_store < name_terminator < base_priority:
        raise AssertionError("task initializer field-write order changed")
    require_fragment(initialise, "cmp r1, #0x20")
    require_fragment(initialise, "cmp.w sb, #0x38")

    ready = decoded["prvAddNewTaskToReadyList"]
    require_fragment(ready, "str r0, [r4, #0x58]")

    return {
        "package_size": len(package),
        "package_sha256": package_digest,
        "stock_spans": [
            {
                "name": span.name,
                "start": span.start,
                "end": span.end,
                "size": span.end - span.start,
                "sha256": span.sha256,
            }
            for span in SPANS
        ],
        "layout": {
            "tcb_size": 0x70,
            "name_offset": 0x34,
            "name_size": 0x20,
            "stack_depth_offset": 0x54,
            "trace_offsets": [0x58, 0x5C],
            "mutex_offsets": [0x60, 0x64],
            "notification_offsets": [0x68, 0x6C],
            "allocation_offset": 0x6D,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--patch", type=Path, default=DEFAULT_PATCH)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = {
        "schema_version": 1,
        "classification": "vendor-derived-minimal-patch",
        "upstream": verify_sources(args.patch),
        "stock": verify_binary(args.image),
        "unknowns": [
            "original vendor field identifier and comments",
            "original vendor patch commit or private repository identity",
        ],
    }
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print(f"PASS package: {args.image}")
        print(f"PASS upstream FreeRTOS V10.5.1: {UPSTREAM_COMMIT}")
        print(f"PASS reviewed task spans: {len(SPANS)}")
        print("PASS TCB delta: one 32-bit stack-depth word at +0x54")
        print("PASS patched layout: 0x70 bytes; later fields shifted by four")
        print("BOUNDED UNKNOWN: original vendor field name and patch commit")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, UnicodeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
