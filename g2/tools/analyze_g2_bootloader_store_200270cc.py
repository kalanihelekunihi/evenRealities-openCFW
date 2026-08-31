#!/usr/bin/env python3
"""Fail-closed audit for the G2 bootloader SRAM-word setter."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from apollo_artifact_consistency import validate_apollo_main_artifacts


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/bootloader/core_overlay"
SOURCE = COMPONENT / "runtime_store_200270cc.c"
HEADER = COMPONENT / "runtime_store_200270cc.h"
CONFIG = COMPONENT / "overlay.json"
BUILDER = COMPONENT / "build_component.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
RUN_BASE = 0x00410000
STOCK_ADDRESS = 0x0041583C
STOCK_SIZE = 8
STOCK_SHA256 = "8bee0f65c10cb18c0d50f225275e41e44c54b0c06cdaef05017cccf89162d0f8"
SRAM_ADDRESS = 0x200270CC
CALLERS = (0x0041FABA,)
FUNCTION = "open_cfw_bootloader_store_200270cc"
FUNCTION_ADDRESS = 0x004348C4
FUNCTION_SIZE = 12
FUNCTION_SHA256 = "99c0589d704d517cb23105abaa50664dab79efb3911235140a2c3fe492283c31"
SOURCE_PINS = {
    SOURCE: (390, "41c4545e6e897a973f9a4af860ac72780a3cdeffeb927f8ff2f8ce9521925d17"),
    HEADER: (229, "cb7aef4233436d729ccd0790175fa2124b78c769479b0e73dfaddd0b1adbdf58"),
}
OVERLAY = (15240, "d68bca1fc09b1b734a65a706e9d5a4d5aa4201e53441f6ad1354be44f428b314")
PROVIDER = (163840, "f570bbf749b16043c8ccfc6eeae66fafaabf4146d5cc55f63d5fab729775ccad")
LINUX_PROVIDER = (163824, "e859e0ce78f8b21e8a1542701eb52b4d7d97a62902546ef451919948d4dbbf8e")


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
    require(int.from_bytes(official[0x5FDC:0x5FE0], "little") == SRAM_ADDRESS, "SRAM literal changed")
    callers = tuple(address for address in range(RUN_BASE, RUN_BASE + len(official) - 3, 2) if decode_bl(official, address) == STOCK_ADDRESS)
    require(callers == CALLERS, "whole-image BL caller topology changed")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    leaf = next((item for item in config["relocated_leaves"] if item["function"] == FUNCTION), None)
    require(leaf is not None and leaf["strict_relocation_contract"] is True, "strict leaf disappeared")
    require((leaf["expected"]["offset"], leaf["expected"]["size"], leaf["expected"]["sha256"]) == (1100, FUNCTION_SIZE, FUNCTION_SHA256), "leaf pins changed")
    require(leaf["relocations"] == [], "setter leaf gained relocations")
    with tempfile.TemporaryDirectory(prefix="open-cfw-boot-store-audit-") as raw:
        output = Path(raw)
        subprocess.run(["python3", str(BUILDER), "--output-dir", str(output)], cwd=ROOT, check=True, capture_output=True, text=True)
        report = json.loads((output / "build-report.json").read_text(encoding="utf-8"))
        overlay = (output / "bootloader_core_overlay.bin").read_bytes()
        provider = (output / "ota_s200_bootloader.bin").read_bytes()
    require((len(overlay), digest(overlay)) == OVERLAY, "overlay identity changed")
    require((len(provider), digest(provider)) == PROVIDER, "provider identity changed")
    require(report["overlay"]["functions"][FUNCTION] == {"offset": 1100, "size": FUNCTION_SIZE}, "placement changed")
    patch = next(item for item in report["overlay"]["patched_sites"] if item["name"] == "replace_bootloader_store_200270cc")
    require((patch["target_address"], patch["expected_size"], patch["expected_sha256"], patch["replacement_hex"]) == (FUNCTION_ADDRESS, STOCK_SIZE, STOCK_SHA256, "1ff042b800bf00bf"), "patch contract changed")
    component = report["component"]
    require(
        component["source_owned_bytes"] + component["opaque_base_bytes"]
        + component["generated_patch_site_bytes"]
        + component["generated_alignment_bytes"] == component["size"],
        "provider accounting does not conserve bytes",
    )
    require(report["safety"]["hardware_operations"] == [], "builder reported hardware operations")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    artifacts = validate_apollo_main_artifacts(ROOT, AuditError, "bootloader store helper")
    boot = manifest["component_overrides"]["apollo_bootloader"]["provider"]
    require((boot["size"], boot["sha256"]) == PROVIDER, "canonical provider pin is stale")
    require((boot["profiles"]["linux-clang"]["size"], boot["profiles"]["linux-clang"]["sha256"]) == LINUX_PROVIDER, "Linux provider pin is stale")
    package = manifest["package"]
    linux_package = package["profiles"]["linux-clang"]
    require(isinstance(linux_package.get("expected_size"), int) and linux_package["expected_size"] > 0 and len(linux_package.get("expected_sha256", "")) == 64, "Linux package metadata is incomplete")
    return {
        "component": "G2 Apollo bootloader SRAM-word setter",
        "status": "implemented-in-source / hardware-validation-blocked-by-unavailable-physical-evidence",
        "software_gap_count": 0,
        "stock": {"address": STOCK_ADDRESS, "size": STOCK_SIZE, "sha256": STOCK_SHA256, "whole_image_callers": len(CALLERS), "sram_address": SRAM_ADDRESS},
        "source": {"function": FUNCTION, "address": FUNCTION_ADDRESS, "size": FUNCTION_SIZE, "sha256": FUNCTION_SHA256, "relocations": 0},
        "provider": {"size": PROVIDER[0], "sha256": PROVIDER[1], "source_owned_bytes": component["source_owned_bytes"], "generated_patch_bytes": component["generated_patch_site_bytes"], "alignment_bytes": component["generated_alignment_bytes"], "retained_official_bytes": component["opaque_base_bytes"]},
        "deployment": {"apple_package": artifacts["package"], "linux_package": {"size": linux_package["expected_size"], "sha256": linux_package["expected_sha256"]}},
        "hardware_block": {"physical_evidence_available": False, "required_evidence": "authorized G2 hardware showing the sole caller writes the expected value to SRAM 0x200270CC and boot continues", "stock_bootloader_retained_for_hardware": True},
        "safety": {"hardware_operations": [], "signing_performed": False, "flashing_performed": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else f"Bootloader SRAM setter closure: {report['status']}\n  authenticated callers: 1\n  hardware operations: none; physical validation blocked by unavailable physical evidence")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader SRAM setter audit failed: {exc}") from exc
