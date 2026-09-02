#!/usr/bin/env python3
"""Register the G2 SPOT-manager stepwise temperature-transition dispatcher."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = (
    ROOT / "components/bootloader/core_overlay/"
    "runtime_spotmgr_temperature_transition_separate_42a43a.c"
)
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = (
    "docs/research/"
    "g2-bootloader-spotmgr-temperature-transition-separate-42a43a-source-closure.md"
)
BOOT_BASE = 0x00410000
FUNCTION = "open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a"
START = 0x0042A43A
END = 0x0042A4BC
STOCK_SHA = "1075e4055c2ef66d985f8938f881a08d43a90791be3dc0b2700ff7e0074ed107"
UNRELOCATED_SHA = "066596bd21489fc692537d3fb5724af2ab6ba1eecb93d78b36ce35ea3a4d44cc"
SOURCE_SHA = "4de53020af984d02bceb30519540dc7dda7633e2ecd998dac51c82ef31b96766"
APPLE_COMPONENT_SHA = "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"
LINUX_COMPONENT_SHA = "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"
RELOCATIONS = (
    (0x28, "open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4", 0x0042A2B4),
    (0x58, "open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4", 0x0042A2B4),
)
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
    if len(payload) != 5_192 or digest(payload) != SOURCE_SHA:
        raise SystemExit("SPOT-manager temperature dispatcher source identity changed")
    return {
        "path": SOURCE.relative_to(ROOT).as_posix(),
        "size": len(payload),
        "sha256": digest(payload),
        "license": "BSD-3-Clause",
        "origin": "Apollo510-compatible SPOT-manager temperature dispatcher",
        "upstream": "AmbiqSuite SDK 5.1.0 Apollo510 SPOT manager",
        "upstream_commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
        "evidence": EVIDENCE,
    }


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
            raise SystemExit("SPOT-manager temperature dispatcher census identity changed")
        row.update({
            "kind": "source_function",
            "name": "spotmgr_temperature_transition_separate_42a43a",
            "disposition": "source_owned_production",
            "provider": "AmbiqSuite Apollo510 SPOT-manager temperature dispatcher",
            "license_status": "BSD-3-Clause",
            "evidence": (
                "reviewed production C with exact dual-toolchain bytes, two "
                "state-selector edges, and exhaustive valid-state-pair host tests"
            ),
        })
        seen = True
    if not seen:
        raise SystemExit("SPOT-manager temperature dispatcher census row not found")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output, fieldnames=fields, delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    CENSUS.write_text(output.getvalue(), encoding="utf-8")


def relocation_records() -> list[dict[str, Any]]:
    return [{
        "offset": offset,
        "type": "R_ARM_THM_CALL",
        "symbol": symbol,
        "symbol_type": "STT_NOTYPE",
        "target_address": target,
    } for offset, symbol, target in RELOCATIONS]


def main() -> int:
    stock = BOOT.read_bytes()[START - BOOT_BASE:END - BOOT_BASE]
    if len(stock) != END - START or digest(stock) != STOCK_SHA:
        raise SystemExit("authenticated SPOT-manager temperature dispatcher changed")
    relocations = relocation_records()
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
    retained = [
        item for item in overlay["in_place_leaves"]
        if item.get("function") != FUNCTION
    ]
    overlay["in_place_leaves"] = sorted(
        [*retained, entry], key=lambda item: int(item["runtime_address"])
    )
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"][
        "component_sha256"
    ] = LINUX_COMPONENT_SHA
    write_json(OVERLAY, overlay)
    update_census()
    print("registered SPOT-manager temperature dispatcher at 0x0042A43A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
