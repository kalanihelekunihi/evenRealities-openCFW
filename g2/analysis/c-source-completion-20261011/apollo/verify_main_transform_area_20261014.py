#!/usr/bin/env python3
"""Compose the source-owned Ambiq transform-area pair into current Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-transform-area-closure"
BASE = G2 / "build/c-firmware/20261014/main-ambiq-leaf-closure/apollo-main-ambiq-leaves.o"
PINNED = G2 / "build/c-firmware/20261014/main-root-dependencies/ambiq-graph-current-receipt.json"
SOURCES = (
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/transform_area.c",
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/transform_point.c",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    text = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return {row.split()[-1] for row in text.splitlines() if row.strip()}


def main():
    old = json.loads(PINNED.read_text())
    if old["status"] != "PASS_CURRENT_MAIN_AMBIQ_GRAPH_COMPILE":
        raise RuntimeError("Ambiq source receipt changed")
    rows = {row["source"]: row for row in old["source_units"]}
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    for name in SOURCES:
        source = ROOT / name
        if sha(source) != rows[name]["source_sha256"]:
            raise RuntimeError(f"source drift: {name}")
        obj = OUT / (source.stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    linked = OUT / "apollo-main-transform-area.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "-o", str(linked)], check=True)
    before, after = imports(BASE), imports(linked)
    expected = {"audio_uart_ambiq_transform_area_488cda"}
    if (len(before), len(after)) != (500, 499) or before - after != expected or after - before:
        raise RuntimeError("Ambiq transform-area closure changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_TRANSFORM_AREA_C_COMPOSITION",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "pinned_graph_receipt": str(PINNED.relative_to(ROOT)),
        "pinned_graph_receipt_sha256": sha(PINNED),
        "sources": {name: sha(ROOT / name) for name in SOURCES},
        "objects": {str(obj.relative_to(ROOT)): sha(obj) for obj in objects},
        "linked_object": str(linked.relative_to(ROOT)),
        "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(expected), "imports_added": [],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Native transform behavior and display hardware effects remain unqualified.",
                   "Other Main imports and final payload placement remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
