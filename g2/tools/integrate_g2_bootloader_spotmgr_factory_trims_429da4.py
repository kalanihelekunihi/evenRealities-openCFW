#!/usr/bin/env python3
"""Register the reviewed G2 bootloader SPOT-manager factory-trim loader.

This metadata-only tool never signs, flashes, resets, or contacts hardware.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_factory_trims_429da4.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-spotmgr-factory-trims-429da4-source-closure.md"
BOOT_BASE = 0x00410000
FUNCTION = "open_cfw_bootloader_spotmgr_load_factory_trims_429da4"
START = 0x00429DA4
END = 0x00429DF6
STOCK_SHA = "a69ea6c52f959eba65684feebd9651d2068cdd0d91caf8eb45d74e52969c61a4"
SOURCE_SHA = "d20dde33ad27aefe7d14c36ffbbdb7dd038ae938d51dd80bfaa0dd214a1bbb6d"
APPLE_COMPONENT_SHA = "94afbc3d7e1aa8d0d21095de081523c2ed9e422287355128eb20d36bf27c88e2"
LINUX_COMPONENT_SHA = "426d77749f96307ae9a45173d20684570d5994d902cf1f1f5cb01f935c6ba7c6"
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
    if len(payload) != 2_490 or digest(payload) != SOURCE_SHA:
        raise SystemExit("factory-trim source identity changed")
    return {
        "path": SOURCE.relative_to(ROOT).as_posix(),
        "size": len(payload),
        "sha256": digest(payload),
        "license": "MIT",
        "origin": "openCFW clean-room indexed Apollo510 factory-trim loader",
        "evidence": EVIDENCE,
    }


def update_census(boot: bytes) -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ())
        rows = list(reader)
    found = False
    for row in rows:
        if int(row["start"], 16) != START:
            continue
        if int(row["end"], 16) != END:
            raise SystemExit("factory-trim census interval changed")
        row.update({
            "kind": "source_function",
            "name": "spotmgr_load_factory_trims_429da4",
            "size": str(END - START),
            "sha256": digest(boot[START - BOOT_BASE:END - BOOT_BASE]),
            "disposition": "source_owned_production",
            "provider": "openCFW clean-room indexed factory-trim loader",
            "license_status": "MIT",
            "evidence": (
                "reviewed production C with exact dual-toolchain bytes, an "
                "exact Apollo-main analogue, and a 50000-state host test"
            ),
        })
        found = True
    if not found:
        raise SystemExit("factory-trim census interval was not found")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t",
                            lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    CENSUS.write_text(output.getvalue(), encoding="utf-8")


def main() -> int:
    boot = BOOT.read_bytes()
    stock = boot[START - BOOT_BASE:END - BOOT_BASE]
    if len(stock) != END - START or digest(stock) != STOCK_SHA:
        raise SystemExit("authenticated factory-trim stock body changed")
    pins = {
        "size": END - START,
        "sha256": STOCK_SHA,
        "unrelocated_sha256": STOCK_SHA,
    }
    entry = {
        "function": FUNCTION,
        "runtime_address": START,
        "source": source_record(),
        "toolchain": {
            "target": "arm-none-eabi",
            "reviewed_version_prefix": "Apple clang version 21.0.0",
            "flags": FLAGS,
        },
        "strict_relocation_contract": True,
        "expected": pins,
        "stock": {"size": END - START, "sha256": STOCK_SHA},
        "relocations": [],
        "allow_discarded_alloc_sections": True,
        "toolchain_profiles": {
            "linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": pins,
                "stock": {"size": END - START, "sha256": STOCK_SHA},
                "relocations": [],
            }
        },
    }
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    retained = [item for item in overlay["in_place_leaves"]
                if item.get("function") != FUNCTION]
    overlay["in_place_leaves"] = sorted(
        [*retained, entry], key=lambda item: int(item["runtime_address"])
    )
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"][
        "component_sha256"
    ] = LINUX_COMPONENT_SHA
    write_json(OVERLAY, overlay)
    update_census(boot)
    print("registered SPOT-manager factory-trim loader at 0x00429DA4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
