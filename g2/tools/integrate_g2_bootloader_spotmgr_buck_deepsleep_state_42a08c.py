#!/usr/bin/env python3
"""Register the G2 SPOT-manager SIMOBUCK deep-sleep state classifier."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_buck_deepsleep_state_42a08c.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-spotmgr-buck-deepsleep-42a08c-source-closure.md"
BOOT_BASE = 0x00410000
FUNCTION = "open_cfw_bootloader_spotmgr_buck_deepsleep_state_42a08c"
START = 0x0042A08C
END = 0x0042A19C
STOCK_SHA = "d6be1f893c0f78437db76208bb71ae7bf478411acb3ec307430709cd3dfe2e67"
UNRELOCATED_SHA = "6e729b8c3c563a543f80219483d16ec5b38f5f31bb9afdf0d5869f7b3f70869c"
SOURCE_SHA = "45df23181652757089f6a69ff4a095ff8e68e392c627ed69db53f387feed9b72"
APPLE_COMPONENT_SHA = "94afbc3d7e1aa8d0d21095de081523c2ed9e422287355128eb20d36bf27c88e2"
LINUX_COMPONENT_SHA = "426d77749f96307ae9a45173d20684570d5994d902cf1f1f5cb01f935c6ba7c6"
FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-builtin", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall",
    "-Wextra", "-Werror", "-fno-ident", "-mllvm",
    "-enable-machine-outliner=never",
]
RELOCATION = (
    0x30, "open_cfw_bootloader_stimer_is_running_41f3f0", 0x0041F3F0,
)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def source_record() -> dict[str, Any]:
    payload = SOURCE.read_bytes()
    if len(payload) != 6_394 or digest(payload) != SOURCE_SHA:
        raise SystemExit("SPOT-manager SIMOBUCK classifier source identity changed")
    return {
        "path": SOURCE.relative_to(ROOT).as_posix(),
        "size": len(payload),
        "sha256": digest(payload),
        "license": "BSD-3-Clause",
        "origin": "Apollo510-compatible SPOT-manager SIMOBUCK deep-sleep classifier",
        "upstream": "AmbiqSuite SDK 5.1.0 Apollo510 SPOT manager",
        "upstream_commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
        "evidence": EVIDENCE,
    }


def update_census(boot: bytes) -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ())
        rows = list(reader)
    seen = False
    for row in rows:
        if int(row["start"], 16) != START:
            continue
        if int(row["end"], 16) != END:
            raise SystemExit("SPOT-manager SIMOBUCK classifier extent changed")
        row.update({
            "kind": "source_function",
            "name": "spotmgr_buck_deepsleep_state_42a08c",
            "size": str(END - START),
            "sha256": digest(boot[START - BOOT_BASE:END - BOOT_BASE]),
            "disposition": "source_owned_production",
            "provider": "AmbiqSuite Apollo510 SPOT-manager deep-sleep classifier",
            "license_status": "BSD-3-Clause",
            "evidence": (
                "reviewed production C with exact dual-toolchain bytes, one "
                "authenticated STIMER provider edge, and a 100000-state host test"
            ),
        })
        seen = True
    if not seen:
        raise SystemExit("SPOT-manager SIMOBUCK classifier census row not found")
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
        raise SystemExit("authenticated SPOT-manager SIMOBUCK classifier changed")
    offset, symbol, target = RELOCATION
    relocations = [{
        "offset": offset,
        "type": "R_ARM_THM_CALL",
        "symbol": symbol,
        "symbol_type": "STT_NOTYPE",
        "target_address": target,
    }]
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
    print("registered SPOT-manager SIMOBUCK classifier at 0x0042A08C")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
