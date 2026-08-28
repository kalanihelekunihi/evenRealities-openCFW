#!/usr/bin/env python3
"""Fail-closed source/toolchain audit for bootloader mspi_cq_init at 0x423F28."""

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
ENTRY = 0x00423F28
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CORE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
PRODUCTION_SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_cq_init_423f28.c"
BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"
CENSUS = ROOT / "tools/manifests/g2-bootloader-mspi-cq-init-423f28.tsv"
BOUNDARY_DIR = ROOT / "research/admission/bootloader_mspi_cq_init_423f28"
BOUNDARY = BOUNDARY_DIR / "runtime_bootloader_mspi_cq_init_boundary.c"
HEADER = BOUNDARY.with_suffix(".h")
PROVIDER_FRAGMENT = BOUNDARY_DIR / "upstream_am_hal_cmdq_init_fragment.c"
AMBIQ_ROOT = ROOT / "third_party/ambiqsuite-apollo510"
AMBIQ_SOURCE = AMBIQ_ROOT / "mcu/apollo510/hal/mcu/am_hal_mspi.c"
CMDQ_HEADER = AMBIQ_ROOT / "mcu/apollo510/hal/mcu/am_hal_cmdq.h"
PROVENANCE = AMBIQ_ROOT / "PROVENANCE.json"
LICENSE = AMBIQ_ROOT / "LICENSE"
CMSIS_CORE = ROOT / "third_party/cmsis-core/CMSIS/Core/Include"

FILE_PINS = {
    PRODUCTION_SOURCE: (2021, "3112ebd6442131e09ae6d37d4b51f095033905e26aed05be5122a71af619b448"),
    CENSUS: (3109, "11ae9a31756438f29e42e48d4fae6d4b17c74dba4e2bf673827d5a7c81ac142b"),
    BOUNDARY: (2650, "a812f9bc8fec12c115107b0aa394582700f2f120cd989e26272beb2528fa403b"),
    HEADER: (1911, "eee01d2102b78f8c15cbbffa6c50b66dd0f9484c65ab66f353d1871061ee5066"),
    PROVIDER_FRAGMENT: (3286, "78bd5b722bac14934fb6537e7d5b2e72361b38c937a090490910a523201e568e"),
    AMBIQ_SOURCE: (168473, "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"),
    CMDQ_HEADER: (10496, "0113aed2f109c5f022d38055b83a75c2cf141e8621177296757fc8315926762f"),
    PROVENANCE: (18060, "ee9eb7e9ab8465bbe8b836b9baf04d6a10d470091bb60fe51f0771fecf36bdec"),
    LICENSE: (1525, "0770df5c1956b75715604d5788804eabfc293fc61d5dbbec498c6d379a63755f"),
}

SPANS = {
    "mspi_cq_init": (0x00423F28, 0x00423F54, "8e2e5409620c3c1b334d8c3ede2ea19b20a31471e40a0c8b0c88f6550a7e9b05"),
    "mspi_state_base": (0x00424AEC, 0x00424AF0, "9b725a263fa8efdc9db13e5ad62b70166e989bcf42cb6020b325e954d34983eb"),
    "am_hal_cmdq_init": (0x00427794, 0x00427878, "ad7e3d6257b791855a8cd7fe90389313dfb9496262724777900d6a4193c09b52"),
    "cmdq_state_and_register_table_pointers": (0x00427C80, 0x00427C88, "3eacd36ef95e51396f22c8e40064f3edaf94b8a8c1796b757cca3c8ef34e7aca"),
    "cmdq_register_table": (0x00430880, 0x00430A60, "1ed1fa3682f9c16c403ee0e6cee7761b70ca610656a2b6e56de3f0b05cee7fea"),
    "next_sequential_entry": (0x00423F54, 0x00423F8E, "07a7e8e54305fbecb7f891cd4e843881b73a33186ba1750b147e0647d0041807"),
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


def build_profile(clang: str, objcopy: str, objdump: str, output: Path,
                  short_enums: bool) -> bytes:
    label = ("apple" if Path(clang) == Path("/usr/bin/clang") else "homebrew")
    label += "-short" if short_enums else "-default"
    obj = output / f"{label}.o"
    raw = obj.with_suffix(".bin")
    command = [
        clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
        "-fno-inline", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
        "-fdata-sections", "-Wno-unused-function",
    ]
    if short_enums:
        command.append("-fshort-enums")
    command += [
        "-I", str(AMBIQ_ROOT / "mcu/apollo510"),
        "-I", str(AMBIQ_ROOT / "mcu/apollo510/hal"),
        "-I", str(AMBIQ_ROOT / "CMSIS/AmbiqMicro/Include"),
        "-I", str(CMSIS_CORE), "-c", str(AMBIQ_SOURCE), "-o", str(obj),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)
    subprocess.run([objcopy, "-O", "binary", "--only-section=.text.mspi_cq_init",
                    str(obj), str(raw)], check=True, capture_output=True, text=True)
    listing = subprocess.run([objdump, "-r", str(obj)], check=True,
                             capture_output=True, text=True).stdout
    block = re.search(r"RELOCATION RECORDS FOR \[\.text\.mspi_cq_init\]:(.*?)(?:\n\n|\Z)",
                      listing, re.S)
    require(block is not None, f"mspi_cq_init relocations missing under {label}")
    call = re.search(r"^([0-9a-fA-F]{8})\s+R_ARM_THM_CALL\s+am_hal_cmdq_init$",
                     block.group(1), re.MULTILINE)
    state = re.search(r"^([0-9a-fA-F]{8})\s+R_ARM_ABS32\s+\.bss\.g_MSPIState$",
                      block.group(1), re.MULTILINE)
    expected = (0x22, 0x28) if short_enums else (0x1E, 0x24)
    require(call is not None and state is not None, f"provider relocations changed under {label}")
    require((int(call.group(1), 16), int(state.group(1), 16)) == expected,
            f"provider relocation offsets changed under {label}")
    return raw.read_bytes()


def audit() -> dict:
    image = OFFICIAL.read_bytes()
    require((len(image), digest(image)) ==
            (148599, "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"),
            "official bootloader pin changed")
    for path, expected in FILE_PINS.items():
        payload = path.read_bytes()
        require((len(payload), digest(payload)) == expected, f"file pin changed: {path}")

    rows = list(csv.DictReader(CENSUS.read_text(encoding="utf-8").splitlines(), delimiter="\t"))
    indexed = {row["name"]: row for row in rows}
    require(tuple(indexed) == (
        "mspi_cq_init", "mspi_state_base", "am_hal_cmdq_init",
        "cmdq_state_and_register_table_pointers", "cmdq_register_table",
        "apple_clang_default_enum", "homebrew_clang_default_enum",
        "apple_clang_short_enum", "homebrew_clang_short_enum",
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

    stock = image[ENTRY - RUN_BASE:0x00423F54 - RUN_BASE]
    require(stock.hex() ==
            "e0b501924908009101218df80810dff8b41b4ff40d6202fb00f2114401f6280269460830c0b203f021fc0ebd",
            "stock adapter ABI instructions changed")
    require(direct_callers(image, ENTRY) == (0x0042509C,), "adapter caller changed")
    require(decode_thumb_bl(image, 0x00423F4E) == 0x00427794, "CMDQ provider edge changed")
    require(direct_callers(image, 0x00427794) == (0x00423F4E, 0x0042C40E),
            "CMDQ init caller set changed")
    require(int.from_bytes(image[0x00424AEC - RUN_BASE:0x00424AF0 - RUN_BASE], "little")
            == 0x2001CAA0, "g_MSPIState pointer changed")
    require((int.from_bytes(image[0x00427C80 - RUN_BASE:0x00427C84 - RUN_BASE], "little"),
             int.from_bytes(image[0x00427C84 - RUN_BASE:0x00427C88 - RUN_BASE], "little"))
            == (0x200262F0, 0x00430880), "CMDQ provider literals changed")

    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    require(provenance["license"] == "BSD-3-Clause", "Ambiq license changed")
    require(provenance["upstream"]["selected_commit"]
            == "5efc0228528a8adce5eae0d226fac85d2551eb3b", "Ambiq commit changed")
    source = AMBIQ_SOURCE.read_text(encoding="utf-8")
    wrapper = re.search(r"static uint32_t\nmspi_cq_init\(.*?\n}\n", source, re.S)
    require(wrapper is not None, "upstream mspi_cq_init disappeared")
    require((len(wrapper.group(0).encode()), digest(wrapper.group(0).encode())) ==
            (398, "6179d2e4e0e36e63954708034fcd3e24f359952b02b123243ef7614d0aeea68f"),
            "upstream adapter identity changed")
    successor = re.search(r"static uint32_t\nmspi_cq_term\(.*?\n}\n", source, re.S)
    require(successor is not None and
            (len(successor.group(0).encode()), digest(successor.group(0).encode())) ==
            (453, "e9ec9c329833a40994012659b7559dcddcf279f951db4156c315b2d0c86231d6"),
            "successor identity changed")
    provider_text = PROVIDER_FRAGMENT.read_text(encoding="utf-8")
    provider = re.search(r"uint32_t\nam_hal_cmdq_init\(.*?\n}\n", provider_text, re.S)
    require(provider is not None and
            (len(provider.group(0).encode()), digest(provider.group(0).encode())) ==
            (1521, "651a9da33b3fefc16a5f1d5f2ce95ae4030939d991bb4a168bc7a58a7c958390"),
            "authenticated CMDQ provider fragment changed")
    for token in ("AM_HAL_CMDQ_IF_MAX", "cmdQSize < 2", "gAmHalCmdq[hwIf]",
                  "gAmHalCmdQReg[hwIf]", "*ppHandle = pCmdQ"):
        require(token in provider.group(0), f"provider semantic token missing: {token}")
    header = CMDQ_HEADER.read_text(encoding="utf-8")
    for token in ("AM_HAL_CMDQ_IF_MSPI0", "AM_HAL_CMDQ_IF_MSPI3",
                  "am_hal_cmdq_cfg_t", "am_hal_cmdq_init(am_hal_cmdq_if_e hwIf"):
        require(token in header, f"CMDQ ABI token missing: {token}")

    expected_builds = {
        ("/usr/bin/clang", False): (40, "eab31502d7ca042cdbb3c646be9426b8ce2108b0381a7a2bdaa872e8257012ae"),
        ("/usr/bin/clang", True): (44, "747f4344fbd039cf5f0fa93e55c3748000925237f7410304164b2eb3c491c413"),
    }
    homebrew = Path("/opt/homebrew/opt/llvm@22/bin/clang")
    if homebrew.is_file():
        expected_builds[(str(homebrew), False)] = expected_builds[("/usr/bin/clang", False)]
        expected_builds[(str(homebrew), True)] = expected_builds[("/usr/bin/clang", True)]
    objcopy = llvm_tool("llvm-objcopy")
    objdump = llvm_tool("llvm-objdump")
    with tempfile.TemporaryDirectory(prefix="open-cfw-mspi-cq-init-") as raw:
        output = Path(raw)
        for (clang, short_enums), expected in expected_builds.items():
            built = build_profile(clang, objcopy, objdump, output, short_enums)
            require((len(built), digest(built)) == expected,
                    f"reviewed semantic build changed under {clang}, short={short_enums}")
            require(built != stock, "toolchain mismatch unexpectedly disappeared")

    boundary_text = BOUNDARY.read_text(encoding="utf-8") + HEADER.read_text(encoding="utf-8")
    for token in ("SPDX-License-Identifier: MIT", "EXACT_TOOLCHAIN_UNRESOLVED",
                  "0x00423F28U", "0x00427794U", "0x2001CAA0U", "0x00430880U",
                  "short-enum ABI options", "BSD-3-Clause"):
        require(token in boundary_text, f"typed boundary token missing: {token}")

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    routed = overlay.get("in_place_leaves", []) + overlay.get("relocated_leaves", [])
    production = [entry for entry in routed if entry.get("runtime_address") == ENTRY]
    require(len(production) == 1 and
            production[0]["function"] == "open_cfw_bootloader_mspi_cq_init_423f28",
            "CQ-init production route changed")
    with tempfile.TemporaryDirectory(prefix="open-cfw-mspi-cq-production-") as raw:
        output = Path(raw)
        subprocess.run(["python3", str(BUILDER), "--output-dir", str(output)],
                       cwd=ROOT, check=True, capture_output=True, text=True)
        report = json.loads((output / "build-report.json").read_text(encoding="utf-8"))
    leaf = next(item for item in report["in_place_leaves"]
                if item["extraction"]["runtime_address"] == ENTRY)
    extraction = leaf["extraction"]
    require((extraction["size"], extraction["sha256"],
             extraction["unrelocated_sha256"], extraction["relocation_count"])
            == (44, SPANS["mspi_cq_init"][2],
                "af220b4ac459468b86a84c43c1321c96d0f247c4b102c89ffd7ca7b614717fc0", 1),
            "CQ-init exact production extraction changed")
    require([(row["offset"], row["target_address"])
             for row in extraction["relocations"]] == [(38, 0x00427794)],
            "CQ-init relocation contract changed")
    component = report["component"]
    require(
        component["source_owned_bytes"] + component["opaque_base_bytes"]
        + component["generated_patch_site_bytes"]
        + component["generated_alignment_bytes"] == component["size"],
        "CQ-init production byte conservation changed",
    )
    core = json.loads(CORE_MANIFEST.read_text(encoding="utf-8"))
    regions = core["component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {row["name"]: row for row in regions}
    source_name = "bootloader_mspi_cq_init_423f28_source_in_place"
    successor_name = "bootloader_mspi_cq_term_423f54_source_in_place"
    require(source_name in by_name, "CQ-init production region disappeared")
    require(successor_name in by_name, "CQ-term successor region disappeared")
    source_region = by_name[source_name]
    successor = by_name[successor_name]
    require((source_region["target_address"], source_region["size"],
             source_region["address_status"])
            == (0x00423F28, 44, "source_compiled"),
            "CQ-init production ownership changed")
    require(
        (successor["target_address"], successor["size"],
         successor["address_status"])
        == (0x00423F54, 58, "source_compiled"),
        "CQ-term local successor ownership changed",
    )

    return {
        "status": "implemented-in-source / hardware-validation-deferred-by-project-direction",
        "identity": {
            "function": "mspi_cq_init", "provider": "am_hal_cmdq_init",
            "upstream_commit": provenance["upstream"]["selected_commit"],
            "provider_blob": "0a286e565cad27cef801c389b5dedae826a2669a",
            "license": "BSD-3-Clause",
        },
        "stock": {"start": ENTRY, "end": 0x00423F54, "bytes": 44,
                  "sole_caller": 0x0042509C},
        "abi": {"cmdq_interface_base": 8, "short_enum_bytes": 1,
                "config_size_entries": "length / 2", "priority": 1,
                "mspi_state_base": 0x2001CAA0, "mspi_state_stride": 0x8D0,
                "cmdq_handle_offset": 0x828},
        "provider": {"start": 0x00427794, "end": 0x00427878,
                     "state_base": 0x200262F0, "register_table": 0x00430880,
                     "register_table_bytes": 480},
        "toolchain": {"upstream_default_enum_bytes": 40,
                      "upstream_short_enum_bytes": 44,
                      "production_bytes": 44, "exact_match": True,
                      "method": "typed clean-room host model plus exact target mnemonic body"},
        "production": {"routed": True,
                       "next_frontier": successor["target_address"],
                       "next_identity": successor["function"],
                       "local_successor": {
                           "start": successor["target_address"],
                           "end": successor["target_address"] + successor["size"],
                           "address_status": successor["address_status"],
                       },
                       "source_owned_bytes": component["source_owned_bytes"],
                       "retained_official_bytes": component["opaque_base_bytes"]},
        "hardware_validation": "deferred by project direction",
        "hardware_gate": {
            "required_future_evidence": "authorized G2 qualification exercising command-queue initialization, all MSPI interfaces, retained handle publication, and cold boot",
        },
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
        print("Bootloader MSPI CQ-init 0x423f28: implemented in exact source")
        print("  physical validation: deferred by project direction")
        print("  exact local successor: 0x423f54 (CQ term, source-owned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
