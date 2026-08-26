#!/usr/bin/env python3
"""Fail-closed source/build audit for the G2 bootloader byte comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/bootloader/core_overlay"
SOURCE = COMPONENT / "runtime_memcmp.c"
HEADER = COMPONENT / "runtime_memcmp.h"
CONFIG = COMPONENT / "overlay.json"
BUILDER = COMPONENT / "build_component.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
RUN_BASE = 0x00410000
STOCK_ADDRESS = 0x00415758
STOCK_SIZE = 104
STOCK_SHA256 = "33e09969a8e4f7ca9290ef4678d252c217a5d031eb362f8d6c5ad656424d4154"
FUNCTION = "open_cfw_bootloader_memcmp"
FUNCTION_ADDRESS = 0x00434840
FUNCTION_SIZE = 28
FUNCTION_SHA256 = "27a66a6c870f14f8ff02ed06584fc60e5e6bb17274f13e4234314e5fcbb2ece1"
SOURCE_PINS = {
    SOURCE: (530, "ad02b1bb52b3ed3d55c6559ed02d80642b3c64c9a5442b0c975efaa297dd8f1a"),
    HEADER: (324, "287d7f8677012fd40ee5f564de47a339e29b7ae78969504b51ea791b03010f59"),
}
CALLERS = (0x00410738, 0x00411D0A, 0x00411D1E, 0x00411D42, 0x00411D54, 0x0042DA9A)
OVERLAY = (1856, "6693a0fec4dfd7c9ba82639de56264a1ba1519768b6aa90b40885092f6fe4913")
PROVIDER = (150456, "cb3ea4265d21ae37c0f7ec3671d67440f90cd0f05e3360b472716e69962aeb2d")
LINUX_PROVIDER = (150456, "df6ec98c263e1e5d4f16244af450171e149be673eb0347f076f997b8de326187")
PACKAGE = (4732034, "bee2f83e6afb805f9427e3565f0e39660188ef37a5b3683f7193bb52a9dadcbb")
LINUX_PACKAGE = (4508044, "ff147a4647c0cc8f5c7c31fc29b57eed5513bd774abc65caaad67ee8bebd3ac8")


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
    callers = tuple(address for address in range(RUN_BASE, RUN_BASE + len(official) - 3, 2) if decode_bl(official, address) == STOCK_ADDRESS)
    require(callers == CALLERS, "whole-image BL caller topology changed")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    leaf = next((item for item in config["relocated_leaves"] if item["function"] == FUNCTION), None)
    require(leaf is not None and leaf["strict_relocation_contract"] is True, "strict leaf disappeared")
    require((leaf["expected"]["offset"], leaf["expected"]["size"], leaf["expected"]["sha256"]) == (968, FUNCTION_SIZE, FUNCTION_SHA256), "leaf pins changed")
    require(leaf["relocations"] == [], "comparison leaf gained relocations")
    with tempfile.TemporaryDirectory(prefix="open-cfw-boot-memcmp-audit-") as raw:
        output = Path(raw)
        subprocess.run(["python3", str(BUILDER), "--output-dir", str(output)], cwd=ROOT, check=True, capture_output=True, text=True)
        report = json.loads((output / "build-report.json").read_text(encoding="utf-8"))
        overlay = (output / "bootloader_core_overlay.bin").read_bytes()
        provider = (output / "ota_s200_bootloader.bin").read_bytes()
    require((len(overlay), digest(overlay)) == OVERLAY, "overlay identity changed")
    require((len(provider), digest(provider)) == PROVIDER, "provider identity changed")
    require(report["overlay"]["functions"][FUNCTION] == {"offset": 968, "size": 28}, "placement changed")
    patch = next(item for item in report["overlay"]["patched_sites"] if item["name"] == "replace_bootloader_memcmp")
    require((patch["target_address"], patch["expected_size"], patch["expected_sha256"]) == (FUNCTION_ADDRESS, STOCK_SIZE, STOCK_SHA256), "patch contract changed")
    require(patch["replacement_hex"][8:] == "00bf" * 50, "full-span NOP fill changed")
    component = report["component"]
    require((component["source_owned_bytes"], component["generated_patch_site_bytes"], component["generated_alignment_bytes"], component["opaque_base_bytes"]) == (1849, 2398, 8, 146201), "provider accounting changed")
    require(report["safety"]["hardware_operations"] == [], "builder reported hardware operations")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    boot = manifest["component_overrides"]["apollo_bootloader"]["provider"]
    require((boot["size"], boot["sha256"]) == PROVIDER, "canonical provider pin is stale")
    require((boot["profiles"]["linux-clang"]["size"], boot["profiles"]["linux-clang"]["sha256"]) == LINUX_PROVIDER, "Linux provider pin is stale")
    package = manifest["package"]
    require((package["expected_size"], package["expected_sha256"]) == PACKAGE, "package pin is stale")
    require((package["profiles"]["linux-clang"]["expected_size"], package["profiles"]["linux-clang"]["expected_sha256"]) == LINUX_PACKAGE, "Linux package pin is stale")
    return {
        "component": "G2 Apollo bootloader bounded byte comparison",
        "status": "implemented-in-source / hardware-validation-blocked",
        "software_gap_count": 0,
        "stock": {"address": STOCK_ADDRESS, "size": STOCK_SIZE, "sha256": STOCK_SHA256, "whole_image_callers": len(CALLERS)},
        "source": {"function": FUNCTION, "address": FUNCTION_ADDRESS, "size": FUNCTION_SIZE, "sha256": FUNCTION_SHA256, "relocations": 0},
        "provider": {"size": PROVIDER[0], "sha256": PROVIDER[1], "source_owned_bytes": 1849, "retained_official_bytes": 146201},
        "deployment": {"apple_package": {"size": PACKAGE[0], "sha256": PACKAGE[1]}, "linux_package": {"size": LINUX_PACKAGE[0], "sha256": LINUX_PACKAGE[1]}},
        "hardware_block": {"physical_evidence_available": False, "required_evidence": "authorized responsive G2 right temple demonstrating boot progression through all comparison callers", "stock_bootloader_retained_for_hardware": True},
        "safety": {"hardware_operations": [], "signing_performed": False, "flashing_performed": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else f"Bootloader byte-comparison closure: {report['status']}\n  authenticated callers: {report['stock']['whole_image_callers']}\n  hardware operations: none; physical validation unavailable")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader byte-comparison audit failed: {exc}") from exc
