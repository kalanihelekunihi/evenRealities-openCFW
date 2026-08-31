#!/usr/bin/env python3
"""Authenticate and classify the bootloader post-MSPI frontier.

The audit is software-only.  It compiles and relocates the two admitted,
reviewable Thumb-2 AmbiqSuite realizations, checks their semantic provider
edges, checks the exhaustive byte ledger, and verifies production ownership
without probing, executing MMIO, flashing, signing, or assembling a release
package.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apollo_overlay


ROOT = Path(__file__).resolve().parents[1]
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_interrupt_power_426536.S"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILD_REPORT = ROOT / "components/bootloader/core_overlay/build/build-report.json"
AMBIQ_SOURCE = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
AMBIQ_HEADER = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.h"
AMBIQ_LICENSE = ROOT / "third_party/ambiqsuite-apollo510/LICENSE"
AMBIQ_PROVENANCE = ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json"

PINS = {
    BOOT: (148_599, "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"),
    MAIN: (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"),
    SOURCE: (44_692, "a1b9c4a5519a59329cb1c2a3bad6ab7eb973db56903a04fbed489c678a1f3d81"),
    CENSUS: (75_754, "76aa4c93419ee7055e6023ae28fa3382551be46fc72456ae700f0a1529780ded"),
    AMBIQ_SOURCE: (168_473, "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"),
    AMBIQ_HEADER: (36_982, "2a682bb7c1618982d6a802f3220a38696cd594c89d90e64b1a698d226b0a557b"),
    AMBIQ_LICENSE: (1_525, "0770df5c1956b75715604d5788804eabfc293fc61d5dbbec498c6d379a63755f"),
    AMBIQ_PROVENANCE: (18_060, "ee9eb7e9ab8465bbe8b836b9baf04d6a10d470091bb60fe51f0771fecf36bdec"),
}

FUNCTIONS = {
    "open_cfw_bootloader_mspi_interrupt_service_426536": {
        "start": 0x00426536,
        "end": 0x004267FE,
        "sha256": "baf487db99da530690cd9100a3f10947ce5bbbca07dfc93cd76ff57bc87ad313",
        "upstream": "am_hal_mspi_interrupt_service",
        "main_start": 0x004C240E,
        "main_sha256": "8c43c0d8fd418e04cf808e80d00867981dc2a3eaefb23ee0227ed39538484164",
        "identical_bytes": 692,
        "difference_runs": 10,
        "callers": (0x0041FE22,),
        "provider_edges": (
            (0xEA, 0x0042403E), (0x136, 0x00422364),
            (0x16C, 0x00427A56), (0x224, 0x00423FAC),
            (0x26C, 0x00427B38), (0x278, 0x00423F8E),
            (0x288, 0x00423FAC), (0x2B8, 0x00422364),
        ),
    },
    "open_cfw_bootloader_mspi_power_control_426808": {
        "start": 0x00426808,
        "end": 0x00426BFE,
        "sha256": "80479d7c73fd0238da60b347069e233490562e35122272a235c35827f1e9084a",
        "upstream": "am_hal_mspi_power_control",
        "main_start": 0x004C26E0,
        "main_sha256": "4567f43c1d695764bc62c881fbf0bc9c3766c06e9d16d66454f1b87ec4b0ae5b",
        "identical_bytes": 985,
        "difference_runs": 15,
        "callers": (0x0041FE3E, 0x0041FE54, 0x004202AC),
        "provider_edges": (
            (0x4A, 0x0041BF84), (0x6C, 0x004222F0),
            (0x7E, 0x004249A0), (0x1EC, 0x00423F8E),
            (0x206, 0x004222F0), (0x216, 0x004249A0),
            (0x39E, 0x00423FAC), (0x3AE, 0x00426484),
            (0x3C6, 0x0041D1C0), (0x3D0, 0x0041C17A),
            (0x3DC, 0x004249A0), (0x3E6, 0x004223D8),
        ),
    },
}

POOLS = (
    (0x004267FE, 0x00426808, "f0ef1fedd08c40bdcdbac2afa7a8df77f7a1b6cebf3ccbe24145340afa295b16"),
    (0x00426BFE, 0x00426C10, "6d01aee7b0ea94693ad3e39e729d72dbdcf694fa0bb121442d026ca719b3d5c4"),
)

EXPECTED_ROWS = 253
EXPECTED_DISPOSITIONS = {
    "source_owned_production": (2, 1_726),
    "retained_typed_data": (2, 28),
    "cross_image_exact_source_candidate": (58, 4_550),
    "typed_unresolved_executable": (124, 19_534),
    "typed_ambiguous_control_flow_envelope": (1, 188),
    "typed_nonentry_mixed_or_data": (66, 31_127),
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
    "linux-clang": (Path("/opt/homebrew/opt/llvm@22/bin/clang"), "Homebrew clang version 22.1.8"),
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def decode_thumb_bl(payload: bytes, address: int, base: int = BOOT_BASE) -> int | None:
    offset = address - base
    if offset < 0 or offset + 4 > len(payload):
        return None
    first, second = struct.unpack_from("<HH", payload, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22)
                 | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFFFFFF


def direct_callers(payload: bytes, target: int) -> tuple[int, ...]:
    return tuple(
        address
        for address in range(BOOT_BASE, BOOT_BASE + len(payload) - 3, 2)
        if decode_thumb_bl(payload, address) == target
    )


def difference_runs(left: bytes, right: bytes) -> int:
    indexes = [index for index, pair in enumerate(zip(left, right)) if pair[0] != pair[1]]
    return sum(index == indexes[0] or index != indexes[pos - 1] + 1
               for pos, index in enumerate(indexes)) if indexes else 0


def extract_section(path: Path, name: str) -> tuple[bytes, int]:
    payload, sections = apollo_overlay.parse_elf32(path)
    section = apollo_overlay.section_named(sections, ".text." + name)
    body = payload[int(section["offset"]):int(section["offset"]) + int(section["size"])]
    relocations = sum(
        int(item["size"]) // 8
        for item in sections
        if int(item["type"]) == 9 and int(item["info"]) == int(section["index"])
    )
    return body, relocations


def audit() -> dict:
    authenticated: dict[Path, bytes] = {}
    for path, expected in PINS.items():
        payload = path.read_bytes()
        require((len(payload), sha256(payload)) == expected, f"pin changed: {path.relative_to(ROOT)}")
        authenticated[path] = payload
    boot = authenticated[BOOT]
    main = authenticated[MAIN]

    rows = list(csv.DictReader(authenticated[CENSUS].decode().splitlines(), delimiter="\t"))
    require(len(rows) == EXPECTED_ROWS, "frontier row count changed")
    cursor = 0x00426536
    disposition_counts: dict[str, int] = {}
    disposition_bytes: dict[str, int] = {}
    for row in rows:
        start, end, size = int(row["start"], 16), int(row["end"], 16), int(row["size"])
        require(start == cursor and end > start and size == end - start, f"partition drift: {row['name']}")
        body = boot[start - BOOT_BASE:end - BOOT_BASE]
        require(sha256(body) == row["sha256"], f"span hash changed: {row['name']}")
        if row["disposition"] == "cross_image_exact_source_candidate":
            require(main.find(body) >= 0, f"cross-image candidate disappeared: {row['name']}")
        disposition_counts[row["disposition"]] = disposition_counts.get(row["disposition"], 0) + 1
        disposition_bytes[row["disposition"]] = disposition_bytes.get(row["disposition"], 0) + size
        cursor = end
    require(cursor == 0x00434477, "frontier partition no longer reaches stock EOF")
    require(sum(disposition_bytes.values()) == 57_153, "frontier byte conservation changed")
    require({key: (disposition_counts.get(key, 0), disposition_bytes.get(key, 0))
             for key in EXPECTED_DISPOSITIONS} == EXPECTED_DISPOSITIONS,
            "frontier classification changed")

    upstream = authenticated[AMBIQ_SOURCE].decode()
    mnemonic_source = authenticated[SOURCE].decode()
    require("BSD 3-Clause License" in authenticated[AMBIQ_LICENSE].decode(), "Ambiq license changed")
    provenance = json.loads(authenticated[AMBIQ_PROVENANCE])
    require(provenance["upstream"]["selected_commit"] ==
            "5efc0228528a8adce5eae0d226fac85d2551eb3b",
            "Ambiq upstream commit changed")
    require(all(token not in mnemonic_source for token in (".byte", ".short", ".word")),
            "executable raw-encoding directive reintroduced")
    for token in (".syntax unified", ".thumb", ".cpu cortex-m55",
                  "ABI r0=pHandle", "am_hal_mspi_interrupt_service",
                  "am_hal_mspi_power_control"):
        require(token in mnemonic_source, f"mnemonic source proof token missing: {token}")

    overlay = json.loads(OVERLAY.read_text())
    configured = {item["function"]: item for item in overlay["in_place_leaves"]}
    profiles: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="open-cfw-post-mspi-audit-") as directory:
        for profile, (compiler, version_prefix) in PROFILES.items():
            version = subprocess.run([str(compiler), "--version"], check=True,
                                     capture_output=True, text=True).stdout.splitlines()[0]
            require(version.startswith(version_prefix), f"{profile} compiler changed")
            for name, facts in FUNCTIONS.items():
                body, leaf_report = apollo_overlay.compile_in_place_leaf(
                    root=ROOT,
                    clang=str(compiler),
                    leaf_config=configured[name],
                    object_path=Path(directory) / f"{profile}-{name}.o",
                    toolchain_profile=profile,
                )
                extraction = leaf_report["extraction"]
                stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
                require((len(body), sha256(body), extraction["relocation_count"]) ==
                        (facts["end"] - facts["start"], facts["sha256"],
                         len(facts["provider_edges"])),
                        f"{profile} compiled body changed: {name}")
                require(body == stock, f"{profile} body is not stock-exact: {name}")
            profiles[profile] = version

    function_results = {}
    for name, facts in FUNCTIONS.items():
        require(facts["upstream"] + "(" in upstream, f"upstream function disappeared: {facts['upstream']}")
        stock = boot[facts["start"] - BOOT_BASE:facts["end"] - BOOT_BASE]
        main_body = main[facts["main_start"] - MAIN_BASE:
                         facts["main_start"] - MAIN_BASE + len(stock)]
        require(sha256(stock) == facts["sha256"], f"stock body changed: {name}")
        require(sha256(main_body) == facts["main_sha256"], f"main analogue changed: {name}")
        require(sum(a == b for a, b in zip(stock, main_body)) == facts["identical_bytes"],
                f"cross-image identity count changed: {name}")
        require(difference_runs(stock, main_body) == facts["difference_runs"],
                f"cross-image difference topology changed: {name}")
        require(direct_callers(boot, facts["start"]) == facts["callers"],
                f"caller topology changed: {name}")
        function_results[name] = {
            "start": facts["start"], "end_exclusive": facts["end"],
            "bytes": len(stock), "sha256": facts["sha256"],
            "upstream": facts["upstream"], "main_analogue": facts["main_start"],
            "identical_bytes": facts["identical_bytes"],
            "address_coupled_difference_bytes": len(stock) - facts["identical_bytes"],
            "direct_call_sites": list(facts["callers"]),
            "provider_edges": [
                {"offset": offset, "target_address": target}
                for offset, target in facts["provider_edges"]
            ],
        }
    for start, end, expected in POOLS:
        body = boot[start - BOOT_BASE:end - BOOT_BASE]
        require(sha256(body) == expected, f"literal pool changed: {start:#x}")
        require(struct.pack("<I", start | 1) not in boot, f"pool gained stored entry pointer: {start:#x}")

    for name, facts in FUNCTIONS.items():
        item = configured[name]
        require((item["runtime_address"], item["expected"]["size"],
                 item["expected"]["sha256"], item["source"]["license"]) ==
                (facts["start"], facts["end"] - facts["start"], facts["sha256"], "BSD-3-Clause"),
                f"production overlay registration changed: {name}")
        require(tuple((entry["offset"], entry["target_address"])
                      for entry in item["relocations"]) == facts["provider_edges"],
                f"semantic provider-edge contract changed: {name}")

    manifest = json.loads(MANIFEST.read_text())
    regions = manifest["component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {item["name"]: item for item in regions}
    expected_regions = {
        "bootloader_mspi_interrupt_service_426536_source_in_place": (0x00426536, 712, "source_compiled"),
        "bootloader_mspi_interrupt_service_literal_pool_4267fe_opaque": (0x004267FE, 10, "official_blob"),
        "bootloader_mspi_power_control_426808_source_in_place": (0x00426808, 1014, "source_compiled"),
        "bootloader_opaque_before_clkmgr_divider_entries": (0x00426BFE, 38, "official_blob"),
        "bootloader_clkmgr_hfrc2_uq15_divider_source_redirect": (0x00426C24, 42, "generated_source_entry_replacement"),
        "bootloader_clkmgr_hfrc_integer_divider_source_redirect": (0x00426C4E, 10, "generated_source_entry_replacement"),
        "bootloader_opaque_after_mspi_power_control_426bfe": (0x00426C58, 55_327, "official_blob"),
    }
    for name, expected in expected_regions.items():
        item = by_name[name]
        require((item["target_address"], item["size"], item["address_status"]) == expected,
                f"core manifest region changed: {name}")

    report = json.loads(BUILD_REPORT.read_text())
    component = report["component"]
    require((component["size"], component["sha256"]) ==
            (163_840, "f570bbf749b16043c8ccfc6eeae66fafaabf4146d5cc55f63d5fab729775ccad"),
            "canonical boot provider identity changed")
    require((component["source_owned_bytes"], component["opaque_base_bytes"],
             component["source_owned_in_place_bytes"]) == (27_925, 119_425, 12_232),
            "live source/official accounting changed")
    require(component["source_owned_bytes"] + component["opaque_base_bytes"] == 147_350,
            "boot source/official conservation changed")

    return {
        "component": "G2 Apollo bootloader post-MSPI frontier",
        "status": "classification-complete / two exact production source admissions / hardware validation blocked by unavailable physical evidence",
        "frontier": {"start": 0x00426536, "end_exclusive": 0x00434477, "bytes": 57_153},
        "classification": {
            "exhaustive": True, "unclassified_bytes": 0,
            "row_count": len(rows),
            "by_disposition": {key: {"spans": value[0], "bytes": value[1]}
                               for key, value in EXPECTED_DISPOSITIONS.items()},
        },
        "admission": {
            "license": "BSD-3-Clause", "production_routed": True,
            "upstream_commit": provenance["upstream"]["selected_commit"],
            "instruction_representation": "reviewable Thumb-2 mnemonics; no raw encoding directives",
            "source_owned_bytes": 1_726, "retained_literal_pool_bytes": 28,
            "functions": function_results,
        },
        "profiles": profiles,
        "boot_component": component,
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Post-MSPI frontier: 57,153 bytes exhaustively classified; 1,726 bytes exact BSD source")
        print("  hardware validation: blocked by unavailable physical evidence")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"post-MSPI frontier audit failed: {error}") from error
