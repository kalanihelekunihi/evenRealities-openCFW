#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio slave connection unit."""
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
SOURCE=ROOT/"components/shared/cordio/runtime_cordio_dm_conn_slave.c";HEADER=ROOT/"components/shared/cordio/runtime_cordio_dm_conn_slave.h";TEST=ROOT/"tests/test_runtime_cordio_dm_conn_slave.py"
PACKAGE=ROOT/"build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin";FLASH_PLAN=ROOT/"build/source/flash-plan.json"
SOURCE_PIN=(4382,"a31c726ba9ae2928718bccc4db7d6bf1c0d8b049b39f075a1e2b902ef611f736");HEADER_PIN=(4015,"486264428d87a2008ae5510e9d5371b9078bb1d614837b98b12fbf8b434f4fc9");TEST_PIN=(3863,"628dbb179808581c676630b74c676445f58cc65cd5ac019483aa527762cbff63")
PRODUCTION_OVERLAY=(404796,"a55b20ca90792f195ef8de456a6cb7d90c831575b9aff147676a716844bfc73d");PRODUCTION_COMPONENT=(3928192,"5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73")
PRODUCTION_PACKAGE=(4706686,"30afcda8c32cc34fb1a1c12df13aff2f97223e12d74425690e67a6e4d81bfddf");PRODUCTION_FLASH_PLAN=(4071097,"cf46c2b6e6ed099ce9ef240520be8d81847ae219d52479286a373c326d22da6d")
PINS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-slave-function-map.tsv": "7c4b78bbe289b5f1dbc3340b72deb1280fa1d2599baa680798ce9f3c4af02825",
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-slave-provenance.tsv": "0867db5f49e1a0bc606d2e355ff34458b0a9d070f73a12caa702fac2b81ba465",
}
FUNCTIONS = {
    "dmConnUpdateCback": (0x56E4F8, 0x56E526, "bbefb6269cfe50e109e67128887afce8f64cee9f0f34c0c2c74105d17ec7c6f5"),
    "dmConnUpdActUpdateSlave": (0x56E526, 0x56E564, "48c98f0dd227f3a52cdb1d929992b13f7b9377aaffa21fcd1afe9b6b46284aad"),
    "dmConnUpdActL2cUpdateCnf": (0x56E564, 0x56E580, "efd59c8c2b769d9c8ed00bbfd2169ab03adf4fef9a53c80ea97395c82c73978b"),
    "DmL2cConnUpdateCnf": (0x56E580, 0x56E5A4, "05cdb79f244178b693ca42e4c71d4c84889c4a536ec38461ad745f23a15359a2"),
    "DmL2cCmdRejInd": (0x56E5A4, 0x56E5C6, "41de48e3802fa5de0d9a98452d10ec005a97fd407ca35c5104c6ecef8ad2060a"),
}
CALLERS = {
    "dmConnUpdateCback": [0x56E55E, 0x56E57A],
    "dmConnUpdActUpdateSlave": [],
    "dmConnUpdActL2cUpdateCnf": [],
    "DmL2cConnUpdateCnf": [0x536C4C, 0x536D14],
    "DmL2cCmdRejInd": [0x536D22],
}
PRODUCTION_FUNCTIONS=["open_cfw_cordio_dm_connection_slave_update_callback","open_cfw_cordio_dm_connection_slave_action_update","open_cfw_cordio_dm_connection_slave_action_l2c_confirm","open_cfw_cordio_dm_connection_slave_l2c_confirm","open_cfw_cordio_dm_connection_slave_l2c_reject"]
PRODUCTION_LEAVES=[(358664,58,0,"483fa70b36fb8baa2b0717e5caa0148f8e0b9dde852ddc3ddd3dad30779df5b2"),(358724,84,4,"e23c8e65a09a583d4c50fa9328806ebfe23ead14fe81db2f0bbac3a43bf02754"),(358808,34,1,"fbcb3dc47f798bbc42c18314ccdadef98337f22d43c6b674b99f2ac810850a3e"),(358844,36,2,"6d12448363beaad35e84fe2039ac9133413dabf354f50d6352727fe30b9f08d4"),(358880,44,0,"0f3b8c77de54952cec0a7ab695880c8e4135298a8346bf5b44701c3715d05645")]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sl(image: bytes, start: int, end: int) -> bytes:
    return image[start - BASE : end - BASE]


def decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_conn_slave_thumb", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def verify_file(path,expected,label):
    data=path.read_bytes()
    if (len(data),sha(data))!=expected: raise RuntimeError(f"{label} changed")

def verify_production():
    verify_file(SOURCE,SOURCE_PIN,"slave source");verify_file(HEADER,HEADER_PIN,"slave header");verify_file(TEST,TEST_PIN,"slave test")
    report=json.loads(REPORT.read_text());config=json.loads(CONFIG.read_text());manifest=json.loads(MANIFEST.read_text())
    leaves=sorted([r for r in report["relocated_leaves"] if r.get("source",{}).get("path","").endswith(SOURCE.name)],key=lambda r:r["pins"]["offset"])
    if len(leaves)!=5: raise RuntimeError("slave leaf count changed")
    for row,function,expected in zip(leaves,PRODUCTION_FUNCTIONS,PRODUCTION_LEAVES):
        observed=(row["pins"]["offset"],row["extraction"]["size"],row["extraction"]["relocation_count"],row["extraction"]["sha256"])
        if row["extraction"]["function"]!=function or observed!=expected: raise RuntimeError(f"slave leaf changed: {function}")
    sites={r["name"]:r for r in config["patch_sites"] if r["name"].startswith("replace_cordio_dm_conn_slave_core_")}
    for index,((name,(start,end,digest)),function) in enumerate(zip(FUNCTIONS.items(),PRODUCTION_FUNCTIONS),1):
        site=sites.get(f"replace_cordio_dm_conn_slave_core_{index:02d}")
        if site is None or site["runtime_address"]!=start or site["expected_size"]!=end-start or site["expected_sha256"]!=digest or site["target_function"]!=function or site["branch"]!="b_w": raise RuntimeError(f"slave route changed: {name}")
    override=manifest["component_overrides"]["apollo_main"];regions=[r for r in override["regions"] if r["name"].startswith("cordio_dm_conn_slave_core_")]
    if (report["overlay"]["size"],report["overlay"]["sha256"])!=PRODUCTION_OVERLAY or (report["component"]["size"],report["component"]["sha256"])!=PRODUCTION_COMPONENT or (override["provider"].get("size"),override["provider"].get("sha256"))!=PRODUCTION_COMPONENT or len(regions)!=13: raise RuntimeError("slave ownership changed")
    verify_file(PACKAGE,PRODUCTION_PACKAGE,"slave package");verify_file(FLASH_PLAN,PRODUCTION_FLASH_PLAN,"slave flash plan")
    flash=json.loads(FLASH_PLAN.read_text());counts=tuple(len(flash[k]) for k in ("flash_regions","unresolved_flash_regions","container_only_regions","protected_regions"))
    if counts!=(5576,2,5,6): raise RuntimeError("slave flash counts changed")
    return {"status":"production-routed","redirected_stock_functions":5,"redirected_stock_bytes":206,"source_owned_bytes_added":256,"alignment_bytes_added":6,"strict_relocations":7,"manifest_regions":13,"flash_plan_counts":counts}


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
    if sha(b"".join(bodies)) != "8391722feea37207e7d5010fc21f238777a153d0b78aa780404903e8c0fd4d3e":
        raise RuntimeError("body concatenation changed")
    if sha(sl(image, 0x56E4F8, 0x56E5CC)) != "69b64b7e5f7a5a2e6cb6666a88a25d06373a5c1f778086526836307bd7858f45":
        raise RuntimeError("physical interval changed")

    tail = sl(image, 0x56E5C6, 0x56E5CC)
    if sha(tail) != "b80cfed4b0e18a3a8b7f8878f098736983800213b50952d4dc6f8c07728eadf6" or tail[:2] != b"\0\0" or struct.unpack("<I", tail[2:])[0] != 0x200712A4:
        raise RuntimeError("literal tail changed")
    update_table = sl(image, 0x78D42C, 0x78D434)
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
    if entries != [(0x78D42C, 0x56E527), (0x78D430, 0x56E565)]:
        raise RuntimeError("stored entry closure changed")
    # This odd-address byte window is packed unrelated data, not an aligned pointer.
    if inside != [(0x643397, 0x56E500)]:
        raise RuntimeError("interior byte-window closure changed")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x56E4F8,
            "end_exclusive": 0x56E5CC,
            "physical_bytes": 212,
            "linked_function_count": 5,
            "linked_function_bytes": 206,
            "source_inventory_functions": 6,
            "source_only_functions": ["DmConnAccept"],
            "direct_bl_ingress_sites": 5,
            "registered_function_pointers": 2,
            "strict_interior_pointers": 0,
            "unaligned_false_pointer_windows": 1,
        },
        "architecture": {
            "update_action_entries": 2,
            "separate_update_component": True,
            "l2c_update_confirm_event": 0x73,
            "update_executor": "dmConnUpdExecute",
        },
        "lineage": {
            "selected_blob": "9422ae8e45e12c3ea26aa6dbdc5730ed40e74cdd",
            "selected_sha256": "4fc01fd9a83d370f3899d75c0bda7ce7473067cde17efe41b5e6b87b4c15847e",
            "license": "Apache-2.0",
            "historical_generating_commit_resolved": False,
        },
        "build_readiness": {
            "status": "target-compiled",
            "profiles": 7,
        },
        "production": verify_production(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else "Cordio dm_conn_slave closed: 5 linked, 1 source-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
