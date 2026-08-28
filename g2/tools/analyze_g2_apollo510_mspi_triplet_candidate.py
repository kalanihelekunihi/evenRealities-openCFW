#!/usr/bin/env python3
"""Qualify the software-only Apollo510 MSPI HAL triplet candidate.

This read-only audit binds three stock Apollo-main bodies to the authenticated
AmbiqSuite 5.1.0 translation unit and verifies the separate G2 request-ordinal
adapter.  It never signs, flashes, erases, probes, or opens a device.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
AMBIQ_ROOT = ROOT / "third_party/ambiqsuite-apollo510"
AMBIQ_SOURCE = AMBIQ_ROOT / "mcu/apollo510/hal/mcu/am_hal_mspi.c"
AMBIQ_HEADER = AMBIQ_ROOT / "mcu/apollo510/hal/mcu/am_hal_mspi.h"
AMBIQ_LICENSE = AMBIQ_ROOT / "LICENSE"
CORPUS = (
    ROOT
    / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-05.c"
)
CORPUS_CALLERS = (
    ROOT / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-02.c",
    ROOT / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-12.c",
)
ADAPTER = (
    ROOT
    / "components/shared/ambiqsuite/runtime_apollo510_mspi_stock_abi_candidate.c"
)

FILE_PINS = {
    OFFICIAL: (
        3_523_396,
        "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
    ),
    AMBIQ_SOURCE: (
        168_473,
        "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f",
    ),
    AMBIQ_HEADER: (
        36_982,
        "2a682bb7c1618982d6a802f3220a38696cd594c89d90e64b1a698d226b0a557b",
    ),
    AMBIQ_LICENSE: (
        1_525,
        "0770df5c1956b75715604d5788804eabfc293fc61d5dbbec498c6d379a63755f",
    ),
    CORPUS: (
        582_144,
        "606364a89d1be4be2a6eb0c114069ffa93139ca36cf7b8e9739fae2458c282f1",
    ),
    CORPUS_CALLERS[0]: (
        662_399,
        "4efd96c175b25c1c6ea7478df792db4ce6711f76fcb05e574a366ce867b5a0da",
    ),
    CORPUS_CALLERS[1]: (
        606_573,
        "1f8038a93bb5b5d424fd8d2b8858a0b9fcc9fc55a6935cde0d77ee9cb1988ae8",
    ),
}

LOAD_ADDRESS = 0x00438000
HEADER_SIZE = 32
TRIPLET = {
    0x004C099C: {
        "end": 0x004C0E1E,
        "size": 1_154,
        "sha256": "7bff62978262757d9fae426199f54aaa265779f4d0ee5e61add9a710d7fd08bd",
        "upstream": "am_hal_mspi_device_configure",
        "callers": (
            0x0046FC32, 0x0046FC42, 0x00470DDA,
            0x00593272, 0x0059C8D2, 0x0059D038,
        ),
    },
    0x004C0F78: {
        "end": 0x004C2098,
        "size": 4_384,
        "body_bytes": 4_372,
        "sha256": "a9676ac0717977a1d4be1a730ba02d5dfefc3da780721c8b3ccd3543ca80bf7c",
        "upstream": "am_hal_mspi_control",
        "callers": (
            0x0046F6E0, 0x0046F7BC, 0x0046FD28, 0x0046FD3A,
            0x00470F10, 0x00470FC4, 0x0059C9DE, 0x0059CAAC,
        ),
    },
    0x004C240E: {
        "end": 0x004C26D6,
        "size": 712,
        "sha256": "8c43c0d8fd418e04cf808e80d00867981dc2a3eaefb23ee0227ed39538484164",
        "upstream": "am_hal_mspi_interrupt_service",
        "callers": (0x0046F506, 0x0059267A, 0x005BBD6A),
    },
}

# Stock -> public AmbiqSuite 5.1.0.  Stock-only 10/11 and sentinel 40 are
# deliberately absent.  The public-only requests 38/39 have no stock input.
EXPECTED_TRANSLATION = {
    **{value: value for value in range(10)},
    **{value: value - 2 for value in range(12, 24)},
    24: 22,
    25: 24,
    26: 23,
    **{value: value - 2 for value in range(27, 40)},
}
EXPECTED_USED_REQUESTS = Counter({16: 2, 18: 1, 21: 1, 24: 4})
EXPECTED_PUBLIC_ENUM = (
    "AM_HAL_MSPI_REQ_APBCLK",
    "AM_HAL_MSPI_REQ_FLAG_SETCLR",
    "AM_HAL_MSPI_REQ_LINK_IOM",
    "AM_HAL_MSPI_REQ_LINK_MSPI",
    "AM_HAL_MSPI_REQ_DCX_DIS",
    "AM_HAL_MSPI_REQ_DCX_EN",
    "AM_HAL_MSPI_REQ_SCRAMB_DIS",
    "AM_HAL_MSPI_REQ_SCRAMB_EN",
    "AM_HAL_MSPI_REQ_XIPACK",
    "AM_HAL_MSPI_REQ_CE_LATENCY",
    "AM_HAL_MSPI_REQ_DDR_DIS",
    "AM_HAL_MSPI_REQ_DDR_EN",
    "AM_HAL_MSPI_REQ_DQS",
    "AM_HAL_MSPI_REQ_RXCFG",
    "AM_HAL_MSPI_REQ_TIMING_SCAN_SET",
    "AM_HAL_MSPI_REQ_TIMING_SCAN_GET",
    "AM_HAL_MSPI_REQ_XIP_CONFIG",
    "AM_HAL_MSPI_REQ_XIP_MISC_CONFIG",
    "AM_HAL_MSPI_REQ_XIP_DIS",
    "AM_HAL_MSPI_REQ_XIP_EN",
    "AM_HAL_MSPI_REQ_BIG_ENDIAN",
    "AM_HAL_MSPI_REQ_LITTLE_ENDIAN",
    "AM_HAL_MSPI_REQ_PIOMIXED_CONFIG",
    "AM_HAL_MSPI_REQ_DEVICE_CONFIG",
    "AM_HAL_MSPI_REQ_CLOCK_CONFIG",
    "AM_HAL_MSPI_REQ_PAUSE",
    "AM_HAL_MSPI_REQ_UNPAUSE",
    "AM_HAL_MSPI_REQ_SET_SEQMODE",
    "AM_HAL_MSPI_REQ_SEQ_END",
    "AM_HAL_MSPI_REQ_INIT_HIPRIO",
    "AM_HAL_MSPI_REQ_START_BLOCK",
    "AM_HAL_MSPI_REQ_END_BLOCK",
    "AM_HAL_MSPI_REQ_CQ_RAW",
    "AM_HAL_MSPI_REQ_SET_INSTR_ADDR_LEN",
    "AM_HAL_MSPI_REQ_NAND_FLASH_SET_WLAT",
    "AM_HAL_MSPI_REQ_NAND_FLASH_SENDADDR_DIS",
    "AM_HAL_MSPI_REQ_NAND_FLASH_SENDADDR_EN",
    "AM_HAL_MSPI_REQ_CPU_READ_COMBINE",
    "AM_HAL_MSPI_REQ_SCRAMBLE_CONFIG",
    "AM_HAL_MSPI_REQ_SET_DATA_LATENCY",
    "AM_HAL_MSPI_REQ_MAX",
)


class AuditError(RuntimeError):
    """Raised when a pinned input or compatibility invariant drifts."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def authenticate(path: Path, expected: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    actual = (len(data), sha256(data))
    if actual != expected:
        raise AuditError(f"{path}: identity drift: {actual} != {expected}")
    return data


def thumb_bl_target(address: int, first: int, second: int) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    imm11 = second & 0x07FF
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    immediate = (sign << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFFFFFF


def direct_callers(payload: bytes, target: int) -> tuple[int, ...]:
    callers: list[int] = []
    for offset in range(0, len(payload) - 3, 2):
        first, second = struct.unpack_from("<HH", payload, offset)
        address = LOAD_ADDRESS + offset
        if thumb_bl_target(address, first, second) == target:
            callers.append(address)
    return tuple(callers)


def adapter_translation(source: str) -> dict[int, int]:
    table_match = re.search(
        r"g_request_translation\[\]\s*=\s*\{(?P<body>.*?)\n\};",
        source,
        re.S,
    )
    if not table_match:
        raise AuditError("adapter translation table is missing")
    pairs = {
        int(stock): int(upstream)
        for stock, upstream in re.findall(
            r"\{\s*(\d+)u,\s*(\d+)u\s*\}", table_match.group("body")
        )
    }
    if len(pairs) != len(re.findall(r"\{\s*\d+u,", table_match.group("body"))):
        raise AuditError("adapter contains duplicate stock request ordinals")
    return pairs


def public_enum(header: str) -> tuple[str, ...]:
    anchor = header.find("AM_HAL_MSPI_REQ_APBCLK")
    start = header.rfind("typedef enum", 0, anchor)
    match = re.match(
        r"typedef enum\s*\{(?P<body>.*?)\}\s*am_hal_mspi_request_e\s*;",
        header[start:],
        re.S,
    ) if start >= 0 else None
    if not match:
        raise AuditError("could not recover am_hal_mspi_request_e")
    names = re.findall(
        r"^\s*(AM_HAL_MSPI_REQ_[A-Z0-9_]+)\s*,",
        match.group("body"),
        re.M,
    )
    if re.search(r"^\s*AM_HAL_MSPI_REQ_MAX\s*$", match.group("body"), re.M):
        names.append("AM_HAL_MSPI_REQ_MAX")
    return tuple(names)


def corpus_function(corpus: str, entry: int) -> tuple[str, int, str]:
    marker = re.search(
        rf"/\* FUN 0x{entry:08x} .*? bytes=(\d+) sha256=([0-9a-f]{{64}}) \*/",
        corpus,
    )
    if not marker:
        raise AuditError(f"corpus marker missing for 0x{entry:08x}")
    next_marker = corpus.find("/* FUN 0x", marker.end())
    if next_marker < 0:
        next_marker = len(corpus)
    return corpus[marker.start():next_marker], int(marker.group(1)), marker.group(2)


def run_audit() -> dict[str, Any]:
    authenticated = {str(path.relative_to(ROOT)): authenticate(path, pin) for path, pin in FILE_PINS.items()}
    package = authenticated[str(OFFICIAL.relative_to(ROOT))]
    payload = package[HEADER_SIZE:]
    ambiq_source = authenticated[str(AMBIQ_SOURCE.relative_to(ROOT))].decode()
    corpus = authenticated[str(CORPUS.relative_to(ROOT))].decode()
    caller_corpus = "\n".join(
        authenticated[str(path.relative_to(ROOT))].decode()
        for path in CORPUS_CALLERS
    )
    license_text = authenticated[str(AMBIQ_LICENSE.relative_to(ROOT))].decode()
    header = authenticated[str(AMBIQ_HEADER.relative_to(ROOT))].decode()
    adapter = ADAPTER.read_text()

    if "BSD 3-Clause License" not in license_text or "Copyright (c) 2025, Ambiq Micro, Inc." not in license_text:
        raise AuditError("Ambiq BSD-3-Clause terms are incomplete")
    if public_enum(header) != EXPECTED_PUBLIC_ENUM:
        raise AuditError("public AmbiqSuite request enum drift")
    translation = adapter_translation(adapter)
    if translation != EXPECTED_TRANSLATION:
        raise AuditError("G2 stock/public request translation drift")
    if "stock_request & 0xffu" not in adapter:
        raise AuditError("adapter no longer preserves the stock low-byte request ABI")
    if "SPDX-License-Identifier: BSD-3-Clause" not in adapter:
        raise AuditError("adapter lost its BSD-3-Clause declaration")

    source_functions = {}
    for facts in TRIPLET.values():
        name = facts["upstream"]
        if not re.search(rf"\b{name}\s*\(", ambiq_source):
            raise AuditError(f"upstream provider missing {name}")
        source_functions[name] = True

    triplet_result: dict[str, Any] = {}
    for entry, facts in TRIPLET.items():
        offset = entry - LOAD_ADDRESS
        installed = payload[offset:offset + facts["size"]]
        body, corpus_bytes, corpus_sha = corpus_function(corpus, entry)
        expected_body_bytes = int(facts.get("body_bytes", facts["size"]))
        if corpus_bytes != expected_body_bytes or corpus_sha != facts["sha256"]:
            raise AuditError(f"0x{entry:08x}: corpus boundary drift")
        # The control function has a 12-byte inline pool excluded by Ghidra's
        # body hash.  The other two entries are contiguous executable bodies.
        if entry != 0x004C0F78 and sha256(installed) != facts["sha256"]:
            raise AuditError(f"0x{entry:08x}: stock body hash drift")
        callers = direct_callers(payload, entry)
        if callers != facts["callers"]:
            raise AuditError(f"0x{entry:08x}: direct caller topology drift")
        triplet_result[f"0x{entry:08X}"] = {
            "end_exclusive": facts["end"],
            "envelope_bytes": facts["size"],
            "body_bytes": expected_body_bytes,
            "body_sha256": facts["sha256"],
            "upstream_function": facts["upstream"],
            "direct_call_sites": list(callers),
            "corpus_has_handle_validation": "0x1ffffff" in body,
        }

    control_body, _, _ = corpus_function(corpus, 0x004C0F78)
    required_control_evidence = (
        "0x28 < ((uint)param_2 & 0xff)",
        "uVar5 = (uint)param_2 & 0xff",
        "uVar5 == 0x10",
        "uVar5 == 0x12",
        "uVar5 == 0x18",
        "uVar5 != 0x27",
    )
    if not all(token in control_body for token in required_control_evidence):
        raise AuditError("stock control-dispatch evidence drift")

    call_args = Counter(
        int(value, 0)
        for value in re.findall(r"FUN_004c0f78\([^,\n]+,\s*(0x[0-9a-f]+|\d+)\s*,", caller_corpus)
    )
    if call_args != EXPECTED_USED_REQUESTS:
        raise AuditError(f"stock control-call requests drift: {call_args}")
    translated_used = {stock: translation[stock] for stock in sorted(call_args)}

    return {
        "status": "candidate-qualified",
        "read_only": True,
        "hardware_operations": False,
        "upstream": {
            "version": "AmbiqSuite 5.1.0",
            "commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
            "translation_unit": str(AMBIQ_SOURCE.relative_to(ROOT)),
            "license": "BSD-3-Clause",
            "functions": list(source_functions),
        },
        "triplet": triplet_result,
        "request_abi": {
            "stock_valid_range": [0, 39],
            "stock_sentinel": 40,
            "stock_only_unsupported": [10, 11],
            "public_only": [38, 39],
            "complete_translation": {str(key): value for key, value in sorted(translation.items())},
            "observed_stock_requests": dict(sorted(call_args.items())),
            "observed_translation": translated_used,
            "all_observed_requests_supported": True,
            "low_byte_abi_preserved": True,
        },
        "admission": {
            "production_routed": False,
            "software_candidate": True,
            "safe_for_opaque_stock_callers": "only through the ordinal adapter",
            "integration_blockers": [
                "root and resolve the complete upstream device-configure/control/interrupt-service dependency closure",
                "prove the stock private-handle layout reached by all three larger bodies against the 5.1.0 translation unit",
                "choose an explicit policy or implementation for unused stock-only SDR250 requests 10 and 11",
                "keep new source-owned callers on named 5.1.0 enums; do not pass them through the stock adapter",
                "perform hardware qualification only in the later release-validation phase",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_audit()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Apollo510 MSPI triplet candidate: qualified (software only)")
        print("stock requests observed: 16->14, 18->16, 21->19, 24->22")
        print("production routing: disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
