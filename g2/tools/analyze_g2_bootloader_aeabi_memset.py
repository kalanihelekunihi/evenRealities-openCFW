#!/usr/bin/env python3
"""Fail-closed source/build audit for the G2 bootloader byte-fill entry."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/bootloader/core_overlay"
SOURCE = COMPONENT / "runtime_aeabi_memset.c"
HEADER = COMPONENT / "runtime_aeabi_memset.h"
CONFIG = COMPONENT / "overlay.json"
BUILDER = COMPONENT / "build_component.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

RUN_BASE = 0x00410000
STOCK_ADDRESS = 0x0041560C
STOCK_SIZE = 102
STOCK_SHA256 = "34da1a99d5cb56ca41cfaff98190ced2a7767f53cd95c53c504009566e9ca10a"
FUNCTION = "open_cfw_bootloader_aeabi_memset"
FUNCTION_ADDRESS = 0x00434824
FUNCTION_SIZE = 12
FUNCTION_SHA256 = "57aa3a55299e81fefe7ae3b0807a149cf0d3d6c56adfcd6bf507f3850e6c229e"
SOURCE_PINS = {
    SOURCE: (522, "d2e8eb19cc43bd75995bc75f2a404768612376c1d990a80ab2e8121998183c22"),
    HEADER: (338, "20da14c2a8ff377971c731003ab011ac7bf46ba6a3f9d0619a570457ba65ce49"),
}
CALLERS = (
    0x00410538, 0x00410E68, 0x004110B6, 0x004112D8, 0x004116A8,
    0x00412488, 0x00412950, 0x00414548, 0x004175D6, 0x00417790,
    0x0041779E, 0x0041783A, 0x00417CDC, 0x00417D46, 0x00417DAC,
    0x0041CE62, 0x0041FD7E, 0x00422FC6, 0x00426C1C, 0x0042DE66,
)
OVERLAY = (9916, "f00be08414c7e4731ed8e2e61ed1f8041f105c520d941c0b26d16ba4f4e8143a")
PROVIDER = (158516, "5ec3947c373c9d765d8c3385c0f7d436f8c4599ddae90429bc48263f1f80783a")
LINUX_PROVIDER = (158500, "06e369900458478ec088319400809d6bfb7883c3ddeb0808e3fff0f8bb52e4f5")
PACKAGE = (4740094, "f76455fc72574e0c8357b14b7f0c422931ae65896eb642e61787d0df40cb8c7f")
LINUX_PACKAGE = (4516088, "72935d6882098e5d65e30bdf6630214c5fb428bff20dbabca7e4988ba2aefc37")


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_bl(blob: bytes, address: int) -> int | None:
    offset = address - RUN_BASE
    if offset < 0 or offset + 4 > len(blob):
        return None
    first = int.from_bytes(blob[offset:offset + 2], "little")
    second = int.from_bytes(blob[offset + 2:offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = 1 ^ j1 ^ sign
    i2 = 1 ^ j2 ^ sign
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def audit() -> dict:
    for path, expected in SOURCE_PINS.items():
        data = path.read_bytes()
        require((len(data), digest(data)) == expected, f"source identity changed: {path.name}")

    official = OFFICIAL.read_bytes()
    start = STOCK_ADDRESS - RUN_BASE
    stock = official[start:start + STOCK_SIZE]
    require((len(stock), digest(stock)) == (STOCK_SIZE, STOCK_SHA256), "stock entry changed")
    observed_callers = tuple(
        address for address in range(RUN_BASE, RUN_BASE + len(official) - 3, 2)
        if decode_bl(official, address) == STOCK_ADDRESS
    )
    require(observed_callers == CALLERS, "whole-image BL caller topology changed")

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    leaf = next((item for item in config["relocated_leaves"] if item["function"] == FUNCTION), None)
    require(leaf is not None, "relocated leaf disappeared")
    require(leaf["strict_relocation_contract"] is True, "strict relocation contract disabled")
    require(leaf["expected"]["offset"] == 940, "leaf offset changed")
    require(leaf["expected"]["size"] == FUNCTION_SIZE, "leaf size changed")
    require(leaf["expected"]["sha256"] == FUNCTION_SHA256, "leaf hash changed")
    require(leaf["relocations"] == [], "byte-fill leaf gained relocations")

    with tempfile.TemporaryDirectory(prefix="open-cfw-boot-memset-audit-") as raw:
        output = Path(raw)
        subprocess.run(
            ["python3", str(BUILDER), "--output-dir", str(output)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        report = json.loads((output / "build-report.json").read_text(encoding="utf-8"))
        overlay = (output / "bootloader_core_overlay.bin").read_bytes()
        provider = (output / "ota_s200_bootloader.bin").read_bytes()
    require((len(overlay), digest(overlay)) == OVERLAY, "overlay identity changed")
    require((len(provider), digest(provider)) == PROVIDER, "provider identity changed")
    require(report["overlay"]["functions"][FUNCTION] == {"offset": 940, "size": 12}, "placement changed")
    patch = next(item for item in report["overlay"]["patched_sites"] if item["name"] == "replace_bootloader_aeabi_memset")
    require(patch["target_address"] == FUNCTION_ADDRESS, "redirect destination changed")
    require(patch["expected_size"] == STOCK_SIZE, "patch span changed")
    require(patch["expected_sha256"] == STOCK_SHA256, "patch input changed")
    require(patch["replacement_hex"][8:] == "00bf" * 49, "full-span NOP fill changed")
    component = report["component"]
    require(component["source_owned_bytes"] == 9903, "source accounting changed")
    require(component["generated_patch_site_bytes"] == 11310, "patch accounting changed")
    require(component["generated_alignment_bytes"] == 14, "alignment accounting changed")
    require(component["opaque_base_bytes"] == 137289, "retained accounting changed")
    require(report["safety"]["hardware_operations"] == [], "builder reported hardware operations")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    boot = manifest["component_overrides"]["apollo_bootloader"]["provider"]
    require((boot["size"], boot["sha256"]) == PROVIDER, "canonical provider pin is stale")
    linux = boot["profiles"]["linux-clang"]
    require((linux["size"], linux["sha256"]) == LINUX_PROVIDER, "Linux provider pin is stale")
    package = manifest["package"]
    require((package["expected_size"], package["expected_sha256"]) == PACKAGE, "package pin is stale")
    linux_package = package["profiles"]["linux-clang"]
    require((linux_package["expected_size"], linux_package["expected_sha256"]) == LINUX_PACKAGE, "Linux package pin is stale")

    return {
        "component": "G2 Apollo bootloader Arm EABI byte-fill",
        "status": "implemented-in-source / hardware-validation-blocked",
        "software_gap_count": 0,
        "stock": {"address": STOCK_ADDRESS, "size": STOCK_SIZE, "sha256": STOCK_SHA256, "whole_image_callers": len(CALLERS)},
        "source": {"function": FUNCTION, "address": FUNCTION_ADDRESS, "size": FUNCTION_SIZE, "sha256": FUNCTION_SHA256, "relocations": 0},
        "provider": {"size": PROVIDER[0], "sha256": PROVIDER[1], "source_owned_bytes": 9211, "retained_official_bytes": 138057},
        "deployment": {"apple_package": {"size": PACKAGE[0], "sha256": PACKAGE[1]}, "linux_package": {"size": LINUX_PACKAGE[0], "sha256": LINUX_PACKAGE[1]}},
        "hardware_block": {"physical_evidence_available": False, "required_evidence": "authorized responsive G2 right temple demonstrating boot progression through all byte-fill callers", "stock_bootloader_retained_for_hardware": True},
        "safety": {"hardware_operations": [], "signing_performed": False, "flashing_performed": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Bootloader byte-fill closure: {report['status']}")
        print(f"  authenticated callers: {report['stock']['whole_image_callers']}")
        print("  hardware operations: none; physical validation unavailable")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader byte-fill audit failed: {exc}") from exc
