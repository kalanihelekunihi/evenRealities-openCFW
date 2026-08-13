#!/usr/bin/env python3
"""Fail-closed lineage and boundary audit for the G2 ring-buffer cluster."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x0043_7FE0

UPSTREAM = {
    "repository": "https://github.com/AndersKaloer/Ring-Buffer.git",
    "license": "MIT",
    "compatible_floor_commit": "cda00e1efb815bad5100757f0d10d117f633ced6",
    "compatible_ceiling_commit": "190e30bebcec22d7311fd941179d70b4f439c441",
    "selected_commit": "190e30bebcec22d7311fd941179d70b4f439c441",
    "selected_tree": "017721c429f238ebd40216c9d832866c5323dfaa",
    "firmware_build_timestamp": "2025-04-28T13:29:15Z",
}

SOURCE = ROOT / "third_party/ring-buffer/ringbuffer.c"
HEADER = ROOT / "third_party/ring-buffer/ringbuffer.h"
PRODUCTION_SOURCE = ROOT / "components/shared/ring_buffer/runtime_ring_buffer.c"
OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE_PIN = (2_202, "c930c1bb55d7efe1116566bacfb00b55ddf031e7df22b22e7138849068819c7f")
HEADER_PIN = (4_446, "065589a731ffa8367ace4a17885968a53f35e265c7d0d45cdddbe3fa09cfa9e9")
PRODUCTION_SOURCE_PIN = (5_290, "7357f1229ccb40cab3e23204ff7e98176d1026c5c86fbabb67a0a5067c8074b2")

SEGMENTS = (
    ("ring_buffer_is_empty", 0x0059_8134, 0x0059_8146, "054058b2601f056cb0155f6c4c0ea651ac4204b6b34d3b8d93eb14a65c817ecd"),
    ("ring_buffer_is_full", 0x0059_8146, 0x0059_8160, "f02a2098edbd8e1bf24b0329641f2c2c392ba51c56e6e7ba87d657d653fd90da"),
    ("ring_buffer_init", 0x0059_8160, 0x0059_818C, "06163a542a026816da10ad0b2e070c8c01d73a5c22d303bd7a00fec20a2a58f9"),
    ("ring_buffer_init_literals", 0x0059_818C, 0x0059_8198, "0077e40ace26b203b787fe72c2fe40dd88bf0a5c305457ead3cb38625961fe3c"),
    ("ring_buffer_queue", 0x0059_8198, 0x0059_81C4, "69bf50226f3a3711cf3f19269efe304fd4602525fedc463c57d0344ff436a3aa"),
    ("ring_buffer_queue_arr", 0x0059_81C4, 0x0059_81E0, "0afdd325440f509dc9855696adb840bcd45d1337781c02d6e57bb206a8278c83"),
    ("ring_buffer_dequeue", 0x0059_81E0, 0x0059_820A, "b0380f2b019ced5407d913c2ea35b2b612e6a02a3ad27be48fd4be21d503798e"),
    ("ring_buffer_dequeue_arr", 0x0059_820A, 0x0059_823C, "543ea89fd124c8341640d02fa349b02b6c0b794e6df129c522123b3a3b998f63"),
)
CLUSTER = (0x0059_8134, 0x0059_823C, 264, "19b070eb57bf11089632a16a58f077f816d3b45502914ab2dc435dbd2b10d009")
FUNCTION_ENTRIES = {start: name for name, start, _end, _digest in SEGMENTS if name != "ring_buffer_init_literals"}
EXPECTED_CALLERS = {
    0x0059_8134: ((0x0059_81E8, "fff7a4ff"), (0x0059_8214, "fff78eff")),
    0x0059_8146: ((0x0059_81A0, "fff7d1ff"),),
    0x0059_8160: ((0x0058_FB62, "08f0fdfa"),),
    0x0059_8198: ((0x0059_81D4, "fff7e0ff"),),
    0x0059_81C4: ((0x0058_FB24, "08f04efb"),),
    0x0059_81E0: ((0x0059_8230, "fff7d6ff"),),
    0x0059_820A: ((0x0058_FB32, "08f06afb"),),
}
ASSERTION = "((buf_size & (buf_size - 1)) == 0) == 1"
SOURCE_PATH = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\ringBuffer\\ringbuffer.c"


class AuditError(RuntimeError):
    """Raised when an authenticated ring-buffer invariant changes."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def c_string(blob: bytes, address: int) -> str:
    offset = address - LOAD_BASE
    end = blob.index(0, offset)
    return blob[offset:end].decode("ascii")


def wide_branch_target(address: int, first: int, second: int, *, link: bool) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    immediate = (
        sign << 24
        | (1 ^ (j1 ^ sign)) << 23
        | (1 ^ (j2 ^ sign)) << 22
        | (first & 0x03FF) << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def scan_callers(blob: bytes) -> dict[int, tuple[tuple[int, str], ...]]:
    found: dict[int, list[tuple[int, str]]] = {entry: [] for entry in FUNCTION_ENTRIES}
    for offset in range(0, len(blob) - 3, 2):
        address = LOAD_BASE + offset
        first, second = struct.unpack_from("<HH", blob, offset)
        target = wide_branch_target(address, first, second, link=True)
        if target in found:
            found[target].append((address, blob[offset:offset + 4].hex()))
    return {entry: tuple(records) for entry, records in found.items()}


def analyze(image: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official Apollo-main image identity mismatch")

    source = SOURCE.read_bytes()
    header = HEADER.read_bytes()
    if (len(source), sha256(source)) != SOURCE_PIN:
        raise AuditError("selected ringbuffer.c snapshot changed")
    if (len(header), sha256(header)) != HEADER_PIN:
        raise AuditError("selected ringbuffer.h snapshot changed")
    production_source = PRODUCTION_SOURCE.read_bytes()
    if (len(production_source), sha256(production_source)) != PRODUCTION_SOURCE_PIN:
        raise AuditError("production ring-buffer adaptation changed")

    segments = []
    for name, start, end, digest in SEGMENTS:
        body = image_slice(blob, start, end)
        if sha256(body) != digest:
            raise AuditError(f"{name} stock boundary changed")
        segments.append({"name": name, "start": start, "end": end, "size": len(body), "sha256": digest})
    start, end, size, digest = CLUSTER
    cluster = image_slice(blob, start, end)
    if len(cluster) != size or sha256(cluster) != digest:
        raise AuditError("contiguous ring-buffer cluster changed")

    callers = scan_callers(blob)
    if callers != EXPECTED_CALLERS:
        raise AuditError(f"ring-buffer caller topology changed: {callers!r}")

    path_pointer, assertion_pointer = struct.unpack("<II", image_slice(blob, 0x0059_8190, 0x0059_8198))
    if c_string(blob, path_pointer) != SOURCE_PATH or c_string(blob, assertion_pointer) != ASSERTION:
        raise AuditError("ring-buffer source/assertion fingerprint changed")
    assert_call = image_slice(blob, 0x0059_8174, 0x0059_8178)
    first, second = struct.unpack("<HH", assert_call)
    if wide_branch_target(0x0059_8174, first, second, link=True) != 0x004D_09B4:
        raise AuditError("ring-buffer assertion provider changed")

    required_source_tokens = (
        b"RING_BUFFER_ASSERT(RING_BUFFER_IS_POWER_OF_TWO(buf_size) == 1)",
        b"buffer->buffer_mask = buf_size - 1",
        b"ring_buffer_queue(buffer, data[i])",
        b"ring_buffer_dequeue(buffer, data_ptr)",
    )
    if any(token not in source for token in required_source_tokens):
        raise AuditError("selected upstream source no longer carries the stock fingerprint")

    production_functions = tuple(
        f"open_cfw_{name}" for name in FUNCTION_ENTRIES.values()
    )
    overlay = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
    configured_functions = {
        record["function"] for record in overlay["relocated_leaves"]
        if record.get("function") in production_functions
    }
    configured_patches = {
        record["target_function"] for record in overlay["patch_sites"]
        if record.get("target_function") in production_functions
    }
    if configured_functions != set(production_functions):
        raise AuditError("production relocated-leaf closure changed")
    if configured_patches != set(production_functions):
        raise AuditError("production entry-redirect closure changed")

    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    manifest_regions = manifest["component_overrides"]["apollo_main"]["regions"]
    ring_regions = [record for record in manifest_regions if record["name"].startswith("apollo_ring_buffer_")]
    if len(ring_regions) != 9:
        raise AuditError("production manifest ring-buffer closure changed")
    if sum(record["size"] for record in ring_regions if record["address_status"] == "source_compiled") != 248:
        raise AuditError("production source-owned ring-buffer byte count changed")
    if sum(record["size"] for record in ring_regions if record["address_status"] == "generated_alignment") != 4:
        raise AuditError("production ring-buffer alignment byte count changed")
    stock_replacements = [
        record for record in manifest_regions
        if record["name"].startswith("ring_buffer_")
        and record["name"].endswith("_source_replacement")
    ]
    if len(stock_replacements) != 7 or sum(record["size"] for record in stock_replacements) != 252:
        raise AuditError("production stock-entry ownership closure changed")

    return {
        "identity": {
            "classification": "definitive AndersKaloer/Ring-Buffer dynamic-buffer lineage",
            "stock_cluster": {"start": start, "end": end, "size": size, "sha256": digest},
            "source_path": SOURCE_PATH,
            "assertion": ASSERTION,
        },
        "upstream": {
            **UPSTREAM,
            "exact_vendor_checkout_proven": False,
            "selection_reason": "newest source-equivalent upstream commit available at the firmware build timestamp",
            "why_not_exact": "commits inside the compatible interval change no retained behavior distinguishable in this binary",
        },
        "abi": {
            "object_size": 16,
            "fields": {"buffer": 0, "buffer_mask": 4, "tail_index": 8, "head_index": 12},
            "capacity": "buf_size - 1",
            "full_policy": "overwrite oldest byte",
        },
        "segments": segments,
        "callers": {f"0x{entry:08X}": records for entry, records in callers.items()},
        "recovery": {
            "identification_percent": 100,
            "boundary_percent": 100,
            "source_snapshot_percent": 100,
            "production_integration_percent": 100,
            "stock_executable_bytes": 250,
            "stock_literal_alignment_bytes": 14,
            "production_source_bytes": 248,
            "production_generated_alignment_bytes": 4,
            "production_generated_entry_replacement_bytes": 252,
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("G2 ring-buffer audit: PASS")
        print(json.dumps(report["recovery"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
