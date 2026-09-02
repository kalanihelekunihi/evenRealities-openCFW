#!/usr/bin/env python3
"""Authenticate the G2 bootloader mspi_device_configure source closure."""

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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_device_configure_424120.c"
HEADER = ROOT / "components/bootloader/core_overlay/runtime_mspi_device_configure_424120.h"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_device_configure_host.c"
BOUNDARY = ROOT / "tools/manifests/g2-bootloader-mspi-device-configure-424120.tsv"
PROVENANCE = ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json"
UPSTREAM = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"

RUN_BASE = 0x00410000
ENTRY = 0x00424120
END = 0x0042488E
STOCK_SHA = "3b95c5af6c3c2140cc4e1522a1f284ae31825e4e35ae6c2427e0edba41774818"
TARGET_SIZE = 284
TARGET_SHA = "960b3d30653a94dd8b0c9037d9e0cdd53991d88c06a9d27cecf6576a0bbce97f"
CALLERS = (0x00425012, 0x004258E4)
INPUT_PINS = {
    SOURCE: (4188, "6ed08297ec6283b5ae48de7c2f1ab17c6ca8b2369e5f724ebed60f6fac18d262"),
    HEADER: (1331, "4842e22f3233f19e0edf383f1026726562b13cfaad14e42dfa2ccdb7296e313d"),
    FIXTURE: (2962, "7941270dc51fade28ed7a9f08c36055625a98bd524e517f921c0e33356454a05"),
    BOUNDARY: (1721, "569278d08f1d64adfb23082cb1161b61eff6bdb61dfe0b0404c0042dcec3cd75"),
}
FLAGS = (
    "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
    "-fno-jump-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident",
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


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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


def extract_body(path: Path) -> tuple[bytes, int]:
    data, sections = apollo_overlay.parse_elf32(path)
    section = apollo_overlay.section_named(
        sections, ".text.open_cfw_bootloader_mspi_device_configure_424120")
    body = data[int(section["offset"]):int(section["offset"]) + int(section["size"])]
    relocation_count = sum(
        int(row["size"]) // 8 for row in sections
        if int(row["type"]) == 9 and int(row["info"]) == int(section["index"])
    )
    return body, relocation_count


def compile_profiles() -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    with tempfile.TemporaryDirectory(prefix="open-cfw-device-config-audit-") as raw:
        for profile, (compiler, version_prefix) in PROFILES.items():
            require(compiler.is_file(), f"reviewed {profile} compiler unavailable")
            version = subprocess.run([str(compiler), "--version"], check=True,
                                     capture_output=True, text=True).stdout.splitlines()[0]
            require(version.startswith(version_prefix),
                    f"reviewed {profile} compiler identity changed")
            output = Path(raw) / f"{profile}.o"
            subprocess.run([str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(output)],
                           check=True, capture_output=True, text=True)
            body, relocation_count = extract_body(output)
            require((len(body), digest(body)) == (TARGET_SIZE, TARGET_SHA),
                    f"{profile} structured target body changed")
            require(relocation_count == 0, f"{profile} unexpectedly emitted relocations")
            reports[profile] = {
                "version": version, "body_size": len(body),
                "sha256": digest(body), "relocation_count": relocation_count,
            }
    return reports


def audit() -> dict[str, Any]:
    for path, expected in INPUT_PINS.items():
        payload = path.read_bytes()
        require((len(payload), digest(payload)) == expected,
                f"input pin changed: {path.relative_to(ROOT)}")
    image = OFFICIAL.read_bytes()
    stock = image[ENTRY - RUN_BASE:END - RUN_BASE]
    require((len(stock), digest(stock)) == (1902, STOCK_SHA),
            "stock device-configure body changed")
    callers = tuple(address for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
                    if decode_bl(image, address) == ENTRY)
    require(callers == CALLERS, "device-configure caller topology changed")
    require(struct.unpack_from("<I", image, 0x0042499C - RUN_BASE)[0] == 0x40060000,
            "device-configure MSPI base literal changed")
    successor = image[END - RUN_BASE:0x00424976 - RUN_BASE]
    require((len(successor), digest(successor)) ==
            (232, "e8323e8e0ac6f59465ce1d30087eb6f4a2e3de336c45bff3e6954325a2e32fee"),
            "mspi_piomixed_configure successor changed")
    residual = image[END - RUN_BASE:0x00426506 - RUN_BASE]
    require((len(residual), digest(residual)) ==
            (7288, "8713fce0ce450cc46ceec01e4bfce016479b24e76e2e70c939e8a93b7df40601"),
            "residual official frontier changed")

    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    require(provenance["license"] == "BSD-3-Clause", "upstream license changed")
    upstream = UPSTREAM.read_text(encoding="utf-8")
    for token in ("mspi_device_configure(am_hal_mspi_state_t *pMSPIState)",
                  "AM_HAL_MSPI_FLASH_SERIAL_CE0", "AM_HAL_MSPI_FLASH_HEX_DDR_CE1",
                  "AM_HAL_MSPI_FLASH_OCTAL_CE0_1_8_8", "MSPI0_PADOUTEN_OUTEN_HEX"):
        require(token in upstream, f"upstream identity token changed: {token}")
    source_text = SOURCE.read_text(encoding="utf-8")
    require(".byte" not in source_text and "__asm__" not in source_text,
            "structured production source regressed to raw executable encoding")
    profiles = compile_profiles()

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    routed = [row for row in overlay["in_place_leaves"]
              if row["function"] == "open_cfw_bootloader_mspi_device_configure_424120"]
    require(len(routed) == 1, "structured device configure is not uniquely routed")
    routed_leaf = routed[0]
    require((routed_leaf["runtime_address"], routed_leaf["expected"]["size"],
             routed_leaf["expected"]["sha256"]) ==
            (ENTRY, TARGET_SIZE, TARGET_SHA),
            "production device-configure route changed")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    regions = manifest["component_overrides"]["apollo_bootloader"]["regions"]
    by_name = {row["name"]: row for row in regions}
    source_region = by_name["bootloader_mspi_device_configure_424120_source_in_place"]
    require((source_region["target_address"], source_region["size"],
             source_region["address_status"]) ==
            (ENTRY, TARGET_SIZE, "source_compiled"),
            "source-owned device-configure boundary changed")
    retained = by_name[
        "bootloader_mspi_device_configure_tail_42423c_and_piomixed_42488e_official"]
    require((retained["target_address"], retained["size"],
             retained["address_status"]) ==
            (ENTRY + TARGET_SIZE, 1850, "official_blob"),
            "retained unreachable tail and successor boundary changed")
    with tempfile.TemporaryDirectory(prefix="open-cfw-device-config-component-") as raw:
        subprocess.run(["python3", str(BUILDER), "--output-dir", raw], cwd=ROOT,
                       check=True, capture_output=True, text=True)
        report = json.loads((Path(raw) / "build-report.json").read_text(encoding="utf-8"))
    component = report["component"]
    require(component["source_owned_bytes"] + component["opaque_base_bytes"] == 146994,
            "production device-configure byte conservation changed")
    require(component["source_owned_in_place_bytes"] <= component["source_owned_bytes"],
            "production device-configure in-place accounting changed")
    return {
        "status": "structured-source-dual-profile / production-source-in-place / hardware-validation-blocked-by-unavailable-physical-evidence",
        "stock": {"start": ENTRY, "end": END, "bytes": len(stock), "sha256": STOCK_SHA},
        "identity": {"function": "mspi_device_configure",
                     "upstream_commit": provenance["upstream"]["selected_commit"],
                     "license": "BSD-3-Clause", "supported_modes": 26},
        "callers": list(callers),
        "abi": {"module_offset": 4, "clock_on_d4_offset": 9,
                "device_configuration_offset": 10,
                "mspi0_base": 0x40060000, "module_stride": 0x1000,
                "pad_output_offset": 0x44, "device_config_offset": 0x84,
                "device_xip_offset": 0x90},
        "profiles": profiles,
        "production": {"routed": True,
                       "compiled_bytes": TARGET_SIZE,
                       "compiled_sha256": TARGET_SHA,
                       "source_owned_bytes": component["source_owned_bytes"],
                       "retained_official_bytes": component["opaque_base_bytes"],
                       "boundary_status": "source_compiled",
                       "next_frontier": END},
        "next_frontier": {"start": END, "end": 0x00424976,
                          "identity": "mspi_piomixed_configure", "bytes": 232,
                          "status": "official_blob"},
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_gate": {"blocking_condition":
                          "directed hardware testing is blocked by unavailable physical evidence",
                          "required_future_evidence":
                          "authorized all-mode MSPI register, pad, XIP, clock-on-D4, and cold-boot qualification"},
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
        print("Bootloader mspi_device_configure 0x424120: structured source routed in place")
        print("  next sequential frontier: 0x42488e (mspi_piomixed_configure)")
        print("  physical validation: blocked by unavailable physical evidence")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader device-configure audit failed: {exc}")
