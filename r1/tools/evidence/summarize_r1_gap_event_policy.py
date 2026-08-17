#!/usr/bin/env python3
"""Pin the noncontiguous Ghidra-omitted R1 GAP event policy handler."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE
from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
REGISTRATION_POINTER_ADDRESS = 0x000C45C0

EXECUTABLE_SEGMENTS = (
    (0x00052B9C, 0x00052F9E, 1026,
     "9aa721ab9b5f9adcd1478ffa3e2eb49b3e65a2a4ecbc3d219ef90610d5827453"),
    (0x00053278, 0x00053536, 702,
     "844baa6cfcf69cd6a4bc7b953152413158d6096d506a5b05f09d06c266caed62"),
)

R1_GAP_EVENT_POLICY_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00052B9C,
    "end_exclusive": 0x0005380C,
    "size": 3184,
    "symbol": "r1_gap_event_plan_build",
    "sha256": "1fe5a29f37f52ee7f0d7ea75ffb52dd65da44e37b3b64b2daffdc4efd6f62eac",
    "callers": (),
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

EXPECTED_STRINGS = {
    0x00052FB4: b"[RING]Connected",
    0x00052FC4: b"Connected",
    0x000530F4: b"[RING]Disconnected, conn_handle: %d, reason: 0x%x",
    0x00053548: b"[RING]request PHY update: tx_phys=0x%02X, rx_phys=0x%02X",
    0x00053620: b"[RING]Glasses PHY update request. conn_handle: %d",
    0x00053680: b"[RING]Using local preferred PHY: tx=1M, rx=coded",
    0x000536E0: b"[RING]APP PHY update request conn_handle: %d",
    0x00053750: b"[RING]PHY update failed with status: 0x%02X",
    0x000537A4: b"[RING]GATT Client Timeout.",
    0x000537D8: b"[RING]GATT Server Timeout.",
}


def in_executable(address: int) -> bool:
    return any(start <= address < end for start, end, _size, _sha in EXECUTABLE_SEGMENTS)


def local_calls(image: bytes, target: int) -> tuple[tuple[int, str], ...]:
    return tuple(
        (address, kind)
        for address, kind in direct_thumb_branches_to(image, DEFAULT_BASE, target)
        if in_executable(address)
    )


def read_c_string(image: bytes, address: int) -> bytes:
    start = address - DEFAULT_BASE
    return image[start:image.index(b"\0", start)]


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")
    function = R1_GAP_EVENT_POLICY_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    envelope = image[entry - DEFAULT_BASE:end - DEFAULT_BASE]
    callers = tuple(direct_thumb_branches_to(image, DEFAULT_BASE, entry))
    registration_pointer = struct.unpack_from(
        "<I", image, REGISTRATION_POINTER_ADDRESS - DEFAULT_BASE)[0]
    executable = bytearray()
    segments = []
    for start, segment_end, size, expected_sha in EXECUTABLE_SEGMENTS:
        body = image[start - DEFAULT_BASE:segment_end - DEFAULT_BASE]
        actual_sha = hashlib.sha256(body).hexdigest()
        if len(body) != size or actual_sha != expected_sha:
            raise ValueError(f"GAP executable segment changed at 0x{start:08x}")
        executable.extend(body)
        segments.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{segment_end:08x}",
            "bytes": size,
            "sha256": expected_sha,
        })
    strings = {
        address: read_c_string(image, address) for address in EXPECTED_STRINGS
    }
    if len(envelope) != int(function["size"]) or \
            hashlib.sha256(envelope).hexdigest() != function["sha256"] or \
            len(executable) != 1728 or \
            hashlib.sha256(executable).hexdigest() != \
            "47e481cd2ccaf7721e760d015e4d9c503f819ba74ab1afcad277642647e4a282" or \
            callers != function["callers"] or \
            registration_pointer != entry + 1 or \
            strings != EXPECTED_STRINGS or \
            local_calls(image, 0x00065D64) != (
                (0x00052C04, "BL"), (0x00052CF0, "BL"),
                (0x00052CFC, "BL"), (0x00052E3A, "BL"),
                (0x00052E42, "BL"), (0x00052E4A, "BL"),
                (0x00052F72, "BL")) or \
            local_calls(image, 0x00065B4C) != (
                (0x00052C10, "BL"), (0x00052D12, "BL"),
                (0x00052D4E, "BL"), (0x000532C8, "BL")) or \
            local_calls(image, 0x0004D2F4) != ((0x000533DA, "B.W"),):
        raise ValueError("R1 GAP event policy changed")

    return {
        "analysis": "R1 GAP event policy",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": int(function["size"]),
        "executable_bytes": len(executable),
        "ghidra_function_count": 0,
        "manual_supplement_count": 1,
        "function": {
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [],
        },
        "executable_segments": segments,
        "registration": {
            "observer_pointer_address": f"0x{REGISTRATION_POINTER_ADDRESS:08x}",
            "observer_thumb_pointer": f"0x{registration_pointer:08x}",
            "direct_callers_expected": 0,
        },
        "event_routes": {
            "0x10": "connected",
            "0x11": "disconnected",
            "0x21": "PHY update request",
            "0x22": "PHY update complete",
            "0x3b": "GATT client timeout diagnostic",
            "0x56": "GATT server timeout diagnostic",
            "other": "ignore",
        },
        "connected_policy": {
            "connection_timeout_ticks": 0xF000,
            "peer_cache_connection_limit": 3,
            "factory_marker": 0x5A,
            "factory_role_delay_ticks": 0x7800,
            "link_slot_count": 3,
            "fail_stop_on_link_context_initialization_error": True,
        },
        "disconnected_policy": {
            "glasses_role_precedes_phone_role": True,
            "unassigned_role_code": 0,
            "phone_role_code": 1,
            "glasses_role_code": 2,
            "advertising_mode": 3,
            "advertising_retry_ticks": 0x66,
            "accepted_tx_power_statuses": (0, 8),
        },
        "phy_policy": {
            "non_glasses_local_phys": (1, 1),
            "glasses_swaps_peer_rx_tx_into_local_tx_rx": True,
            "coded_phy_bit_value": 4,
            "completion_status_offset": 8,
            "completion_tx_phy_offset": 9,
            "completion_rx_phy_offset": 10,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "softdevice_reimplemented": False,
            "nordic_connection_state_reimplemented": False,
            "advertising_provider_reimplemented": False,
            "logging_reimplemented": False,
            "live_gap_dispatch_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
