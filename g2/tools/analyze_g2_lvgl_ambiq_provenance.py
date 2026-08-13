#!/usr/bin/env python3
"""Authenticate the G2 Ambiq-LVGL backend source state and draw-buffer ABI.

This analyzer is read-only.  It verifies the official G2 image, the source
provenance manifest, exact stock function spans, retained source paths, and the
three 32-byte handler tables.  It has no transport, signer, programmer, erase,
or device-write path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-ambiq-source-provenance.json"
LOAD_BASE = 0x0043_7FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"


class AuditError(RuntimeError):
    """Raised when an authenticated input or recovered invariant changes."""


PINNED_SPANS = {
    "lv_draw_buf_init_handlers": (
        0x0048_AA60,
        0x0048_AA80,
        "e4de25b90643cb14e1ae26a01319d6df79db3f7801ea86cfaf8ca3c80bfbf86d",
    ),
    "lv_draw_buf_init_with_default_handlers": (
        0x0048_AA80,
        0x0048_AAA2,
        "bd080c2e2a4958df53ff92255de62a61647fc512302dfcecc29c5966af7e081a",
    ),
    "lv_draw_buf_handlers_init": (
        0x0048_AAA2,
        0x0048_AAD8,
        "14ae3316b82b22eaaa0d1e8d1f7a977758e7d9fed06fa406a28596964abb2f18",
    ),
    "lv_draw_ambiq_init_buf_handlers": (
        0x0053_D5DA,
        0x0053_D65C,
        "5a62de8cc39482ab76a6319fd44451d76696e95efd4b203fdb265b47c4d18ed6",
    ),
    "lv_draw_ambiq_vector_font_event": (
        0x0053_D82C,
        0x0053_D87C,
        "a9124f038ebe1a3d19e7305e324275090955b92bab3ad3e0456544d9eee32530",
    ),
    "lv_draw_ambiq_vector_font_push_pair": (
        0x0053_D87C,
        0x0053_D8FC,
        "a36797308e33bf3b1d6c12f004c114089f5dce4586b0255a8394d97245fd183c",
    ),
    "lv_draw_ambiq_vector_font_outline_push": (
        0x0053_D8FC,
        0x0053_DA50,
        "38d7a87939854fcd94f3a7c910ea9564d2acc0c62afaf1becbaf3192398f5001",
    ),
    "lv_draw_ambiq_vector_font_alloc": (
        0x0053_DA54,
        0x0053_DB3C,
        "9266e6e90684b537f0a7f86a214f7843086d1bea51076930800f78bc67f76154",
    ),
    "lv_draw_ambiq_vector_font_destroy": (
        0x0053_DB3C,
        0x0053_DBD8,
        "9541a18e88c1fd7ac384a8416a7312fcc78562c2b05b7aa6d462c3e6e6f149c5",
    ),
    "lv_draw_ambiq_letter_width_alignment": (
        0x0053_FABA,
        0x0053_FB18,
        "d822f81a9bca227b50bdc5667f22c859074ee02c642c44360a86b3a9f740df60",
    ),
    "lv_draw_ambiq_letter_raw_bitmap": (
        0x0053_FB18,
        0x0053_FCC2,
        "b97199eb1ebc9560c17bd7fcbc1e2655e8ad4e256d591705677448c9475ef12f",
    ),
}

RETAINED_PATHS = {
    0x0053_D66C: (
        0x006D_8CDC,
        r"D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\LVGL\src\draw\ambiq\lv_draw_ambiq_buffer.c",
    ),
    0x0053_DBE0: (
        0x006D_796C,
        r"D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\LVGL\src\draw\ambiq\lv_draw_ambiq_vector_font.c",
    ),
    0x0053_FFF4: (
        0x006D_8D44,
        r"D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\LVGL\src\draw\ambiq\lv_draw_ambiq_letter.c",
    ),
}

HANDLER_LITERAL_TABLE = {
    0x0053_D698: 0x2006_F548,
    0x0053_D69C: 0x0053_D56B,
    0x0053_D6A0: 0x0053_D57B,
    0x0053_D6A4: 0x0053_D587,
    0x0053_D6A8: 0x0053_D595,
    0x0053_D6AC: 0x0053_CFE5,
    0x0053_D6B0: 0x0053_CFF1,
    0x0053_D6B4: 0x0053_D0B7,
    0x0053_D6B8: 0x0053_D25B,
    0x0053_D6BC: 0x0053_D5A3,
    0x0053_D6C0: 0x0053_D5B3,
    0x0053_D6C4: 0x0053_D5BF,
    0x0053_D6C8: 0x0053_D5CD,
}

EXPECTED_SUBTREE = "1e774257495fa43177e04fc5c8a42a77c2d7d619"
EXPECTED_CANONICAL_COMMIT = "5be8e0ae5077aa3880aba8a322b1487d6bc73c07"
EXPECTED_REPLAY_COMMIT = "67fd93e268f86b2ce90d4f1b14b53e36bf49ddd0"
EXPECTED_NEXT_COMMIT = "6770071cb7c4ab97b83669078fe461df812bc79e"
EXPECTED_REPOSITORY = "https://github.com/AmbiqMicro/LVGL.git"
EXPECTED_LICENSE_DIGEST = "c16dcc92ba555c7908be1881efcf7531b76c7cedcd96fd67dfc08cfc02b1e9ff"
EXPECTED_CANDIDATE_DIGEST = "7ac38f743d34e9af187708ca7abc72243bcb6bceec5f993a9fd27dc1cfda72ff"


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _slice(data: bytes, start: int, end: int) -> bytes:
    first = start - LOAD_BASE
    last = end - LOAD_BASE
    if first < 0 or last < first or last > len(data):
        raise AuditError(f"span 0x{start:08X}..0x{end:08X} lies outside image")
    return data[first:last]


def _word(data: bytes, run: int) -> int:
    return struct.unpack("<I", _slice(data, run, run + 4))[0]


def _cstr(data: bytes, run: int, limit: int = 256) -> str:
    raw = _slice(data, run, min(run + limit, LOAD_BASE + len(data)))
    end = raw.find(b"\0")
    if end < 0:
        raise AuditError(f"unterminated string at 0x{run:08X}")
    try:
        return raw[:end].decode("ascii")
    except UnicodeDecodeError as exc:
        raise AuditError(f"non-ASCII string at 0x{run:08X}") from exc


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AuditError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"manifest root is not an object: {path}")
    return value


def audit(data: bytes, manifest: dict[str, Any]) -> dict[str, Any]:
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != IMAGE_SIZE or digest != IMAGE_SHA256:
        raise AuditError("official G2 image identity changed")

    if manifest.get("repository") != EXPECTED_REPOSITORY:
        raise AuditError("Ambiq repository identity changed")
    if _canonical_digest(manifest.get("license")) != EXPECTED_LICENSE_DIGEST:
        raise AuditError("Ambiq license identity changed")
    source = manifest.get("source_state", {})
    if source.get("subtree_git_tree_sha1") != EXPECTED_SUBTREE:
        raise AuditError("Ambiq source subtree identity changed")
    if source.get("canonical_default_branch_commit") != EXPECTED_CANONICAL_COMMIT:
        raise AuditError("canonical Ambiq commit changed")
    if source.get("equivalent_replay_commit") != EXPECTED_REPLAY_COMMIT:
        raise AuditError("equivalent Ambiq replay changed")
    if source.get("immediately_excluded_backend_commit") != EXPECTED_NEXT_COMMIT:
        raise AuditError("immediately excluded Ambiq commit changed")
    files = manifest.get("candidate_files")
    if not isinstance(files, list) or len(files) != 16:
        raise AuditError("Ambiq candidate-file census changed")
    if len({item["path"] for item in files}) != 16:
        raise AuditError("Ambiq candidate paths are not unique")
    if sum(item["size"] for item in files) != 170_833:
        raise AuditError("Ambiq candidate byte census changed")
    if _canonical_digest(files) != EXPECTED_CANDIDATE_DIGEST:
        raise AuditError("Ambiq candidate source identities changed")
    for item in files:
        if not item["path"].startswith("src/draw/ambiq/"):
            raise AuditError(f"candidate escaped Ambiq subtree: {item['path']}")
        if len(item["git_blob_sha1"]) != 40 or len(item["sha256"]) != 64:
            raise AuditError(f"invalid source identity: {item['path']}")

    spans: dict[str, dict[str, Any]] = {}
    for name, (start, end, expected) in PINNED_SPANS.items():
        actual = hashlib.sha256(_slice(data, start, end)).hexdigest()
        if actual != expected:
            raise AuditError(f"stock span changed: {name}")
        spans[name] = {
            "start": start,
            "end_exclusive": end,
            "size": end - start,
            "sha256": actual,
        }

    for run, expected in HANDLER_LITERAL_TABLE.items():
        if _word(data, run) != expected:
            raise AuditError(f"Ambiq handler literal changed at 0x{run:08X}")

    retained: list[dict[str, Any]] = []
    for pointer_cell, (path_run, expected) in RETAINED_PATHS.items():
        if _word(data, pointer_cell) != path_run:
            raise AuditError(f"retained path pointer changed at 0x{pointer_cell:08X}")
        actual = _cstr(data, path_run)
        if actual != expected:
            raise AuditError(f"retained path changed at 0x{path_run:08X}")
        retained.append(
            {"pointer_cell": pointer_cell, "run": path_run, "path": actual}
        )

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no hardware or flash operation",
        "image": {"size": len(data), "sha256": digest},
        "source_recovery": {
            "repository": manifest["repository"],
            "license": manifest["license"],
            "subtree_git_tree_sha1": EXPECTED_SUBTREE,
            "canonical_default_branch_commit": EXPECTED_CANONICAL_COMMIT,
            "equivalent_replay_commit": EXPECTED_REPLAY_COMMIT,
            "immediately_excluded_backend_commit": EXPECTED_NEXT_COMMIT,
            "commit_resolution": (
                "exact Ambiq subtree state; commit object remains two-way ambiguous "
                "because both public commits contain identical subtree bytes"
            ),
            "candidate_file_count": len(files),
            "candidate_bytes": sum(item["size"] for item in files),
        },
        "draw_buffer_abi": {
            "lv_global_base": 0x2006_F548,
            "handler_offsets": [0xC8, 0xE8, 0x108],
            "handler_size": 0x20,
            "callback_offsets": {
                "buf_malloc_cb": 0x00,
                "buf_free_cb": 0x04,
                "align_pointer_cb": 0x08,
                "invalidate_cache_cb": 0x0C,
                "flush_cache_cb": 0x10,
                "width_to_stride_cb": 0x14,
                "clear_cb": 0x18,
                "copy_cb": 0x1C,
            },
            "generic_hook_origin_commit": manifest["patch_history"]["generic_clear_copy_hook_commit"],
            "ambiq_wiring_origin_commit": manifest["patch_history"]["ambiq_buffer_wiring_commit"],
        },
        "retained_paths": retained,
        "pinned_spans": spans,
        "source_line_fingerprints": manifest["stock_evidence"]["retained_source_line_fingerprints"],
        "integration_status": manifest["integration_status"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        data = args.image.read_bytes()
        report = audit(data, _load_json(args.manifest))
    except (OSError, AuditError) as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        source = report["source_recovery"]
        abi = report["draw_buffer_abi"]
        print("G2 Ambiq-LVGL source/ABI audit: PASS")
        print(f"subtree: {source['subtree_git_tree_sha1']}")
        print(f"canonical commit: {source['canonical_default_branch_commit']}")
        print(f"equivalent replay: {source['equivalent_replay_commit']}")
        print(
            "draw handlers: %d bytes at lv_global+%s"
            % (abi["handler_size"], ",+".join(f"0x{x:X}" for x in abi["handler_offsets"]))
        )
        print("hardware/flash operations: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
