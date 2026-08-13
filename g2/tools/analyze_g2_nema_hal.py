#!/usr/bin/env python3
"""Authenticate the stock G2 bare-metal Nema HAL and its public source lineage."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
GPU_BASE = 0x40090000
VECTOR_WORD = 0x004380B0
VECTOR_VALUE = 0x00513F93
PUBLIC_PATH = "components/graphics/NemaGFX_SDK/port/nema_hal.c"
EARLY_COMMIT = "4e7d42766d5af90810c9cea5d774970c17d5ac14"
EARLY_BLOB = "79acb73ca23bae39193a84fa7a0091ed92e45b23"
EARLY_SHA256 = "4174286156d3bfa8f59e70784e2c425cc1af189b2d69c433c263f2c038bd6eb9"
EARLY_BYTES = 18_611
PACKAGE_COMMIT = "b853fded7e545f005727e13bf2ce83018c7e242d"
PACKAGE_BLOB = "3db4d884dce154c3f4107688d8992184e67b88d5"
PACKAGE_SHA256 = "053044dd8db3a84e57ff1c55200fdfefaef3e463361ea8de3fc238c40ed51cac"
PACKAGE_BYTES = 17_527

# name, start, end, sha256, direct BL ingress count
FUNCTIONS = (
    ("prvNemaInterruptHandler", 0x00513F34, 0x00513F92, "aba6161a7478242e1c6be27146ddb2d1c8daf540e6eeaa69320f4c90faa43322", 1),
    ("GPU_IRQHandler", 0x00513F92, 0x00513F9C, "3c424a27cb1802368c429e8ec8beef1dfa4fb04b9295a391c9778d3bd77e7830", 0),
    ("nema_sys_init", 0x00513F9C, 0x0051400A, "9e014098c460b5a94ff0cf388e5d01ce9462eb27b537798a46f5dc0be251bcfd", 1),
    ("nema_wait_irq", 0x0051400A, 0x00514026, "93164ca586cda9f31b49cbf2843378fba2f9e3754efc072b5f7d0e45e3f7ae5d", 1),
    ("nema_wait_irq_cl", 0x00514026, 0x0051403C, "344748628799dab6f8e829e5e4c4dfbc11fddc90ba4915639fb641fcdb08b926", 3),
    ("nema_reg_read", 0x0051403C, 0x00514046, "b8b1d0b5fd8ddfdf6b7a25e837081525e37abb38816818d10abe7f4e9c4a3c7d", 8),
    ("nema_reg_write", 0x00514046, 0x00514050, "3f5806279dfe7d2cc5b1720fa010b07c2959e7199f7616a9ab88f36d034aa36d", 21),
    ("select_heap", 0x00514050, 0x00514070, "9ea14c05d38180b70a4375535ad95003861ad83728c38133641b5ed3964a26e3", 5),
    ("nema_buffer_create_pool", 0x00514070, 0x005140C6, "d9beae1fc551852d210f2cb11e3bd58e873e219da4092e9dd74f3184b0a99dd4", 7),
    ("nema_buffer_destroy", 0x005140C6, 0x005140EA, "25943f5db229374561bcd467ef4197506947aa1cf067fd1de3eb9086e163c595", 2),
    ("nema_buffer_flush", 0x005140EA, 0x0051411A, "9b4d4ca619be8f645ff6b7343b323a9d933311895176c7e8a437040947096a7a", 13),
    ("nema_buffer_invalidate", 0x0051411A, 0x00514148, "7899709976ddd9c5dff28a3f0d312b79d6bea138a2fdcf85af83b2d1c737e260", 1),
    ("nema_buffer_is_within_pool", 0x00514148, 0x0051416C, "aa2873c2e579c1e1ff6d0914451629553552d54175ca2f0ee8b64853901eda07", 3),
    ("nema_host_malloc", 0x0051416C, 0x00514178, "888b1d4507fb20a1b9d9d9a3bb7dc8b40c330c690bd0df172e4367219dc2aa77", 7),
    ("nema_host_free", 0x00514178, 0x00514184, "6bc561ef9feaf8c8f327bb904b93da1a391b244ea3321319207f26b0c1b786c4", 7),
    ("nema_reset_last_cl_id", 0x00514184, 0x0051418E, "f3c08e85a950089b3e9d12343e1da22d0c37379321a4eb31e4f34d4abd485500", 1),
    ("nema_get_last_cl_id", 0x0051418E, 0x00514194, "d3e8c911f7f7e0d2eb62ee4748a793dabd6bde1a3454660995b42cb6f90f5340", 1),
    ("nema_get_last_submission_id", 0x00514194, 0x0051419A, "a51abe05402e6b85d6e6a095137c24e4ba804005bb8c4d14dd92e7acd8ea0fbb", 1),
)


class AuditError(RuntimeError):
    pass


def _thumb_bl_target(blob: bytes, address: int) -> int | None:
    offset = address - BASE
    first, second = struct.unpack_from("<HH", blob, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    j1, j2 = (second >> 13) & 1, (second >> 11) & 1
    i1, i2 = int(not (j1 ^ sign)), int(not (j2 ^ sign))
    value = (sign << 24) | (i1 << 23) | (i2 << 22) | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1)
    if value & (1 << 24):
        value -= 1 << 25
    return address + 4 + value


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE:end - BASE]


def _word(blob: bytes, address: int) -> int:
    return int.from_bytes(_slice(blob, address, address + 4), "little")


def _git(repo: Path, *args: str) -> bytes:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args], check=True, capture_output=True
        ).stdout
    except subprocess.CalledProcessError as exc:
        raise AuditError(exc.stderr.decode(errors="replace").strip()) from exc


def verify_history(repo: Path) -> dict[str, object]:
    rows = []
    for commit, expected_blob, expected_sha, expected_size in (
        (EARLY_COMMIT, EARLY_BLOB, EARLY_SHA256, EARLY_BYTES),
        (PACKAGE_COMMIT, PACKAGE_BLOB, PACKAGE_SHA256, PACKAGE_BYTES),
    ):
        actual_blob = _git(repo, "rev-parse", f"{commit}:{PUBLIC_PATH}").decode().strip()
        body = _git(repo, "show", f"{commit}:{PUBLIC_PATH}")
        if actual_blob != expected_blob or len(body) != expected_size or hashlib.sha256(body).hexdigest() != expected_sha:
            raise AuditError(f"public Nema HAL identity changed at {commit}")
        rows.append({"commit": commit, "git_blob_sha1": actual_blob, "bytes": len(body), "sha256": expected_sha})
    if subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", EARLY_COMMIT, PACKAGE_COMMIT]
    ).returncode != 0:
        raise AuditError("early public HAL commit is not on the package lineage")
    return {"verified": True, "files": rows}


def analyze(image: Path = IMAGE, history_repo: Path | None = None) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or hashlib.sha256(blob).hexdigest() != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    targets = {start for _, start, _, _, _ in FUNCTIONS}
    calls = {target: [] for target in targets}
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = _thumb_bl_target(blob, address)
        if target in calls:
            calls[target].append(address)
    census = []
    for name, start, end, expected_sha, expected_calls in FUNCTIONS:
        body = _slice(blob, start, end)
        actual_sha = hashlib.sha256(body).hexdigest()
        if actual_sha != expected_sha or len(calls[start]) != expected_calls:
            raise AuditError(f"stock Nema HAL function changed: {name}")
        census.append({
            "function": name, "start": start, "end_exclusive": end,
            "bytes": len(body), "sha256": actual_sha,
            "direct_bl_callers": calls[start],
        })
    cluster = _slice(blob, FUNCTIONS[0][1], FUNCTIONS[-1][2])
    if len(cluster) != 614 or hashlib.sha256(cluster).hexdigest() != "e669f4c7a13b2f2b15621c714cdfd42748ca8b1609f0d1013f453991c6ca88ce":
        raise AuditError("complete stock Nema HAL cluster changed")
    if _word(blob, VECTOR_WORD) != VECTOR_VALUE or _word(blob, 0x00514264) != 0x0078F2F4 or _word(blob, 0x0078F2F4) != GPU_BASE:
        raise AuditError("GPU vector/register-base identity changed")
    report: dict[str, object] = {
        "schema_version": 1,
        "stock": {
            "start": FUNCTIONS[0][1], "end_exclusive": FUNCTIONS[-1][2],
            "bytes": len(cluster), "sha256": hashlib.sha256(cluster).hexdigest(),
            "functions": census, "function_count": len(census),
            "direct_bl_call_sites": sum(len(row["direct_bl_callers"]) for row in census),
            "gpu_base": GPU_BASE, "irq": 28, "ring_bytes": 0x1300,
            "max_pending_command_lists": 100,
            "heap_descriptors": [0x20000354, 0x20000370, 0x20000338],
        },
        "public_lineage": {
            "repository": "https://github.com/AmbiqMicro/ambiqhal_ambiq.git",
            "early_bare_register_zephyr_port": {
                "commit": EARLY_COMMIT, "git_blob_sha1": EARLY_BLOB,
                "sha256": EARLY_SHA256, "bytes": EARLY_BYTES,
            },
            "exact_package_zephyr_driver_port": {
                "commit": PACKAGE_COMMIT, "git_blob_sha1": PACKAGE_BLOB,
                "sha256": PACKAGE_SHA256, "bytes": PACKAGE_BYTES,
            },
            "stock_generating_source": None,
            "qualification": "The public files establish Ambiq API ancestry but both are Zephyr ports; G2 uses CMSIS-FreeRTOS, three project heap descriptors, and a direct IRQ-28 vector.",
        },
        "candidate_source": "components/shared/lvgl/runtime_ambiq_nema_hal_candidate.c",
        "production_status": "excluded-pending-atomic-integration-and-hardware-validation",
    }
    if history_repo is not None:
        report["history_verification"] = verify_history(history_repo)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--history-repo", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image, args.history_repo)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        stock = report["stock"]
        print(f"G2 Nema bare-metal HAL audit: PASS ({stock['function_count']} functions / {stock['bytes']} bytes)")
        print("public port ancestry: 4e7d4276 -> b853fded; stock source remains private")
        print("hardware/flash operations: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
