#!/usr/bin/env python3
"""Replace Main locale consumer and add C-relocatable callback table providers."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-combined-ram-settings-font-archive/receipt.json"
EVIDENCE = G2 / "build/c-firmware/20261016/main-locale-relocatable-source/receipt.json"
MANIFEST = G2 / "build/c-firmware/20261014/main-root-source-refresh2/apollo_main/audio/compile-results.json"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ring_locale_dispatch.c"
OUT = G2 / "build/c-firmware/20261016/main-locale-relocatable-archive"
ADDED = {"audio_uart_ring_locale_dispatch_200044c0",
         "audio_uart_locale_ascii_space_4d4384",
         "audio_uart_locale_ascii_lower_4d4398"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", *args, str(path)], text=True).splitlines()}


def size(path, name):
    rows = [row.split() for row in subprocess.check_output(
        ["arm-none-eabi-nm", "-S", str(path)], text=True).splitlines()
            if row.endswith(" " + name)]
    if len(rows) != 1:
        raise RuntimeError("missing/duplicate locale or settings symbol: " + name)
    return int(rows[0][1], 16)


def main():
    base, evidence = json.loads(BASE.read_text()), json.loads(EVIDENCE.read_text())
    if base["status"] != "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_SETTINGS_FONT_ARCHIVE_C" or \
            evidence["status"] != "PASS_EXPERIMENTAL_MAIN_LOCALE_RELOCATABLE_TABLE_C" or \
            evidence["comparisons"] != 534:
        raise RuntimeError("locale archive input evidence changed")
    prior_archive = ROOT / base["archive"]
    prior_object = ROOT / base["linked_object"]
    main_archive = ROOT / base["main_archive"]
    if sha(prior_archive) != base["archive_sha256"] or \
            sha(prior_object) != base["linked_object_sha256"] or \
            sha(main_archive) != base["main_archive_sha256"]:
        raise RuntimeError("locale base archive changed")
    manifest = json.loads(MANIFEST.read_text())
    row = next(item for item in manifest["rows"]
               if item["source"] == str(SOURCE.relative_to(ROOT)))
    member = Path(row["object_path"]).name
    members = subprocess.check_output(["arm-none-eabi-ar", "t", str(prior_archive)],
                                      text=True).splitlines()
    if members.count(member) != 1:
        raise RuntimeError("locale consumer archive member missing")
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    flags = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
             "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
             "-Wextra", "-Werror", "-c"]
    sources = (SOURCE,
               G2 / "components/audio/uart_thread_source_candidate/display_ring_locale_dispatch_relocatable_200044c0.c",
               G2 / "components/audio/uart_thread_source_candidate/display_ring_locale_callbacks_4d4384.c")
    for source in sources:
        obj = OUT / (member if source == SOURCE else source.stem + ".o")
        subprocess.run([*flags, str(source), "-o", str(obj)], check=True)
        if evidence["sources"][str(source.relative_to(ROOT))] != sha(source):
            raise RuntimeError("locale source changed since wrapper oracle")
        objects.append(obj)
    archive = OUT / "libaudio-combined-ram-settings-font-locale.a"
    shutil.copyfile(prior_archive, archive)
    subprocess.run(["arm-none-eabi-ar", "rcsD", str(archive),
                    *(str(obj) for obj in objects)], check=True)
    after_members = subprocess.check_output(["arm-none-eabi-ar", "t", str(archive)],
                                            text=True).splitlines()
    if after_members != members + [objects[1].name, objects[2].name]:
        raise RuntimeError("locale archive ordering changed")
    linked = OUT / "candidate-input-combined-ram-settings-font-locale.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "--whole-archive", str(archive),
                    str(main_archive), "--no-whole-archive", "-o", str(linked)], check=True)
    before, after = names(prior_object, "-u"), names(linked, "-u")
    before_d, after_d = names(prior_object, "-g", "--defined-only"), \
                        names(linked, "-g", "--defined-only")
    if before - after != {"audio_uart_ring_locale_dispatch_200044c0"} or \
            after - before or after_d - before_d != ADDED or before_d - after_d or \
            size(linked, "audio_settings_last_message_state") != 104 or \
            size(linked, "audio_uart_ring_locale_dispatch_200044c0") != 44:
        raise RuntimeError("locale archive source frontier changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LOCALE_RELOCATABLE_ARCHIVE_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "evidence_receipt": str(EVIDENCE.relative_to(ROOT)),
               "evidence_receipt_sha256": sha(EVIDENCE),
               "manifest": str(MANIFEST.relative_to(ROOT)), "manifest_sha256": sha(MANIFEST),
               "prior_archive": base["archive"], "prior_archive_sha256": sha(prior_archive),
               "prior_object": base["linked_object"],
               "prior_object_sha256": sha(prior_object),
               "main_archive": base["main_archive"],
               "main_archive_sha256": sha(main_archive),
               "source_objects": {str(source.relative_to(ROOT)): {
                   "source_sha256": sha(source), "object": str(obj.relative_to(ROOT)),
                   "object_sha256": sha(obj)} for source, obj in zip(sources, objects)},
               "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": ["audio_uart_ring_locale_dispatch_200044c0"],
               "imports_added": [], "providers_added": sorted(ADDED),
               "settings_extent_bytes": 104,
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["The early Main archive carries source-linked locale callbacks and table plus prior RAM repairs; later stages still need replay.",
                          "Other stock pointers in the selected table and runtime mutation remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
