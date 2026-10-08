#!/usr/bin/env python3
"""Verify GX8002 image-A KWS model extents and emit metadata only.

The command and weights are hashed in place; their bytes are never written to
an output file. This checks the locked stock codec image, not model-source
completeness or NPU execution semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
DEFAULT_CODEC = ROOT / "g2/blobs/official/g2-2.2.6.10/firmware_codec.bin"
LOCKED_SIZE = 326092
LOCKED_SHA256 = "b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0"
FWPK_SEGMENT_OFFSET = 38284
IMAGE_A_END = 0x2F3B0
MODEL_START = 0xF804
TASK_INIT_OFFSET = 0x8C28
TASK_INIT_BYTES = 56

GETTERS = {
    "cmd": {"offset": 0x8BF4, "size": 9164, "bytes": "00eacc233c780000"},
    "weight": {"offset": 0x8BFC, "size": 120800, "bytes": "00eae0d7b0383c78"},
    "ops": {"offset": 0x8C04, "size": 0, "bytes": "00303c78"},
    "data": {"offset": 0x8C08, "size": 13056, "bytes": "cc3006403c78"},
    "tmp": {"offset": 0x8C10, "size": 4, "bytes": "04303c78"},
}
TASK_INIT_SHA256 = "abef8eff3685a8e789509abad858f5f1323969ae83d0a7c4eb160f56d91845fd"
STAGING_ARENA_BASE = 0x20000000
EXPECTED_COMMAND_CPU = 0x20003304
EXPECTED_WEIGHT_CPU = 0x200056D0


class VerificationError(ValueError):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def align4(value: int) -> int:
    return (value + 3) & ~3


def verify(codec: bytes, *, command_start: int = MODEL_START,
           command_size: int = GETTERS["cmd"]["size"],
           weight_start: int | None = None,
           weight_size: int = GETTERS["weight"]["size"]) -> dict:
    """Verify extents against bytes in a locked codec payload; return metadata."""
    require(len(codec) == LOCKED_SIZE and sha(codec) == LOCKED_SHA256,
            "codec payload does not match the locked official image")
    require(len(codec) >= FWPK_SEGMENT_OFFSET + IMAGE_A_END,
            "codec payload is truncated before image A end")
    seg = codec[FWPK_SEGMENT_OFFSET:]
    if weight_start is None:
        weight_start = command_start + command_size

    # Verify all five compiled getter return bodies in the hash-pinned image.
    for name, fact in GETTERS.items():
        off = fact["offset"]
        expected = bytes.fromhex(fact["bytes"])
        require(seg[off:off + len(expected)] == expected,
                f"stock {name} size getter bytes changed at segment+0x{off:x}")
    # movi 9164; movi 55264 + bseti bit 16 (120800); remaining getters
    # return 0, 13056, and 4. The instruction encodings above pin each value.

    require(command_start == MODEL_START,
            f"wrong command start: 0x{command_start:x}")
    require(command_size == GETTERS["cmd"]["size"],
            f"wrong command extent: {command_size}")
    require(weight_start == command_start + command_size,
            f"wrong weight start: 0x{weight_start:x}")
    require(weight_size == GETTERS["weight"]["size"],
            f"wrong weight extent: {weight_size}")
    command_end = command_start + command_size
    weight_end = weight_start + weight_size
    require(command_end == 0x11BD0, "command boundary disagrees with stock layout")
    require(weight_end == IMAGE_A_END, "model extents do not end at image-B boundary")

    # The stock setup lays out ops/data/tmp before cmd and weights in its
    # candidate DRAM arena. Round each getter extent to the observed 4-byte
    # alignment, then derive both staged destinations from actual getter sizes.
    cmd_cpu = STAGING_ARENA_BASE + sum(
        align4(GETTERS[k]["size"]) for k in ("ops", "data", "tmp"))
    weight_cpu = cmd_cpu + align4(GETTERS["cmd"]["size"])
    weight_cpu_end = weight_cpu + align4(GETTERS["weight"]["size"])
    require(cmd_cpu == EXPECTED_COMMAND_CPU,
            f"getter-derived command staging address changed: 0x{cmd_cpu:x}")
    require(weight_cpu == EXPECTED_WEIGHT_CPU,
            f"getter-derived weight staging address changed: 0x{weight_cpu:x}")

    command = seg[command_start:command_end]
    weight = seg[weight_start:weight_end]
    require(len(command) == command_size and len(weight) == weight_size,
            "model extent falls outside available image bytes")

    # This 56-byte stock routine consumes a GRUS-compatible task object. Its
    # field transfers (including cmd +0x14 and weight +0x1c) are anchored by
    # the raw image hash and separately reviewed disassembly.
    task_init = seg[TASK_INIT_OFFSET:TASK_INIT_OFFSET + TASK_INIT_BYTES]
    require(sha(task_init) == TASK_INIT_SHA256,
            "stock task initializer body changed")

    return {
        "schema_version": 1,
        "verification": "PASS: locked stock codec bytes and model extent metadata",
        "codec": {"size": len(codec), "sha256": sha(codec),
                  "fwpk_segment_offset": FWPK_SEGMENT_OFFSET},
        "interface": {
            "getter_return_sizes_bytes": {k: v["size"] for k, v in GETTERS.items()},
            "grus_task_fields": {
                "module_id": "0x00", "ops": "0x04", "data": "0x08",
                "input": "0x0c", "output": "0x10", "cmd": "0x14",
                "tmp_mem": "0x18", "weight": "0x1c",
            },
            "task_initializer": {
                "segment_offset": f"0x{TASK_INIT_OFFSET:x}",
                "length": TASK_INIT_BYTES, "sha256": sha(task_init),
                "field_transfer_evidence": "raw-body hash; see evidence references",
            },
        },
        "image_a_model": {
            "commands": {"segment_extent": [command_start, command_end],
                          "hex_extent": f"[0x{command_start:x},0x{command_end:x})",
                          "size": len(command), "sha256": sha(command),
                          "staged_cpu_address": f"0x{cmd_cpu:08x}",
                          "kind": "gxNPU command stream; executable by NPU"},
            "weights": {"segment_extent": [weight_start, weight_end],
                        "hex_extent": f"[0x{weight_start:x},0x{weight_end:x})",
                        "size": len(weight), "sha256": sha(weight),
                        "staged_cpu_address": f"0x{weight_cpu:08x}",
                        "kind": "trained-model weights/data"},
            "staged_layout": {
                "arena_base": f"0x{STAGING_ARENA_BASE:08x}",
                "command_start": f"0x{cmd_cpu:08x}",
                "command_end_and_weight_start": f"0x{weight_cpu:08x}",
                "weight_end": f"0x{weight_cpu_end:08x}",
                "arithmetic": "0x20000000 + align4(0) + align4(13056) + align4(4) = 0x20003304; + align4(9164) = 0x200056d0; + align4(120800) = 0x20022eb0",
            },
            "exact_fit_to_backup_image": f"0x{weight_end:x} == 0x{IMAGE_A_END:x}",
        },
        "evidence": [
            "g2/tools/analyze_g2_codec_stage2_sections.py: binary-verified image and model boundaries",
            "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-npu-staging-review-053/review.json: independent conditional staging tuple review",
            "g2/build/pseudocode-first/20260930T190500Z/attempts/P1-codec-npu-consumer-mapping-061/001/consumer-proposal.json: initializer fields and GRUS layout corroboration",
            "third-party/upstream/nationalchip-lvp-kws/include/driver/gx_snpu.h: pinned SDK GRUS structure reference",
        ],
        "limits": [
            "Staging addresses remain conditional instruction-backed candidates; no live hardware read is claimed.",
            "Commands and weights are not extracted to output files.",
            "No trained-model source pipeline, NPU instruction semantics, C-source completeness, or byte-identical rebuild claim.",
            "LVP/GXDNN component licenses vary; this tool imports no SDK header or model bytes.",
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("codec", nargs="?", type=Path, default=DEFAULT_CODEC)
    ap.add_argument("--command-start", type=lambda x: int(x, 0), default=MODEL_START)
    ap.add_argument("--command-size", type=int, default=GETTERS["cmd"]["size"])
    ap.add_argument("--weight-start", type=lambda x: int(x, 0))
    ap.add_argument("--weight-size", type=int, default=GETTERS["weight"]["size"])
    ap.add_argument("--output", type=Path, help="write metadata JSON (never model bytes)")
    args = ap.parse_args()
    result = verify(args.codec.read_bytes(), command_start=args.command_start,
                    command_size=args.command_size, weight_start=args.weight_start,
                    weight_size=args.weight_size)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
