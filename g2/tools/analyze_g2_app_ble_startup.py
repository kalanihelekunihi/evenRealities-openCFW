#!/usr/bin/env python3
"""Fail-closed audit for the G2 product BLE startup and adjacent vector body."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-app-ble-startup-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-app-ble-startup-provenance.tsv"
CLOSURE = ROOT / "tools/manifests/g2-app-ble-startup-closure.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "b281579c8c76a10b9066b4288eb26eb39403a0808451c05f1790a835f4f1ea5b",
    PROVENANCE: "79ef994d8a57c41e858a61d71a840d51d73042b39b2e21d6a1a5d0e8fcdc14db",
    CLOSURE: "9010e5413dcde827bc16e2849e5d9ab2416f9f439e0c87b9728c7e5e3e1692e4",
}

BODY_BYTES = 3_236
BODY_SHA256 = "60845b967cc5c6fb4c87f827d863defa45504ff642966e07aad9e2f4a284c025"
PRODUCT_BODY_BYTES = 3_192
PRODUCT_BODY_SHA256 = "48edec01b421a876d18a123ee28396ea52e07b73400f0dbb887af1f4d3bebaf2"
PHYSICAL_SPAN = (0x004B7478, 0x004B8122)
PHYSICAL_SHA256 = "1c36c8ffbc29b94e18b2a4f1804c30ac5389805a4833bb3c9e5d4b48bc0d7090"
DATA_ISLAND = (0x004B7F5E, 0x004B7F64)
DATA_ISLAND_SHA256 = "cef73a4084cae3cf39ea6be5260d9caa4512a825bf0230a69331bc922b101d55"
DIRECT_CALL_COUNT = 9
DIRECT_CALL_DIGEST = "b487e4d27642b496fdd3823ede5b237b719880cd8961c87fcffdfabcd020d7f4"
BODY_CALL_COUNT = 267
BODY_CALL_DIGEST = "b5892a23703b942c56d0da83479c6fe475f5bd2008859368a6c726ceee7d3f66"
STORED_ENTRIES = [
    (0x0043812C, 0x004B80BF),
    (0x004B7F60, 0x004B758B),
    (0x004B8734, 0x004B748D),
    (0x004B8738, 0x004B74F1),
    (0x004B8740, 0x004B7533),
    (0x004B8794, 0x004B7D33),
    (0x004B87A0, 0x004B758B),
]
STORED_ENTRY_DIGEST = "1474229354443ffea1abf12c4857fbbe40f8e25252a9a3e0c7828d3c9068cec8"
INTERIOR_LOOKALIKES = [(0x00479395, 0x004B7AD0), (0x004F5677, 0x004B78F8)]
INTERIOR_LOOKALIKE_DIGEST = "c894de0313efc8f6a6ebfe011f4f6f4dc5dec8b44a5895d86ecdcfa48d2d9560"

EXPECTED_CALLERS = {
    "bleSubsystemInit": [0x004B7EBC],
    "bleDmCback": [],
    "bleAttCback": [],
    "bleCccCback": [],
    "bleDelayedStartCback": [],
    "bleProcMsg": [0x004B7E58],
    "_bleCommHandler": [],
    "bleCommHandlerInit": [0x004B80AA],
    "bleStackRegister": [0x004B810A],
    "_bleExactleStackInit": [0x004B8106],
    "GPIO0_607F_IRQHandler": [],
    "APP_BleAddressGet": [0x0057E766, 0x00581152, 0x005A576E],
    "appBleStart": [0x004D0A6A],
}

LITERAL_WORDS = {
    0x004B81B4: 0x0078C9A4,  # product application configuration
    0x004B81FC: 0x200727F0,  # product BLE control block
    0x004B820C: 0x00711D94,  # retained app_ble.c path
    0x004B8210: 0x00789FF8,  # ble.comm category
    0x004B8478: 0x007516C8,  # DM connection diagnostic
    0x004B847C: 0x00784C80,  # _bleCommHandler
    0x004B8484: 0x006DF2C4,  # ring-connection diagnostic
    0x004B8720: 0x006D9C4C,  # prefixed ring diagnostic
    0x004B8724: 0x00774D44,  # runtime SMP configuration
    0x004B8728: 0x200004B8,  # pSmpCfg
    0x004B872C: 0x20074358,  # application configuration pointer slot
    0x004B8730: 0x200737B0,  # product application state
    0x004B8734: 0x004B748D,  # DM callback
    0x004B8738: 0x004B74F1,  # ATT callback
    0x004B873C: 0x005345AB,  # AppServerConnCback
    0x004B8740: 0x004B7533,  # CCC callback
    0x004B8744: 0x007518C0,  # six-entry CCC set
    0x004B8748: 0x005355E1,  # application discovery callback
    0x004B874C: 0x004B5B03,  # product profile callback
    0x004B8750: 0x004B5ADD,  # product profile callback
    0x004B8754: 0x004BDC9D,  # product service callback
    0x004B8758: 0x004BDF3D,  # product service callback
    0x004B875C: 0x004BE2B5,  # product service callback
    0x004B8760: 0x004BE487,  # product service callback
    0x004B8764: 0x004BE7D3,  # product service callback
    0x004B8768: 0x200003B0,  # WSF buffer-pool descriptor input
    0x004B876C: 0x2004FA98,  # WSF buffer memory
    0x004B8770: 0x007516EC,  # short memory-pool diagnostic
    0x004B8774: 0x00774BF4,  # _bleExactleStackInit
    0x004B8778: 0x0073BA34,  # prefixed memory-pool diagnostic
    0x004B877C: 0x00536815,  # HciHandler
    0x004B8780: 0x004D2A5D,  # DmHandler
    0x004B8784: 0x00536FA5,  # L2cSlaveHandler
    0x004B8788: 0x004B5147,  # AttHandler
    0x004B878C: 0x00537D0D,  # SmpHandler
    0x004B8790: 0x004BAE85,  # AppHandler
    0x004B8794: 0x004B7D33,  # product BLE handler
    0x004B8798: 0x004B4AB3,  # HciDrvHandler
    0x004B879C: 0x200737BF,  # six-byte product BLE address
    0x004B87A0: 0x004B758B,  # delayed callback
}

EXPECTED_STRINGS = {
    0x00711D94: r"D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble.c",
    0x00774BF4: "_bleExactleStackInit",
    0x00784C80: "_bleCommHandler",
    0x00789FF8: "ble.comm",
    0x007516EC: "Memory pool is too small by %d\r\n",
    0x0073BA34: "[ble.comm]Memory pool is too small by %d\r\n",
}


class AuditError(RuntimeError):
    """Raised when authenticated product BLE-startup evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or last > len(blob) or first >= last:
        raise AuditError(f"invalid image span [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def cstring(blob: bytes, address: int) -> str:
    first = address - BASE
    last = blob.find(b"\0", first)
    if first < 0 or last < first:
        raise AuditError(f"invalid C string at 0x{address:08x}")
    return blob[first:last].decode("ascii")


def packed_pairs_digest(pairs: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("app_ble_startup_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def thumb_wide_branch_target(address: int, first: int, second: int) -> int | None:
    """Decode an unconditional Thumb-2 B.W target (BL is checked separately)."""

    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    imm11 = second & 0x07FF
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | (imm11 << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned BLE-startup input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 13 or [int(row["recovery_order"]) for row in rows] != list(range(1, 14)):
        raise AuditError("BLE-startup body inventory changed")

    bodies: list[bytes] = []
    ranges: list[tuple[int, int]] = []
    starts: dict[int, str] = {}
    interiors: set[int] = set()
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"stock body changed: {row['function']}")
        bodies.append(raw)
        ranges.append((start, end))
        starts[start] = row["function"]
        interiors.update(range(start + 2, end, 2))
    if sum(map(len, bodies)) != BODY_BYTES or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("BLE-startup body concatenation changed")
    product_bodies = [
        raw for raw, row in zip(bodies, rows) if row["owner"] == "product app_ble.c"
    ]
    if (
        sum(map(len, product_bodies)) != PRODUCT_BODY_BYTES
        or sha256(b"".join(product_bodies)) != PRODUCT_BODY_SHA256
    ):
        raise AuditError("product app_ble.c body concatenation changed")
    if sha256(image_slice(blob, *PHYSICAL_SPAN)) != PHYSICAL_SHA256:
        raise AuditError("mixed BLE-startup physical interval changed")
    if sha256(image_slice(blob, *DATA_ISLAND)) != DATA_ISLAND_SHA256:
        raise AuditError("product callback data island changed")

    for cell, expected in LITERAL_WORDS.items():
        actual = struct.unpack("<I", image_slice(blob, cell, cell + 4))[0]
        if actual != expected:
            raise AuditError(f"BLE-startup literal changed at 0x{cell:08x}")
    for address, expected in EXPECTED_STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"BLE-startup retained string changed at 0x{address:08x}")

    decoder = load_decoder()
    callers = {name: [] for name in starts.values()}
    ingress: list[tuple[int, int]] = []
    interior_bl: list[tuple[int, int]] = []
    interior_wide_branch: list[tuple[int, int]] = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            ingress.append((address, target))
            callers[starts[target]].append(address)
        if target in interiors:
            interior_bl.append((address, target))
        first, second = struct.unpack("<HH", image_slice(blob, address, address + 4))
        target = thumb_wide_branch_target(address, first, second)
        if target in interiors:
            interior_wide_branch.append((address, target))
    if callers != EXPECTED_CALLERS:
        raise AuditError("BLE-startup direct callers changed")
    if len(ingress) != DIRECT_CALL_COUNT or packed_pairs_digest(ingress) != DIRECT_CALL_DIGEST:
        raise AuditError("BLE-startup direct-call ingress changed")
    if interior_bl or interior_wide_branch:
        raise AuditError("direct branch into BLE-startup strict interior appeared")

    body_calls: list[tuple[int, int]] = []
    for start, end in ranges:
        for address in range(start, end, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None:
                body_calls.append((address, target))
    if len(body_calls) != BODY_CALL_COUNT or packed_pairs_digest(body_calls) != BODY_CALL_DIGEST:
        raise AuditError("BLE-startup provider-call closure changed")

    stored_entries: list[tuple[int, int]] = []
    stored_interiors: list[tuple[int, int]] = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        address = BASE + offset
        if target in starts:
            stored_entries.append((address, value))
        elif target in interiors:
            stored_interiors.append((address, value))
    if stored_entries != STORED_ENTRIES or packed_pairs_digest(stored_entries) != STORED_ENTRY_DIGEST:
        raise AuditError("stored BLE-startup entry pointers changed")
    if (
        stored_interiors != INTERIOR_LOOKALIKES
        or packed_pairs_digest(stored_interiors) != INTERIOR_LOOKALIKE_DIGEST
        or any(address % 2 == 0 for address, _ in stored_interiors)
    ):
        raise AuditError("BLE-startup unaligned interior-lookalike classification changed")

    vector_value = struct.unpack("<I", image_slice(blob, 0x0043812C, 0x00438130))[0]
    if vector_value != 0x004B80BF:
        raise AuditError("GPIO0_607F vector changed")

    return {
        "schema_version": 1,
        "image": {"path": str(image_path), "sha256": IMAGE_SHA256},
        "surface": {
            "bounded_bodies": 13,
            "product_app_ble_bodies": 12,
            "foreign_vector_bodies": 1,
            "body_bytes": BODY_BYTES,
            "product_body_bytes": PRODUCT_BODY_BYTES,
            "mixed_physical_start": PHYSICAL_SPAN[0],
            "mixed_physical_end_exclusive": PHYSICAL_SPAN[1],
            "mixed_physical_bytes": PHYSICAL_SPAN[1] - PHYSICAL_SPAN[0],
            "direct_bl_ingress_sites": len(ingress),
            "direct_provider_calls": len(body_calls),
            "stored_entry_pointers": STORED_ENTRIES,
            "stored_strict_interior_pointers": 0,
            "excluded_unaligned_interior_lookalikes": len(stored_interiors),
            "direct_strict_interior_branches": 0,
            "whole_contiguous_app_ble_object": False,
        },
        "vector": {
            "table_base": 0x00438000,
            "cell": 0x0043812C,
            "vector_index": 75,
            "external_irq": 59,
            "irq_enum": "GPIO0_607F_IRQn",
            "handler": 0x004B80BE,
            "calls_hci_drv_int_service": False,
        },
        "startup": {
            "buffer_pool_bytes": 0x2940,
            "buffer_pool_memory": 0x2004FA98,
            "buffer_pool_descriptor_input": 0x200003B0,
            "max_rx_acl_length": 251,
            "radio_boot_mode": 0,
            "pre_boot_delay_us": 100,
            "delayed_callback_ms": 10_000,
            "ble_address": 0x200737BF,
            "product_ble_control_block": 0x200727F0,
            "handler_id_offset": 0x56,
            "p_smp_cfg": 0x200004B8,
            "runtime_smp_config": 0x00774D44,
            "ccc_set": 0x007518C0,
            "ccc_set_len": 6,
            "dm_client_id_app": 3,
            "handler_order": [
                "HCI",
                "DM",
                "L2C",
                "ATT",
                "SMP",
                "APP",
                "product BLE",
                "HCI driver",
            ],
        },
        "lineage": {
            "retained_product_path": r"D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble.c",
            "radio_task_oracle": "AmbiqSuite R2.5.1 ble_freertos_fit/radio_task.c",
            "whole_file_source_exact": False,
            "historical_generating_commit_resolved": False,
        },
        "production": {
            "stock_bytes_replaced": 0,
            "source_owned_bytes_added": 0,
            "vendor_source_copied": False,
        },
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
        print("G2 BLE startup closed: 12 product bodies + 1 Apollo510 GPIO vector body")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
