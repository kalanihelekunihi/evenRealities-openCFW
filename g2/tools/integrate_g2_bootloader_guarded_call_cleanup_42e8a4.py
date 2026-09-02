#!/usr/bin/env python3
"""Register the G2 guarded indirect-call cleanup service."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_guarded_call_cleanup_42e8a4.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-guarded-call-cleanup-42e8a4-source-closure.md"
BOOT_BASE = 0x00410000
FUNCTION = "open_cfw_bootloader_guarded_call_cleanup_42e8a4"
START = 0x0042E8A4
END = 0x0042E8C2
BODY_SHA = "c4d87e8f170f723eedb93c2fd52d09e6f176b9d41d75a0dba72b894fd9a42275"
SOURCE_SHA = "26c4cd2d2d2380931c4dc8f98ce3ef2177914f0cb92ec5f3a32e776ee433dc78"
APPLE_COMPONENT_SHA = "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"
LINUX_COMPONENT_SHA = "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"
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


def update_census() -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ()); rows = list(reader)
    matches = [row for row in rows if int(row["start"], 16) == START]
    if len(matches) != 1 or int(matches[0]["end"], 16) != END:
        raise SystemExit("guarded-call census boundary changed")
    matches[0].update({"kind": "source_function",
                       "name": "guarded_call_cleanup_42e8a4",
                       "disposition": "source_owned_production",
                       "provider": "clean-room guarded indirect-call cleanup service",
                       "license_status": "MIT",
                       "evidence": "exact dual-toolchain and Apollo-main body with portable ordered-cleanup model"})
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    CENSUS.write_text(output.getvalue(), encoding="utf-8")


def main() -> int:
    source = SOURCE.read_bytes(); boot = BOOT.read_bytes()
    if len(source) != 2_504 or digest(source) != SOURCE_SHA:
        raise SystemExit("guarded-call source identity changed")
    if digest(boot[START - BOOT_BASE:END - BOOT_BASE]) != BODY_SHA:
        raise SystemExit("authenticated guarded-call body changed")
    source_record = {"path": SOURCE.relative_to(ROOT).as_posix(),
                     "size": len(source), "sha256": SOURCE_SHA, "license": "MIT",
                     "origin": "clean-room guarded indirect-call cleanup service",
                     "evidence": EVIDENCE}
    pins = {"size": END - START, "sha256": BODY_SHA,
            "unrelocated_sha256": BODY_SHA}
    entry = {"function": FUNCTION, "runtime_address": START,
             "source": source_record,
             "toolchain": {"target": "arm-none-eabi",
                           "reviewed_version_prefix": "Apple clang version 21.0.0",
                           "flags": FLAGS},
             "strict_relocation_contract": True, "expected": pins,
             "stock": {"size": END - START, "sha256": BODY_SHA},
             "relocations": [], "allow_discarded_alloc_sections": True,
             "toolchain_profiles": {"linux-clang": {
                 "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                 "expected": pins, "stock": {"size": END - START, "sha256": BODY_SHA},
                 "relocations": []}}}
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    retained = [item for item in overlay["in_place_leaves"]
                if item.get("function") != FUNCTION]
    overlay["in_place_leaves"] = sorted([*retained, entry],
                                         key=lambda item: int(item["runtime_address"]))
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"]["component_sha256"] = LINUX_COMPONENT_SHA
    write_json(OVERLAY, overlay); update_census()
    print("registered guarded indirect-call cleanup service")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
