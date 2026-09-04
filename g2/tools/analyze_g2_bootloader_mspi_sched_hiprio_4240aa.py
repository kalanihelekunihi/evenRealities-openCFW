#!/usr/bin/env python3
"""Authenticate and verify the G2 bootloader sched_hiprio source closure."""

from __future__ import annotations

import argparse
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
SOURCE = ROOT / "research/admission/bootloader_mspi_sched_hiprio_4240aa/runtime_bootloader_mspi_sched_hiprio_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = SOURCE.parent / "host_fixture.c"
PRODUCTION = ROOT / "components/bootloader/core_overlay/runtime_mspi_sched_hiprio_4240aa.c"
BOUNDARY = ROOT / "tools/manifests/g2-bootloader-mspi-sched-hiprio-4240aa.tsv"
PROVENANCE = ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json"
UPSTREAM = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"

RUN_BASE = 0x00410000
ENTRY = 0x004240AA
END = 0x00424120
STOCK_SHA = "dfbd51c61eba1ea51418a1faeaaa99df5aebb0ea900ed157a0c3a55a7b28d144"
UNRELOCATED_SHA = "8a686489b87dfe77a19e92ea48ec29bd7fe728a8f7d54a94d4f44939520a83e0"
CALLERS = (0x00425F92,)
RELOCATIONS = (
    (8, "open_cfw_bootloader_critical_save_41b8ec", 0x0041B8EC),
    (40, "open_cfw_bootloader_mspi_cq_pause_423fb8", 0x00423FB8),
    (100, "open_cfw_bootloader_mspi_program_dma_42403e", 0x0042403E),
)
INPUT_PINS = {
    SOURCE: (3466, "5673d0726217a52cf9602a28ff06582a5b05262b56cc3a3bc330eedc08d31c3c"),
    HEADER: (1675, "e35cb68ca61f8f7585f24715120d2b3c61ba91b6f244039110d46cd50241b0b0"),
    FIXTURE: (4737, "811726b83d4093c8b650003169ee7e10fc8ab1f115fa00bc879a3c812f99c7b2"),
    PRODUCTION: (1767, "19aa8b8b678fdd733e45d04d53fa4738e38576e8c530e507279f935cf4c44af7"),
    BOUNDARY: (2226, "ef075c1eeefc40ba01f319c00aba2d60f4395f89344d2c4ee45958b73814fed2"),
}
FLAGS = (
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
        sections, ".text.open_cfw_bootloader_mspi_sched_hiprio_4240aa")
    body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
    symtab = apollo_overlay.section_named(sections, ".symtab")
    strtab = sections[int(symtab["link"])]
    strings = data[int(strtab["offset"]):int(strtab["offset"]) + int(strtab["size"])]
    symbols: list[tuple[str, tuple[int, ...]]] = []
    for index in range(int(symtab["size"]) // 16):
        fields = struct.unpack_from("<IIIBBH", data, int(symtab["offset"]) + index * 16)
        symbols.append((apollo_overlay.elf_string(strings, fields[0], "symbol"), fields))
    relocations: list[tuple[int, int, str]] = []
    for relsec in sections:
        if int(relsec["type"]) != 9 or int(relsec["info"]) != int(section["index"]):
            continue
        for index in range(int(relsec["size"]) // 8):
            offset, info = struct.unpack_from("<II", data, int(relsec["offset"]) + index * 8)
            relocations.append((offset, info & 0xFF, symbols[info >> 8][0]))
    return body, relocations


def compile_profiles(stock: bytes) -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    expected_relocations = [(offset, 10, symbol)
                            for offset, symbol, _ in RELOCATIONS]
    with tempfile.TemporaryDirectory(prefix="open-cfw-sched-hiprio-audit-") as raw:
        for profile, (compiler, version_prefix) in PROFILES.items():
            require(compiler.is_file(), f"reviewed {profile} compiler unavailable")
            version = subprocess.run([str(compiler), "--version"], check=True,
                                     capture_output=True, text=True).stdout.splitlines()[0]
            require(version.startswith(version_prefix),
                    f"reviewed {profile} compiler identity changed")
            output = Path(raw) / f"{profile}.o"
            subprocess.run([str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(output)],
                           check=True, capture_output=True, text=True)
            body, relocations = extract_function(output)
            require((len(body), digest(body)) == (118, UNRELOCATED_SHA),
                    f"{profile} unrelocated body changed")
            require(relocations == expected_relocations,
                    f"{profile} relocation graph changed")
            linked = bytearray(body)
            for offset, _, target in RELOCATIONS:
                linked[offset:offset + 4] = apollo_overlay.encode_thumb_branch(
                    ENTRY + offset, target, link=True)
            require(bytes(linked) == stock, f"{profile} linked body is not exact stock")
            reports[profile] = {
                "version": version, "body_size": len(body),
                "unrelocated_sha256": digest(body), "linked_sha256": digest(linked),
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
    require((len(stock), digest(stock)) == (118, STOCK_SHA),
            "stock sched_hiprio body changed")
    callers = tuple(address for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
                    if decode_bl(image, address) == ENTRY)
    require(callers == CALLERS, "sched_hiprio caller topology changed")
    for offset, _, target in RELOCATIONS:
        require(decode_bl(image, ENTRY + offset) == target,
                f"sched_hiprio call at +{offset} changed")
    require(struct.unpack_from("<I", image, 0x00424BD8 - RUN_BASE)[0] == 0x40060000,
            "sched_hiprio MSPI base literal changed")
    successor = image[END - RUN_BASE:0x0042488E - RUN_BASE]
    require((len(successor), digest(successor)) ==
            (1902, "3b95c5af6c3c2140cc4e1522a1f284ae31825e4e35ae6c2427e0edba41774818"),
            "mspi_device_configure successor changed")
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    require(provenance["license"] == "BSD-3-Clause", "upstream license changed")
    upstream = UPSTREAM.read_text(encoding="utf-8")
    for token in ("sched_hiprio(am_hal_mspi_state_t *pMSPIState, uint32_t numTrans)",
                  "ui32NumHPEntries += numTrans", "mspi_cq_pause(pMSPIState)",
                  "AM_HAL_MSPI_INT_DMACMP", "program_dma(pMSPIState)"):
        require(token in upstream, f"upstream identity token changed: {token}")
    profiles = compile_profiles(stock)

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    leaf = next(row for row in overlay["in_place_leaves"]
                if row["function"] == "open_cfw_bootloader_mspi_sched_hiprio_4240aa")
    require((leaf["runtime_address"], leaf["expected"]["size"],
             leaf["expected"]["sha256"], leaf["source"]["license"])
            == (ENTRY, 118, STOCK_SHA, "BSD-3-Clause"),
            "production sched_hiprio overlay registration changed")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    regions = manifest["component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {row["name"]: row for row in regions}
    source_name = "bootloader_mspi_sched_hiprio_4240aa_source_in_place"
    successor_name = "bootloader_mspi_device_configure_424120_source_in_place"
    require(source_name in by_name, "scheduler production region disappeared")
    require(successor_name in by_name, "device-configure successor disappeared")
    source_region = by_name[source_name]
    successor = by_name[successor_name]
    require((source_region["target_address"], source_region["size"],
             source_region["address_status"]) == (ENTRY, 118, "source_compiled"),
            "production sched_hiprio manifest registration changed")
    require(
        (successor["target_address"], successor["size"],
         successor["address_status"])
        == (END, 284, "source_compiled"),
        "device-configure source-successor ownership changed",
    )
    with tempfile.TemporaryDirectory(prefix="open-cfw-sched-hiprio-component-") as raw:
        subprocess.run(["python3", str(BUILDER), "--output-dir", raw], cwd=ROOT,
                       check=True, capture_output=True, text=True)
        report = json.loads((Path(raw) / "build-report.json").read_text(encoding="utf-8"))
    component = report["component"]
    require(
        component["source_owned_bytes"] + component["opaque_base_bytes"]
        + component["generated_patch_site_bytes"]
        + component["generated_alignment_bytes"] == component["size"],
        "production sched_hiprio byte conservation changed",
    )
    require(component["source_owned_in_place_bytes"] <= component["source_owned_bytes"],
            "production sched_hiprio in-place accounting changed")
    built = next(row for row in report["in_place_leaves"]
                 if row["extraction"]["function"] ==
                 "open_cfw_bootloader_mspi_sched_hiprio_4240aa")
    require((built["extraction"]["sha256"], built["placement"]["stock_sha256"])
            == (STOCK_SHA, STOCK_SHA), "production sched_hiprio placement changed")
    return {
        "status": "production-routed-exact-dual-profile-source / hardware-validation-blocked-by-unavailable-physical-evidence",
        "stock": {"start": ENTRY, "end": END, "bytes": len(stock), "sha256": STOCK_SHA},
        "identity": {"function": "sched_hiprio",
                     "upstream_commit": provenance["upstream"]["selected_commit"],
                     "license": "BSD-3-Clause"},
        "callers": list(callers),
        "abi": {"module_offset": 4, "transaction_interrupt_offset": 0x24,
                "high_priority_active_offset": 0x83C,
                "high_priority_entries_offset": 0x840,
                "mspi0_base": 0x40060000, "module_stride": 0x1000,
                "interrupt_enable_offset": 0x200,
                "interrupt_clear_offset": 0x208, "dma_complete_bit": 0x40},
        "profiles": profiles,
        "production": {"routed": True,
                       "source_owned_bytes": component["source_owned_bytes"],
                       "retained_official_bytes": component["opaque_base_bytes"],
                       "next_frontier": successor["target_address"]},
        "next_frontier": {"start": END, "end": 0x0042488E,
                          "identity": "mspi_device_configure", "bytes": 1902,
                          "source_compiled_bytes": 284,
                          "retained_unreachable_tail_bytes": 1618,
                          "status": "source-compiled-with-retained-unreachable-tail"},
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_gate": {"blocking_condition":
                          "directed hardware testing is blocked by unavailable physical evidence",
                          "required_future_evidence":
                          "authorized PRIMASK, command-queue, DMA, MMIO, interrupt, concurrency, and cold-boot qualification"},
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Bootloader sched_hiprio 0x4240aa: production-routed exact source")
        print("  next sequential frontier: 0x424120 (mspi_device_configure)")
        print("  physical validation: blocked by unavailable physical evidence")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader sched_hiprio audit failed: {exc}")
