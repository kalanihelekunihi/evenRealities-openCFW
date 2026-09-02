#!/usr/bin/env python3
"""Register the G2 hardware-handle command service."""

from __future__ import annotations
import csv, hashlib, io, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_handle_command_42eff4.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
FUNCTION = "open_cfw_bootloader_hw_handle_command_42eff4"
START, END, BOOT_BASE = 0x0042EFF4, 0x0042F014, 0x00410000
BODY_SHA = "ed0aedd4d0d69cedbcae932b154d2ed9f290d4c95bc0f3f06f8135539c19ec6f"
SOURCE_SHA = "660091c82acdcb71a8b384e0929c76e3229ad60b39957ceae3471941847cefa8"
FLAGS = ["-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
         "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
         "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
         "-fno-ident", "-mllvm", "-enable-machine-outliner=never"]

def sha(data: bytes) -> str: return hashlib.sha256(data).hexdigest()

def main() -> int:
    source, boot = SOURCE.read_bytes(), BOOT.read_bytes()
    if (len(source), sha(source)) != (1_199, SOURCE_SHA): raise SystemExit("command source changed")
    if sha(boot[START-BOOT_BASE:END-BOOT_BASE]) != BODY_SHA: raise SystemExit("command body changed")
    record = {"path": SOURCE.relative_to(ROOT).as_posix(), "size": len(source),
              "sha256": SOURCE_SHA, "license": "MIT",
              "origin": "clean-room hardware-handle command service",
              "evidence": "docs/research/g2-bootloader-hw-handle-command-42eff4-source-closure.md"}
    pins = {"size": 32, "sha256": BODY_SHA, "unrelocated_sha256": BODY_SHA}
    entry = {"function": FUNCTION, "runtime_address": START, "source": record,
             "toolchain": {"target": "arm-none-eabi",
                           "reviewed_version_prefix": "Apple clang version 21.0.0",
                           "flags": FLAGS}, "strict_relocation_contract": True,
             "expected": pins, "stock": {"size": 32, "sha256": BODY_SHA},
             "relocations": [], "allow_discarded_alloc_sections": True,
             "toolchain_profiles": {"linux-clang": {
                 "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                 "expected": pins, "stock": {"size": 32, "sha256": BODY_SHA},
                 "relocations": []}}}
    overlay = json.loads(OVERLAY.read_text()); overlay["in_place_leaves"] = sorted(
        [x for x in overlay["in_place_leaves"] if x.get("function") != FUNCTION] + [entry],
        key=lambda x: int(x["runtime_address"]))
    temp = OVERLAY.with_name(f".{OVERLAY.name}.tmp"); temp.write_text(json.dumps(overlay, indent=2)+"\n"); temp.replace(OVERLAY)
    with CENSUS.open(newline="") as stream:
        reader=csv.DictReader(stream, delimiter="\t"); fields=list(reader.fieldnames or ()); rows=list(reader)
    row=next((x for x in rows if int(x["start"],16)==START),None)
    if row is None or int(row["end"],16)!=END: raise SystemExit("command census boundary changed")
    row.update({"kind":"source_function","name":"hw_handle_command_42eff4",
                "disposition":"source_owned_production","provider":"clean-room hardware-handle command service",
                "license_status":"MIT","evidence":"exact dual-toolchain and Apollo-main body; portable command model"})
    out=io.StringIO(newline=""); writer=csv.DictWriter(out,fieldnames=fields,delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows);CENSUS.write_text(out.getvalue())
    print("registered hardware-handle command service"); return 0

if __name__ == "__main__": raise SystemExit(main())
