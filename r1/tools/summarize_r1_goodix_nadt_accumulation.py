#!/usr/bin/env python3
"""Pin the remaining private Goodix GH_NADT accumulation/decision helper closure."""

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
    sha256: str,
    callers: tuple[tuple[int, str], ...],
    segments: tuple[tuple[int, int], ...] = (),
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": sum(end - start for start, end in segments) if segments
                else end_exclusive - entry,
        "role": "GH_NADT closed-callgraph accumulation/decision helper",
        "sha256": sha256,
        "callers": callers,
        "segments": segments,
        "provider_family": "goodix_gh3x2x_candidate",
        "source_disposition": "vendor_source_required_not_redistributable",
    }


# Every formerly-unclassified entry reachable from the eight remaining direct
# calls of the pinned GH_NADT root at 0x0006E838. All direct callers are either
# inside this tuple or already gated Goodix functions. The two composite entries
# include their compiler-shared tail blocks explicitly.
GOODIX_NADT_ACCUMULATION_FUNCTIONS = (
    _function(0x000290BC, 0x000290DC, "7fc8eded36b20285d51918f48bee2fd6bebefdb703e597958f98897bd8e90724", ((0x0006E908, "BL"),)),
    _function(0x0002F2F8, 0x0002F472, "0d8207628374b1ff1cd09c3d7653ddbbb82ccd973a298073d342cd23ceebe515", ((0x0007314A, "BL"),)),
    _function(0x0002F660, 0x0002F7C2, "2def440e994e4f25516d3607c1cbfb003c3f17778f9ee7a98f584544d6404c6c", ((0x000357E2, "BL"),)),
    _function(0x0002FEE2, 0x0002FF0E, "3406976ddf832dae407a6a9d0a161d8f7fb5a2669dd803fa97c3c8a90f5312e6", ((0x0002F69C, "BL"), (0x0002F6AE, "BL")), ((0x0002FEE2, 0x0002FF0E), (0x0002F2AC, 0x0002F2F2))),
    _function(0x00030970, 0x000309DC, "547244759a6167e4642255ecc7dc5b65e0ec04f4afd2c0662970f195630636af", ((0x00073138, "BL"),)),
    _function(0x00030CD8, 0x00030E10, "db6913cbf5915b831c032abd0afe90bb5353b9854e14d4f29a5bfe372ba0efdd", ((0x000730B2, "BL"), (0x000730C2, "BL"))),
    _function(0x000357CE, 0x00035812, "a18ec8e2992fa3e776dc0949c6449b25321802938114a9e02f8e301dd18dac36", ((0x0006E8C0, "BL"),)),
    _function(0x00035812, 0x00035850, "73bf6f97f8242f9ec16f01e648d90005a4f32d11ca1bad30b3a3d9863d27e013", ((0x00030D0C, "BL"),)),
    _function(0x00036282, 0x000362B6, "444637c826170bb2e46a1cb9ee58c92f3d4e0eb82a90c1a2b5aa74346adc9421", ((0x0006E926, "BL"),)),
    _function(0x00036974, 0x00036B40, "45ba48d1583b4a554014a6695eae5061ff50ee2bbe8995430efaba47945d337d", ((0x0006EAA8, "BL"),)),
    _function(0x00036C32, 0x00036C60, "7a50d9d39a1f8541640595033febb5fd80da825013cc5d4ab309ee674961a8f1", ((0x000362AA, "BL"),)),
    _function(0x00036DD4, 0x00036EAC, "b3f88d05133573f3196c15e60589b96537c65576417c0f61939477e66352840b", ((0x0002FEF8, "BL"),)),
    _function(0x000377D8, 0x0003788A, "ac111b5ddd5971bfdbdd3447ce902aa90127292df05dcf229e94ece18a50ae3e", ((0x00077DFE, "BL"),)),
    _function(0x0003F89C, 0x0003F9D8, "3193960a29c218f12dddbc2a2ff5fdc9c3d39fec489f15c383867fd847a8a578", ((0x0009187C, "BL"),)),
    _function(0x00043860, 0x0004387C, "6c9e3234889027a5802a39e045c29e3756d74aafa31a22e923f266328425a417", ((0x00091886, "BL"),)),
    _function(0x00044A78, 0x00044BD4, "86ccddba2dc45d37e3a4328964a5943867997e6c7689279ef00bd4cf274e4ce0", ((0x0006EA56, "BL"),)),
    _function(0x000481A4, 0x00048234, "1798eff3dd89b30f19c3ff55fb3cee40efa8a75caeb881f5aa56558c23795161", ((0x00077D88, "BL"),)),
    _function(0x00061C48, 0x00061D86, "5ddf758d3191994a62ffe77c43fe5c28687de2803a58ce70834bce9242be15bd", ((0x000357F0, "BL"),)),
    _function(0x00066458, 0x00066470, "85f8a4e389d893fe42326ea3257d4b5dfd9e652a4f5c385a733d12f80f358dba", ((0x00043870, "BL"),), ((0x00066458, 0x00066470), (0x0009293E, 0x0009295A))),
    _function(0x000665A0, 0x00066608, "a3a21bc16f1adeeedaf1ccf2044729a5a296b1a2dfcf46f4c5887453839a7af2", ((0x0002F7AE, "BL"),)),
    _function(0x00072DCC, 0x00072FB6, "34eabb03e0c50157b5693d08c4f496f2e6d1cfed8e428118226e557593689ecf", ((0x0006E892, "BL"),)),
    _function(0x0007309C, 0x0007311E, "d76387c7fe3f4c10dad416e44930e6fa1dcfe11496623f216189e44549aa0e8e", ((0x0003099E, "BL"), (0x0007672A, "BL"))),
    _function(0x0007311E, 0x00073154, "035447bad43eca5d647f9d27b2573b3784993b5b4581a4d41a77de430464418a", ((0x00077DB4, "BL"), (0x00077DE4, "BL"))),
    _function(0x0007412C, 0x0007418A, "681ead43ebe04532e67f24a862bb3da9cd277ce473df87cd412008f62c88cef9", ((0x0006E996, "BL"), (0x0006EAD8, "BL"))),
    _function(0x00076A68, 0x00076B64, "41c8ccbc01efa3af8d94d51af088e76ac0916167315a4ed90c3417f2f1ced410", ((0x0006E8A8, "BL"),)),
    _function(0x00077D2C, 0x00077E26, "74290a65c9e315f8622592fcd820db1317f59a14e41785eae3e99f0be72a6739", ((0x000290D6, "BL"),)),
    _function(0x00091870, 0x00091890, "e9db522136961fea0fe78ead865140bdbbc57441f591124ff4e576c0ffb92659", ((0x000290C8, "BL"),)),
    _function(0x00092900, 0x0009291E, "a0b0c98ffb51c492ccf6a8a9f9ea34279f30a567ec30ed63da38cf39ae529ce2", ((0x000377F8, "BL"),)),
    _function(0x00092988, 0x000929B6, "8a3a2e95f117d8c0acb056ca5610ece55a494d27c8c1a2d43bbef0dded053936", ((0x0002F366, "BL"), (0x00044B4A, "BL"))),
    _function(0x0009775C, 0x00097796, "1aea673af1706d9c614086904531e7a8df34542beee66d15110db6cbd886ecff", ((0x00036E00, "BL"), (0x00036E3E, "BL"))),
)


def _body(image: bytes, function: dict[str, Any]) -> bytes:
    segments = function["segments"] or (
        (int(function["entry"]), int(function["end_exclusive"])),
    )
    return b"".join(
        image[start - LOAD_BASE:end - LOAD_BASE] for start, end in segments
    )


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    functions = []
    for function in GOODIX_NADT_ACCUMULATION_FUNCTIONS:
        entry = int(function["entry"])
        body = _body(image, function)
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"Goodix NADT accumulation closure changed at 0x{entry:08x}")
        segments = function["segments"] or (
            (entry, int(function["end_exclusive"])),
        )
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
            "segments": [
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for start, end in segments
            ],
        })

    return {
        "analysis": "supplemental Goodix GH_NADT accumulation/decision provider boundary",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "composite_function_count": sum(bool(item["segments"]) for item in GOODIX_NADT_ACCUMULATION_FUNCTIONS),
        "functions": functions,
        "callgraph": {
            "existing_provider_root": "0x0006e838",
            "direct_new_root_callsites": [
                "0x0006e892", "0x0006e8a8", "0x0006e8c0", "0x0006e908",
                "0x0006e926", "0x0006e996", "0x0006ea56", "0x0006eaa8",
                "0x0006ead8",
            ],
            "outside_non_goodix_callers": 0,
            "component": "GH_NADT_pre v1.0.2.0 / 548d894d",
        },
        "boundary": {
            "provider_family": "goodix_gh3x2x_candidate",
            "source_disposition": "vendor_source_required_not_redistributable",
            "local_algorithm_reimplementation_authorized": False,
            "private_constants_or_formula_emitted": False,
            "toolchain_and_sensor_heap_excluded": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
