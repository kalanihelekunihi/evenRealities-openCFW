#!/usr/bin/env python3
"""Register and correct the G2 SPOT-manager timer interrupt-service extent."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_timer_irq_service_42a04a.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-spotmgr-timer-irq-42a04a-source-closure.md"
BOOT_BASE = 0x00410000
FUNCTION = "open_cfw_bootloader_spotmgr_timer_irq_service_42a04a"
START = 0x0042A04A
END = 0x0042A078
NEXT_END = 0x0042A08C
STOCK_SHA = "2ce0019a9c986275a9d5c9ea8d04c05e055c163e2802417c4ee68be2fd2b7fd4"
UNRELOCATED_SHA = "fbeda6f0cc785f369e1ecc2da2a580a954b3c705058d8f32c3137dd609ae7e79"
SOURCE_SHA = "13c2ca02ec9303e3a1c0506b76f489599b6131a9fd33421fa59723ab724483b6"
APPLE_COMPONENT_SHA = "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"
LINUX_COMPONENT_SHA = "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"
FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-builtin", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall",
    "-Wextra", "-Werror", "-fno-ident", "-mllvm",
    "-enable-machine-outliner=never",
]
RELOCATIONS = (
    (0x02, "open_cfw_bootloader_critical_save_41b8ec", 0x0041B8EC),
    (0x12, "open_cfw_bootloader_spotmgr_transition_sequence_2b_428378", 0x00428378),
    (0x1E, "open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94", 0x00428A94),
    (0x22, "open_cfw_bootloader_spotmgr_timer_finish_41ccd6", 0x0041CCD6),
)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def source_record() -> dict[str, Any]:
    payload = SOURCE.read_bytes()
    if len(payload) != 2_589 or digest(payload) != SOURCE_SHA:
        raise SystemExit("SPOT-manager timer interrupt source identity changed")
    return {
        "path": SOURCE.relative_to(ROOT).as_posix(),
        "size": len(payload),
        "sha256": digest(payload),
        "license": "BSD-3-Clause",
        "origin": "Apollo510-compatible SPOT-manager boost-timer interrupt service",
        "upstream": "AmbiqSuite SDK 5.1.0 Apollo510 SPOT manager",
        "upstream_commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
        "evidence": EVIDENCE,
    }


def update_census(boot: bytes) -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ())
        rows = list(reader)
    function_seen = False
    gap_seen = False
    for row in rows:
        row_start = int(row["start"], 16)
        if row_start == START:
            if int(row["end"], 16) != 0x0042A074:
                raise SystemExit("SPOT-manager timer interrupt prior extent changed")
            row.update({
                "kind": "source_function",
                "name": "spotmgr_timer_irq_service_42a04a",
                "end": f"0x{END:08x}",
                "size": str(END - START),
                "sha256": digest(boot[START - BOOT_BASE:END - BOOT_BASE]),
                "disposition": "source_owned_production",
                "provider": "AmbiqSuite Apollo510 SPOT-manager timer ISR",
                "license_status": "BSD-3-Clause",
                "evidence": (
                    "reviewed production C with corrected authenticated extent, "
                    "exact dual-toolchain bytes, and a 100000-state host test"
                ),
            })
            function_seen = True
        elif row_start == 0x0042A074:
            if int(row["end"], 16) != NEXT_END:
                raise SystemExit("SPOT-manager post-ISR gap extent changed")
            row.update({
                "name": "post_mspi_gap_0042a078",
                "start": f"0x{END:08x}",
                "size": str(NEXT_END - END),
                "sha256": digest(boot[END - BOOT_BASE:NEXT_END - BOOT_BASE]),
                "evidence": (
                    "corrected to begin after the authenticated msr/pop ISR epilogue; "
                    "no recovered function entry in this exact interval"
                ),
            })
            gap_seen = True
    if not function_seen or not gap_seen:
        raise SystemExit("SPOT-manager ISR census rows were not found")
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
        raise SystemExit("authenticated SPOT-manager timer ISR body changed")
    relocations = [{
        "offset": offset,
        "type": "R_ARM_THM_CALL",
        "symbol": symbol,
        "symbol_type": "STT_NOTYPE",
        "target_address": target,
    } for offset, symbol, target in RELOCATIONS]
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
    print("registered SPOT-manager timer interrupt service at 0x0042A04A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
