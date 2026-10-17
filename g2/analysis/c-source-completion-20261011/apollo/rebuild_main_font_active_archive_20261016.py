#!/usr/bin/env python3
"""Replace the colliding font loader in a copied Main input archive."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OLD = G2 / "build/c-firmware/20261014/main-input-archive-member-refresh"
AUDIO = OLD / "libaudio-input-corrected.a"
BASE = OLD / "candidate-input-corrected.o"
MAIN = G2 / "build/c-firmware/20261014/main-root-refresh/apollo_main/main/main-candidates.a"
MANIFEST = G2 / "build/c-firmware/20261014/main-root-source-refresh2/apollo_main/audio/compile-results.json"
LOADER = G2 / "components/audio/uart_thread_source_candidate/display_ring_static_init.c"
REPAIR = G2 / "build/c-firmware/20261016/main-font-active-collision-repair/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-font-active-archive-refresh"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *options):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", *options, str(path)], text=True).splitlines()}


def main():
    repair = json.loads(REPAIR.read_text())
    if repair["status"] != "PASS_EXPERIMENTAL_MAIN_FONT_ACTIVE_COLLISION_REPAIR_C" or \
            repair["loader_sha256"] != sha(LOADER):
        raise RuntimeError("font active collision repair changed")
    manifest = json.loads(MANIFEST.read_text())
    row = next(r for r in manifest["rows"] if r["source"] == str(LOADER.relative_to(ROOT)))
    member = Path(row["object_path"]).name
    members = subprocess.check_output(["arm-none-eabi-ar", "t", str(AUDIO)],
                                      text=True).splitlines()
    if members.count(member) != 1:
        raise RuntimeError("font loader archive member missing or duplicated")
    data = ROOT / next(path for path in repair["objects"]
                       if path.endswith("/font-active-data.o"))
    loader = ROOT / next(path for path in repair["objects"]
                         if path.endswith("/display-ring-static-init.o"))
    if sha(data) != repair["objects"][str(data.relative_to(ROOT))] or \
            sha(loader) != repair["objects"][str(loader.relative_to(ROOT))]:
        raise RuntimeError("focused repair object changed")
    OUT.mkdir(parents=True, exist_ok=True)
    replacement = OUT / member
    shutil.copyfile(loader, replacement)
    archive = OUT / "libaudio-input-font-active-corrected.a"
    shutil.copyfile(AUDIO, archive)
    subprocess.run(["arm-none-eabi-ar", "rcsD", str(archive), str(replacement),
                    str(data)], check=True)
    current_members = subprocess.check_output(["arm-none-eabi-ar", "t", str(archive)],
                                              text=True).splitlines()
    if current_members != members + [data.name]:
        raise RuntimeError("font archive member order changed unexpectedly")
    linked = OUT / "candidate-input-font-active-corrected.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "--whole-archive", str(archive),
                    str(MAIN), "--no-whole-archive", "-o", str(linked)], check=True)
    before, after = names(BASE, "-u"), names(linked, "-u")
    if before - after != {"audio_uart_ring_secondary_active"} or \
            after - before or len(after) != len(before) - 1:
        raise RuntimeError("unexpected font archive import delta")
    prior, current = names(BASE, "-g", "--defined-only"), \
                     names(linked, "-g", "--defined-only")
    state = {"audio_uart_font_primary_active", "audio_uart_font_secondary_active"}
    if current - prior != state or prior - current or \
            "audio_uart_ring_active" not in current:
        raise RuntimeError("unexpected font archive provider change")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_FONT_ACTIVE_ARCHIVE_REFRESH_C",
               "repair": str(REPAIR.relative_to(ROOT)), "repair_sha256": sha(REPAIR),
               "prior_archive": str(AUDIO.relative_to(ROOT)),
               "prior_archive_sha256": sha(AUDIO),
               "prior_object": str(BASE.relative_to(ROOT)),
               "prior_object_sha256": sha(BASE),
               "main_archive": str(MAIN.relative_to(ROOT)),
               "main_archive_sha256": sha(MAIN),
               "manifest": str(MANIFEST.relative_to(ROOT)),
               "manifest_sha256": sha(MANIFEST),
               "replacement_member": member,
               "replacement_object": str(replacement.relative_to(ROOT)),
               "replacement_object_sha256": sha(replacement),
               "data_object": str(data.relative_to(ROOT)),
               "data_object_sha256": sha(data),
               "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "archive_members": len(current_members),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": ["audio_uart_ring_secondary_active"],
               "imports_added": [], "providers_added": sorted(state),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Corrected loader and initialized state are linked in the copied early Main input archive. All later Main waves still need replay against this archive.",
                          "Selected seven-word extents do not prove complete native allocations, startup copy or physical behavior."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
