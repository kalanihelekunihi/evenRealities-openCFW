#!/usr/bin/env python3
"""Pin the exact Nordic power-management shutdown cluster in the R1 image."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x27000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
SOURCE = "components/libraries/pwr_mgmt/nrf_pwr_mgmt.c"

NORDIC_POWER_MANAGEMENT_FUNCTIONS = (
    {
        "entry": 0x79D50,
        "end_exclusive": 0x79DA8,
        "size": 88,
        "symbol": "nrf_pwr_mgmt_shutdown",
        "sha256": "c6e216bd9dac1ac011389a3d30b918072e3f66c599095e1f57350bd3dc356772",
        "callsites": (0x52070, 0x567B8),
    },
    {
        "entry": 0x8F234,
        "end_exclusive": 0x8F328,
        "size": 244,
        "symbol": "shutdown_process",
        "sha256": "5e2fb1680fe1e62efad43cc8374fb60605b392a677f4f1683cb09f1a15852725",
        "callsites": (0x79DA2,),
    },
)


def flash_bytes(image: bytes, address: int, length: int) -> bytes:
    offset = address - LOAD_BASE
    if offset < 0 or offset + length > len(image):
        raise ValueError(f"address outside image: 0x{address:08x}")
    return image[offset:offset + length]


def summarize(path: Path) -> dict[str, object]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    output: list[dict[str, object]] = []
    for function in NORDIC_POWER_MANAGEMENT_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = flash_bytes(image, entry, end - entry)
        calls = tuple(
            address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry)
        )
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                calls != function["callsites"]:
            raise ValueError(f"Nordic power-management function changed at 0x{entry:08x}")
        item = dict(function)
        item.update(
            entry=f"0x{entry:08x}",
            end_exclusive=f"0x{end:08x}",
            source=SOURCE,
            callsites=[f"0x{address:08x}" for address in calls],
        )
        output.append(item)

    return {
        "analysis": "Nordic SDK 17.1.0 power-management shutdown closure",
        "image_sha256": digest,
        "function_count": len(output),
        "function_bytes": sum(
            int(item["size"]) for item in NORDIC_POWER_MANAGEMENT_FUNCTIONS
        ),
        "functions": output,
        "configuration": {
            "NRF_PWR_MGMT_CONFIG_USE_SCHEDULER": 0,
            "SOFTDEVICE_PRESENT": True,
            "shutdown_continue_value": 4,
            "prepare_dfu_value": 2,
            "prepare_reset_value": 3,
        },
        "provider": {
            "family": "nordic_nrf5_sdk_17_1_0",
            "source": SOURCE,
            "local_reimplementation_authorized": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
