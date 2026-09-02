#!/usr/bin/env python3
"""Register the source-owned hardware event service."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path

R = Path(__file__).resolve().parent.parent
O = R / "components/bootloader/core_overlay/overlay.json"
S = R / "components/bootloader/core_overlay/runtime_hw_event_service_42c6f8.c"
B = R / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
C = R / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
BASE = 0x410000
SS = 8225
SH = "51c3bbd85505c2e89946ced24728ed528943a3ec02c38a0ea8c84e010fa87695"
FN = "open_cfw_bootloader_hw_event_service_42c6f8"
A = 0x42C6F8
Z = 0x42C980
BH = "7272867858e1c23f8ad5e5938ef7f5e02d59289de7c3c76eb6c7ea69fcec5958"
UH = "68622fb39f74db4f8713335ee263e25dc024684d86d5e59bc43f600a11ee72b4"
FL = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-builtin", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall",
    "-Wextra", "-Werror", "-fno-ident", "-mllvm",
    "-enable-machine-outliner=never",
]
RS = (
    (0x09E, "open_cfw_bootloader_hw_error_classify_42c076", 0x42C076),
    (0x0D8, "open_cfw_bootloader_hw_event_apply_42c0b2", 0x42C0B2),
    (0x0F4, "open_cfw_bootloader_hw_descriptor_publish_42c45a", 0x42C45A),
    (0x13E, "open_cfw_bootloader_cmdq_get_status_427a56", 0x427A56),
    (0x1D6, "open_cfw_bootloader_hw_error_classify_42c076", 0x42C076),
    (0x232, "open_cfw_bootloader_hw_event_apply_42c0b2", 0x42C0B2),
    (0x23A, "open_cfw_bootloader_cmdq_error_resume_427b38", 0x427B38),
    (0x246, "open_cfw_bootloader_cmdq_adapter_enable_42c420", 0x42C420),
    (0x252, "open_cfw_bootloader_cmdq_adapter_disable_42c44e", 0x42C44E),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    source = S.read_bytes()
    boot = B.read_bytes()
    if (len(source), sha(source)) != (SS, SH):
        raise SystemExit("hardware-event source changed")
    if sha(boot[A - BASE:Z - BASE]) != BH:
        raise SystemExit("hardware-event stock body changed")
    record = {
        "path": S.relative_to(R).as_posix(), "size": SS, "sha256": SH,
        "license": "MIT",
        "origin": "clean-room hardware event, descriptor, callback, and command-queue service",
        "evidence": "docs/research/g2-bootloader-hw-event-service-42c6f8-source-closure.md",
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
        raise SystemExit("hardware-event census changed")
    row.update({
        "kind": "source_function", "name": "hw_event_service_42c6f8",
        "disposition": "source_owned_production",
        "provider": "clean-room hardware event service",
        "license_status": "MIT",
        "evidence": "exact dual-toolchain body with portable behavioral model",
    })
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t",
                            lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    C.write_text(output.getvalue())
    print("registered hardware event service")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
