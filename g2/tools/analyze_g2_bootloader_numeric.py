#!/usr/bin/env python3
"""Fail-closed source/build audit for the G2 bootloader numeric helpers."""

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
OVERLAY_ADDRESS = 0x00434478

SOURCE_PINS = {
    COMPONENT / "runtime_udiv10.c": (503, "07aad3a209f72364611a414d96ccd7ae90a2e77395bcc2a1c2ee0253c2d6a0d9"),
    COMPONENT / "runtime_udiv10.h": (222, "6a2ae5ff4086de7ac2f367ab05929ffc5981e53e5808af7c9fcfa153837e7928"),
    COMPONENT / "runtime_numeric.h": (1067, "d47e10d491de3bae2679ec9ac8148f9d56e8e81a67d1892b3290403ab2e17a03"),
    COMPONENT / "runtime_udec_digits.c": (405, "45e2280f132aa67416ae0db36957f1bef15e9680c15f242bdab27c0cb806647e"),
    COMPONENT / "runtime_sdec_digits.c": (349, "7a17b01833b2ce6eb8b43ba72bd2c4c299e0c4f0217007be0bd7e8604c4ab6b8"),
    COMPONENT / "runtime_hex_digits.c": (298, "bd5b8ee533f2c3be7a1975740e8d455cbc52e2de578358e3de9471fa77d7d182"),
    COMPONENT / "runtime_parse_dec.c": (728, "4bc07532ba67ef07c32f1a061d468f77ff72caf9ee5797eb7116b256d84543ee"),
    COMPONENT / "runtime_u64_to_dec.c": (710, "bde9a306740d5619bfd0d2aab99420fb408cdf80dfbce1f3152dd17ab2a13f06"),
    COMPONENT / "runtime_u64_to_hex.c": (838, "488ce02ee663caa60ab9a12192bee035cc4bc6b5e0d0f4567d6e2151aebf5c39"),
    COMPONENT / "runtime_nullable_strlen.c": (330, "59144871f6c479c5d853cc309d6ea688f9a07bb078585dd613571c44b29dcd99"),
    COMPONENT / "runtime_repeat_char.c": (478, "deab8b51da6dbb862c58b6f0c8eb6a67706bb377e14139122a57f894ca068349"),
    COMPONENT / "runtime_float_to_fixed.c": (3041, "b586dd014fed40e8f28118e4891cde433c318675c091299c40ef9cc18edeecd9"),
}

FUNCTIONS = (
    {
        "function": "open_cfw_bootloader_udiv10",
        "stock_address": 0x00415844,
        "stock_size": 188,
        "stock_sha256": "193eb3cd689460ea3fcc0e840a7899200f5d430b601bc86b96fe36110031a536",
        "callers": (0x00415912, 0x004159B4),
        "offset": 1112,
        "size": 106,
        "sha256": "4295ddbce56a2ae2b23df120be24b5756eb71ea80842c392c390f303880872a6",
        "unrelocated_sha256": "4295ddbce56a2ae2b23df120be24b5756eb71ea80842c392c390f303880872a6",
        "relocations": (),
    },
    {
        "function": "open_cfw_bootloader_udec_digits",
        "stock_address": 0x00415900,
        "stock_size": 36,
        "stock_sha256": "5cb5a2122755c72fe1feee92066675fd744718498be799c4b7163476c5bb30da",
        "callers": (0x00415930, 0x00415E36),
        "offset": 1218,
        "size": 28,
        "sha256": "6386d3a8ce78e1d2d7cb9f6f1528e5baf14ad2bf949d1ca78bd7f9c295002200",
        "unrelocated_sha256": "0f777f7fce9bc6f0f7ff4d11d25815af4bcc531b52d1bb8e112683cd5404aab0",
        "relocations": ((14, "R_ARM_THM_CALL", "open_cfw_bootloader_udiv10"),),
    },
    {
        "function": "open_cfw_bootloader_sdec_digits",
        "stock_address": 0x00415924,
        "stock_size": 18,
        "stock_sha256": "84075552582aa3faed79585d7af9bfad49ea10cf6c5f023343cf1acd47ae5b35",
        "callers": (0x00415EB0,),
        "offset": 1246,
        "size": 20,
        "sha256": "30f15a834bafce03d4a2e39f5d7d0291887c478fa3ad815ab152fb4fcb39e14b",
        "unrelocated_sha256": "87503ca05ba402c4aab51eef8c9cd139b9482a413556133382ba70476884dcf5",
        "relocations": ((16, "R_ARM_THM_JUMP24", "open_cfw_bootloader_udec_digits"),),
    },
    {
        "function": "open_cfw_bootloader_hex_digits",
        "stock_address": 0x00415936,
        "stock_size": 38,
        "stock_sha256": "b32fcab992f19ef52dc494a38c6c8a5269c8bb5ec39f0a62ddb3030ef01280d7",
        "callers": (0x00415DD0,),
        "offset": 1266,
        "size": 24,
        "sha256": "6b3adefeb3b90ab3e15f08d57506b9816e6b7e287c3e1e83ea79c5f5faf9da3e",
        "unrelocated_sha256": "6b3adefeb3b90ab3e15f08d57506b9816e6b7e287c3e1e83ea79c5f5faf9da3e",
        "relocations": (),
    },
    {
        "function": "open_cfw_bootloader_parse_dec",
        "stock_address": 0x0041595C,
        "stock_size": 68,
        "stock_sha256": "82f777f8f00d318187e88d72d7a0a4d5d7a61b8ea7e1981b9d3472999e433caf",
        "callers": (0x00415C64, 0x00415CA4),
        "offset": 1290,
        "size": 48,
        "sha256": "ace0135fe9f0230855197b88faf6af8fb79292f2ac4fbba765f8d594bb88d462",
        "unrelocated_sha256": "ace0135fe9f0230855197b88faf6af8fb79292f2ac4fbba765f8d594bb88d462",
        "relocations": (),
    },
    {
        "function": "open_cfw_bootloader_u64_to_dec",
        "stock_address": 0x004159A0,
        "stock_size": 104,
        "stock_sha256": "8d34c568f2d0799b69f812076b3c2a84f2ee6c9c5a0e46a2782e87f9c2a435e0",
        "callers": (0x00415B64, 0x00415B76, 0x00415E62, 0x00415F30),
        "offset": 1338,
        "size": 74,
        "sha256": "2c131175df18cf4d4eb14af3c6ef64c2da035c42f23e50f711e829d73a3205e1",
        "unrelocated_sha256": "8d82b8e2fa35a8c602ea4a69f59719e249f931a9a99e8385620f342e79b1d01d",
        "relocations": ((22, "R_ARM_THM_CALL", "open_cfw_bootloader_udiv10"),),
    },
    {
        "function": "open_cfw_bootloader_u64_to_hex",
        "stock_address": 0x00415A08,
        "stock_size": 116,
        "stock_sha256": "e53ad1ebe639d9b80c3bf2f5a2c2228698a5a0b9849cc0ddebdea54e7caee28c",
        "callers": (0x00415E00,),
        "offset": 1412,
        "size": 72,
        "sha256": "d00e848bd2b979f3e34d0fe39d17ee1387eda21966360cf3f9cb5b4b8e4d9cb6",
        "unrelocated_sha256": "d00e848bd2b979f3e34d0fe39d17ee1387eda21966360cf3f9cb5b4b8e4d9cb6",
        "relocations": (),
    },
    {
        "function": "open_cfw_bootloader_nullable_strlen",
        "stock_address": 0x00415A7C,
        "stock_size": 24,
        "stock_sha256": "b2232233b8706cc7900d6aea4f778cc04d1859ba9a969ea895a2648eecb364d1",
        "callers": (0x00415D16,),
        "offset": 1484,
        "size": 20,
        "sha256": "fb0242904bfe442fbc6d61d275e46cbb4acfd8fe9d0aa1c5128b60542b802efa",
        "unrelocated_sha256": "fb0242904bfe442fbc6d61d275e46cbb4acfd8fe9d0aa1c5128b60542b802efa",
        "relocations": (),
    },
    {
        "function": "open_cfw_bootloader_repeat_char",
        "stock_address": 0x00415A94,
        "stock_size": 34,
        "stock_sha256": "e8b9ffb732e3d15c42a4e890c903fa548091b27e57858fa91044b78ff127b636",
        "callers": (0x00415D3E, 0x00415D8C, 0x00415DE0, 0x00415E46, 0x00415EE2),
        "offset": 1504,
        "size": 32,
        "sha256": "f2bc5eeddd15814db65a25945e356afb8e20c158921520b32db269fedb58fa00",
        "unrelocated_sha256": "f2bc5eeddd15814db65a25945e356afb8e20c158921520b32db269fedb58fa00",
        "relocations": (),
    },
    {
        "function": "open_cfw_bootloader_float_to_fixed",
        "stock_address": 0x00415AB6,
        "stock_size": 320,
        "stock_sha256": "d3c06c2907e1a0e8b3890aae57449889724a45e0a45bb167c8947d8de11743d6",
        "callers": (0x00415F5E,),
        "offset": 1536,
        "alignment": 8,
        "size": 320,
        "sha256": "c127b325a2b36be0aae257659caea624cc2080ba4e04326de56a23e03613d0a5",
        "unrelocated_sha256": "22706de7bb71b4c48e9325224244f01b454c9ca0e4c79944441eb281b5429fad",
        "relocations": ((160, "R_ARM_THM_CALL", "open_cfw_bootloader_u64_to_dec"),),
    },
)

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
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    leaves = {item["function"]: item for item in config["relocated_leaves"]}
    for expected in FUNCTIONS:
        start = expected["stock_address"] - RUN_BASE
        stock = official[start:start + expected["stock_size"]]
        require((len(stock), digest(stock)) == (expected["stock_size"], expected["stock_sha256"]), f"{expected['function']}: stock entry changed")
        callers = tuple(address for address in range(RUN_BASE, RUN_BASE + len(official) - 3, 2) if decode_bl(official, address) == expected["stock_address"])
        require(callers == expected["callers"], f"{expected['function']}: caller topology changed")
        leaf = leaves.get(expected["function"])
        require(leaf is not None and leaf["strict_relocation_contract"] is True, f"{expected['function']}: strict leaf disappeared")
        pins = leaf["expected"]
        require((pins["offset"], pins["alignment"], pins["size"], pins["sha256"], pins["unrelocated_sha256"]) == (expected["offset"], expected.get("alignment", 2), expected["size"], expected["sha256"], expected["unrelocated_sha256"]), f"{expected['function']}: leaf pins changed")
        relocations = tuple((item["offset"], item["type"], item["target_function"]) for item in leaf["relocations"])
        require(relocations == expected["relocations"], f"{expected['function']}: relocation contract changed")

    with tempfile.TemporaryDirectory(prefix="open-cfw-boot-numeric-audit-") as raw:
        output = Path(raw)
        subprocess.run(["python3", str(BUILDER), "--output-dir", str(output)], cwd=ROOT, check=True, capture_output=True, text=True)
        report = json.loads((output / "build-report.json").read_text(encoding="utf-8"))
        overlay = (output / "bootloader_core_overlay.bin").read_bytes()
        provider = (output / "ota_s200_bootloader.bin").read_bytes()
    require((len(overlay), digest(overlay)) == OVERLAY, "overlay identity changed")
    require((len(provider), digest(provider)) == PROVIDER, "provider identity changed")
    for expected in FUNCTIONS:
        function = expected["function"]
        require(report["overlay"]["functions"][function] == {"offset": expected["offset"], "size": expected["size"]}, f"{function}: placement changed")
        patch = next(item for item in report["overlay"]["patched_sites"] if item["target_function"] == function)
        require((patch["target_address"], patch["expected_size"], patch["expected_sha256"]) == (OVERLAY_ADDRESS + expected["offset"], expected["stock_size"], expected["stock_sha256"]), f"{function}: patch contract changed")
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
        "component": "G2 Apollo bootloader numeric runtime",
        "status": "implemented-in-source / hardware-validation-blocked",
        "software_gap_count": 0,
        "stock": {"function_count": len(FUNCTIONS), "direct_caller_count": sum(len(item["callers"]) for item in FUNCTIONS)},
        "source": {"function_count": len(FUNCTIONS), "compiled_bytes": sum(item["size"] for item in FUNCTIONS), "relocation_count": sum(len(item["relocations"]) for item in FUNCTIONS)},
        "provider": {"size": PROVIDER[0], "sha256": PROVIDER[1], "source_owned_bytes": 1849, "generated_patch_bytes": 2398, "alignment_bytes": 8, "retained_official_bytes": 146201},
        "deployment": {"apple_package": {"size": PACKAGE[0], "sha256": PACKAGE[1]}, "linux_package": {"size": LINUX_PACKAGE[0], "sha256": LINUX_PACKAGE[1]}},
        "hardware_block": {"physical_evidence_available": False, "required_evidence": "authorized responsive G2 right temple demonstrating boot progression and numeric formatting/parsing behavior through the authenticated callers", "stock_bootloader_retained_for_hardware": True},
        "safety": {"hardware_operations": [], "signing_performed": False, "flashing_performed": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else f"Bootloader numeric closure: {report['status']}\n  authenticated functions: {report['stock']['function_count']}\n  hardware operations: none; physical validation unavailable")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader numeric audit failed: {exc}") from exc
