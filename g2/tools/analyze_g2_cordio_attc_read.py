#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio ATT client read unit."""

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
sys.path.insert(0, str(ROOT / "tools"))
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
MAP = ROOT / "tools/manifests/packetcraft-cordio-attc-read-function-map.tsv"
PINS = {
    ROOT / "components/shared/cordio/runtime_cordio_attc_read.c": (
        "197421e5d0c6c8872889fc9707d5e4bf51853e0927af8dad6cd454c637448b87"
    ),
    ROOT / "components/shared/cordio/runtime_cordio_attc_read.h": (
        "85a626ebe42abad6fc7eea0223a357edd7bba0a97448e101792391cc5749283d"
    ),
    MAP: "31879310a701f02ae0e7978970baf2caeb7c90bf1d7c937cdf5b61b55c3ecb0f",
    ROOT / "tools/manifests/packetcraft-cordio-attc-read-provenance.tsv": (
        "4507932bdb8da38bef00e93ee9f37500a982655f40f8d58cca01bf14d5c6f64f"
    ),
}
CALLS = {
    "attcProcFindByTypeRsp": [],
    "attcProcReadLongRsp": [],
    "AttcFindByTypeValueReq": [0x56BF2C],
    "AttcReadByTypeReq": [0x533840, 0x56C1D4],
}
OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
CANDIDATE_SOURCE_PATH = "components/shared/cordio/runtime_cordio_attc_read.c"
CANDIDATE_FUNCTIONS = [
    "open_cfw_cordio_attc_process_find_by_type_response",
    "open_cfw_cordio_attc_process_read_long_response",
    "open_cfw_cordio_attc_find_by_type_value_request",
    "open_cfw_cordio_attc_read_by_type_request",
]
CANDIDATE_METRICS = [
    (347284, 136, 0), (347420, 40, 0),
    (347460, 140, 2), (347600, 124, 2),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE : end - BASE]


def load_decoder():
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("attc_read_thumb", path)
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
        "AttcReadLongReq",
        "AttcReadMultipleReq",
        "AttcReadByGroupTypeReq",
    ]
    if len(linked) != 4 or source_only != expected_source_only:
        raise RuntimeError("source inventory changed")
    bodies = []
    for name, start, end, expected in linked:
        body = image_slice(blob, start, end)
        if len(body) != end - start or sha(body) != expected:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != "fadfa806bdf0bfa8a4a02254ca0661f4f2ec3a709a0bbb28471feed859aa554b":
        raise RuntimeError("body concatenation changed")
    if sha(image_slice(blob, 0x56C3B0, 0x56C550)) != "d3286218cfb6d8bfe2a4a3a783073b4d98f67d5c93e91361c313013543a64495":
        raise RuntimeError("physical object changed")
    if image_slice(blob, 0x56C54E, 0x56C550) != b"\0\0":
        raise RuntimeError("terminal alignment changed")

    response_cells = {
        0x700970: 0x56C3B1,
        0x70097C: 0x56C455,
    }
    for address, expected in response_cells.items():
        if struct.unpack_from("<I", blob, address - BASE)[0] != expected:
            raise RuntimeError(f"response-table cell changed at {address:#x}")

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
    if stored != sorted(response_cells.items()):
        raise RuntimeError("stored entry-pointer closure changed")
    if inside:
        raise RuntimeError("stored strict-interior pointer found")

    overlay = json.loads(OVERLAY_CONFIG.read_text())
    leaves_by_function = {
        row["function"]: row for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == CANDIDATE_SOURCE_PATH
    }
    if set(leaves_by_function) != set(CANDIDATE_FUNCTIONS):
        raise RuntimeError("attc_read production leaf inventory changed")
    source_hash = PINS[ROOT / CANDIDATE_SOURCE_PATH]
    leaves = []
    for function, metrics in zip(CANDIDATE_FUNCTIONS, CANDIDATE_METRICS):
        leaf = leaves_by_function[function]
        actual = (
            leaf["expected"]["offset"], leaf["expected"]["size"],
            len(leaf["relocations"]),
        )
        if actual != metrics or leaf["source"].get("sha256") != source_hash:
            raise RuntimeError(f"attc_read production leaf changed: {function}")
        leaves.append(leaf)
    sites = {row["name"]: row for row in overlay["patch_sites"]}
    for index, (function, (name, start, end, expected)) in enumerate(
        zip(CANDIDATE_FUNCTIONS, linked), 1
    ):
        site = sites.get(f"replace_cordio_attc_read_{index:02d}")
        if (
            site is None or site.get("runtime_address") != start
            or site.get("target_function") != function
            or site.get("expected_size") != end - start
            or site.get("expected_sha256") != expected
            or function not in overlay["functions"]
        ):
            raise RuntimeError(f"attc_read production route changed: {name}")
    compiled = sum(row["expected"]["size"] for row in leaves)
    alignment = leaves[0]["expected"]["offset"] - 347282
    alignment += sum(
        right["expected"]["offset"]
        - left["expected"]["offset"] - left["expected"]["size"]
        for left, right in zip(leaves, leaves[1:])
    )
    relocations = sum(len(row["relocations"]) for row in leaves)
    if (compiled, alignment, relocations) != (440, 2, 4):
        raise RuntimeError("attc_read production metrics changed")

    build = json.loads(BUILD_REPORT.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    validate_apollo_main_artifacts(ROOT, RuntimeError, "ATT client read")
    if len([
        row for row in override["regions"]
        if row["name"].startswith("cordio_attc_read_")
    ]) != 9:
        raise RuntimeError("attc_read component/manifest ownership changed")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x56C3B0,
            "end_exclusive": 0x56C550,
            "physical_bytes": 416,
            "linked_function_count": 4,
            "linked_function_bytes": 414,
            "source_inventory_functions": 7,
            "source_only_functions": source_only,
            "direct_bl_ingress_sites": 3,
            "registered_function_pointers": 2,
            "strict_interior_pointers": 0,
            "strict_interior_branches": 0,
        },
        "architecture": {
            "response_table": 0x700964,
            "response_table_slots": [3, 6],
            "bearer_aware_read_long": True,
            "att_bearer_slot_from_ccb": True,
            "retained_source_path": None,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c and official AmbiqSuite R4.4.1 import",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "bd2afa58c92129b5c5c93df31cec5f6c7c52ba87",
            "selected_sha256": "59d30e36b1c9acb9af1659f75af7e8151ef8329772f0de20fb9f9dc6e006517f",
            "license": "Apache-2.0",
            "independent_release_discriminator": True,
            "historical_generating_commit_resolved": False,
            "discriminator": "per-bearer Read Long MTU access introduced with the r20 EATT architecture",
        },
        "production": {
            "status": "routed",
            "linked_functions": 4,
            "source_functions": 7,
            "stock_bytes_replaced": 414,
            "source_owned_bytes_added": compiled,
            "compiled_text_bytes": compiled,
            "alignment_bytes": alignment,
            "strict_relocations": relocations,
            "guarded_redirects": 4,
            "source_only_public_helpers": source_only,
            "truncated_pair_guard": True,
            "hardware_validation": (
                "deferred by project direction; future qualification requires authorized responsive G2/ATT peer evidence"
            ),
        },
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
        print("Cordio attc_read closed: 4 linked / 3 source-only; 3 BL + 2 stored ingress")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
