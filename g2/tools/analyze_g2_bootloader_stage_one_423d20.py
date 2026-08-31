#!/usr/bin/env python3
"""Exact source-admission audit for the bootloader stage-one 0x423D20 graph."""

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
RUNTIME_ADDRESS = 0x00423D20
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CANDIDATE = ROOT / "research/admission/bootloader_stage_one_423d20"
ASSEMBLY = CANDIDATE / "runtime_bootloader_stage_one_423d20.S"
HEADER = CANDIDATE / "runtime_bootloader_stage_one_423d20.h"
MODEL = CANDIDATE / "runtime_bootloader_stage_one_423d20_model.c"
CENSUS = ROOT / "tools/manifests/g2-bootloader-stage-one-423d20.tsv"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"

FILE_PINS = {
    ASSEMBLY: (3477, "9688273a0aa2b030f49dcd31c44e178cc924fa18c5a5908ca8429673a088a074"),
    HEADER: (1856, "08b78221eff605e5a07885e8fd5f7ab2544e4dc5197db3df7cc8343ddca7f23b"),
    MODEL: (1670, "8795a361c45f9fae40fb55a624790448c5902f5dd7d50050dc573cdb5ff9416e"),
    CENSUS: (2516, "92db0c47d4013709f7af0190d5a7491dabef2cd4d64a9351d84fc39f1b3905ef"),
}

SPANS = (
    ("stage_one_entry", 0x00423D20, 0x00423D58, "e4c5106b0aba4050c24d6e8afc548516c92c295bec52ed0397c029a4bad40850"),
    ("stage_one_status", 0x00423D58, 0x00423D7A, "147c53dc0c6246332d50080fbb99095103cdf73f3c89014027bdaa261ab30e68"),
    ("stage_one_wait_reg80", 0x00423D7A, 0x00423D9A, "43b8c7f2aeaba4ddf52365d8bb3eefb7391bdd57169fe64c618552989a536824"),
    ("stage_one_register_literal", 0x00423D9A, 0x00423DA0, "7cf4979cad48b6ce2b499300c3c3b8ed96387be1abbadcd932aba625b082f975"),
    ("stage_one_wait_index", 0x00423DA0, 0x00423DC4, "c5f33fc0af91c57d50e522764587e3d6aa5a7bd031187567023c6d825b333c36"),
    ("stage_one_wait_zero", 0x00423DC4, 0x00423DCE, "721f0a9d955a564fa40b09a08980d999ef5cddfb5c55598a28093affa4ef86a6"),
)
CLUSTER_SHA256 = "40a472fa5f161c713a218060464481a0f2722dea60bff8b8a6a51253264481bc"

RELOCATIONS = (
    (0x04, "open_cfw_bootloader_stage_one_status_423d58", 0x00423D58),
    (0x24, "open_cfw_bootloader_delay_status_change_41d21c", 0x0041D21C),
    (0x2C, "open_cfw_bootloader_debug_disable_422468", 0x00422468),
    (0x3A, "open_cfw_bootloader_stage_one_wait_zero_423dc4", 0x00423DC4),
    (0x42, "open_cfw_bootloader_stage_one_wait_reg80_423d7a", 0x00423D7A),
    (0x52, "open_cfw_bootloader_retained_delay_41d1c0", 0x0041D1C0),
    (0x68, "open_cfw_bootloader_delay_status_change_41d21c", 0x0041D21C),
    (0x92, "open_cfw_bootloader_delay_status_change_41d21c", 0x0041D21C),
    (0xA8, "open_cfw_bootloader_stage_one_wait_index_423da0", 0x00423DA0),
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


def build_profile(clang: str, objcopy: str, objdump: str, output: Path) -> tuple[bytes, tuple]:
    obj = output / (Path(clang).name.replace("/", "_") + "-stage-one.o")
    raw = obj.with_suffix(".bin")
    subprocess.run(
        [clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
         "-c", str(ASSEMBLY), "-o", str(obj)],
        check=True, capture_output=True, text=True,
    )
    subprocess.run(
        [objcopy, "-O", "binary",
         "--only-section=.text.open_cfw_bootloader_stage_one_423d20",
         str(obj), str(raw)],
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
    payload = bytearray(raw.read_bytes())
    require(len(payload) == 174, f"target cluster size changed under {clang}")
    for offset, _, target in RELOCATIONS:
        payload[offset:offset + 4] = encode_thumb_bl(RUNTIME_ADDRESS + offset, target)
    return bytes(payload), found


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
    stock = image[0x00423D20 - RUN_BASE:0x00423DCE - RUN_BASE]
    require(digest(stock) == CLUSTER_SHA256, "stock cluster identity changed")

    expected_callers = {
        0x00423D20: (0x0041FAA4,),
        0x00423D58: (0x00423D24,),
        0x00423D7A: (0x00423D62,),
        0x00423DA0: (0x00423DC8,),
        0x00423DC4: (0x00423D5A,),
    }
    for target, expected in expected_callers.items():
        require(direct_callers(image, target) == expected, f"caller graph changed: {target:#x}")

    source = ASSEMBLY.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    model = MODEL.read_text(encoding="utf-8")
    require("SPDX-License-Identifier: MIT" in source + header + model, "MIT SPDX missing")
    require(".byte" not in source and ".inst" not in source, "raw opcode transcription is not maintainable source")
    for token in (
        "open_cfw_bootloader_delay_status_change_41d21c",
        "open_cfw_bootloader_debug_disable_422468",
        "open_cfw_bootloader_retained_delay_41d1c0",
        "0xE0000E80", "#500", "#1000",
    ):
        require(token in source + header, f"source ABI token missing: {token}")

    objcopy = llvm_tool("llvm-objcopy")
    objdump = llvm_tool("llvm-objdump")
    profiles = ["/usr/bin/clang"]
    homebrew_clang = Path("/opt/homebrew/opt/llvm@22/bin/clang")
    if homebrew_clang.is_file():
        profiles.append(str(homebrew_clang))
    with tempfile.TemporaryDirectory(prefix="open-cfw-stage-one-audit-") as raw:
        output = Path(raw)
        for clang in profiles:
            built, _ = build_profile(clang, objcopy, objdump, output)
            require(built == stock, f"normalized target bytes differ under {clang}")

    overlay_text = OVERLAY.read_text(encoding="utf-8")
    require("runtime_bootloader_stage_one_423d20" not in overlay_text,
            "isolated source candidate was unexpectedly production-routed")
    overlay = json.loads(overlay_text)
    routed = overlay.get("in_place_leaves", []) + overlay.get("relocated_leaves", [])
    production = {entry.get("runtime_address"): entry for entry in routed
                  if 0x00423D20 <= entry.get("runtime_address", 0) < 0x00423DCE}
    expected_production = {
        start: expected_hash for name, start, end, expected_hash in SPANS
        if name != "stage_one_register_literal"
    }
    require(set(production) == set(expected_production),
            "production stage-one ownership graph changed")
    for address, expected_hash in expected_production.items():
        entry = production[address]
        require(entry.get("source", {}).get("path")
                == "components/bootloader/core_overlay/runtime_hw_control_services_423d20.c"
                and entry.get("source", {}).get("license") == "MIT",
                f"production stage-one provenance changed: {address:#x}")
        require(entry.get("stock", {}).get("sha256") == expected_hash
                and entry.get("expected", {}).get("sha256") == expected_hash,
                f"production stage-one exact-body contract changed: {address:#x}")
    provider_rows = [row for row in rows if row["kind"] == "provider"]
    unresolved = tuple(row["name"] for row in provider_rows
                       if "unresolved" in row["license_status"])
    require(unresolved == ("delay_status_change", "retained_delay"),
            "provider license blockers changed")

    return {
        "component": "G2 bootloader stage-one status graph",
        "status": "exact candidate reconciled with equivalent production source",
        "source": {
            "start": 0x00423D20, "end": 0x00423DCE,
            "executable_bytes": 168, "literal_bytes": 6,
            "sha256": CLUSTER_SHA256, "profiles": len(profiles),
        },
        "providers": {
            "typed_calls": 9,
            "source_owned": ["debug_disable"],
            "unresolved_license_or_source": list(unresolved),
        },
        "production": {
            "equivalent_source_routed": True,
            "isolated_candidate_routed": False,
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
        print("Bootloader stage-one 0x423d20: exact isolated source candidate")
        print("  normalized target bytes: exact under both profiles")
        print("  equivalent exact MIT source is already production-routed")
        print("  two retained providers remain redistribution blockers")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Bootloader stage-one audit failed: {exc}") from exc
