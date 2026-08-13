#!/usr/bin/env python3
"""Emit the exact Nordic nRF52 SystemInit provider boundary in the R1 app."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
SYSTEM_SOURCE = "modules/nrfx/mdk/system_nrf52.c"
WRAPPER_SOURCE = "modules/nrfx/mdk/system_nrf52840.c"


NORDIC_SYSTEM_INIT_FUNCTIONS = [
    {
        "entry": 0x00033364,
        "end_exclusive": 0x00033576,
        "size": 530,
        "symbol": "SystemInit",
        "sha256": "a09c9eaeba82d61e0cc0d0d26778aaf27f13aa0b9aad13e66a5b71a86b7becca",
        "source": SYSTEM_SOURCE,
        "caller_entry": 0x00027488,
        "caller_symbol": "Reset_Handler",
        "callsite": 0x0002748A,
    },
    {
        "entry": 0x0007CA7C,
        "end_exclusive": 0x0007CA8A,
        "size": 14,
        "symbol": "nvmc_config",
        "sha256": "f22f49539484bb5d46cfd079ac9a0b82d693b64b552315b8ab771d57144b3fa1",
        "source": SYSTEM_SOURCE,
        "caller_entry": 0x00033364,
        "caller_symbol": "SystemInit",
        "callsites": (
            0x000334BE, 0x000334D6, 0x000334DE, 0x000334FA,
            0x00033510, 0x0003353E, 0x00033556,
        ),
    },
]


def _word(image: bytes, address: int) -> int:
    return struct.unpack_from("<I", image, address - LOAD_BASE)[0]


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    functions: list[dict[str, Any]] = []
    for function in NORDIC_SYSTEM_INIT_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"Nordic startup body changed at 0x{entry:08x}")
        record = {
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "caller_entry": f"0x{int(function['caller_entry']):08x}",
        }
        if entry == 0x00033364:
            # Reset_Handler loads the Thumb entry from its literal pool and BLXes it.
            target = _word(image, 0x000274A4)
            if target != entry | 1 or image[0x27488 - LOAD_BASE:0x2748C - LOAD_BASE] != \
                    bytes.fromhex("06488047"):
                raise ValueError("Reset_Handler no longer dispatches to SystemInit")
            record["callsite"] = f"0x{int(function['callsite']):08x}"
            record["thumb_target_literal"] = f"0x{target:08x}"
        else:
            actual_callsites = tuple(
                address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry)
            )
            if actual_callsites != function["callsites"]:
                raise ValueError(
                    f"nvmc_config callers changed: {actual_callsites} != "
                    f"{function['callsites']}"
                )
            record["callsites"] = [f"0x{address:08x}" for address in actual_callsites]
        functions.append(record)

    if _word(image, 0x0007CA8C) != 0x4001E504 or \
            _word(image, 0x0007CA90) != 0x4001E400:
        raise ValueError("NVMC CONFIG/READY literal pair changed")

    return {
        "analysis": "R1 application Nordic nRF52 SystemInit provider boundary",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "functions": functions,
        "provider": {
            "family": "nordic_nrf5_sdk_17_1_0",
            "disposition": "use_nordic_sdk",
            "system_source": SYSTEM_SOURCE,
            "wrapper_source": WRAPPER_SOURCE,
            "local_reimplementation_authorized": False,
        },
        "recovered_configuration": {
            "device": "NRF52840_XXAA",
            "hard_float": True,
            "CONFIG_NFCT_PINS_AS_GPIOS": True,
            "CONFIG_GPIO_AS_PINRESET": True,
            "reset_pin": 18,
            "system_core_clock_hz": 64000000,
        },
        "semantic_fingerprints": [
            "nRF52840 FICR variant/revision-gated errata workarounds",
            "TEMP calibration transfer and CCM MAXPACKETSIZE 0xFB",
            "RAM, QSPI, RESETREAS, and FPU CPACR initialization",
            "APPROTECT UICR compatibility handling",
            "NFCPINS UICR conversion using NVMC CONFIG/READY",
            "PSELRESET[0..1] programming to pin 18 using NVMC CONFIG/READY",
            "CMSIS NVIC_SystemReset and 64 MHz SystemCoreClockUpdate",
        ],
        "safety": {
            "static_parser_only": True,
            "provider_body_reimplementation_emitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
