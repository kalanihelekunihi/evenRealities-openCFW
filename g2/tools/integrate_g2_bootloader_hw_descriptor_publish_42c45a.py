#!/usr/bin/env python3
"""Register the source-owned hardware descriptor publisher."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path

R = Path(__file__).resolve().parent.parent
O = R / "components/bootloader/core_overlay/overlay.json"
S = R / "components/bootloader/core_overlay/runtime_hw_descriptor_publish_42c45a.c"
B = R / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
C = R / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
BASE = 0x410000
SS = 1650
SH = "a3a8b458d92e6ad3e61861c7e44dfad202d5a50cd53afd70af47d60b5936365f"
FN = "open_cfw_bootloader_hw_descriptor_publish_42c45a"
A = 0x42C45A
Z = 0x42C4C6
BH = "0deea2026365cb9c3471cdd81a7644c3fa519db2239154f3456da25ab88c5525"
FL = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-builtin", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall",
    "-Wextra", "-Werror", "-fno-ident", "-mllvm",
    "-enable-machine-outliner=never",
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    source = S.read_bytes()
    boot = B.read_bytes()
    if (len(source), sha(source)) != (SS, SH):
        raise SystemExit("hardware-descriptor source changed")
    if sha(boot[A - BASE:Z - BASE]) != BH:
        raise SystemExit("hardware-descriptor stock body changed")

    record = {
        "path": S.relative_to(R).as_posix(),
        "size": SS,
        "sha256": SH,
        "license": "MIT",
        "origin": "clean-room ring-descriptor selection and register publication",
        "evidence": "docs/research/g2-bootloader-hw-descriptor-publish-42c45a-source-closure.md",
    }
    pins = {"size": Z - A, "sha256": BH, "unrelocated_sha256": BH}
    entry = {
        "function": FN,
        "runtime_address": A,
        "source": record,
        "toolchain": {
            "target": "arm-none-eabi",
            "reviewed_version_prefix": "Apple clang version 21.0.0",
            "flags": FL,
        },
        "strict_relocation_contract": True,
        "expected": pins,
        "stock": {"size": Z - A, "sha256": BH},
        "relocations": [],
        "allow_discarded_alloc_sections": True,
        "toolchain_profiles": {
            "linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": pins,
                "stock": {"size": Z - A, "sha256": BH},
                "relocations": [],
            }
        },
    }
    overlay = json.loads(O.read_text())
    overlay["in_place_leaves"] = sorted(
        [item for item in overlay["in_place_leaves"] if item.get("function") != FN]
        + [entry],
        key=lambda item: int(item["runtime_address"]),
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
        raise SystemExit("hardware-descriptor census changed")
    row.update({
        "kind": "source_function",
        "name": "hw_descriptor_publish_42c45a",
        "disposition": "source_owned_production",
        "provider": "clean-room hardware descriptor publisher",
        "license_status": "MIT",
        "evidence": "exact dual-toolchain body with portable behavioral model",
    })
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output, fieldnames=fields, delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    C.write_text(output.getvalue())
    print("registered hardware descriptor publisher")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
