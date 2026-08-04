#!/usr/bin/env python3
"""Audit the G2 FreeRTOS BASEPRI assertion/interrupt-mask seam.

This tool is deliberately read-only.  It authenticates the official
2.2.6.10 Apollo-main image and the pinned FreeRTOS-Kernel V10.5.1 source,
then checks the exact ulSetInterruptMask body, neighboring boundaries, direct
call topology, and absence of stored or interior references.  It has no
device, serial, debugger, signing, or flash-programming path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
UPSTREAM_PORTASM = (
    ROOT
    / "third_party"
    / "freertos-kernel"
    / "portable"
    / "IAR"
    / "ARM_CM55_NTZ"
    / "non_secure"
    / "portasm.s"
)

PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863"
)
PACKAGE_PREAMBLE_SIZE = 32
APPLICATION_BASE = 0x0043_8000
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)

FUNCTION_START = 0x005F_A0A4
FUNCTION_END = 0x005F_A0BA
FUNCTION_BYTES = bytes.fromhex(
    "eff31180"  # mrs r0, basepri
    "4ff03001"  # mov.w r1, #0x30
    "81f31188"  # msr basepri, r1
    "bff34f8f"  # dsb sy
    "bff36f8f"  # isb sy
    "7047"      # bx lr
)
FUNCTION_SHA256 = (
    "f6bd0708e653c8e8880e33e298f9dc8"
    "ede1305c9386ea4ca5ff554d4022dc323"
)

PREDECESSOR_START = 0x005F_A08C
PREDECESSOR_BYTES = bytes.fromhex(
    "2a480068006880f3088862b661b6bff34f8fbff36f8f02df"
)
PREDECESSOR_SHA256 = (
    "44ba0097fbbc1d0691837d5c51bee83e"
    "6b61509c9d89efffee9c202d930e6347"
)
SUCCESSOR_END = 0x005F_A0C8
SUCCESSOR_BYTES = bytes.fromhex(
    "80f31188bff34f8fbff36f8f7047"
)
SUCCESSOR_SHA256 = (
    "97532a7902b38e1551198dd647d0fcdc"
    "3a6f19315b6491058a813c7643e0028a"
)

UPSTREAM_COMMIT = "def7d2df2b0506d3d249334974f51e427c17a41c"
UPSTREAM_TREE = "7496dfa815c3cea2f45a090c6e92d113f494b930"
UPSTREAM_PORTASM_SHA256 = (
    "eaa83b3867edec5560c69f2a21facd7a"
    "ff3c0f3bfcdfc5751722375ae328ee8f"
)
UPSTREAM_PORTASM_GIT_BLOB = "4d02a431e1d759f12f50e70fc55a7b0b4d368e89"

CALLSITE_COUNT = 181
CALLSITE_SHA256 = (
    "f0187e62c4c399694d4fdd8e64a2e238"
    "724f6fb0ec89a6520c3020156eb9c106"
)
CALLSITE_PAGE_COUNTS = {
    0x0043_C000: 2,
    0x0044_1000: 37,
    0x0044_2000: 6,
    0x0044_4000: 5,
    0x0044_9000: 2,
    0x0045_4000: 14,
    0x0045_5000: 31,
    0x0045_6000: 5,
    0x0045_E000: 1,
    0x0046_4000: 2,
    0x0046_5000: 7,
    0x0046_D000: 1,
    0x0047_5000: 2,
    0x0047_E000: 20,
    0x0048_E000: 4,
    0x0049_1000: 2,
    0x004C_4000: 2,
    0x004C_9000: 3,
    0x004D_0000: 2,
    0x004E_1000: 3,
    0x0052_A000: 2,
    0x0053_8000: 3,
    0x0054_1000: 1,
    0x0057_D000: 8,
    0x0057_E000: 14,
    0x0058_4000: 2,
}
REPRESENTATIVE_CALLS = {
    0x0044_15D4: "queue create assertion",
    0x0044_208C: "portable-layer assertion",
    0x0045_4F26: "pcTaskGetName assertion",
    0x0045_61A2: "heap_4 assertion",
    0x0047_E6C8: "timer service assertion",
    0x0058_47D0: "late application assertion",
}


class AuditError(RuntimeError):
    """Raised when an authenticated input or recovered invariant drifts."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    prefix = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def image_slice(application: bytes, start: int, end: int) -> bytes:
    first = start - APPLICATION_BASE
    last = end - APPLICATION_BASE
    if first < 0 or first >= last or last > len(application):
        raise AuditError(
            f"span [0x{start:08X},0x{end:08X}) is outside the application"
        )
    return application[first:last]


def thumb_wide_branch_target(
    address: int,
    first: int,
    second: int,
    *,
    link: bool,
) -> int | None:
    """Decode a Thumb-2 BL or unconditional B.W immediate target."""

    expected_second = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected_second:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    imm11 = second & 0x07FF
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | (imm11 << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    """Return targets for narrow B/Bcc/CBZ/CBNZ encodings."""

    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if (
        halfword & 0xF000 == 0xD000
        and ((halfword >> 8) & 0x0F) < 0x0E
    ):
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (
            (((halfword >> 9) & 1) << 5)
            | ((halfword >> 3) & 0x1F)
        )
        return (address + 4 + immediate * 2,)
    return ()


def scan_branches(application: bytes) -> dict[str, list[dict[str, int | str]]]:
    calls: list[dict[str, int | str]] = []
    jumps: list[dict[str, int | str]] = []
    interior: list[dict[str, int | str]] = []
    narrow: list[dict[str, int | str]] = []

    for offset in range(0, len(application) - 3, 2):
        address = APPLICATION_BASE + offset
        first, second = struct.unpack_from("<HH", application, offset)
        encoded = application[offset : offset + 4].hex()
        for link, collection, kind in (
            (True, calls, "BL"),
            (False, jumps, "B.W"),
        ):
            target = thumb_wide_branch_target(
                address,
                first,
                second,
                link=link,
            )
            if target is None:
                continue
            if target == FUNCTION_START:
                collection.append(
                    {"address": address, "target": target, "encoding": encoded}
                )
            if (
                FUNCTION_START < target < FUNCTION_END
                and not FUNCTION_START <= address < FUNCTION_END
            ):
                interior.append(
                    {
                        "address": address,
                        "target": target,
                        "encoding": encoded,
                        "kind": kind,
                    }
                )

    for offset in range(0, len(application) - 1, 2):
        address = APPLICATION_BASE + offset
        halfword = struct.unpack_from("<H", application, offset)[0]
        for target in narrow_branch_targets(address, halfword):
            if (
                FUNCTION_START <= target < FUNCTION_END
                and not FUNCTION_START <= address < FUNCTION_END
            ):
                narrow.append(
                    {
                        "address": address,
                        "target": target,
                        "encoding": f"{halfword:04x}",
                    }
                )

    return {
        "direct_bl": calls,
        "direct_bw": jumps,
        "external_interior_wide": interior,
        "external_entry_or_interior_narrow": narrow,
    }


def scan_stored_references(application: bytes) -> list[dict[str, int]]:
    references: list[dict[str, int]] = []
    for offset in range(0, len(application) - 3):
        value = struct.unpack_from("<I", application, offset)[0]
        canonical = value & ~1
        if FUNCTION_START <= canonical < FUNCTION_END:
            references.append(
                {
                    "address": APPLICATION_BASE + offset,
                    "value": value,
                    "canonical": canonical,
                }
            )
    return references


def verify_upstream_source() -> dict[str, Any]:
    data = UPSTREAM_PORTASM.read_bytes()
    if sha256(data) != UPSTREAM_PORTASM_SHA256:
        raise AuditError("FreeRTOS portasm.s SHA-256 drift")
    if git_blob_sha1(data) != UPSTREAM_PORTASM_GIT_BLOB:
        raise AuditError("FreeRTOS portasm.s Git blob drift")

    text = data.decode("utf-8")
    required = (
        "ulSetInterruptMask:",
        "mrs r0, basepri",
        "mov r1, #configMAX_SYSCALL_INTERRUPT_PRIORITY",
        "msr basepri, r1",
        "vClearInterruptMask:",
        "msr basepri, r0",
    )
    for fragment in required:
        if fragment not in text:
            raise AuditError(f"FreeRTOS port source is missing {fragment!r}")
    first = text.index("ulSetInterruptMask:")
    second = text.index("vClearInterruptMask:", first)
    block = text[first:second]
    for fragment in ("dsb", "isb", "bx lr"):
        if fragment not in block:
            raise AuditError(
                f"ulSetInterruptMask source block is missing {fragment!r}"
            )

    return {
        "release": "FreeRTOS-Kernel V10.5.1",
        "commit": UPSTREAM_COMMIT,
        "tree": UPSTREAM_TREE,
        "path": str(UPSTREAM_PORTASM.relative_to(ROOT)),
        "sha256": UPSTREAM_PORTASM_SHA256,
        "git_blob_sha1": UPSTREAM_PORTASM_GIT_BLOB,
        "source_lines": "156-162",
        "portable_layer": "IAR/ARM_CM55_NTZ/non_secure",
        "license": "MIT",
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

    body = image_slice(application, FUNCTION_START, FUNCTION_END)
    predecessor = image_slice(
        application,
        PREDECESSOR_START,
        FUNCTION_START,
    )
    successor = image_slice(application, FUNCTION_END, SUCCESSOR_END)
    if body != FUNCTION_BYTES or sha256(body) != FUNCTION_SHA256:
        raise AuditError("ulSetInterruptMask body drift")
    if (
        predecessor != PREDECESSOR_BYTES
        or sha256(predecessor) != PREDECESSOR_SHA256
    ):
        raise AuditError("vStartFirstTask predecessor boundary drift")
    if successor != SUCCESSOR_BYTES or sha256(successor) != SUCCESSOR_SHA256:
        raise AuditError("vClearInterruptMask successor boundary drift")

    branches = scan_branches(application)
    callers = [int(item["address"]) for item in branches["direct_bl"]]
    caller_digest = sha256(
        b"".join(struct.pack("<I", address) for address in callers)
    )
    page_counts = dict(Counter(address & ~0xFFF for address in callers))
    if len(callers) != CALLSITE_COUNT or caller_digest != CALLSITE_SHA256:
        raise AuditError("direct BL caller topology drift")
    if page_counts != CALLSITE_PAGE_COUNTS:
        raise AuditError("direct BL page distribution drift")
    for address in REPRESENTATIVE_CALLS:
        if address not in callers:
            raise AuditError(
                f"representative caller 0x{address:08X} is missing"
            )
    for key in (
        "direct_bw",
        "external_interior_wide",
        "external_entry_or_interior_narrow",
    ):
        if branches[key]:
            raise AuditError(f"unexpected branch references in {key}")

    stored = scan_stored_references(application)
    if stored:
        raise AuditError("unexpected stored entry/interior reference")

    upstream = verify_upstream_source()
    return {
        "status": "ok",
        "read_only": True,
        "image": {
            "path": str(image_path),
            "package_sha256": PACKAGE_SHA256,
            "application_sha256": APPLICATION_SHA256,
            "load_address": APPLICATION_BASE,
        },
        "function": {
            "name": "ulSetInterruptMask",
            "start": FUNCTION_START,
            "end_exclusive": FUNCTION_END,
            "size": len(body),
            "sha256": FUNCTION_SHA256,
            "instructions": (
                "mrs r0,basepri",
                "mov.w r1,#0x30",
                "msr basepri,r1",
                "dsb sy",
                "isb sy",
                "bx lr",
            ),
            "abi": {
                "architecture": "Arm Cortex-M55 / Armv8-M Mainline",
                "calling_convention": "AAPCS32 Thumb",
                "return": "r0 = previous BASEPRI",
                "clobbers": ["r0", "r1"],
                "architectural_side_effect": "BASEPRI becomes 0x30",
                "privilege_requirement": (
                    "BASEPRI write must execute in privileged context"
                ),
                "private_data_dependencies": [],
                "outgoing_calls": [],
                "relocations_or_literals": [],
                "configMAX_SYSCALL_INTERRUPT_PRIORITY": 0x30,
            },
        },
        "neighbors": {
            "predecessor": {
                "name": "vStartFirstTask",
                "start": PREDECESSOR_START,
                "end_exclusive": FUNCTION_START,
                "sha256": PREDECESSOR_SHA256,
            },
            "successor": {
                "name": "vClearInterruptMask",
                "start": FUNCTION_END,
                "end_exclusive": SUCCESSOR_END,
                "sha256": SUCCESSOR_SHA256,
            },
        },
        "references": {
            "direct_bl_count": len(callers),
            "direct_bl_callsite_sha256": caller_digest,
            "direct_bl_addresses": callers,
            "page_counts": {
                f"0x{page:08X}": count
                for page, count in sorted(page_counts.items())
            },
            "representative_calls": [
                {"address": address, "role": role}
                for address, role in REPRESENTATIVE_CALLS.items()
            ],
            "direct_bw": branches["direct_bw"],
            "external_interior_wide": branches[
                "external_interior_wide"
            ],
            "external_entry_or_interior_narrow": branches[
                "external_entry_or_interior_narrow"
            ],
            "stored_entry_or_interior": stored,
        },
        "upstream": upstream,
        "ownership_assessment": {
            "unequivocal_public_source": True,
            "source_ownable": True,
            "fixed_seam_safe_while_official_provider_is_retained": True,
            "preferred_next_step": (
                "compile a syntax-adapted MIT-retaining Cortex-M55 assembly "
                "leaf with mask 0x30 and claim the exact stock span"
            ),
            "fixed_seam_conditions": [
                "retain authenticated bytes at [0x005FA0A4,0x005FA0BA)",
                "bind calls to even entry 0x005FA0A4 using Thumb BL semantics",
                "preserve AAPCS return of previous BASEPRI in r0",
                "do not remove the official provider until all 181 calls migrate",
            ],
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
        print(f"PASS package: {args.image}")
        print(
            "PASS ulSetInterruptMask: "
            "[0x005FA0A4,0x005FA0BA), 22 bytes, BASEPRI=0x30"
        )
        print(
            "PASS references: "
            f"{result['references']['direct_bl_count']} direct BL, "
            "no B.W/narrow/interior/stored references"
        )
        print(
            "PASS upstream: FreeRTOS-Kernel V10.5.1 "
            "IAR/ARM_CM55_NTZ/non_secure, MIT"
        )
        print("PASS ownership: source-ownable; audited fixed seam is bounded")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, OSError, ValueError) as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
