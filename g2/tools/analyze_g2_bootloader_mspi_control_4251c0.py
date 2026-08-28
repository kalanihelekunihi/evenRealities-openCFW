#!/usr/bin/env python3
"""Authenticate production closure of the G2 bootloader MSPI control body."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import apollo_overlay
from analyze_g2_apollo510_mspi_triplet_candidate import run_audit as triplet_audit
from analyze_g2_bootloader_mspi_device_configure_424120 import decode_bl


ROOT = Path(__file__).resolve().parents[1]
BOOT_BASE = 0x00410000
BOOT_START = 0x004251C0
BOOT_END = 0x004262E0
MAIN_BASE = 0x00438000
MAIN_START = 0x004C0F78
MAIN_END = 0x004C2098
BOOT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN_PACKAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
REMOVED_TRANSCRIPT = ROOT / "components/bootloader/core_overlay/runtime_mspi_control_4251c0.c"
CANDIDATE = ROOT / "research/admission/bootloader_mspi_control_4251c0/runtime_bootloader_mspi_control_candidate.c"
CANDIDATE_HEADER = CANDIDATE.with_suffix(".h")
HOST_FIXTURE = CANDIDATE.parent / "host_fixture.c"
UPSTREAM = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
UPSTREAM_HEADER = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.h"
UPSTREAM_LICENSE = ROOT / "third_party/ambiqsuite-apollo510/LICENSE"
ADAPTER = ROOT / "components/shared/ambiqsuite/runtime_apollo510_mspi_stock_abi_candidate.c"
BOUNDARY = ROOT / "tools/manifests/g2-bootloader-mspi-control-4251c0.tsv"
DOCUMENT = ROOT / "docs/research/g2-bootloader-mspi-control-4251c0-4262e0-source-closure.md"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"

BOOT_SHA = "d936cfa583f4d53150c86b30217e2e08ed0698793f13735e365f5a7d0cce0d48"
MAIN_SHA = "a9676ac0717977a1d4be1a730ba02d5dfefc3da780721c8b3ccd3543ca80bf7c"
CALLERS = (0x0041FF5A, 0x00420036, 0x00420EE8, 0x00420F48)
PINS = {
    CANDIDATE: (8229, "4914e60172be80f6e3743ffb77fd4fe500ed3b0a1af691c4ac21cf163c57a85a"),
    CANDIDATE_HEADER: (1728, "dedf0acee5de7e6dc219b5476b479d56c4d576e7d717c54a3b520bf900d5ddd5"),
    HOST_FIXTURE: (3647, "5824f00d57992364d51b0ded5c82f92cad7124aaffad5f9bb1d420811046b448"),
    UPSTREAM: (168473, "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"),
    UPSTREAM_HEADER: (36982, "2a682bb7c1618982d6a802f3220a38696cd594c89d90e64b1a698d226b0a557b"),
    UPSTREAM_LICENSE: (1525, "0770df5c1956b75715604d5788804eabfc293fc61d5dbbec498c6d379a63755f"),
    ADAPTER: (2930, "f84c982da08e189d5c1c1207e18c70d7b65bb36717139ce99da3cbaabd240fc3"),
    BOUNDARY: (2351, "53a8e692d35b0a97d57d4c7cb16b5d42e5ba68b425e36b526cc94fad6215e061"),
    DOCUMENT: (1744, "60b651e1699616224dcc6b881c4c1a49eabcbab02b583a79eeff713ae6d67289"),
}
FLAGS = (
    "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra",
    "-Werror", "-fno-ident",
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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_function(path: Path) -> tuple[bytes, int]:
    data, sections = apollo_overlay.parse_elf32(path)
    section = apollo_overlay.section_named(
        sections, ".text.open_cfw_bootloader_mspi_control_4251c0"
    )
    body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
    relocations = sum(
        int(item["size"]) // 8
        for item in sections
        if int(item["type"]) == 9 and int(item["info"]) == int(section["index"])
    )
    return body, relocations


def audit() -> dict[str, object]:
    require(not REMOVED_TRANSCRIPT.exists(), "raw executable transcript returned to public component source")
    for path, expected in PINS.items():
        data = path.read_bytes()
        require((len(data), sha256(data)) == expected, f"pin changed: {path.relative_to(ROOT)}")

    boot_image = BOOT_IMAGE.read_bytes()
    boot_body = boot_image[BOOT_START - BOOT_BASE:BOOT_END - BOOT_BASE]
    require((len(boot_body), sha256(boot_body)) == (4384, BOOT_SHA), "boot control body changed")
    main_package = MAIN_PACKAGE.read_bytes()
    require(len(main_package) == 3_523_396, "main package envelope changed")
    main_payload = main_package[32:]
    main_body = main_payload[MAIN_START - MAIN_BASE:MAIN_END - MAIN_BASE]
    require((len(main_body), sha256(main_body)) == (4384, MAIN_SHA), "main control body changed")
    differences = tuple(index for index, pair in enumerate(zip(boot_body, main_body)) if pair[0] != pair[1])
    require((len(differences), 4384 - len(differences)) == (87, 4297), "cross-image identity changed")

    callers = tuple(
        address
        for address in range(BOOT_BASE, BOOT_BASE + len(boot_image) - 3, 2)
        if decode_bl(boot_image, address) == BOOT_START
    )
    require(callers == CALLERS, "boot control callers changed")

    upstream = UPSTREAM.read_text()
    header = UPSTREAM_HEADER.read_text()
    for token in (
        "am_hal_mspi_control", "AM_HAL_MSPI_REQ_APBCLK", "AM_HAL_MSPI_REQ_XIP_CONFIG",
        "AM_HAL_MSPI_REQ_DEVICE_CONFIG", "AM_HAL_MSPI_REQ_SET_INSTR_ADDR_LEN",
    ):
        require(token in upstream or token in header, f"upstream control token changed: {token}")
    require("Copyright (c) 2025, Ambiq Micro" in UPSTREAM_LICENSE.read_text(), "upstream license changed")
    triplet = triplet_audit()
    control = triplet["triplet"]["0x004C0F78"]
    require(
        (control["end_exclusive"], control["envelope_bytes"], control["upstream_function"])
        == (MAIN_END, 4384, "am_hal_mspi_control"),
        "independent main control attribution changed",
    )
    require(triplet["request_abi"]["stock_only_unsupported"] == [10, 11], "request ABI changed")
    require(triplet["request_abi"]["all_observed_requests_supported"], "observed request translation changed")

    profiles: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="open-cfw-boot-control-") as directory:
        for profile, (compiler, version_prefix) in PROFILES.items():
            version = subprocess.run(
                [str(compiler), "--version"], check=True, capture_output=True, text=True
            ).stdout.splitlines()[0]
            require(version.startswith(version_prefix), f"{profile} compiler changed")
            profiles[profile] = version

        host_library = Path(directory) / ("control.dylib" if sys.platform == "darwin" else "control.so")
        host_command = [
            "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            str(CANDIDATE), str(HOST_FIXTURE),
        ]
        host_command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        subprocess.run([*host_command, "-o", str(host_library)], check=True, capture_output=True, text=True)
        host = ctypes.CDLL(str(host_library))
        host.open_cfw_test_control_run_valid.argtypes = [ctypes.c_uint32]
        host.open_cfw_test_control_run_valid.restype = ctypes.c_uint32
        for request in range(40):
            require(host.open_cfw_test_control_run_valid(request) == 0, f"semantic request {request} failed")
            require(host.open_cfw_test_control_run_valid(request | 0x123400) == 0, f"semantic low-byte alias {request} failed")
        require(host.open_cfw_test_control_run_valid(40) == 6, "semantic sentinel did not fail closed")
        require(host.open_cfw_test_control_run_valid(255) == 6, "semantic invalid request did not fail closed")

    leaves = {item["function"]: item for item in json.loads(OVERLAY.read_text())["in_place_leaves"]}
    require("open_cfw_bootloader_mspi_control_4251c0" not in leaves,
            "deleted transcript remains production-routed")
    regions = json.loads(MANIFEST.read_text())["component_overrides"]["apollo_bootloader"]["regions"]
    retained = next(item for item in regions if item["name"] == "bootloader_opaque_after_easylogger_transport")
    require(
        (retained["target_address"], retained["size"], retained["address_status"])
        == (0x424A5A, 6828, "official_blob"),
        "retained official MSPI boundary changed",
    )
    require(retained["target_address"] <= BOOT_START and
            BOOT_END <= retained["target_address"] + retained["size"],
            "control span escaped retained official boundary")

    with tempfile.TemporaryDirectory(prefix="open-cfw-boot-control-component-") as directory:
        subprocess.run(
            ["python3", str(BUILDER), "--output-dir", directory],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        component = json.loads((Path(directory) / "build-report.json").read_text())["component"]
    require(component["source_owned_bytes"] + component["opaque_base_bytes"] == 147296, "component accounting changed")
    require(component["source_owned_in_place_bytes"] <= component["source_owned_bytes"], "in-place accounting changed")

    return {
        "status": "semantic-candidate / production-retained-official-boundary",
        "function": {"start": BOOT_START, "end": BOOT_END, "bytes": 4384, "sha256": BOOT_SHA},
        "cross_image": {
            "main_start": MAIN_START,
            "main_end": MAIN_END,
            "main_sha256": MAIN_SHA,
            "identical_bytes": 4297,
            "address_coupled_bytes": 87,
            "difference_runs": 53,
        },
        "callers": list(callers),
        "profiles": profiles,
        "production": {
            "routed": False,
            "source_owned_bytes": component["source_owned_bytes"],
            "retained_official_bytes": component["opaque_base_bytes"],
            "boundary_status": "official_blob",
        },
        "semantic_model": {"valid_stock_requests": 40, "low_byte_aliases": 40, "invalid_requests_fail_closed": True},
        "hardware_validation": "deferred by project direction",
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    result = audit()
    print(
        json.dumps(result, indent=2, sort_keys=True)
        if parser.parse_args().json
        else "Bootloader MSPI control: semantic candidate; production retains authenticated official bytes"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"bootloader MSPI control audit failed: {error}")
