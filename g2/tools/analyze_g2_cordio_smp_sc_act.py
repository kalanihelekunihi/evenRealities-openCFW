#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio shared SMP SC actions."""

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
MAP = ROOT / "tools/manifests/packetcraft-cordio-smp-sc-act-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-smp-sc-act-provenance.tsv"
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smp_sc_act.c"
PRODUCTION_SOURCE_SIZE = 39_464
PRODUCTION_SOURCE_SHA256 = "2b7977d36ee69f70159a51538dc41b9c447bf572a0e7f4932a5f2965454396cf"
PRODUCTION_ROUTES = {
    "open_cfw_cordio_smp_sc_act_cat_initiator_address": (174816, 140, "8673fff8de0b7adaf9ef05c42f31c6a63579b08c5d1653454c256bb4b8875828"),
    "open_cfw_cordio_smp_sc_act_cat_responder_address": (174956, 140, "7361424cbe209d3868f68ef3675dba452a8a392802f07f59016b8620609db7c0"),
    "open_cfw_cordio_smp_sc_act_process_pairing": (175096, 568, "e93de190e3da29ead1c8ea900522d7cb71626fbbbfbcaa13b38a0192d9938011"),
    "open_cfw_cordio_smp_sc_act_authentication_request": (175664, 104, "eb5fe0341568fcbd160fac134cd4f951a40909be0c4be64b1ed96c85c751d345"),
    "open_cfw_cordio_smp_sc_act_cleanup": (175768, 18, "5267eee1ec549ec988fd0f29e85483e0d016962313b19e1cf47f2984fb21707c"),
    "open_cfw_cordio_smp_sc_act_pairing_failed": (175788, 22, "ada38ba9056b6daa9d9e3c601fd9f69b769c3ef93b054ddf14303240a1f3b03b"),
    "open_cfw_cordio_smp_sc_act_pairing_cancel": (175812, 24, "4fa680ce91f1222b002200ee967eb48313f1f13f61a0f060d88af88e96fd252d"),
    "open_cfw_cordio_smp_sc_act_authentication_select": (175836, 108, "703407c9b9716a99eb5b105d2506b6861991f962b2644b4abbd2317f88585381"),
    "open_cfw_cordio_smp_sc_act_passkey_setup": (175944, 52, "2976ca2197029d7df4c1aedf79cb6658d337b09131b940c0096a3837a0ad32e9"),
    "open_cfw_cordio_smp_sc_act_jwnc_calculate_f4": (175996, 66, "98984975879420f8964b15efcf4e1560a0bf2b524ae93c65fac704ae55e76f9b"),
    "open_cfw_cordio_smp_sc_act_jwnc_calculate_g2": (176064, 94, "8632b5661e0d69a19657857e8ab74a7a00f552ebeb7717a52b490515a1790e87"),
    "open_cfw_cordio_smp_sc_act_jwnc_display": (176160, 60, "70f6093d3e1baf48480fa3992cc8c96ebc35353fd5363b64f9b4cb3df6fb67f3"),
    "open_cfw_cordio_smp_sc_act_passkey_receive": (176220, 62, "feb99f2fe75fb7eddb430f44ff446b288c071f1c66363f6129f94ec4bf664fa9"),
    "open_cfw_cordio_smp_sc_act_passkey_send": (176284, 74, "ceeed3e2d2688074bf782006d4298c9808b9ca355293afac56c47920e1904c7c"),
    "open_cfw_cordio_smp_sc_act_calculate_shared_secret": (176360, 100, "88bcf4be138cf0b4317924ecfc3c9717df58d8d0e5dfef7f3ce9183c275020e0"),
    "open_cfw_cordio_smp_sc_act_calculate_f5_t": (176460, 170, "063e66c1cfb0b983500aba5a4d7d63bfa590dd60a6fad3efa691e2463b1fc71f"),
    "open_cfw_cordio_smp_sc_act_calculate_f5_mac": (176632, 120, "80ab81575e56bd3cf1d87867cb730b716a6a542b2dcda27f9e10514b0d173cf0"),
    "open_cfw_cordio_smp_sc_act_calculate_f5_ltk": (176752, 118, "69d8d637a2367265dfa6f22479cfd3a31ab965a3fa741a6507ca0f766667f444"),
    "open_cfw_cordio_smp_sc_act_calculate_f6_ea": (176872, 110, "8ec5083684a8bb5bcfd3387cccbb58343d9a8af983de8ddac1d1ce4e3496924a"),
    "open_cfw_cordio_smp_sc_act_calculate_f6_eb": (176984, 108, "880820328e879b16d0278becabcbee5b88c7c28cd587ddc3b12d99edacbd75b6"),
}
PINS = {
    MAP: "dbed6294647a497c8a03764d213f4ffe19b336bf7eea7349acc61ab4e55649da",
    PROVENANCE: "7e68aba87cffb3daf21d8ccf7d9c5b8f46e7a217f0125bf4c6f4abb92a0b3530",
}

CALLERS = {
    "smpScCatInitiatorBdAddr": [0x5E2F34, 0x5E2FB2, 0x5E3044, 0x5E30C2],
    "smpScCatResponderBdAddr": [0x5E2F3C, 0x5E2FBA, 0x5E304C, 0x5E30BA],
    "smpScProcPairing": [],
    "smpScAuthReq": [],
    "smpScActCleanup": [0x5E2B48],
    "smpScActPairingFailed": [0x5E2B68],
    "smpScActPairingCancel": [],
    "smpScActAuthSelect": [0x5E3476, 0x5E3DD8],
    "smpScActPkSetup": [],
    "smpScActJwncCalcF4": [0x5E3524, 0x5E3E30],
    "smpScActJwncCalcG2": [0x5E355A, 0x5E3E6E],
    "smpScActJwncDisplay": [0x5E3E94],
    "smpScActPkKeypress": [],
    "smpScActPkSendKeypress": [],
    "smpScActCalcSharedSecret": [0x5E37AC, 0x5E4140],
    "smpScActCalcF5TKey": [],
    "smpScActCalcF5MacKey": [],
    "smpScActCalcF5Ltk": [],
    "smpScActDHKeyCalcF6Ea": [],
    "smpScActDHKeyCalcF6Eb": [],
}
EXPECTED_STORED_ENTRIES = [
    (0x56D824, 0x5E2785), (0x56D828, 0x5E2ABB),
    (0x6D0B68, 0x5E2B2D), (0x6D0B6C, 0x5E2B3F),
    (0x6D0B74, 0x5E2B57), (0x6D0BD0, 0x5E2BDF),
    (0x6D0BD4, 0x5E2D81), (0x6D0BD8, 0x5E2DC7),
    (0x6D0C10, 0x5E2E73), (0x6D0C14, 0x5E2EDB),
    (0x6D0C18, 0x5E2F61), (0x6D0C1C, 0x5E2FDF),
    (0x6D0C20, 0x5E3063),
    (0x6D1218, 0x5E2B2D), (0x6D121C, 0x5E2B3F),
    (0x6D1220, 0x5E2B57), (0x6D1290, 0x5E2D21),
    (0x6D1294, 0x5E2BDF), (0x6D1298, 0x5E2D81),
    (0x6D129C, 0x5E2DC7), (0x6D12C0, 0x5E2E11),
    (0x6D12C4, 0x5E2E73), (0x6D12C8, 0x5E2EDB),
    (0x6D12CC, 0x5E2F61), (0x6D12D0, 0x5E2FDF),
    (0x6D12D4, 0x5E3063),
]
# These are even packed-data windows, not Cortex-M function pointers.
EVEN_INTERIOR_WINDOWS = [(0x63944B, 0x5E2F00), (0x685CB0, 0x5E2F00)]
# The lightweight raw decoder starts on the second halfword of two valid
# 32-bit arithmetic instructions. Pin those known false BL interpretations.
FALSE_INTERIOR_BRANCH_DECODES = [
    (0x4F26E8, 0x5E2CF4), (0x4F270E, 0x5E2D1A),
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
    spec = importlib.util.spec_from_file_location("smp_sc_act_thumb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_rows() -> tuple[list[tuple[str, int, int, str]], list[str]]:
    linked = []
    excluded = []
    with MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] == "linked":
                linked.append((row["function"], int(row["stock_start"], 0),
                               int(row["stock_end_exclusive"], 0), row["stock_sha256"]))
            elif row["stock_status"] == "configuration_excluded":
                excluded.append(row["function"])
            else:
                raise RuntimeError("unexpected shared SC action status")
    return linked, excluded


def production_report(
    linked: list[tuple[str, int, int, str]],
) -> dict:
    source = PRODUCTION_SOURCE.read_bytes()
    if len(source) != PRODUCTION_SOURCE_SIZE or sha(source) != PRODUCTION_SOURCE_SHA256:
        raise RuntimeError("Cordio SMP SC action production source identity changed")
    required_tokens = (
        "G2/R4 behavior: retain MITM for no-input/no-output JW.",
        "OPEN_CFW_SMP_SC_ACT_IO_NONE",
        "open_cfw_retained_cordio_sec_ecc_gen_shared_secret",
    )
    text = source.decode("utf-8")
    if any(token not in text for token in required_tokens):
        raise RuntimeError("Cordio SMP SC action hybrid behavior changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    leaves = {
        row["function"]: row for row in overlay.get("relocated_leaves", [])
        if row.get("function") in PRODUCTION_ROUTES
    }
    patches = {
        row["target_function"]: row for row in overlay.get("patch_sites", [])
        if row.get("target_function") in PRODUCTION_ROUTES
    }
    if set(leaves) != set(PRODUCTION_ROUTES) or set(patches) != set(PRODUCTION_ROUTES):
        raise RuntimeError("Cordio SMP SC action production routing is incomplete")
    source_path = PRODUCTION_SOURCE.relative_to(ROOT).as_posix()
    for (function, (offset, size, digest)), stock_row in zip(
        PRODUCTION_ROUTES.items(), linked
    ):
        stock_name, stock_start, stock_end, stock_digest = stock_row
        leaf = leaves[function]
        record = leaf.get("source", {})
        if (
            leaf.get("profiles") != ["apple-clang"]
            or record.get("path") != source_path
            or record.get("size") != PRODUCTION_SOURCE_SIZE
            or record.get("sha256") != PRODUCTION_SOURCE_SHA256
            or record.get("license") != "Apache-2.0"
            or record.get("upstream_commit")
            != "4264b9309e03064ffad13a0468d5d0c1110c5288"
            or leaf.get("expected", {}).get("offset") != offset
            or leaf.get("expected", {}).get("size") != size
            or leaf.get("expected", {}).get("sha256") != digest
            or leaf.get("strict_relocation_contract") is not True
        ):
            raise RuntimeError(
                f"Cordio SMP SC action production leaf changed: {function}"
            )
        patch = patches[function]
        if (
            patch.get("profiles") != ["apple-clang"]
            or patch.get("runtime_address") != stock_start
            or patch.get("expected_size") != stock_end - stock_start
            or patch.get("expected_sha256") != stock_digest
            or patch.get("branch") != "b_w"
        ):
            raise RuntimeError(
                f"Cordio SMP SC action stock patch changed: {stock_name}"
            )

    return {
        "status": (
            "production-routed authenticated AmbiqSuite R4.4.1 definitions "
            "with the stock G2 R4/r19 no-I/O association-model branch"
        ),
        "candidate": source_path,
        "production_routed": True,
        "live_functions": len(PRODUCTION_ROUTES),
        "relocated_functions": len(PRODUCTION_ROUTES),
        "compiled_leaf_bytes": sum(route[1] for route in PRODUCTION_ROUTES.values()),
        "source_owned_bytes_added": 2_276,
        "stock_bytes_replaced": sum(end - start for _, start, end, _ in linked),
        "hardware_validation": (
            "deferred by project direction; future qualification requires authorized G2/EM9305 Secure Connections "
            "pairing, numeric comparison, passkey/key-press, OOB, F4/G2/F5/F6, "
            "DH-key, cancellation, and interoperability physical evidence"
        ),
    }


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise RuntimeError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise RuntimeError(f"pinned input changed: {path}")

    rows, excluded = load_rows()
    if len(rows) != 20 or excluded != ["SmpScEnableZeroDhKey"]:
        raise RuntimeError("source inventory changed")
    bodies = []
    for name, start, end, digest in rows:
        body = image_slice(blob, start, end)
        if len(body) != end - start or sha(body) != digest:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != "cee95996181d0a9836a45338891e214d755c23cdd0d6263372d73c498d0ffbd6":
        raise RuntimeError("body concatenation changed")
    if sha(image_slice(blob, 0x5E267C, 0x5E3118)) != "241c1ba219999a6194f12f6a338ac39e80d1e1e3dd4535adadd64c4b48b7cd43":
        raise RuntimeError("physical object changed")
    tail = image_slice(blob, 0x5E30E2, 0x5E3118)
    if sha(tail) != "4f3f441888b40377d33f10e898c18f0a4714116b06dd5dc389b4527ae9f03867":
        raise RuntimeError("owned tail changed")
    if tail[:14] != b"\0\0T\0\0\0MAC\0LTK\0":
        raise RuntimeError("shared SC tail labels changed")
    if list(struct.unpack("<10I", tail[14:])) != [
        0x20070AEC, 0x200004B8, 0x78E6F4, 0x78E6FC, 0x78E704,
        0x783870, 0x77BF74, 0x7890D0, 0x78F3FC, 0x78C170,
    ]:
        raise RuntimeError("shared SC literal pool changed")
    # R4/r19 behavior retained by stock but removed from Packetcraft r20:
    # after numeric-comparison selection, either IO capability value 3 forces
    # justWorks false. This instruction sequence is the exact extra branch.
    if image_slice(blob, 0x5E2938, 0x5E294E) != bytes.fromhex(
            "002508e094f82800032803d094f82100032800d10025"):
        raise RuntimeError("no-input/no-output pairing branch changed")

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
    interior_decodes = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            calls[starts[target]].append(address)
        elif target in interiors:
            interior_decodes.append((address, target))
    if calls != CALLERS:
        raise RuntimeError("direct shared SC entry-call closure changed")
    if interior_decodes != FALSE_INTERIOR_BRANCH_DECODES:
        raise RuntimeError("shared SC interior branch-decode closure changed")
    if len(outbound) != 112:
        raise RuntimeError("shared SC outbound-call closure changed")

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
        raise RuntimeError("stored shared SC entry-pointer closure changed")
    if stored_interiors != EVEN_INTERIOR_WINDOWS:
        raise RuntimeError("shared SC interior-looking windows changed")
    if any(value & 1 for _, value in stored_interiors):
        raise RuntimeError("shared SC strict-interior Thumb pointer found")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x5E267C,
            "end_exclusive": 0x5E3118,
            "physical_bytes": 2716,
            "linked_function_count": 20,
            "linked_function_bytes": 2662,
            "owned_noncode_bytes": 54,
            "source_inventory_functions": 21,
            "source_only_functions": ["SmpScEnableZeroDhKey"],
            "configuration_excluded_functions": ["SmpScEnableZeroDhKey"],
            "direct_bl_ingress_sites": 19,
            "external_direct_bl_ingress_sites": 9,
            "registered_function_pointer_cells": 26,
            "registered_function_roots": 15,
            "strict_interior_pointers": 0,
            "false_interior_branch_decodes": 2,
            "even_interior_looking_windows": 2,
            "decoded_outbound_bl_sites": 112,
        },
        "architecture": {
            "retained_source_path": None,
            "smp_cb": 0x20070AEC,
            "smp_config_pointer": 0x200004B8,
            "f5_text_length": 0x54,
            "f5_salt": 0x7890D0,
            "f5_key": 0x78F3FC,
            "proc_pairing_pointer_cell": 0x56D824,
            "auth_req_pointer_cell": 0x56D828,
            "next_unit_entry": 0x5E3118,
        },
        "lineage": {
            "selected_exact_later_oracle": "AmbiqSuite R4.4.1 import at 4264b930",
            "selected_blob": "65d79f72b9e7536e554bb183c56f14bccc00b5af",
            "selected_sha256": "6e77a1429fe3bee3c0638c39d3784cfe7a9a789f3cf55be4b3e48a10ef360e34",
            "public_definition_base": "Packetcraft r19.02 for smpScProcPairing; r20.05c for the remaining invariant definitions",
            "license": "Apache-2.0",
            "independent_release_discriminator": True,
            "discriminator": "stock retains the R4/r19 no-input/no-output MITM branch removed from Packetcraft r20.05-c",
            "r20_message_and_table_abi": True,
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
        print("Cordio smp_sc_act closed: 20 linked, 1 config-excluded; R4/r19 pairing branch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
