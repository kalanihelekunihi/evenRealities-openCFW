#!/usr/bin/env python3
"""Authenticate and verify the G2 bootloader program_dma source closure."""

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
SOURCE = ROOT / "research/admission/bootloader_mspi_program_dma_42403e/runtime_bootloader_mspi_program_dma_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = SOURCE.parent / "host_fixture.c"
PRODUCTION = ROOT / "components/bootloader/core_overlay/runtime_mspi_program_dma_42403e.c"
BOUNDARY = ROOT / "tools/manifests/g2-bootloader-mspi-program-dma-42403e.tsv"
PROVENANCE = ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json"
UPSTREAM = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"

RUN_BASE = 0x00410000
ENTRY = 0x0042403E
END = 0x004240AA
STOCK_SHA = "d075d73aba138735bc9229bcf8672cb6a1c2fadec21985d2159043534ad130e1"
UNRELOCATED_SHA = "96f36a90d1f35ecee3a6a94eac7f4bf8bdda10b5db9da66949c335b84770f367"
CALLERS = (0x0042410E, 0x00426620)
RELOCATION = (42, "open_cfw_bootloader_mode_enable_route_4222f0", 0x004222F0)
INPUT_PINS = {
    SOURCE: (3270, "4fd56749aa5ef6b2daf00fc2019fbbf1d89ea00e78cd414a5193953f606e8d6f"),
    HEADER: (1554, "cbf3bd6097abf87d71d84ec6cbaa1cec12a90912cfce3412290a53495ff1fa48"),
    FIXTURE: (2535, "0985ff5d155edc22c369c9e209133a95d3d13aef74a61bc087bdb288165d534e"),
    PRODUCTION: (1458, "5b3d0246fa1fca6222cd0677cc02f7a96a87bab6dbb43808901f0162be414e06"),
    BOUNDARY: (2005, "96ecf260299300434a3aafccad25488984ca62b8c026b20823ba990a455356e5"),
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
        sections, ".text.open_cfw_bootloader_mspi_program_dma_42403e")
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
    with tempfile.TemporaryDirectory(prefix="open-cfw-program-dma-audit-") as raw:
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
            require((len(body), digest(body)) == (108, UNRELOCATED_SHA),
                    f"{profile} unrelocated body changed")
            require(relocations == [(RELOCATION[0], 10, RELOCATION[1])],
                    f"{profile} relocation graph changed")
            linked = bytearray(body)
            linked[RELOCATION[0]:RELOCATION[0] + 4] = apollo_overlay.encode_thumb_branch(
                ENTRY + RELOCATION[0], RELOCATION[2], link=True)
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
    require((len(stock), digest(stock)) == (108, STOCK_SHA),
            "stock program_dma body changed")
    callers = tuple(address for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
                    if decode_bl(image, address) == ENTRY)
    require(callers == CALLERS, "program_dma caller topology changed")
    require(decode_bl(image, ENTRY + RELOCATION[0]) == RELOCATION[2],
            "program_dma clock-provider call changed")
    require(struct.unpack_from("<I", image, 0x00424BD8 - RUN_BASE)[0] == 0x40060000,
            "program_dma MSPI base literal changed")
    successor = image[END - RUN_BASE:0x00424120 - RUN_BASE]
    require((len(successor), digest(successor)) ==
            (118, "dfbd51c61eba1ea51418a1faeaaa99df5aebb0ea900ed157a0c3a55a7b28d144"),
            "sched_hiprio successor changed")
    residual = image[END - RUN_BASE:0x00426506 - RUN_BASE]
    require((len(residual), digest(residual)) ==
            (9308, "d6ae4b18a13d3806c116248ace7c7d3b6d6ebc6de288b3a327cd7226e87a4fc9"),
            "residual official frontier changed")

    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    require(provenance["license"] == "BSD-3-Clause", "upstream license changed")
    upstream = UPSTREAM.read_text(encoding="utf-8")
    for token in ("program_dma(void *pHandle)",
                  "ui32LastHPIdxProcessed", "ui32MaxHPTransactions",
                  "pHPTransactions", "DMATARGADDR", "DMATOTCOUNT"):
        require(token in upstream, f"upstream identity token changed: {token}")
    profiles = compile_profiles(stock)

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    leaf = next(row for row in overlay["in_place_leaves"]
                if row["function"] == "open_cfw_bootloader_mspi_program_dma_42403e")
    require((leaf["runtime_address"], leaf["expected"]["size"],
             leaf["expected"]["sha256"], leaf["source"]["license"])
            == (ENTRY, 108, STOCK_SHA, "BSD-3-Clause"),
            "production program_dma overlay registration changed")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    regions = manifest["component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {row["name"]: row for row in regions}
    source_name = "bootloader_mspi_program_dma_42403e_source_in_place"
    successor_name = "bootloader_mspi_sched_hiprio_4240aa_source_in_place"
    require(source_name in by_name, "program-DMA production region disappeared")
    require(successor_name in by_name, "high-priority scheduler successor disappeared")
    source_region = by_name[source_name]
    successor = by_name[successor_name]
    require((source_region["target_address"], source_region["size"],
             source_region["address_status"]) == (ENTRY, 108, "source_compiled"),
            "production program_dma manifest registration changed")
    require(
        (successor["target_address"], successor["size"],
         successor["address_status"])
        == (END, 118, "source_compiled"),
        "high-priority scheduler local successor ownership changed",
    )
    with tempfile.TemporaryDirectory(prefix="open-cfw-program-dma-component-") as raw:
        subprocess.run(["python3", str(BUILDER), "--output-dir", raw], cwd=ROOT,
                       check=True, capture_output=True, text=True)
        report = json.loads((Path(raw) / "build-report.json").read_text(encoding="utf-8"))
    component = report["component"]
    require(
        component["source_owned_bytes"] + component["opaque_base_bytes"]
        + component["generated_patch_site_bytes"]
        + component["generated_alignment_bytes"] == component["size"],
        "production program_dma byte conservation changed",
    )
    require(component["source_owned_in_place_bytes"] <= component["source_owned_bytes"],
            "production program_dma in-place accounting changed")
    built = next(row for row in report["in_place_leaves"]
                 if row["extraction"]["function"] ==
                 "open_cfw_bootloader_mspi_program_dma_42403e")
    require((built["extraction"]["sha256"], built["placement"]["stock_sha256"])
            == (STOCK_SHA, STOCK_SHA), "production program_dma placement changed")
    return {
        "status": "production-routed-exact-dual-profile-source / hardware-validation-deferred-by-project-direction",
        "stock": {"start": ENTRY, "end": END, "bytes": len(stock), "sha256": STOCK_SHA},
        "identity": {"function": "program_dma",
                     "upstream_commit": provenance["upstream"]["selected_commit"],
                     "license": "BSD-3-Clause"},
        "callers": list(callers),
        "abi": {"module_offset": 4, "max_hp_offset": 0x848,
                "last_hp_offset": 0x850, "transactions_offset": 0x854,
                "entry_bytes": 24, "clock_id": 4, "clock_user_base": 16,
                "mspi0_base": 0x40060000, "module_stride": 0x1000},
        "profiles": profiles,
        "production": {"routed": True,
                       "source_owned_bytes": component["source_owned_bytes"],
                       "retained_official_bytes": component["opaque_base_bytes"],
                       "next_frontier": successor["target_address"]},
        "next_frontier": {"start": END, "end": 0x00424120,
                          "identity": "sched_hiprio", "bytes": 118},
        "hardware_validation": "deferred by project direction",
        "hardware_gate": {"required_future_evidence":
                          "authorized clock-request, DMA MMIO, queue-index, concurrency, interrupt, and cold-boot qualification"},
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
        print("Bootloader program_dma 0x42403e: production-routed exact source")
        print("  next sequential frontier: 0x4240aa (sched_hiprio)")
        print("  physical validation: deferred by project direction")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader program_dma audit failed: {exc}")
