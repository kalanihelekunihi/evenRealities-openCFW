#!/usr/bin/env python3
"""Fail-closed source/toolchain audit for bootloader mspi_fifo_write at 0x423E40."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
RUN_BASE = 0x00410000
ENTRY = 0x00423E40
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
PRODUCTION_SOURCE = (
    ROOT / "components/bootloader/core_overlay/runtime_mspi_fifo_write_423e40.c"
)
READ_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_fifo_read_423e8a.c"
BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"
CENSUS = ROOT / "tools/manifests/g2-bootloader-mspi-fifo-write-423e40.tsv"
BOUNDARY_DIR = ROOT / "research/admission/bootloader_mspi_fifo_write_423e40"
BOUNDARY = BOUNDARY_DIR / "runtime_bootloader_mspi_fifo_write_boundary.c"
HEADER = BOUNDARY.with_suffix(".h")
AMBIQ_ROOT = ROOT / "third_party/ambiqsuite-apollo510"
AMBIQ_SOURCE = AMBIQ_ROOT / "mcu/apollo510/hal/mcu/am_hal_mspi.c"
AMBIQ_HEADER = AMBIQ_ROOT / "mcu/apollo510/hal/mcu/am_hal_mspi.h"
UTILS_HEADER = AMBIQ_ROOT / "mcu/apollo510/hal/am_hal_utils.h"
DEVICE_HEADER = AMBIQ_ROOT / "CMSIS/AmbiqMicro/Include/apollo510.h"
PROVENANCE = AMBIQ_ROOT / "PROVENANCE.json"
LICENSE = AMBIQ_ROOT / "LICENSE"
CMSIS_CORE = ROOT / "third_party/cmsis-core/CMSIS/Core/Include"

FILE_PINS = {
    PRODUCTION_SOURCE: (2466, "3594fe14cc673e58032785ab9f5fbacb0479db9d0187b7b49610734fdbe31f48"),
    READ_SOURCE: (4381, "d82f43ac56e65dd0cd4072828a6566d3ec6cc34008572704f26d1d72f9efc274"),
    CENSUS: (2401, "f5bc20c18c35157037b5f4ea1b2438686940f9b6f46316d459c554e469c41070"),
    BOUNDARY: (1757, "5ee3b81deb6b434ba0b446f741fb66ee9745b6b60d9c5c6b94dc3f6674944ecf"),
    HEADER: (2404, "b0af55fe72697e234fce3ca70c48006638630f0b2e24190b836d896ce4da433d"),
    AMBIQ_SOURCE: (168473, "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"),
    AMBIQ_HEADER: (36982, "2a682bb7c1618982d6a802f3220a38696cd594c89d90e64b1a698d226b0a557b"),
    UTILS_HEADER: (5857, "15f4657c5838278f3cf3bf68862e61ccb222569660dc3bc180e85520bd869154"),
    DEVICE_HEADER: (10449123, "b6ca35dc828ef95825c0a22f06e6ca5ed558a6542dc74310515fdc350051a797"),
    PROVENANCE: (18060, "ee9eb7e9ab8465bbe8b836b9baf04d6a10d470091bb60fe51f0771fecf36bdec"),
    LICENSE: (1525, "0770df5c1956b75715604d5788804eabfc293fc61d5dbbec498c6d379a63755f"),
}

SPANS = {
    "mspi_fifo_write": (
        0x00423E40, 0x00423E8A,
        "8ea56d5bbd1d671d999791ea24b747f4083048a9bfe169360470ebf4d36914d1",
    ),
    "mspi0_base_literal": (
        0x0042499C, 0x004249A0,
        "512cda42a9c3b00954f5ebd4cc8487efe02285b6c25f63e91df882b8846d7ded",
    ),
    "delay_us_status_check": (
        0x0041D246, 0x0041D28A,
        "c6bf044dbb8f4a358cc93e10eff0b2ec7065b47f8ff08cde9f912d749fd42ef9",
    ),
    "delay_us": (
        0x0041D1C0, 0x0041D21C,
        "778937554944e0d3d1b3f3ff11fa408db63ff275b20e0af1e32d549219cc1ae7",
    ),
    "next_sequential_entry": (
        0x00423E8A, 0x00423F28,
        "9bb93dd67b7844ce1e9d75d6a165667cc38f27b45ad937ea7815c357d8ce4a7b",
    ),
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def decode_thumb_bl(image: bytes, address: int) -> int | None:
    offset = address - RUN_BASE
    if offset < 0 or offset + 4 > len(image):
        return None
    first = int.from_bytes(image[offset:offset + 2], "little")
    second = int.from_bytes(image[offset + 2:offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22)
                 | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def direct_callers(image: bytes, target: int) -> tuple[int, ...]:
    return tuple(address for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
                 if decode_thumb_bl(image, address) == target)


def llvm_tool(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    candidate = Path("/opt/homebrew/opt/llvm/bin") / name
    require(candidate.is_file(), f"required LLVM tool unavailable: {name}")
    return str(candidate)


def build_upstream_profile(clang: str, objcopy: str, objdump: str, output: Path) -> bytes:
    obj = output / (Path(clang).parent.name + "-mspi.o")
    raw = obj.with_suffix(".bin")
    command = [
        clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
        "-fno-inline", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
        "-fdata-sections", "-Wno-unused-function",
        "-I", str(AMBIQ_ROOT / "mcu/apollo510"),
        "-I", str(AMBIQ_ROOT / "mcu/apollo510/hal"),
        "-I", str(AMBIQ_ROOT / "CMSIS/AmbiqMicro/Include"),
        "-I", str(CMSIS_CORE), "-c", str(AMBIQ_SOURCE), "-o", str(obj),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)
    subprocess.run(
        [objcopy, "-O", "binary", "--only-section=.text.mspi_fifo_write",
         str(obj), str(raw)], check=True, capture_output=True, text=True,
    )
    listing = subprocess.run(
        [objdump, "-r", str(obj)], check=True, capture_output=True, text=True,
    ).stdout
    block = re.search(
        r"RELOCATION RECORDS FOR \[\.text\.mspi_fifo_write\]:(.*?)(?:\n\n|\Z)",
        listing, re.S,
    )
    require(block is not None, f"upstream relocation section missing under {clang}")
    relocations = tuple(
        (int(match.group(1), 16), match.group(2))
        for match in re.finditer(
            r"^([0-9a-fA-F]{8})\s+R_ARM_THM_CALL\s+(\S+)$",
            block.group(1), re.MULTILINE,
        )
    )
    require(relocations == ((0x3E, "am_hal_delay_us_status_check"),),
            f"upstream provider graph changed under {clang}")
    return raw.read_bytes()


def audit() -> dict:
    image = OFFICIAL.read_bytes()
    require((len(image), digest(image)) == (
        148599, "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
    ), "official bootloader pin changed")
    for path, expected in FILE_PINS.items():
        payload = path.read_bytes()
        require((len(payload), digest(payload)) == expected, f"file pin changed: {path}")

    rows = list(csv.DictReader(CENSUS.read_text(encoding="utf-8").splitlines(), delimiter="\t"))
    indexed = {row["name"]: row for row in rows}
    require(tuple(indexed) == (
        "mspi_fifo_write", "mspi0_base_literal", "delay_us_status_check",
        "delay_us", "bootrom_delay_cycles", "clang_preserved_leaf",
        "next_sequential_entry",
    ), "census graph changed")
    for name, (start, end, expected_hash) in SPANS.items():
        body = image[start - RUN_BASE:end - RUN_BASE]
        require((len(body), digest(body)) == (end - start, expected_hash),
                f"stock span changed: {name}")
        row = indexed[name]
        require((int(row["start"], 16), int(row["end"], 16),
                 int(row["size"]), row["sha256"])
                == (start, end, end - start, expected_hash),
                f"census row changed: {name}")
    require(int.from_bytes(image[0x0042499C - RUN_BASE:0x004249A0 - RUN_BASE], "little")
            == 0x40060000, "MSPI0 base literal changed")

    require(direct_callers(image, ENTRY) == (0x0042640C,), "FIFO-write caller changed")
    status_callers = direct_callers(image, 0x0041D246)
    require(len(status_callers) == 18 and 0x00423E7A in status_callers,
            "status-check caller graph changed")
    require(decode_thumb_bl(image, 0x0041D260) == 0x0041D1C0,
            "status-check delay edge changed")
    require(decode_thumb_bl(image, 0x0041D20A) == 0x00000040,
            "delay boot-ROM edge changed")

    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    require(provenance["license"] == "BSD-3-Clause", "Ambiq license changed")
    require(provenance["upstream"]["selected_commit"]
            == "5efc0228528a8adce5eae0d226fac85d2551eb3b",
            "Ambiq upstream commit changed")
    source_text = AMBIQ_SOURCE.read_text(encoding="utf-8")
    fragment = re.search(
        r"static uint32_t\nmspi_fifo_write\(.*?\n}\n", source_text, re.S
    )
    require(fragment is not None, "upstream mspi_fifo_write disappeared")
    fragment_bytes = fragment.group(0).encode()
    require((len(fragment_bytes), digest(fragment_bytes)) == (
        1231, "60aee6b52b81906e40b3094c1b2ffcccef76fe7c762a0b864fe9543fc088639d"
    ), "upstream mspi_fifo_write identity changed")
    for token in (
        "AM_REG_MSPI_NUM_MODULES", "MSPIn(ui32Module)->TXFIFO",
        "MSPIn(ui32Module)->TXENTRIES", "MSPI0_TXENTRIES_TXENTRIES_Msk",
        "AM_HAL_MSPI_MAX_FIFO_SIZE", "false",
    ):
        require(token in fragment.group(0), f"upstream semantic token missing: {token}")
    require("extern uint32_t am_hal_delay_us_status_check" in UTILS_HEADER.read_text(),
            "status-check typed upstream ABI changed")
    device = DEVICE_HEADER.read_text(encoding="utf-8")
    require("#define MSPI0_BASE                  0x40060000UL" in device,
            "MSPI0 base definition changed")
    require("#define MSPI0_TXENTRIES_TXENTRIES_Msk     (0x3fUL)" in device,
            "TXENTRIES mask changed")
    require("#define AM_HAL_MSPI_MAX_FIFO_SIZE               16" in AMBIQ_HEADER.read_text(),
            "MSPI FIFO depth changed")

    objcopy = llvm_tool("llvm-objcopy")
    objdump = llvm_tool("llvm-objdump")
    profiles = ["/usr/bin/clang"]
    homebrew = Path("/opt/homebrew/opt/llvm@22/bin/clang")
    if homebrew.is_file():
        profiles.append(str(homebrew))
    with tempfile.TemporaryDirectory(prefix="open-cfw-mspi-fifo-audit-") as raw:
        output = Path(raw)
        for clang in profiles:
            built = build_upstream_profile(clang, objcopy, objdump, output)
            require((len(built), digest(built)) == (
                80, "f7a88e1c056f8fc82c62783cf6e29266093356d73615bb4ef391b4fd50e1a796"
            ), f"reviewed Clang semantic build changed under {clang}")
            require(built != image[ENTRY - RUN_BASE:0x00423E8A - RUN_BASE],
                    "toolchain mismatch unexpectedly disappeared")

    boundary_text = BOUNDARY.read_text(encoding="utf-8") + HEADER.read_text(encoding="utf-8")
    for token in (
        "SPDX-License-Identifier: MIT",
        "OPEN_CFW_BOOT_MSPI_FIFO_WRITE_EXACT_TOOLCHAIN_UNRESOLVED",
        "0x00423E40U", "0x0041D246U", "0x40060000U", "BSD-3-Clause",
        "stock IAR compiler release/options",
    ):
        require(token in boundary_text, f"typed boundary token missing: {token}")

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    routed = overlay.get("in_place_leaves", []) + overlay.get("relocated_leaves", [])
    production = [entry for entry in routed if entry.get("runtime_address") == ENTRY]
    require(len(production) == 1, "FIFO-write production route changed")
    require(production[0]["function"] == "open_cfw_bootloader_mspi_fifo_write_423e40",
            "FIFO-write production symbol changed")
    with tempfile.TemporaryDirectory(prefix="open-cfw-mspi-fifo-production-") as raw:
        output = Path(raw)
        subprocess.run(
            ["python3", str(BUILDER), "--output-dir", str(output)], cwd=ROOT,
            check=True, capture_output=True, text=True,
        )
        report = json.loads((output / "build-report.json").read_text(encoding="utf-8"))
    leaf = next(item for item in report["in_place_leaves"]
                if item["extraction"]["runtime_address"] == ENTRY)
    extraction = leaf["extraction"]
    require((extraction["size"], extraction["sha256"],
             extraction["unrelocated_sha256"], extraction["relocation_count"])
            == (74, SPANS["mspi_fifo_write"][2],
                "aac9e4aa3174a187885885bcffef4eaa8fb5d7f2a3a7557925f22f4becd41b50", 1),
            "exact production extraction changed")
    require(extraction["relocations"] == [{
        "offset": 58,
        "runtime_address": 0x00423E7A,
        "runtime_address_hex": "0x00423E7A",
        "symbol": "open_cfw_bootloader_retained_status_check_41d246",
        "symbol_type": "STT_NOTYPE",
        "target_address": 0x0041D246,
        "target_address_hex": "0x0041D246",
        "type": "R_ARM_THM_CALL",
        "type_id": 10,
    }], "production relocation contract changed")
    component = report["component"]
    require(
        component["source_owned_bytes"] + component["opaque_base_bytes"]
        + component["generated_patch_site_bytes"]
        + component["generated_alignment_bytes"] == component["size"],
        "production byte conservation changed",
    )
    read_leaf = next(item for item in report["in_place_leaves"]
                     if item["extraction"]["runtime_address"] == 0x00423E8A)
    require((read_leaf["extraction"]["size"], read_leaf["extraction"]["sha256"],
             read_leaf["extraction"]["relocation_count"])
            == (158, "9bb93dd67b7844ce1e9d75d6a165667cc38f27b45ad937ea7815c357d8ce4a7b", 2),
            "FIFO-read sequential source closure changed")
    core = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
    regions = core["component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {row["name"]: row for row in regions}
    write_name = "bootloader_mspi_fifo_write_423e40_source_in_place"
    read_name = "bootloader_mspi_fifo_read_423e8a_source_in_place"
    require(write_name in by_name, "FIFO-write production region disappeared")
    require(read_name in by_name, "FIFO-read successor region disappeared")
    write_region = by_name[write_name]
    read_region = by_name[read_name]
    require(
        (write_region["target_address"], write_region["size"],
         write_region["address_status"])
        == (ENTRY, 74, "source_compiled"),
        "FIFO-write production ownership changed",
    )
    require(
        (read_region["target_address"], read_region["size"],
         read_region["address_status"])
        == (0x00423E8A, 158, "source_compiled"),
        "FIFO-read local successor ownership changed",
    )

    return {
        "component": "G2 bootloader Ambiq MSPI FIFO-write frontier",
        "status": "implemented-in-source / hardware-validation-deferred-by-project-direction",
        "stock": {
            "start": ENTRY, "end": 0x00423E8A, "bytes": 74,
            "sha256": SPANS["mspi_fifo_write"][2],
            "sole_caller": 0x0042640C,
        },
        "identity": {
            "function": "mspi_fifo_write",
            "provider": "am_hal_delay_us_status_check",
            "upstream_commit": provenance["upstream"]["selected_commit"],
            "license": "BSD-3-Clause",
            "source_redistribution": "permitted with BSD conditions",
            "official_binary_redistribution": "unresolved",
        },
        "abi": {
            "mspi_base": 0x40060000, "module_stride": 0x1000,
            "txfifo_offset": 0x10, "txentries_offset": 0x18,
            "mask": 0x3F, "full_value": 0x10, "is_equal": False,
        },
        "provider_graph": [
            "am_hal_delay_us_status_check@0x0041D246",
            "am_hal_delay_us@0x0041D1C0",
            "bootrom_delay_cycles@0x00000040",
        ],
        "toolchain": {
            "reviewed_profiles": len(profiles), "upstream_semantic_clang_bytes": 80,
            "production_bytes": 74, "exact_match": True,
            "method": "typed clean-room host model plus exact target mnemonic body",
        },
        "production": {
            "routed": True,
            "next_frontier": read_region["target_address"] + read_region["size"],
            "local_successor": {
                "start": read_region["target_address"],
                "end": read_region["target_address"] + read_region["size"],
                "address_status": read_region["address_status"],
            },
            "source_owned_bytes": component["source_owned_bytes"],
            "retained_official_bytes": component["opaque_base_bytes"],
        },
        "hardware_validation": "deferred by project direction",
        "hardware_gate": {
            "required_future_evidence": "authorized G2 qualification exercising all four MSPI instances, FIFO writes, timeout polling, and cold boot",
        },
        "hardware_operations": [],
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Bootloader MSPI FIFO-write 0x423e40: implemented in exact source")
        print("  physical validation: deferred by project direction")
        print("  locally proven source closure: 0x423e40 through 0x423f28")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader MSPI FIFO-write audit failed: {exc}") from exc
