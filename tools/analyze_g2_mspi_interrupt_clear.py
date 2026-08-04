#!/usr/bin/env python3
"""Audit the exact Apollo510 MSPI interrupt-clear source boundary.

The audit is deliberately read-only.  It authenticates the official G2 main
and boot images, pins both copies of the function and their direct callers,
and optionally authenticates an AmbiqSuite 5.1.0 am_hal_mspi.c snapshot.
It has no device, debugger, serial, or flash-programming path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


class AuditError(RuntimeError):
    """Raised when an authenticated input or recovered invariant drifts."""


@dataclass(frozen=True)
class Image:
    name: str
    path: Path
    file_sha256: str
    header_size: int
    load_address: int
    function_start: int
    function_end: int
    magic_literal: int
    register_base_literal: int
    direct_callers: tuple[int, ...]
    caller_roles: dict[int, str]


IMAGES = (
    Image(
        name="main",
        path=(
            ROOT
            / "blobs"
            / "official"
            / "g2-2.2.6.10"
            / "ota_s200_firmware_ota.bin"
        ),
        file_sha256=(
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863"
        ),
        header_size=32,
        load_address=0x00438000,
        function_start=0x004C23DE,
        function_end=0x004C240E,
        magic_literal=0x004C2ADC,
        register_base_literal=0x004C26DC,
        direct_callers=(
            0x0046F4FE,
            0x0046FD4A,
            0x00592672,
            0x0059CE4C,
            0x0059D0D8,
            0x005BBD62,
        ),
        caller_roles={
            0x0046F4FE: "MSPI1 IRQ wrapper used by the G2 NOR transport",
            0x0046FD4A: "G2 MX25U25643G/MSPI1 low-level initializer",
            0x00592672: "additional MSPI IRQ wrapper",
            0x0059CE4C: "additional MSPI transaction setup",
            0x0059D0D8: "additional MSPI controller initializer",
            0x005BBD62: "additional MSPI IRQ wrapper",
        },
    ),
    Image(
        name="boot",
        path=(
            ROOT
            / "blobs"
            / "official"
            / "g2-2.2.6.10"
            / "ota_s200_bootloader.bin"
        ),
        file_sha256=(
            "f89a4c4657537cec6bfc572bdb8318866"
            "309b90a5d180c4307680d39824167b5"
        ),
        header_size=0,
        load_address=0x00410000,
        function_start=0x00426506,
        function_end=0x00426536,
        magic_literal=0x00426C04,
        register_base_literal=0x00426804,
        direct_callers=(0x0041FE1A, 0x004203CC),
        caller_roles={
            0x0041FE1A: "MSPI1 IRQ wrapper used by the boot NOR transport",
            0x004203CC: "boot MX25U25643G/MSPI1 low-level initializer",
        },
    ),
)


EXPECTED_FUNCTION = bytes.fromhex(
    "02 00"              # movs r2,r0
    "00 28"              # cmp r0,#0
    "06 d0"              # beq invalid
    "00 68"              # ldr r0,[r0]
    "20 f0 7e 40"        # bic r0,r0,#0xfe000000
    "df f8 f0 36"        # ldr.w r3,[pc,#0x6f0] -> 0x01bebebe
    "98 42"              # cmp r0,r3
    "01 d0"              # beq valid
    "02 20"              # movs r0,#2 (INVALID_HANDLE)
    "0a e0"              # b return
    "50 68"              # ldr r0,[r2,#4] (module)
    "b8 4a"              # ldr r2,[pc,#0x2e0] -> 0x40060000
    "12 eb 00 33"        # base + module*0x1000
    "c3 f8 08 12"        # str.w r1,[r3,#0x208] (INTCLR)
    "12 eb 00 32"        # base + module*0x1000
    "d2 f8 04 02"        # ldr.w r0,[r2,#0x204] (INTSTAT readback)
    "00 20"              # movs r0,#0 (SUCCESS)
    "70 47"              # bx lr
)
EXPECTED_FUNCTION_SHA256 = (
    "4b01a25a8075cf158eb59da277f8730e36c751ee01c67bae86bc172ec877bd48"
)
EXPECTED_PREDECESSOR_TAIL = bytes.fromhex("10 bc 70 47")
EXPECTED_SUCCESSOR_HEAD = bytes.fromhex("2d e9 ff 41")
EXPECTED_HANDLE_WORD = 0x01BEBEBE
EXPECTED_REGISTER_BASE = 0x40060000

UPSTREAM = {
    "repository": "https://github.com/AmbiqMicro/ambiqhal_ambiq.git",
    "commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
    "commit_subject": "Import Apollo510 HAL from AmbiqSuite SDK 5.1.0",
    "sdk_version": "5.1.0",
    "source_revision": "release_sdk5p1p0-366b80e084",
    "file": "mcu/apollo510/hal/mcu/am_hal_mspi.c",
    "function": "am_hal_mspi_interrupt_clear",
    "source_lines": "4135-4161",
    "git_blob_sha1": "c12ef914660227aba3ebef3a0fb3ec749510c1bc",
    "file_sha256": (
        "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"
    ),
    "license": "BSD-3-Clause",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    prefix = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def image_slice(image: Image, payload: bytes, address: int, size: int) -> bytes:
    offset = address - image.load_address
    if offset < 0 or offset + size > len(payload):
        raise AuditError(
            f"{image.name}: address 0x{address:08x}+0x{size:x} is outside image"
        )
    return payload[offset : offset + size]


def thumb_bl_target(address: int, first: int, second: int) -> int | None:
    """Decode a Thumb-2 BL immediate, returning its even target address."""

    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
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
    return (address + 4 + immediate) & 0xFFFFFFFF


def direct_bl_callers(payload: bytes, load_address: int, target: int) -> list[int]:
    callers: list[int] = []
    for offset in range(0, len(payload) - 3, 2):
        first, second = struct.unpack_from("<HH", payload, offset)
        address = load_address + offset
        if thumb_bl_target(address, first, second) == target:
            callers.append(address)
    return callers


def stored_entry_addresses(
    payload: bytes, load_address: int, target: int
) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    for label, value in (("even", target), ("thumb", target | 1)):
        needle = struct.pack("<I", value)
        addresses: list[int] = []
        cursor = 0
        while True:
            cursor = payload.find(needle, cursor)
            if cursor < 0:
                break
            addresses.append(load_address + cursor)
            cursor += 1
        result[label] = addresses
    return result


def verify_upstream_source(path: Path) -> dict[str, str]:
    data = path.read_bytes()
    actual_sha256 = sha256(data)
    actual_blob = git_blob_sha1(data)
    if actual_sha256 != UPSTREAM["file_sha256"]:
        raise AuditError(
            f"Ambiq source SHA-256 drift: {actual_sha256} != "
            f"{UPSTREAM['file_sha256']}"
        )
    if actual_blob != UPSTREAM["git_blob_sha1"]:
        raise AuditError(
            f"Ambiq source Git blob drift: {actual_blob} != "
            f"{UPSTREAM['git_blob_sha1']}"
        )
    text = data.decode("utf-8")
    required_fragments = (
        UPSTREAM["source_revision"],
        "am_hal_mspi_interrupt_clear(void *pHandle,",
        "MSPIn(ui32Module)->INTCLR = ui32IntMask;",
        "*(volatile uint32_t*)(&MSPIn(ui32Module)->INTSTAT);",
    )
    for fragment in required_fragments:
        if fragment not in text:
            raise AuditError(f"Ambiq source is missing {fragment!r}")
    return {"path": str(path), "sha256": actual_sha256, "git_blob_sha1": actual_blob}


def run_audit(ambiq_source: Path | None = None) -> dict[str, Any]:
    image_results: dict[str, Any] = {}
    common_body: bytes | None = None

    for image in IMAGES:
        file_data = image.path.read_bytes()
        if sha256(file_data) != image.file_sha256:
            raise AuditError(f"{image.name}: authenticated image hash drift")
        payload = file_data[image.header_size :]
        size = image.function_end - image.function_start
        body = image_slice(image, payload, image.function_start, size)
        if body != EXPECTED_FUNCTION:
            raise AuditError(f"{image.name}: interrupt-clear body drift")
        if sha256(body) != EXPECTED_FUNCTION_SHA256:
            raise AuditError(f"{image.name}: interrupt-clear hash drift")
        if common_body is not None and body != common_body:
            raise AuditError("main and boot interrupt-clear functions differ")
        common_body = body

        predecessor = image_slice(
            image,
            payload,
            image.function_start - len(EXPECTED_PREDECESSOR_TAIL),
            len(EXPECTED_PREDECESSOR_TAIL),
        )
        successor = image_slice(
            image,
            payload,
            image.function_end,
            len(EXPECTED_SUCCESSOR_HEAD),
        )
        if predecessor != EXPECTED_PREDECESSOR_TAIL:
            raise AuditError(f"{image.name}: predecessor boundary drift")
        if successor != EXPECTED_SUCCESSOR_HEAD:
            raise AuditError(f"{image.name}: successor boundary drift")

        handle_word = struct.unpack(
            "<I",
            image_slice(image, payload, image.magic_literal, 4),
        )[0]
        register_base = struct.unpack(
            "<I",
            image_slice(image, payload, image.register_base_literal, 4),
        )[0]
        if handle_word != EXPECTED_HANDLE_WORD:
            raise AuditError(f"{image.name}: combined handle validation word drift")
        if register_base != EXPECTED_REGISTER_BASE:
            raise AuditError(f"{image.name}: MSPI register base drift")

        callers = direct_bl_callers(
            payload,
            image.load_address,
            image.function_start,
        )
        if callers != list(image.direct_callers):
            raise AuditError(
                f"{image.name}: direct caller drift: "
                f"{[hex(value) for value in callers]}"
            )
        stored = stored_entry_addresses(
            payload,
            image.load_address,
            image.function_start,
        )
        if stored["even"] or stored["thumb"]:
            raise AuditError(f"{image.name}: unexpected stored entry address")

        image_results[image.name] = {
            "file": str(image.path.relative_to(ROOT)),
            "file_sha256": image.file_sha256,
            "function": {
                "start": image.function_start,
                "end_exclusive": image.function_end,
                "size": size,
                "sha256": EXPECTED_FUNCTION_SHA256,
            },
            "literal_evidence": {
                "combined_initialized_handle_word": handle_word,
                "mspi_register_base": register_base,
                "module_field_offset": 4,
                "module_register_stride": 0x1000,
                "intstat_offset": 0x204,
                "intclr_offset": 0x208,
            },
            "direct_callers": [
                {
                    "address": caller,
                    "role": image.caller_roles[caller],
                }
                for caller in callers
            ],
            "stored_entry_addresses": stored,
        }

    result: dict[str, Any] = {
        "status": "ok",
        "read_only": True,
        "upstream": UPSTREAM,
        "images": image_results,
        "cross_image": {
            "byte_identical": True,
            "function_sha256": EXPECTED_FUNCTION_SHA256,
        },
        "source_equivalence": {
            "handle_validation": (
                "pHandle non-null, initialized bit set, magic 0xBEBEBE"
            ),
            "module_lookup": "uint32_t at handle offset +4",
            "side_effects": [
                "write ui32IntMask to MSPI[module].INTCLR (+0x208)",
                "volatile read of MSPI[module].INTSTAT (+0x204)",
            ],
            "returns": {
                "invalid_handle": 2,
                "success": 0,
            },
        },
        "reuse_assessment": {
            "safe_candidate": True,
            "safe_scope": (
                "compile the pinned AmbiqSuite 5.1.0 am_hal_mspi.c with its "
                "Apollo510 headers and select this function from that "
                "translation unit"
            ),
            "unsafe_scope": (
                "do not hand-copy it as an ABI-free standalone leaf or call "
                "the 5.1.0 am_hal_mspi_control enum ABI from opaque stock code"
            ),
            "version_limit": (
                "the exact function body is also present in AmbiqSuite 5.0.0; "
                "it proves a source match to 5.1.0, not exclusive historical "
                "5.1.0 provenance for the G2 binary"
            ),
        },
    }
    if ambiq_source is not None:
        result["upstream_source_verification"] = verify_upstream_source(
            ambiq_source
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ambiq-source",
        type=Path,
        help="optional AmbiqSuite 5.1.0 am_hal_mspi.c to authenticate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit complete machine-readable evidence",
    )
    args = parser.parse_args()

    try:
        result = run_audit(args.ambiq_source)
    except (AuditError, FileNotFoundError, UnicodeDecodeError) as error:
        raise SystemExit(
            f"Apollo510 MSPI interrupt-clear audit: FAIL: {error}"
        ) from error

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Apollo510 MSPI interrupt-clear audit: OK")
        print("main/boot function bodies: byte-identical (48 bytes)")
        print("upstream: AmbiqSuite 5.1.0 am_hal_mspi_interrupt_clear")
        print("source candidate: safe only with the pinned Apollo510 HAL context")
        print("analysis mode: read-only; no device or flash operation performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
