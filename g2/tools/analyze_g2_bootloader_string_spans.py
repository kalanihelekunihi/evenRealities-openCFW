#!/usr/bin/env python3
"""Fail-closed source/build audit for the G2 bootloader string spans."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/bootloader/core_overlay"
CONFIG = COMPONENT / "overlay.json"
BUILDER = COMPONENT / "build_component.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
RUN_BASE = 0x00410000
SOURCE_PINS = {
    COMPONENT / "runtime_strcspn.c": (616, "69c1c369adb07437f875e4a28086707156a5fb2c70773cb8c04792e8227ee277"),
    COMPONENT / "runtime_strspn.c": (575, "f7383389453e2e8b7fb7ac04d9a11394bac1457a46cb75d78ab043f30332c331"),
    COMPONENT / "runtime_string_spans.h": (429, "24016f04b600c7ec1bc70ae503cac8c2415191ca41966fa827bdee3f48b548c4"),
}
ENTRIES = {
    "strcspn": {
        "function": "open_cfw_bootloader_strcspn",
        "stock_address": 0x004157F8,
        "stock_size": 34,
        "stock_sha256": "f37ecd01540d7e9eb35cce13ef72d20c729e84932a0cbf296f3ff8d8ac58c5cb",
        "callers": (0x00410A82, 0x00411CF8, 0x00411D74),
        "offset": 996,
        "runtime_address": 0x0043485C,
        "size": 30,
        "sha256": "d331d9fb8cccb8f60badaf3dfab936298bdf11cf61320cca6ce19008d42e3096",
        "replacement": "1ff030b8" + "00bf" * 15,
    },
    "strspn": {
        "function": "open_cfw_bootloader_strspn",
        "stock_address": 0x0041581A,
        "stock_size": 34,
        "stock_sha256": "9abdb501517f35c72df7dd947891eb902da69f5598591ba36103bf450bdeb7fa",
        "callers": (0x00410A9A, 0x00411CEA, 0x00411D68),
        "offset": 1026,
        "runtime_address": 0x0043487A,
        "size": 28,
        "sha256": "f955f2e0febe0b7b844837f389b4eb1e601e349bf6f9183426b2e16de8961d22",
        "replacement": "1ff02eb8" + "00bf" * 15,
    },
}
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
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="open-cfw-boot-spans-audit-") as raw:
        output = Path(raw)
        subprocess.run(["python3", str(BUILDER), "--output-dir", str(output)], cwd=ROOT, check=True, capture_output=True, text=True)
        report = json.loads((output / "build-report.json").read_text(encoding="utf-8"))
        overlay = (output / "bootloader_core_overlay.bin").read_bytes()
        provider = (output / "ota_s200_bootloader.bin").read_bytes()
    require((len(overlay), digest(overlay)) == OVERLAY, "overlay identity changed")
    require((len(provider), digest(provider)) == PROVIDER, "provider identity changed")
    entry_report = {}
    for name, expected in ENTRIES.items():
        start = expected["stock_address"] - RUN_BASE
        stock = official[start:start + expected["stock_size"]]
        require((len(stock), digest(stock)) == (expected["stock_size"], expected["stock_sha256"]), f"{name} stock entry changed")
        callers = tuple(address for address in range(RUN_BASE, RUN_BASE + len(official) - 3, 2) if decode_bl(official, address) == expected["stock_address"])
        require(callers == expected["callers"], f"{name} caller topology changed")
        leaf = next((item for item in config["relocated_leaves"] if item["function"] == expected["function"]), None)
        require(leaf is not None and leaf["strict_relocation_contract"] is True, f"{name} strict leaf disappeared")
        require(leaf["relocations"] == [], f"{name} gained relocations")
        require((leaf["expected"]["offset"], leaf["expected"]["size"], leaf["expected"]["sha256"]) == (expected["offset"], expected["size"], expected["sha256"]), f"{name} leaf pins changed")
        require(report["overlay"]["functions"][expected["function"]] == {"offset": expected["offset"], "size": expected["size"]}, f"{name} placement changed")
        patch = next(item for item in report["overlay"]["patched_sites"] if item["name"] == f"replace_bootloader_{name}")
        require((patch["target_address"], patch["expected_size"], patch["expected_sha256"], patch["replacement_hex"]) == (expected["runtime_address"], expected["stock_size"], expected["stock_sha256"], expected["replacement"]), f"{name} patch contract changed")
        entry_report[name] = {"stock_address": expected["stock_address"], "stock_size": expected["stock_size"], "callers": len(callers), "source_address": expected["runtime_address"], "source_size": expected["size"], "relocations": 0}
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
        "component": "G2 Apollo bootloader string-span primitives",
        "status": "implemented-in-source / hardware-validation-blocked",
        "software_gap_count": 0,
        "entries": entry_report,
        "provider": {"size": PROVIDER[0], "sha256": PROVIDER[1], "source_owned_bytes": 9211, "generated_patch_bytes": 10542, "retained_official_bytes": 138057},
        "deployment": {"apple_package": {"size": PACKAGE[0], "sha256": PACKAGE[1]}, "linux_package": {"size": LINUX_PACKAGE[0], "sha256": LINUX_PACKAGE[1]}},
        "hardware_block": {"physical_evidence_available": False, "required_evidence": "authorized responsive G2 right temple demonstrating boot progression through all six authenticated string-span callers", "stock_bootloader_retained_for_hardware": True},
        "safety": {"hardware_operations": [], "signing_performed": False, "flashing_performed": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else f"Bootloader string-span closure: {report['status']}\n  authenticated callers: 6\n  hardware operations: none; physical validation unavailable")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader string-span audit failed: {exc}") from exc
