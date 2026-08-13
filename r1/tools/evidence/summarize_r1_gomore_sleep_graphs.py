#!/usr/bin/env python3
"""Pin the paired GoMore sleep-classifier graph-builder boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
EXPECTED_ENTRY_SHA256 = "d8cbe6e0812df229bc45921b278027817c454d1c0a7084435c2f1e8516964955"
EXPECTED_BODY_SHA256 = "cccd90d00fd6e47ede7c2b3928d67c6cd6ab2202b598cb90958158a9f77fe7ac"
EXPECTED_CALLMAP_SHA256 = "cf8faa6d8f95904421c17ea0950992a532ac39ea70b5bab8e920b677eb88fcc6"


def _function(
    entry: int,
    end_exclusive: int,
    symbol: str,
    sha256: str,
    callsites: tuple[int, ...],
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": end_exclusive - entry,
        "segments": ((entry, end_exclusive),),
        "symbol": symbol,
        "sha256": sha256,
        "callsites": callsites,
        "provider_family": "gomore_health_algorithm_candidate",
        "source_disposition": "vendor_source_required_not_redistributable",
    }


GOMORE_SLEEP_GRAPH_FUNCTIONS = (
    _function(0x0002874C, 0x00028AC8, "gomore_sleep_graph_family_zero_candidate",
              "d6852587eae7537e604db32d01d9ad20f65213a11bb0cb8fc60833b0c821aa96",
              (0x00034186,)),
    _function(0x00028B8A, 0x00028BAE, "gomore_sleep_graph_mode_two_allocate_candidate",
              "aae69ef808f0715f4066cf134d417a90eb348a94a09778530af7e685bc0d58db",
              ()),
    _function(0x0002966C, 0x000299E0, "gomore_sleep_graph_family_nonzero_candidate",
              "567b58852908649927ab76c84cfa008239dc54d8d49827172f66f2c94a1a692a",
              (0x000340BA,)),
    _function(0x000340A0, 0x0003418C, "gomore_sleep_graph_family_dispatch_candidate",
              "0391ad699d487be7def954d813437839a0e16e69bfc804be261c8b0dcb57c2f1",
              (0x00028BA2, 0x00048D3A, 0x00072C04)),
    _function(0x00048D22, 0x00048D46, "gomore_sleep_graph_mode_one_allocate_candidate",
              "f2faa98c4dbb7692b88d7b84baf2033b3e61fd1114a8f0fe1a39b8714aada77d",
              ()),
    _function(0x00072BE0, 0x00072C48, "gomore_sleep_graph_mode_zero_allocate_candidate",
              "c61c86867bd6c6fe669a6648e5c9c10bdcd1b1b7556d368d6fcab320beeb2491",
              ()),
)


def _mapped(image: bytes, start: int, end: int) -> bytes:
    return image[start - LOAD_BASE:end - LOAD_BASE]


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    image_digest = hashlib.sha256(image).hexdigest()
    if image_digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {image_digest}")

    ordered = tuple(sorted(GOMORE_SLEEP_GRAPH_FUNCTIONS, key=lambda item: item["entry"]))
    entry_digest = hashlib.sha256(b"".join(
        int(item["entry"]).to_bytes(4, "little") for item in ordered
    )).hexdigest()
    bodies = []
    callmap = []
    output = []
    for item in ordered:
        entry = int(item["entry"])
        end = int(item["end_exclusive"])
        body = _mapped(image, entry, end)
        calls = tuple(address for address, _ in direct_thumb_branches_to(
            image, LOAD_BASE, entry
        ))
        if len(body) != item["size"] or \
                hashlib.sha256(body).hexdigest() != item["sha256"] or \
                calls != item["callsites"]:
            raise ValueError(f"GoMore sleep graph changed at 0x{entry:08x}")
        bodies.append(body)
        callmap.append([f"0x{entry:08x}", [f"0x{x:08x}" for x in calls]])
        output.append({
            **item,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callsites": [f"0x{x:08x}" for x in calls],
            "segments": [{
                "start": f"0x{entry:08x}",
                "end_exclusive": f"0x{end:08x}",
                "size": end - entry,
            }],
        })

    body_digest = hashlib.sha256(b"".join(bodies)).hexdigest()
    callmap_digest = hashlib.sha256(json.dumps(
        callmap, separators=(",", ":")
    ).encode()).hexdigest()
    if entry_digest != EXPECTED_ENTRY_SHA256 or \
            body_digest != EXPECTED_BODY_SHA256 or \
            callmap_digest != EXPECTED_CALLMAP_SHA256:
        raise ValueError("GoMore sleep graph aggregate changed")

    constructor_table = struct.unpack(
        "<III", _mapped(image, 0x000BCF40, 0x000BCF4C)
    )
    if constructor_table != (0x00072BE1, 0x00048D23, 0x00028B8B):
        raise ValueError("GoMore sleep graph constructor table changed")

    models = {
        "modes_below_100": (0x000B2458, 0x000B7998,
                            "da353b02976da84378f6321b2f5ec7cbc4c184eb706b1d6a7fad5499258c4861"),
        "modes_at_least_100": (0x000B7998, 0x000BCED8,
                               "09f807f0c73daae139a0f2aa39ec37b4c57db8c6a7178e943aec6bd8913ee82c"),
    }
    model_output = {}
    for name, (start, end, expected) in models.items():
        digest = hashlib.sha256(_mapped(image, start, end)).hexdigest()
        if digest != expected:
            raise ValueError(f"GoMore sleep classifier model changed: {name}")
        model_output[name] = {
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "bytes": end - start,
            "sha256": digest,
        }

    return {
        "analysis": "GoMore paired sleep-classifier graph-builder boundary",
        "image": str(image_path),
        "image_sha256": image_digest,
        "entry_set_sha256": entry_digest,
        "body_set_sha256": body_digest,
        "callmap_sha256": callmap_digest,
        "function_count": len(output),
        "function_bytes": sum(int(item["size"]) for item in output),
        "functions": output,
        "constructor_table": {
            "address": "0x000bcf40",
            "thumb_pointers": [f"0x{value:08x}" for value in constructor_table],
        },
        "classifier_models": model_output,
        "boundary": {
            "provider_family": "gomore_health_algorithm_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "local_graph_or_model_reimplementation_authorized": False,
            "licensed_provider_required": True,
            "goodix_graph_0x0004387c_included": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
