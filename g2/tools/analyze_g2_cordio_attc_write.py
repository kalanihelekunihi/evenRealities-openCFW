#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio ATT client write unit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
MAP = ROOT / "tools/manifests/packetcraft-cordio-attc-write-function-map.tsv"
PINS = {
    MAP: "0d11fec6f719c850df22330ac890593aa6f23c3c1205c6a2237e43bce8d25840",
    ROOT / "tools/manifests/packetcraft-cordio-attc-write-provenance.tsv": (
        "3929610dad817d24ae08a43301c764f400f0e0ad29e5cd1c6c8a0d61d13f1837"
    ),
}
CALLS = {"attcProcPrepWriteRsp": [], "AttcWriteCmd": [0x4C4A60]}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE : end - BASE]


def load_decoder():
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("attc_write_thumb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_rows():
    linked, source_only = [], []
    with MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] == "linked":
                linked.append(
                    (
                        row["function"],
                        int(row["stock_start"], 0),
                        int(row["stock_end_exclusive"], 0),
                        row["stock_sha256"],
                    )
                )
            else:
                source_only.append(row["function"])
    return linked, source_only


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise RuntimeError("official image changed")
    for path, expected in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != expected:
            raise RuntimeError(f"pinned input changed: {path}")

    linked, source_only = load_rows()
    expected_source_only = [
        "attcPrepWriteAllocMsg",
        "AttcPrepareWriteReq",
        "AttcExecuteWriteReq",
    ]
    if len(linked) != 2 or source_only != expected_source_only:
        raise RuntimeError("source inventory changed")
    bodies = []
    for name, start, end, expected in linked:
        body = image_slice(blob, start, end)
        if len(body) != end - start or sha(body) != expected:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    expected_physical = "72a705a886cf5ec553b89b61f9480e21cc672b35676cbac9fbd9cf2f2ac4adc9"
    if sha(b"".join(bodies)) != expected_physical:
        raise RuntimeError("body concatenation changed")
    if sha(image_slice(blob, 0x539DCC, 0x539E48)) != expected_physical:
        raise RuntimeError("physical object changed")

    response_cell = struct.unpack_from("<I", blob, 0x700990 - BASE)[0]
    if response_cell != 0x539DCD:
        raise RuntimeError("prepare-write response-table cell changed")

    decoder = load_decoder()
    starts = {start: name for name, start, _, _ in linked}
    interiors = set()
    for _, start, end, _ in linked:
        interiors.update(range(start + 2, end, 2))
    calls = {name: [] for name, _, _, _ in linked}
    interior_branches = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            calls[starts[target]].append(address)
        elif target in interiors:
            interior_branches.append((address, target))
    if calls != CALLS:
        raise RuntimeError("direct caller closure changed")
    if interior_branches:
        raise RuntimeError("direct branch to strict interior found")

    stored, inside = [], []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if not value & 1:
            continue
        target = value & ~1
        if target in starts:
            stored.append((BASE + offset, value))
        elif target in interiors:
            inside.append((BASE + offset, value))
    if stored != [(0x700990, 0x539DCD)]:
        raise RuntimeError("stored entry-pointer closure changed")
    if inside:
        raise RuntimeError("stored strict-interior pointer found")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x539DCC,
            "end_exclusive": 0x539E48,
            "physical_bytes": 124,
            "linked_function_count": 2,
            "linked_function_bytes": 124,
            "source_inventory_functions": 5,
            "source_only_functions": source_only,
            "direct_bl_ingress_sites": 1,
            "registered_function_pointers": 1,
            "strict_interior_pointers": 0,
            "strict_interior_branches": 0,
        },
        "architecture": {
            "response_table": 0x700964,
            "prepare_write_response_slot": 11,
            "retained_write_command_opcode": 0x52,
            "retained_source_path": None,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c and official AmbiqSuite R4.4.1 import",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "7602baa5ffa944a96757a9f36f5ee517aa4754fd",
            "selected_sha256": "def6d08036fdaed16a97483858ef8f37c3a49f114122aad0dcffd4ba41c8688e",
            "license": "Apache-2.0",
            "independent_release_discriminator": False,
            "historical_generating_commit_resolved": False,
            "qualification": "both linked bodies are source-identical in r19 and r20; r20 selection follows the independently proven ATT architecture",
        },
        "production": {"stock_bytes_replaced": 0, "source_owned_bytes_added": 0},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Cordio attc_write closed: 2 linked / 3 source-only; 1 BL + 1 stored ingress")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
