#!/usr/bin/env python3
"""Fail-closed linked-object and provider audit for the G2 transport protocol."""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x0043_7FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-transport-protocol-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-transport-protocol-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-transport-protocol-provider-map.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "fa8a7a9eeaf4f386a9419ffeee5e876dccc188a076ac785f1685fd5637556e6a",
    CLOSURE: "9796ec6f1094dece1a5b2a81ecbc28de721171dcd20da01b2a5b1598d72874fc",
    PROVIDER_MAP: "52bbdb1316e572fb2b3c6fe92bc9842087141207090af093f5fe253d743c99d7",
}

RETAINED_PATH = (
    r"D:\01_workspace\s200_ap510b_iar_git\platform\protocols\transport_protocol"
    r"\transport_protocol.c"
)
PATH_RUN = 0x006D_EC74
PATH_POINTER_CELLS = [0x004B_90FC, 0x004B_9A0C]

PHYSICAL = (0x004B_892C, 0x004B_9A80)
PHYSICAL_BYTES = 4_436
PHYSICAL_SHA256 = "586bbbe6936ab46ca99434ca4d05d85a8b8031d457cb9b3d587e21f96adff3d4"
BODY_BYTES = 4_134
BODY_SHA256 = "28112dd512e93b63735bd152bacc19314949603ceec591e0f5e4900645ba3bb1"
POOL_REGIONS = 4
POOL_BYTES = 302
POOL_SHA256 = "3ee27abef3889ff223b4c47ca6a27bb2400e282effc396757f76fe8fab422edc"

# The predecessor is a first-party BLE handler lookup followed by its final
# pool.  The successor is an independently rooted Cordio advertising helper.
PRECEDING_FUNCTION = (0x004B_848C, 0x004B_871E)
PRECEDING_FUNCTION_SHA256 = "f51c94cd61a6aa9aa875f985b3875bc0410b4caafe27cecb8598170a7db11905"
PRECEDING_POOL = (0x004B_871E, 0x004B_892C)
PRECEDING_POOL_SHA256 = "ce6d297d0c4ec34160b9a3fef9d14a3d51734d3b96d8b679d088ac09e60423c7"
FOLLOWING_OBJECT = (0x004B_9A80, 0x004B_9AC0)
FOLLOWING_OBJECT_SHA256 = "f687db593110076bcf1e6a2512b05cc86e323cef21a59e98575065570003002a"

ENTRY_COUNT = 26
EXTERNAL_ENTRY_COUNT = 5
ENTRY_SHA256 = "c4d0eb953e9748443f0363c724d5d16b275a1ddb024b755498f1672036dda55d"
BODY_CALL_COUNT = 193
INTERNAL_BODY_CALL_COUNT = 21
BODY_CALL_SHA256 = "ed1e1140f34585ae594ab96c5001c08185037ee9e945df71cd03f4d1988fbb0d"
STORED = [(0x004B_9A18, 0x004B_8C6D), (0x004B_9A34, 0x004B_8F7D)]
STORED_SHA256 = "52b7084bf03cc257199c63cdaffaeb0960903653a3ea025d8ea6ef483bb49f60"

EXTERNAL_TARGET_COUNTS = {
    0x0043_9BE4: 6,   # memory copy
    0x0043_C0E4: 5,   # memory fill
    0x0043_CE9E: 28,  # EasyLogger backend
    0x0043_D0CE: 84,  # EasyLogger level gate
    0x0043_D574: 28,  # EasyLogger structured output
    0x0044_90CC: 1,   # CMSIS osKernelGetTickCount
    0x0044_971C: 1,   # CMSIS osMutexNew
    0x0044_97B6: 1,   # CMSIS osMutexAcquire
    0x0044_981C: 2,   # CMSIS osMutexRelease
    0x0046_F2C6: 2,   # G2 BLE payload-capacity getter
    0x0047_4CD2: 1,   # G2 synchronized TLSF allocation wrapper
    0x0047_4D16: 1,   # G2 synchronized TLSF free wrapper
    0x0047_697E: 1,   # G2 delayed-event insertion
    0x0047_6ACE: 5,   # G2 delayed-event removal
    0x0049_ACD4: 3,   # first-party CRC-16/CCITT provider
    0x004B_8122: 1,   # G2 BLE controller/handler lookup
    0x004B_F99E: 1,   # Cordio WsfMsgAlloc
    0x004B_F9BA: 1,   # Cordio WsfMsgSend
}

TINYFRAME = (0x0049_16C8, 0x0049_22F6)
CRC_PROVIDER = 0x0049_ACD4
RECOVERED_FUNCTION = (0x004B_8C6C, 0x004B_8DA2)
RECOVERED_RETURN = (0x004B_8DA0, bytes.fromhex("f0bd"))

STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0078_C7A0: "TPL_Init",
    0x0078_461C: "_getOrCreateContext",
    0x0077_D0B4: "_rxNextPacketTimeout",
    0x0077_3D48: "TPL_RxPacketTimeoutHandler",
    0x0077_D0CC: "_rxSyncEventCallback",
    0x0078_C7B8: "_tplReponse",
    0x0078_4644: "TPL_ReceivePacket",
    0x0078_9CC0: "TPL_SendPacket",
    0x0075_C0CC: "Failed to create _g_SendBufferMutex",
    0x0078_C7AC: "prot.tran",
}


class AuditError(RuntimeError):
    """Raised when authenticated evidence or the closed object changes."""


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or last > len(blob) or first > last:
        raise AuditError(f"invalid image interval [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def _pair_digest(pairs: list[tuple[int, int]]) -> str:
    return _sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def _c_string(blob: bytes, address: int) -> str:
    offset = address - BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def _validate_provider_pins() -> None:
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != (
        "d213f261b5be6bb29a7cce8b84071706b72f4d53"
    ):
        raise AuditError("CMSIS-FreeRTOS provider commit changed")
    tinyframe = json.loads((ROOT / "third_party/tinyframe/PROVENANCE.json").read_text())
    if tinyframe["upstream"]["selected_commit"] != (
        "eb75483e035916ef9f3e9fce0d2ae389cb09785f"
    ):
        raise AuditError("TinyFrame comparison commit changed")
    cordio = json.loads((ROOT / "third_party/cordio/PROVENANCE.json").read_text())
    if cordio["upstream"]["selected_commit"] != (
        "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"
    ):
        raise AuditError("Cordio provider commit changed")
    wsf_audit = (ROOT / "docs/research/cordio-wsf-buffer-message-source-recovery.md").read_text()
    if "86372d84ef0386d8834ed036e613c8f2ded1ff16" not in wsf_audit:
        raise AuditError("Cordio r19.02 exact message-source commit changed")
    tlsf = (ROOT / "third_party/tlsf/README.openCFW.md").read_text()
    for commit in (
        "a1f743ffac0305408b39e791e0ffb45f6d9bc777",
        "deff9ab509341f264addbd3c8ada533678591905",
    ):
        if commit not in tlsf:
            raise AuditError("TLSF provider equivalence interval changed")
    easylogger = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easylogger["upstream"]["selected_commit"] != (
        "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"
    ):
        raise AuditError("EasyLogger provider commit changed")


def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official Apollo image changed")
    for path, expected in INPUT_PINS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")
    _validate_provider_pins()

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        provider_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 13 or len(provider_rows) != 8:
        raise AuditError("function or provider inventory changed")

    starts: set[int] = set()
    strict_interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    gaps: list[bytes] = []
    anchored = 0
    previous_end = PHYSICAL[0]
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        if start in starts or start < previous_end or not start < end:
            raise AuditError(f"invalid or overlapping function at 0x{start:08x}")
        if previous_end < start:
            gaps.append(_slice(blob, previous_end, start))
        body = _slice(blob, start, end)
        if len(body) != int(row["stock_bytes"]) or _sha256(body) != row["stock_sha256"]:
            raise AuditError(f"function body changed: {row['function']}")
        starts.add(start)
        strict_interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(body)
        anchored += row["source_path_anchor"] == "yes"
        previous_end = end
    if previous_end < PHYSICAL[1]:
        gaps.append(_slice(blob, previous_end, PHYSICAL[1]))
    if intervals[0][0] != PHYSICAL[0] or previous_end > PHYSICAL[1]:
        raise AuditError("function inventory escaped physical object")
    if anchored != 7:
        raise AuditError(f"source-path anchor census changed: {anchored}")
    if sum(map(len, bodies)) != BODY_BYTES or _sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body inventory changed")
    if len(gaps) != POOL_REGIONS or sum(map(len, gaps)) != POOL_BYTES:
        raise AuditError("literal-pool inventory changed")
    if _sha256(b"".join(gaps)) != POOL_SHA256:
        raise AuditError("literal-pool bytes changed")

    physical = _slice(blob, *PHYSICAL)
    if len(physical) != PHYSICAL_BYTES or _sha256(physical) != PHYSICAL_SHA256:
        raise AuditError("physical transport-protocol object changed")
    for bounds, expected, label in (
        (PRECEDING_FUNCTION, PRECEDING_FUNCTION_SHA256, "preceding BLE function"),
        (PRECEDING_POOL, PRECEDING_POOL_SHA256, "preceding BLE pool"),
        (FOLLOWING_OBJECT, FOLLOWING_OBJECT_SHA256, "following Cordio helper"),
    ):
        if _sha256(_slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} boundary changed")
    terminal, encoding = RECOVERED_RETURN
    if _slice(blob, terminal, terminal + len(encoding)) != encoding:
        raise AuditError("recursively recovered timeout return changed")
    if RECOVERED_FUNCTION not in intervals:
        raise AuditError("recursively recovered timeout function disappeared")

    for address, expected in STRINGS.items():
        if _c_string(blob, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    path_word = struct.pack("<I", PATH_RUN)
    path_hits: list[int] = []
    cursor = blob.find(path_word)
    while cursor >= 0:
        path_hits.append(BASE + cursor)
        cursor = blob.find(path_word, cursor + 1)
    if path_hits != PATH_POINTER_CELLS:
        raise AuditError(f"source-path pointer topology changed: {path_hits!r}")

    sys.path.insert(0, str(ROOT / "tools"))
    import recover_apollo_embedded_source_paths as decoder

    entries: list[tuple[int, int]] = []
    interior: list[tuple[int, int]] = []
    unknown_object_targets: list[tuple[int, int]] = []
    for offset in range(0, len(blob) - 3, 2):
        address = BASE + offset
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in strict_interiors:
            interior.append((address, target))
        elif target is not None and PHYSICAL[0] <= target < PHYSICAL[1]:
            unknown_object_targets.append((address, target))
    if len(entries) != ENTRY_COUNT or _pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct entry topology changed")
    external_entries = sum(not (PHYSICAL[0] <= site < PHYSICAL[1]) for site, _ in entries)
    if external_entries != EXTERNAL_ENTRY_COUNT:
        raise AuditError("external direct entry census changed")
    if interior or unknown_object_targets:
        raise AuditError("strict-interior or unrecovered object target appeared")

    calls: list[tuple[int, int]] = []
    image_end = BASE + len(blob)
    for start, end in intervals:
        for address in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None and BASE <= target < image_end:
                calls.append((address, target))
    if len(calls) != BODY_CALL_COUNT or _pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body callee topology changed")
    internal_calls = sum(target in starts for _, target in calls)
    if internal_calls != INTERNAL_BODY_CALL_COUNT:
        raise AuditError("internal callee census changed")
    external_counts = Counter(target for _, target in calls if target not in starts)
    if dict(external_counts) != EXTERNAL_TARGET_COUNTS:
        raise AuditError(f"external provider target census changed: {external_counts!r}")

    encoded_starts = starts | {entry | 1 for entry in starts}
    stored: list[tuple[int, int]] = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in encoded_starts:
            stored.append((BASE + offset, value))
    if stored != STORED or _pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored entry-pointer topology changed")

    tinyframe_calls = [(site, target) for site, target in calls if TINYFRAME[0] <= target < TINYFRAME[1]]
    tinyframe_words: list[tuple[int, int]] = []
    for address in range(PHYSICAL[0], PHYSICAL[1] - 3, 4):
        value = struct.unpack_from("<I", blob, address - BASE)[0] & ~1
        if TINYFRAME[0] <= value < TINYFRAME[1]:
            tinyframe_words.append((address, value))
    if tinyframe_calls or tinyframe_words:
        raise AuditError("transport protocol acquired a TinyFrame dependency")
    crc_sites = [site for site, target in calls if target == CRC_PROVIDER]
    if crc_sites != [0x004B_91D8, 0x004B_9486, 0x004B_97B0]:
        raise AuditError("CCITT checksum call topology changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any(
        "transport_protocol" in item.get("path", "").lower()
        for item in overlay["sources"]
    )
    if routed:
        raise AuditError("analysis-only transport object entered production")

    return {
        "surface": {
            "linked_functions": len(rows),
            "path_anchored_functions": anchored,
            "additional_recovered_functions": len(rows) - anchored,
            "baseline_ghidra_functions": len(rows) - 1,
            "recursive_decode_recoveries": 1,
            "body_bytes": BODY_BYTES,
            "literal_pool_regions": len(gaps),
            "literal_pool_bytes": POOL_BYTES,
            "physical_bytes": len(physical),
            "direct_bl_entry_sites": len(entries),
            "external_direct_bl_entry_sites": external_entries,
            "direct_body_calls": len(calls),
            "internal_direct_body_calls": internal_calls,
            "stored_entry_pointers": len(stored),
            "strict_interior_raw_bl_decodes": len(interior),
            "unrecovered_direct_object_targets": len(unknown_object_targets),
        },
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_multipart_transport_protocol",
            "historical_source_available": False,
            "private_producing_commit_observable": False,
            "embedded_third_party_definitions": [],
        },
        "boundary": {
            "physical_start": f"0x{PHYSICAL[0]:08x}",
            "physical_end_exclusive": f"0x{PHYSICAL[1]:08x}",
            "preceded_by": "BLE handler-lookup literal pool",
            "followed_by": "independent Cordio advertising helper",
            "path_pointer_cells": [f"0x{value:08x}" for value in PATH_POINTER_CELLS],
        },
        "behavior": {
            "magic": "0xAA",
            "header_bytes": 8,
            "maximum_payload_bytes": 4_096,
            "receive_contexts": 4,
            "receive_timeout_ms": 1_500,
            "timeout_event": "0xB8",
            "send_mutex_timeout_ticks": 100,
            "crc": "CRC-16/CCITT-FALSE, polynomial 0x1021, seed 0xFFFF",
            "crc_call_sites": [f"0x{site:08x}" for site in crc_sites],
        },
        "provider_boundary": {
            "provider_rows": len(provider_rows),
            "direct_external_targets": len(external_counts),
            "cmsis_freertos": {
                "version": "v10.5.1",
                "commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
                "calls": 5,
            },
            "cordio_wsf_message": {
                "exact_public_definition_floor": "86372d84ef0386d8834ed036e613c8f2ded1ff16",
                "selected_oracle_ceiling": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
                "calls": 2,
            },
            "tlsf": {
                "equivalence_interval": "a1f743ffac0305408b39e791e0ffb45f6d9bc777..deff9ab509341f264addbd3c8ada533678591905",
                "direct_calls": 0,
                "wrapper_calls": 2,
            },
            "tinyframe": {
                "direct_calls": len(tinyframe_calls),
                "stored_pointers": len(tinyframe_words),
                "assessment": "not a dependency; separate 0xAA multipart protocol",
            },
            "assessment": "all third-party relationships terminate at already authenticated provider seams; the object contains no opaque upstream body",
        },
        "cross_version": {
            "prior_g2_named_functions_in_sequence": 13,
            "same_size_functions": 13,
            "qualification": "the prior G2 corpus is a naming/topology oracle only; every current byte and boundary is independently pinned",
        },
        "production": {
            "candidate": None,
            "production_routed": routed,
            "ownership_bytes": 0,
        },
        "limitations": [
            "the exact private G2 source and producing commit remain unavailable",
            "five conservative current labels use behavior plus prior-G2 order because no current function-name string survives",
            "provider commits identify reusable upstream seams but cannot identify the private first-party transport revision",
            "linked-object closure does not make the callback ABI production-routable without a dedicated clean-room implementation and target validation",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 transport-protocol audit: PASS")
