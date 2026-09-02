#!/usr/bin/env python3
"""Fail-closed source/build audit for the G2 bootloader forward-copy entry."""

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
SOURCE = COMPONENT / "runtime_aeabi_memcpy.c"
HEADER = COMPONENT / "runtime_aeabi_memcpy.h"
CONFIG = COMPONENT / "overlay.json"
BUILDER = COMPONENT / "build_component.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
RUN_BASE = 0x00410000
STOCK_ADDRESS = 0x0041568C
STOCK_SIZE = 166
STOCK_SHA256 = "8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd"
ALIGNED_ENTRY_ADDRESS = 0x004156AC
ENTRY_SPANS = {
    STOCK_ADDRESS: (32, "e0294160ea267d7f79540d517dc72e5a084496cbd167c0d301640609f78a810f"),
    ALIGNED_ENTRY_ADDRESS: (134, "e23d4858d3544f196ab6b0b89510165e191a9364c4167192e9508e7cb36c8d0c"),
}
FUNCTION = "open_cfw_bootloader_aeabi_memcpy"
FUNCTION_ADDRESS = 0x00434830
FUNCTION_SIZE = 16
FUNCTION_SHA256 = "d2d832a0c13fc4c0b9b47396bfb6d68fb7e07925ad0fa4eedc9c14c5b062590d"
SOURCE_PINS = {
    SOURCE: (551, "4727cfa1e3d10f6a587bd29213e73cab8ca10bafe5dd524fc04417bef54adcbd"),
    HEADER: (332, "606122a0eaef19b7240e359c7c5e54dbe5e225c99789e2035c19710812fd8d44"),
}
CALLERS = (
    0x0041059A, 0x0041060E, 0x004109B6, 0x00411140, 0x004111B4,
    0x0041394C, 0x0041A4D6, 0x0041A4F8, 0x0041A550, 0x0041EA20,
    0x0041EDAE, 0x0041EE38, 0x0041EEDC, 0x0041EF16, 0x0041EF4C,
    0x0041FA16, 0x004217B4, 0x004218CA, 0x004219D6, 0x00422428,
    0x00423896, 0x004238A0, 0x004238AA, 0x004238F6, 0x00423900,
    0x0042390A, 0x00423914, 0x0042394E, 0x00423964, 0x00423B30,
    0x00423B3A, 0x00423B44, 0x00430AB6,
)
ALIGNED_CALLERS = (
    0x004113C6, 0x0041147E, 0x0041237C, 0x00412896, 0x00412A5E,
    0x00412BEE, 0x00412C24, 0x00412C92, 0x00412CB4, 0x00412F48,
    0x0041301C, 0x004139E0, 0x004139F6, 0x004145A2, 0x0041466A,
    0x00414676, 0x0041496A, 0x00414976, 0x00414AF2, 0x00414BC4,
    0x00414EAA, 0x00414FA0, 0x00415076, 0x0041B910, 0x0041FA76,
    0x00420E96, 0x004210D2, 0x0042A2C6, 0x0042DE36,
)
OVERLAY = (15240, "d68bca1fc09b1b734a65a706e9d5a4d5aa4201e53441f6ad1354be44f428b314")
PROVIDER = (163840, "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b")
LINUX_PROVIDER = (163824, "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875")


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
    ingress = {
        target: tuple(
            address
            for address in range(RUN_BASE, RUN_BASE + len(official) - 3, 2)
            if decode_bl(official, address) == target
        )
        for target in range(STOCK_ADDRESS, STOCK_ADDRESS + STOCK_SIZE, 2)
    }
    ingress = {target: callers for target, callers in ingress.items() if callers}
    require(
        ingress == {
            STOCK_ADDRESS: CALLERS,
            ALIGNED_ENTRY_ADDRESS: ALIGNED_CALLERS,
        },
        "whole-image forward-copy interior-ingress topology changed",
    )

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    leaf = next((item for item in config["relocated_leaves"] if item["function"] == FUNCTION), None)
    require(leaf is not None and leaf["strict_relocation_contract"] is True, "strict leaf disappeared")
    require((leaf["expected"]["offset"], leaf["expected"]["size"], leaf["expected"]["sha256"]) == (952, FUNCTION_SIZE, FUNCTION_SHA256), "leaf pins changed")
    require(leaf["relocations"] == [], "copy leaf gained relocations")

    with tempfile.TemporaryDirectory(prefix="open-cfw-boot-memcpy-audit-") as raw:
        output = Path(raw)
        subprocess.run(["python3", str(BUILDER), "--output-dir", str(output)], cwd=ROOT, check=True, capture_output=True, text=True)
        report = json.loads((output / "build-report.json").read_text(encoding="utf-8"))
        overlay = (output / "bootloader_core_overlay.bin").read_bytes()
        provider = (output / "ota_s200_bootloader.bin").read_bytes()
    require((len(overlay), digest(overlay)) == OVERLAY, "overlay identity changed")
    require((len(provider), digest(provider)) == PROVIDER, "provider identity changed")
    require(report["overlay"]["functions"][FUNCTION] == {"offset": 952, "size": 16}, "placement changed")
    patch_by_name = {
        item["name"]: item for item in report["overlay"]["patched_sites"]
    }
    for name, address in (
        ("replace_bootloader_aeabi_memcpy", STOCK_ADDRESS),
        ("replace_bootloader_aeabi_memcpy_aligned_entry", ALIGNED_ENTRY_ADDRESS),
    ):
        patch = patch_by_name.get(name)
        size, expected_sha = ENTRY_SPANS[address]
        require(patch is not None, f"missing forward-copy ingress patch: {name}")
        require(
            (patch["runtime_address"], patch["target_address"],
             patch["expected_size"], patch["expected_sha256"])
            == (address, FUNCTION_ADDRESS, size, expected_sha),
            f"forward-copy ingress patch contract changed: {name}",
        )
        require(
            patch["replacement_hex"][8:] == "00bf" * ((size - 4) // 2),
            f"forward-copy ingress NOP fill changed: {name}",
        )
    component = report["component"]
    require(
        component["source_owned_bytes"] + component["opaque_base_bytes"]
        + component["generated_patch_site_bytes"]
        + component["generated_alignment_bytes"] == component["size"],
        "provider accounting does not conserve bytes",
    )
    require(report["safety"]["hardware_operations"] == [], "builder reported hardware operations")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    artifacts = validate_apollo_main_artifacts(ROOT, AuditError, "bootloader memcpy")
    boot = manifest["component_overrides"]["apollo_bootloader"]["provider"]
    require((boot["size"], boot["sha256"]) == PROVIDER, "canonical provider pin is stale")
    require((boot["profiles"]["linux-clang"]["size"], boot["profiles"]["linux-clang"]["sha256"]) == LINUX_PROVIDER, "Linux provider pin is stale")
    package = manifest["package"]
    linux_package = package["profiles"]["linux-clang"]
    require(isinstance(linux_package.get("expected_size"), int) and linux_package["expected_size"] > 0 and len(linux_package.get("expected_sha256", "")) == 64, "Linux package metadata is incomplete")
    return {
        "component": "G2 Apollo bootloader Arm EABI forward copy",
        "status": "implemented-in-source / hardware-validation-blocked-by-unavailable-physical-evidence",
        "software_gap_count": 0,
        "stock": {
            "address": STOCK_ADDRESS,
            "size": STOCK_SIZE,
            "sha256": STOCK_SHA256,
            "entry_points": 2,
            "whole_image_callers": len(CALLERS) + len(ALIGNED_CALLERS),
            "entry_callers": len(CALLERS),
            "aligned_entry_callers": len(ALIGNED_CALLERS),
        },
        "source": {"function": FUNCTION, "address": FUNCTION_ADDRESS, "size": FUNCTION_SIZE, "sha256": FUNCTION_SHA256, "relocations": 0},
        "provider": {"size": PROVIDER[0], "sha256": PROVIDER[1], "source_owned_bytes": component["source_owned_bytes"], "retained_official_bytes": component["opaque_base_bytes"]},
        "deployment": {"apple_package": artifacts["package"], "linux_package": {"size": linux_package["expected_size"], "sha256": linux_package["expected_sha256"]}},
        "hardware_block": {"physical_evidence_available": False, "required_evidence": "authorized G2 hardware demonstrating boot progression through all forward-copy callers", "stock_bootloader_retained_for_hardware": True},
        "safety": {"hardware_operations": [], "signing_performed": False, "flashing_performed": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else f"Bootloader forward-copy closure: {report['status']}\n  authenticated callers: {report['stock']['whole_image_callers']}\n  hardware operations: none; physical validation blocked by unavailable physical evidence")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader forward-copy audit failed: {exc}") from exc
