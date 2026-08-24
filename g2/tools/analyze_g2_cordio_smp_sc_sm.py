#!/usr/bin/env python3
"""Fail-closed audit for G2 Cordio SMP SC initiator/responder state machines."""

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
LOAD_BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/packetcraft-cordio-smp-sc-sm-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-smp-sc-sm-provenance.tsv"
TABLE_MAP = ROOT / "tools/manifests/packetcraft-cordio-smp-sc-sm-table-map.tsv"
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smp_sc_sm.c"
OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
OVERLAY_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
PRODUCTION_SOURCE_SIZE = 16284
PRODUCTION_SOURCE_SHA256 = "6bc75e8320b1ceabff762f64ba655b12f5a18c8539a5258a5c8d61f08d2a8739"
PRODUCTION_FUNCTIONS = (
    "open_cfw_cordio_smpi_sc_initialize",
    "open_cfw_cordio_smpi_sc_state_string",
    "open_cfw_cordio_smpr_sc_initialize",
    "open_cfw_cordio_smpr_sc_state_string",
)
PRODUCTION_PATCHES = {
    "replace_cordio_smpi_sc_initialize": (0x00537F14, 16),
    "replace_cordio_smpi_sc_state_string": (0x00537F24, 276),
    "replace_cordio_smpr_sc_initialize": (0x00538104, 16),
    "replace_cordio_smpr_sc_state_string": (0x00538114, 290),
}
PRODUCTION_DISPATCH_SIZE = 1495
PRODUCTION_DISPATCH_SHA256 = "9438c7c72904056d2d0f6e9a4ce322cb1e52198738aef88558b35d5281bda801"
PINNED_INPUTS = {
    FUNCTION_MAP: "40965f3bb294bbd20ec25f740c28150d25e1f554692403fff5f01c61b74c89b9",
    PROVENANCE: "78a5e95dac7acedf37595b8d307eb6c21ab4fc7af6b38161709c29859949899d",
    TABLE_MAP: "7261869afdc4c187fdb5ad838c3e990f03f5f3fc39db1fa3957444b319c55c59",
}

EXPECTED_CALLS = {
    "SmpiScInit": [0x004B8080],
    "smpiStateStr": [0x0056D466],
    "SmprScInit": [0x004B8088],
    "smprStateStr": [0x0056D46E],
}

ROLES = {
    "initiator": {
        "physical": (0x00537F14, 0x005380DC),
        "physical_sha256": "f3064c0be233c40088ecb5885ec0d7c89aa19c65f99ab1bcb18f927a692d8b98",
        "tail": (0x00538038, 0x005380DC),
        "tail_sha256": "95d13191e60864b2a9a061abddff03d1929aa34c800816229f2eb1c94f53ef48",
        "interface": 0x0078C320,
        "interface_sha256": "1508b605bff288e2b52c70a9da85a432d7cadd5c69906a61afb4bc1c100af5c0",
        "action_count": 51,
        "action_sha256": "2f7d77ff2105f2a6153d40c15bff8ed0ee8197df738ea1547ff57a023185dd01",
        "state_count": 38,
        "state_pointer_sha256": "8dcc4c5a65d77037ce373b6682bba705c9753c7a5338f94d3ef7b106bea44877",
        "state_entry_bytes": 345,
        "state_entry_sha256": "bc2cc72e72729f50e4798d141300e8a38e8492f1d233c0ce06b2f833d98175a1",
        "owned_bytes": 1169,
        "owned_sha256": "36d79cdd666d033f2c936895a1250578108f8034ad463f6bf4a61d8e1480a43f",
        "smp_cb_offset": 0xE8,
    },
    "responder": {
        "physical": (0x00538104, 0x005382E4),
        "physical_sha256": "9d2c76c594328e391b1befb588ccd45131a078f13ee8edcb55c217581c7eb663",
        "tail": (0x00538236, 0x005382E4),
        "tail_sha256": "0c2743b98127e77960b4313dd346e6dfec799c9f82a2003d828f74066d521b85",
        "interface": 0x0078C470,
        "interface_sha256": "d7b358d531fbc4969b6f7a9b89b7d607251993e16f46e946c32f4fed47c34cf7",
        "action_count": 55,
        "action_sha256": "bbcc96d09c9c3d6842797ab8c9c61604dca828aaaf230fba8e5df96d77245718",
        "state_count": 40,
        "state_pointer_sha256": "872a6660494cf59f8c2e18110d460ebd1a35e08163f65d286dbecf143d0e5080",
        "state_entry_bytes": 390,
        "state_entry_sha256": "382342288ac6a9e9ebbfd4c4fbb51af5ff6ecba8fdaf81432f5676aa7d211eeb",
        "owned_bytes": 1262,
        "owned_sha256": "15ada20aace7996dbcc692d7eef76a374690251494703a43b3043e450d406057",
        "smp_cb_offset": 0xE4,
    },
}

COMBINED_BODY_SHA256 = "6b6deafa0a0f983caff67e6360fa0865114c9d5b33dbd1988a9febd6fc113f42"
COMBINED_PHYSICAL_SHA256 = "dece9269c8ed132e0c2329b226c3db5e3f593464f9ddd046fc6bcc65dc2be71a"
SMPR_API_PAIR_REQUEST = bytes.fromhex(
    "0a00010602140700020300010800010900010f01031f0001000000"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def read_u32(blob: bytes, address: int) -> int:
    return struct.unpack_from("<I", blob, address - LOAD_BASE)[0]


def load_functions() -> list[dict[str, object]]:
    rows = []
    with FUNCTION_MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] != "linked":
                raise RuntimeError(f"unexpected source-only function: {row['function']}")
            rows.append(
                {
                    "source_file": row["source_file"],
                    "name": row["function"],
                    "start": int(row["stock_start"], 0),
                    "end": int(row["stock_end_exclusive"], 0),
                    "size": int(row["stock_bytes"]),
                    "sha256": row["stock_sha256"],
                }
            )
    return rows


def load_decoder():
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("smp_sc_sm_thumb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_state_table(blob: bytes, address: int) -> bytes:
    """Read one three-column state table through its {0,0,0} terminator."""
    rows = []
    for index in range(64):
        row = image_slice(blob, address + index * 3, address + index * 3 + 3)
        if len(row) != 3:
            raise RuntimeError(f"state table leaves image at {address:#x}")
        rows.append(row)
        if row == b"\0\0\0":
            return b"".join(rows)
    raise RuntimeError(f"unterminated state table at {address:#x}")


def verify_role(blob: bytes, role: str, config: dict[str, object]) -> dict:
    physical_start, physical_end = config["physical"]
    physical = image_slice(blob, physical_start, physical_end)
    if sha256(physical) != config["physical_sha256"]:
        raise RuntimeError(f"{role} physical object changed")

    tail_start, tail_end = config["tail"]
    if sha256(image_slice(blob, tail_start, tail_end)) != config["tail_sha256"]:
        raise RuntimeError(f"{role} literal tail changed")

    interface = config["interface"]
    interface_data = image_slice(blob, interface, interface + 12)
    if sha256(interface_data) != config["interface_sha256"]:
        raise RuntimeError(f"{role} interface changed")
    state_root, action_root, common_root = struct.unpack("<III", interface_data)

    action_count = config["action_count"]
    action_data = image_slice(blob, action_root, action_root + action_count * 4)
    if sha256(action_data) != config["action_sha256"]:
        raise RuntimeError(f"{role} action table changed")
    action_targets = struct.unpack(f"<{action_count}I", action_data)
    if not all(target & 1 for target in action_targets):
        raise RuntimeError(f"{role} action table contains non-Thumb target")

    state_count = config["state_count"]
    pointer_data = image_slice(blob, state_root, state_root + state_count * 4)
    if sha256(pointer_data) != config["state_pointer_sha256"]:
        raise RuntimeError(f"{role} state-pointer table changed")
    state_targets = struct.unpack(f"<{state_count}I", pointer_data)
    if len(set(state_targets)) != state_count:
        raise RuntimeError(f"{role} state-pointer table aliases entries")

    state_tables = [read_state_table(blob, common_root)]
    state_tables.extend(read_state_table(blob, target) for target in state_targets)
    state_data = b"".join(state_tables)
    if len(state_data) != config["state_entry_bytes"]:
        raise RuntimeError(f"{role} state-entry byte count changed")
    if sha256(state_data) != config["state_entry_sha256"]:
        raise RuntimeError(f"{role} state-entry tables changed")

    owned = physical + interface_data + action_data + pointer_data + state_data
    if len(owned) != config["owned_bytes"] or sha256(owned) != config["owned_sha256"]:
        raise RuntimeError(f"{role} owned-byte concatenation changed")

    literal = tail_start if role == "initiator" else tail_start + 2
    if read_u32(blob, literal) != interface or read_u32(blob, literal + 4) != 0x20070AEC:
        raise RuntimeError(f"{role} initializer literals changed")

    return {
        "physical_start": physical_start,
        "physical_end_exclusive": physical_end,
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
    }


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise RuntimeError("official image changed")
    for path, digest in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != digest:
            raise RuntimeError(f"pinned input changed: {path}")

    functions = load_functions()
    bodies = []
    for function in functions:
        body = image_slice(blob, function["start"], function["end"])
        if len(body) != function["size"] or sha256(body) != function["sha256"]:
            raise RuntimeError(f"function body changed: {function['name']}")
        bodies.append(body)
    if sha256(b"".join(bodies)) != COMBINED_BODY_SHA256:
        raise RuntimeError("combined function-body digest changed")

    physical_parts = [image_slice(blob, *ROLES[role]["physical"]) for role in ROLES]
    if sha256(b"".join(physical_parts)) != COMBINED_PHYSICAL_SHA256:
        raise RuntimeError("combined physical-object digest changed")

    role_reports = {
        role: verify_role(blob, role, config) for role, config in ROLES.items()
    }
    responder_state_root = role_reports["responder"]["state_pointer_table"]
    api_pair_request = read_state_table(blob, read_u32(blob, responder_state_root + 4))
    if api_pair_request != SMPR_API_PAIR_REQUEST:
        raise RuntimeError("r20 responder API-pair-request discriminator changed")

    decoder = load_decoder()
    starts = {function["start"]: function["name"] for function in functions}
    calls = {function["name"]: [] for function in functions}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            calls[starts[target]].append(address)
    if calls != EXPECTED_CALLS:
        raise RuntimeError("direct-call ingress changed")

    interiors = set()
    for function in functions:
        interiors.update(range(function["start"] + 2, function["end"], 2))
    entry_values = []
    interior_values = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in starts:
            entry_values.append((LOAD_BASE + offset, value))
        elif target in interiors:
            interior_values.append((LOAD_BASE + offset, value))
    if entry_values or interior_values:
        raise RuntimeError("stored function-entry/interior closure changed")

    source = PRODUCTION_SOURCE.read_bytes()
    if len(source) != PRODUCTION_SOURCE_SIZE or sha256(source) != PRODUCTION_SOURCE_SHA256:
        raise RuntimeError("production SC state-machine source changed")
    overlay_config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
    configured_leaves = {
        item.get("function"): item
        for item in overlay_config.get("relocated_leaves", [])
        if item.get("function") in PRODUCTION_FUNCTIONS
    }
    if tuple(configured_leaves) != PRODUCTION_FUNCTIONS:
        raise RuntimeError("production SC state-machine leaf order changed")
    configured_sites = {
        item.get("name"): item
        for item in overlay_config.get("patch_sites", [])
        if item.get("name") in PRODUCTION_PATCHES
    }
    for name, (address, size) in PRODUCTION_PATCHES.items():
        site = configured_sites.get(name)
        if (
            site is None
            or site.get("runtime_address") != address
            or site.get("expected_size") != size
            or site.get("branch") != "b_w"
            or site.get("target_function") not in PRODUCTION_FUNCTIONS
        ):
            raise RuntimeError(f"production route changed: {name}")
    data_groups = overlay_config.get("in_place_data", [])
    data_group = next(
        (
            item for item in data_groups
            if item.get("symbol") == "open_cfw_cordio_smp_sc_dispatch"
        ),
        None,
    )
    if (
        data_group is None
        or data_group.get("expected", {}).get("size") != PRODUCTION_DISPATCH_SIZE
        or data_group.get("expected", {}).get("sha256") != PRODUCTION_DISPATCH_SHA256
        or len(data_group.get("placements", [])) != 86
    ):
        raise RuntimeError("production SC dispatch-data contract changed")

    build_report = json.loads(OVERLAY_REPORT.read_text(encoding="utf-8"))
    reported_functions = build_report.get("overlay", {}).get("functions", {})
    if any(name not in reported_functions for name in PRODUCTION_FUNCTIONS):
        raise RuntimeError("production SC state-machine functions are not built")
    reported_sites = {
        item.get("name"): item
        for item in build_report.get("overlay", {}).get("patched_sites", [])
    }
    if any(name not in reported_sites for name in PRODUCTION_PATCHES):
        raise RuntimeError("production SC state-machine routes are not patched")
    reported_data = build_report.get("overlay", {}).get("patched_in_place_data", [])
    if (
        len([item for item in reported_data if item.get("symbol") == data_group["symbol"]])
        != 86
    ):
        raise RuntimeError("production SC dispatch data is not installed")

    return {
        "schema_version": 1,
        "module": {
            "translation_units": 2,
            "source_function_count": 4,
            "linked_function_count": len(functions),
            "linked_function_bytes": sum(function["size"] for function in functions),
            "physical_object_bytes": sum(len(part) for part in physical_parts),
            "dispatch_data_bytes": sum(
                report["owned_bytes"] - report["physical_bytes"]
                for report in role_reports.values()
            ),
            "total_identified_owned_bytes": sum(
                report["owned_bytes"] for report in role_reports.values()
            ),
            "direct_bl_ingress_sites": sum(map(len, EXPECTED_CALLS.values())),
            "stored_function_pointers": 0,
            "strict_interior_pointers": 0,
            "source_only_functions": [],
        },
        "roles": role_reports,
        "abi": {
            "smp_control_block": 0x20070AEC,
            "state_entry_bytes": 3,
            "connection_count": 3,
            "initiator_state_range": [0x00, 0x25],
            "responder_state_range": [0x00, 0x27],
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "license": "Apache-2.0",
            "independent_release_discriminator": True,
            "discriminator": (
                "responder has 55 actions plus r20 response-timeout and cleanup rows"
            ),
        },
        "production": {
            "source_path": str(PRODUCTION_SOURCE.relative_to(ROOT)),
            "function_count": 4,
            "compiled_closure_bytes": 1696,
            "alignment_bytes": 6,
            "dispatch_data_bytes": PRODUCTION_DISPATCH_SIZE,
            "dispatch_placement_count": 86,
            "stock_bytes_replaced": 2093,
            "source_owned_bytes_added": 3197,
            "all_function_entries_routed": True,
            "all_dispatch_data_installed": True,
            "hardware_validation": {
                "status": "blocked",
                "reason": (
                    "authorized physical G2/EM9305 pairing and controller "
                    "evidence is unavailable"
                ),
            },
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
        print("Cordio SMP SC state machines closed: 4 functions, 2,431 owned bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
