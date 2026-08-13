#!/usr/bin/env python3
"""Pin the R1-owned retained reset-trace and reset-adapter closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x27000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

R1_RESET_TRACE_FUNCTIONS = (
    {
        "entry": 0x27484,
        "size": 4,
        "symbol": "r1_reset_trace_program_counter_probe",
        "sha256": "2f36aa868e36a46cb9de8406212506a64e14817b3c631b90f30a905674fac3f9",
        "extents": ((0x27484, 0x27488),),
        "callsites": (0x58A9E, 0x7EFEC),
    },
    {
        "entry": 0x58A9A,
        "size": 74,
        "symbol": "r1_reset_trace_capture_site_adapter",
        "sha256": "bde43a241c98603e87d276d909e04b4a3a886c3f8f4105bfb05858b753ad5c39",
        "extents": ((0x58A9A, 0x58AB8), (0x7EEDA, 0x7EF06)),
        "callsites": (0x8F30A,),
    },
    {
        "entry": 0x7A5E0,
        "size": 36,
        "symbol": "r1_fault_reset_adapter",
        "sha256": "77f3d4d2be4de22f3dc279b544d03040d312d8ee7be3ea82d20d34ffb0a47388",
        "extents": ((0x7A5E0, 0x7A604),),
        "callsites": (0x274B4, 0x274C0, 0x274CC, 0x274D8, 0x274E4),
    },
    {
        "entry": 0x7EDFC,
        "size": 48,
        "symbol": "r1_reset_trace_byte_read",
        "sha256": "bdba1d9e048b2fdcd3026ae9e30695dbdfaf87cfbd0f2f1999717c17d202355a",
        "extents": ((0x7EDFC, 0x7EE2C),),
        "callsites": (0x7EE86, 0x7EE92, 0x7EE9E, 0x7EEAA, 0x7EF56,
                      0x7EF62, 0x7EF6E, 0x7EF7A, 0x81AF4, 0x81B42),
    },
    {
        "entry": 0x7EE30,
        "size": 70,
        "symbol": "r1_reset_trace_byte_write",
        "sha256": "6704ba247e2313adaff20df009598e1182e338277b3e4e92a6c088c79b621635",
        "extents": ((0x7EE30, 0x7EE76),),
        "callsites": (0x7EEE2, 0x7EEEC, 0x7EEF6, 0x7EF02, 0x7EF0C,
                      0x7EF14, 0x7EF1C, 0x7EF24, 0x7EF2C, 0x7EF34,
                      0x7EF3C, 0x7EF48, 0x7EFB2, 0x7EFBC, 0x7EFC6,
                      0x7EFD2, 0x7EFE6, 0x7F012),
    },
    {
        "entry": 0x7EE7C,
        "size": 94,
        "symbol": "r1_reset_trace_return_address_read",
        "sha256": "f18ca971732969e60bc92ceba01f0b9d43786390c6df5bae0f669bff265997aa",
        "extents": ((0x7EE7C, 0x7EEDA),),
        "callsites": (0x81AB8,),
    },
    {
        "entry": 0x7EF06,
        "size": 70,
        "symbol": "r1_reset_trace_addresses_clear",
        "sha256": "75f3a2038e40662326683c09ae2a344c2cf935360fa1425348f475b9315a49e5",
        "extents": ((0x7EF06, 0x7EF4C),),
        "callsites": (0x7EFDA, 0x7F006),
    },
    {
        "entry": 0x7EF4C,
        "size": 94,
        "symbol": "r1_reset_trace_program_counter_read",
        "sha256": "957a422f61c5ef5d497ff8db7e28e5a17af0a6ab0c47df4358d6d1ebdb23d593",
        "extents": ((0x7EF4C, 0x7EFAA),),
        "callsites": (0x81A7A,),
    },
    {
        "entry": 0x7EFAA,
        "size": 44,
        "symbol": "r1_reset_trace_program_counter_write",
        "sha256": "87f1ceef56d1255890b15f103c2afd4e426ccf58606f6e59ca899323d79a721a",
        "extents": ((0x7EFAA, 0x7EFD6),),
        "callsites": (0x58AA4, 0x7EFF0),
    },
    {
        "entry": 0x7EFD6,
        "size": 20,
        "symbol": "r1_reset_trace_reboot_caller_write",
        "sha256": "f5f20cd326030969b639bda3b9561b04fbc68e6ac180ed986ede7131b6944464",
        "extents": ((0x7EFD6, 0x7EFEA),),
        "callsites": (0x3E9CE, 0x84428),
    },
    {
        "entry": 0x7EFEA,
        "size": 20,
        "symbol": "r1_reset_trace_current_site_capture",
        "sha256": "c997bcb97299bfbeaf3eedf09363fb0e3b48ee027af96d4412cb379c34a0e6b4",
        "extents": ((0x7EFEA, 0x7EFFE),),
        "callsites": (0x4602C, 0x4606E, 0x46090, 0x7A5E6),
    },
    {
        "entry": 0x7EFFE,
        "size": 24,
        "symbol": "r1_reset_trace_persist_tag_write",
        "sha256": "0f14dfd6b784417c86fd3f583af41a31c055e046f496d05a4ccb53895c110b86",
        "extents": ((0x7EFFE, 0x7F016),),
        "callsites": (0x46028, 0x4606A, 0x4608C, 0x6298C, 0x62D7C,
                      0x7A5E2),
    },
)


def flash_bytes(image: bytes, address: int, length: int) -> bytes:
    offset = address - LOAD_BASE
    if offset < 0 or offset + length > len(image):
        raise ValueError(f"address outside image: 0x{address:08x}")
    return image[offset:offset + length]


def function_bytes(image: bytes, function: dict[str, object]) -> bytes:
    return b"".join(
        flash_bytes(image, start, end - start)
        for start, end in function["extents"]
    )


def summarize(path: Path) -> dict[str, object]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    output: list[dict[str, object]] = []
    for function in R1_RESET_TRACE_FUNCTIONS:
        entry = int(function["entry"])
        body = function_bytes(image, function)
        calls = tuple(
            address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry)
        )
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                calls != function["callsites"]:
            raise ValueError(f"R1 reset-trace function changed at 0x{entry:08x}")
        item = dict(function)
        item.update(
            entry=f"0x{entry:08x}",
            extents=[
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for start, end in function["extents"]
            ],
            callsites=[f"0x{address:08x}" for address in calls],
        )
        output.append(item)

    return {
        "analysis": "R1 retained reset-trace clean-room closure",
        "image_sha256": digest,
        "function_count": len(output),
        "function_bytes": sum(int(item["size"]) for item in output),
        "functions": output,
        "record": {
            "bytes": 16,
            "crc_input_bytes": 14,
            "crc": "Modbus CRC16",
            "field_bytes": 13,
            "persist_tag_index": 0,
            "reboot_caller_index": 1,
            "return_address_indices": [2, 3, 4, 5],
            "program_counter_indices": [6, 7, 8, 9],
            "fault_tag": 7,
        },
        "source_boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "reset_provider": "Nordic SDK 17.1.0 CMSIS NVIC_SystemReset",
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
