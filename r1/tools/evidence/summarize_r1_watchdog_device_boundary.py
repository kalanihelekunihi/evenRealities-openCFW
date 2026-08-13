#!/usr/bin/env python3
"""Emit the exact R1 watchdog-device and Nordic nrfx_wdt boundary census."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


WATCHDOG_DEVICE_FUNCTIONS = [
    {
        "entry": 0x00056638, "end_exclusive": 0x00056654,
        "symbol": "r1_watchdog_channel_feed_adapter",
        "role": "validate_device_state_and_feed_allocated_channel",
        "provider_family": "r1_nordic_wdt_provider_adapter",
        "sha256": "534e19d257a42c41d56ba3261267e5b691548d166e378a42996c55e8af9ea061",
    },
    {
        "entry": 0x00056658, "end_exclusive": 0x0005668C,
        "symbol": "r1_watchdog_initialize_adapter",
        "role": "initialize_allocate_enable_and_mark_open",
        "provider_family": "r1_nordic_wdt_provider_adapter",
        "sha256": "a2e2dbb1f7f1d6344ac65efcbbe52e46e0d2cafca8ebd9b95e073da7a844a0c5",
    },
    {
        "entry": 0x00056694, "end_exclusive": 0x000566A6,
        "symbol": "r1_watchdog_binding_configuration",
        "role": "fixed_record_and_operation_table_registration",
        "provider_family": "r1_device_registry_configuration_adapter",
        "sha256": "4379e2505f43a616cf240ba170809a0ed57b8dfd3d92b51d6986e14886cbee24",
    },
    {
        "entry": 0x0007B470, "end_exclusive": 0x0007B4D6,
        "symbol": "nrfx_wdt_channel_alloc",
        "role": "Nordic_WDT_reload_channel_allocate",
        "provider_family": "nordic_nrf5_sdk_17_1_0",
        "source": "modules/nrfx/drivers/src/nrfx_wdt.c",
        "sha256": "9977aa9b9e9fa9c9f80db68b66289a25ee158f2985d3eeb8e351efb7d7013f47",
    },
    {
        "entry": 0x0007B508, "end_exclusive": 0x0007B516,
        "symbol": "nrfx_wdt_channel_feed",
        "role": "Nordic_WDT_reload_channel_feed",
        "provider_family": "nordic_nrf5_sdk_17_1_0",
        "source": "modules/nrfx/drivers/src/nrfx_wdt.c",
        "sha256": "36748a8f4fb193ff5b039077b258545bbca30d9ff56fac2ba576113afb0f9c9e",
    },
    {
        "entry": 0x0007B520, "end_exclusive": 0x0007B556,
        "symbol": "nrfx_wdt_enable",
        "role": "Nordic_WDT_interrupt_and_start",
        "provider_family": "nordic_nrf5_sdk_17_1_0",
        "source": "modules/nrfx/drivers/src/nrfx_wdt.c",
        "sha256": "b321c1afe1e05c5c436e17ce4631685c560ad8e97f6f65670c01279b41665734",
    },
    {
        "entry": 0x0007B570, "end_exclusive": 0x0007B5E6,
        "symbol": "nrfx_wdt_init",
        "role": "Nordic_WDT_configuration_and_IRQ_initialize",
        "provider_family": "nordic_nrf5_sdk_17_1_0",
        "source": "modules/nrfx/drivers/src/nrfx_wdt.c",
        "sha256": "0dd0d04621a580b5621355a13e79c864860461371558687913b2c7f125bfb151",
    },
]

for _function in WATCHDOG_DEVICE_FUNCTIONS:
    _function["size"] = int(_function["end_exclusive"]) - int(_function["entry"])


def summarize(image_path: Path) -> dict[str, object]:
    image = image_path.read_bytes()
    image_digest = hashlib.sha256(image).hexdigest()
    if image_digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {image_digest}")

    functions = []
    for function in WATCHDOG_DEVICE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        if len(body) != function["size"] or hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"watchdog boundary changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
        })

    counts: dict[str, int] = {}
    for function in functions:
        family = str(function["provider_family"])
        counts[family] = counts.get(family, 0) + 1
    return {
        "analysis": "R1 watchdog-device/Nordic nrfx_wdt boundary census",
        "image": str(image_path),
        "image_sha256": image_digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "provider_counts": counts,
        "recovered_configuration": {
            "behaviour": "run_in_sleep_pause_in_halt",
            "reload_milliseconds": 10_000,
            "interrupt_priority": 6,
            "reload_channels": 1,
        },
        "functions": functions,
        "source_lineage": {
            "provider": "Nordic nRF5 SDK 17.1.0 nrfx_wdt.c",
            "local_driver_reimplementation_authorized": False,
            "local_adapter_scope": "fixed configuration, lifecycle, and feed scheduling only",
        },
        "safety": {
            "static_parser_only": True,
            "live_watchdog_control": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
