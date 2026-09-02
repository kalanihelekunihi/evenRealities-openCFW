#!/usr/bin/env python3
"""Register four G2 Cortex-M startup services and correct their extents."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_startup_services_432910.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-startup-services-432910-source-closure.md"
BOOT_BASE = 0x00410000
SOURCE_SHA = "c36332b66bfe3f4c2a0fbc064fe761896000fc674c45f63c08f7eadd5e0ebad6"
APPLE_COMPONENT_SHA = "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"
LINUX_COMPONENT_SHA = "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"
FUNCTIONS = (
    ("open_cfw_bootloader_vector_table_relocate_432910", 0x00432910, 0x0043291A,
     "bee8bcf07546d7e7b549b10cfe4fc3c6519a6a49dc357d32179df469f5a8e36c", ()),
    ("open_cfw_bootloader_stack_limits_init_43291a", 0x0043291A, 0x0043292A,
     "320ede47e52c2388957bf2ba938af992c2fb0cfa01e63bf1b6d6fea1f56b5980",
     ((0x0A, "open_cfw_bootloader_process_stack_provider_43293c", 0x0043293C),)),
    ("open_cfw_bootloader_process_stack_init_43293c", 0x0043293C, 0x00432954,
     "83b3b48d97503ec64f1922ffc3774a94e510616f7621abca62508fe9aa65d21a",
     ((0x10, "open_cfw_bootloader_fpu_provider_432958", 0x00432958),
      (0x14, "open_cfw_bootloader_runtime_start_43297c", 0x0043297C))),
    ("open_cfw_bootloader_fpu_enable_432958", 0x00432958, 0x0043297A,
     "0a4d65c423e1840131ae14f4b432a592b8928d1dffeb7624edd12b5e483dd00a", ()),
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
    if len(payload) != 3_395 or digest(payload) != SOURCE_SHA:
        raise SystemExit("startup-services source identity changed")
    return {"path": SOURCE.relative_to(ROOT).as_posix(), "size": len(payload),
            "sha256": digest(payload), "license": "MIT",
            "origin": "clean-room Cortex-M startup services", "evidence": EVIDENCE}


def source_row(template: dict[str, str], function: str, start: int, end: int,
               sha: str) -> dict[str, str]:
    row = dict(template)
    row.update({"kind": "source_function", "name": function.removeprefix("open_cfw_bootloader_"),
                "start": f"0x{start:08x}", "end": f"0x{end:08x}",
                "size": str(end - start), "sha256": sha,
                "disposition": "source_owned_production",
                "provider": "clean-room Cortex-M startup service",
                "license_status": "MIT",
                "evidence": "complete exact dual-toolchain and Apollo-main body with corrected boundary"})
    return row


def gap_row(template: dict[str, str], start: int, end: int, boot: bytes) -> dict[str, str]:
    row = dict(template)
    row.update({"kind": "mixed_gap", "name": f"post_mspi_gap_{start:08x}",
                "start": f"0x{start:08x}", "end": f"0x{end:08x}",
                "size": str(end - start),
                "sha256": digest(boot[start - BOOT_BASE:end - BOOT_BASE]),
                "disposition": "typed_nonentry_mixed_or_data",
                "provider": "authenticated startup literal/alignment",
                "license_status": "redistribution authority unresolved",
                "evidence": "external literal/alignment bytes; no function entry"})
    return row


def update_census(boot: bytes) -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ()); rows = list(reader)
    starts = [int(row["start"], 16) for row in rows]
    first = starts.index(0x00432910)
    expected = [(0x00432910, 0x0043291A), (0x0043291A, 0x0043293C),
                (0x0043293C, 0x00432946), (0x00432946, 0x00432958),
                (0x00432958, 0x0043297A)]
    observed = [(int(row["start"], 16), int(row["end"], 16))
                for row in rows[first:first + 5]]
    if observed != expected:
        raise SystemExit(f"startup census topology changed: {observed}")
    template = rows[first]
    replacements = [
        source_row(template, *FUNCTIONS[0][:3], FUNCTIONS[0][3]),
        source_row(template, *FUNCTIONS[1][:3], FUNCTIONS[1][3]),
        gap_row(template, 0x0043292A, 0x0043293C, boot),
        source_row(template, *FUNCTIONS[2][:3], FUNCTIONS[2][3]),
        gap_row(template, 0x00432954, 0x00432958, boot),
        source_row(template, *FUNCTIONS[3][:3], FUNCTIONS[3][3]),
    ]
    rows[first:first + 5] = replacements
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    CENSUS.write_text(output.getvalue(), encoding="utf-8")


def main() -> int:
    boot = BOOT.read_bytes(); source = source_record(); entries = []
    for function, start, end, sha, edges in FUNCTIONS:
        if digest(boot[start - BOOT_BASE:end - BOOT_BASE]) != sha:
            raise SystemExit(f"authenticated startup service changed at {start:#x}")
        relocations = [{"offset": offset, "type": "R_ARM_THM_CALL",
                        "symbol": symbol, "symbol_type": "STT_NOTYPE",
                        "target_address": target} for offset, symbol, target in edges]
        pins = {"size": end - start, "sha256": sha,
                "unrelocated_sha256": ({0x0043291A: "8766f0e90be5027c2318484e7caf3d1e90b6c0dd518b1b44e840c11cf6b17753",
                                         0x0043293C: "6edb7912c020837b919c7f14c6750aec722f8b2f0abbc92a2e719a652d819731"}.get(start, sha))}
        entries.append({"function": function, "runtime_address": start, "source": source,
                        "toolchain": {"target": "arm-none-eabi",
                                      "reviewed_version_prefix": "Apple clang version 21.0.0",
                                      "flags": FLAGS},
                        "strict_relocation_contract": True, "expected": pins,
                        "stock": {"size": end - start, "sha256": sha},
                        "relocations": relocations, "allow_discarded_alloc_sections": True,
                        "toolchain_profiles": {"linux-clang": {
                            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                            "expected": pins, "stock": {"size": end - start, "sha256": sha},
                            "relocations": relocations}}})
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8")); names = {item[0] for item in FUNCTIONS}
    retained = [item for item in overlay["in_place_leaves"] if item.get("function") not in names]
    overlay["in_place_leaves"] = sorted([*retained, *entries], key=lambda item: int(item["runtime_address"]))
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"]["component_sha256"] = LINUX_COMPONENT_SHA
    write_json(OVERLAY, overlay); update_census(boot)
    print("registered four complete Cortex-M startup services")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
