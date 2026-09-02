#!/usr/bin/env python3
"""Register the reviewed G2 bootloader SPOT-manager transition-7b leaf.

This tool updates source-ownership metadata only. It never signs, flashes,
resets, or communicates with hardware.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_transition_7b_428a94.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-spotmgr-transition-7b-428a94-source-closure.md"
BOOT_BASE = 0x00410000
FUNCTION = "open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94"
START = 0x00428A94
END = 0x00428BA8
STOCK_SHA = "1e0e7ddb0036670d692a97a50f6cc821d2a2358e741b72d502e943d31bb0b351"
UNRELOCATED_SHA = "b9d0e8cfa43d1d1a1514e2ff0fda56c2b0d50511f816d53894b19f7feb3975d8"
DELAY = "open_cfw_bootloader_delay_us_41d1c0"
STATUS_DELAY = "open_cfw_bootloader_delay_us_status_change_41d21c"
APPLE_COMPONENT_SHA = "94afbc3d7e1aa8d0d21095de081523c2ed9e422287355128eb20d36bf27c88e2"
LINUX_COMPONENT_SHA = "426d77749f96307ae9a45173d20684570d5994d902cf1f1f5cb01f935c6ba7c6"
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


def source_record() -> dict[str, Any]:
    payload = SOURCE.read_bytes()
    return {
        "path": SOURCE.relative_to(ROOT).as_posix(),
        "size": len(payload),
        "sha256": digest(payload),
        "license": "BSD-3-Clause",
        "origin": (
            "address-stable Apollo510 SPOT-manager transition_sequence_7b "
            "realization"
        ),
        "evidence": EVIDENCE,
        "upstream": "AmbiqSuite SDK 5.1.0 Apollo510 SPOT manager",
        "upstream_commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
    }


def update_census(boot: bytes) -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ())
        rows = list(reader)
    found = False
    for row in rows:
        if int(row["start"], 16) != START:
            continue
        if int(row["end"], 16) != END:
            raise SystemExit("SPOT-manager transition-7b census interval changed")
        row.update({
            "kind": "source_function",
            "name": "spotmgr_transition_sequence_7b_428a94",
            "size": str(END - START),
            "sha256": digest(boot[START - BOOT_BASE:END - BOOT_BASE]),
            "disposition": "source_owned_production",
            "provider": "AmbiqSuite Apollo510 SPOT-manager transition_sequence_7b",
            "license_status": "BSD-3-Clause",
            "evidence": (
                "reviewed production C with an exact dual-toolchain linked "
                "body and a 50000-state host differential test"
            ),
        })
        found = True
    if not found:
        raise SystemExit("SPOT-manager transition-7b census interval was not found")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t",
                            lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    CENSUS.write_text(output.getvalue(), encoding="utf-8")


def main() -> int:
    boot = BOOT.read_bytes()
    stock = boot[START - BOOT_BASE:END - BOOT_BASE]
    if len(stock) != END - START or digest(stock) != STOCK_SHA:
        raise SystemExit("authenticated SPOT-manager transition-7b body changed")
    relocations = []
    for offset, symbol, target in (
        (0x2E, DELAY, 0x0041D1C0),
        (0x64, DELAY, 0x0041D1C0),
        (0xB4, DELAY, 0x0041D1C0),
        (0xC6, STATUS_DELAY, 0x0041D21C),
        (0xEA, DELAY, 0x0041D1C0),
    ):
        relocations.append({
            "offset": offset,
            "type": "R_ARM_THM_CALL",
            "symbol": symbol,
            "symbol_type": "STT_NOTYPE",
            "target_address": target,
        })
    pins = {
        "size": END - START,
        "sha256": STOCK_SHA,
        "unrelocated_sha256": UNRELOCATED_SHA,
    }
    entry = {
        "function": FUNCTION,
        "runtime_address": START,
        "source": source_record(),
        "toolchain": {
            "target": "arm-none-eabi",
            "reviewed_version_prefix": "Apple clang version 21.0.0",
            "flags": FLAGS,
        },
        "strict_relocation_contract": True,
        "expected": pins,
        "stock": {"size": END - START, "sha256": STOCK_SHA},
        "relocations": relocations,
        "allow_discarded_alloc_sections": True,
        "toolchain_profiles": {
            "linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": pins,
                "stock": {"size": END - START, "sha256": STOCK_SHA},
                "relocations": relocations,
            }
        },
    }
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    retained = [item for item in overlay["in_place_leaves"]
                if item.get("function") != FUNCTION]
    overlay["in_place_leaves"] = sorted(
        [*retained, entry], key=lambda item: int(item["runtime_address"])
    )
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"][
        "component_sha256"
    ] = LINUX_COMPONENT_SHA
    write_json(OVERLAY, overlay)
    update_census(boot)
    print("registered SPOT-manager transition_sequence_7b at 0x00428A94")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
