#!/usr/bin/env python3
"""Fail-closed exclusion audit for Cordio's alternative non-SMP implementation."""

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
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/packetcraft-cordio-smp-non-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-smp-non-provenance.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "37a70445e587f9eefc18b484f3cef2c3d2b820c68c9d0c64140990f8f25d9942",
    PROVENANCE: "63d7070004431b13f470afb96bb6dc95c61bb3bb42d249f43eedc4ca058a610b",
}

L2C_REGISTER = 0x00530B5E
DM_CONN_ID_BY_HANDLE = 0x004B6E96
DM_CONN_ROLE = 0x004B73C4
SMP_MSG_ALLOC = 0x00537BCA
L2C_DATA_REQ = 0x00530BBC
PROVIDER_TARGETS = {
    "L2cRegister": L2C_REGISTER,
    "DmConnIdByHandle": DM_CONN_ID_BY_HANDLE,
    "DmConnRole": DM_CONN_ROLE,
    "smpMsgAlloc": SMP_MSG_ALLOC,
    "L2cDataReq": L2C_DATA_REQ,
}
EXPECTED_CALLS = {
    "L2cRegister": [0x004B5138, 0x00537CEA],
    "DmConnIdByHandle": [
        0x00530784, 0x00530AAA, 0x00531A82, 0x005351AE,
        0x00536C6C, 0x00536EAE, 0x005375CC,
    ],
    "DmConnRole": [
        0x0046E118, 0x0046E12E, 0x0046E2C2, 0x0046E32A, 0x0046E4D4,
        0x00477AF4, 0x00477B32, 0x00477CBE, 0x004785A6, 0x004A0768,
        0x004A0786, 0x004A08DA, 0x004A094A, 0x004A098A, 0x004A09B0,
        0x004A0A7E, 0x004A0B4E, 0x004A0B8E, 0x004A0BB6, 0x004A0EEA,
        0x004A117E, 0x004A13B0, 0x004A1424, 0x004A14AC, 0x004A1D72,
        0x004B6D3C, 0x004B7720, 0x004B77BE, 0x004B7AF0, 0x004B7BFC,
        0x004B7D6A, 0x004B7DA8, 0x004B7DCA, 0x004B7DE8, 0x004BAD06,
        0x004BDC86, 0x004BDF2A, 0x004BE2A2, 0x004BE474, 0x004BE7C0,
        0x004BF7F0, 0x004BF80A, 0x004C4A6A, 0x004C4A7E, 0x004C4B40,
        0x00530796, 0x00531368, 0x00532AB2, 0x00535628, 0x00535662,
        0x0053567C, 0x005357B0, 0x00535818, 0x0053585E, 0x005358A8,
        0x005358EA, 0x0053593A, 0x005359E6, 0x00535ABE, 0x00535AE2,
        0x00535B28, 0x00535F46, 0x00535FCE, 0x005374C8, 0x005374E0,
        0x0053751A, 0x0056E97A, 0x0056F0F0,
    ],
    "smpMsgAlloc": [
        0x0056D006, 0x0056D070, 0x0056D0C4, 0x0056D118, 0x0056E632,
        0x0056E8F6, 0x0056EA16, 0x005E2DDE, 0x005E3140, 0x005E326A,
        0x005E38D6, 0x005E3AE8, 0x005E3C24,
    ],
    "L2cDataReq": [
        0x004B50CA, 0x004B561C, 0x004B5986, 0x00530B22,
        0x00534E9E, 0x00536F64, 0x00537272, 0x00537BB2,
    ],
}
EXPECTED_CALL_DIGESTS = {
    "L2cRegister": "fe9f2ec4b3a0e2a5b3fc9e857ca5d7c04438c768e0e1a71d30606205128c2490",
    "DmConnIdByHandle": "56dfbd82852f27bd2da130f7054402f136a15222db0dfa0e5864342959a25dbc",
    "DmConnRole": "ca27542bb64d90f478a919fa8a528a16a85fdac1072c9218af49fcf73f1f49f4",
    "smpMsgAlloc": "bb6d5d0baa5a7d2c6909b1b751540a8751643cfefd522d860bb15eaffc2fe091",
    "L2cDataReq": "303f14ee905ce3fb9d99c1f6aa3362a928aa346fc9f8efc2f764d50c1f03ceba",
}

ATT_REGISTRATION = (0x004B5132, 0x004B513C)
ATT_REGISTRATION_SHA256 = "9369b1e555c2f7453391147e5fdb4bd364aa4765aee27f61ac64af1c98cb9739"
SMP_REGISTRATION = (0x00537CE4, 0x00537CEE)
SMP_REGISTRATION_SHA256 = "c907f54d55ebd120a05f5218c260deee18a84857cfaac3bd1dc23256ea7f3789"
FULL_SMP_CALLBACK_POINTERS = {
    0x00537ED4: 0x00537445,
    0x00537ED8: 0x00537279,
}
ATT_CALLBACK_POINTERS = {
    0x004B51F4: 0x004B4E09,
    0x004B51F8: 0x004B4DE1,
}
ABSENT_MARKERS = (
    b"smp_non.c", b"smpNonL2cDataCback", b"smpNonL2cCtrlCback",
    b"SmpNonInit", b"SMP is not supported",
)


class AuditError(RuntimeError):
    """Raised when the authenticated non-SMP exclusion evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or last > len(blob) or first >= last:
        raise AuditError(f"invalid image span [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def occurrences(blob: bytes, value: int) -> list[int]:
    needle = struct.pack("<I", value)
    return [BASE + offset for offset in range(len(blob) - 3)
            if blob[offset:offset + 4] == needle]


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


def packed_digest(addresses: list[int]) -> str:
    return sha256(b"".join(struct.pack("<I", address) for address in addresses))


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned smp_non input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        functions = list(csv.DictReader(handle, delimiter="\t"))
    if len(functions) != 3:
        raise AuditError("smp_non source inventory changed")
    if any(row["stock_status"] != "dead_stripped" or row["stock_address"] != "-"
           for row in functions):
        raise AuditError("smp_non function classification changed")

    decoder = load_tool("smp_non_thumb", "recover_apollo_embedded_source_paths.py")
    calls = {name: [] for name in PROVIDER_TARGETS}
    targets_to_names = {target: name for name, target in PROVIDER_TARGETS.items()}
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        name = targets_to_names.get(target)
        if name is not None:
            calls[name].append(address)
    for name, expected in EXPECTED_CALLS.items():
        if calls[name] != expected or packed_digest(calls[name]) != EXPECTED_CALL_DIGESTS[name]:
            raise AuditError(f"{name} direct-call census changed")

    if sha256(image_slice(blob, *ATT_REGISTRATION)) != ATT_REGISTRATION_SHA256:
        raise AuditError("ATT L2CAP registration window changed")
    if sha256(image_slice(blob, *SMP_REGISTRATION)) != SMP_REGISTRATION_SHA256:
        raise AuditError("full SMP L2CAP registration window changed")
    for cell, target in {**FULL_SMP_CALLBACK_POINTERS, **ATT_CALLBACK_POINTERS}.items():
        if struct.unpack_from("<I", blob, cell - BASE)[0] != target:
            raise AuditError(f"registered callback pointer changed at 0x{cell:08x}")
        if occurrences(blob, target) != [cell]:
            raise AuditError(f"registered callback pointer closure changed for 0x{target:08x}")
    for marker in ABSENT_MARKERS:
        if marker in blob:
            raise AuditError(f"unexpected non-SMP marker appeared: {marker!r}")

    smp_main = load_tool("smp_non_smp_main", "analyze_g2_cordio_smp_main.py").analyze(image_path)
    linked_names = {item["name"] for item in smp_main["module"]["functions"]}
    required_full_smp = {
        "smpL2cDataCback", "smpL2cCtrlCback", "smpMsgAlloc",
        "SmpHandlerInit", "SmpHandler",
    }
    if not required_full_smp <= linked_names:
        raise AuditError("full SMP positive closure changed")

    return {
        "schema_version": 1,
        "image": {"path": str(image_path), "sha256": IMAGE_SHA256},
        "module": {
            "classification": "configuration_excluded_not_linked",
            "linked_function_count": 0,
            "linked_function_bytes": 0,
            "source_inventory_functions": len(functions),
            "source_only_functions": [row["function"] for row in functions],
            "retained_path_anchors": 0,
            "semantic_body_anchors": 0,
        },
        "exclusion": {
            "l2c_register_direct_calls": calls["L2cRegister"],
            "l2c_register_call_count": len(calls["L2cRegister"]),
            "registered_fixed_channels": [4, 6],
            "smp_registration_call": 0x00537CEA,
            "smp_data_callback": FULL_SMP_CALLBACK_POINTERS[0x00537ED8],
            "smp_control_callback": FULL_SMP_CALLBACK_POINTERS[0x00537ED4],
            "full_smp_required_functions_linked": sorted(required_full_smp),
            "smp_msg_alloc_calls_reviewed": len(calls["smpMsgAlloc"]),
            "l2c_data_req_calls_reviewed": len(calls["L2cDataReq"]),
            "dm_conn_id_by_handle_calls_reviewed": len(calls["DmConnIdByHandle"]),
            "dm_conn_role_calls_reviewed": len(calls["DmConnRole"]),
            "alternate_smp_registration_calls": 0,
            "alternate_smp_callback_pointers": 0,
            "retained_non_smp_markers": 0,
            "closure_argument": (
                "smp_non.c and smp_main.c are alternative CID-6 providers; the only stock "
                "CID-6 registration roots the complete smp_main callbacks, while every direct "
                "provider call required by the non-SMP data callback is already closed"
            ),
        },
        "lineage": {
            "selected_optional_release": "Packetcraft r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "b024dc746c712284f2cb0b54669358b3f3cbd0fd",
            "selected_sha256": "792892f2ca830fce8f1f0b280d098a9b188621fd5feb94a877a48b54779407b2",
            "later_r4_exact": True,
            "stock_body_version_discriminated": False,
            "implementation_delta_r19_to_r20": "none; license-header formatting only",
            "compatibility_basis": "surrounding stock full SMP implementation uses the r20/R4 ABI",
            "license": "Apache-2.0",
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
        print("Cordio smp_non excluded: 3 source-only functions; full SMP owns CID 6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
