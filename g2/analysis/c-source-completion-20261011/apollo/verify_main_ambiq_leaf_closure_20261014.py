#!/usr/bin/env python3
"""Compose five source-owned Ambiq/NPMX leaf providers into current Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-ambiq-leaf-closure"
BASE = G2 / "build/c-firmware/20261014/main-freetype-source-closure/apollo-main-freetype-jump-c.o"
PINNED = G2 / "build/c-firmware/20261014/main-root-dependencies/ambiq-graph-current-receipt.json"
SOURCES = (
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/ambiq_state.c",
    "g2/components/main/npmx_watchdog_candidate_20261014/kick.c",
    "g2/components/main/lv_style_removed_candidate_20261014/style_removed.c",
    "g2/components/main/ambiq_clip_change_candidate_20261014/clip.c",
    "g2/components/main/ambiq_buffer_handlers_candidate_20261014/layer.c",
)
EXPECTED = {
    "audio_uart_ambiq_unit_cell", "audio_uart_ambiq_vector_current_path_200746c4",
    "audio_uart_ambiq_vector_path_data_20073cd4",
    "audio_uart_ambiq_vector_path_segments_20073cc0",
    "audio_ble_npmx_kick_watchdog_5118e8", "audio_uart_lv_style_removed_44ce2a",
    "audio_uart_ambiq_clip_change_4b077e", "audio_uart_ambiq_draw_layer_53f400",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    text = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return {row.split()[-1] for row in text.splitlines() if row.strip()}


def main():
    prior = json.loads(PINNED.read_text())
    if prior["status"] != "PASS_CURRENT_MAIN_AMBIQ_GRAPH_COMPILE":
        raise RuntimeError("pinned Ambiq graph receipt changed")
    rows = {row["source"]: row for row in prior["source_units"]}
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    before = imports(BASE)
    if not EXPECTED <= before:
        raise RuntimeError("expected Ambiq/NPMX imports changed")
    for name in SOURCES:
        row = rows[name]
        source = ROOT / name
        if sha(source) != row["source_sha256"]:
            raise RuntimeError(f"source drift: {source}")
        obj = OUT / (source.stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    linked = OUT / "apollo-main-ambiq-leaves.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if (len(before), len(after)) != (508, 500) or before - after != EXPECTED or after - before:
        raise RuntimeError(f"unexpected Ambiq leaf closure: {len(before)}->{len(after)}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_AMBIQ_LEAF_C_COMPOSITION",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "pinned_graph_receipt": str(PINNED.relative_to(ROOT)),
        "pinned_graph_receipt_sha256": sha(PINNED),
        "sources": {name: sha(ROOT / name) for name in SOURCES},
        "objects": {str(obj.relative_to(ROOT)): sha(obj) for obj in objects},
        "linked_object": str(linked.relative_to(ROOT)),
        "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": [],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Source-owned cells still need native RAM placement and lifecycle qualification.",
                   "NPMX, Ambiq and LVGL hardware effects remain unqualified.",
                   "Other Main imports and final payload placement remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
