#!/usr/bin/env python3
"""Pin the dormant R1 health-daily synthetic-data test fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x27000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

R1_HEALTH_DAILY_TEST_FUNCTIONS = ({
    "entry": 0x0008B378,
    "end_exclusive": 0x0008E626,
    "size": 1344,
    "symbol": "r1_health_daily_test_fixture",
    "sha256": "75cfeeac1565b8d44e251089066133f06e946af53ed3a849f230787c436ee255",
    "segments": ((0x0008B378, 0x0008B686), (0x0008D40C, 0x0008D4C2),
                 (0x0008E3F8, 0x0008E4AE), (0x0008E560, 0x0008E626)),
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)


def summarize(path: Path) -> dict[str, object]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")
    function = R1_HEALTH_DAILY_TEST_FUNCTIONS[0]
    body = b"".join(
        image[start - LOAD_BASE:end - LOAD_BASE]
        for start, end in function["segments"]
    )
    if len(body) != function["size"] or \
            hashlib.sha256(body).hexdigest() != function["sha256"]:
        raise ValueError("R1 health-daily test fixture changed")
    return {
        "analysis": "R1 health-daily synthetic-data test fixture",
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": len(body),
        "entry": "0x0008b378",
        "segments": [
            {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}",
             "size": end - start}
            for start, end in function["segments"]
        ],
        "direct_callers": [],
        "behavior": {
            "input_types": {"0": "heart rate", "1": "SpO2", "2": "temperature"},
            "maximum_hours": 24,
            "hour_seconds": 3600,
            "writes_random_synthetic_samples": True,
            "prints_complete_24_hour_record": True,
            "production_reachability_proven": False,
        },
        "ownership": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "production_feature_required": False,
            "vendor_algorithm_included": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
