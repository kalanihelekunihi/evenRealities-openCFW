#!/usr/bin/env python3
"""Fail-closed audit of the G2 first-party JBD4010 ULED driver object."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-uled-jbd4010-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-uled-jbd4010-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-uled-jbd4010-provenance.tsv"
PINS = {
    FUNCTION_MAP: "59d0f96576955b4b686022e4f8873b57aa7b85601ffb6874c650dd5265cd64f5",
    CLOSURE: "b349632a7356babb9824bb4703d6b6b32c10200e30a581221c6b610de7e16495",
    PROVENANCE: "99687f8cbd9ccd839e8c2d01f4dbab20edcf41facaa8d63dea28884af7ec839c",
}
PHYSICAL = (0x00592658, 0x005939A0)
PHYSICAL_SHA256 = "0dc52441e3eb2272fc97972eee102f01a3d3e9f59499e4708d8f95be565e5391"
BODY_SHA256 = "282897dacb6bac34ce77cfa56e28ebdefc318589bfb1363c753e7c86d418d83a"
GAPS = [
    (0x0059307E, 0x0059308C),
    (0x005931FA, 0x00593200),
    (0x00593288, 0x0059328C),
    (0x005932F8, 0x00593334),
    (0x00593524, 0x00593528),
    (0x0059364A, 0x00593660),
    (0x00593738, 0x00593750),
    (0x005938CA, 0x005939A0),
]
NONCODE_SHA256 = "9383f55824c401b734170954caf85267a6a55a26a47b64a8406b803e93c8f258"
ENTRY_COUNT = 77
ENTRY_SHA256 = "7d81e9a6bb5e39782971ac96ce48705c1503425aa1018026814ff1e8ae2e7987"
EXTERIOR_ENTRY = [(0x0057E5CC, 0x0059308C), (0x0057E610, 0x00592F9A)]
EXTERIOR_ENTRY_SHA256 = "2806ea37fb06abee7cafcc0f16c9adcae1473d1d6a0816dadfeda6f309b19952"
BODY_CALL_COUNT = 289
BODY_CALL_SHA256 = "320cb0698b9cdd47d6f05f93f19b6ff6f54360acf74c6a02214f06c455224cab"
STORED_ENTRY_SHA256 = "028b33caff6f72304e4a33cd8bb58c002771707a30bdcf4d5ed2684a23a00881"
RAW_INTERIOR_WINDOWS = [
    (0x0050CC49, 0x005928F8),
    (0x0057AD85, 0x00593043),
    (0x005B6CD9, 0x005928F8),
    (0x00644AE7, 0x00592C00),
    (0x0067FAC7, 0x00592DBC),
    (0x0078F390, 0x00593057),
    (0x0078F39C, 0x00593157),
]
RAW_INTERIOR_SHA256 = "1b55325294362922a711bdcee2d8efd09d0034536abed715ef1ef08515b1f757"
ASCII_COLLISION = (0x0078F388, 0x0078F3A0)
ASCII_COLLISION_SHA256 = "ef928024bec4d1ff009ed1628481e786d3c1a0941916ef6c7c7aeabd01edccc9"
OPS_OBJECT = (0x0070B024, 0x0070B064)
OPS_SHA256 = "7eecc0a32f95c8d1d712327198d4b473a7f065eeb1c2e8132f98526debef4418"
TEMPLATES = [0x0076B244, 0x0076B260, 0x0076B27C, 0x0076B298]
TEMPLATE_SHA256 = "568d17202d90a57a652a07e99cce0780372261cc61910ade92ededad20a2e015"
PATH_ADDRESS = 0x006F313C
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\driver\uled\jbd4010\drv_mspi_jbd4010.c"
WORDS = {
    0x005931FC: 0x20000788,
    0x00593288: 0x0076B244,
    0x005932F8: 0x20074524,
    0x005932FC: 0x2007452C,
    0x00593300: 0x20074528,
    0x00593304: 0x200007A0,
    0x00593308: 0x0076B260,
    0x0059330C: 0x0076B27C,
    0x00593310: 0x0076B298,
    0x0059331C: PATH_ADDRESS,
    0x0059364C: 0x2007501A,
    0x00593738: 0x20003994,
    0x005938FC: PATH_ADDRESS,
    0x00593928: 0x4001044C,
    0x0059392C: 0x40010444,
    0x00593930: 0x40010468,
    0x00593934: 0x40010460,
}
STRINGS = {
    PATH_ADDRESS: RETAINED_PATH,
    0x00785C90: "driver.jbd4010",
    0x00749844: "am_devices_jbd4010_QSPI_PartialReflash",
    0x00733704: "am_devices_jbd4010_QSPI_PartialReflash_async",
    0x0074986C: "am_devices_mspi_jbd4010_setBrightness",
    0x00753C9C: "am_devices_mspi_jbd4010_read_chipId",
    0x00753CC0: "am_devices_mspi_jbd4010_read_dieId",
    0x00776D24: "jdb4010_status_check",
    0x00776D3C: "jdb4010_status_recovery",
    0x00733734: "am_devices_jbd4010_status_check_and_recovery",
    0x0076B20C: "am_devices_jbd4010_set_mode",
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(data: bytes, start: int, end: int) -> bytes:
    return data[start - BASE : end - BASE]


def pair_digest(values: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


def cstring(data: bytes, address: int) -> str:
    offset = address - BASE
    end = data.find(b"\0", offset)
    if end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return data[offset:end].decode("ascii")


def thumb_bw_target(data: bytes, address: int) -> int | None:
    offset = address - BASE
    first, second = struct.unpack_from("<HH", data, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def analyze(image_path: Path = IMAGE) -> dict:
    data = image_path.read_bytes()
    if len(data) != 3_523_396 or sha256(data) != IMAGE_SHA256:
        raise AuditError("official image changed")
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    starts: set[int] = set()
    interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(data, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 24 or sum(map(len, bodies)) != 4588:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    noncode = b"".join(image_slice(data, *gap) for gap in GAPS)
    if len(noncode) != 348 or sha256(noncode) != NONCODE_SHA256:
        raise AuditError("owned non-code changed")

    for address, expected in WORDS.items():
        actual = struct.unpack("<I", image_slice(data, address, address + 4))[0]
        if actual != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    if sha256(image_slice(data, *OPS_OBJECT)) != OPS_SHA256:
        raise AuditError("external ULED operations object changed")
    templates = b"".join(image_slice(data, address, address + 28) for address in TEMPLATES)
    if sha256(templates) != TEMPLATE_SHA256:
        raise AuditError("request templates changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entry: list[tuple[int, int]] = []
    interior: list[tuple[int, int]] = []
    entry_bw: list[tuple[int, int]] = []
    interior_bw: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            interior.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts:
            entry_bw.append((site, target))
        elif target in interiors:
            interior_bw.append((site, target))
    if len(entry) != ENTRY_COUNT or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("BL entry closure changed")
    if interior or entry_bw or interior_bw:
        raise AuditError("direct strict-interior/B.W closure changed")
    exterior = [pair for pair in entry if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    if exterior != EXTERIOR_ENTRY or pair_digest(exterior) != EXTERIOR_ENTRY_SHA256:
        raise AuditError("exterior BL closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != BODY_CALL_COUNT or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("direct body-call closure changed")

    encoded_entries = starts | {value | 1 for value in starts}
    encoded_interiors = interiors | {value | 1 for value in interiors}
    stored_entries: list[tuple[int, int]] = []
    stored_interiors: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded_entries:
            stored_entries.append((BASE + offset, value))
        if value in encoded_interiors:
            stored_interiors.append((BASE + offset, value))
    if len(stored_entries) != 14 or pair_digest(stored_entries) != STORED_ENTRY_SHA256:
        raise AuditError("stored operations-table closure changed")
    if [site for site, _ in stored_entries] != list(range(0x0070B024, 0x0070B05C, 4)):
        raise AuditError("stored entry pointers escaped the external operations table")
    if stored_interiors != RAW_INTERIOR_WINDOWS or pair_digest(stored_interiors) != RAW_INTERIOR_SHA256:
        raise AuditError("raw interior overlap qualification changed")
    if sha256(image_slice(data, *ASCII_COLLISION)) != ASCII_COLLISION_SHA256:
        raise AuditError("packed-ASCII collision evidence changed")
    if any(site % 2 == 0 for site, _ in stored_interiors[:5]):
        raise AuditError("unaligned overlap became executable-looking")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("jbd4010" in source.get("path", "").lower() for source in overlay["sources"])
    if routed:
        raise AuditError("unimplemented JBD4010 driver unexpectedly entered production overlay")

    return {
        "surface": {
            "linked_functions": 24,
            "body_bytes": 4588,
            "owned_noncode_bytes": 348,
            "physical_bytes": 4936,
            "direct_bl_entry_sites": 77,
            "exterior_bl_entry_sites": 2,
            "direct_body_calls": 289,
            "stored_entry_pointers": 14,
            "strict_interior_ingress": 0,
            "qualified_raw_overlap_windows": 7,
        },
        "abi": {
            "request_bytes": 28,
            "request_templates": 4,
            "mspi_handle": "0x20074524",
            "framebuffer": "0x20074528",
            "clear_callback": "0x2007452c",
            "offset_mode_flag": "0x2007501a",
            "operations_table": "0x0070b024",
            "operations_callbacks": 14,
        },
        "display": {
            "width": 640,
            "height": 480,
            "bits_per_pixel": 4,
            "scanline_bytes": 320,
            "offset_x_range": [2, 22],
            "offset_y_range": [2, 18],
            "accepted_modes": [0x71, 0x72, 0x73, 0x74],
            "chip_id_command": "0x9f",
            "die_id_command": "0x81",
            "die_id_bytes": 12,
        },
        "production": {
            "candidate": None,
            "production_routed": routed,
            "ownership_bytes": 0,
            "source_inventory_available": False,
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 JBD4010 ULED audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
