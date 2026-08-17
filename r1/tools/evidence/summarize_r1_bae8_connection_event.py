#!/usr/bin/env python3
"""Pin the Ghidra-omitted R1 BAE8 connection/CCCD event handler."""

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
EXECUTABLE_END = 0x0007CD7A
LOG_STRING_ADDRESS = 0x0007CD88
PREFIXED_LOG_STRING_ADDRESS = 0x000BE694

R1_BAE8_CONNECTION_EVENT_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x0007CCB4,
    "end_exclusive": 0x0007CDC8,
    "size": 276,
    "symbol": "r1_bae8_connection_event_plan_build",
    "sha256": "e72b8ea7bb55915ba8783ea67e76a3d0d747eb32f808f66e48da2a0a2ba3385a",
    "callers": ((0x00052B58, "B.W"),),
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)


def local_calls(image: bytes, entry: int, end: int, target: int) -> tuple[tuple[int, str], ...]:
    return tuple(
        (address, kind)
        for address, kind in direct_thumb_branches_to(image, DEFAULT_BASE, target)
        if entry <= address < end
    )


def c_string(image: bytes, address: int) -> bytes:
    start = address - DEFAULT_BASE
    return image[start:image.index(b"\0", start)]


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    function = R1_BAE8_CONNECTION_EVENT_FUNCTIONS[0]
    entry = int(function["entry"])
    end = int(function["end_exclusive"])
    body = image[entry - DEFAULT_BASE:end - DEFAULT_BASE]
    executable = image[entry - DEFAULT_BASE:EXECUTABLE_END - DEFAULT_BASE]
    callers = tuple(direct_thumb_branches_to(image, DEFAULT_BASE, entry))
    link_context_calls = local_calls(image, entry, end, 0x000514E0)
    notification_helper_calls = local_calls(image, entry, end, 0x000539B0)
    memset_calls = local_calls(image, entry, end, 0x000277AA)
    literals = struct.unpack_from("<III", image, 0x0007CD7C - DEFAULT_BASE)
    log_string = c_string(image, LOG_STRING_ADDRESS)
    prefixed_log_string = c_string(image, PREFIXED_LOG_STRING_ADDRESS)
    svc_sites = tuple(
        entry + offset
        for offset in range(len(executable) - 1)
        if executable[offset:offset + 2] == b"\xad\xdf"
    )
    if len(body) != int(function["size"]) or \
            hashlib.sha256(body).hexdigest() != function["sha256"] or \
            len(executable) != 198 or \
            hashlib.sha256(executable).hexdigest() != \
            "869bf2a4799c3d53a701556c7fddcb6f48df477405a7a0c1e323d47f0bb94083" or \
            callers != function["callers"] or \
            link_context_calls != ((0x0007CCC6, "BL"),) or \
            notification_helper_calls != (
                (0x0007CD28, "BL"), (0x0007CD46, "BL")) or \
            memset_calls != ((0x0007CD5C, "BL"),) or \
            svc_sites != (0x0007CD1E, 0x0007CD3A) or \
            literals != (0x000BE694, 0x000C44FC, 0x000C441C) or \
            log_string != \
            b"Link context for 0x%02X connection handle could not be fetched." or \
            prefixed_log_string != b"[RING]" + log_string:
        raise ValueError("R1 BAE8 connection-event handler changed")

    return {
        "analysis": "R1 BAE8 connection and CCCD event policy",
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
            "callers": [
                {"address": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        },
        "route": {
            "observer": "r1_bae8_raw_observer",
            "observer_event_id": "0x0010",
            "tail_callsite": "0x00052b58",
        },
        "provider_calls": {
            "link_context_lookup": "0x000514e0",
            "cccd_value_get_svc": "0xad",
            "cccd_value_get_sites": ("0x0007cd1e", "0x0007cd3a"),
            "notification_helper": "ble_srv_is_notification_enabled",
            "notification_helper_sites": ("0x0007cd28", "0x0007cd46"),
        },
        "service_layout": {
            "link_context_manager_offset": 0x28,
            "channel1_cccd_handle_offset": 0x0A,
            "channel2_cccd_handle_offset": 0x1A,
            "callback_offset": 0x2C,
            "link_context_channel1_flag_offset": 0,
            "link_context_channel2_flag_offset": 1,
        },
        "behavior": {
            "log_lookup_failure": True,
            "read_both_cccds_after_lookup_failure": True,
            "cccd_length": 2,
            "cccd_offset": 0,
            "set_flags_only_on_success_callback_and_context": True,
            "clear_disabled_flags": False,
            "callback_event_type": 0,
            "callback_record_bytes": 24,
            "callback_allows_null_link_context": True,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "nordic_link_context_reimplemented": False,
            "softdevice_value_get_reimplemented": False,
            "nordic_cccd_helper_reimplemented": False,
            "live_callback_dispatch_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
