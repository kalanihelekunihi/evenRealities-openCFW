#!/usr/bin/env python3
"""Pin the private Goodix GH_NADT extrema/peak-mask helper closure."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


def _function(
    entry: int,
    end_exclusive: int,
    role: str,
    sha256: str,
    callers: tuple[tuple[int, str], ...],
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": end_exclusive - entry,
        "role": role,
        "symbol": "goodix_nadt_private_peak_mask_candidate",
        "sha256": sha256,
        "callers": callers,
        "provider_family": "goodix_gh3x2x_candidate",
        "source_disposition": "vendor_source_required_not_redistributable",
    }


# Complete formerly-unclassified direct-call chain reached only from the already
# pinned GH_NADT_pre root at 0x0006E838. Descriptive roles are boundary labels,
# not assertions about private Goodix symbol names.
GOODIX_NADT_PEAK_MASK_FUNCTIONS = (
    _function(
        0x00030114, 0x00030174, "GH_NADT peak-selection entry adapter",
        "86ffd84b5eabbbb7383ea6336db45b32628580be49023bb6df3efadf623b3928",
        ((0x0006E8E6, "BL"),),
    ),
    _function(
        0x0003441C, 0x00034490, "GH_NADT window/descriptor adapter",
        "1641ae97790267d6bd8fc99781f0e940ad42fc3b15c015e96eff02321d6ebae7",
        ((0x00030162, "BL"),),
    ),
    _function(
        0x00047FA8, 0x00048018, "GH_NADT selected-index collector",
        "2541e8de64c0307ae2d13d0fb93d510bf2145e695803ca30867e92c948a449f6",
        ((0x0003444A, "BL"), (0x00034472, "BL")),
    ),
    _function(
        0x00076B78, 0x00076BDC, "GH_NADT private peak-mask orchestrator",
        "a86ef96a9c2046ff06bf0096115c61dcad778323d4ec3e832727cdeb7b2f6ae1",
        ((0x00047FD0, "BL"),),
    ),
    _function(
        0x00030178, 0x00030366, "GH_NADT extrema-neighborhood bit-mask stage",
        "4f3edf2a164e390199812e629c67c6036c1b01b21e585426aae0ceda6aea0484",
        ((0x00076BB6, "BL"),),
    ),
    _function(
        0x00066AB2, 0x00066B2E, "GH_NADT mask-row selection helper",
        "7a9e10c57b462656670156434855de2509f349ad5990ee820efc49ba73df63f3",
        ((0x00076BC2, "BL"),),
    ),
    _function(
        0x00029AA0, 0x00029AD8, "GH_NADT mask-column reduction helper",
        "9330d95dc0f73d51c2523896dcee83ad70cfa0d6e8056eb82f376fbcca3b09a6",
        ((0x00076BCE, "BL"),),
    ),
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    functions = []
    for function in GOODIX_NADT_PEAK_MASK_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"Goodix NADT peak-mask body changed at 0x{entry:08x}")
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if callers != function["callers"]:
            raise ValueError(
                f"Goodix NADT peak-mask caller set changed at 0x{entry:08x}: {callers}"
            )
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"callsite": f"0x{callsite:08x}", "kind": kind}
                for callsite, kind in callers
            ],
        })

    return {
        "analysis": "supplemental Goodix GH_NADT extrema/peak-mask provider boundary",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "functions": functions,
        "callgraph": {
            "existing_provider_root": "0x0006e838",
            "root_callsite": "0x0006e8e6",
            "maximum_private_helper_depth": 5,
            "outside_direct_callers": 0,
            "component": "GH_NADT_pre v1.0.2.0 / 548d894d",
        },
        "boundary": {
            "provider_family": "goodix_gh3x2x_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "private_symbols_or_sdk_version_resolved": False,
            "local_peak_selection_reimplementation_authorized": False,
            "private_thresholds_or_formula_emitted": False,
        },
        "safety": {
            "static_parser_only": True,
            "live_sensor_data_read": False,
            "algorithm_implementation_emitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
