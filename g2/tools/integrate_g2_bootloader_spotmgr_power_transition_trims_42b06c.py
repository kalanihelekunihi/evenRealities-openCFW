#!/usr/bin/env python3
"""Register the G2 SPOT-manager power-transition trim transaction."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_power_transition_trims_42b06c.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-spotmgr-power-transition-trims-42b06c-source-closure.md"
BOOT_BASE = 0x00410000
FUNCTION = "open_cfw_bootloader_spotmgr_power_transition_trims_42b06c"
START = 0x0042B06C
END = 0x0042B294
STOCK_SHA = "44271365df4592f33c91286690e4e75e328a8dd11127aa934bec2c571292c377"
UNRELOCATED_SHA = "35646af379886e8764cde56a2bf9bc6fb22e94f53ea178c5c60dd1727d190127"
SOURCE_SHA = "1daae8e352b04325e7a1e519111e4a9207042e8b5740e1b59692b8afc0004a27"
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


def source_record() -> dict[str, Any]:
    payload = SOURCE.read_bytes()
    if len(payload) != 11_845 or digest(payload) != SOURCE_SHA:
        raise SystemExit("SPOT-manager power-transition source identity changed")
    return {
        "path": SOURCE.relative_to(ROOT).as_posix(), "size": len(payload),
        "sha256": digest(payload), "license": "BSD-3-Clause",
        "origin": "Apollo510-compatible SPOT-manager power-transition trim transaction",
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
            raise SystemExit("SPOT-manager power-transition extent changed")
        row.update({
            "kind": "source_function",
            "name": "spotmgr_power_transition_trims_42b06c",
            "size": str(END - START), "sha256": digest(boot[START - BOOT_BASE:END - BOOT_BASE]),
            "disposition": "source_owned_production",
            "provider": "AmbiqSuite Apollo510 SPOT-manager power-transition trim transaction",
            "license_status": "BSD-3-Clause",
            "evidence": "exact dual-toolchain body, two delay edges, Apollo-main analogue, and 10500 routed host cases",
        })
        seen = True
    if not seen:
        raise SystemExit("SPOT-manager power-transition census row not found")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    CENSUS.write_text(output.getvalue(), encoding="utf-8")


def main() -> int:
    boot = BOOT.read_bytes(); stock = boot[START - BOOT_BASE:END - BOOT_BASE]
    if len(stock) != END - START or digest(stock) != STOCK_SHA:
        raise SystemExit("authenticated SPOT-manager power-transition body changed")
    relocations = [{
        "offset": offset, "type": "R_ARM_THM_CALL",
        "symbol": "open_cfw_bootloader_delay_cycles_41d1c0",
        "symbol_type": "STT_NOTYPE", "target_address": 0x0041D1C0,
    } for offset in (0x76, 0x90)]
    pins = {"size": END - START, "sha256": STOCK_SHA,
            "unrelocated_sha256": UNRELOCATED_SHA}
    entry = {
        "function": FUNCTION, "runtime_address": START,
        "source": source_record(),
        "toolchain": {"target": "arm-none-eabi",
                      "reviewed_version_prefix": "Apple clang version 21.0.0",
                      "flags": FLAGS},
        "strict_relocation_contract": True, "expected": pins,
        "stock": {"size": END - START, "sha256": STOCK_SHA},
        "relocations": relocations, "allow_discarded_alloc_sections": True,
        "toolchain_profiles": {"linux-clang": {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
            "expected": pins, "stock": {"size": END - START, "sha256": STOCK_SHA},
            "relocations": relocations,
        }},
    }
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    retained = [item for item in overlay["in_place_leaves"] if item.get("function") != FUNCTION]
    overlay["in_place_leaves"] = sorted([*retained, entry], key=lambda item: int(item["runtime_address"]))
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"]["component_sha256"] = LINUX_COMPONENT_SHA
    write_json(OVERLAY, overlay); update_census(boot)
    print("registered SPOT-manager power-transition trims at 0x0042B06C")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
