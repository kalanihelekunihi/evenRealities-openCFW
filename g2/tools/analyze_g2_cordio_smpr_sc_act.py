#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio SMP SC responder actions."""

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
MAP = ROOT / "tools/manifests/packetcraft-cordio-smpr-sc-act-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-smpr-sc-act-provenance.tsv"
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smpr_sc_act.c"
PRODUCTION_SOURCE_SIZE = 17_715
PRODUCTION_SOURCE_SHA256 = "9aeeb7deca5ddba366291e2b19daeb4c06f8d1feb4915dc863b50b5dd1d82c26"
PRODUCTION_ROUTES = {
    "open_cfw_cordio_smpr_sc_store_pin": (178048, 78, "aa7e81ac7c5ca3734db2a2e0459c16a01bde2156c6a6ce08ed344d5c772f7d8a"),
    "open_cfw_cordio_smpr_sc_send_public_key": (178128, 22, "d2788ef0c1a065341fb1abc9ba0e27823c4273157938848c6a262caf174d527b"),
    "open_cfw_cordio_smpr_sc_jwnc_setup": (178152, 70, "5cb5f7afe5d8e383eca630e3c9cb0a8214695e4f087f15170ad8a19f62fcd869"),
    "open_cfw_cordio_smpr_sc_jwnc_send_confirm": (178224, 6, "bacac1b51e885f085b42ce0a352bde12899c29fb8cbf6d976822dcca30e191f1"),
    "open_cfw_cordio_smpr_sc_jwnc_calculate_g2": (178232, 32, "37275b0bbf60da8acc65d4d1e6e01bf1c30ae550fe74626657f58f0bee567bf0"),
    "open_cfw_cordio_smpr_sc_jwnc_display": (178264, 40, "22f506225868c20e7da32450bc99d098175377f62c821564659e040a17b707cf"),
    "open_cfw_cordio_smpr_sc_passkey_store_confirm": (178304, 16, "56b9d58af240ba305a2ecdf345bf3699e88568178e90f3c0f0290fd58c51d27e"),
    "open_cfw_cordio_smpr_sc_passkey_calculate_cb": (178320, 68, "5de400a0875e9691e99b4d45d72fbc383d09a0c441d8a0be43ce252533679aa5"),
    "open_cfw_cordio_smpr_sc_passkey_store_confirm_and_calculate_cb": (178388, 22, "e62812baa6c9b6a16fa821f36b336ddf98c1a9b35a449d84d3c4271f552c8248"),
    "open_cfw_cordio_smpr_sc_passkey_store_pin_and_calculate_cb": (178412, 22, "4ffc9c6fe149d5645ab9ae8984ac1f78f37044ebc21210f31aaee462e536f6b5"),
    "open_cfw_cordio_smpr_sc_passkey_send_confirm": (178436, 6, "b489cef80508e5cc899d35ba388e53a7613e0108ca2e13fa50124fa3cdf364ea"),
    "open_cfw_cordio_smpr_sc_passkey_calculate_ca": (178444, 62, "7097f3b30b3e5436d326d6f7d4be860ad2d4ac56b3734e1d17a1593a9450fa71"),
    "open_cfw_cordio_smpr_sc_passkey_send_random": (178508, 104, "072cf10a56591443dd21ed45122e4c248c96791534c582c9aeb5ea10929f9879"),
    "open_cfw_cordio_smpr_sc_oob_setup": (178612, 8, "2a43add7a549e97c68c78df9dc7426a70da8ba405877d5eb8ba2db8120786026"),
    "open_cfw_cordio_smpr_sc_oob_calculate_ca": (178620, 122, "0ef61cbad359c78cc4d4b8d8e7db1c0087aef201e3bdffc8e313df6f67b8dedb"),
    "open_cfw_cordio_smpr_sc_oob_send_random": (178744, 72, "8544ef428007b8f0803bbd390bd1237f2e07ec764b23e7e77bf1713cd0d984e7"),
    "open_cfw_cordio_smpr_sc_store_dh_key_check": (178816, 22, "f828d5fbf2d994a02dca987b49c2fa3640f310774e217072323368218a3a8c51"),
    "open_cfw_cordio_smpr_sc_wait_dh_key_check": (178840, 26, "6e8da75389e0e21d75c31888b3d05ea4a0b73e085f69a1c04b5e326272f75021"),
    "open_cfw_cordio_smpr_sc_calculate_dh_key": (178868, 50, "6955a85cdf356c909a4effe9be7bad4f8cde399e93467161f36a880e8808ec72"),
    "open_cfw_cordio_smpr_sc_dh_key_check_send": (178920, 158, "ee1202fabf6a4df5ab949d21bc8a1400ed61f7125bf1205c538e76fc4b448488"),
}
PINS = {
    MAP: "e312d66d683e5bb0610cfb15498fa89f0e86eee2bdeacc02dea2ab0d0e957ae1",
    PROVENANCE: "ef701fa5ec14d4f41747b6bc5c31cc879b69123fdec500d2182e6f7227c97d28",
}

CALLERS = {
    "smprScActStoreLescPin": [0x5E3ED0],
    "smprScActSendPubKey": [],
    "smprScActJwncSetup": [],
    "smprScActJwncSendCnf": [],
    "smprScActJwncCalcG2": [],
    "smprScActJwncDisplay": [],
    "smprScActPkStoreCnf": [0x5E3EB8],
    "smprScActPkStoreCnfAndCalcCb": [],
    "smprScActPkStorePinAndCalcCb": [],
    "smprScActPkCalcCb": [0x5E3EC0, 0x5E3ED8],
    "smprScActPkSendCnf": [],
    "smprScActPkCalcCa": [],
    "smprScActPkSendRand": [],
    "smprScActOobSetup": [],
    "smprScActOobCalcCa": [],
    "smprScActOobSendRand": [],
    "smprScActStoreDhCheck": [],
    "smprScActWaitDhCheck": [],
    "smprScActCalcDHKey": [],
    "smprScActDHKeyCheckSend": [],
}
ACTION_TABLE = (0x6D0B64, 0x6D0C40,
                "bbcc96d09c9c3d6842797ab8c9c61604dca828aaaf230fba8e5df96d77245718")
EXPECTED_STORED_ENTRIES = [
    (0x6D0B78, 0x5E3DCF), (0x6D0B80, 0x5E3D7D),
    (0x6D0BC0, 0x5E3DE7), (0x6D0BC4, 0x5E3E37),
    (0x6D0BC8, 0x5E3E55), (0x6D0BCC, 0x5E3E75),
    (0x6D0BDC, 0x5E3E9B), (0x6D0BE0, 0x5E3EAF),
    (0x6D0BE4, 0x5E3EC7), (0x6D0BE8, 0x5E3EDF),
    (0x6D0BEC, 0x5E3F2B), (0x6D0BF0, 0x5E3F47),
    (0x6D0BF4, 0x5E3F7F), (0x6D0BF8, 0x5E4001),
    (0x6D0BFC, 0x5E4009), (0x6D0C00, 0x5E4081),
    (0x6D0C04, 0x5E40E7), (0x6D0C08, 0x5E4101),
    (0x6D0C0C, 0x5E411D), (0x6D0C24, 0x5E4147),
]
# These five packed-data byte windows decode to even body-interior-looking
# values. None has the Thumb bit required by a Cortex-M function pointer. Pin
# them so an image change cannot hide a new real pointer among them.
EVEN_INTERIOR_WINDOWS = [
    (0x62E882, 0x5E3F00), (0x64E565, 0x5E3F00),
    (0x64EACD, 0x5E3F0E), (0x64EF18, 0x5E3F00),
    (0x6C0AFD, 0x5E409E),
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
    spec = importlib.util.spec_from_file_location("smpr_sc_act_thumb", path)
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
                raise RuntimeError("unexpected source-only SC responder action")
            rows.append((row["function"], int(row["stock_start"], 0),
                         int(row["stock_end_exclusive"], 0), row["stock_sha256"]))
    return rows


def production_report(linked: list[tuple[str, int, int, str]]) -> dict:
    source = PRODUCTION_SOURCE.read_bytes()
    if len(source) != PRODUCTION_SOURCE_SIZE or sha(source) != PRODUCTION_SOURCE_SHA256:
        raise RuntimeError("Cordio responder SC action production source identity changed")
    text = source.decode("utf-8")
    if "c->key_ready=1U;" not in text or "OPEN_CFW_SMPR_SC_DH_SEND_ONLY" not in text:
        raise RuntimeError("Cordio responder SC r20/R4 behavior changed")
    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    leaves = {x["function"]: x for x in overlay.get("relocated_leaves", [])
              if x.get("function") in PRODUCTION_ROUTES}
    patches = {x["target_function"]: x for x in overlay.get("patch_sites", [])
               if x.get("target_function") in PRODUCTION_ROUTES}
    if set(leaves) != set(PRODUCTION_ROUTES) or set(patches) != set(PRODUCTION_ROUTES):
        raise RuntimeError("Cordio responder SC production routing is incomplete")
    source_path = PRODUCTION_SOURCE.relative_to(ROOT).as_posix()
    stock_by_start = {start: (name, end, digest) for name, start, end, digest in linked}
    for function, (offset, size, digest) in PRODUCTION_ROUTES.items():
        leaf = leaves[function]; record = leaf.get("source", {}); patch = patches[function]
        start = patch.get("runtime_address"); stock = stock_by_start.get(start)
        if (leaf.get("profiles") != ["apple-clang"] or record.get("path") != source_path
                or record.get("size") != PRODUCTION_SOURCE_SIZE
                or record.get("sha256") != PRODUCTION_SOURCE_SHA256
                or record.get("license") != "Apache-2.0"
                or record.get("upstream_commit") != "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"
                or leaf.get("expected", {}).get("offset") != offset
                or leaf.get("expected", {}).get("size") != size
                or leaf.get("expected", {}).get("sha256") != digest
                or leaf.get("strict_relocation_contract") is not True):
            raise RuntimeError(f"Cordio responder SC production leaf changed: {function}")
        if (stock is None or patch.get("profiles") != ["apple-clang"]
                or patch.get("expected_size") != stock[1] - start
                or patch.get("expected_sha256") != stock[2]
                or patch.get("branch") != "b_w"):
            raise RuntimeError(f"Cordio responder SC stock patch changed: {function}")
    return {
        "status": "production-routed authenticated Packetcraft r20.05c responder actions",
        "candidate": source_path,
        "production_routed": True,
        "live_functions": len(PRODUCTION_ROUTES),
        "relocated_functions": len(PRODUCTION_ROUTES),
        "compiled_leaf_bytes": sum(route[1] for route in PRODUCTION_ROUTES.values()),
        "source_owned_bytes_added": 1030,
        "stock_bytes_replaced": sum(end - start for _, start, end, _ in linked),
        "hardware_validation": (
            "blocked by unavailable physical evidence; future qualification requires authorized G2/EM9305 responder Secure Connections "
            "pairing, numeric comparison, passkey/key-press, OOB, DH-key, retry, and "
            "interoperability physical evidence"
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
    if len(rows) != 20:
        raise RuntimeError("source inventory changed")
    bodies = []
    for name, start, end, digest in rows:
        body = image_slice(blob, start, end)
        if len(body) != end - start or sha(body) != digest:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != "812d6e4df932f94837db3f980104e9432251aca1625a2b200f00c49e648ea86a":
        raise RuntimeError("body concatenation changed")
    if sha(image_slice(blob, 0x5E3D7C, 0x5E4228)) != "a93663591adfe7aeaad3c3fe562766e3cc447b5ebdda406e45160f549a9e6e2f":
        raise RuntimeError("physical object changed")
    tail = image_slice(blob, 0x5E4206, 0x5E4228)
    if sha(tail) != "55fdc0c2ce5baa59f5fb8b95f6209dc472b53c6543d5928733ac5e11a0c83e44":
        raise RuntimeError("owned tail changed")
    if tail[:10] != b"\0\0Cbi\0Ca\0\0":
        raise RuntimeError("SC responder tail labels changed")
    if list(struct.unpack("<6I", tail[10:])) != [
        0x7856B0, 0x78E85C, 0x7892F0, 0x78E864, 0x78C350, 0x200004B8,
    ]:
        raise RuntimeError("SC responder literal pool changed")
    if image_slice(blob, 0x5E41A8, 0x5E41AE) != bytes.fromhex("012084f84400"):
        raise RuntimeError("r20 SC responder keyReady assignment changed")

    decoder = load_decoder()
    starts = {start: name for name, start, _, _ in rows}
    calls = {name: [] for name, _, _, _ in rows}
    outbound = []
    interiors = set()
    for _, start, end, _ in rows:
        interiors.update(range(start + 2, end, 2))
        for address in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None:
                outbound.append((address, target))
    interior_branches = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            calls[starts[target]].append(address)
        elif target in interiors:
            interior_branches.append((address, target))
    if calls != CALLERS:
        raise RuntimeError("direct SC responder entry-call closure changed")
    if interior_branches:
        raise RuntimeError("direct branch to SC responder body interior found")
    if len(outbound) != 59:
        raise RuntimeError("SC responder outbound-call closure changed")

    start, end, digest = ACTION_TABLE
    if sha(image_slice(blob, start, end)) != digest:
        raise RuntimeError("responder SC action table changed")
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
        raise RuntimeError("stored SC responder entry-pointer closure changed")
    if stored_interiors != EVEN_INTERIOR_WINDOWS:
        raise RuntimeError("SC responder interior-looking byte windows changed")
    if any(value & 1 for _, value in stored_interiors):
        raise RuntimeError("SC responder body-interior Thumb pointer found")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x5E3D7C,
            "end_exclusive": 0x5E4228,
            "physical_bytes": 1196,
            "linked_function_count": 20,
            "linked_function_bytes": 1162,
            "owned_noncode_bytes": 34,
            "source_inventory_functions": 20,
            "source_only_functions": [],
            "direct_bl_ingress_sites": 4,
            "external_direct_bl_ingress_sites": 0,
            "registered_function_pointers": 20,
            "strict_interior_pointers": 0,
            "even_interior_looking_windows": 5,
            "decoded_outbound_bl_sites": 59,
        },
        "architecture": {
            "retained_source_path": None,
            "smp_config_pointer": 0x200004B8,
            "calc128_zeros": 0x7856B0,
            "ccb_key_ready_offset": 0x44,
            "secure_connections_action_roots": 20,
            "next_unit_entry": 0x5E4228,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "062799ba7c52aff19cb29d07eb0fbfc38ae1d1e4",
            "selected_sha256": "6c98c9eb132b19a6b7870ae35d7e31f0480d2566a83590f09984e205b10567d5",
            "official_later_oracle": "AmbiqSuite R4.4.1 import at 4264b930",
            "license": "Apache-2.0",
            "independent_release_discriminator": True,
            "discriminator": "stock DH-key-check send writes smpCcb.keyReady at +0x44; r19/AmbiqSuite 2.x omits it",
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
        print("Cordio smpr_sc_act closed: 20/20 linked; 20 table roots; r20 keyReady path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
