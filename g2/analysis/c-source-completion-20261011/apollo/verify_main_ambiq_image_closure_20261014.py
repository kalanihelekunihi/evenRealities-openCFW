#!/usr/bin/env python3
"""Build the Ambiq image C dependency closure rooted at draw_image."""
import collections
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-ambiq-image-closure"
BASE = G2 / "build/c-firmware/20261014/main-ambiq-buffer-closure/apollo-main-ambiq-buffer-complete.o"
PINNED = G2 / "build/c-firmware/20261014/main-root-dependencies/ambiq-graph-current-receipt.json"
ENTRY = "g2/components/main/ambiq_buffer_handlers_candidate_20261014/image.c"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, option):
    text = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {row.split()[-1] for row in text.splitlines() if row.strip()}


def main():
    prior = json.loads(PINNED.read_text())
    if prior["status"] != "PASS_CURRENT_MAIN_AMBIQ_GRAPH_COMPILE":
        raise RuntimeError("pinned Ambiq source inventory changed")
    base_imports, base_defined = symbols(BASE, "-u"), symbols(BASE, "--defined-only")
    sources = {}
    providers = collections.defaultdict(list)
    for unit in prior["source_units"]:
        source, obj = ROOT / unit["source"], ROOT / unit["object"]
        if sha(source) != unit["source_sha256"] or sha(obj) != unit["object_sha256"]:
            raise RuntimeError(f"pinned Ambiq source/object drift: {source}")
        defined, imports = symbols(obj, "--defined-only"), symbols(obj, "-u")
        if defined & base_defined:
            continue
        sources[unit["source"]] = (defined, imports)
        for name in defined:
            providers[name].append(unit["source"])
    if ENTRY not in sources:
        raise RuntimeError("Ambiq image entry unavailable")
    pending, selected = {ENTRY}, set()
    while pending:
        name = pending.pop()
        if name in selected:
            continue
        selected.add(name)
        _, imported = sources[name]
        for symbol in imported - base_defined - base_imports:
            matches = providers.get(symbol, [])
            if len(matches) != 1:
                raise RuntimeError(f"unattributed image child: {symbol}: {matches}")
            pending.add(matches[0])
    if len(selected) != 36:
        raise RuntimeError(f"image source graph changed: {len(selected)} units")
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    for index, name in enumerate(sorted(selected)):
        obj = OUT / f"image-{index:02d}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(ROOT / name),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    linked = OUT / "apollo-main-ambiq-image.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    resolved = {"audio_uart_ambiq_draw_image_53f42a"}
    if (len(base_imports), len(after)) != (498, 497) or base_imports - after != resolved or after - base_imports:
        raise RuntimeError("Ambiq image C graph did not close")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_AMBIQ_IMAGE_C_COMPOSITION",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "pinned_inventory": str(PINNED.relative_to(ROOT)),
        "pinned_inventory_sha256": sha(PINNED),
        "root_source": ENTRY,
        "sources": {name: sha(ROOT / name) for name in sorted(selected)},
        "objects": {str(obj.relative_to(ROOT)): sha(obj) for obj in objects},
        "linked_object": str(linked.relative_to(ROOT)),
        "linked_object_sha256": sha(linked),
        "unresolved_before": len(base_imports), "unresolved_after": len(after),
        "imports_resolved": sorted(resolved), "imports_added": [],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Ambiq GPU/image effects are not hardware qualified.",
                   "Source-owned image state still needs final placement and runtime validation.",
                   "Other Main imports and final payload layout remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(base_imports), len(after), sha(path))


if __name__ == "__main__":
    main()
