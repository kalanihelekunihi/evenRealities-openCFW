#!/usr/bin/env python3
"""Register the source-owned hardware configuration transaction."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path

R = Path(__file__).resolve().parent.parent
O = R / "components/bootloader/core_overlay/overlay.json"
S = R / "components/bootloader/core_overlay/runtime_hw_config_transaction_42c988.c"
B = R / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
C = R / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
BASE = 0x410000
SS = 7095
SH = "1e31cff5fb69b6256b7cb7081392364b3fd398402bad28bd30b058e902accbcf"
FN = "open_cfw_bootloader_hw_config_transaction_42c988"
A = 0x42C988
Z = 0x42CC34
BH = "1a89b00660cf0c54c66e781ac95f19dd764bb671587c36959ad2cd34fec53ae5"
UH = "904ef19dffe0d14d032fbab68fc23a1902fc9eb9704230e52a4a29e5d302503f"
FL = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-builtin", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall",
    "-Wextra", "-Werror", "-fno-ident", "-mllvm",
    "-enable-machine-outliner=never",
]
RS = (
    (0x04A, "open_cfw_bootloader_pwrctrl_periph_enable_41bf84", 0x41BF84),
    (0x11C, "open_cfw_bootloader_cmdq_adapter_enable_42c420", 0x42C420),
    (0x140, "open_cfw_bootloader_retained_status_check_41d246", 0x41D246),
    (0x152, "open_cfw_bootloader_mode_enable_route_4222f0", 0x4222F0),
    (0x258, "open_cfw_bootloader_cmdq_adapter_disable_42c44e", 0x42C44E),
    (0x290, "open_cfw_bootloader_pwrctrl_periph_disable_41c17a", 0x41C17A),
    (0x29C, "open_cfw_bootloader_mode_disable_route_422364", 0x422364),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    source = S.read_bytes()
    boot = B.read_bytes()
    if (len(source), sha(source)) != (SS, SH):
        raise SystemExit("hardware-config transaction source changed")
    if sha(boot[A - BASE:Z - BASE]) != BH:
        raise SystemExit("hardware-config transaction stock body changed")
    record = {
        "path": S.relative_to(R).as_posix(), "size": SS, "sha256": SH,
        "license": "MIT",
        "origin": "clean-room hardware configuration save/restore and resource transaction",
        "evidence": "docs/research/g2-bootloader-hw-config-transaction-42c988-source-closure.md",
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
        raise SystemExit("hardware-config transaction census changed")
    row.update({
        "kind": "source_function", "name": "hw_config_transaction_42c988",
        "disposition": "source_owned_production",
        "provider": "clean-room hardware configuration transaction",
        "license_status": "MIT",
        "evidence": "exact dual-toolchain body with portable behavioral model",
    })
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t",
                            lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    C.write_text(output.getvalue())
    print("registered hardware configuration transaction")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
