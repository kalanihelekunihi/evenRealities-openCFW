#!/usr/bin/env python3
"""Register the source-owned hardware-context enable service."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path

R = Path(__file__).resolve().parent.parent
O = R / "components/bootloader/core_overlay/overlay.json"
S = R / "components/bootloader/core_overlay/runtime_hw_context_enable_42c538.c"
B = R / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
C = R / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
BASE = 0x410000
SS = 3720
SH = "4d85710f4613af13dfce38e85c2ff61e9bc94b2683573642116b0e17e2668ae2"
FN = "open_cfw_bootloader_hw_context_enable_42c538"
A = 0x42C538
Z = 0x42C63A
BH = "0183cf1cab1b0089fb0b49f71137bf868309198abd9319ca1e35f794ba430f2a"
UH = "0541dca0e2b4a414177436b877cf5473f5b854a12b96d4d98724747ac1293da4"
FL = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-builtin", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall",
    "-Wextra", "-Werror", "-fno-ident", "-mllvm",
    "-enable-machine-outliner=never",
]
RS = (
    (0x38, "open_cfw_bootloader_hw_status_route_42c034", 0x42C034),
    (0x98, "open_cfw_bootloader_cmdq_adapter_init_42c3e2", 0x42C3E2),
    (0xC6, "open_cfw_bootloader_retained_status_check_41d246", 0x41D246),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    source = S.read_bytes()
    boot = B.read_bytes()
    if (len(source), sha(source)) != (SS, SH):
        raise SystemExit("hardware-context enable source changed")
    if sha(boot[A - BASE:Z - BASE]) != BH:
        raise SystemExit("hardware-context enable stock body changed")
    record = {
        "path": S.relative_to(R).as_posix(), "size": SS, "sha256": SH,
        "license": "MIT",
        "origin": "clean-room hardware-context enable and rollback sequence",
        "evidence": "docs/research/g2-bootloader-hw-context-enable-42c538-source-closure.md",
    }
    relocations = [
        {"offset": offset, "type": "R_ARM_THM_CALL", "symbol": symbol,
         "symbol_type": "STT_NOTYPE", "target_address": target}
        for offset, symbol, target in RS
    ]
    pins = {"size": Z - A, "sha256": BH, "unrelocated_sha256": UH}
    entry = {
        "function": FN, "runtime_address": A, "source": record,
        "toolchain": {
            "target": "arm-none-eabi",
            "reviewed_version_prefix": "Apple clang version 21.0.0",
            "flags": FL,
        },
        "strict_relocation_contract": True, "expected": pins,
        "stock": {"size": Z - A, "sha256": BH},
        "relocations": relocations, "allow_discarded_alloc_sections": True,
        "toolchain_profiles": {"linux-clang": {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
            "expected": pins, "stock": {"size": Z - A, "sha256": BH},
            "relocations": relocations,
        }},
    }
    overlay = json.loads(O.read_text())
    overlay["in_place_leaves"] = sorted(
        [item for item in overlay["in_place_leaves"] if item.get("function") != FN]
        + [entry], key=lambda item: int(item["runtime_address"])
    )
    tmp = O.with_name(f".{O.name}.tmp")
    tmp.write_text(json.dumps(overlay, indent=2) + "\n")
    tmp.replace(O)
    with C.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ())
        rows = list(reader)
    row = next((item for item in rows if int(item["start"], 16) == A), None)
    if row is None or int(row["end"], 16) != Z:
        raise SystemExit("hardware-context enable census changed")
    row.update({
        "kind": "source_function", "name": "hw_context_enable_42c538",
        "disposition": "source_owned_production",
        "provider": "clean-room hardware-context enable service",
        "license_status": "MIT",
        "evidence": "exact dual-toolchain body with portable behavioral model",
    })
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t",
                            lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    C.write_text(output.getvalue())
    print("registered hardware-context enable service")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
