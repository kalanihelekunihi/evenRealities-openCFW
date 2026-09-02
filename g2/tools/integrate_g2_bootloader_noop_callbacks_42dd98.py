#!/usr/bin/env python3
"""Register three exact G2 no-op callbacks."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_noop_callbacks_42dd98.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
EVIDENCE = "docs/research/g2-bootloader-noop-callbacks-42dd98-source-closure.md"
BOOT_BASE = 0x00410000
SOURCE_SHA = "6f05f0addaef7c09b1cf28b951ad696d1ae895485b9ca1239c5e7fe60dcddd65"
BODY_SHA = "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"
APPLE_COMPONENT_SHA = "13e2cee5351e5767d0cfc053025e7456a0771335086736a02e543f82adbb474b"
LINUX_COMPONENT_SHA = "11f12f80ce187fce53f37b2d27bf9326a8374e1b62a061394e39c511a21b1875"
FUNCTIONS = (
    ("open_cfw_bootloader_noop_callback_42dd98", 0x0042DD98),
    ("open_cfw_bootloader_noop_callback_42e276", 0x0042E276),
    ("open_cfw_bootloader_noop_callback_42e39a", 0x0042E39A),
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
    if len(payload) != 939 or digest(payload) != SOURCE_SHA:
        raise SystemExit("no-op callback source identity changed")
    return {"path": SOURCE.relative_to(ROOT).as_posix(), "size": len(payload),
            "sha256": digest(payload), "license": "MIT",
            "origin": "clean-room no-op callback", "evidence": EVIDENCE}


def update_census(boot: bytes) -> None:
    with CENSUS.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fields = list(reader.fieldnames or ()); rows = list(reader)
    pending = {address for _function, address in FUNCTIONS}
    for row in rows:
        start = int(row["start"], 16)
        if start not in pending:
            continue
        if int(row["end"], 16) != start + 2 or digest(boot[start - BOOT_BASE:start - BOOT_BASE + 2]) != BODY_SHA:
            raise SystemExit(f"no-op callback extent changed at {start:#x}")
        row.update({"kind": "source_function", "name": f"noop_callback_{start:08x}",
                    "size": "2", "sha256": BODY_SHA,
                    "disposition": "source_owned_production",
                    "provider": "clean-room no-op callback", "license_status": "MIT",
                    "evidence": "exact dual-toolchain bx-lr body and authenticated direct caller"})
        pending.remove(start)
    if pending:
        raise SystemExit(f"no-op callback census rows missing: {pending}")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    CENSUS.write_text(output.getvalue(), encoding="utf-8")


def main() -> int:
    boot = BOOT.read_bytes(); source = source_record(); entries = []
    for function, address in FUNCTIONS:
        if digest(boot[address - BOOT_BASE:address - BOOT_BASE + 2]) != BODY_SHA:
            raise SystemExit(f"authenticated no-op callback changed at {address:#x}")
        pins = {"size": 2, "sha256": BODY_SHA, "unrelocated_sha256": BODY_SHA}
        entries.append({"function": function, "runtime_address": address,
                        "source": source,
                        "toolchain": {"target": "arm-none-eabi",
                                      "reviewed_version_prefix": "Apple clang version 21.0.0",
                                      "flags": FLAGS},
                        "strict_relocation_contract": True, "expected": pins,
                        "stock": {"size": 2, "sha256": BODY_SHA}, "relocations": [],
                        "allow_discarded_alloc_sections": True,
                        "toolchain_profiles": {"linux-clang": {
                            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                            "expected": pins, "stock": {"size": 2, "sha256": BODY_SHA},
                            "relocations": []}}})
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    names = {item[0] for item in FUNCTIONS}
    retained = [item for item in overlay["in_place_leaves"] if item.get("function") not in names]
    overlay["in_place_leaves"] = sorted([*retained, *entries], key=lambda item: int(item["runtime_address"]))
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA
    overlay["toolchain_profiles"]["linux-clang"]["expected"]["component_sha256"] = LINUX_COMPONENT_SHA
    write_json(OVERLAY, overlay); update_census(boot)
    print("registered three exact no-op callbacks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
