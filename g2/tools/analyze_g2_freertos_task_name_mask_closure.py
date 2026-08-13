#!/usr/bin/env python3
"""Audit the production closure for pcTaskGetName and the BASEPRI leaves.

This tool is deliberately read-only.  It authenticates the official G2
2.2.6.10 Apollo-main image, verifies the three complete source-identifiable
FreeRTOS entry ranges, scans their complete recoverable caller/reference
topology, and states the smallest safe source-promotion unit.  It has no
device, serial, debugger, signing, or flash-programming path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

import analyze_g2_freertos_assert_port_seam as port_seam


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = port_seam.DEFAULT_IMAGE
PACKAGE_SIZE = port_seam.PACKAGE_SIZE
PACKAGE_SHA256 = port_seam.PACKAGE_SHA256
PACKAGE_PREAMBLE_SIZE = port_seam.PACKAGE_PREAMBLE_SIZE
APPLICATION_BASE = port_seam.APPLICATION_BASE
APPLICATION_SHA256 = port_seam.APPLICATION_SHA256

TASK_CANDIDATE = (
    ROOT / "research" / "candidates" / "freertos_pc_task_get_name.c"
)
MASK_CANDIDATE = (
    ROOT / "research" / "candidates" / "freertos_interrupt_mask_pair.S"
)
TASK_CANDIDATE_SHA256 = (
    "cd80886bfec8eb99df0a07ca721685f3"
    "87a44c079c1da8139fa944e99ff8a278"
)
MASK_CANDIDATE_SHA256 = (
    "710a2b348df985a981a5c1f6829a849e"
    "1c3635b599549c7847df7151370ed2a6"
)

TASK_START = 0x0045_4F16
TASK_END = 0x0045_4F38
TASK_BYTES = bytes.fromhex(
    "80b5002802d1a1480068ffe7002806d1"
    "a5f1bdf800205ff0ff310860fee7343002bd"
)
TASK_SHA256 = (
    "a25ace28ece3ca37f11da7e73945acb2"
    "8f1f99d906203613e9856d2070c07817"
)
TASK_CALLERS = (0x0044_AAEE,)
TASK_CALLSITE_SHA256 = (
    "6b6b656546449e21e970d725927d278f"
    "881d1c0bf448fd732bf3759f73366ee4"
)
TASK_RAW_WINDOW = (0x004A_56B7, 0x0045_4F20)
TASK_RAW_CONTEXT_START = 0x004A_56B0
TASK_RAW_CONTEXT = bytes.fromhex("4c4500204e4500204f450020")

SET_START = 0x005F_A0A4
SET_END = 0x005F_A0BA
SET_BYTES = port_seam.FUNCTION_BYTES
SET_SHA256 = port_seam.FUNCTION_SHA256
SET_CALLSITE_COUNT = port_seam.CALLSITE_COUNT
SET_CALLSITE_SHA256 = port_seam.CALLSITE_SHA256

CLEAR_START = SET_END
CLEAR_END = 0x005F_A0C8
CLEAR_BYTES = port_seam.SUCCESSOR_BYTES
CLEAR_SHA256 = port_seam.SUCCESSOR_SHA256
CLEAR_CALLERS = (
    0x0043_C9F2,
    0x0044_1A38,
    0x0044_1B02,
    0x0044_1E5C,
    0x0044_210E,
    0x0044_212E,
    0x0044_9D96,
    0x0044_9E3C,
    0x0045_5F54,
    0x0045_6420,
    0x0047_ED6E,
    0x0057_E0E6,
)
CLEAR_CALLSITE_SHA256 = (
    "5047082ba3888cae8330f9276620611cd"
    "f412c86fee71d1cd0ffc97447fd2746"
)
CLEAR_RAW_WINDOW = (0x0062_FCDF, CLEAR_START)
CLEAR_RAW_CONTEXT_START = 0x0062_FCD8
CLEAR_RAW_CONTEXT = bytes.fromhex(
    "e6db03802f301dbaa05f0001df401fb4"
)
CLEAR_ALIGNED_WORDS = (
    (0x0062_FCDC, 0xBA1D_302F),
    (0x0062_FCE0, 0x0100_5FA0),
)

CURRENT_TCB_WORD = 0x2007_4A20
TASK_ASSERT_CALL = 0x0045_4F26


class AuditError(RuntimeError):
    """Raised when an authenticated input or recovered invariant drifts."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(application: bytes, start: int, end: int) -> bytes:
    first = start - APPLICATION_BASE
    last = end - APPLICATION_BASE
    if first < 0 or first >= last or last > len(application):
        raise AuditError(
            f"span [0x{start:08X},0x{end:08X}) is outside the application"
        )
    return application[first:last]


def _span_for_target(target: int) -> tuple[str, int, int] | None:
    for name, start, end in (
        ("pcTaskGetName", TASK_START, TASK_END),
        ("ulSetInterruptMask", SET_START, SET_END),
        ("vClearInterruptMask", CLEAR_START, CLEAR_END),
    ):
        if start <= target < end:
            return name, start, end
    return None


def scan_topology(application: bytes) -> dict[str, dict[str, Any]]:
    topology: dict[str, dict[str, Any]] = {}
    for name in (
        "pcTaskGetName",
        "ulSetInterruptMask",
        "vClearInterruptMask",
    ):
        topology[name] = {
            "direct_bl": [],
            "direct_bw": [],
            "external_interior_wide": [],
            "external_entry_or_interior_narrow": [],
            "raw_entry_or_interior_windows": [],
            "naturally_aligned_entry_or_interior_words": [],
        }

    for offset in range(0, len(application) - 3, 2):
        address = APPLICATION_BASE + offset
        first, second = struct.unpack_from("<HH", application, offset)
        encoding = application[offset : offset + 4].hex()
        for link, kind in ((True, "direct_bl"), (False, "direct_bw")):
            target = port_seam.thumb_wide_branch_target(
                address,
                first,
                second,
                link=link,
            )
            if target is None:
                continue
            selected = _span_for_target(target)
            if selected is None:
                continue
            name, start, end = selected
            if target == start:
                topology[name][kind].append(
                    {
                        "address": address,
                        "target": target,
                        "encoding": encoding,
                    }
                )
            elif not start <= address < end:
                topology[name]["external_interior_wide"].append(
                    {
                        "address": address,
                        "target": target,
                        "encoding": encoding,
                        "kind": "BL" if link else "B.W",
                    }
                )

    for offset in range(0, len(application) - 1, 2):
        address = APPLICATION_BASE + offset
        halfword = struct.unpack_from("<H", application, offset)[0]
        for target in port_seam.narrow_branch_targets(address, halfword):
            selected = _span_for_target(target)
            if selected is None:
                continue
            name, start, end = selected
            if not start <= address < end:
                topology[name][
                    "external_entry_or_interior_narrow"
                ].append(
                    {
                        "address": address,
                        "target": target,
                        "encoding": f"{halfword:04x}",
                    }
                )

    for offset in range(0, len(application) - 3):
        address = APPLICATION_BASE + offset
        value = struct.unpack_from("<I", application, offset)[0]
        canonical = value & ~1
        selected = _span_for_target(canonical)
        if selected is None:
            continue
        name, _, _ = selected
        item = {
            "address": address,
            "value": value,
            "canonical": canonical,
        }
        topology[name]["raw_entry_or_interior_windows"].append(item)
        if address % 4 == 0:
            topology[name][
                "naturally_aligned_entry_or_interior_words"
            ].append(item)

    return topology


def _callsite_digest(items: list[dict[str, int | str]]) -> str:
    return sha256(
        b"".join(
            struct.pack("<I", int(item["address"]))
            for item in items
        )
    )


def _verify_empty_branch_topology(
    topology: dict[str, dict[str, Any]],
) -> None:
    for name, references in topology.items():
        for key in (
            "direct_bw",
            "external_interior_wide",
            "external_entry_or_interior_narrow",
        ):
            if references[key]:
                raise AuditError(f"unexpected {name} references in {key}")


def _verify_candidate_sources() -> dict[str, Any]:
    task = TASK_CANDIDATE.read_bytes()
    mask = MASK_CANDIDATE.read_bytes()
    if sha256(task) != TASK_CANDIDATE_SHA256:
        raise AuditError("pcTaskGetName candidate SHA-256 drift")
    if sha256(mask) != MASK_CANDIDATE_SHA256:
        raise AuditError("interrupt-mask candidate SHA-256 drift")

    task_text = task.decode("utf-8")
    for fragment in (
        "FreeRTOS Kernel V10.5.1",
        "SPDX-License-Identifier: MIT",
        "ulSetInterruptMask",
        "0x20074A20U",
        "task_name) == 0x34",
    ):
        if fragment not in task_text:
            raise AuditError(
                f"pcTaskGetName candidate is missing {fragment!r}"
            )

    mask_text = mask.decode("utf-8")
    for fragment in (
        "SPDX-License-Identifier: MIT",
        "ulSetInterruptMask:",
        "vClearInterruptMask:",
        "mov.w   r1, #0x30",
        "msr     basepri, r0",
    ):
        if fragment not in mask_text:
            raise AuditError(
                f"interrupt-mask candidate is missing {fragment!r}"
            )

    return {
        "pcTaskGetName": {
            "path": str(TASK_CANDIDATE.relative_to(ROOT)),
            "sha256": TASK_CANDIDATE_SHA256,
            "unresolved_production_seam": "ulSetInterruptMask",
        },
        "interrupt_mask_pair": {
            "path": str(MASK_CANDIDATE.relative_to(ROOT)),
            "sha256": MASK_CANDIDATE_SHA256,
            "text_is_exact_stock_pair": True,
            "private_dependencies": [],
        },
    }


def run_audit(image_path: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    package = image_path.read_bytes()
    if len(package) != PACKAGE_SIZE:
        raise AuditError(
            f"official package size drift: {len(package)} != {PACKAGE_SIZE}"
        )
    if sha256(package) != PACKAGE_SHA256:
        raise AuditError("official package SHA-256 drift")
    application = package[PACKAGE_PREAMBLE_SIZE:]
    if sha256(application) != APPLICATION_SHA256:
        raise AuditError("installed application SHA-256 drift")

    for name, start, end, expected, digest in (
        (
            "pcTaskGetName",
            TASK_START,
            TASK_END,
            TASK_BYTES,
            TASK_SHA256,
        ),
        (
            "ulSetInterruptMask",
            SET_START,
            SET_END,
            SET_BYTES,
            SET_SHA256,
        ),
        (
            "vClearInterruptMask",
            CLEAR_START,
            CLEAR_END,
            CLEAR_BYTES,
            CLEAR_SHA256,
        ),
    ):
        body = image_slice(application, start, end)
        if body != expected or sha256(body) != digest:
            raise AuditError(f"{name} body drift")

    assert_offset = TASK_ASSERT_CALL - APPLICATION_BASE
    assert_target = port_seam.thumb_wide_branch_target(
        TASK_ASSERT_CALL,
        *struct.unpack_from("<HH", application, assert_offset),
        link=True,
    )
    if assert_target != SET_START:
        raise AuditError("pcTaskGetName assertion dependency drift")

    topology = scan_topology(application)
    _verify_empty_branch_topology(topology)

    task_calls = topology["pcTaskGetName"]["direct_bl"]
    set_calls = topology["ulSetInterruptMask"]["direct_bl"]
    clear_calls = topology["vClearInterruptMask"]["direct_bl"]
    if tuple(int(item["address"]) for item in task_calls) != TASK_CALLERS:
        raise AuditError("pcTaskGetName caller topology drift")
    if _callsite_digest(task_calls) != TASK_CALLSITE_SHA256:
        raise AuditError("pcTaskGetName caller digest drift")
    if (
        len(set_calls) != SET_CALLSITE_COUNT
        or _callsite_digest(set_calls) != SET_CALLSITE_SHA256
    ):
        raise AuditError("ulSetInterruptMask caller topology drift")
    if tuple(int(item["address"]) for item in clear_calls) != CLEAR_CALLERS:
        raise AuditError("vClearInterruptMask caller topology drift")
    if _callsite_digest(clear_calls) != CLEAR_CALLSITE_SHA256:
        raise AuditError("vClearInterruptMask caller digest drift")

    task_raw = topology["pcTaskGetName"]["raw_entry_or_interior_windows"]
    clear_raw = topology[
        "vClearInterruptMask"
    ]["raw_entry_or_interior_windows"]
    if [
        (int(item["address"]), int(item["canonical"]))
        for item in task_raw
    ] != [TASK_RAW_WINDOW]:
        raise AuditError("pcTaskGetName raw-window classification drift")
    if topology[
        "ulSetInterruptMask"
    ]["raw_entry_or_interior_windows"]:
        raise AuditError("unexpected ulSetInterruptMask raw address window")
    if [
        (int(item["address"]), int(item["canonical"]))
        for item in clear_raw
    ] != [CLEAR_RAW_WINDOW]:
        raise AuditError("vClearInterruptMask raw-window classification drift")
    for name in topology:
        if topology[name]["naturally_aligned_entry_or_interior_words"]:
            raise AuditError(
                f"unexpected naturally aligned {name} stored address"
            )

    task_context = image_slice(
        application,
        TASK_RAW_CONTEXT_START,
        TASK_RAW_CONTEXT_START + len(TASK_RAW_CONTEXT),
    )
    if task_context != TASK_RAW_CONTEXT:
        raise AuditError("pcTaskGetName raw-window context drift")
    clear_context = image_slice(
        application,
        CLEAR_RAW_CONTEXT_START,
        CLEAR_RAW_CONTEXT_START + len(CLEAR_RAW_CONTEXT),
    )
    if clear_context != CLEAR_RAW_CONTEXT:
        raise AuditError("vClearInterruptMask raw-window context drift")
    for address, expected in CLEAR_ALIGNED_WORDS:
        observed = struct.unpack(
            "<I",
            image_slice(application, address, address + 4),
        )[0]
        if observed != expected:
            raise AuditError(
                "vClearInterruptMask aligned-word context drift"
            )

    candidates = _verify_candidate_sources()
    return {
        "status": "ok",
        "read_only": True,
        "image": {
            "path": str(image_path),
            "package_sha256": PACKAGE_SHA256,
            "application_sha256": APPLICATION_SHA256,
            "load_address": APPLICATION_BASE,
        },
        "functions": {
            "pcTaskGetName": {
                "start": TASK_START,
                "end_exclusive": TASK_END,
                "size": len(TASK_BYTES),
                "sha256": TASK_SHA256,
                "outgoing_call": {
                    "site": TASK_ASSERT_CALL,
                    "target": SET_START,
                    "role": "fatal configASSERT path; saved mask discarded",
                },
                "fixed_data_seam": {
                    "name": "pxCurrentTCB",
                    "address": CURRENT_TCB_WORD,
                },
            },
            "ulSetInterruptMask": {
                "start": SET_START,
                "end_exclusive": SET_END,
                "size": len(SET_BYTES),
                "sha256": SET_SHA256,
                "return": "previous BASEPRI in r0",
                "side_effect": "BASEPRI=0x30, DSB, ISB",
            },
            "vClearInterruptMask": {
                "start": CLEAR_START,
                "end_exclusive": CLEAR_END,
                "size": len(CLEAR_BYTES),
                "sha256": CLEAR_SHA256,
                "argument": "saved BASEPRI in r0",
                "side_effect": "restore BASEPRI, DSB, ISB",
            },
        },
        "references": {
            name: {
                **references,
                "direct_bl_count": len(references["direct_bl"]),
                "direct_bl_callsite_sha256": _callsite_digest(
                    references["direct_bl"]
                ),
            }
            for name, references in topology.items()
        },
        "raw_window_classification": {
            "vClearInterruptMask": {
                "address": CLEAR_RAW_WINDOW[0],
                "apparent_value": CLEAR_RAW_WINDOW[1],
                "address_mod_4": CLEAR_RAW_WINDOW[0] % 4,
                "address_mod_2": CLEAR_RAW_WINDOW[0] % 2,
                "context_start": CLEAR_RAW_CONTEXT_START,
                "context_hex": CLEAR_RAW_CONTEXT.hex(),
                "aligned_words": [
                    {"address": address, "value": value}
                    for address, value in CLEAR_ALIGNED_WORDS
                ],
                "classification": (
                    "false positive: byte-sliding window across two "
                    "naturally aligned non-pointer data words"
                ),
                "basis": [
                    "the apparent word starts at address mod 4 = 3",
                    (
                        "it is assembled from the last byte of 0xBA1D302F "
                        "and the first three bytes of 0x01005FA0"
                    ),
                    (
                        "there is no naturally aligned stored entry or "
                        "interior address"
                    ),
                    (
                        "there is no direct wide or narrow branch into any "
                        "mask-leaf interior"
                    ),
                ],
            },
        },
        "candidates": candidates,
        "production_readiness": {
            "smallest_safe_atomic_promotion": [
                "pcTaskGetName",
                "ulSetInterruptMask",
            ],
            "vClearInterruptMask_required_in_same_increment": False,
            "reason": (
                "pcTaskGetName only calls ulSetInterruptMask on its fatal "
                "assertion path and discards the saved mask; it never calls "
                "vClearInterruptMask"
            ),
            "exact_redirects": [
                {
                    "stock_span": [TASK_START, TASK_END],
                    "target": "open_cfw_freertos_pc_task_get_name",
                    "preserve_existing_callers": list(TASK_CALLERS),
                },
                {
                    "stock_span": [SET_START, SET_END],
                    "target": "source-owned ulSetInterruptMask",
                    "preserve_existing_callers": [
                        int(item["address"]) for item in set_calls
                    ],
                },
            ],
            "address_preservation_constraints": [
                (
                    "do not patch at or beyond 0x005FA0BA; all 12 direct "
                    "vClearInterruptMask calls must continue to resolve to "
                    "that exact even entry"
                ),
                (
                    "bind the source pcTaskGetName assertion relocation to "
                    "the source-owned ulSetInterruptMask, not an unresolved "
                    "or shifted entry"
                ),
                (
                    "retain pxCurrentTCB at fixed word 0x20074A20 until "
                    "kernel globals migrate atomically"
                ),
            ],
            "optional_broader_increment": [
                "pcTaskGetName",
                "ulSetInterruptMask",
                "vClearInterruptMask",
            ],
            "optional_broader_redirect": {
                "stock_span": [SET_START, CLEAR_END],
                "entry_offsets": {
                    "ulSetInterruptMask": 0,
                    "vClearInterruptMask": CLEAR_START - SET_START,
                },
                "requirement": (
                    "both public entries must remain independently callable "
                    "at 0x005FA0A4 and 0x005FA0BA"
                ),
            },
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "image",
        nargs="?",
        type=Path,
        default=DEFAULT_IMAGE,
        help="official ota_s200_firmware_ota.bin package",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the complete machine-readable audit",
    )
    args = parser.parse_args()
    result = run_audit(args.image)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        references = result["references"]
        print(f"PASS package: {args.image}")
        print(
            "PASS entries: pcTaskGetName 34 B; "
            "ulSetInterruptMask 22 B; vClearInterruptMask 14 B"
        )
        print(
            "PASS callers: "
            f"{references['pcTaskGetName']['direct_bl_count']} / "
            f"{references['ulSetInterruptMask']['direct_bl_count']} / "
            f"{references['vClearInterruptMask']['direct_bl_count']} direct BL"
        )
        print(
            "PASS raw window: 0x0062FCDF is an unaligned "
            "two-word byte-overlap false positive"
        )
        print(
            "PASS production closure: pcTaskGetName + ulSetInterruptMask; "
            "preserve vClearInterruptMask at 0x005FA0BA"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, OSError, ValueError) as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
