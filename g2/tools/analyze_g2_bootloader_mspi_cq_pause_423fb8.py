#!/usr/bin/env python3
"""Authenticate the software-only G2 bootloader mspi_cq_pause candidate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
from typing import Any

import apollo_overlay


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "research/admission/bootloader_mspi_cq_pause_423fb8/runtime_bootloader_mspi_cq_pause_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = SOURCE.parent / "host_fixture.c"
MANIFEST = ROOT / "tools/manifests/g2-bootloader-mspi-cq-pause-423fb8.tsv"
PROVENANCE = ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json"
UPSTREAM = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
CMSIS = ROOT / "third_party/ambiqsuite-apollo510/CMSIS/AmbiqMicro/Include/apollo510.h"
CORE_OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
COMPONENT_BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"

RUN_BASE = 0x00410000
ENTRY = 0x00423FB8
END = 0x0042403E
STOCK_SHA = "ff20411c8e4283f16d82cb8373e95004d648e4c03d151ba89bf43ff7d58a2794"
UNRELOCATED_SHA = "66e8cd3f9313756950f835406c64e621358d7f0bcc505cacd1666fb7a5a4339f"
CALLERS = (0x004240D2, 0x00425C60, 0x00425CC8)
RELOCATIONS = (
    (0x2A, "open_cfw_bootloader_retained_delay_us_41d1c0", 0x0041D1C0),
    (0x7C, "open_cfw_bootloader_retained_status_check_41d246", 0x0041D246),
)
INPUT_PINS = {
    SOURCE: (3731, "72710cc8ea51529346089b1bd3423a4a8512ad1b4d665f5432e65f905a7bd406"),
    HEADER: (1481, "5edb1867347fb9f4ede3b2dfa97462bf95969944033ead74f9c25897620b549c"),
    FIXTURE: (3250, "763c95f302ab4b029098168887ba6a392e11b829ab195efa1fb8424b63830b1b"),
    MANIFEST: (1985, "d270f41cbacc91ee6129448dad11d75bcabef04578033428a5d75d39209706a2"),
}
TARGET_FLAGS = (
    "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident",
)
PROFILES = {
    "apple-clang": (Path("/usr/bin/clang"), "Apple clang version 21.0.0"),
    "linux-clang": (Path("/opt/homebrew/opt/llvm@22/bin/clang"),
                    "Homebrew clang version 22.1.8"),
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_bl(image: bytes, address: int) -> int | None:
    offset = address - RUN_BASE
    if offset < 0 or offset + 4 > len(image):
        return None
    first, second = struct.unpack_from("<HH", image, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = first >> 10 & 1
    i1 = (~((second >> 13 & 1) ^ sign)) & 1
    i2 = (~((second >> 11 & 1) ^ sign)) & 1
    immediate = (sign << 24 | i1 << 23 | i2 << 22 |
                 (first & 0x3FF) << 12 | (second & 0x7FF) << 1)
    if sign:
        immediate -= 1 << 25
    return address + 4 + immediate


def extract_function(path: Path) -> tuple[bytes, list[tuple[int, int, str]]]:
    data, sections = apollo_overlay.parse_elf32(path)
    section = apollo_overlay.section_named(
        sections, ".text.open_cfw_bootloader_mspi_cq_pause_423fb8")
    body = data[int(section["offset"]):
                int(section["offset"]) + int(section["size"])]
    symtab = apollo_overlay.section_named(sections, ".symtab")
    strtab = sections[int(symtab["link"])]
    strings = data[int(strtab["offset"]):
                   int(strtab["offset"]) + int(strtab["size"])]
    symbols: list[tuple[str, tuple[int, ...]]] = []
    for index in range(int(symtab["size"]) // 16):
        fields = struct.unpack_from(
            "<IIIBBH", data, int(symtab["offset"]) + index * 16)
        symbols.append((apollo_overlay.elf_string(strings, fields[0], "symbol"),
                        fields))
    relocations: list[tuple[int, int, str]] = []
    for relsec in sections:
        if int(relsec["type"]) != 9 or int(relsec["info"]) != int(section["index"]):
            continue
        for index in range(int(relsec["size"]) // 8):
            offset, info = struct.unpack_from(
                "<II", data, int(relsec["offset"]) + index * 8)
            relocations.append((offset, info & 0xFF, symbols[info >> 8][0]))
    return body, relocations


def compile_profiles(stock: bytes) -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    with tempfile.TemporaryDirectory(prefix="open-cfw-cq-pause-audit-") as td:
        for profile, (compiler, version_prefix) in PROFILES.items():
            require(compiler.is_file(), f"reviewed {profile} compiler is unavailable")
            version = subprocess.run(
                [str(compiler), "--version"], check=True, capture_output=True,
                text=True).stdout.splitlines()[0]
            require(version.startswith(version_prefix),
                    f"reviewed {profile} compiler identity changed")
            output = Path(td) / f"{profile}.o"
            subprocess.run(
                [str(compiler), *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(output)],
                check=True, capture_output=True, text=True)
            body, relocations = extract_function(output)
            require((len(body), digest(body)) == (134, UNRELOCATED_SHA),
                    f"{profile} unrelocated body changed")
            require(relocations == [(offset, 10, symbol)
                                    for offset, symbol, _target in RELOCATIONS],
                    f"{profile} relocation graph changed")
            linked = bytearray(body)
            for offset, _symbol, target in RELOCATIONS:
                linked[offset:offset + 4] = apollo_overlay.encode_thumb_branch(
                    ENTRY + offset, target, link=True)
            require(bytes(linked) == stock,
                    f"{profile} linked body is not exact stock")
            reports[profile] = {
                "version": version, "object_size": output.stat().st_size,
                "object_sha256": digest(output.read_bytes()),
                "body_size": len(body), "unrelocated_sha256": digest(body),
                "linked_sha256": digest(linked),
                "relocations": relocations,
            }
    return reports


def audit() -> dict[str, Any]:
    for path, expected in INPUT_PINS.items():
        data = path.read_bytes()
        require((len(data), digest(data)) == expected,
                f"input pin changed: {path.relative_to(ROOT)}")
    image = OFFICIAL.read_bytes()
    stock = image[ENTRY - RUN_BASE:END - RUN_BASE]
    require((len(stock), digest(stock)) == (134, STOCK_SHA),
            "stock mspi_cq_pause body changed")
    callers = tuple(address for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
                    if decode_bl(image, address) == ENTRY)
    require(callers == CALLERS, "mspi_cq_pause direct callers changed")
    outgoing = tuple((address, decode_bl(image, address))
                     for address in range(ENTRY, END, 2)
                     if decode_bl(image, address) is not None)
    require(outgoing == ((ENTRY + 0x2A, 0x0041D1C0),
                         (ENTRY + 0x7C, 0x0041D246)),
            "mspi_cq_pause provider calls changed")
    require(struct.unpack_from("<II", image, 0x00424BD4 - RUN_BASE) ==
            (100000, 0x40060000), "pause-limit/MSPI-base literals changed")
    successor = image[0x0042403E - RUN_BASE:0x004240AA - RUN_BASE]
    require((len(successor), digest(successor)) ==
            (108, "d075d73aba138735bc9229bcf8672cb6a1c2fadec21985d2159043534ad130e1"),
            "program_dma successor changed")

    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    require(provenance["license"] == "BSD-3-Clause", "upstream license changed")
    require(provenance["upstream"]["selected_commit"] ==
            "5efc0228528a8adce5eae0d226fac85d2551eb3b",
            "AmbiqSuite commit changed")
    upstream = UPSTREAM.read_text(encoding="utf-8")
    for token in ("mspi_cq_pause(am_hal_mspi_state_t *pMSPIState)",
                  "AM_HAL_MSPI_MAX_PAUSE_DELAY", "AM_HAL_MSPI_SC_PAUSE_CQ",
                  "am_hal_delay_us_status_check"):
        require(token in upstream, f"upstream identity token changed: {token}")
    require("#define MSPI0_BASE" in CMSIS.read_text(encoding="utf-8"),
            "authenticated CMSIS MSPI0 base definition missing")
    profiles = compile_profiles(stock)
    config = json.loads(CORE_OVERLAY.read_text(encoding="utf-8"))
    leaf = next(row for row in config["in_place_leaves"]
                if row["function"] == "open_cfw_bootloader_mspi_cq_pause_423fb8")
    require((leaf["runtime_address"], leaf["expected"]["size"],
             leaf["expected"]["sha256"], leaf["source"]["license"])
            == (ENTRY, 134, STOCK_SHA, "BSD-3-Clause"),
            "production CQ-pause overlay registration changed")
    core = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
    regions = core["component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {row["name"]: row for row in regions}
    source_name = "bootloader_mspi_cq_pause_423fb8_source_in_place"
    successor_name = "bootloader_mspi_program_dma_42403e_source_in_place"
    require(source_name in by_name, "CQ-pause production region disappeared")
    require(successor_name in by_name, "program-DMA successor region disappeared")
    source_region = by_name[source_name]
    successor = by_name[successor_name]
    require((source_region["target_address"], source_region["size"],
             source_region["address_status"])
            == (ENTRY, 134, "source_compiled"),
            "production CQ-pause manifest registration changed")
    require(
        (successor["target_address"], successor["size"],
         successor["address_status"])
        == (END, 108, "source_compiled"),
        "program-DMA local successor ownership changed",
    )
    with tempfile.TemporaryDirectory(prefix="open-cfw-cq-pause-component-") as td:
        subprocess.run(
            ["python3", str(COMPONENT_BUILDER), "--output-dir", td],
            cwd=ROOT, check=True, capture_output=True, text=True)
        component_report = json.loads(
            (Path(td) / "build-report.json").read_text(encoding="utf-8"))
    component = component_report["component"]
    require(
        component["source_owned_bytes"] + component["opaque_base_bytes"]
        + component["generated_patch_site_bytes"]
        + component["generated_alignment_bytes"] == component["size"],
        "production CQ-pause component byte conservation changed",
    )
    require(component["source_owned_in_place_bytes"] <= component["source_owned_bytes"],
            "production CQ-pause in-place accounting changed")
    built_leaf = next(
        row for row in component_report["in_place_leaves"]
        if row["extraction"]["function"] ==
        "open_cfw_bootloader_mspi_cq_pause_423fb8")
    require((built_leaf["extraction"]["sha256"],
             built_leaf["placement"]["stock_sha256"])
            == (STOCK_SHA, STOCK_SHA),
            "production CQ-pause linked placement changed")
    return {
        "status": "production-routed-exact-dual-profile-source",
        "stock": {"start": ENTRY, "end": END, "bytes": len(stock),
                  "sha256": STOCK_SHA},
        "identity": {"function": "mspi_cq_pause",
                     "upstream_commit": provenance["upstream"]["selected_commit"],
                     "license": "BSD-3-Clause"},
        "abi": {"module_offset": 4, "mspi0_base": 0x40060000,
                "module_stride": 0x1000, "pause_limit": 100000,
                "timeout_status": 4, "cqcfg_offset": 0x2A0,
                "cqstat_offset": 0x2AC, "cqsetclear_offset": 0x2B4,
                "cqpause_offset": 0x2B8, "dmastat_offset": 0x104},
        "callers": list(callers),
        "providers": [{"address": target, "symbol": symbol,
                       "binary_redistribution": "unresolved"}
                      for _offset, symbol, target in RELOCATIONS],
        "profiles": profiles,
        "production": {"routed": True,
                       "source_owned_bytes": component["source_owned_bytes"],
                       "retained_official_bytes": component["opaque_base_bytes"],
                       "next_frontier": successor["target_address"]},
        "next_frontier": {"start": 0x0042403E, "end": 0x004240AA,
                          "identity": "program_dma", "bytes": 108},
        "hardware_validation": "deferred by project direction",
        "hardware_gate": {"required_future_evidence":
                          "authorized CQ pause/timeout, DMA-idle, MMIO, concurrency, and cold-boot qualification"},
        "hardware_operations": [],
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Bootloader mspi_cq_pause 0x423fb8: production-routed exact source")
        print("  current sequential frontier: 0x424120 (add_hp_transaction)")
        print("  physical validation: deferred by project direction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
