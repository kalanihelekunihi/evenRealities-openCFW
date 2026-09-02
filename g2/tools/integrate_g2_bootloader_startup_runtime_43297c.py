#!/usr/bin/env python3
"""Register the split G2 Cortex-M runtime startup tail."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_startup_runtime_43297c.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-startup-runtime-43297c-source-closure.md"
BOOT_BASE = 0x00410000
SOURCE_SHA = "ce14cbec8a9cf538be52f2c76cbd0255ae0c8ab94f179ebef9a1407c1ab3cea6"
APPLE_COMPONENT_SHA = "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"
LINUX_COMPONENT_SHA = "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"
FUNCTIONS = (
    ("open_cfw_bootloader_runtime_start_43297c", 0x0043297C, 0x0043299A,
     "0f697df14e7a3026cd502d19b3c2bbdd540389796647c301283e815b47a6be2d",
     "a709d60bc609aa531644c3db7d80fff60277a16d425ef1f830569cc8afeb86a7",
     ((0x00, "open_cfw_bootloader_vector_table_provider_432910", 0x00432910),
      (0x08, "open_cfw_bootloader_init_array_provider_43299c", 0x0043299C),
      (0x16, "open_cfw_bootloader_platform_init_provider_41b862", 0x0041B862),
      (0x1A, "open_cfw_bootloader_terminal_loop_provider_4329c4", 0x004329C4))),
    ("open_cfw_bootloader_init_array_run_43299c", 0x0043299C, 0x004329BC,
     "c18f6c848dedbb42dc53582eb239f9f59017656fafad4cc4c948827bb6c342bd",
     "c18f6c848dedbb42dc53582eb239f9f59017656fafad4cc4c948827bb6c342bd", ()),
    ("open_cfw_bootloader_terminal_loop_4329c4", 0x004329C4, 0x004329D2,
     "bea26157ebbe31038bcf52f8a3233885515b034fd35636d6349e9b21370f26a2",
     "e24a1349df6d186d6dbd5558a6e03f2e5bd58d8791f8a899b6be5e2ccbacf22f",
     ((0x08, "open_cfw_bootloader_terminal_service_provider_41b298", 0x0041B298),)),
)
FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-builtin", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall",
    "-Wextra", "-Werror", "-fno-ident", "-mllvm", "-enable-machine-outliner=never",
]


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def source_record() -> dict[str, Any]:
    payload = SOURCE.read_bytes()
    if len(payload) != 3_861 or digest(payload) != SOURCE_SHA:
        raise SystemExit("startup-runtime source identity changed")
    return {"path": SOURCE.relative_to(ROOT).as_posix(), "size": len(payload),
            "sha256": digest(payload), "license": "MIT",
            "origin": "clean-room Cortex-M runtime startup tail", "evidence": EVIDENCE}


def source_row(template: dict[str, str], function: str, start: int, end: int,
               sha: str) -> dict[str, str]:
    row = dict(template)
    row.update({"kind": "source_function",
                "name": function.removeprefix("open_cfw_bootloader_"),
                "start": f"0x{start:08x}", "end": f"0x{end:08x}",
                "size": str(end - start), "sha256": sha,
                "disposition": "source_owned_production",
                "provider": "clean-room Cortex-M runtime startup tail",
                "license_status": "MIT",
                "evidence": "complete exact dual-toolchain body and instruction-equivalent Apollo-main analogue"})
    return row


def gap_row(template: dict[str, str], start: int, end: int, boot: bytes,
            description: str) -> dict[str, str]:
    row = dict(template)
    row.update({"kind": "mixed_gap", "name": f"post_mspi_gap_{start:08x}",
                "start": f"0x{start:08x}", "end": f"0x{end:08x}",
                "size": str(end - start),
                "sha256": digest(boot[start - BOOT_BASE:end - BOOT_BASE]),
                "disposition": "typed_nonentry_mixed_or_data",
                "provider": description,
                "license_status": "redistribution authority unresolved",
                "evidence": "external alignment/literal bytes; no function entry"})
    return row


def update_census(boot: bytes) -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ()); rows = list(reader)
    starts = [int(row["start"], 16) for row in rows]
    first = starts.index(0x0043297C)
    expected = [(0x0043297C, 0x004329BC), (0x004329BC, 0x004329C4),
                (0x004329C4, 0x004329D2)]
    observed = [(int(row["start"], 16), int(row["end"], 16))
                for row in rows[first:first + 3]]
    if observed != expected:
        raise SystemExit(f"startup-runtime census topology changed: {observed}")
    template = rows[first]
    replacements = [
        source_row(template, *FUNCTIONS[0][:3], FUNCTIONS[0][3]),
        gap_row(template, 0x0043299A, 0x0043299C, boot, "runtime-start alignment"),
        source_row(template, *FUNCTIONS[1][:3], FUNCTIONS[1][3]),
        gap_row(template, 0x004329BC, 0x004329C4, boot, "constructor-table literals"),
        source_row(template, *FUNCTIONS[2][:3], FUNCTIONS[2][3]),
    ]
    rows[first:first + 3] = replacements
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    CENSUS.write_text(output.getvalue(), encoding="utf-8")


def main() -> int:
    boot = BOOT.read_bytes(); source = source_record(); entries = []
    for function, start, end, sha, unrelocated, edges in FUNCTIONS:
        if digest(boot[start - BOOT_BASE:end - BOOT_BASE]) != sha:
            raise SystemExit(f"authenticated startup-runtime body changed at {start:#x}")
        relocations = [{"offset": offset, "type": "R_ARM_THM_CALL",
                        "symbol": symbol, "symbol_type": "STT_NOTYPE",
                        "target_address": target} for offset, symbol, target in edges]
        pins = {"size": end - start, "sha256": sha,
                "unrelocated_sha256": unrelocated}
        entries.append({"function": function, "runtime_address": start,
                        "source": source,
                        "toolchain": {"target": "arm-none-eabi",
                                      "reviewed_version_prefix": "Apple clang version 21.0.0",
                                      "flags": FLAGS},
                        "strict_relocation_contract": True, "expected": pins,
                        "stock": {"size": end - start, "sha256": sha},
                        "relocations": relocations,
                        "allow_discarded_alloc_sections": True,
                        "toolchain_profiles": {"linux-clang": {
                            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                            "expected": pins, "stock": {"size": end - start, "sha256": sha},
                            "relocations": relocations}}})
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    names = {item[0] for item in FUNCTIONS}
    retained = [item for item in overlay["in_place_leaves"]
                if item.get("function") not in names]
    overlay["in_place_leaves"] = sorted([*retained, *entries],
                                         key=lambda item: int(item["runtime_address"]))
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"]["component_sha256"] = LINUX_COMPONENT_SHA
    write_json(OVERLAY, overlay); update_census(boot)
    print("registered three split Cortex-M runtime startup services")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
