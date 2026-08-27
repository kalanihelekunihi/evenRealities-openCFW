#!/usr/bin/env python3
"""Fail-closed source/build audit for the G2 bootloader CRC-32 updater."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/bootloader/core_overlay"
SOURCE = COMPONENT / "runtime_crc32.c"
HEADER = COMPONENT / "runtime_crc32.h"
CONFIG = COMPONENT / "overlay.json"
BUILDER = COMPONENT / "build_component.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
RUN_BASE = 0x00410000
STOCK_ADDRESS = 0x004157C0
STOCK_SIZE = 56
STOCK_SHA256 = "acba42ebe6d52e7d353fe1cd586fb79cea530e243d2ffaeaf1019f7548dc20be"
TABLE_ADDRESS = 0x0043174C
TABLE_SIZE = 64
TABLE_SHA256 = "9af680c2988bbb73e930ba9b2e9a51a28303c3add723b5685f2d5e9a9d1eb8a8"
CALLERS = (0x004107B6, 0x004117E6, 0x004117FC, 0x0041187E, 0x00411E8A, 0x0041207C)
FUNCTION = "open_cfw_bootloader_crc32"
FUNCTION_ADDRESS = 0x00434898
FUNCTION_SIZE = 44
FUNCTION_SHA256 = "d51095aed51181e2bcb9f7882c6430298be29ad66f6613b434c07fac7f7df205"
SOURCE_PINS = {
    SOURCE: (612, "7a8d810c1804f76a8068c0caf4558ffe0be71a0725b5e4b316489e0f5577e040"),
    HEADER: (267, "6857c60af1e7d278bda71ee0485c14d41646eb91c17b6e23b47ac813a94c994b"),
}
OVERLAY = (9916, "f00be08414c7e4731ed8e2e61ed1f8041f105c520d941c0b26d16ba4f4e8143a")
PROVIDER = (158516, "5ec3947c373c9d765d8c3385c0f7d436f8c4599ddae90429bc48263f1f80783a")
LINUX_PROVIDER = (158500, "06e369900458478ec088319400809d6bfb7883c3ddeb0808e3fff0f8bb52e4f5")
PACKAGE = (4740094, "f76455fc72574e0c8357b14b7f0c422931ae65896eb642e61787d0df40cb8c7f")
LINUX_PACKAGE = (4516088, "72935d6882098e5d65e30bdf6630214c5fb428bff20dbabca7e4988ba2aefc37")
REPLACEMENT = "1ff06ab8" + "00bf" * 26


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_bl(blob: bytes, address: int) -> int | None:
    offset = address - RUN_BASE
    first = int.from_bytes(blob[offset:offset + 2], "little")
    second = int.from_bytes(blob[offset + 2:offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22) | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def audit() -> dict:
    for path, expected in SOURCE_PINS.items():
        data = path.read_bytes()
        require((len(data), digest(data)) == expected, f"source identity changed: {path.name}")
    official = OFFICIAL.read_bytes()
    start = STOCK_ADDRESS - RUN_BASE
    require((len(official[start:start + STOCK_SIZE]), digest(official[start:start + STOCK_SIZE])) == (STOCK_SIZE, STOCK_SHA256), "stock entry changed")
    table_start = TABLE_ADDRESS - RUN_BASE
    table = official[table_start:table_start + TABLE_SIZE]
    require((len(table), digest(table)) == (TABLE_SIZE, TABLE_SHA256), "stock nibble table changed")
    require(int.from_bytes(table[32:36], "little") == 0xEDB88320, "CRC polynomial identity changed")
    callers = tuple(address for address in range(RUN_BASE, RUN_BASE + len(official) - 3, 2) if decode_bl(official, address) == STOCK_ADDRESS)
    require(callers == CALLERS, "whole-image BL caller topology changed")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    leaf = next((item for item in config["relocated_leaves"] if item["function"] == FUNCTION), None)
    require(leaf is not None and leaf["strict_relocation_contract"] is True, "strict leaf disappeared")
    require((leaf["expected"]["offset"], leaf["expected"]["alignment"], leaf["expected"]["size"], leaf["expected"]["sha256"]) == (1056, 4, FUNCTION_SIZE, FUNCTION_SHA256), "leaf pins changed")
    require(leaf["relocations"] == [], "CRC leaf gained relocations")
    with tempfile.TemporaryDirectory(prefix="open-cfw-boot-crc32-audit-") as raw:
        output = Path(raw)
        subprocess.run(["python3", str(BUILDER), "--output-dir", str(output)], cwd=ROOT, check=True, capture_output=True, text=True)
        report = json.loads((output / "build-report.json").read_text(encoding="utf-8"))
        overlay = (output / "bootloader_core_overlay.bin").read_bytes()
        provider = (output / "ota_s200_bootloader.bin").read_bytes()
    require((len(overlay), digest(overlay)) == OVERLAY, "overlay identity changed")
    require((len(provider), digest(provider)) == PROVIDER, "provider identity changed")
    require(report["overlay"]["functions"][FUNCTION] == {"offset": 1056, "size": FUNCTION_SIZE}, "placement changed")
    patch = next(item for item in report["overlay"]["patched_sites"] if item["name"] == "replace_bootloader_crc32")
    require((patch["target_address"], patch["expected_size"], patch["expected_sha256"], patch["replacement_hex"]) == (FUNCTION_ADDRESS, STOCK_SIZE, STOCK_SHA256, REPLACEMENT), "patch contract changed")
    component = report["component"]
    require((component["source_owned_bytes"], component["generated_patch_site_bytes"], component["generated_alignment_bytes"], component["opaque_base_bytes"]) == (9903, 11310, 14, 137289), "provider accounting changed")
    require(report["safety"]["hardware_operations"] == [], "builder reported hardware operations")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    boot = manifest["component_overrides"]["apollo_bootloader"]["provider"]
    require((boot["size"], boot["sha256"]) == PROVIDER, "canonical provider pin is stale")
    require((boot["profiles"]["linux-clang"]["size"], boot["profiles"]["linux-clang"]["sha256"]) == LINUX_PROVIDER, "Linux provider pin is stale")
    package = manifest["package"]
    require((package["expected_size"], package["expected_sha256"]) == PACKAGE, "package pin is stale")
    require((package["profiles"]["linux-clang"]["expected_size"], package["profiles"]["linux-clang"]["expected_sha256"]) == LINUX_PACKAGE, "Linux package pin is stale")
    return {
        "component": "G2 Apollo bootloader reflected CRC-32 updater",
        "status": "implemented-in-source / hardware-validation-blocked",
        "software_gap_count": 0,
        "stock": {"address": STOCK_ADDRESS, "size": STOCK_SIZE, "sha256": STOCK_SHA256, "whole_image_callers": len(CALLERS), "table_address": TABLE_ADDRESS, "table_polynomial": "0xEDB88320"},
        "source": {"function": FUNCTION, "address": FUNCTION_ADDRESS, "size": FUNCTION_SIZE, "sha256": FUNCTION_SHA256, "relocations": 0},
        "provider": {"size": PROVIDER[0], "sha256": PROVIDER[1], "source_owned_bytes": 9211, "generated_patch_bytes": 10542, "alignment_bytes": 14, "retained_official_bytes": 138057},
        "deployment": {"apple_package": {"size": PACKAGE[0], "sha256": PACKAGE[1]}, "linux_package": {"size": LINUX_PACKAGE[0], "sha256": LINUX_PACKAGE[1]}},
        "hardware_block": {"physical_evidence_available": False, "required_evidence": "authorized responsive G2 right temple demonstrating boot progression and CRC results through all six authenticated callers", "stock_bootloader_retained_for_hardware": True},
        "safety": {"hardware_operations": [], "signing_performed": False, "flashing_performed": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else f"Bootloader CRC-32 closure: {report['status']}\n  authenticated callers: {report['stock']['whole_image_callers']}\n  hardware operations: none; physical validation unavailable")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader CRC-32 audit failed: {exc}") from exc
