#!/usr/bin/env python3
"""Pin the native Ghidra entry inside the accepted R1 battery runtime service."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
CALL_GRAPH = ROOT / "research/decompilation/application/call-graph.csv"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


R1_BATTERY_RUNTIME_SERVICE_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00031FD0,
    "end_exclusive": 0x00032166,
    "size": 406,
    "role": "R1 battery sampling, charge-state, percentage, and publication orchestration",
    "symbol": "r1_battery_runtime_update_service",
    "sha256": "81fbdac0326291722319030ab711e90075c000759f03e34c3dbf2c1e3291cfd6",
    "callers": ((0x0009127A, "BL"), (0x000913CE, "BL")),
    "inventory": "ghidra_functions_csv",
},)


def callsites_to(entry: int) -> tuple[tuple[int, str], ...]:
    with CALL_GRAPH.open(newline="", encoding="utf-8") as handle:
        return tuple(sorted(
            (int(row["from_address"], 16), "BL")
            for row in csv.DictReader(handle)
            if int(row["callee_entry"], 16) == entry and
            row["reference_type"] == "UNCONDITIONAL_CALL"
        ))


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in R1_BATTERY_RUNTIME_SERVICE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = callsites_to(entry)
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"battery runtime service changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })

    accepted_extent = image[0x00031FCC - LOAD_BASE:0x00032168 - LOAD_BASE]
    if len(accepted_extent) != 412 or hashlib.sha256(accepted_extent).hexdigest() != \
            "863f83ebcc66161453cb498ddbef63e81ea83d42424291e15534367fb4cea5fb":
        raise ValueError("accepted battery runtime extent changed")

    return {
        "analysis": "R1 battery runtime service native-entry reconciliation",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": 1,
        "function_bytes": 406,
        "functions": functions,
        "overlap_reconciliation": {
            "accepted_manual_extent": "0x00031fcc..<0x00032168",
            "accepted_manual_extent_bytes": 412,
            "native_ghidra_entry": "0x00031fd0",
            "leading_veneer_bytes": 4,
            "trailing_alignment_bytes": 2,
            "duplicate_algorithm_body_created": False,
        },
        "behavior": {
            "charge_state_refresh": True,
            "five_sample_voltage_provider": True,
            "nv_compensation_range": "-299...299",
            "charging_float_divisor_bits": "0x3f86c8b4",
            "voltage_ring_samples": 8,
            "percentage_ring_samples": 8,
            "stalled_charge_recovery": True,
            "shared_power_release_when_not_charging": True,
            "percentage_change_publication": True,
            "zero_percentage_return_normalized_to_one": True,
        },
        "ownership": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "existing_clean_room_controller_reused": True,
            "provider_dependencies_admitted_by_this_closure": False,
        },
        "excluded_dependencies": {
            "saadc_sampling": "Nordic provider plus R1 analog adapter",
            "yhm_power_state": "licensed provider boundary",
            "clock_and_publication": "independently owned or unresolved seams",
        },
        "safety": {
            "static_parser_only": True,
            "live_adc_read": False,
            "power_operation": False,
            "notification_send": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
