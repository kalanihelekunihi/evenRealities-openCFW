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
    ROOT / "components/shared/cordio/runtime_cordio_attc_write.c": (
        "0037ba32b3da7a302f5e13acb846cc23a2a239a7702757963db4bc5b53bf269d"
    ),
    ROOT / "components/shared/cordio/runtime_cordio_attc_write.h": (
        "f6053c127877ff7e314a52ed7adbb1d7ed2b76da7bddef671bb5d14ccd27d4f3"
    ),
    MAP: "0d11fec6f719c850df22330ac890593aa6f23c3c1205c6a2237e43bce8d25840",
    ROOT / "tools/manifests/packetcraft-cordio-attc-write-provenance.tsv": (
        "3929610dad817d24ae08a43301c764f400f0e0ad29e5cd1c6c8a0d61d13f1837"
    ),
}
CALLS = {"attcProcPrepWriteRsp": [], "AttcWriteCmd": [0x4C4A60]}
OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
CANDIDATE_SOURCE_PATH = "components/shared/cordio/runtime_cordio_attc_write.c"
CANDIDATE_FUNCTIONS = [
    "open_cfw_cordio_attc_process_prepare_write_response",
    "open_cfw_cordio_attc_write_command",
]
CANDIDATE_METRICS = [(347136, 30, 0), (347168, 114, 2)]


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

    overlay = json.loads(OVERLAY_CONFIG.read_text())
    leaves_by_function = {
        row["function"]: row for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == CANDIDATE_SOURCE_PATH
    }
    if set(leaves_by_function) != set(CANDIDATE_FUNCTIONS):
        raise RuntimeError("attc_write production leaf inventory changed")
    source_hash = PINS[ROOT / CANDIDATE_SOURCE_PATH]
    leaves = []
    for function, metrics in zip(CANDIDATE_FUNCTIONS, CANDIDATE_METRICS):
        leaf = leaves_by_function[function]
        actual = (
            leaf["expected"]["offset"], leaf["expected"]["size"],
            len(leaf["relocations"]),
        )
        if actual != metrics or leaf["source"].get("sha256") != source_hash:
            raise RuntimeError(f"attc_write production leaf changed: {function}")
        leaves.append(leaf)
    sites = {row["name"]: row for row in overlay["patch_sites"]}
    for index, (function, (name, start, end, expected)) in enumerate(
        zip(CANDIDATE_FUNCTIONS, linked), 1
    ):
        site = sites.get(f"replace_cordio_attc_write_{index:02d}")
        if (
            site is None or site.get("runtime_address") != start
            or site.get("target_function") != function
            or site.get("expected_size") != end - start
            or site.get("expected_sha256") != expected
            or function not in overlay["functions"]
        ):
            raise RuntimeError(f"attc_write production route changed: {name}")
    compiled = sum(row["expected"]["size"] for row in leaves)
    alignment = leaves[0]["expected"]["offset"] - 347136
    alignment += sum(
        right["expected"]["offset"]
        - left["expected"]["offset"] - left["expected"]["size"]
        for left, right in zip(leaves, leaves[1:])
    )
    relocations = sum(len(row["relocations"]) for row in leaves)
    if (compiled, alignment, relocations) != (144, 2, 2):
        raise RuntimeError("attc_write production metrics changed")

    build = json.loads(BUILD_REPORT.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    if (
        build["overlay"]["size"] != 404796
        or build["overlay"]["sha256"]
        != "a55b20ca90792f195ef8de456a6cb7d90c831575b9aff147676a716844bfc73d"
        or build["component"]["size"] != 3928192
        or build["component"]["sha256"]
        != "5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73"
        or override["provider"].get("size") != 3928192
        or override["provider"].get("sha256")
        != "5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73"
        or len([
            row for row in override["regions"]
            if row["name"].startswith("cordio_attc_write_")
        ]) != 5
    ):
        raise RuntimeError("attc_write component/manifest ownership changed")
    if (
        PACKAGE.stat().st_size != 4706686
        or sha(PACKAGE.read_bytes())
        != "30afcda8c32cc34fb1a1c12df13aff2f97223e12d74425690e67a6e4d81bfddf"
    ):
        raise RuntimeError("attc_write package changed")
    flash = json.loads(FLASH_PLAN.read_text())
    if (
        FLASH_PLAN.stat().st_size != 4071097
        or sha(FLASH_PLAN.read_bytes())
        != "cf46c2b6e6ed099ce9ef240520be8d81847ae219d52479286a373c326d22da6d"
        or (
            len(flash["flash_regions"]), len(flash["unresolved_flash_regions"]),
            len(flash["container_only_regions"]), len(flash["protected_regions"]),
        ) != (5863, 2, 5, 6)
    ):
        raise RuntimeError("attc_write flash plan changed")

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
        "production": {
            "status": "routed",
            "linked_functions": 2,
            "source_functions": 5,
            "stock_bytes_replaced": 124,
            "source_owned_bytes_added": compiled,
            "compiled_text_bytes": compiled,
            "alignment_bytes": alignment,
            "strict_relocations": relocations,
            "guarded_redirects": 2,
            "source_only_public_helpers": source_only,
            "hardware_validation": (
                "blocked by unavailable authorized responsive G2/ATT peer evidence"
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
        print("Cordio attc_write closed: 2 linked / 3 source-only; 1 BL + 1 stored ingress")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
