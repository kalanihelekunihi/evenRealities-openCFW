#!/usr/bin/env python3
"""Exact source-admission audit for the G2 bootloader 0x423DD0 frontier."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
RUN_BASE = 0x00410000
STATUS_ADDRESS = 0x00423DD0
MODE_ADDRESS = 0x00423E14
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CANDIDATE = ROOT / "research/admission/bootloader_stage_two_423dd0"
ASSEMBLY = CANDIDATE / "runtime_bootloader_stage_two_423dd0.S"
HEADER = CANDIDATE / "runtime_bootloader_stage_two_423dd0.h"
MODEL = CANDIDATE / "runtime_bootloader_stage_two_423dd0_model.c"
CENSUS = ROOT / "tools/manifests/g2-bootloader-stage-two-423dd0.tsv"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"

FILE_PINS = {
    ASSEMBLY: (2087, "ef3762a723d9b7d2c7d2ea06e70f78141d6941cc44ab46a1e3d7c5a19d03756e"),
    HEADER: (1366, "ebff659ff3b0aa40b03b55757e7744ff27981285a40a5b7458d62c9ba96467ff"),
    MODEL: (1306, "ce60266ed85bbadfc26be259f64b4c64daeef72065a31303b5098d48af4907e8"),
    CENSUS: (1951, "bcc7ec3e2b1b08444bd2681c3e6aa8962610fb1cff465c247ae21776abfaba39"),
}

SPANS = (
    ("stage_two_status", 0x00423DD0, 0x00423E0C,
     "946b697419fa8bb2a0eb8988766eaacf053308752bd1ea57f7bbfc353e744002"),
    ("stage_two_sram_literals", 0x00423E0C, 0x00423E14,
     "eb9eccfa0c7b87835a778c7ab67a2f4201b14d38a0d6b02bbb85a110f172d963"),
    ("stage_two_mode_flags", 0x00423E14, 0x00423E40,
     "7179c8490a752b21bfb18de838e98aa785e90da2cbde22e10356fc75829045c1"),
)
CLUSTER_SHA256 = "b6f037077c2577f042a56ca31101ce7c6734eda572bf1d613195bb3967064c12"
RELOCATIONS = (
    (0x02, "open_cfw_bootloader_critical_save_41b8ec", 0x0041B8EC),
    (0x26, "open_cfw_bootloader_debug_disable_422468", 0x00422468),
)


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def encode_thumb_bl(address: int, target: int) -> bytes:
    offset = target - (address + 4)
    require(offset % 2 == 0 and -(1 << 24) <= offset < (1 << 24), "BL range invalid")
    immediate = offset & ((1 << 25) - 1)
    sign = (immediate >> 24) & 1
    i1 = (immediate >> 23) & 1
    i2 = (immediate >> 22) & 1
    j1 = (~(i1 ^ sign)) & 1
    j2 = (~(i2 ^ sign)) & 1
    first = 0xF000 | (sign << 10) | ((immediate >> 12) & 0x3FF)
    second = 0xD000 | (j1 << 13) | (j2 << 11) | ((immediate >> 1) & 0x7FF)
    return first.to_bytes(2, "little") + second.to_bytes(2, "little")


def decode_thumb_bl(image: bytes, address: int) -> int | None:
    offset = address - RUN_BASE
    if offset < 0 or offset + 4 > len(image):
        return None
    first = int.from_bytes(image[offset:offset + 2], "little")
    second = int.from_bytes(image[offset + 2:offset + 4], "little")
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    i1 = 1 ^ ((second >> 13) & 1) ^ sign
    i2 = 1 ^ ((second >> 11) & 1) ^ sign
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22)
                 | ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def direct_callers(image: bytes, target: int) -> tuple[int, ...]:
    return tuple(address for address in range(RUN_BASE, RUN_BASE + len(image) - 3, 2)
                 if decode_thumb_bl(image, address) == target)


def llvm_tool(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    candidate = Path("/opt/homebrew/opt/llvm/bin") / name
    require(candidate.is_file(), f"required LLVM tool unavailable: {name}")
    return str(candidate)


def build_profile(clang: str, objcopy: str, objdump: str, output: Path) -> bytes:
    obj = output / (Path(clang).name.replace("/", "_") + "-stage-two.o")
    status_raw = obj.with_name(obj.stem + "-status.bin")
    mode_raw = obj.with_name(obj.stem + "-mode.bin")
    subprocess.run(
        [clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
         "-c", str(ASSEMBLY), "-o", str(obj)],
        check=True, capture_output=True, text=True,
    )
    for section, raw in (
        (".text.open_cfw_bootloader_stage_two_423dd0", status_raw),
        (".text.open_cfw_bootloader_stage_two_mode_flags_423e14", mode_raw),
    ):
        subprocess.run(
            [objcopy, "-O", "binary", "--only-section=" + section, str(obj), str(raw)],
            check=True, capture_output=True, text=True,
        )
    listing = subprocess.run(
        [objdump, "-r", str(obj)], check=True, capture_output=True, text=True,
    ).stdout
    found = tuple(
        (int(match.group(1), 16), match.group(2))
        for match in re.finditer(
            r"^([0-9a-fA-F]{8})\s+R_ARM_THM_CALL\s+(\S+)$", listing, re.MULTILINE
        )
    )
    expected = tuple((offset, symbol) for offset, symbol, _ in RELOCATIONS)
    require(found == expected, f"target relocation graph changed under {clang}")
    status = bytearray(status_raw.read_bytes())
    mode = mode_raw.read_bytes()
    require((len(status), len(mode)) == (68, 44), f"target sizes changed under {clang}")
    for offset, _, target in RELOCATIONS:
        status[offset:offset + 4] = encode_thumb_bl(STATUS_ADDRESS + offset, target)
    return bytes(status) + mode


def audit() -> dict:
    image = OFFICIAL.read_bytes()
    require((len(image), digest(image)) == (
        148599, "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
    ), "official bootloader pin changed")
    for path, expected in FILE_PINS.items():
        payload = path.read_bytes()
        require((len(payload), digest(payload)) == expected, f"candidate pin changed: {path.name}")

    rows = list(csv.DictReader(CENSUS.read_text(encoding="utf-8").splitlines(), delimiter="\t"))
    indexed = {row["name"]: row for row in rows}
    for name, start, end, expected_hash in SPANS:
        body = image[start - RUN_BASE:end - RUN_BASE]
        require((len(body), digest(body)) == (end - start, expected_hash), f"stock span changed: {name}")
        row = indexed[name]
        require((int(row["start"], 16), int(row["end"], 16), int(row["size"]), row["sha256"])
                == (start, end, end - start, expected_hash), f"census row changed: {name}")
    stock = image[STATUS_ADDRESS - RUN_BASE:0x00423E40 - RUN_BASE]
    require((len(stock), digest(stock)) == (112, CLUSTER_SHA256), "stock cluster identity changed")
    require(tuple(int.from_bytes(stock[offset:offset + 4], "little") for offset in (60, 64))
            == (0x200271C2, 0x200271C3), "SRAM literal ownership changed")

    require(direct_callers(image, STATUS_ADDRESS) == (0x0041FAAE,), "stage-two caller changed")
    require(direct_callers(image, MODE_ADDRESS) == (0x00425E60, 0x00425FFE),
            "mode-flags callers changed")

    source = ASSEMBLY.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    model = MODEL.read_text(encoding="utf-8")
    require("SPDX-License-Identifier: MIT" in source + header + model, "MIT SPDX missing")
    require(".byte" not in source and ".inst" not in source,
            "raw opcode transcription is not maintainable source")
    for token in (
        "open_cfw_bootloader_critical_save_41b8ec",
        "open_cfw_bootloader_debug_disable_422468",
        "0x200271C2", "0x200271C3", "#0x838",
    ):
        require(token in source + header, f"source ABI token missing: {token}")

    objcopy = llvm_tool("llvm-objcopy")
    objdump = llvm_tool("llvm-objdump")
    profiles = ["/usr/bin/clang"]
    homebrew_clang = Path("/opt/homebrew/opt/llvm@22/bin/clang")
    if homebrew_clang.is_file():
        profiles.append(str(homebrew_clang))
    with tempfile.TemporaryDirectory(prefix="open-cfw-stage-two-audit-") as raw:
        output = Path(raw)
        for clang in profiles:
            built = build_profile(clang, objcopy, objdump, output)
            require(built == stock, f"normalized target bytes differ under {clang}")

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    routed = overlay.get("in_place_leaves", []) + overlay.get("relocated_leaves", [])
    names = {entry.get("function") for entry in routed}
    require("open_cfw_bootloader_debug_disable_422468" in names,
            "source-owned debug-disable provider is no longer routed")
    require("open_cfw_bootloader_stage_two_status_423dd0" not in names
            and "open_cfw_bootloader_stage_two_mode_flags_423e14" not in names,
            "isolated candidate symbol was unexpectedly production-routed")
    production_status = [entry for entry in routed
                         if entry.get("runtime_address") == STATUS_ADDRESS]
    require(len(production_status) == 1, "production stage-two ownership changed")
    production_status = production_status[0]
    require(production_status.get("function")
            == "open_cfw_bootloader_hw_control_critical_423dd0",
            "production stage-two symbol changed")
    require(production_status.get("source", {}).get("path")
            == "components/bootloader/core_overlay/runtime_hw_control_services_423d20.c"
            and production_status.get("source", {}).get("license") == "MIT",
            "production stage-two source provenance changed")
    require(production_status.get("expected") == {
                "size": 60,
                "sha256": SPANS[0][3],
                "unrelocated_sha256": "0d36101cb281da8307d72283c0c7c18df80e49b6c95e663fc2ade39468edd241",
            } and production_status.get("stock") == {
                "size": 60, "sha256": SPANS[0][3],
            }, "production stage-two exact-body contract changed")
    require(tuple((relocation.get("offset"), relocation.get("target_address"))
                  for relocation in production_status.get("relocations", []))
            == ((2, 0x0041B8EC), (38, 0x00422468)),
            "production stage-two provider graph changed")
    production_mode = [entry for entry in routed
                       if entry.get("runtime_address") == MODE_ADDRESS]
    require(len(production_mode) == 1, "production mode-flags ownership changed")
    production_mode = production_mode[0]
    require(production_mode.get("function")
            == "open_cfw_bootloader_hw_control_state_423e14"
            and production_mode.get("source", {}).get("path")
            == "components/bootloader/core_overlay/runtime_hw_control_state_423e14.c"
            and production_mode.get("source", {}).get("license") == "MIT",
            "production mode-flags provenance changed")
    require(production_mode.get("expected", {}).get("sha256") == SPANS[2][3]
            and production_mode.get("stock", {}).get("sha256") == SPANS[2][3]
            and production_mode.get("relocations") == [],
            "production mode-flags exact-body contract changed")

    critical = indexed["critical_save"]
    require("unresolved" in critical["license_status"],
            "critical-save redistribution blocker changed")
    require(indexed["stage_two_status"]["disposition"]
            == "exact_candidate_and_production_owned",
            "concurrent production ownership reconciliation changed")
    require(indexed["stage_two_mode_flags"]["disposition"]
            == "exact_candidate_and_production_owned",
            "provider-free production ownership reconciliation changed")

    return {
        "component": "G2 bootloader stage-two frontier",
        "status": "exact candidate reconciled with production source / admissible leaf",
        "source": {
            "start": STATUS_ADDRESS,
            "end": 0x00423E40,
            "executable_bytes": 104,
            "literal_bytes": 8,
            "sha256": CLUSTER_SHA256,
            "profiles": len(profiles),
        },
        "functions": {
            "stage_two_status": "exact-MIT-candidate / equivalent-MIT-production-source-routed",
            "stage_two_mode_flags": "exact-MIT-candidate / equivalent-MIT-production-source-routed",
        },
        "providers": {
            "typed_calls": 2,
            "source_owned": ["debug_disable"],
            "unresolved_license_or_source": ["critical_save"],
        },
        "production": {
            "equivalent_stage_two_source_routed": True,
            "isolated_candidate_routed": False,
            "equivalent_mode_flags_source_routed": True,
            "next_frontier": 0x00423E40,
        },
        "hardware_operations": [],
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Bootloader stage-two 0x423dd0: exact isolated source tranche")
        print("  mode-flags leaf: equivalent exact MIT source now production-routed")
        print("  status seam: equivalent exact MIT source already production-routed")
        print("  retained critical-save provider remains a redistribution blocker")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader stage-two audit failed: {exc}") from exc
