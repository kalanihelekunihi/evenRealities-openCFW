#!/usr/bin/env python3
"""Fail-closed source/toolchain audit for bootloader mspi_fifo_read at 0x423E8A."""

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
ENTRY = 0x00423E8A
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
PRODUCTION_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_fifo_read_423e8a.c"
BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"
CENSUS = ROOT / "tools/manifests/g2-bootloader-mspi-fifo-read-423e8a.tsv"
BOUNDARY_DIR = ROOT / "research/admission/bootloader_mspi_fifo_read_423e8a"
BOUNDARY = BOUNDARY_DIR / "runtime_bootloader_mspi_fifo_read_boundary.c"
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
    PRODUCTION_SOURCE: (4381, "d82f43ac56e65dd0cd4072828a6566d3ec6cc34008572704f26d1d72f9efc274"),
    CENSUS: (2717, "510707c06c9f0c2685152c2dcbd7434ffed02ea4c70a967cf9c1ec73812a320d"),
    BOUNDARY: (2613, "43d72d56442cec4e749804059452b8a85dbd6845e16aae9d6247ea4c5632e4b5"),
    HEADER: (2074, "38370f780cacab76432eeef3dd3d6b54a622a8bcefc92071412c5a0e40532a4b"),
    AMBIQ_SOURCE: (168473, "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"),
    AMBIQ_HEADER: (36982, "2a682bb7c1618982d6a802f3220a38696cd594c89d90e64b1a698d226b0a557b"),
    UTILS_HEADER: (5857, "15f4657c5838278f3cf3bf68862e61ccb222569660dc3bc180e85520bd869154"),
    DEVICE_HEADER: (10449123, "b6ca35dc828ef95825c0a22f06e6ca5ed558a6542dc74310515fdc350051a797"),
    PROVENANCE: (18060, "ee9eb7e9ab8465bbe8b836b9baf04d6a10d470091bb60fe51f0771fecf36bdec"),
    LICENSE: (1525, "0770df5c1956b75715604d5788804eabfc293fc61d5dbbec498c6d379a63755f"),
}

SPANS = {
    "mspi_fifo_read": (
        0x00423E8A, 0x00423F28,
        "9bb93dd67b7844ce1e9d75d6a165667cc38f27b45ad937ea7815c357d8ce4a7b",
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
        0x00423F28, 0x00423F54,
        "8e2e5409620c3c1b334d8c3ede2ea19b20a31471e40a0c8b0c88f6550a7e9b05",
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
    obj = output / (Path(clang).parent.name + "-mspi-read.o")
    raw = obj.with_suffix(".bin")
    subprocess.run([
        clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
        "-fno-inline", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
        "-fdata-sections", "-Wno-unused-function",
        "-I", str(AMBIQ_ROOT / "mcu/apollo510"),
        "-I", str(AMBIQ_ROOT / "mcu/apollo510/hal"),
        "-I", str(AMBIQ_ROOT / "CMSIS/AmbiqMicro/Include"),
        "-I", str(CMSIS_CORE), "-c", str(AMBIQ_SOURCE), "-o", str(obj),
    ], check=True, capture_output=True, text=True)
    subprocess.run(
        [objcopy, "-O", "binary", "--only-section=.text.mspi_fifo_read",
         str(obj), str(raw)], check=True, capture_output=True, text=True,
    )
    listing = subprocess.run(
        [objdump, "-r", str(obj)], check=True, capture_output=True, text=True,
    ).stdout
    block = re.search(
        r"RELOCATION RECORDS FOR \[\.text\.mspi_fifo_read\]:(.*?)(?:\n\n|\Z)",
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
    if Path(clang) == Path("/usr/bin/clang"):
        require(relocations == (
            (0x40, "am_hal_delay_us_status_check"),
            (0x62, "am_hal_delay_us_status_check"),
        ), "Apple Clang provider graph changed")
    else:
        require(relocations == (
            (0x38, "am_hal_delay_us_status_check"),
            (0x5A, "am_hal_delay_us_status_check"),
        ), "Homebrew Clang provider graph changed")
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
        "mspi_fifo_read", "mspi0_base_literal", "delay_us_status_check",
        "delay_us", "bootrom_delay_cycles", "apple_clang_preserved_leaf",
        "homebrew_clang_preserved_leaf", "next_sequential_entry",
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

    require(direct_callers(image, ENTRY) == (0x004263F6,), "FIFO-read caller changed")
    require((decode_thumb_bl(image, 0x00423ED8), decode_thumb_bl(image, 0x00423EFC))
            == (0x0041D246, 0x0041D246), "FIFO-read provider edges changed")
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
    fragment = re.search(r"static uint32_t\nmspi_fifo_read\(.*?\n}\n", source_text, re.S)
    require(fragment is not None, "upstream mspi_fifo_read disappeared")
    fragment_bytes = fragment.group(0).encode()
    require((len(fragment_bytes), digest(fragment_bytes)) == (
        3235, "b9f06db08f91f779171115ad8be39425554cfb36dad123597e13b576bf039cd7"
    ), "upstream mspi_fifo_read identity changed")
    for token in (
        "AM_REG_MSPI_NUM_MODULES", "ui32NumBytes / 4",
        "MSPIn(ui32Module)->RXFIFO", "MSPIn(ui32Module)->RXENTRIES",
        "MSPI0_RXENTRIES_RXENTRIES_Msk", "ui32Leftovers", "false",
    ):
        require(token in fragment.group(0), f"upstream semantic token missing: {token}")
    require("extern uint32_t am_hal_delay_us_status_check" in UTILS_HEADER.read_text(),
            "status-check typed upstream ABI changed")
    device = DEVICE_HEADER.read_text(encoding="utf-8")
    require("#define MSPI0_BASE                  0x40060000UL" in device,
            "MSPI0 base definition changed")
    require("#define MSPI0_RXENTRIES_RXENTRIES_Msk     (0x3fUL)" in device,
            "RXENTRIES mask changed")
    require("#define AM_HAL_MSPI_MAX_FIFO_SIZE               16" in AMBIQ_HEADER.read_text(),
            "MSPI FIFO depth changed")

    objcopy = llvm_tool("llvm-objcopy")
    objdump = llvm_tool("llvm-objdump")
    profiles = ["/usr/bin/clang"]
    homebrew = Path("/opt/homebrew/opt/llvm@22/bin/clang")
    if homebrew.is_file():
        profiles.append(str(homebrew))
    expected_builds = {
        "/usr/bin/clang": (156, "e229e94145fb9563f438954cd0f35394cf5fa0563576c62e8d86958c5e7123c9"),
        str(homebrew): (148, "c3ab2557e0dfc8cafc6c215072fad483b0b7c67f6a27e98e5ed7b85e186bf97a"),
    }
    with tempfile.TemporaryDirectory(prefix="open-cfw-mspi-read-audit-") as raw:
        output = Path(raw)
        for clang in profiles:
            built = build_upstream_profile(clang, objcopy, objdump, output)
            require((len(built), digest(built)) == expected_builds[clang],
                    f"reviewed semantic build changed under {clang}")
            require(built != image[ENTRY - RUN_BASE:0x00423F28 - RUN_BASE],
                    "toolchain mismatch unexpectedly disappeared")

    boundary_text = BOUNDARY.read_text(encoding="utf-8") + HEADER.read_text(encoding="utf-8")
    for token in (
        "SPDX-License-Identifier: MIT",
        "OPEN_CFW_BOOT_MSPI_FIFO_READ_EXACT_TOOLCHAIN_UNRESOLVED",
        "0x00423E8AU", "0x0041D246U", "0x40060000U", "BSD-3-Clause",
        "stock IAR compiler release/options",
    ):
        require(token in boundary_text, f"typed boundary token missing: {token}")

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    routed = overlay.get("in_place_leaves", []) + overlay.get("relocated_leaves", [])
    production = [entry for entry in routed if entry.get("runtime_address") == ENTRY]
    require(len(production) == 1, "FIFO-read production route changed")
    require(production[0]["function"] == "open_cfw_bootloader_mspi_fifo_read_423e8a",
            "FIFO-read production symbol changed")
    with tempfile.TemporaryDirectory(prefix="open-cfw-mspi-read-production-") as raw:
        output = Path(raw)
        subprocess.run(["python3", str(BUILDER), "--output-dir", str(output)], cwd=ROOT,
                       check=True, capture_output=True, text=True)
        build_report = json.loads((output / "build-report.json").read_text(encoding="utf-8"))
    leaf = next(item for item in build_report["in_place_leaves"]
                if item["extraction"]["runtime_address"] == ENTRY)
    extraction = leaf["extraction"]
    require((extraction["size"], extraction["sha256"],
             extraction["unrelocated_sha256"], extraction["relocation_count"])
            == (158, SPANS["mspi_fifo_read"][2],
                "e6a327fa4c600e41273694a52a6bc7c1faf77f01020ccf3272d9304d1d0f51f1", 2),
            "exact production extraction changed")
    require([(row["offset"], row["target_address"]) for row in extraction["relocations"]]
            == [(78, 0x0041D246), (114, 0x0041D246)],
            "production relocation contract changed")
    component = build_report["component"]
    require(
        component["source_owned_bytes"] + component["opaque_base_bytes"]
        + component["generated_patch_site_bytes"]
        + component["generated_alignment_bytes"] == component["size"],
        "production byte conservation changed",
    )
    core = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
    regions = core["component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {row["name"]: row for row in regions}
    source_name = "bootloader_mspi_fifo_read_423e8a_source_in_place"
    successor_name = "bootloader_mspi_cq_init_423f28_source_in_place"
    require(source_name in by_name, "FIFO-read production region disappeared")
    require(successor_name in by_name, "CQ-init successor region disappeared")
    source_region = by_name[source_name]
    successor = by_name[successor_name]
    require(
        (source_region["target_address"], source_region["size"],
         source_region["address_status"])
        == (ENTRY, 158, "source_compiled"),
        "FIFO-read production ownership changed",
    )
    require(
        (successor["target_address"], successor["size"],
         successor["address_status"])
        == (0x00423F28, 44, "source_compiled"),
        "CQ-init local successor ownership changed",
    )

    return {
        "component": "G2 bootloader Ambiq MSPI FIFO-read frontier",
        "status": "implemented-in-source / hardware-validation-deferred-by-project-direction",
        "stock": {
            "start": ENTRY, "end": 0x00423F28, "bytes": 158,
            "sha256": SPANS["mspi_fifo_read"][2], "sole_caller": 0x004263F6,
        },
        "identity": {
            "function": "mspi_fifo_read",
            "provider": "am_hal_delay_us_status_check",
            "upstream_commit": provenance["upstream"]["selected_commit"],
            "license": "BSD-3-Clause",
            "source_redistribution": "permitted with BSD conditions",
            "official_binary_redistribution": "unresolved",
        },
        "abi": {
            "mspi_base": 0x40060000, "module_stride": 0x1000,
            "rxfifo_offset": 0x14, "rxentries_offset": 0x1C,
            "mask": 0x3F, "target_value": 0, "is_equal": False,
            "timeout_short_circuit": True, "little_endian_leftovers": True,
        },
        "provider_graph": [
            "am_hal_delay_us_status_check@0x0041D246",
            "am_hal_delay_us@0x0041D1C0",
            "bootrom_delay_cycles@0x00000040",
        ],
        "toolchain": {
            "reviewed_profiles": len(profiles),
            "apple_clang_bytes": 156, "homebrew_clang_bytes": 148,
            "stock_bytes": 158, "exact_match": False,
            "blocker": "stock IAR release/options and emitted-body identity unresolved",
        },
        "production": {"routed": True,
                       "next_frontier": successor["target_address"],
                       "local_successor": {
                           "start": successor["target_address"],
                           "end": successor["target_address"] + successor["size"],
                           "address_status": successor["address_status"],
                       },
                       "source_owned_bytes": component["source_owned_bytes"],
                       "retained_official_bytes": component["opaque_base_bytes"]},
        "hardware_validation": "deferred by project direction",
        "hardware_gate": {
            "required_future_evidence": "authorized G2 qualification exercising all four MSPI instances, full-word and partial FIFO reads, timeouts, and cold boot",
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
        print("Bootloader MSPI FIFO-read 0x423e8a: implemented in exact source")
        print("  upstream build identity remains fail-closed; clean-room production bytes exact")
        print("  physical validation: deferred by project direction")
        print("  exact local successor: 0x423f28 (CQ init, source-owned)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader MSPI FIFO-read audit failed: {exc}") from exc
