#!/usr/bin/env python3
"""Fail-closed source/build audit for the G2 bootloader redirect initializer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/bootloader/core_overlay"
SOURCE = COMPONENT / "runtime_redirect_init.c"
HEADER = COMPONENT / "runtime_redirect_init.h"
CONFIG = COMPONENT / "overlay.json"
BUILDER = COMPONENT / "build_component.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"

PINS = {
    SOURCE: (2295, "9df4daeea0af317c1556361a15f1625d5b1e9d00b3c72ae9b753de4608c3294f"),
    HEADER: (1982, "d59de5e4176f72b95aa93c3e497de815bc29ac1ea816d2e3b8512d4349125414"),
}
STOCK_ADDRESS = 0x00415590
STOCK_SIZE = 88
STOCK_SHA256 = "b53b1d0eae9d2787d431ae1950d956c54429fb339a67ee7f219ff7c01ffc0cd6"
FUNCTION = "open_cfw_bootloader_redirect_init"
FUNCTION_ADDRESS = 0x00434710
FUNCTION_SIZE = 132
FUNCTION_SHA256 = "cbd1c5a521eef64ba9075a211311b71c8a025fd49fc4040814ba893c77260f22"
CLOSURE_SIZE = 275
CLOSURE_SHA256 = "ddb1d064bf765803fac4fc89c0b6c585f13b0ea7bcfc3b5ad7b78ee7d8e50922"
RODATA_SHA256 = "617e0aef0ca7b9cc2d64b76394bd2203cf40de647d25e4caafe628433a0c30a0"
OVERLAY_SIZE = 1856
OVERLAY_SHA256 = "6693a0fec4dfd7c9ba82639de56264a1ba1519768b6aa90b40885092f6fe4913"
PROVIDER_SIZE = 150456
PROVIDER_SHA256 = "cb3ea4265d21ae37c0f7ec3671d67440f90cd0f05e3360b472716e69962aeb2d"
PACKAGE_SIZE = 4732034
PACKAGE_SHA256 = "bee2f83e6afb805f9427e3565f0e39660188ef37a5b3683f7193bb52a9dadcbb"
FLASH_PLAN_SIZE = 4329363
FLASH_PLAN_SHA256 = "5f00aee58cfc9c32557a7302b46efbc61ec59e8346ec90b6cc947cb345c1f663"
LINUX_PACKAGE_SIZE = 4508044
LINUX_PACKAGE_SHA256 = "ff147a4647c0cc8f5c7c31fc29b57eed5513bd774abc65caaad67ee8bebd3ac8"


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit() -> dict:
    for path, (size, sha256) in PINS.items():
        data = path.read_bytes()
        require(len(data) == size, f"size changed: {path.relative_to(ROOT)}")
        require(digest(data) == sha256, f"SHA-256 changed: {path.relative_to(ROOT)}")

    official = OFFICIAL.read_bytes()
    stock_offset = STOCK_ADDRESS - 0x00410000
    stock = official[stock_offset : stock_offset + STOCK_SIZE]
    require(len(stock) == STOCK_SIZE, "authenticated stock span is truncated")
    require(digest(stock) == STOCK_SHA256, "authenticated stock span changed")

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    leaf = next((item for item in config["relocated_leaves"] if item["function"] == FUNCTION), None)
    require(leaf is not None, "redirect-init relocated-leaf record disappeared")
    require(leaf["strict_relocation_contract"] is True, "strict relocation contract disabled")
    require(leaf["expected"]["offset"] == 664, "redirect-init overlay offset changed")
    require(leaf["expected"]["size"] == FUNCTION_SIZE, "redirect-init size pin changed")
    require(leaf["expected"]["closure_size"] == CLOSURE_SIZE, "closure size pin changed")
    require(leaf["expected"]["closure_sha256"] == CLOSURE_SHA256, "closure hash pin changed")
    require(leaf["closure"]["rodata"]["sha256"] == RODATA_SHA256, "rodata hash pin changed")
    expected_calls = [
        (4, "osMutexNew", 0x00416610),
        (16, "osMutexNew", 0x00416610),
        (52, "elog_output", 0x004176CE),
        (86, "elog_output", 0x004176CE),
    ]
    actual_calls = [
        (item["offset"], item["symbol"], item["target_address"])
        for item in leaf["relocations"]
        if item["type"] == "R_ARM_THM_CALL"
    ]
    require(actual_calls == expected_calls, "external call contract changed")
    require(len(leaf["relocations"]) == 12, "relocation count changed")

    with tempfile.TemporaryDirectory(prefix="open-cfw-boot-redirect-audit-") as raw:
        output = Path(raw)
        subprocess.run(
            ["python3", str(BUILDER), "--output-dir", str(output)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads((output / "build-report.json").read_text(encoding="utf-8"))
        overlay = (output / "bootloader_core_overlay.bin").read_bytes()
        provider = (output / "ota_s200_bootloader.bin").read_bytes()

    require((len(overlay), digest(overlay)) == (OVERLAY_SIZE, OVERLAY_SHA256), "overlay identity changed")
    require((len(provider), digest(provider)) == (PROVIDER_SIZE, PROVIDER_SHA256), "provider identity changed")
    function = report["overlay"]["functions"][FUNCTION]
    require(function == {"offset": 664, "size": FUNCTION_SIZE}, "function placement changed")
    built_leaf = next(item for item in report["relocated_leaves"] if item["extraction"]["function"] == FUNCTION)
    extraction = built_leaf["extraction"]
    require(extraction["runtime_address"] == FUNCTION_ADDRESS, "function runtime address changed")
    require(extraction["sha256"] == FUNCTION_SHA256, "relocated function hash changed")
    require(extraction["closure_sha256"] == CLOSURE_SHA256, "built closure hash changed")
    require(extraction["rodata"]["sha256"] == RODATA_SHA256, "built rodata hash changed")
    patch = next(item for item in report["overlay"]["patched_sites"] if item["name"] == "replace_bootloader_redirect_init")
    require(patch["runtime_address"] == STOCK_ADDRESS, "stock patch address changed")
    require(patch["target_address"] == FUNCTION_ADDRESS, "redirect destination changed")
    require(patch["expected_size"] == STOCK_SIZE, "patch span changed")
    require(patch["expected_sha256"] == STOCK_SHA256, "patch stock identity changed")
    require(patch["replacement_hex"][8:] == "00bf" * 42, "full-span NOP fill changed")
    component = report["component"]
    require(component["source_owned_bytes"] == 1849, "source ownership accounting changed")
    require(component["generated_patch_site_bytes"] == 2398, "generated patch accounting changed")
    require(component["opaque_base_bytes"] == 146201, "retained-byte accounting changed")
    require(report["safety"]["hardware_operations"] == [], "builder reported hardware operations")
    require(report["safety"]["flashing_performed"] is False, "builder reported flashing")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    provider_record = manifest["component_overrides"]["apollo_bootloader"]["provider"]
    require(provider_record["size"] == PROVIDER_SIZE, "manifest provider size is stale")
    require(provider_record["sha256"] == PROVIDER_SHA256, "manifest provider hash is stale")
    package_record = manifest["package"]
    require(package_record["expected_size"] == PACKAGE_SIZE, "manifest package size is stale")
    require(package_record["expected_sha256"] == PACKAGE_SHA256, "manifest package hash is stale")
    linux_package = package_record["profiles"]["linux-clang"]
    require(linux_package["expected_size"] == LINUX_PACKAGE_SIZE, "Linux package size is stale")
    require(linux_package["expected_sha256"] == LINUX_PACKAGE_SHA256, "Linux package hash is stale")
    package = PACKAGE.read_bytes()
    require((len(package), digest(package)) == (PACKAGE_SIZE, PACKAGE_SHA256), "canonical package identity changed")
    plan_bytes = FLASH_PLAN.read_bytes()
    require((len(plan_bytes), digest(plan_bytes)) == (FLASH_PLAN_SIZE, FLASH_PLAN_SHA256), "canonical flash-plan identity changed")
    plan = json.loads(plan_bytes)
    require(plan["package_sha256"] == PACKAGE_SHA256, "flash plan names a different package")
    require(
        tuple(len(plan[key]) for key in ("flash_regions", "unresolved_flash_regions", "container_only_regions", "protected_regions"))
        == (6236, 2, 5, 6),
        "flash-plan ownership counts changed",
    )

    return {
        "component": "G2 Apollo bootloader redirect_init",
        "status": "implemented-in-source / hardware-validation-blocked",
        "software_gap_count": 0,
        "stock": {"address": STOCK_ADDRESS, "size": STOCK_SIZE, "sha256": STOCK_SHA256},
        "source": {"function": FUNCTION, "address": FUNCTION_ADDRESS, "text_bytes": FUNCTION_SIZE, "closure_bytes": CLOSURE_SIZE},
        "provider": {"size": PROVIDER_SIZE, "sha256": PROVIDER_SHA256, "source_owned_bytes": 1849, "generated_patch_bytes": 2398, "retained_official_bytes": 146201},
        "deployment": {
            "apple_package": {"size": PACKAGE_SIZE, "sha256": PACKAGE_SHA256, "flash_plan_sha256": FLASH_PLAN_SHA256},
            "linux_package": {"size": LINUX_PACKAGE_SIZE, "sha256": LINUX_PACKAGE_SHA256},
            "unresolved_flash_regions": 2,
        },
        "hardware_block": {
            "physical_evidence_available": False,
            "required_evidence": "authorized responsive G2 right temple with boot UART and debugger visibility validating both mutex allocations, IAR stream serialization, failure logging, and boot continuation",
            "stock_bootloader_retained_for_hardware": True,
        },
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
        print(f"Bootloader redirect-init closure: {report['status']}")
        print(f"  source closure: {report['source']['closure_bytes']} bytes")
        print("  hardware operations: none; physical validation unavailable")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader redirect-init audit failed: {exc}") from exc
