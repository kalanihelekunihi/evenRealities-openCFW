#!/usr/bin/env python3
"""Pin the R1-only FreeRTOS 10.5.1 timer-version discriminator."""

from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from summarize_r1_gomore_call_graph import direct_thumb_branches_to

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x27000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

FREERTOS_VERSION_FUNCTIONS = [{
    "entry": 0x85440, "end_exclusive": 0x85468, "size": 40,
    "symbol": "prvReloadTimer", "source": "timers.c",
    "sha256": "d03d69b29abd0f1d1fd5c818b9cda349717d56534de9709497af868b7cb4b635",
    "callsites": (0x852C2, 0x85354),
}]

def summarize(path: Path) -> dict[str, object]:
    image = path.read_bytes(); digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256: raise ValueError(f"unexpected application image SHA-256: {digest}")
    item = FREERTOS_VERSION_FUNCTIONS[0]; entry = item["entry"]; end = item["end_exclusive"]
    body = image[entry-LOAD_BASE:end-LOAD_BASE]
    calls = tuple(a for a, _ in direct_thumb_branches_to(image, LOAD_BASE, entry))
    if len(body) != item["size"] or hashlib.sha256(body).hexdigest() != item["sha256"] or calls != item["callsites"]:
        raise ValueError("FreeRTOS version discriminator changed")
    return {"analysis": "FreeRTOS 10.5.1 kernel version discriminator", "image_sha256": digest,
            "function_count": 1, "function_bytes": 40,
            "functions": [{**item, "entry": f"0x{entry:08x}", "end_exclusive": f"0x{end:08x}",
                           "callsites": [f"0x{x:08x}" for x in calls]}],
            "provider": {"core": "freertos_kernel_10_5_1_authenticated",
                         "port": "nordic_nrf52_port_from_sdk_17_1_0",
                         "local_reimplementation_authorized": False}}

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(p.parse_args().image), indent=2, sort_keys=True))
