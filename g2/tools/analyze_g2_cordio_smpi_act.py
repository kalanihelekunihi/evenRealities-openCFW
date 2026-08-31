#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio SMP initiator actions."""

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
MAP = ROOT / "tools/manifests/packetcraft-cordio-smpi-act-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-smpi-act-provenance.tsv"
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smpi_act.c"
PRODUCTION_SOURCE_SIZE = 16_690
PRODUCTION_SOURCE_SHA256 = "0a19fb3adddd4ae6b9a71a4b012b2dea23cc3999938e3e6be1f8da4772a538df"
PRODUCTION_ROUTES = {
    "open_cfw_cordio_smpi_pair_request": (180784, 140, "ec24f8ac35a2e004f0d3290dce6d4d44e4bc7ce489881bebfb155a2cf241edff"),
    "open_cfw_cordio_smpi_check_security_request": (180924, 22, "8833b22dd7c1ee01e7008eb4ae35fbc2c5568edeb48fa8e498f474919b5f348a"),
    "open_cfw_cordio_smpi_process_security_request": (180948, 44, "2b4bf2afafcb7e9760994679686fe608a52e4a5ec28a3e13fe08fecc6801b38d"),
    "open_cfw_cordio_smpi_process_pair_response": (180992, 112, "640ae77bc4e4d1f8e089d7c42c96a8a2b257214dec1a1058c359f441dc40244c"),
    "open_cfw_cordio_smpi_process_pair_confirm": (181104, 74, "e31dd4e016d83d584cf231bb63546dcaa9380264c0939c513627a419bfc3cf98"),
    "open_cfw_cordio_smpi_confirm_verify": (181180, 100, "a8450550a9e8492ca79d549b326044d3f6c121b66ce399e553491ce8ce6931e2"),
    "open_cfw_cordio_smpi_stk_encrypt": (181280, 76, "9cf4bb931b9b8248cdeea6364230964a309fd2079dca80e38b7241c1bdbd54ab"),
    "open_cfw_cordio_smpi_setup_key_distribution": (181356, 148, "66617b6e2bed5e91464eb30505f15faed8f1381771bc12bc99a777971ec6edf9"),
    "open_cfw_cordio_smpi_receive_key": (181504, 54, "69315b8f2ac2f75fbd4a7c541bab74e0970b36aad69b6e2cbe842a40f8f3df91"),
    "open_cfw_cordio_smpi_send_key": (181560, 50, "6d43669f43a1b49d64eff8f4424ac27f5b0eeafe205ba23c73f296a5c518279b"),
}
PINS = {
    MAP: "a0fcd353e2cb16c6c71eda095ca7af07f13d9d6c4eb6d1bb82561513347316d9",
    PROVENANCE: "4f39b941305bd4d4ea95c53a4550e5aa5331bb7a2a0a12d56d94f5dc3515ca06",
}

RAW_FALSE_CALLS = {"smpiActStkEncrypt": [0x5E1CEC]}
ACTION_TABLES = [
    (0x6D1214, 0x6D12E0, "2f7d77ff2105f2a6153d40c15bff8ed0ee8197df738ea1547ff57a023185dd01"),
    (0x6DBAC4, 0x6DBB28, "2b2fd073285f4dae0973e64cfe07b3d68c4c119797401b2d2d8f932a2250150f"),
]
EXPECTED_STORED_ENTRIES = [
    (0x6D1250, 0x5E3119), (0x6D1254, 0x5E3199),
    (0x6D1258, 0x5E31B1), (0x6D125C, 0x5E31D7),
    (0x6D1260, 0x5E3245), (0x6D1264, 0x5E3297),
    (0x6D1268, 0x5E32FD), (0x6D126C, 0x5E335D),
    (0x6D1270, 0x5E340D), (0x6D1274, 0x5E3441),
    (0x6DBB00, 0x5E3119), (0x6DBB04, 0x5E3199),
    (0x6DBB08, 0x5E31B1), (0x6DBB0C, 0x5E31D7),
    (0x6DBB10, 0x5E3245), (0x6DBB14, 0x5E3297),
    (0x6DBB18, 0x5E32FD), (0x6DBB1C, 0x5E335D),
    (0x6DBB20, 0x5E340D), (0x6DBB24, 0x5E3441),
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
    spec = importlib.util.spec_from_file_location("smpi_act_thumb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_rows() -> list[tuple[str, int, int, str]]:
    rows = []
    with MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] != "linked":
                raise RuntimeError("unexpected source-only initiator action")
            rows.append((row["function"], int(row["stock_start"], 0),
                         int(row["stock_end_exclusive"], 0), row["stock_sha256"]))
    return rows


def production_report(linked: list[tuple[str, int, int, str]]) -> dict:
    source = PRODUCTION_SOURCE.read_bytes()
    if len(source) != PRODUCTION_SOURCE_SIZE or sha(source) != PRODUCTION_SOURCE_SHA256:
        raise RuntimeError("Cordio legacy initiator production source identity changed")
    text = source.decode("utf-8")
    if "ccb->key_ready = 1U;" not in text or "OPEN_CFW_SMPI_STK_ENCRYPT_ONLY" not in text:
        raise RuntimeError("Cordio legacy initiator r20/R4 behavior changed")
    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    leaves = {x["function"]: x for x in overlay.get("relocated_leaves", [])
              if x.get("function") in PRODUCTION_ROUTES}
    patches = {x["target_function"]: x for x in overlay.get("patch_sites", [])
               if x.get("target_function") in PRODUCTION_ROUTES}
    if set(leaves) != set(PRODUCTION_ROUTES) or set(patches) != set(PRODUCTION_ROUTES):
        raise RuntimeError("Cordio legacy initiator production routing is incomplete")
    source_path = PRODUCTION_SOURCE.relative_to(ROOT).as_posix()
    for (function, (offset, size, digest)), stock in zip(PRODUCTION_ROUTES.items(), linked):
        stock_name, start, end, stock_digest = stock
        leaf = leaves[function]; record = leaf.get("source", {}); patch = patches[function]
        if (leaf.get("profiles") != ["apple-clang"] or record.get("path") != source_path
                or record.get("size") != PRODUCTION_SOURCE_SIZE
                or record.get("sha256") != PRODUCTION_SOURCE_SHA256
                or record.get("license") != "Apache-2.0"
                or record.get("upstream_commit") != "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"
                or leaf.get("expected", {}).get("offset") != offset
                or leaf.get("expected", {}).get("size") != size
                or leaf.get("expected", {}).get("sha256") != digest
                or leaf.get("strict_relocation_contract") is not True):
            raise RuntimeError(f"Cordio legacy initiator production leaf changed: {function}")
        if (patch.get("profiles") != ["apple-clang"] or patch.get("runtime_address") != start
                or patch.get("expected_size") != end - start
                or patch.get("expected_sha256") != stock_digest
                or patch.get("branch") != "b_w"):
            raise RuntimeError(f"Cordio legacy initiator stock patch changed: {stock_name}")
    return {
        "status": "production-routed authenticated Packetcraft r20.05c legacy initiator actions",
        "candidate": source_path,
        "production_routed": True,
        "live_functions": len(PRODUCTION_ROUTES),
        "relocated_functions": len(PRODUCTION_ROUTES),
        "compiled_leaf_bytes": sum(route[1] for route in PRODUCTION_ROUTES.values()),
        "source_owned_bytes_added": 830,
        "stock_bytes_replaced": sum(end - start for _, start, end, _ in linked),
        "hardware_validation": (
            "blocked by unavailable physical evidence; future qualification requires authorized G2/EM9305 legacy initiator pairing, "
            "confirm/random, STK encryption, key distribution, retry, and interoperability physical evidence"
        ),
    }


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise RuntimeError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise RuntimeError(f"pinned input changed: {path}")

    rows = load_rows()
    if len(rows) != 10:
        raise RuntimeError("source inventory changed")
    bodies = []
    for name, start, end, digest in rows:
        body = image_slice(blob, start, end)
        if sha(body) != digest:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != "08a38806ad6b2936fbd3f6ea7f22f0f247982f1d660e7ff0d3bc3de25a5291ed":
        raise RuntimeError("body concatenation changed")
    if sha(image_slice(blob, 0x5E3118, 0x5E3474)) != "b872fde1c48e7f3ca8b9538a4767c94003803903738007ef046e2b094f32c862":
        raise RuntimeError("physical object changed")
    if sha(image_slice(blob, 0x5E3404, 0x5E340C)) != "68deba1131e11625268525b8e2bd5db2ed3e0c7218d7ce75c4007f027d4eabec":
        raise RuntimeError("literal island changed")
    if list(struct.unpack("<2I", image_slice(blob, 0x5E3404, 0x5E340C))) != [0x200004B8, 0x20070AEC]:
        raise RuntimeError("pSmpCfg/smpCb literals changed")
    if image_slice(blob, 0x5E333A, 0x5E3340) != bytes.fromhex("012084f84400"):
        raise RuntimeError("r20 initiator keyReady assignment changed")

    decoder = load_decoder()
    starts = {start: name for name, start, _, _ in rows}
    raw_calls = {name: [] for name, _, _, _ in rows}
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            raw_calls[starts[target]].append(address)
    if raw_calls != {**{name: [] for name in starts.values()}, **RAW_FALSE_CALLS}:
        raise RuntimeError("raw direct-entry candidate closure changed")
    # 0x5E1CEC is the second halfword of the wide multiply at 0x5E1CEA.
    if image_slice(blob, 0x5E1CEA, 0x5E1CEE) != bytes.fromhex("07fb01f0"):
        raise RuntimeError("false BL-like wide multiply changed")

    for start, end, digest in ACTION_TABLES:
        if sha(image_slice(blob, start, end)) != digest:
            raise RuntimeError(f"initiator action table changed at {start:#x}")
    interiors = set()
    for _, start, end, _ in rows:
        interiors.update(range(start + 2, end, 2))
    stored_entries = []
    stored_interiors = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in starts:
            stored_entries.append((BASE + offset, value))
        elif target in interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries != EXPECTED_STORED_ENTRIES:
        raise RuntimeError("stored entry-pointer closure changed")
    if stored_interiors:
        raise RuntimeError("stored strict-interior pointer found")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x5E3118,
            "end_exclusive": 0x5E3474,
            "physical_bytes": 860,
            "linked_function_count": 10,
            "linked_function_bytes": 852,
            "owned_noncode_bytes": 8,
            "source_inventory_functions": 10,
            "source_only_functions": [],
            "direct_bl_ingress_sites": 0,
            "raw_false_bl_candidates": 1,
            "registered_function_pointers": 20,
            "strict_interior_pointers": 0,
            "decoded_outbound_bl_sites": 28,
        },
        "architecture": {
            "retained_source_path": None,
            "smp_control_block": 0x20070AEC,
            "smp_config_pointer": 0x200004B8,
            "ccb_key_ready_offset": 0x44,
            "legacy_action_roots": 10,
            "secure_connections_action_roots": 10,
            "next_unit_entry": 0x5E3474,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "404a9e20dac01b1aa466b8758c6e46cb59d4af40",
            "selected_sha256": "c61194f9d62c5dd974056cd0d6d6e025243b3d10b75c6c08ac7f97ed749e5ac2",
            "official_later_oracle": "AmbiqSuite R4.4.1 import at 4264b930",
            "license": "Apache-2.0",
            "independent_release_discriminator": True,
            "discriminator": "stock writes smpCcb.keyReady at +0x44; r19/AmbiqSuite 2.x lacks that assignment",
            "historical_generating_commit_resolved": False,
        },
        "production": production_report(rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Cordio smpi_act closed: 10/10 linked; 20 table roots; r20 keyReady path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
