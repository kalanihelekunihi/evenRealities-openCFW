#!/usr/bin/env python3
"""Fail-closed audit for G2 Cordio legacy SMP role state machines."""

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
FUNCTION_MAP = ROOT / "tools/manifests/packetcraft-cordio-smp-legacy-sm-function-map.tsv"
TABLE_MAP = ROOT / "tools/manifests/packetcraft-cordio-smp-legacy-sm-table-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-smp-legacy-sm-provenance.tsv"
PINS = {
    FUNCTION_MAP: "7fe82b6779d5b7107f21232cdcad458b74e5a2162bd6ffc9d52d04f3e10357bb",
    TABLE_MAP: "e3f18ad5e0b893ad116111dc01978e91aa48d946370b6237553ce84401e9655a",
    PROVENANCE: "5379ef8a78f01aa827ca204aa78404967cef615e88b167614e5bd23b3139c37c",
}

EXPECTED_CALLS = {"SmpiInit": [0x4B807C], "SmprInit": [0x4B8084]}
ROLES = {
    "initiator": {
        "physical": (0x537EEC, 0x537F14),
        "physical_sha256": "692ebaa593161de42e912411698481ce0ba40d0dd8e75b19cc5efeb6d15979b4",
        "tail": (0x537F02, 0x537F14),
        "tail_sha256": "55502190cdae916e849c61303e97e4f0a028be6a634f6f05482eb6d692e7aa96",
        "interface": 0x78C344,
        "interface_sha256": "a0eb9c52d96f5d8dbec3ed04946b77c28175e9f769e57544d568fd97fe76405f",
        "action_count": 25,
        "action_sha256": "2b2fd073285f4dae0973e64cfe07b3d68c4c119797401b2d2d8f932a2250150f",
        "state_count": 14,
        "state_pointer_sha256": "abcfedddf8b6ece51e10104e8179a1c8423a0a679def8008acaf59b9f77af3cd",
        "state_entry_bytes": 162,
        "state_entry_sha256": "b94bcdff170bcac4b156a80b14a6cc802502d340d57037d9b88349b89df4b1eb",
        "owned_bytes": 370,
        "owned_sha256": "ecfe3c9d668814bb4783f5cf046424a255729c271e78881d95bcae466b8c005c",
        "smp_cb_offset": 0xE8,
    },
    "responder": {
        "physical": (0x5380DC, 0x538104),
        "physical_sha256": "e8b27cfbbf917047a50437d2cf68b10640ae740cf9e92fe2bee79fff26316bd3",
        "tail": (0x5380F2, 0x538104),
        "tail_sha256": "627ef85160035d50d96c1eb03991b56723ae835d3144ab687c761f2cec5aaacd",
        "interface": 0x78C4AC,
        "interface_sha256": "3df793b9a82597461457fc13ceeb6f0d671bef63630da55b9d55926464596d16",
        "action_count": 27,
        "action_sha256": "f98a484ebaee566eda7ad88adbadd10b8e2670de97b1370e35783fea117143cc",
        "state_count": 15,
        "state_pointer_sha256": "b99a11d8b8df5246263e583089627e81a2c630c7fe1eb85b6a378d373ded036b",
        "state_entry_bytes": 195,
        "state_entry_sha256": "5b9fe4ec712191eaef713c870eb07065c037f2c537544358e37a410a4e80fdb2",
        "owned_bytes": 415,
        "owned_sha256": "1e94a3355528895406876ad88ea5a3c18315174911355e866d6d2bb9fe0de56a",
        "smp_cb_offset": 0xE4,
    },
}
COMBINED_BODY_SHA = "e957d03023af5c782d26b44be471b6264b5c39888d5ec0dbf3c50d8f9933d3df"
COMBINED_PHYSICAL_SHA = "fad1bda3ec041308d66b70d4c4546a0ce583874908fd9b9d24d685921537a7f5"
COMBINED_OWNED_SHA = "98a3708291e1ca0add3c7cc3e182b11e240680905fd74e336558d01f1e96fa79"
SMPR_API_PAIR_REQUEST = bytes.fromhex(
    "0a00010602120700020300010800010900010f01031f0001000000"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE : end - BASE]


def load_decoder():
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("smp_legacy_sm_thumb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_functions() -> list[dict[str, object]]:
    rows = []
    with FUNCTION_MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] != "linked":
                raise RuntimeError("unexpected legacy state-machine source-only function")
            rows.append({
                "source_file": row["source_file"],
                "name": row["function"],
                "start": int(row["stock_start"], 0),
                "end": int(row["stock_end_exclusive"], 0),
                "size": int(row["stock_bytes"]),
                "sha256": row["stock_sha256"],
            })
    return rows


def read_state_table(blob: bytes, address: int) -> bytes:
    rows = []
    for index in range(64):
        row = image_slice(blob, address + index * 3, address + index * 3 + 3)
        if len(row) != 3:
            raise RuntimeError(f"state table leaves image at {address:#x}")
        rows.append(row)
        if row == b"\0\0\0":
            return b"".join(rows)
    raise RuntimeError(f"unterminated state table at {address:#x}")


def verify_role(blob: bytes, role: str, config: dict[str, object]) -> tuple[dict, bytes]:
    physical = image_slice(blob, *config["physical"])
    if sha(physical) != config["physical_sha256"]:
        raise RuntimeError(f"{role} physical initializer changed")
    if sha(image_slice(blob, *config["tail"])) != config["tail_sha256"]:
        raise RuntimeError(f"{role} initializer tail changed")

    interface = config["interface"]
    interface_data = image_slice(blob, interface, interface + 12)
    if sha(interface_data) != config["interface_sha256"]:
        raise RuntimeError(f"{role} interface changed")
    state_root, action_root, common_root = struct.unpack("<III", interface_data)

    action_count = config["action_count"]
    action_data = image_slice(blob, action_root, action_root + action_count * 4)
    if sha(action_data) != config["action_sha256"]:
        raise RuntimeError(f"{role} action table changed")
    if not all(value & 1 for value in struct.unpack(f"<{action_count}I", action_data)):
        raise RuntimeError(f"{role} action table has non-Thumb target")

    state_count = config["state_count"]
    pointer_data = image_slice(blob, state_root, state_root + state_count * 4)
    if sha(pointer_data) != config["state_pointer_sha256"]:
        raise RuntimeError(f"{role} state-pointer table changed")
    state_targets = struct.unpack(f"<{state_count}I", pointer_data)
    if len(set(state_targets)) != state_count:
        raise RuntimeError(f"{role} state-pointer table aliases entries")
    state_data = read_state_table(blob, common_root)
    state_data += b"".join(read_state_table(blob, value) for value in state_targets)
    if len(state_data) != config["state_entry_bytes"] or sha(state_data) != config["state_entry_sha256"]:
        raise RuntimeError(f"{role} state-entry closure changed")

    owned = physical + interface_data + action_data + pointer_data + state_data
    if len(owned) != config["owned_bytes"] or sha(owned) != config["owned_sha256"]:
        raise RuntimeError(f"{role} owned-byte concatenation changed")

    tail_start, _ = config["tail"]
    literals = struct.unpack("<4I", image_slice(blob, tail_start + 2, tail_start + 18))
    if literals != (0x20070AEC, interface, 0x56E6E1, 0x56E84D):
        raise RuntimeError(f"{role} initializer literal closure changed")

    return ({
        "physical_start": config["physical"][0],
        "physical_end_exclusive": config["physical"][1],
        "physical_bytes": len(physical),
        "interface": interface,
        "action_table": action_root,
        "action_count": action_count,
        "state_pointer_table": state_root,
        "state_count": state_count,
        "common_state_table": common_root,
        "state_table_count": state_count + 1,
        "state_entry_bytes": len(state_data),
        "owned_bytes": len(owned),
        "smp_cb_field_offset": config["smp_cb_offset"],
    }, owned)


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise RuntimeError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise RuntimeError(f"pinned input changed: {path}")

    functions = load_functions()
    if len(functions) != 2:
        raise RuntimeError("legacy state-machine function inventory changed")
    bodies = []
    for function in functions:
        body = image_slice(blob, function["start"], function["end"])
        if len(body) != function["size"] or sha(body) != function["sha256"]:
            raise RuntimeError(f"function body changed: {function['name']}")
        bodies.append(body)
    if sha(b"".join(bodies)) != COMBINED_BODY_SHA:
        raise RuntimeError("combined initializer-body digest changed")
    physical = [image_slice(blob, *ROLES[role]["physical"]) for role in ROLES]
    if sha(b"".join(physical)) != COMBINED_PHYSICAL_SHA:
        raise RuntimeError("combined physical-initializer digest changed")

    verified = {role: verify_role(blob, role, config) for role, config in ROLES.items()}
    role_reports = {role: result[0] for role, result in verified.items()}
    owned = [result[1] for result in verified.values()]
    if sha(b"".join(owned)) != COMBINED_OWNED_SHA:
        raise RuntimeError("combined legacy state-machine ownership changed")
    responder_state_root = role_reports["responder"]["state_pointer_table"]
    api_pair_request = read_state_table(
        blob, struct.unpack_from("<I", blob, responder_state_root + 4 - BASE)[0]
    )
    if api_pair_request != SMPR_API_PAIR_REQUEST:
        raise RuntimeError("r20 responder timeout/cleanup discriminator changed")

    decoder = load_decoder()
    starts = {function["start"]: function["name"] for function in functions}
    calls = {function["name"]: [] for function in functions}
    interiors = set()
    for function in functions:
        interiors.update(range(function["start"] + 2, function["end"], 2))
    interior_branches = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            calls[starts[target]].append(address)
        elif target in interiors:
            interior_branches.append((address, target))
    if calls != EXPECTED_CALLS or interior_branches:
        raise RuntimeError("legacy initializer direct-ingress closure changed")

    stored_entries = []
    stored_interiors = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in starts:
            stored_entries.append((BASE + offset, value))
        elif target in interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries or stored_interiors:
        raise RuntimeError("stored legacy initializer entry/interior closure changed")

    return {
        "schema_version": 1,
        "module": {
            "translation_units": 2,
            "source_function_count": 2,
            "linked_function_count": 2,
            "linked_function_bytes": 44,
            "physical_initializer_bytes": 80,
            "dispatch_data_bytes": 705,
            "total_identified_owned_bytes": 785,
            "direct_bl_ingress_sites": 2,
            "stored_function_pointers": 0,
            "strict_interior_pointers": 0,
            "source_only_functions": [],
        },
        "roles": role_reports,
        "abi": {
            "smp_control_block": 0x20070AEC,
            "state_entry_bytes": 3,
            "initiator_interface_field_offset": 0xE8,
            "responder_interface_field_offset": 0xE4,
            "pairing_callback": 0x56E6E0,
            "authentication_callback": 0x56E84C,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "official_later_oracle": "AmbiqSuite R4.4.1 import at 4264b930",
            "license": "Apache-2.0",
            "independent_release_discriminator": True,
            "discriminator": "responder retains the r20 security-request-timeout action and timeout/cleanup API-pair-request transitions",
            "initiator_release_invariant": True,
            "historical_generating_commit_resolved": False,
        },
        "production": {"stock_bytes_replaced": 0, "source_owned_bytes_added": 0},
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
        print("Cordio legacy SMP state machines closed: 2 init functions, 785 owned bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
