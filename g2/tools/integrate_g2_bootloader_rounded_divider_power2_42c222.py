#!/usr/bin/env python3
"""Register the G2 rounded-divider and power-of-two helpers."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_rounded_divider_power2_42c222.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-rounded-divider-power2-42c222-source-closure.md"
BOOT_BASE = 0x00410000
SOURCE_SHA = "be25364b30dff6d5acdd9695429b6280567a541a44856ef07935fd5d327ce4b8"
APPLE_COMPONENT_SHA = "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"
LINUX_COMPONENT_SHA = "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"
FUNCTIONS = (
    ("open_cfw_bootloader_rounded_divider_42c222", 0x0042C222, 0x0042C256,
     "84a7909276921edf87861325fa09f547e536659109a2de4eeb1fd171f7f57411",
     "rounded_divider_42c222", "clean-room rounded integer divider"),
    ("open_cfw_bootloader_is_power_of_two_42c256", 0x0042C256, 0x0042C26A,
     "c7c013df5ce01fcc66215af1337fed966a975393591a7bc7e17ebcf71bde8213",
     "is_power_of_two_42c256", "clean-room nonzero power-of-two predicate"),
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
    if len(payload) != 2_794 or digest(payload) != SOURCE_SHA:
        raise SystemExit("rounded-divider helper source identity changed")
    return {
        "path": SOURCE.relative_to(ROOT).as_posix(), "size": len(payload),
        "sha256": digest(payload), "license": "MIT",
        "origin": "clean-room rounded-divider and power-of-two helpers",
        "evidence": EVIDENCE,
    }


def update_census(boot: bytes) -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ()); rows = list(reader)
    pending = {start: (end, sha, name, origin)
               for _function, start, end, sha, name, origin in FUNCTIONS}
    for row in rows:
        start = int(row["start"], 16)
        if start not in pending:
            continue
        end, sha, name, origin = pending.pop(start)
        if int(row["end"], 16) != end or digest(boot[start - BOOT_BASE:end - BOOT_BASE]) != sha:
            raise SystemExit(f"rounded-divider helper extent changed at {start:#x}")
        row.update({
            "kind": "source_function", "name": name, "size": str(end - start),
            "sha256": sha, "disposition": "source_owned_production",
            "provider": origin, "license_status": "MIT",
            "evidence": "exact dual-toolchain and Apollo-main body with randomized host semantics",
        })
    if pending:
        raise SystemExit(f"rounded-divider census rows missing: {pending}")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    CENSUS.write_text(output.getvalue(), encoding="utf-8")


def main() -> int:
    boot = BOOT.read_bytes(); source = source_record(); entries = []
    for function, start, end, sha, _name, origin in FUNCTIONS:
        stock = boot[start - BOOT_BASE:end - BOOT_BASE]
        if len(stock) != end - start or digest(stock) != sha:
            raise SystemExit(f"authenticated helper changed at {start:#x}")
        pins = {"size": end - start, "sha256": sha, "unrelocated_sha256": sha}
        entries.append({
            "function": function, "runtime_address": start,
            "source": {**source, "origin": origin},
            "toolchain": {"target": "arm-none-eabi",
                          "reviewed_version_prefix": "Apple clang version 21.0.0",
                          "flags": FLAGS},
            "strict_relocation_contract": True, "expected": pins,
            "stock": {"size": end - start, "sha256": sha}, "relocations": [],
            "allow_discarded_alloc_sections": True,
            "toolchain_profiles": {"linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": pins, "stock": {"size": end - start, "sha256": sha},
                "relocations": [],
            }},
        })
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    names = {row[0] for row in FUNCTIONS}
    retained = [item for item in overlay["in_place_leaves"] if item.get("function") not in names]
    overlay["in_place_leaves"] = sorted([*retained, *entries], key=lambda item: int(item["runtime_address"]))
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"]["component_sha256"] = LINUX_COMPONENT_SHA
    write_json(OVERLAY, overlay); update_census(boot)
    print("registered rounded-divider and power-of-two helpers at 0x0042C222")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
