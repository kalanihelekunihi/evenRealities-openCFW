#!/usr/bin/env python3
"""Pin the private GoMore energy-model dispatcher and estimator closure.

This is a read-only ownership gate. It emits no energy algorithm, lookup table,
or locally executable substitute for the licensed provider.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


def _function(
    entry: int,
    end_exclusive: int,
    size: int,
    role: str,
    sha256: str,
    callsites: tuple[int, ...],
    segments: tuple[tuple[int, int], ...] = (),
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": size,
        "role": role,
        "sha256": sha256,
        "callsites": callsites,
        "segments": segments,
        "provider_family": "gomore_health_algorithm_candidate",
        "source_disposition": "vendor_source_required_not_redistributable",
    }


GOMORE_ENERGY_MODEL_FUNCTIONS = (
    _function(0x0002F488, 0x0002F5D8, 336, "energy-model mode dispatcher",
              "6685792d78a984950c2d7f4db9660d146118df272cf61d22b2cc587e93e1d5b9",
              (0x0005F6DC, 0x0005F85A, 0x0005FA30)),
    _function(0x000304D8, 0x00030524, 76, "energy-model output transform",
              "db76d03f6de91caec6124cb309e0f6e7fb43d53a9b24db0e121d493e3deb2f3c",
              (0x0007DC96,)),
    _function(0x0005A448, 0x0005A59C, 340, "energy-model estimator family B",
              "e9a46d2767ade1aef0337bd7c90f81d4a305187d34996b99a852d11a5bce4f36",
              (0x0002F5D2,)),
    _function(0x0005D3F8, 0x0005D4D4, 220, "energy-model result projection",
              "0b8b4768523d69cc571632f7807d183d5ca672e2f3df3c9c1b419e26e0625ff6",
              (0x0005A598, 0x0007DAFC, 0x0007DB32, 0x0007DB9A, 0x00088D70)),
    _function(0x00075D88, 0x00075E0C, 132, "energy-model nonlinear scale helper",
              "cd0a5e47925615715bacdbc87c50a561c88ba1ba3c063f3db2ed349c1b9b6e8d",
              (0x0007DB86, 0x0007DBE0, 0x00088E1C)),
    _function(0x0007DA30, 0x0007DCA8, 632, "table-driven energy estimator",
              "4a1eeec9e1e5b6b5563e814c2f17e74d9adb8f1af90fe46a85e6bf95c59aed6a",
              (0x0002F50A,)),
    _function(0x00088BD0, 0x00088D7C, 426, "energy-model estimator family A",
              "e2562d06dc038acd9336895aacd6d86fb053ea4bb6659f4c665a7fb0326611c1",
              (0x0002F5BA,), ((0x00088BD0, 0x00088D4C),
                              (0x00088D4E, 0x00088D7C))),
    _function(0x00088DB4, 0x00088E5C, 168, "energy-model interpolation helper",
              "4985b8bdbab30e3305369dd0aa55605026344f7db0e4be1d204546cc994e0578",
              (0x0007DAEC, 0x0007DB22, 0x0007DB5E, 0x0007DB7A,
               0x00088D46, 0x00088D60)),
    _function(0x00090E68, 0x00090E86, 30, "energy-model state reset helper",
              "c08ecfcbba8cf696f53274a0b36d3c9984d980c32b9e1d5bab11f0259ddd28a9",
              (0x0005F5FA, 0x000715E4, 0x00088C4C)),
)


def _body(image: bytes, function: dict[str, Any]) -> bytes:
    segments = function["segments"] or ((function["entry"], function["end_exclusive"]),)
    return b"".join(
        image[int(start) - LOAD_BASE:int(end) - LOAD_BASE]
        for start, end in segments
    )


def summarize(image_path: Path) -> dict[str, object]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    functions = []
    for function in GOMORE_ENERGY_MODEL_FUNCTIONS:
        entry = int(function["entry"])
        body = _body(image, function)
        calls = tuple(address for address, _ in direct_thumb_branches_to(
            image, LOAD_BASE, entry))
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                calls != function["callsites"]:
            raise ValueError(f"GoMore energy-model boundary changed at 0x{entry:08x}")
        segments = function["segments"] or ((entry, int(function["end_exclusive"])),)
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "callsites": [f"0x{address:08x}" for address in calls],
            "segments": [
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for start, end in segments
            ],
        })

    return {
        "analysis": "GoMore energy-model dispatcher/estimator provider boundary",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "functions": functions,
        "identity": {
            "existing_energy_output_producer": "0x0005f56c",
            "dispatcher": "0x0002f488",
            "largest_estimator": "0x0007da30",
            "dispatcher_callsites": ["0x0005f6dc", "0x0005f85a", "0x0005fa30"],
            "mode_selector_offset": "0x08",
        },
        "closure": {
            "recursive_unclassified_descendant_count": 9,
            "outside_caller_exclusivity": True,
            "already_gated_gomore_helpers_excluded": True,
            "toolchain_runtime_excluded": True,
        },
        "boundary": {
            "provider_family": "gomore_health_algorithm_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "licensed_provider_required": True,
            "local_algorithm_reimplementation_authorized": False,
        },
        "safety": {
            "static_parser_only": True,
            "algorithm_reimplementation_emitted": False,
            "live_sensor_access": False,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))
