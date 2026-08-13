#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio ATT core and EATT defaults."""

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
BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
MAP = ROOT / "tools/manifests/packetcraft-cordio-att-main-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-att-main-provenance.tsv"
PINS = {
    MAP: "5600e22eaa76e7d7d2d242db6b3addfa170439fde7a2c24dab4c6bba51145807",
    PROVENANCE: "0540ef736d6ba874e550b85b86cdb80aa2ce6d6e73bc863efba824b211ad1f32",
}

FUNCTIONS = {
    "attL2cDataCback": (0x004B4DE0, 0x004B4E08, "3c50f4bdf27504015615ebde4a000ecd0add827de07d996a2d2f79ccf2f7bc3e"),
    "attL2cCtrlCback": (0x004B4E08, 0x004B4E50, "6b428384cbbbb0bb3af12907d8a9cd8ce85a05e99becc3c56df1710fe38b2973"),
    "attDmConnCback": (0x004B4E50, 0x004B4EE6, "2da7bc7e64dd8665aabd6496779be32587ab6058057c146597385d60f80c46b6"),
    "attEmptyHandler": (0x004B4EE6, 0x004B4EE8, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    "attEmptyConnCback": (0x004B4EE8, 0x004B4EEA, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    "attEmptyL2cCocCback": (0x004B4EEA, 0x004B4EEC, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    "attEmptyDataCback": (0x004B4EEC, 0x004B4EEE, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    "attCcbByConnId": (0x004B4EEE, 0x004B500E, "b30b7670536a697aafce0182527b1c212d22815e4e691a2d17d1e9c851baa187"),
    "attUuidCmp16to128": (0x004B5014, 0x004B5036, "10bde0c93db4f6cfc458c3ec4aca6deabafe00255914369e00a8e35584922897"),
    "attSetMtu": (0x004B503C, 0x004B5074, "22a9af0645faac9bb326fc8e9e6d6c4c3a87aa15214557df24f45c4ccc48194c"),
    "attExecCallback": (0x004B5074, 0x004B50AE, "d5e7273c4835f3ab83e0d62b9257981babf3ea45225f287df8d25e1c36ca1234"),
    "attMsgAlloc": (0x004B50AE, 0x004B50BA, "ec586584b19d0f893f16cc374f5b88d5433dc758526adb391f3052fe32113bcf"),
    "attL2cDataReq": (0x004B50BA, 0x004B50EA, "e23b6dde51fe9756ee94de9043a831d3357da1ae150525b7621275740741e19b"),
    "attMsgParam": (0x004B50F0, 0x004B50FE, "885ee48a6f1ceb9fe5398859700327f2f34aafb6e9a4242382ea668faf343cba"),
    "attDecodeMsgParam": (0x004B50FE, 0x004B511E, "f02b7da4dd68eab60e52e66a4341392c45e8d0ed4d8d3edb142357b3027fe825"),
    "AttHandlerInit": (0x004B511E, 0x004B5146, "3fd39a6ee0725a847482491557373f558cd27ca4b0c81b1c0e92846676e8f342"),
    "AttHandler": (0x004B5146, 0x004B519E, "525512ef36b7609b323f7e2f1f1180c330cf0f5c1311e80e62b49b69b01e3b35"),
    "AttRegister": (0x004B519E, 0x004B51C8, "ed79bfc1bdac45206752ff344bf1d3b6762f50e037bba3fcd485e4ebd41dac5f"),
    "AttConnRegister": (0x004B51C8, 0x004B51CE, "fb95ef4ad0ef59beb7aa654f7dc70edf1525df7aca53c28cf2a36c7b4e1965c2"),
    "AttGetMtu": (0x004B5204, 0x004B5210, "7662e7e48ade1931fd01f00faa5361c0866049bbd744de8f636aa75961796309"),
    "AttMsgFree": (0x004B5210, 0x004B522E, "89f7706f0724e9f3c90d64c48783c3a883b98a60d2044689335be19eee1bde99"),
}
SOURCE_ONLY = ["attCcbByHandle", "AttMsgAlloc"]
BODY_CONCAT_SHA = "c1530e0a1d6ed2ab1e0e0ac5bd9b63592cb0a97e2fc83b5ce78e4081ca4b6e0c"
PHYSICAL = (0x004B4DE0, 0x004B5230)
PHYSICAL_SHA = "0540437900968a8a29771142d36c14d9f4a5eafb21d606e779c58611367970ec"
GAPS = [
    (0x004B500E, 0x004B5014, "2c63161bef9b35aa71cbc37025db3d9c2a2f8a62b9bfc564af6b13e959cfddd6"),
    (0x004B5036, 0x004B503C, "0589b6037e4d1d238bf39b685cca6350a975d2f763efe27e97c6445588923adb"),
    (0x004B50EA, 0x004B50F0, "a09591f721837cb325df3b73b468bb33b75f20cd2ff47067c196ce64a3eace3d"),
    (0x004B51CE, 0x004B5204, "37adea647292dd4fc818fba46e533914d580ee152f5e9f10f5eba5612a7a033e"),
    (0x004B522E, 0x004B5230, "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
]

CALLERS = {
    "attL2cDataCback": [], "attL2cCtrlCback": [], "attDmConnCback": [],
    "attEmptyHandler": [], "attEmptyConnCback": [], "attEmptyL2cCocCback": [],
    "attEmptyDataCback": [],
    "attCcbByConnId": [0x004B4E10, 0x004B4E58, 0x004B5208],
    "attUuidCmp16to128": [0x0056B82A, 0x0056C59A, 0x0056C5A4, 0x0056C5CE],
    "attSetMtu": [0x004B52BC, 0x0056C91C],
    "attExecCallback": [0x004B506E, 0x004B51C2, 0x00531AEC, 0x00533946, 0x00533A1C],
    "attMsgAlloc": [0x004B5606, 0x004B572A, 0x004B5762, 0x004B57AE, 0x004B5802, 0x004B5964,
        0x00530E76, 0x005310B4, 0x00533D28, 0x00534CA6, 0x00534E36, 0x00539DFC,
        0x0056C492, 0x0056C502, 0x0056C8E0, 0x0056C986, 0x0056CB6A, 0x0056CC00,
        0x0056DB9C, 0x0056DC68, 0x0056DF1E, 0x0056E110, 0x0056E352, 0x005A5F4C,
        0x005A60FC, 0x005A6236],
    "attL2cDataReq": [0x00530E5E, 0x00530F02, 0x0053113E, 0x005339C2, 0x00534CD8,
        0x0056C90A, 0x0056CA86, 0x0056CB9C, 0x0056CD62, 0x0056DBD6, 0x0056DD78,
        0x0056E0BA, 0x0056E23E, 0x0056E4C4, 0x005A5F68, 0x005A6146, 0x005A6252],
    "attMsgParam": [0x005339E0], "attDecodeMsgParam": [0x00533C2E],
    "AttHandlerInit": [0x004B805E], "AttHandler": [], "AttRegister": [0x004B7EDA],
    "AttConnRegister": [0x004B7EE2], "AttGetMtu": [0x0046DEE4],
    "AttMsgFree": [0x00533DCA, 0x0056CD6C],
}
DIRECT_CALLEE_COUNT = 32
DIRECT_CALLEE_DIGEST = "17f4357b9ec3a4ca466ee1233b865d71ce41afada21564b8bc4433081b6d496a"
WIDE_SECOND_HALF = 0x004B5108
WIDE_SECOND_HALF_SHA = "f6ea3185763067598c4e1c90f02ecf6f680ab1b362609cd4812ee74eddc3da54"

ENTRY_POINTERS = [
    (0x004B51F4, 0x004B4E09), (0x004B51F8, 0x004B4DE1), (0x004B51FC, 0x004B4E51),
    (0x004B8788, 0x004B5147), (0x00535480, 0x004B4EE7),
    (0x007851E0, 0x004B4EED), (0x007851E4, 0x004B4EE7),
    (0x007851E8, 0x004B4EE7), (0x007851EC, 0x004B4EE9),
    (0x007851F0, 0x004B4EEB), (0x007851F4, 0x004B4EEB),
    (0x007851F8, 0x004B4EE7), (0x007851FC, 0x004B4EE9),
    (0x007852C0, 0x004B4EED),
]
ACCIDENTAL_INTERIORS = [
    (0x00579127, 0x004B4F00), (0x0064CF3B, 0x004B4EFF),
    (0x00759F95, 0x004B4F20), (0x00759FBA, 0x004B4F20),
    (0x0076536C, 0x004B4F20), (0x007653CA, 0x004B4F20),
    (0x007653EA, 0x004B4F20), (0x0076540B, 0x004B4F20),
    (0x0076544C, 0x004B4F20), (0x0077FE24, 0x004B4F5F),
    (0x00783662, 0x004B4F20), (0x007836D9, 0x004B4F20),
    (0x007836EF, 0x004B4F20), (0x00783704, 0x004B4F20),
    (0x00783716, 0x004B4F20), (0x00788F6C, 0x004B4F20),
    (0x00788F8C, 0x004B4F20),
]

ATT_CB = 0x200610AC
ATT_FCN_DEFAULT = 0x007851E0
EATT_FCN_DEFAULT = 0x007851F0
ATT_FCN_WORDS = [0x004B4EED, 0x004B4EE7, 0x004B4EE7, 0x004B4EE9]
EATT_FCN_WORDS = [0x004B4EEB, 0x004B4EEB, 0x004B4EE7, 0x004B4EE9]
PATH = (0x006DC754, 93, "73798944bdeaf345d5c5071788c28264b6ed61e721b7932ba787b0343e7b3e00")
LITERAL_WORDS = [0x200610AC, 0x0078CC4C, 0x006DC754, 0x0078CC54, 0x00747CEC,
    0x007851D0, 0x2000044C, 0x007851E0, 0x007851F0, 0x004B4E09,
    0x004B4DE1, 0x004B4E51, 0x200004B4]
BASE_UUID = bytes.fromhex("fb349b5f800000800010000000000000")


class AuditError(RuntimeError):
    """Raised when authenticated ATT-core evidence changes."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE:end - BASE]


def load_tool(name: str, filename: str):
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / filename)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_inventory() -> tuple[list[str], list[str]]:
    with MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    linked = [row["function"] for row in rows if row["stock_status"] == "linked"]
    source_only = [row["function"] for row in rows if row["stock_status"] == "source_only"]
    return linked, source_only


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise AuditError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise AuditError(f"pinned input changed: {path}")
    linked, source_only = source_inventory()
    if linked != list(FUNCTIONS) or source_only != SOURCE_ONLY:
        raise AuditError("att_main source inventory changed")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        body = image_slice(blob, start, end)
        if sha(body) != expected:
            raise AuditError(f"stock att_main body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != BODY_CONCAT_SHA:
        raise AuditError("att_main body concatenation changed")
    if sha(image_slice(blob, *PHYSICAL)) != PHYSICAL_SHA:
        raise AuditError("att_main physical object changed")
    for start, end, expected in GAPS:
        if sha(image_slice(blob, start, end)) != expected:
            raise AuditError(f"att_main owned data changed at {start:#x}")

    path_start, path_len, path_sha = PATH
    if sha(image_slice(blob, path_start, path_start + path_len)) != path_sha:
        raise AuditError("att_main retained path changed")
    if list(struct.unpack("<13I", image_slice(blob, 0x004B51D0, 0x004B5204))) != LITERAL_WORDS:
        raise AuditError("att_main literal pool changed")
    att_default = image_slice(blob, ATT_FCN_DEFAULT, ATT_FCN_DEFAULT + 16)
    eatt_default = image_slice(blob, EATT_FCN_DEFAULT, EATT_FCN_DEFAULT + 16)
    if list(struct.unpack("<4I", att_default)) != ATT_FCN_WORDS or sha(att_default) != "1c10c97a1c7e62a595752a5eafe39ee9ceea8b7f56cd1302147afb9d6f3daf68":
        raise AuditError("legacy ATT default interface changed")
    if list(struct.unpack("<4I", eatt_default)) != EATT_FCN_WORDS or sha(eatt_default) != "ed7e8fbf6a5cee43039a565ea591e8fe949fbd4901905e56cdc436423b2b8bd4":
        raise AuditError("EATT default interface changed")
    flashdb = load_tool("att_main_flashdb", "analyze_g2_flashdb.py")
    initialized = flashdb._decode_initialized_sram(blob)
    if flashdb._sram_slice(initialized, 0x2000044C, 16) != BASE_UUID:
        raise AuditError("ATT base UUID changed")

    decoder = load_tool("att_main_thumb", "recover_apollo_embedded_source_paths.py")
    starts = {start: name for name, (start, _, _) in FUNCTIONS.items()}
    direct_by_target: dict[int, list[int]] = {}
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target is not None:
            direct_by_target.setdefault(target, []).append(address)
    for name, (start, _, _) in FUNCTIONS.items():
        if direct_by_target.get(start, []) != CALLERS[name]:
            raise AuditError(f"att_main caller closure changed: {name}")
    callee_edges = []
    for start, end, _ in FUNCTIONS.values():
        for address in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None and address != WIDE_SECOND_HALF:
                callee_edges.append((address, target))
    if len(callee_edges) != DIRECT_CALLEE_COUNT or sha(b"".join(struct.pack("<II", *edge) for edge in callee_edges)) != DIRECT_CALLEE_DIGEST:
        raise AuditError("att_main direct-callee closure changed")
    if sha(image_slice(blob, WIDE_SECOND_HALF, WIDE_SECOND_HALF + 4)) != WIDE_SECOND_HALF_SHA:
        raise AuditError("att_main wide-instruction overlap changed")

    entries = set(starts)
    interiors = {address for start, end, _ in FUNCTIONS.values() for address in range(start + 1, end)}
    stored_entries, stored_interiors = [], []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in entries:
            stored_entries.append((BASE + offset, value))
        elif target in interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries != ENTRY_POINTERS or stored_interiors != ACCIDENTAL_INTERIORS:
        raise AuditError("att_main stored-entry/interior closure changed")
    for target, sites in direct_by_target.items():
        if target in interiors and sites:
            raise AuditError("direct BL into an att_main strict interior")

    return {
        "schema_version": 1,
        "module": {
            "classification": "linked_att_core_with_eatt_defaults",
            "start": PHYSICAL[0], "end_exclusive": PHYSICAL[1],
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end - start for start, end, _ in FUNCTIONS.values()),
            "owned_noncode_bytes": sum(end - start for start, end, _ in GAPS),
            "source_inventory_functions": len(FUNCTIONS) + len(SOURCE_ONLY),
            "source_only_functions": SOURCE_ONLY,
            "direct_bl_ingress_sites": sum(len(sites) for sites in CALLERS.values()),
            "registered_function_pointers": len(ENTRY_POINTERS),
            "direct_callee_sites": len(callee_edges),
            "raw_bl_like_wide_instruction_overlaps": 1,
            "accidental_interior_byte_windows": len(ACCIDENTAL_INTERIORS),
            "strict_interior_pointers": 0,
        },
        "dispatch": {
            "att_control_block": ATT_CB,
            "legacy_default_interface": ATT_FCN_DEFAULT,
            "eatt_default_interface": EATT_FCN_DEFAULT,
            "handler_entry": 0x004B5147,
            "handler_pointer_cell": 0x004B8788,
            "l2c_data_callback": 0x004B4DE1,
            "l2c_ctrl_callback": 0x004B4E09,
            "dm_connection_callback": 0x004B4E51,
        },
        "architecture": {
            "connection_count": 3, "bearers_per_connection": 3,
            "ccb_stride": 0x14, "att_cb_handler_id_offset": 0x60,
            "client_interface_offset": 0x3C, "server_interface_offset": 0x40,
            "eatt_server_interface_offset": 0x44, "eatt_client_interface_offset": 0x48,
            "eatt_handler_offset": 0x4C, "eatt_dm_callback_offset": 0x50,
            "eatt_l2c_data_req_offset": 0x54,
            "handler_message_thresholds": [0x20, 0x40, 0x60, 0x80],
            "eatt_defaults_installed_by_att_handler_init": True,
            "enhanced_att_runtime_override_seen_in_this_tu": False,
            "retained_source_path": PATH[0],
            "base_uuid_sram": 0x2000044C,
        },
        "lineage": {
            "selected_public_oracle": "AmbiqSuite R4.4.1 later official import; implementation-identical to Packetcraft r20.05-c",
            "selected_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "selected_blob": "decbdafce60ebc2fe2b9e986ffd97207fceebcb2",
            "selected_sha256": "38c4287295d85efd7c153495a51248397496e71f60b26cf5f1364e9317797359",
            "license": "Apache-2.0", "historical_generating_commit_resolved": False,
            "r20_eatt_architecture_proven": True,
        },
        "production": {"stock_bytes_replaced": 0, "source_owned_bytes_added": 0},
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
        print("Cordio att_main closed: 21 linked / 2 source-only; EATT defaults installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
