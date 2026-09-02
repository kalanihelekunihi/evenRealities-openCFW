#!/usr/bin/env python3
"""Register the exact G2 SPOT-manager power/Ton state classifier."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_power_state_determine_42a550.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-spotmgr-power-state-determine-42a550-source-closure.md"
BOOT_BASE = 0x00410000
FUNCTION = "open_cfw_bootloader_spotmgr_power_state_determine_42a550"
START = 0x0042A550
END = 0x0042A85E
STOCK_SHA = "73e2c284f4c3efc45c0cb02ad3d2d5c520c56ce136e4c185a4fbd56b815a0d87"
SOURCE_SHA = "4e201c6adb3a27bb59f5347a3b4679c3b642b1c4079a3aedfaff5b23432fc1b9"
APPLE_COMPONENT_SHA = "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"
LINUX_COMPONENT_SHA = "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"
FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-builtin", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall",
    "-Wextra", "-Werror", "-fno-ident", "-mllvm",
    "-enable-machine-outliner=never",
]


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def update_census() -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ())
        rows = list(reader)
    seen = False
    for row in rows:
        if int(row["start"], 16) != START:
            continue
        if int(row["end"], 16) != END or row["sha256"] != STOCK_SHA:
            raise SystemExit("SPOT-manager power-state census identity changed")
        row.update({
            "kind": "source_function",
            "name": "spotmgr_power_state_determine_42a550",
            "disposition": "source_owned_production",
            "provider": "AmbiqSuite Apollo510 SPOT-manager power/Ton state classifier",
            "license_status": "BSD-3-Clause",
            "evidence": (
                "reviewed production C with exact dual-toolchain bytes, "
                "authenticated literals/caller/main analogue, and 40960 host cases"
            ),
        })
        seen = True
    if not seen:
        raise SystemExit("SPOT-manager power-state census row not found")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    CENSUS.write_text(output.getvalue(), encoding="utf-8")


def main() -> int:
    source = SOURCE.read_bytes()
    if len(source) != 17_636 or digest(source) != SOURCE_SHA:
        raise SystemExit("SPOT-manager power-state source identity changed")
    stock = BOOT.read_bytes()[START - BOOT_BASE:END - BOOT_BASE]
    if len(stock) != END - START or digest(stock) != STOCK_SHA:
        raise SystemExit("authenticated SPOT-manager power-state body changed")
    pins = {"size": END - START, "sha256": STOCK_SHA, "unrelocated_sha256": STOCK_SHA}
    source_record = {
        "path": SOURCE.relative_to(ROOT).as_posix(), "size": len(source),
        "sha256": digest(source), "license": "BSD-3-Clause",
        "origin": "Apollo510-compatible SPOT-manager power/Ton state classifier",
        "upstream": "AmbiqSuite SDK 5.1.0 Apollo510 SPOT manager",
        "upstream_commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
        "evidence": EVIDENCE,
    }
    entry = {
        "function": FUNCTION, "runtime_address": START, "source": source_record,
        "toolchain": {
            "target": "arm-none-eabi",
            "reviewed_version_prefix": "Apple clang version 21.0.0", "flags": FLAGS,
        },
        "strict_relocation_contract": True, "expected": pins,
        "stock": {"size": END - START, "sha256": STOCK_SHA}, "relocations": [],
        "allow_discarded_alloc_sections": True,
        "toolchain_profiles": {"linux-clang": {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
            "expected": pins, "stock": {"size": END - START, "sha256": STOCK_SHA},
            "relocations": [],
        }},
    }
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    retained = [item for item in overlay["in_place_leaves"] if item.get("function") != FUNCTION]
    overlay["in_place_leaves"] = sorted([*retained, entry], key=lambda item: int(item["runtime_address"]))
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"]["component_sha256"] = LINUX_COMPONENT_SHA
    write_json(OVERLAY, overlay)
    update_census()
    print("registered SPOT-manager power-state classifier at 0x0042A550")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
