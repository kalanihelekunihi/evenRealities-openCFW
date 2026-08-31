#!/usr/bin/env python3
"""Fail-closed source/build audit for the G2 bootloader redirect initializer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from apollo_artifact_consistency import validate_apollo_main_artifacts
COMPONENT = ROOT / "components/bootloader/core_overlay"
SOURCE = COMPONENT / "runtime_redirect_init.c"
HEADER = COMPONENT / "runtime_redirect_init.h"
CONFIG = COMPONENT / "overlay.json"
BUILDER = COMPONENT / "build_component.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"

PINS = {
    SOURCE: (2282, "6901fc3f82d82fdfd4d0f24a7e1bf20e79d9f5f800f98492bf057a843404c417"),
    HEADER: (1969, "01aff14b29d32f5a9e2bd700afdc4fbde1fdf4abb4699aa6578c94ef835ea44f"),
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
OVERLAY_SIZE = 15240
OVERLAY_SHA256 = "d68bca1fc09b1b734a65a706e9d5a4d5aa4201e53441f6ad1354be44f428b314"
PROVIDER_SIZE = 163840
PROVIDER_SHA256 = "f570bbf749b16043c8ccfc6eeae66fafaabf4146d5cc55f63d5fab729775ccad"


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
    require(
        component["source_owned_bytes"] + component["opaque_base_bytes"]
        + component["generated_patch_site_bytes"]
        + component["generated_alignment_bytes"] == component["size"],
        "provider accounting does not conserve bytes",
    )
    require(report["safety"]["hardware_operations"] == [], "builder reported hardware operations")
    require(report["safety"]["flashing_performed"] is False, "builder reported flashing")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    artifacts = validate_apollo_main_artifacts(ROOT, AuditError, "bootloader redirect init")
    provider_record = manifest["component_overrides"]["apollo_bootloader"]["provider"]
    require(provider_record["size"] == PROVIDER_SIZE, "manifest provider size is stale")
    require(provider_record["sha256"] == PROVIDER_SHA256, "manifest provider hash is stale")
    package_record = manifest["package"]
    linux_package = package_record["profiles"]["linux-clang"]
    require(isinstance(linux_package.get("expected_size"), int) and linux_package["expected_size"] > 0 and len(linux_package.get("expected_sha256", "")) == 64, "Linux package metadata is incomplete")
    plan_bytes = FLASH_PLAN.read_bytes()
    plan = json.loads(plan_bytes)

    return {
        "component": "G2 Apollo bootloader redirect_init",
        "status": "implemented-in-source / hardware-validation-blocked-by-unavailable-physical-evidence",
        "software_gap_count": 0,
        "stock": {"address": STOCK_ADDRESS, "size": STOCK_SIZE, "sha256": STOCK_SHA256},
        "source": {"function": FUNCTION, "address": FUNCTION_ADDRESS, "text_bytes": FUNCTION_SIZE, "closure_bytes": CLOSURE_SIZE},
        "provider": {"size": PROVIDER_SIZE, "sha256": PROVIDER_SHA256, "source_owned_bytes": component["source_owned_bytes"], "generated_patch_bytes": component["generated_patch_site_bytes"], "retained_official_bytes": component["opaque_base_bytes"]},
        "deployment": {
            "apple_package": {**artifacts["package"], "flash_plan_sha256": digest(plan_bytes)},
            "linux_package": {"size": linux_package["expected_size"], "sha256": linux_package["expected_sha256"]},
            "unresolved_flash_regions": artifacts["unresolved_flash_regions"],
        },
        "hardware_block": {
            "physical_evidence_available": False,
            "required_evidence": "authorized G2 hardware with boot UART and debugger visibility validating both mutex allocations, IAR stream serialization, failure logging, and boot continuation",
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
        print("  hardware operations: none; physical validation blocked by unavailable physical evidence")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader redirect-init audit failed: {exc}") from exc
