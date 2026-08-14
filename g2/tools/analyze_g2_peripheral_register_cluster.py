#!/usr/bin/env python3
"""Peripheral-register cluster attribution audit for Apollo-main no-evidence functions.

The unanchored-function provenance census
(``docs/research/g2-apollo-unanchored-census.md``) flags 30 no-evidence
functions with hardware hints: 22 whose decompiled text contains tokens in the
``0x40000000`` peripheral range and 8 whose tokens hit SRAM only.  The census
hint is a raw hex-token match and cannot distinguish a peripheral address
from a float or bitmask constant.  This analyzer re-derives the register
evidence from first principles and converts the cluster into an attribution
triage map.

Evidence channels, all re-derived on every run:

1. ``machine-code`` -- the function body bytes from the authenticated image
   are scanned for Thumb-2 ``LDR``-literal instructions (16-bit ``0x4800``
   class and 32-bit ``0xF85F``/``0xF8DF`` class) and for ``MOVW``/``MOVT``
   constant synthesis pairs.  Literal-pool targets are dereferenced against
   the image; a candidate constant is accepted only when it validates against
   the Apollo510 register map (see below).  Junk decodes that happen to land
   in the ``0x4xxxxxxx`` range (floats, instruction words, bitmasks) are
   rejected by the map.
2. ``decompiled-text`` -- the authenticated Ghidra corpus decompilation is
   scanned for absolute-address dereferences (``*(type *)(... 0xADDR ...)``),
   for ``DAT_xxxxxxxx`` cell references whose image content validates as a
   peripheral base (one-hop chase), and for instance-strided offset
   expressions (``DAT_cell + index * 0x1000 + 0xOFF``) on those cells.
3. ``call topology`` -- closed-world callers and callees are computed from
   corpus tokens, exactly like the census; anchored callers are labelled with
   their retained source path.

The register map is rebuilt from the vendored AmbiqSuite Apollo510 5.1.0
dependency closure (``third_party/ambiqsuite-apollo510/``, PROVENANCE.json):
peripheral bases, ``_Type`` bindings, and per-register offsets are parsed
from the CMSIS device header ``apollo510.h``; INFO/OTP-INFO blocks come from
``regs/am_reg_base_addresses.h``; the ``SYNC_READ`` barrier address comes from
``hal/am_hal_sysctrl.h``.  All three headers are pinned by SHA-256, and the
parsed map is pinned by hard structural constants (base count, struct count,
and reviewed register offsets such as ``MSPI0.INTSTAT == 0x204``).

Attribution is triage, not ownership: every cluster function receives exactly
one family (``ambiqsuite-hal``, ``g2-board-support``, or
``investigation-required``), one evidence class, and one confidence level.
The MSPI triplet is anchored by the reviewed
``docs/research/ambiqsuite-mspi-interrupt-clear-source-boundary-audit.md``:
its private cells (MSPI base ``0x40060000`` at ``0x004C26DC``, handle magic
``0x01BEBEBE`` at ``0x004C2ADC``) and the proven ``[0x004C23DE,0x004C240E)``
span of ``am_hal_mspi_interrupt_clear`` are re-validated from the image on
every run.  Any drift in the input census rows, the vendored headers, the
documented cells, or the pinned per-function attributions raises
``ClusterError``.

The analyzer is read-only and deterministic: no signing, flashing, erase, or
hardware operation; nothing under ``g2/research/`` is touched.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import importlib.util
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATH_ANALYZER = ROOT / "tools/analyze_apollo_embedded_source_paths.py"
MANIFESTS = ROOT / "tools/manifests"
CENSUS_FUNCTIONS_TSV = MANIFESTS / "g2-apollo-unanchored-census-functions.tsv"
AMBIQSUITE = ROOT / "third_party/ambiqsuite-apollo510"
APOLLO510_H = AMBIQSUITE / "CMSIS/AmbiqMicro/Include/apollo510.h"
REG_BASE_H = AMBIQSUITE / "mcu/apollo510/regs/am_reg_base_addresses.h"
SYSCTRL_H = AMBIQSUITE / "mcu/apollo510/hal/am_hal_sysctrl.h"

APOLLO510_H_SHA256 = "b6ca35dc828ef95825c0a22f06e6ca5ed558a6542dc74310515fdc350051a797"
REG_BASE_H_SHA256 = "e6d15af8c495288f88a8ad0eea1ccae07cb14cac356f4fb3c138e4c3fedae16d"
SYSCTRL_H_SHA256 = "7ca14c631b87b7b306ab547aa32c0a6c60d53e6ffaf21d6f854c8ab11a89370c"

EXPECTED_CORPUS_FUNCTIONS = 7_370
EXPECTED_CENSUS_ROWS = 5_610

# The census frontier: no-evidence functions whose detail carries the
# peripheral-register hint, and the SRAM-globals-only secondary listing.
# Re-derived from the census manifest and pinned; drift raises ClusterError.
EXPECTED_REGISTER_HINT_ENTRIES = (
    0x0043A1B0, 0x0043C0E4, 0x0043C0EC, 0x0044B158, 0x0047FAE8, 0x0048009E,
    0x004801FC, 0x004C099C, 0x004C0F78, 0x004C240E, 0x004C2AE8, 0x004C3750,
    0x004CA78A, 0x004D3DDA, 0x0051381A, 0x00515304, 0x005202EC, 0x0052262E,
    0x00528DB8, 0x0059BAE4, 0x0059C7AC, 0x005FA13C,
)
EXPECTED_SRAM_ONLY_ENTRIES = (
    0x004408D6, 0x00440968, 0x00440DDA, 0x00472C84,
    0x0052DC98, 0x0052DCDE, 0x005392D4, 0x00539994,
)

# Documented MSPI leaf from the reviewed source-boundary audit.  The cell
# values are re-validated against the authenticated image on every run.
DOCUMENTED_MSPI_INTERRUPT_CLEAR = {
    "entry": 0x004C23DE,
    "end_exclusive": 0x004C240E,
    "magic_cell": 0x004C2ADC,
    "magic_value": 0x01BEBEBE,
    "base_cell": 0x004C26DC,
    "base_value": 0x40060000,
    "source": "docs/research/ambiqsuite-mspi-interrupt-clear-source-boundary-audit.md",
}

# CMSIS map structural pins.  OFFSET_PINS are reviewed register offsets used
# to lock the parsed struct layout (MSPI0.INTSTAT/INTCLR are independently
# static-asserted by the MSPI source-boundary audit's compile proof).
EXPECTED_CMSIS_BASES = 49
EXPECTED_CMSIS_STRUCTS = 30
EXPECTED_CMSIS_SKIPPED_CLOSERS = ("IRQn",)
CMSIS_OFFSET_PINS = {
    ("MSPI0", "INTSTAT"): 0x204,
    ("MSPI0", "INTCLR"): 0x208,
    ("MSPI0", "MSPICFG"): 0x030,
    ("MSPI0", "DEV0XIP"): 0x090,
    ("MSPI0", "CQSETCLEAR"): 0x2B4,
    ("TIMER", "INTEN"): 0x060,
    ("TIMER", "INTCLR"): 0x068,
    ("TIMER", "CTRL15"): 0x3E0,
    ("MCUCTRL", "SIMOBUCK2"): 0x344,
    ("MCUCTRL", "PLLCTL0"): 0x4D8,
    ("PWRCTRL", "DEVPWRSTATUS"): 0x008,
    ("GPIO", "PADKEY"): None,  # presence only; offset locked below at runtime
}
EXPECTED_INFO_BLOCKS = ("INFO0", "INFO1", "OTP_INFO0", "OTP_INFO1", "OTP_INFOC")
SYNC_READ_ADDRESS = 0x47FF0000

# Reviewed peripheral base pins (the full set is 49; these lock the blocks
# the cluster actually touches plus the block-0 anchors).
EXPECTED_BASE_PINS = {
    "RSTGEN": 0x40000000,
    "CLKGEN": 0x40004000,
    "TIMER": 0x40008000,
    "STIMER": 0x40008800,
    "GPIO": 0x40010000,
    "MCUCTRL": 0x40020000,
    "PWRCTRL": 0x40021000,
    "MSPI0": 0x40060000,
    "USB": 0x400B0000,
    "CRYPTO": 0x400C0000,
    "PDM0": 0x40201000,
    "I2S0": 0x40208000,
    "AUDADC": 0x40210000,
}

SRAM_LO = 0x20000000
SRAM_HI = 0x20380000  # DTCM 512KB + SSRAM 3MB window
PERIPH_LO = 0x40000000
PERIPH_HI = 0x60000000
FLASH_LO = 0x00400000
FLASH_HI = 0x00800000  # MRAM window; literal cells live here

FAMILIES = ("ambiqsuite-hal", "g2-board-support", "investigation-required")
EVIDENCE_CLASSES = (
    "machine-code-register-access",
    "decompiled-register-access",
    "sram-indirect-register-candidate",
    "call-topology-into-cluster",
    "no-register-evidence",
    "sram-globals-only-listing",
)
CONFIDENCE_ORDER = ("medium", "low", "none")

MSPI_BLOCKS = frozenset({"MSPI0", "MSPI1", "MSPI2", "MSPI3"})
SYSCTRL_BLOCKS = frozenset(
    {"RSTGEN", "CLKGEN", "RTC", "TIMER", "STIMER", "VCOMP", "MCUCTRL", "PWRCTRL", "WDT"}
)
INFO_OTP_BLOCKS = frozenset(EXPECTED_INFO_BLOCKS)
# Register names distinctive of the Ambiq voltage/power sequencer domain
# (am_hal_pwrctrl / am_hal_spotmgr / am_hal_sysctrl ton-config headers).
POWER_SEQUENCER_REGS = frozenset(
    {
        "SIMOBUCK2", "SIMOBUCK4", "SIMOBUCK6", "SIMOBUCK7", "SIMOBUCK12",
        "SIMOBUCK14", "LDOREG1", "LDOREG2", "VREFGEN2", "VREFGEN4",
        "PWRSW0", "PWRSW1",
    }
)

# Pinned per-function attribution.  Computed by the rule table below, then
# verified against these hard constants; drift raises ClusterError.
# entry: (family, evidence, confidence)
EXPECTED_ATTRIBUTION: dict[int, tuple[str, str, str]] = {
    0x0044B158: ("g2-board-support", "machine-code-register-access", "low"),
    0x0047FAE8: ("ambiqsuite-hal", "machine-code-register-access", "medium"),
    0x0048009E: ("ambiqsuite-hal", "machine-code-register-access", "low"),
    0x004801FC: ("g2-board-support", "machine-code-register-access", "low"),
    0x004C099C: ("ambiqsuite-hal", "machine-code-register-access", "medium"),
    0x004C0F78: ("ambiqsuite-hal", "machine-code-register-access", "medium"),
    0x004C240E: ("ambiqsuite-hal", "machine-code-register-access", "medium"),
    0x004D3DDA: ("ambiqsuite-hal", "machine-code-register-access", "low"),
    0x0051381A: ("g2-board-support", "decompiled-register-access", "low"),
    0x0052262E: ("investigation-required", "sram-indirect-register-candidate", "low"),
    0x004C2AE8: ("investigation-required", "call-topology-into-cluster", "low"),
    0x005202EC: ("investigation-required", "call-topology-into-cluster", "low"),
    0x0043A1B0: ("investigation-required", "no-register-evidence", "none"),
    0x0043C0E4: ("investigation-required", "no-register-evidence", "none"),
    0x0043C0EC: ("investigation-required", "no-register-evidence", "none"),
    0x004C3750: ("investigation-required", "no-register-evidence", "none"),
    0x004CA78A: ("investigation-required", "no-register-evidence", "none"),
    0x00515304: ("investigation-required", "no-register-evidence", "none"),
    0x00528DB8: ("investigation-required", "no-register-evidence", "none"),
    0x0059BAE4: ("investigation-required", "no-register-evidence", "none"),
    0x0059C7AC: ("investigation-required", "no-register-evidence", "none"),
    0x005FA13C: ("investigation-required", "no-register-evidence", "none"),
}

# Pinned validated-reference census for the functions with register evidence:
# entry -> (frozenset of block names, number of validated register references).
EXPECTED_REFERENCE_SUMMARY: dict[int, tuple[frozenset[str], int]] = {
    0x0044B158: (frozenset({"CLKGEN", "STIMER", "MCUCTRL", "USB", "PDM0", "I2S0", "I2S1", "AUDADC", "SYNC_READ"}), 13),
    0x0047FAE8: (frozenset({"CLKGEN", "STIMER", "MCUCTRL", "PWRCTRL"}), 23),
    0x0048009E: (frozenset({"MCUCTRL"}), 3),
    0x004801FC: (frozenset({"TIMER"}), 6),
    0x004C099C: (frozenset({"MSPI0"}), 3),
    0x004C0F78: (frozenset({"MSPI0"}), 11),
    0x004C240E: (frozenset({"MSPI0"}), 4),
    0x004D3DDA: (frozenset({"MCUCTRL", "PWRCTRL", "INFO1", "OTP_INFO0", "OTP_INFO1"}), 5),
    0x0051381A: (frozenset({"OTP_INFOC"}), 1),
}

FUNCTION_BEGIN_RE = re.compile(
    r"OPENCFW_FUNCTION_BEGIN entry=([0-9a-f]+) "
    r"body_start=([0-9a-f]+) body_end=([0-9a-f]+) name=(\S+)",
    re.IGNORECASE,
)
FUNCTION_END_RE = re.compile(r"OPENCFW_FUNCTION_END entry=([0-9a-f]+)", re.IGNORECASE)
ADDRESS_TOKEN_RE = re.compile(r"(?<![0-9a-fA-F])([0-9a-f]{8})(?![0-9a-fA-F])")
DAT_CELL_RE = re.compile(r"(?<![0-9A-Za-z_])DAT_([0-9a-f]{8})(?![0-9A-Za-z_])")
DEREF_RE = re.compile(r"\*(?:\([^()]*\))*\((?:[^()]|\([^()]*\))*\)")
DEREF_BARE_RE = re.compile(r"\*(?:\([^()]*\))*(0x[0-9a-f]{8})(?![0-9a-fA-F])")
HEX_TOKEN_RE = re.compile(r"(?<![0-9a-fA-Fx])(0x[0-9a-f]{8})(?![0-9a-fA-F])")
CELL_OFFSET_RE = re.compile(r"DAT_([0-9a-f]{8})[^()\n;]*?\+ (0x[0-9a-f]{1,8})\)")

CMSIS_BASE_RE = re.compile(r"#define\s+([A-Za-z0-9_]+)_BASE\s+\(?0x([0-9A-Fa-f]{8})UL?\)?")
CMSIS_BIND_RE = re.compile(r"#define\s+([A-Za-z0-9_]+)\s+\(\(([A-Za-z0-9_]+)_Type\s*\*\)")
CMSIS_STRUCT_START_RE = re.compile(r"typedef\s+struct\s*\{")
CMSIS_STRUCT_END_RE = re.compile(r"\}\s*([A-Za-z0-9_]+)_Type\s*;")


class ClusterError(RuntimeError):
    """Raised when authenticated evidence or a closed census changes."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_path_analyzer():
    spec = importlib.util.spec_from_file_location(
        "apollo_paths_for_register_cluster", PATH_ANALYZER
    )
    if spec is None or spec.loader is None:
        raise ClusterError(f"cannot load {PATH_ANALYZER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# CMSIS register map
# ---------------------------------------------------------------------------

def _sizeof_member(statement: str) -> tuple[str | None, int | None]:
    match = re.search(
        r"(?:__IOM|__IM|__OM)?\s*uint32_t\s+([A-Za-z0-9_]+)(?:\[(\d+)\])?\s*$",
        statement.strip(),
    )
    if not match:
        return None, None
    return match.group(1), 4 * (int(match.group(2)) if match.group(2) else 1)


def parse_cmsis_struct(body: str) -> tuple[dict[str, int], int] | None:
    """Offset map for one CMSIS peripheral ``_Type`` struct.

    Only 32-bit members and 32-bit union overlays are accepted; anything else
    returns ``None`` so the caller fails closed instead of guessing offsets.
    """

    body = re.sub(r"/\*!.*?\*/", "", body, flags=re.S)
    body = re.sub(r"//[^\n]*", "", body)
    offset = 0
    registers: dict[str, int] = {}
    pos = 0
    while pos < len(body):
        if body[pos:].strip() == "":
            break
        union = re.match(r"\s*union\s*\{", body[pos:])
        if union:
            depth = 1
            cursor = pos + union.end()
            while depth:
                if cursor >= len(body):
                    return None
                if body[cursor] == "{":
                    depth += 1
                elif body[cursor] == "}":
                    depth -= 1
                cursor += 1
            inner = body[pos + union.end():cursor - 1]
            names = [
                name
                for name in re.findall(
                    r"(?:__IOM|__IM|__OM)\s+uint32_t\s+([A-Za-z0-9_]+)\s*;", inner
                )
                if not name.endswith("_b")
            ]
            if len(names) != 1:
                return None
            registers[names[0]] = offset
            offset += 4
            trailer = re.match(r"\s*;", body[cursor:])
            if not trailer:
                return None
            pos = cursor + trailer.end()
            continue
        member = re.match(r"\s*([^;{}]+);", body[pos:])
        if not member:
            return None
        name, size = _sizeof_member(member.group(1))
        if name is None:
            return None
        if not name.startswith("RESERVED"):
            registers[name] = offset
        offset += size
        pos += member.end()
    return registers, offset


def build_register_map(
    cmsis_text: str,
    reg_base_text: str,
    sysctrl_text: str,
) -> dict[str, Any]:
    """Rebuild the Apollo510 register map from the vendored headers.

    Fail-closed: the parsed map must reproduce the pinned structural
    constants (base count, struct count, skipped non-struct closers, reviewed
    register offsets, INFO blocks, and the SYNC_READ barrier address).
    """

    bases: dict[str, int] = {}
    for match in CMSIS_BASE_RE.finditer(cmsis_text):
        bases[match.group(1)] = int(match.group(2), 16)
    bindings = dict(CMSIS_BIND_RE.findall(cmsis_text))
    if len(bases) != EXPECTED_CMSIS_BASES:
        raise ClusterError(
            f"CMSIS peripheral base census changed: {len(bases)} != {EXPECTED_CMSIS_BASES}"
        )
    for name, address in EXPECTED_BASE_PINS.items():
        if bases.get(name) != address:
            raise ClusterError(
                f"CMSIS peripheral base changed: {name} "
                f"0x{bases.get(name, 0):08X} != 0x{address:08X}"
            )

    starts = [match.end() for match in CMSIS_STRUCT_START_RE.finditer(cmsis_text)]
    structs: dict[str, tuple[dict[str, int], int]] = {}
    skipped: list[str] = []
    start_index = 0
    for end_match in CMSIS_STRUCT_END_RE.finditer(cmsis_text):
        name = end_match.group(1)
        end = end_match.start()
        while start_index + 1 < len(starts) and starts[start_index + 1] < end:
            start_index += 1
        if start_index >= len(starts) or starts[start_index] >= end:
            # non-struct ``_Type;`` closer (for example the IRQn enum)
            skipped.append(name)
            continue
        parsed = parse_cmsis_struct(cmsis_text[starts[start_index]:end])
        start_index += 1
        if parsed is None:
            raise ClusterError(f"CMSIS struct parse failed: {name}")
        structs[name] = parsed
    if len(structs) != EXPECTED_CMSIS_STRUCTS:
        raise ClusterError(
            f"CMSIS struct census changed: {len(structs)} != {EXPECTED_CMSIS_STRUCTS}"
        )
    if tuple(skipped) != EXPECTED_CMSIS_SKIPPED_CLOSERS:
        raise ClusterError(f"CMSIS non-struct closer census changed: {skipped!r}")
    for (type_name, register), offset in CMSIS_OFFSET_PINS.items():
        if type_name not in structs:
            raise ClusterError(f"CMSIS type missing: {type_name}")
        registers = structs[type_name][0]
        if register not in registers:
            raise ClusterError(f"CMSIS register missing: {type_name}.{register}")
        if offset is not None and registers[register] != offset:
            raise ClusterError(
                f"CMSIS register offset changed: {type_name}.{register} "
                f"0x{registers[register]:03x} != 0x{offset:03x}"
            )

    info_blocks: dict[str, tuple[int, int]] = {}
    for block in EXPECTED_INFO_BLOCKS:
        base_match = re.search(
            rf"#define\s+AM_REG_{block}_BASEADDR\s+0x([0-9A-Fa-f]+)", reg_base_text
        )
        size_match = re.search(
            rf"#define\s+AM_REG_{block}_SIZE\s+(\d+)", reg_base_text
        )
        if not base_match or not size_match:
            raise ClusterError(f"INFO block definition missing: {block}")
        info_blocks[block] = (int(base_match.group(1), 16), int(size_match.group(1)))

    sync_match = re.search(r"#define\s+SYNC_READ\s+0x([0-9A-Fa-f]+)", sysctrl_text)
    if not sync_match or int(sync_match.group(1), 16) != SYNC_READ_ADDRESS:
        raise ClusterError("SYNC_READ barrier address changed or missing")

    sorted_bases = sorted(bases.items(), key=lambda item: item[1])
    return {
        "bases": bases,
        "bindings": bindings,
        "structs": structs,
        "sorted_bases": sorted_bases,
        "info_blocks": info_blocks,
    }


def make_classifier(register_map: dict[str, Any]):
    """Map an absolute address to (block, offset, register-name-or-None).

    A candidate is accepted only when it is 4-byte aligned and lands inside a
    known peripheral block below the parsed struct size, inside a vendored
    INFO/OTP-INFO window, or is the SYNC_READ barrier address.  Everything
    else -- float constants, bitmasks, misdecode junk -- is rejected.
    """

    bases = register_map["bases"]
    bindings = register_map["bindings"]
    structs = register_map["structs"]
    sorted_bases = register_map["sorted_bases"]
    addresses = [address for _, address in sorted_bases]
    info_blocks = register_map["info_blocks"]
    names_by_offset = {
        type_name: {offset: name for name, offset in structs[type_name][0].items()}
        for type_name in structs
    }

    def classify(address: int) -> tuple[str, int, str | None] | None:
        if address % 4:
            return None
        if address == SYNC_READ_ADDRESS:
            return "SYNC_READ", 0, None
        index = bisect.bisect_right(addresses, address) - 1
        if index >= 0:
            name, base = sorted_bases[index]
            gap = (
                sorted_bases[index + 1][1] - base
                if index + 1 < len(sorted_bases)
                else 0x1000
            )
            offset = address - base
            if 0 <= offset < gap:
                type_name = bindings.get(name)
                struct = structs.get(type_name)
                if struct is not None and offset < struct[1]:
                    return name, offset, names_by_offset.get(type_name, {}).get(offset)
        for block, (base, size) in info_blocks.items():
            if base <= address < base + size:
                return block, address - base, None
        return None

    return classify


# ---------------------------------------------------------------------------
# Machine-code and decompiled-text evidence
# ---------------------------------------------------------------------------

def scan_code_constants(blob: bytes, load_base: int, start: int, end: int) -> dict[int, set[str]]:
    """Candidate 32-bit constants a Thumb-2 function materializes.

    Scans for ``LDR``-literal loads (16-bit ``0x4800`` class; 32-bit
    ``0xF85F``/``0xF8DF`` classes with Rt != PC) and pairs ``MOVW``/``MOVT``
    syntheses.  Candidates are unvalidated; the register-map classifier
    rejects junk.  The scan is a flat even-offset sweep, so inline literal
    pools cannot desynchronize it; false encodings are filtered downstream.
    """

    def read32(address: int) -> int | None:
        if address % 4 or not (load_base <= address <= load_base + len(blob) - 4):
            return None
        return struct.unpack_from("<I", blob, address - load_base)[0]

    constants: dict[int, set[str]] = defaultdict(set)
    movs: list[tuple[int, int, int, bool]] = []
    address = start & ~1
    while address + 2 <= end:
        halfword = struct.unpack_from("<H", blob, address - load_base)[0]
        if halfword & 0xF800 == 0x4800:
            target = ((address + 4) & ~3) + (halfword & 0xFF) * 4
            value = read32(target)
            if value is not None:
                constants[value].add("ldr16")
        if halfword >> 11 in (0b11101, 0b11110, 0b11111) and address + 4 <= end:
            hw2 = struct.unpack_from("<H", blob, address - load_base + 2)[0]
            if (halfword & 0xFF7F) in (0xF85F, 0xF8DF) and (hw2 >> 12) != 0xF:
                pc = (address + 4) & ~3
                target = pc + (hw2 & 0xFFF) if halfword & 0x80 else pc - (hw2 & 0xFFF)
                value = read32(target)
                if value is not None:
                    constants[value].add("ldr32")
            if halfword & 0xFBF0 in (0xF240, 0xF2C0) and hw2 & 0x8000 == 0:
                imm16 = (
                    ((halfword & 0x0400) << 5)
                    | ((halfword & 0x000F) << 12)
                    | ((hw2 & 0x7000) >> 4)
                    | (hw2 & 0x00FF)
                )
                movs.append((address, (hw2 >> 8) & 0xF, imm16, bool(halfword & 0x0080)))
        address += 2
    for index, (_site, rd, imm, is_movt) in enumerate(movs):
        if not is_movt:
            continue
        for back in range(index - 1, -1, -1):
            _prev_site, prev_rd, prev_imm, prev_movt = movs[back]
            if prev_rd == rd:
                if not prev_movt:
                    constants[(imm << 16) | prev_imm].add("movwt")
                break
    return constants


def scan_text_constants(lines: list[str]) -> tuple[dict[int, set[str]], list[tuple[int, int]]]:
    """Decompiled-text address evidence.

    Returns (candidates, cell_offsets): candidates map absolute addresses to
    evidence kinds (``dat-cell`` for ``DAT_xxxxxxxx`` references,
    ``deref-const`` for constants inside a dereference expression), and
    cell_offsets lists ``(cell_address, offset)`` pairs from instance-strided
    ``DAT_cell + ... + 0xOFF`` access expressions.
    """

    text = "\n".join(lines)
    candidates: dict[int, set[str]] = defaultdict(set)
    for match in DAT_CELL_RE.finditer(text):
        candidates[int(match.group(1), 16)].add("dat-cell")
    for match in DEREF_RE.finditer(text):
        for token in HEX_TOKEN_RE.findall(match.group()):
            candidates[int(token, 16)].add("deref-const")
    for match in DEREF_BARE_RE.finditer(text):
        candidates[int(match.group(1), 16)].add("deref-const")
    cell_offsets = [
        (int(cell, 16), int(offset, 16)) for cell, offset in CELL_OFFSET_RE.findall(text)
    ]
    return candidates, cell_offsets


# ---------------------------------------------------------------------------
# Corpus and census inputs
# ---------------------------------------------------------------------------

def parse_corpus(
    logs: list[Path], keep_text_entries: frozenset[int]
) -> tuple[dict[int, dict[str, Any]], dict[int, list[str]]]:
    """Parse the authenticated corpus: tokens for every function, decompiled
    text only for the cluster entries."""

    functions: dict[int, dict[str, Any]] = {}
    texts: dict[int, list[str]] = {}
    current: dict[str, Any] | None = None
    current_lines: list[str] | None = None
    for log in logs:
        for line in log.read_text(encoding="utf-8", errors="strict").splitlines():
            begin = FUNCTION_BEGIN_RE.search(line)
            if begin:
                entry, body_start, body_end = (int(value, 16) for value in begin.groups()[:3])
                if entry in functions:
                    raise ClusterError(f"duplicate Ghidra function entry 0x{entry:08x}")
                current = {
                    "entry": entry,
                    "body_start": body_start,
                    "body_end_inclusive": body_end,
                    "name": begin.group(4),
                    "tokens": set(),
                }
                functions[entry] = current
                current_lines = [] if entry in keep_text_entries else None
                if current_lines is not None:
                    texts[entry] = current_lines
                continue
            end = FUNCTION_END_RE.search(line)
            if end:
                entry = int(end.group(1), 16)
                if current is None or current["entry"] != entry:
                    raise ClusterError(f"unbalanced Ghidra function marker 0x{entry:08x}")
                current = None
                current_lines = None
                continue
            if current is not None:
                current["tokens"].update(
                    int(token, 16) for token in ADDRESS_TOKEN_RE.findall(line)
                )
                if current_lines is not None:
                    current_lines.append(line)
    if current is not None:
        raise ClusterError("unterminated Ghidra function at end of corpus")
    if len(functions) != EXPECTED_CORPUS_FUNCTIONS:
        raise ClusterError(
            f"expected {EXPECTED_CORPUS_FUNCTIONS} Ghidra functions, found {len(functions)}"
        )
    return functions, texts


def load_census_rows(path: Path) -> dict[int, dict[str, Any]]:
    """Hardware-hint rows of the unanchored census manifest, fail-closed."""

    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    reader = csv.DictReader(lines, delimiter="\t")
    columns = reader.fieldnames or ()
    required = {"entry", "body_start", "body_end_exclusive", "envelope_bytes",
                "official_opaque_bytes", "bucket", "evidence", "confidence", "detail"}
    if not required <= set(columns):
        raise ClusterError(f"unknown census functions schema: {columns!r}")
    rows: dict[int, dict[str, Any]] = {}
    count = 0
    for row in reader:
        count += 1
        entry = int(row["entry"], 16)
        rows[entry] = row
    if count != EXPECTED_CENSUS_ROWS:
        raise ClusterError(f"census function row census changed: {count}")
    register_hint = sorted(
        entry for entry, row in rows.items() if "references peripheral registers" in row["detail"]
    )
    sram_only = sorted(
        entry
        for entry, row in rows.items()
        if row["detail"] == "references SRAM globals"
    )
    if tuple(register_hint) != EXPECTED_REGISTER_HINT_ENTRIES:
        raise ClusterError("census peripheral-register hint set changed")
    if tuple(sram_only) != EXPECTED_SRAM_ONLY_ENTRIES:
        raise ClusterError("census SRAM-globals-only hint set changed")
    for entry in list(EXPECTED_REGISTER_HINT_ENTRIES) + list(EXPECTED_SRAM_ONLY_ENTRIES):
        row = rows[entry]
        if (
            row["bucket"] != "investigation-required-no-evidence"
            or row["evidence"] != "none"
            or row["confidence"] != "none"
        ):
            raise ClusterError(f"census row left the no-evidence bucket: 0x{entry:08X}")
    documented = DOCUMENTED_MSPI_INTERRUPT_CLEAR
    leaf = rows.get(documented["entry"])
    if leaf is None or leaf["detail"] != "no closed-world evidence":
        raise ClusterError("documented am_hal_mspi_interrupt_clear census row changed")
    if (
        int(leaf["body_start"], 16) != documented["entry"]
        or int(leaf["body_end_exclusive"], 16) != documented["end_exclusive"]
    ):
        raise ClusterError("documented am_hal_mspi_interrupt_clear span changed")
    return rows


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze(
    corpus_root: Path,
    census_tsv: Path = CENSUS_FUNCTIONS_TSV,
    ambix_root: Path = AMBIQSUITE,
) -> dict[str, Any]:
    cmsis_path = ambix_root / APOLLO510_H.relative_to(AMBIQSUITE)
    reg_base_path = ambix_root / REG_BASE_H.relative_to(AMBIQSUITE)
    sysctrl_path = ambix_root / SYSCTRL_H.relative_to(AMBIQSUITE)
    for path, expected in (
        (cmsis_path, APOLLO510_H_SHA256),
        (reg_base_path, REG_BASE_H_SHA256),
        (sysctrl_path, SYSCTRL_H_SHA256),
    ):
        if _sha256_bytes(path.read_bytes()) != expected:
            raise ClusterError(f"vendored header identity changed: {path.name}")

    path_module = _load_path_analyzer()
    path_report = path_module.analyze(corpus_root=corpus_root)
    load_base = path_module.LOAD_BASE
    blob = path_module.DEFAULT_IMAGE.read_bytes()

    register_map = build_register_map(
        cmsis_path.read_text(encoding="utf-8"),
        reg_base_path.read_text(encoding="utf-8"),
        sysctrl_path.read_text(encoding="utf-8"),
    )
    classify = make_classifier(register_map)

    cluster_entries = frozenset(EXPECTED_REGISTER_HINT_ENTRIES) | frozenset(
        EXPECTED_SRAM_ONLY_ENTRIES
    )
    logs = path_module.verify_corpus(corpus_root)
    functions, texts = parse_corpus(logs, cluster_entries | {DOCUMENTED_MSPI_INTERRUPT_CLEAR["entry"]})
    census_rows = load_census_rows(census_tsv)

    # Re-validate the documented am_hal_mspi_interrupt_clear cells and span
    # against the authenticated image and corpus.
    documented = DOCUMENTED_MSPI_INTERRUPT_CLEAR
    def image_word(address: int) -> int | None:
        if address % 4 or not (load_base <= address <= load_base + len(blob) - 4):
            return None
        return struct.unpack_from("<I", blob, address - load_base)[0]

    if image_word(documented["magic_cell"]) != documented["magic_value"]:
        raise ClusterError("documented MSPI handle-magic cell changed")
    if image_word(documented["base_cell"]) != documented["base_value"]:
        raise ClusterError("documented MSPI base cell changed")
    leaf = functions.get(documented["entry"])
    if leaf is None or leaf["body_end_inclusive"] + 1 != documented["end_exclusive"]:
        raise ClusterError("documented am_hal_mspi_interrupt_clear is no longer a corpus function")

    anchored: dict[int, dict[str, Any]] = {
        row["entry"]: row for row in path_report["ghidra_correlation"]["functions"]
    }
    anchored_paths = path_report["paths"]

    # Closed-world callers of every cluster entry (corpus tokens, census rules).
    callers: dict[int, set[int]] = {entry: set() for entry in cluster_entries}
    for entry, row in functions.items():
        for target in cluster_entries & row["tokens"]:
            if target != entry:
                callers[target].add(entry)

    def caller_label(caller: int) -> str:
        anchored_row = anchored.get(caller)
        if anchored_row is not None:
            leaves = sorted(
                anchored_paths[index]["relative"].split("\\")[-1]
                for index in anchored_row["path_indexes"]
            )
            return "anchored:" + "|".join(leaves)
        census_row = census_rows.get(caller)
        if census_row is not None:
            return "census:" + census_row["bucket"]
        return "census:anchored-no-path"

    records: list[dict[str, Any]] = []
    for entry in sorted(EXPECTED_REGISTER_HINT_ENTRIES):
        row = functions.get(entry)
        if row is None:
            raise ClusterError(f"cluster entry is no longer a corpus function: 0x{entry:08X}")
        census_row = census_rows[entry]
        body_start = row["body_start"]
        body_end = row["body_end_inclusive"] + 1
        if (
            int(census_row["body_start"], 16) != body_start
            or int(census_row["body_end_exclusive"], 16) != body_end
        ):
            raise ClusterError(f"cluster body range drifted: 0x{entry:08X}")

        code_constants = scan_code_constants(blob, load_base, body_start, body_end)
        text_constants, cell_offsets = scan_text_constants(texts[entry])

        # references: address -> evidence kinds
        references: dict[int, set[str]] = defaultdict(set)
        for value, kinds in code_constants.items():
            if classify(value) is not None:
                references[value] |= kinds
        for value, kinds in text_constants.items():
            if classify(value) is not None:
                references[value] |= kinds
            elif "dat-cell" in kinds and FLASH_LO <= value < FLASH_HI:
                hop = image_word(value)
                if hop is not None and classify(hop) is not None:
                    references[hop] |= {f"{kind}-via-cell" for kind in kinds}
        for cell, offset in cell_offsets:
            base = image_word(cell)
            if base is None or classify(base) is None:
                continue
            block, _base_offset, _name = classify(base)
            register = base + offset
            resolved = classify(register)
            if resolved is not None and resolved[0] == block:
                references[register].add("cell-offset")

        blocks = frozenset(classify(address)[0] for address in references)
        named_registers = frozenset(
            classify(address)[2] for address in references if classify(address)[2]
        )
        callees = {
            token
            for token in functions[entry]["tokens"]
            if token in functions and token != entry
        }
        cluster_callees = sorted(callees & cluster_entries)

        record: dict[str, Any] = {
            "entry": entry,
            "body_start": body_start,
            "body_end_exclusive": body_end,
            "envelope_bytes": int(census_row["envelope_bytes"]),
            "official_opaque_bytes": int(census_row["official_opaque_bytes"]),
            "census_hint": census_row["detail"],
            "references": {
                f"0x{address:08X}": sorted(kinds) for address, kinds in sorted(references.items())
            },
            "blocks": sorted(blocks),
            "callers": sorted(callers[entry]),
            "caller_labels": {caller: caller_label(caller) for caller in sorted(callers[entry])},
            "cluster_callees": cluster_callees,
            "sram_indirect_candidate": False,
        }

        # SRAM-indirect register-write candidate: no validated reference, but
        # the text dereferences a cell whose image content is an SRAM pointer
        # (``*DAT_cell``) and a 0x4xxxxxxx-class constant is staged in a plain
        # local (``var = 0x4xxxxxxx;``) -- a register-style write through a
        # runtime base held in SRAM.  Comparisons, array subscripts, and
        # direct struct-field stores do not qualify.
        if not references:
            text = "\n".join(texts[entry])
            staged = re.search(r"(?m)^\s*[A-Za-z_]\w* = 0x4[0-9a-f]{7};", text)
            if staged:
                for cell in re.findall(r"\*DAT_([0-9a-f]{8})", text):
                    hop = image_word(int(cell, 16))
                    if hop is not None and SRAM_LO <= hop < SRAM_HI:
                        record["sram_indirect_candidate"] = True
                        break
        records.append(record)

    # Attribution rules: deterministic and total over the register-hint set.
    validated = {
        record["entry"] for record in records if record["references"]
    }
    for record in records:
        references = record["references"]
        blocks = frozenset(record["blocks"])
        named = frozenset(
            name
            for address in references
            for name in [classify(int(address, 16))[2]]
            if name
        )
        if not references:
            if record["sram_indirect_candidate"]:
                record.update(
                    family="investigation-required",
                    evidence="sram-indirect-register-candidate",
                    confidence="low",
                    detail="no validated static register reference; writes a "
                    "0x4xxxxxxx-class constant through an SRAM-resolved base "
                    "pointer (runtime register target unknown)",
                )
            # other no-reference functions are classified in the second pass,
            # once the validated and SRAM-indirect sets are final
            continue
        if blocks and blocks <= MSPI_BLOCKS:
            record.update(
                family="ambiqsuite-hal",
                evidence="machine-code-register-access",
                confidence="medium",
                detail="MSPI register block only; shares the authenticated "
                "am_hal_mspi private cells (base 0x40060000, handle magic "
                "0x01BEBEBE) and link-order region with the proven "
                "am_hal_mspi_interrupt_clear leaf [0x004C23DE,0x004C240E); "
                "callers are anchored drv_mx25u25643g.c / drv_mspi_uled_common.c",
            )
            continue
        if blocks <= SYSCTRL_BLOCKS and len(named & POWER_SEQUENCER_REGS) >= 2:
            record.update(
                family="ambiqsuite-hal",
                evidence="machine-code-register-access",
                confidence="medium",
                detail="SIMOBUCK/LDOREG/VREFGEN/PWRSW voltage-sequencer register "
                "signature in the am_hal pwrctrl/spotmgr/sysctrl ton-config "
                "domain (vendored headers only; implementation .c not in the "
                "dependency closure)",
            )
            continue
        if blocks == frozenset({"OTP_INFOC"}):
            record.update(
                family="g2-board-support",
                evidence="decompiled-register-access",
                confidence="low",
                detail="customer OTP_INFOC read helper; called by an anchored "
                "first-party NVDB service",
            )
            continue
        if blocks & INFO_OTP_BLOCKS and blocks <= (INFO_OTP_BLOCKS | SYSCTRL_BLOCKS):
            record.update(
                family="ambiqsuite-hal",
                evidence="machine-code-register-access",
                confidence="low",
                detail="INFO/OTP-INFO trim read with MCUCTRL/PWRCTRL status "
                "registers; am_hal infoc/mram-trim domain; caller chain is "
                "unanchored",
            )
            continue
        if blocks == frozenset({"TIMER"}):
            record.update(
                family="g2-board-support",
                evidence="machine-code-register-access",
                confidence="low",
                detail="fixed-address TIMER15 and global interrupt registers; "
                "absolute timer-15 literals are board-specific (a generic "
                "am_hal_timer translation unit computes bases from a runtime "
                "instance); called by first-party functions",
            )
            continue
        if blocks <= SYSCTRL_BLOCKS:
            record.update(
                family="ambiqsuite-hal",
                evidence="machine-code-register-access",
                confidence="low",
                detail="system-control block access in the am_hal "
                "clkgen/mcuctrl/syspll domain; no board-specific evidence",
            )
            continue
        record.update(
            family="g2-board-support",
            evidence="machine-code-register-access",
            confidence="low",
            detail="cross-domain register sweep spanning system-control and "
            "device blocks; consistent with board clock/power configuration; "
            "an Ambiq clock-manager origin is not excludable",
        )

    # Second pass for no-reference functions: call-topology class needs the
    # finalized validated set plus SRAM-indirect candidates.
    indirect = {
        record["entry"] for record in records if record["sram_indirect_candidate"]
    }
    for record in records:
        if record["references"]:
            record.pop("_topology", None)
            continue
        if record["sram_indirect_candidate"]:
            continue
        topology = [
            callee
            for callee in record["cluster_callees"]
            if callee in validated or callee in indirect
        ]
        if topology:
            record.update(
                family="investigation-required",
                evidence="call-topology-into-cluster",
                confidence="low",
                detail="no validated register reference; calls cluster "
                "function(s) "
                + ",".join(f"0x{callee:08X}" for callee in topology)
                + "; census hint token is a constant collision",
            )
        else:
            record.update(
                family="investigation-required",
                evidence="no-register-evidence",
                confidence="none",
                detail="census peripheral-range hint token(s) fail "
                "register-map validation (float/bitmask constant collision)",
            )
        record.pop("_topology", None)

    for record in records:
        expected = EXPECTED_ATTRIBUTION.get(record["entry"])
        actual = (record["family"], record["evidence"], record["confidence"])
        if expected is None or expected != actual:
            raise ClusterError(
                f"attribution drift at 0x{record['entry']:08X}: {actual} != {expected}"
            )
        summary = EXPECTED_REFERENCE_SUMMARY.get(record["entry"])
        if summary is not None:
            blocks, count = summary
            if frozenset(record["blocks"]) != blocks or len(record["references"]) != count:
                raise ClusterError(
                    f"validated reference census drift at 0x{record['entry']:08X}"
                )
        elif record["references"]:
            raise ClusterError(
                f"unexpected validated references at 0x{record['entry']:08X}"
            )

    # Secondary listing: SRAM-globals-only functions (cheap enumeration).
    sram_records: list[dict[str, Any]] = []
    for entry in EXPECTED_SRAM_ONLY_ENTRIES:
        row = functions[entry]
        census_row = census_rows[entry]
        code_constants = scan_code_constants(
            blob, load_base, row["body_start"], row["body_end_inclusive"] + 1
        )
        text_constants, _offsets = scan_text_constants(texts[entry])
        sram_refs: set[int] = set()
        for value in code_constants:
            if SRAM_LO <= value < SRAM_HI and value % 4 == 0:
                sram_refs.add(value)
        for value, kinds in text_constants.items():
            if SRAM_LO <= value < SRAM_HI and value % 4 == 0:
                sram_refs.add(value)
            elif "dat-cell" in kinds and FLASH_LO <= value < FLASH_HI:
                hop = image_word(value)
                if hop is not None and SRAM_LO <= hop < SRAM_HI and hop % 4 == 0:
                    sram_refs.add(hop)
        sram_records.append(
            {
                "entry": entry,
                "body_start": row["body_start"],
                "body_end_exclusive": row["body_end_inclusive"] + 1,
                "envelope_bytes": int(census_row["envelope_bytes"]),
                "official_opaque_bytes": int(census_row["official_opaque_bytes"]),
                "sram_references": sorted(sram_refs),
                "family": "investigation-required",
                "evidence": "sram-globals-only-listing",
                "confidence": "none",
                "detail": (
                    f"{len(sram_refs)} validated SRAM-global address reference(s); "
                    "secondary listing, no peripheral-register evidence evaluated"
                    if sram_refs
                    else "no validated SRAM-global address reference; census "
                    "SRAM hint token is a constant collision (e.g. 0x20000000 "
                    "bit/region tag)"
                ),
            }
        )

    families: dict[str, dict[str, Any]] = {}
    for family in FAMILIES:
        families[family] = {"functions": 0, "envelope_bytes": 0, "official_opaque_bytes": 0}
    for record in records:
        bucket = families[record["family"]]
        bucket["functions"] += 1
        bucket["envelope_bytes"] += record["envelope_bytes"]
        bucket["official_opaque_bytes"] += record["official_opaque_bytes"]

    reconciliation = {
        "census_register_hint_functions": len(EXPECTED_REGISTER_HINT_ENTRIES),
        "census_sram_only_functions": len(EXPECTED_SRAM_ONLY_ENTRIES),
        "census_hardware_hint_functions": len(EXPECTED_REGISTER_HINT_ENTRIES)
        + len(EXPECTED_SRAM_ONLY_ENTRIES),
        "validated_register_functions": len(validated),
        "validated_register_references": sum(len(record["references"]) for record in records),
        "sram_indirect_candidates": len(indirect),
        "call_topology_members": sum(
            1 for record in records if record["evidence"] == "call-topology-into-cluster"
        ),
        "hint_collision_functions": sum(
            1 for record in records if record["evidence"] == "no-register-evidence"
        ),
    }

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no signing, flashing, erase, or hardware operation",
        "target": "official G2 s200_v2.2.6.10 Apollo main",
        "inputs": {
            "image_sha256": path_report["image"]["sha256"],
            "ghidra_sha256sums_sha256": path_report["ghidra_correlation"]["corpus"]["sha256sums_sha256"],
            "census_functions_tsv_sha256": _sha256_bytes(census_tsv.read_bytes()),
            "apollo510_h_sha256": APOLLO510_H_SHA256,
            "am_reg_base_addresses_h_sha256": REG_BASE_H_SHA256,
            "am_hal_sysctrl_h_sha256": SYSCTRL_H_SHA256,
        },
        "documented_mspi_leaf": {
            "entry": f"0x{documented['entry']:08X}",
            "end_exclusive": f"0x{documented['end_exclusive']:08X}",
            "source": documented["source"],
        },
        "reconciliation": reconciliation,
        "families": families,
        "functions": records,
        "sram_only_functions": sram_records,
    }


MAP_TSV_HEADER = (
    "entry\tbody_start\tbody_end_exclusive\tenvelope_bytes\tofficial_opaque_bytes\t"
    "census_hint\tblocks\tregisters\tcallers\tfamily\tevidence\tconfidence\tdetail"
)


def _format_registers(record: dict[str, Any], classify) -> str:
    parts = []
    for address_hex, kinds in record["references"].items():
        block, offset, name = classify(int(address_hex, 16))
        label = f"{block}+0x{offset:03x}"
        if name:
            label += f":{name}"
        parts.append(f"{label}({'|'.join(kinds)})")
    return ";".join(parts) if parts else "-"


def map_tsv(report: dict[str, Any], classify) -> str:
    lines = [
        "# G2 Apollo peripheral-register cluster attribution audit; regenerated by "
        "tools/analyze_g2_peripheral_register_cluster.py",
        MAP_TSV_HEADER,
    ]
    for record in report["functions"]:
        caller_parts = [
            f"0x{caller:08X}:{record['caller_labels'][caller]}"
            for caller in record["callers"]
        ]
        if len(caller_parts) > 8:
            shown = ";".join(caller_parts[:8]) + f";+{len(caller_parts) - 8} more"
        else:
            shown = ";".join(caller_parts)
        callers = shown or "-"
        lines.append(
            "\t".join(
                (
                    f"0x{record['entry']:08X}",
                    f"0x{record['body_start']:08X}",
                    f"0x{record['body_end_exclusive']:08X}",
                    str(record["envelope_bytes"]),
                    str(record["official_opaque_bytes"]),
                    record["census_hint"],
                    "|".join(record["blocks"]) or "-",
                    _format_registers(record, classify),
                    callers,
                    record["family"],
                    record["evidence"],
                    record["confidence"],
                    record["detail"],
                )
            )
        )
    for record in report["sram_only_functions"]:
        refs = (
            ";".join(f"0x{address:08X}" for address in record["sram_references"]) or "-"
        )
        lines.append(
            "\t".join(
                (
                    f"0x{record['entry']:08X}",
                    f"0x{record['body_start']:08X}",
                    f"0x{record['body_end_exclusive']:08X}",
                    str(record["envelope_bytes"]),
                    str(record["official_opaque_bytes"]),
                    "references SRAM globals",
                    "-",
                    refs,
                    "-",
                    record["family"],
                    record["evidence"],
                    record["confidence"],
                    record["detail"],
                )
            )
        )
    return "\n".join(lines) + "\n"


def summary_json(report: dict[str, Any]) -> str:
    summary = {
        key: report[key]
        for key in (
            "schema_version",
            "analysis_mode",
            "target",
            "inputs",
            "documented_mspi_leaf",
            "reconciliation",
            "families",
        )
    }
    return json.dumps(summary, indent=2, sort_keys=True) + "\n"


def _text(report: dict[str, Any]) -> str:
    reconciliation = report["reconciliation"]
    lines = [
        "G2 Apollo peripheral-register cluster audit: PASS",
        f"  census register-hint functions: {reconciliation['census_register_hint_functions']}",
        f"  validated register functions: {reconciliation['validated_register_functions']}",
        f"  validated register references: {reconciliation['validated_register_references']}",
        f"  hint collisions (no register evidence): {reconciliation['hint_collision_functions']}",
        f"  SRAM-only secondary listing: {reconciliation['census_sram_only_functions']}",
        "  families:",
    ]
    for family, bucket in report["families"].items():
        lines.append(
            f"    {family}: {bucket['functions']} functions, "
            f"{bucket['envelope_bytes']} envelope bytes, "
            f"{bucket['official_opaque_bytes']} official bytes"
        )
    lines.append("hardware/flash operations: none")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--census-tsv", type=Path, default=CENSUS_FUNCTIONS_TSV)
    parser.add_argument("--ambiqsuite", type=Path, default=AMBIQSUITE)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--write-manifests",
        type=Path,
        metavar="DIRECTORY",
        help="write g2-peripheral-register-cluster-map.tsv and -summary.json into DIRECTORY",
    )
    args = parser.parse_args()
    report = analyze(args.ghidra_corpus, census_tsv=args.census_tsv, ambix_root=args.ambiqsuite)
    if args.write_manifests is not None:
        register_map = build_register_map(
            (args.ambiqsuite / APOLLO510_H.relative_to(AMBIQSUITE)).read_text(encoding="utf-8"),
            (args.ambiqsuite / REG_BASE_H.relative_to(AMBIQSUITE)).read_text(encoding="utf-8"),
            (args.ambiqsuite / SYSCTRL_H.relative_to(AMBIQSUITE)).read_text(encoding="utf-8"),
        )
        classify = make_classifier(register_map)
        directory = args.write_manifests
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "g2-peripheral-register-cluster-map.tsv").write_text(
            map_tsv(report, classify), encoding="utf-8"
        )
        (directory / "g2-peripheral-register-cluster-summary.json").write_text(
            summary_json(report), encoding="utf-8"
        )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
