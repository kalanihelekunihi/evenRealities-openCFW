#!/usr/bin/env python3
"""Pin the recovered Goodix GH_HR processing callgraph boundary.

This is an ownership census only.  It emits no heart-rate implementation and
does not convert recovered vendor behavior into clean-room product source.
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
    sha256: str,
    callsites: tuple[int, ...],
    segments: tuple[tuple[int, int], ...],
) -> dict[str, Any]:
    role = (
        "GH_HR feature/event decision core"
        if entry == 0x00032808
        else "GH_HR closed-callgraph helper"
    )
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": size,
        "role": role,
        "sha256": sha256,
        "callsites": callsites,
        "segments": segments,
        "provider_family": "goodix_gh3x2x_candidate",
        "source_disposition": "vendor_source_required_not_redistributable",
    }


# These are exactly the formerly unclassified descendants reachable from the
# already gated GH_HR core at 0x0006D51C in the frozen direct-call graph.
GOODIX_HR_FUNCTIONS = (
    _function(0x00029090, 0x000290B8, 40,
              "99f43d4dc7adb9bf56eae801fec1065f7b45553a26266f05ff43809918bf06f5",
              (0x000328E6, 0x000328F4), ((0x00029090, 0x000290B8),)),
    _function(0x00029656, 0x0002966C, 22,
              "e39b617f8759f42a5cd985fa9877b282ffc86b7b95b51d9578a14c0a48af950f",
              (0x000303B4, 0x000303DA, 0x00032C3E, 0x00032C48, 0x0003763E,
               0x0006D5DA, 0x00070B7E), ((0x00029656, 0x0002966C),)),
    _function(0x000299EC, 0x00029A9C, 176,
              "0d18a28946866e1e8f796ad7fc5bc42cc441285f63e320901e266c84c60de1f8",
              (0x00032E62, 0x000331C0, 0x00033282),
              ((0x000299EC, 0x00029A9C),)),
    _function(0x0002D458, 0x0002D45C, 4,
              "a78fc9996461c9de89dede305a4ebaddf18e69f73df2a59a239610bf4bdef4cd",
              (0x00030406, 0x00034D18, 0x00034D2E, 0x00034DC6, 0x00034DE6,
               0x00034F4E, 0x00034F6E), ((0x0002D458, 0x0002D45C),)),
    _function(0x0002F224, 0x0002F25C, 56,
              "533027372631ec6b27d68b78e1de5133672488114c6840b7452c9aa3e819dd8c",
              (0x00034A5A,), ((0x0002F224, 0x0002F25C),)),
    _function(0x0002F260, 0x0002F2AA, 74,
              "1bc4f877c399b3cf1cff3a86d2ecf0fdb59df602e396ec3759bd67453dbe1a8d",
              (0x00030384, 0x00030396, 0x000303C0, 0x000303FE, 0x0003047A,
               0x00032B3A, 0x00032B46, 0x00032B52, 0x000376E4, 0x0006D5C2,
               0x0006D5E6, 0x0006D836), ((0x0002F260, 0x0002F2AA),)),
    _function(0x00030090, 0x00030110, 128,
              "9eb759ece80f64ff357d30d9d99fe94e29824b2f85b9d42c329c73867932aab7",
              (0x00032DA0, 0x00032EE8, 0x00033328),
              ((0x00030090, 0x00030110),)),
    _function(0x00030368, 0x00030486, 286,
              "e5b9f56f90dd3566e0cdcc3191159f9d5d739cbfbedfd2d2e1f4e3f7649ab521",
              (0x0006D5EE,), ((0x00030368, 0x00030486),)),
    _function(0x00030E1C, 0x00030E64, 72,
              "95c563216cb3d54756db444655cd13d8af8b80636a1704584759b4c4fcf3292c",
              (0x00032DCA,), ((0x00030E1C, 0x00030E64),)),
    _function(0x00032808, 0x00033330, 2814,
              "d2723d09bfc22aef66fafa55623c2d86fb275a1a85b31b96759df0e0a8028a6f",
              (0x0006D5FA,), ((0x00032808, 0x00032C10),
                              (0x00032C1C, 0x00033020),
                              (0x0003303C, 0x000331F4),
                              (0x000331F6, 0x00033330))),
    _function(0x00034490, 0x000344FA, 106,
              "00086b4011800cd2a438662fee1a65cc7e0f60067db032a7612bf84fa4cdff76",
              (0x00048150, 0x00048168, 0x0004817E),
              ((0x00034490, 0x000344FA),)),
    _function(0x00034A58, 0x00034A66, 14,
              "bab66a1503671fa3e44cadfd47c406e3089a150a413638d2a938b7882549a3a6",
              (0x00032BE0, 0x00037398), ((0x00034A58, 0x00034A66),)),
    _function(0x00034A66, 0x00034A7C, 22,
              "bf68da14c26f526e4369ccb1704fe2e305943d8331b41f6c67d0a8c050ec8317",
              (0x0003039E, 0x00037632, 0x0006D5CA),
              ((0x00034A66, 0x00034A7C),)),
    _function(0x00034CBC, 0x0003507A, 956,
              "41bf9766adb1e05d96397c6e20463f9f7b51fc184319261670451cc4fa50dce0",
              (0x0006D5F2,), ((0x00034CBC, 0x0003505A),
                              (0x0003505C, 0x0003507A))),
    _function(0x00035084, 0x000350D8, 84,
              "7cd0df656e68e240d74aacc7db9a6edcf1ad4fcd9b6920c24a4bace1779cae3a",
              (0x0006D688, 0x0006D6AA, 0x0006D6CC, 0x0006D6EE, 0x0006D89A),
              ((0x00035084, 0x000350D8),)),
    _function(0x00036EFC, 0x00036F72, 118,
              "05eecde525037f9c49ba58d1cb7e9ca4ac520a1abc30d5904c009f98cc64f37d",
              (0x000567DE,), ((0x00036EFC, 0x00036F72),)),
    _function(0x0003738C, 0x000373A2, 22,
              "bfc4fd7e0d240bd0113298d5d2d636fe2fc5f6dc2ac75b03bb3ebd9af9a67e65",
              (0x00070B88,), ((0x0003738C, 0x000373A2),)),
    _function(0x00037588, 0x000376FC, 372,
              "4226a6682f55a3c73892a31cf6eab253e4339e794a1a90ae0fbb14e87773e63a",
              (0x0003038A,), ((0x00037588, 0x000376FC),)),
    _function(0x00037710, 0x00037720, 16,
              "65f7a98a4cce7508c9798f09f5fc004beec489937df9bbb4f7d83e675908f3f3",
              (0x000303C8, 0x00032B66, 0x00034CDC),
              ((0x00037710, 0x00037720),)),
    _function(0x00037720, 0x00037738, 24,
              "2cc68dc41e8e0ed1c0f7bb88a9c423a2b7ec5c8e36dc09a6b58dd9d9a491c3ab",
              (0x000303EE, 0x00034D22, 0x00034D38, 0x00034DD0, 0x00034DF0,
               0x00034F58, 0x00034F78), ((0x00037720, 0x00037738),)),
    _function(0x0003773C, 0x000377D2, 150,
              "5db2345cdfadd4cbd5ad894d45db563439f221b20b2e649498c737efa93875f6",
              (0x00034E66, 0x00034FEA), ((0x0003773C, 0x000377D2),)),
    _function(0x00037DEC, 0x00037E8A, 158,
              "14c261ae5690f8d44c617d3cff054f4d217515eeeb8b96c02947a1dc92199bcc",
              (0x00032EB6, 0x000330BA), ((0x00037DEC, 0x00037E8A),)),
    _function(0x00038030, 0x0003804C, 28,
              "41fe15e61d06b99a07adda5e84d9263ed5dc13757cc2b3f8b87b9ddb77a9daa0",
              (0x00087A7C,), ((0x00038030, 0x0003804C),)),
    _function(0x0003DE20, 0x0003DF0A, 234,
              "5785b114a0728e67c96b311409b81422be647869756d2f29995c7c620fe6c183",
              (0x00032B9C,), ((0x0003DE20, 0x0003DF0A),)),
    _function(0x00048018, 0x000481A0, 392,
              "f8022ff47d52fbb45591edbeeb6b9e6ce49125e799a89d4c8d10031084329a51",
              (0x00037776, 0x000377A8), ((0x00048018, 0x000481A0),)),
    _function(0x0004FDB8, 0x0004FDF8, 64,
              "afe564008128bc7e8f9da0281124cde5f197ec277dc84eb27d46a6e6ae1b8c41",
              (0x000328D2, 0x00032CAC, 0x00032CFE, 0x00032D8A, 0x00032ED0,
               0x00032F9C, 0x00032FB6, 0x000331A8, 0x000331D4, 0x000331EE,
               0x000332F6, 0x00033310, 0x00037E60, 0x00037E84),
              ((0x0004FDB8, 0x0004FDF8),)),
    _function(0x000567C4, 0x00056822, 94,
              "b56618e4948650ddf88890bd49806962057ca996e576959c923468517208c3ce",
              (0x0003DE46, 0x0006D84E), ((0x000567C4, 0x00056822),)),
    _function(0x00056828, 0x0005683C, 20,
              "17fe32176b76d401dd20b1d2f43da2b72ce227df014267d9e36c9718887b5229",
              (0x00032CA4, 0x00032CE4, 0x00032D7C, 0x00032E68, 0x00032F94,
               0x000331A0, 0x000331C6, 0x000331CC, 0x0003328C, 0x000332EE,
               0x00037E58, 0x00037E76, 0x00037E7C),
              ((0x00056828, 0x0005683C),)),
    _function(0x00070B60, 0x00070C12, 178,
              "5739c2b40f650bbc26a0609470a07f5d4950317ea86fc8b62d3fd09fa5a6d452",
              (0x0006D658,), ((0x00070B60, 0x00070C12),)),
    _function(0x00086BAC, 0x00086D36, 394,
              "b5cde5b6c7c31622c6e4af29df41081444c9318df020e1f4fafaa01f4973ea00",
              (0x0006D66A,), ((0x00086BAC, 0x00086D36),)),
    _function(0x00087A78, 0x00087A92, 26,
              "4def42f9e0dbe52e82d237b0c2a822360108b6dbf1e280eb5b715b4d9f0da170",
              (0x00029662, 0x0002F22A, 0x00032BD4, 0x0003DE82),
              ((0x00087A78, 0x00087A92),)),
)


def _body(image: bytes, function: dict[str, Any]) -> bytes:
    return b"".join(
        image[start - LOAD_BASE:end - LOAD_BASE]
        for start, end in function["segments"]
    )


def summarize(image_path: Path) -> dict[str, object]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    functions = []
    for function in GOODIX_HR_FUNCTIONS:
        entry = int(function["entry"])
        body = _body(image, function)
        calls = tuple(address for address, _ in direct_thumb_branches_to(
            image, LOAD_BASE, entry))
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                calls != function["callsites"]:
            raise ValueError(f"Goodix GH_HR boundary changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{int(function['end_exclusive']):08x}",
            "callsites": [f"0x{address:08x}" for address in calls],
            "segments": [
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for start, end in function["segments"]
            ],
        })

    return {
        "analysis": "Goodix GH_HR processing provider-boundary closure",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "functions": functions,
        "identity": {
            "component": "Goodix GH_HR",
            "existing_provider_root": "0x0006d51c",
            "root_callsite": "0x0006d5fa",
            "largest_new_entry": "0x00032808",
            "existing_version": "GH_HR_exc_pv_v2.0.3.0_CONF_nc_21d2063d_002271a1",
        },
        "closure": {
            "formerly_unclassified_descendants": 31,
            "maximum_call_depth": 4,
            "outside_direct_callers": 0,
            "toolchain_runtime_and_sensor_heap_excluded": True,
        },
        "boundary": {
            "provider_family": "goodix_gh3x2x_candidate",
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
