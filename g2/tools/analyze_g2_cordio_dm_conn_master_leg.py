#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio legacy-master connection unit."""
from __future__ import annotations

import argparse
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
CONFIG=ROOT/"components/apollo_main/core_overlay/overlay.json";REPORT=ROOT/"components/apollo_main/core_overlay/build/build-report.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json"
SOURCE=ROOT/"components/shared/cordio/runtime_cordio_dm_conn_master_leg.c";HEADER=ROOT/"components/shared/cordio/runtime_cordio_dm_conn_master_leg.h";TEST=ROOT/"tests/test_runtime_cordio_dm_conn_master_leg.py"
PACKAGE=ROOT/"build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin";FLASH_PLAN=ROOT/"build/source/flash-plan.json"
SOURCE_PIN=(3766,"8086127d2ef3c8765c0ceb1be22e56007205df9a40ec512943636304d75b5d39");HEADER_PIN=(2652,"6688956641b5868b23d104eae4423e4e8ccbb16f67156fe3eabf3cce28e7a912");TEST_PIN=(3155,"2ebc3d2c2e818d990851f154d58e7c417d72cd65750e4aba7d3e9bbb8dd129b1")
PRODUCTION_OVERLAY=(404796,"a55b20ca90792f195ef8de456a6cb7d90c831575b9aff147676a716844bfc73d");PRODUCTION_COMPONENT=(3928192,"5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73")
PRODUCTION_PACKAGE=(4706686,"30afcda8c32cc34fb1a1c12df13aff2f97223e12d74425690e67a6e4d81bfddf");PRODUCTION_FLASH_PLAN=(4071097,"cf46c2b6e6ed099ce9ef240520be8d81847ae219d52479286a373c326d22da6d")
PINS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-master-leg-function-map.tsv": "201ba73eade03e81f4285f7a2d83431733c9fa5c7e553b92bf39273e41f36d12",
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-master-leg-provenance.tsv": "308f133caf339064a57fa3977a28159fc814340a1d99005b0def5f91d541d044",
}
FUNCTIONS = {
    "dmConnOpen": (0x536A28, 0x536A86, "9975e28872778dd43bb7342475ee4e4001c39c8971eba92782be2fc3ae62652f"),
    "dmConnSmActOpen": (0x536A86, 0x536A98, "0077a67b79a2766d4853a171429aa024dfaaf0c8e36fc08f3a334dd202214e5a"),
    "DmConnMasterInit": (0x536A98, 0x536AB0, "cb3ef0ea7d184dac46ed70aba73c6f212e1308cdee48c567827704f518a9935b"),
}
CALLERS = {
    "dmConnOpen": [0x536A92],
    "dmConnSmActOpen": [],
    "DmConnMasterInit": [0x4B801E],
}
PRODUCTION_FUNCTIONS=["open_cfw_cordio_dm_connection_master_legacy_open","open_cfw_cordio_dm_connection_master_legacy_action_open","open_cfw_cordio_dm_connection_master_legacy_initialize"]
PRODUCTION_LEAVES=[(358320,118,4,"46fc5443dbee05de32ebddaab25a87e3cd82dbd4f45d9d4880716f8587d55e9e"),(358440,20,1,"9767510ca1300835c89614bf670300e58a5bc69ad52443072ff444629539cea6"),(358460,38,2,"f5cc0be544866194a969bf5ed7c703e060086315313beded64a293fe66de7cb3")]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sl(image: bytes, start: int, end: int) -> bytes:
    return image[start - BASE : end - BASE]


def decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_conn_master_leg_thumb", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def verify_file(path,expected,label):
    data=path.read_bytes()
    if (len(data),sha(data))!=expected: raise RuntimeError(f"{label} changed")

def verify_production():
    verify_file(SOURCE,SOURCE_PIN,"master-leg source");verify_file(HEADER,HEADER_PIN,"master-leg header");verify_file(TEST,TEST_PIN,"master-leg test")
    report=json.loads(REPORT.read_text());config=json.loads(CONFIG.read_text());manifest=json.loads(MANIFEST.read_text())
    leaves=sorted([r for r in report["relocated_leaves"] if r.get("source",{}).get("path","").endswith(SOURCE.name)],key=lambda r:r["pins"]["offset"])
    if len(leaves)!=3: raise RuntimeError("master-leg leaf count changed")
    for row,function,expected in zip(leaves,PRODUCTION_FUNCTIONS,PRODUCTION_LEAVES):
        observed=(row["pins"]["offset"],row["extraction"]["size"],row["extraction"]["relocation_count"],row["extraction"]["sha256"])
        if row["extraction"]["function"]!=function or observed!=expected: raise RuntimeError(f"master-leg leaf changed: {function}")
    sites={r["name"]:r for r in config["patch_sites"] if r["name"].startswith("replace_cordio_dm_conn_master_leg_")}
    for index,((name,(start,end,digest)),function) in enumerate(zip(FUNCTIONS.items(),PRODUCTION_FUNCTIONS),1):
        site=sites.get(f"replace_cordio_dm_conn_master_leg_{index:02d}")
        if site is None or site["runtime_address"]!=start or site["expected_size"]!=end-start or site["expected_sha256"]!=digest or site["target_function"]!=function or site["branch"]!="b_w": raise RuntimeError(f"master-leg route changed: {name}")
    override=manifest["component_overrides"]["apollo_main"];regions=[r for r in override["regions"] if r["name"].startswith("cordio_dm_conn_master_leg_")]
    if (report["overlay"]["size"],report["overlay"]["sha256"])!=PRODUCTION_OVERLAY or (report["component"]["size"],report["component"]["sha256"])!=PRODUCTION_COMPONENT or (override["provider"].get("size"),override["provider"].get("sha256"))!=PRODUCTION_COMPONENT or len(regions)!=7: raise RuntimeError("master-leg ownership changed")
    verify_file(PACKAGE,PRODUCTION_PACKAGE,"master-leg package");verify_file(FLASH_PLAN,PRODUCTION_FLASH_PLAN,"master-leg flash plan")
    flash=json.loads(FLASH_PLAN.read_text());counts=tuple(len(flash[k]) for k in ("flash_regions","unresolved_flash_regions","container_only_regions","protected_regions"))
    if counts!=(5576,2,5,6): raise RuntimeError("master-leg flash counts changed")
    return {"status":"production-routed","redirected_stock_functions":3,"redirected_stock_bytes":136,"source_owned_bytes_added":176,"alignment_bytes_added":2,"strict_relocations":7,"manifest_regions":7,"flash_plan_counts":counts}


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
    if sha(b"".join(bodies)) != "d56996db7796f420899a184c131c11eb461464e1d0de0c1075570afc6350b5ec":
        raise RuntimeError("body concatenation changed")
    if sha(sl(image, 0x536A28, 0x536AC8)) != "b68a143267080514feaba249003d8cfd14b41a1c7714ceda7d274ce1cf4ccc30":
        raise RuntimeError("physical interval changed")

    tail = sl(image, 0x536AB0, 0x536AC8)
    expected_tail = [0x20073B78, 0x200712A4, 0x0078D424, 0x20073FE4, 0x0078D41C, 0x20073FD8]
    if sha(tail) != "abfc26714075e468a60f182516a0834d147dbbe9cc488c44eadb51c9066ce04b" or list(struct.unpack("<6I", tail)) != expected_tail:
        raise RuntimeError("literal tail changed")
    main_table = sl(image, 0x78D424, 0x78D42C)
    update_table = sl(image, 0x78D41C, 0x78D424)
    if list(struct.unpack("<2I", main_table)) != [0x536A87, 0x55BC5D]:
        raise RuntimeError("master action table changed")
    if list(struct.unpack("<2I", update_table)) != [0x55BC71, 0x55BC7D]:
        raise RuntimeError("master update table changed")

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
    if entries != [(0x78D424, 0x536A87)] or inside:
        raise RuntimeError("stored/interior ingress changed")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x536A28,
            "end_exclusive": 0x536AC8,
            "physical_bytes": 160,
            "linked_function_count": 3,
            "linked_function_bytes": 136,
            "source_inventory_functions": 3,
            "source_only_functions": [],
            "direct_bl_ingress_sites": 2,
            "registered_function_pointers": 1,
            "strict_interior_pointers": 0,
        },
        "architecture": {
            "main_action_entries": 2,
            "update_action_entries": 2,
            "separate_update_table": True,
            "task_locked_init": True,
            "init_phys": 2,
        },
        "lineage": {
            "selected_blob": "bdf160b21e58d3e2c34901b1829d81d4890d2b56",
            "selected_sha256": "a0ad6fdc783da5e96979b622ab05ecb2a46dc05b6a7eb2ede2740fc50a3fa656",
            "license": "Apache-2.0",
            "historical_generating_commit_resolved": False,
        },
        "build_readiness": {
            "status": "target-compiled",
            "profiles": 4,
        },
        "production": verify_production(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else "Cordio dm_conn_master_leg closed: 3 linked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
