#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio legacy-slave connection unit."""
from __future__ import annotations

import argparse
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
CONFIG=ROOT/"components/apollo_main/core_overlay/overlay.json";REPORT=ROOT/"components/apollo_main/core_overlay/build/build-report.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json"
SOURCE=ROOT/"components/shared/cordio/runtime_cordio_dm_conn_slave_leg.c";HEADER=ROOT/"components/shared/cordio/runtime_cordio_dm_conn_slave_leg.h";TEST=ROOT/"tests/test_runtime_cordio_dm_conn_slave_leg.py"
PACKAGE=ROOT/"build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin";FLASH_PLAN=ROOT/"build/source/flash-plan.json"
SOURCE_PIN=(3072,"c77284211d2c184be3f612643c0afa2ef9468507ee9e0141d7766f86a1678510");HEADER_PIN=(1498,"e81657bbc8b10ca9d4cfb3be2398889617c04d1c1819c5e494aea1c8db658921");TEST_PIN=(2713,"de8e38f0e9ceea8adba98fe02b3c5f05f471ca4738ef2871b81c9fc0002db95a")
PINS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-slave-leg-function-map.tsv": "5ae3859a539db7e87b26ad1467155caafcc37be93794830ea374cb932ef3fbfe",
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-slave-leg-provenance.tsv": "cb15fde8ff1a740a40823ed0deb7d8c37ed1ac9c082beac4d3e8a4232d3971e2",
}
FUNCTIONS = {
    "dmConnSmActAccept": (0x536AC8, 0x536ADC, "cb4223a6924447c1b017488ed22ef546d0327311d2b68d2f24f37b8ebb06da65"),
    "dmConnSmActCancelAccept": (0x536ADC, 0x536AF0, "0c6f175468ec0e5752c2c9f3b971b23a79879b4034a068757491cd80ecdfe5bc"),
    "dmConnSmActConnAccepted": (0x536AF0, 0x536B04, "04c00827dc49b82195de2a684b9ad9f59c87cac7cf391a97fe6f6e405a4660b0"),
    "dmConnSmActAcceptFailed": (0x536B04, 0x536B18, "ef7b2a173f816f3056b5a9c9d948c7ace0f94be5116c08e243289ddbbcd7fbbe"),
    "DmConnSlaveInit": (0x536B18, 0x536B30, "61d14680fb2e659aceeeba2a4ff3ec60d01b9922a55c4bd2b3fd64caf2f36869"),
}
CALLERS = {
    "dmConnSmActAccept": [],
    "dmConnSmActCancelAccept": [],
    "dmConnSmActConnAccepted": [],
    "dmConnSmActAcceptFailed": [],
    "DmConnSlaveInit": [0x4B8022],
}
PRODUCTION_FUNCTIONS=["open_cfw_cordio_dm_connection_slave_legacy_action_accept","open_cfw_cordio_dm_connection_slave_legacy_action_cancel","open_cfw_cordio_dm_connection_slave_legacy_action_accepted","open_cfw_cordio_dm_connection_slave_legacy_action_failed","open_cfw_cordio_dm_connection_slave_legacy_initialize"]
PRODUCTION_LEAVES=[(290020,24,1,"e47951bcf779541bf90850cf0f78dcf54bd68b392571fcaf5c2a77d8fbb48301"),(290044,30,2,"204d4784283800fa63828277d5a3e151030a03618648517a6a11e178249b7a38"),(290076,30,2,"1f01f2023536cc510ff97582debe15003589dffb735f3875c27f855390aa7c3c"),(290108,30,2,"1f611e69b2d23be4c767280bee7bbacdfb6b7281c6dc057be42e3deba9f358e4"),(290140,42,2,"1611ed46ff3abd9e71e2f5fe671d770a7b7634cefebc785a85f72d919661f6c2")]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sl(image: bytes, start: int, end: int) -> bytes:
    return image[start - BASE : end - BASE]


def decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_conn_slave_leg_thumb", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def verify_file(path,expected,label):
    data=path.read_bytes()
    if (len(data),sha(data))!=expected: raise RuntimeError(f"{label} changed")

def verify_production():
    verify_file(SOURCE,SOURCE_PIN,"slave-leg source");verify_file(HEADER,HEADER_PIN,"slave-leg header");verify_file(TEST,TEST_PIN,"slave-leg test")
    report=json.loads(REPORT.read_text());config=json.loads(CONFIG.read_text());manifest=json.loads(MANIFEST.read_text())
    leaves=sorted([r for r in report["relocated_leaves"] if r.get("source",{}).get("path","").endswith(SOURCE.name)],key=lambda r:r["pins"]["offset"])
    if len(leaves)!=5: raise RuntimeError("slave-leg leaf count changed")
    for row,function,expected in zip(leaves,PRODUCTION_FUNCTIONS,PRODUCTION_LEAVES):
        observed=(row["pins"]["offset"],row["extraction"]["size"],row["extraction"]["relocation_count"],row["extraction"]["sha256"])
        if row["extraction"]["function"]!=function or observed!=expected: raise RuntimeError(f"slave-leg leaf changed: {function}")
    sites={r["name"]:r for r in config["patch_sites"] if r["name"].startswith("replace_cordio_dm_conn_slave_leg_")}
    for index,((name,(start,end,digest)),function) in enumerate(zip(FUNCTIONS.items(),PRODUCTION_FUNCTIONS),1):
        site=sites.get(f"replace_cordio_dm_conn_slave_leg_{index:02d}")
        if site is None or site["runtime_address"]!=start or site["expected_size"]!=end-start or site["expected_sha256"]!=digest or site["target_function"]!=function or site["branch"]!="b_w": raise RuntimeError(f"slave-leg route changed: {name}")
    override=manifest["component_overrides"]["apollo_main"];regions=[r for r in override["regions"] if r["name"].startswith("cordio_dm_conn_slave_leg_")]
    validate_apollo_main_artifacts(ROOT,RuntimeError,"Cordio legacy connection slave")
    if len(regions)!=14: raise RuntimeError("slave-leg ownership changed")
    flash=json.loads(FLASH_PLAN.read_text());counts=tuple(len(flash[k]) for k in ("flash_regions","unresolved_flash_regions","container_only_regions","protected_regions"))
    return {"status":"production-routed","redirected_stock_functions":5,"redirected_stock_bytes":104,"source_owned_bytes_added":156,"alignment_bytes_added":8,"strict_relocations":9,"manifest_regions":14,"flash_plan_counts":counts}


def analyze(image_path: Path = IMAGE) -> dict:
    image = image_path.read_bytes()
    if len(image) != IMAGE_BYTES or sha(image) != IMAGE_SHA:
        raise RuntimeError("official image changed")
    for path, expected in PINS.items():
        if sha(path.read_bytes()) != expected:
            raise RuntimeError(f"pinned input changed: {path}")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        body = sl(image, start, end)
        if sha(body) != expected:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != "119be41d332181caba2d11376872ede47b301b03fef691017bcf459fa37367d9":
        raise RuntimeError("body concatenation changed")
    if sha(sl(image, 0x536AC8, 0x536B40)) != "4a261efbbef393ad9bb9c28d0ad1060ef7c5342cdd2cff83e38e469f6bc2a109":
        raise RuntimeError("physical interval changed")

    tail = sl(image, 0x536B30, 0x536B40)
    expected_tail = [0x00785BE0, 0x20073FE4, 0x0078D42C, 0x20073FD8]
    if sha(tail) != "e0bda53e850e4ba4103f77356eb37065685a08716f011302ce9aa5690b7c7ec4" or list(struct.unpack("<4I", tail)) != expected_tail:
        raise RuntimeError("literal tail changed")
    main_table = sl(image, 0x785BE0, 0x785BF0)
    update_table = sl(image, 0x78D42C, 0x78D434)
    if sha(main_table) != "0df7cb569a3d117fcad9b9d281d35b23a964671567f967c48d7a8195d03432d6" or list(struct.unpack("<4I", main_table)) != [0x536AC9, 0x536ADD, 0x536AF1, 0x536B05]:
        raise RuntimeError("slave action table changed")
    if sha(update_table) != "0de23740d07fc7a7016ee4f748097a49f130a151ea140b24d628accbbbb790b1" or list(struct.unpack("<2I", update_table)) != [0x56E527, 0x56E565]:
        raise RuntimeError("slave update table changed")

    thumb = decoder()
    starts = {start: name for name, (start, _, _) in FUNCTIONS.items()}
    calls = {name: [] for name in FUNCTIONS}
    for address in range(BASE, BASE + len(image) - 3, 2):
        target = thumb._thumb_bl_target(image, address)
        if target in starts:
            calls[starts[target]].append(address)
    if calls != CALLERS:
        raise RuntimeError("direct caller closure changed")

    interiors = set()
    for start, end, _ in FUNCTIONS.values():
        interiors.update(range(start + 2, end, 2))
    entries = []
    inside = []
    for offset in range(len(image) - 3):
        value = struct.unpack_from("<I", image, offset)[0]
        target = value & ~1
        if target in starts:
            entries.append((BASE + offset, value))
        elif target in interiors:
            inside.append((BASE + offset, value))
    expected_entries = [(0x785BE0, 0x536AC9), (0x785BE4, 0x536ADD), (0x785BE8, 0x536AF1), (0x785BEC, 0x536B05)]
    if entries != expected_entries or inside:
        raise RuntimeError("stored/interior ingress changed")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x536AC8,
            "end_exclusive": 0x536B40,
            "physical_bytes": 120,
            "linked_function_count": 5,
            "linked_function_bytes": 104,
            "source_inventory_functions": 5,
            "source_only_functions": [],
            "direct_bl_ingress_sites": 1,
            "registered_function_pointers": 4,
            "strict_interior_pointers": 0,
        },
        "architecture": {
            "main_action_entries": 4,
            "update_action_entries": 2,
            "separate_update_table": True,
            "task_locked_init": True,
            "action_set": "slave",
        },
        "lineage": {
            "selected_blob": "d714da9f52fc08aa963a280dcdaafda1eff2eb39",
            "selected_sha256": "3bfa84746595aee9bd692db41a0df930b2ec1a4c59adbff4c62cc82b0804eef7",
            "license": "Apache-2.0",
            "historical_generating_commit_resolved": False,
        },
        "build_readiness": {
            "status": "target-compiled",
            "profiles": 6,
        },
        "production": verify_production(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else "Cordio dm_conn_slave_leg closed: 5 linked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
