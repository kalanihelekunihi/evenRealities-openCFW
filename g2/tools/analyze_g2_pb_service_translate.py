#!/usr/bin/env python3
"""Fail-closed stock and production audit of G2 pb_service_translate."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-translate-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-translate-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-translate-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_translate.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "673a7bd08a3e20bc9070c99056df0a8b2d43cef8627ec42d78cf21f127cd0cf6",
    CLOSURE: "875f75f22cf1aa450b95d16e1c396498774f2fdfb22882a91f2b5dfc30e9620f",
    PROVENANCE: "e5abf11b1bef210cd5bd9f593423646c296d5f79a83fc592af2821ab2c98ace7",
}
SOURCE_SIZE = 9294
SOURCE_SHA256 = "1e6429d33df883ca498112850f6e38254798d82e88de86d2b2c450d9300d0095"
FUNCTIONS = (
    ("open_cfw_pb_service_translate_buffer_write", 146, 261580, 0,
     "buffer_write"),
    ("open_cfw_pb_service_translate_zero", 88, 261728, 0, "zero"),
    ("open_cfw_pb_translate_encode_and_send", 264, 261816, 7, "encode"),
    ("APP_PbTranslateRxFrameDataProcess", 108, 262080, 3, "rx"),
    ("APP_PbTranslateTxEncodeNotify", 52, 262188, 1, "notify"),
    ("APP_PbTranslateTxEncodeCommResp", 38, 262240, 1, "comm_resp"),
    ("APP_PbTranslateTxEncodeModeSwitch", 52, 262280, 1, "mode_switch"),
)
PATCH_SUFFIXES = ("rx", "notify", "comm_resp", "mode_switch")
PHYSICAL = (0x0059F53C, 0x0059FAE0)
PHYSICAL_SHA256 = "9d31e156165c7371a649d7f048b7b5aaae63554d6e558caa67c20ae04b885ed8"
POOL = (0x0059FA68, 0x0059FAE0)
POOL_SHA256 = "0a9dfaa6ddd2c98157724e809baff1d222b91fc3e2d23238333be1258f86d781"
BODY_SHA256 = "0acba12ce622e3f5044a45e29164bf275f64d30ee8eb8615f3c211beef50f27d"
ENTRY_SHA256 = "3cea787570d4dbc48917c37706e950365df573a856ea7d93112d5e625b9c05dd"
BODY_CALL_SHA256 = "9782fa705dbc1d7c2b0b163f320567abf33c030189b28864cb6b3250a8d765bf"
RAW_WINDOW_SHA256 = "a7daff19c48c8898607413c9a7261fc89f5ff8f95abaa3fa1993911009e55997"
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\platform\protocols\pb_service_translate\pb_service_translate.c"
POOL_WORDS = (
    0x0076FBA8, 0x00757FF8, 0x006DB4E8, 0x00787F20, 0x0074C83C,
    0x00787F30, 0x0077CE5C, 0x0078DF84, 0x007824FC, 0x0075801C,
    0x20075000, 0x00717974, 0x006FBEC4, 0x20074878, 0x006F52C8,
    0x006E131C, 0x00787F40, 0x00763950, 0x00763970, 0x200F9EE4,
    0x2037CAA0, 0x00782510, 0x00758040, 0x00787F50, 0x00763990,
    0x0076FBC4, 0x00782524, 0x00782538, 0x00758064, 0x00758088,
)
STRINGS = {
    0x0076FBA8: "pData or message is NULL",
    0x00757FF8: "APP_PbTranslateRxFrameDataProcess",
    0x006DB4E8: RETAINED_PATH,
    0x00787F20: "pb.translate",
    0x0074C83C: "[pb.translate]pData or message is NULL",
    0x00787F30: "Translate_pb_rx",
    0x0078DF84: "(none)",
    0x007824FC: "Decoding failed: %s",
    0x0075801C: "[pb.translate]Decoding failed: %s",
    0x00717974: "command_id: %d, magic number = %d, last magic number = %d",
    0x006FBEC4: "[pb.translate]command_id: %d, magic number = %d, last magic number = %d",
    0x006F52C8: "Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore",
    0x006E131C: "[pb.translate]Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore",
    0x00787F40: "pNotify is NULL",
    0x00763950: "APP_PbTranslateTxEncodeNotify",
    0x00763970: "[pb.translate]pNotify is NULL",
    0x00782510: "Encoding failed: %s",
    0x00758040: "[pb.translate]Encoding failed: %s",
    0x00787F50: "pResp is NULL",
    0x00763990: "APP_PbTranslateTxEncodeCommResp",
    0x0076FBC4: "[pb.translate]pResp is NULL",
    0x00782524: "Translate_pb_resp",
    0x00782538: "pModeSwitch is NULL",
    0x00758064: "APP_PbTranslateTxEncodeModeSwitch",
    0x00758088: "[pb.translate]pModeSwitch is NULL",
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
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22)
                 | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1))
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
    if len(rows) != 4 or sum(map(len, bodies)) != 1324:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")
    pool = image_slice(data, *POOL)
    if len(pool) != 120 or sha256(pool) != POOL_SHA256:
        raise AuditError("literal pool changed")
    if struct.unpack("<30I", pool) != POOL_WORDS:
        raise AuditError("literal pool layout changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")

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
    expected_entry = [
        (0x0059E1E4, 0x0059F960), (0x0059E476, 0x0059F71A),
        (0x0059F10E, 0x0059F53C), (0x0059F162, 0x0059F842),
        (0x0059F1BA, 0x0059F842), (0x0059F212, 0x0059F842),
        (0x0059F220, 0x0059F842), (0x0059F39A, 0x0059F71A),
    ]
    if entry != expected_entry or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("direct entry closure changed")
    if interior or entry_bw or interior_bw:
        raise AuditError("direct strict-interior/B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 74 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    raw_windows: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            raw_windows.append((BASE + offset, value))
    if len(raw_windows) != 28 or pair_digest(raw_windows) != RAW_WINDOW_SHA256:
        raise AuditError("raw pointer-window closure changed")
    if any(value in starts or value in {start | 1 for start in starts} for _, value in raw_windows):
        raise AuditError("unexpected stored exact-entry pointer")

    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or sha256(source) != SOURCE_SHA256:
        raise AuditError("production source changed")
    overlay = json.loads(OVERLAY.read_text())
    names = {item[0] for item in FUNCTIONS}
    leaves = {item.get("function"): item for item in overlay["relocated_leaves"]
              if item.get("function") in names}
    if set(leaves) != names:
        raise AuditError("production leaf inventory changed")
    for name, size, offset, relocation_count, _ in FUNCTIONS:
        leaf = leaves[name]
        if (leaf["source"].get("path") !=
                "components/apollo_main/core_overlay/pb_service_translate.c"
                or leaf["source"].get("size") != SOURCE_SIZE
                or leaf["source"].get("sha256") != SOURCE_SHA256
                or leaf.get("profiles") != ["apple-clang"]
                or leaf.get("strict_relocation_contract") is not True
                or (leaf["expected"].get("size"),
                    leaf["expected"].get("offset"),
                    leaf["expected"].get("alignment")) != (size, offset, 4)
                or len(leaf.get("relocations", [])) != relocation_count):
            raise AuditError(f"production leaf changed: {name}")
    patch_by_name = {item.get("name"): item for item in overlay["patch_sites"]}
    for suffix, row in zip(PATCH_SUFFIXES, rows):
        patch = patch_by_name.get(f"replace_pb_translate_{suffix}")
        expected = (
            int(row["stock_start"], 0), int(row["stock_bytes"]),
            row["stock_sha256"], "b_w", row["function"], ["apple-clang"],
        )
        if patch is None or (
            patch.get("runtime_address"), patch.get("expected_size"),
            patch.get("expected_sha256"), patch.get("branch"),
            patch.get("target_function"), patch.get("profiles"),
        ) != expected:
            raise AuditError(f"production patch changed: {row['function']}")
    report = json.loads(REPORT.read_text())
    if (report["overlay"]["size"], report["overlay"]["sha256"],
            report["component"]["size"], report["component"]["sha256"]) != (
        332148, "588a29c8d680068b6f27dd2cff831dcfd5aa71a91e4f9f97537d9bcb4a0d145d",
        3855544, "df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc",
    ):
        raise AuditError("production build pins changed")
    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    if (main["provider"].get("size"), main["provider"].get("sha256"),
            manifest["package"].get("expected_size"),
            manifest["package"].get("expected_sha256")) != (
        3855544, "df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc",
        4634038, "3953d7a537b11d75c7f589522ae7958bd7c4f59a15d35b98d92d5bec79b90731",
    ):
        raise AuditError("production manifest pins changed")
    region_by_name = {item["name"]: item for item in main["regions"]}
    for suffix, row in zip(PATCH_SUFFIXES, rows):
        region = region_by_name.get(f"pb_translate_{suffix}_source_replacement")
        if region is None or (
            region.get("target_address"), region.get("size"),
            region.get("address_status"),
        ) != (int(row["stock_start"], 0), int(row["stock_bytes"]),
              "generated_source_entry_replacement"):
            raise AuditError(
                f"production manifest replacement changed: {row['function']}"
            )
    for name, size, offset, _, region_suffix in FUNCTIONS:
        region = region_by_name.get(
            f"pb_translate_{region_suffix}_source_text"
        )
        if region is None or (
            region.get("file_offset"), region.get("size"),
            region.get("target_address"), region.get("address_status"),
        ) != (3523396 + offset, size, 0x00794324 + offset,
              "source_compiled"):
            raise AuditError(f"production manifest source changed: {name}")
    retained = region_by_name.get("pb_translate_retained_literal_pool")
    alignment = [item for item in main["regions"]
                 if item["name"].startswith("pb_translate_")
                 and item["name"].endswith("_source_alignment")]
    if retained is None or retained.get("size") != 120 or (
            retained.get("address_status") != "official_blob") or (
            sum(item["size"] for item in alignment) != 4):
        raise AuditError("production manifest retained/alignment accounting changed")

    return {
        "surface": {
            "linked_functions": 4,
            "body_bytes": 1324,
            "owned_pool_bytes": 120,
            "physical_bytes": 1444,
            "direct_bl_entry_sites": 8,
            "direct_body_calls": 74,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 28,
        },
        "contracts": {
            "rx_status": {"success": 0, "decode_failure": 5, "null": 6, "duplicate": 13},
            "duplicate_window_ms": 3000,
            "tx_status": {"success": 0, "encode_failure": 5, "null": 6},
            "transport_service": 5,
            "notify_subtype": 5,
            "mode_switch_subtype": 6,
            "command_response_subtype": 7,
            "shared_message_buffer": "0x200f9ee4",
            "shared_message_bytes": 0x854,
            "encode_buffer": "0x2037caa0",
            "encode_capacity": 0x100,
            "last_magic": "0x20075000",
            "last_magic_tick": "0x20074878",
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "exact_symbols": [row["function"] for row in rows],
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "ownership_bytes": 1324,
            "source_inventory_available": True,
            "source_functions": 7,
            "compiled_text_bytes": 748,
            "alignment_bytes": 4,
            "strict_relocations": 13,
            "stock_replaced_bytes": 1324,
            "retained_pool_bytes": 120,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized live G2 service 0x05 master/peer BLE and "
                "translation UI evidence is available; the authorized right "
                "temple is nonresponsive and the left temple must remain stock."
            ),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError, UnicodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pb_service_translate audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
