#!/usr/bin/env python3
"""Compose the Ambiq buffer handler and complete NEMA child chain for Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-ambiq-buffer-closure"
BASE = G2 / "build/c-firmware/20261014/main-transform-area-closure/apollo-main-transform-area.o"
PINNED = G2 / "build/c-firmware/20261014/main-root-dependencies"
SOURCES = (
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/handlers.c",
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/base.c",
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/blend.c",
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/render.c",
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/size.c",
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/draw.c",
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/coherency.c",
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/nema_float_translate.c",
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/nema_mask_rectangle.c",
    "g2/components/main/ambiq_gpu_mode_candidate_20261014/gpu_mode.c",
    "g2/components/main/ambiq_gpu_position_candidate_20261014/position.c",
    "g2/components/main/ambiq_gpu_position_candidate_20261014/nema_select.c",
    "g2/components/main/ambiq_gpu_blit_candidate_20261014/nema_mode.c",
    "g2/components/main/ambiq_gpu_blit_candidate_20261014/nema_cache.c",
)
ALIAS = ("display_driver_nema_clear_522ae0",
         "audio_uart_nema_mask_rectangle_522ae0")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    text = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return {row.split()[-1] for row in text.splitlines() if row.strip()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    graph_path = PINNED / "ambiq-graph-current-receipt.json"
    graph = json.loads(graph_path.read_text())
    if graph["status"] != "PASS_CURRENT_MAIN_AMBIQ_GRAPH_COMPILE":
        raise RuntimeError("pinned Ambiq graph changed")
    known = {row["source"]: row["source_sha256"] for row in graph["source_units"]}
    rectangle_path = PINNED / "pool-state-nema-clear-current-receipt.json"
    rectangle = json.loads(rectangle_path.read_text())
    if rectangle["source"] != SOURCES[8] or rectangle["source_sha256"] != sha(ROOT / SOURCES[8]):
        raise RuntimeError("NEMA rectangle/native alias source changed")
    objects = []
    source_hashes = {}
    for index, name in enumerate(SOURCES):
        source = ROOT / name
        source_hashes[name] = sha(source)
        if name in known and source_hashes[name] != known[name]:
            raise RuntimeError(f"Ambiq source drift: {name}")
        obj = OUT / f"buffer-{index:02d}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    linked = OUT / "apollo-main-ambiq-buffer-complete.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    f"--defsym={ALIAS[0]}={ALIAS[1]}", "-o", str(linked)],
                   check=True)
    before, after = imports(BASE), imports(linked)
    expected = {"audio_uart_ambiq_buffer_handlers_53d5da"}
    if (len(before), len(after)) != (499, 498) or before - after != expected or after - before:
        raise RuntimeError("Ambiq buffer graph did not close")
    symbols = subprocess.check_output(["arm-none-eabi-nm", "-g", str(linked)], text=True)
    aliases = {line.split()[-1]: line.split()[0] for line in symbols.splitlines()
               if len(line.split()) == 3 and line.split()[-1] in ALIAS}
    if aliases.get(ALIAS[0]) != aliases.get(ALIAS[1]):
        raise RuntimeError("NEMA rectangle alias differs from source body")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_AMBIQ_BUFFER_C_COMPOSITION",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "pinned_ambiq_receipt": str(graph_path.relative_to(ROOT)),
        "pinned_ambiq_receipt_sha256": sha(graph_path),
        "nema_rectangle_receipt": str(rectangle_path.relative_to(ROOT)),
        "nema_rectangle_receipt_sha256": sha(rectangle_path),
        "sources": source_hashes,
        "objects": {str(p.relative_to(ROOT)): sha(p) for p in objects},
        "nema_rectangle_alias": {ALIAS[0]: ALIAS[1]},
        "linked_object": str(linked.relative_to(ROOT)),
        "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(expected), "imports_added": [],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Native NEMA command behavior has bounded evidence only.",
                   "Final NEMA/display state placement and physical effects remain open.",
                   "Other Main imports and final payload layout remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
