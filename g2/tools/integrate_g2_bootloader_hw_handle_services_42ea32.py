#!/usr/bin/env python3
"""Register four G2 hardware-handle services."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_handle_services_42ea32.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-hw-handle-services-42ea32-source-closure.md"
BOOT_BASE = 0x00410000
SOURCE_SHA = "e4ca2c377c9fa4052ae2be95b13e1dc9acd362e9fd8ba18be05e596cc3d14649"
APPLE_COMPONENT_SHA = "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"
LINUX_COMPONENT_SHA = "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"
FUNCTIONS = (
    ("open_cfw_bootloader_hw_handle_reset_42ea32", 0x0042EA32, 0x0042EA68,
     "33eeb24b6b211f5d9920815c5ccc30b5c985bb5f094890a5e543b85e194c19b4"),
    ("open_cfw_bootloader_hw_handle_configure_42eb74", 0x0042EB74, 0x0042EBAA,
     "d227983f298102fc851a91454e4e48ffcaf57a43f050190e690a7cd6629f7fbb"),
    ("open_cfw_bootloader_hw_handle_enable_42ebaa", 0x0042EBAA, 0x0042EBE2,
     "052085424ed967f77d8f36303a119e299f4428fde2a6482b8a08f4686de151cd"),
    ("open_cfw_bootloader_hw_handle_disable_42ebe2", 0x0042EBE2, 0x0042EC0C,
     "ebd287ea1a933ce89fb082d850d121c22baa5a0a765804e468539386133187d0"),
)
FLAGS = ["-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
         "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
         "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
         "-fno-ident", "-mllvm", "-enable-machine-outliner=never"]


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
    by_start = {int(row["start"], 16): row for row in rows}
    for function, start, end, _sha in FUNCTIONS:
        row = by_start.get(start)
        if row is None or int(row["end"], 16) != end:
            raise SystemExit(f"hardware-handle census boundary changed at {start:#x}")
        row.update({"kind": "source_function",
                    "name": function.removeprefix("open_cfw_bootloader_"),
                    "disposition": "source_owned_production",
                    "provider": "clean-room hardware-handle service",
                    "license_status": "MIT",
                    "evidence": "exact dual-toolchain and Apollo-main body with portable register model"})
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    CENSUS.write_text(output.getvalue(), encoding="utf-8")


def main() -> int:
    source = SOURCE.read_bytes(); boot = BOOT.read_bytes()
    if len(source) != 4_839 or digest(source) != SOURCE_SHA:
        raise SystemExit("hardware-handle source identity changed")
    source_record = {"path": SOURCE.relative_to(ROOT).as_posix(), "size": len(source),
                     "sha256": SOURCE_SHA, "license": "MIT",
                     "origin": "clean-room hardware-handle services", "evidence": EVIDENCE}
    entries = []
    for function, start, end, sha in FUNCTIONS:
        if digest(boot[start - BOOT_BASE:end - BOOT_BASE]) != sha:
            raise SystemExit(f"authenticated hardware-handle body changed at {start:#x}")
        pins = {"size": end - start, "sha256": sha, "unrelocated_sha256": sha}
        entries.append({"function": function, "runtime_address": start,
                        "source": source_record,
                        "toolchain": {"target": "arm-none-eabi",
                                      "reviewed_version_prefix": "Apple clang version 21.0.0",
                                      "flags": FLAGS},
                        "strict_relocation_contract": True, "expected": pins,
                        "stock": {"size": end - start, "sha256": sha},
                        "relocations": [], "allow_discarded_alloc_sections": True,
                        "toolchain_profiles": {"linux-clang": {
                            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                            "expected": pins, "stock": {"size": end - start, "sha256": sha},
                            "relocations": []}}})
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8")); names = {x[0] for x in FUNCTIONS}
    retained = [item for item in overlay["in_place_leaves"]
                if item.get("function") not in names]
    overlay["in_place_leaves"] = sorted([*retained, *entries],
                                         key=lambda item: int(item["runtime_address"]))
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"]["component_sha256"] = LINUX_COMPONENT_SHA
    write_json(OVERLAY, overlay); update_census()
    print("registered four hardware-handle services")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
