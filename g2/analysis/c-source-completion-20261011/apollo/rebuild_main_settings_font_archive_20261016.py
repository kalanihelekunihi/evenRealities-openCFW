#!/usr/bin/env python3
"""Compose the settings extent fix and font symbol repair in one Main archive."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SETTINGS = G2 / "build/c-firmware/20261016/main-settings-ram-archive-refresh/receipt.json"
FONT = G2 / "build/c-firmware/20261016/main-font-active-archive-refresh/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-settings-font-archive-refresh"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *options):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", *options, str(path)], text=True).splitlines()}


def size(path, name):
    rows = [row.split() for row in subprocess.check_output(
        ["arm-none-eabi-nm", "-S", str(path)], text=True).splitlines()
            if row.endswith(" " + name)]
    if len(rows) != 1:
        raise RuntimeError("missing or duplicate " + name)
    return int(rows[0][1], 16)


def main():
    settings, font = json.loads(SETTINGS.read_text()), json.loads(FONT.read_text())
    if settings["status"] != "PASS_EXPERIMENTAL_MAIN_SETTINGS_RAM_ARCHIVE_REFRESH_C" or \
            font["status"] != "PASS_EXPERIMENTAL_MAIN_FONT_ACTIVE_ARCHIVE_REFRESH_C":
        raise RuntimeError("input evidence status changed")
    archive_base = ROOT / settings["archive"]
    input_base = ROOT / settings["linked_object"]
    loader = ROOT / font["replacement_object"]
    data = ROOT / font["data_object"]
    main = ROOT / settings["main_archive"] if "main_archive" in settings else \
           G2 / "build/c-firmware/20261014/main-root-refresh/apollo_main/main/main-candidates.a"
    for path, digest in ((archive_base, settings["archive_sha256"]),
                         (input_base, settings["linked_object_sha256"]),
                         (loader, font["replacement_object_sha256"]),
                         (data, font["data_object_sha256"]),
                         (main, font["main_archive_sha256"])):
        if sha(path) != digest:
            raise RuntimeError("input changed: " + str(path))
    if size(input_base, "audio_settings_last_message_state") != 104:
        raise RuntimeError("settings extent lost before composition")
    prior_members = subprocess.check_output(["arm-none-eabi-ar", "t", str(archive_base)],
                                            text=True).splitlines()
    if prior_members.count(font["replacement_member"]) != 1:
        raise RuntimeError("font loader member missing")
    OUT.mkdir(parents=True, exist_ok=True)
    archive = OUT / "libaudio-input-settings-font-corrected.a"
    shutil.copyfile(archive_base, archive)
    subprocess.run(["arm-none-eabi-ar", "rcsD", str(archive), str(loader), str(data)],
                   check=True)
    members = subprocess.check_output(["arm-none-eabi-ar", "t", str(archive)],
                                      text=True).splitlines()
    if members != prior_members + [data.name]:
        raise RuntimeError("combined archive member order changed")
    linked = OUT / "candidate-input-settings-font-corrected.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "--whole-archive", str(archive),
                    str(main), "--no-whole-archive", "-o", str(linked)], check=True)
    before, after = names(input_base, "-u"), names(linked, "-u")
    if before - after != {"audio_uart_ring_secondary_active"} or after - before:
        raise RuntimeError("combined archive import delta changed")
    prior, current = names(input_base, "-g", "--defined-only"), \
                     names(linked, "-g", "--defined-only")
    added = {"audio_uart_font_primary_active", "audio_uart_font_secondary_active"}
    if current - prior != added or prior - current or \
            size(linked, "audio_settings_last_message_state") != 104:
        raise RuntimeError("combined archive provider or settings extent changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SETTINGS_FONT_ARCHIVE_REFRESH_C",
               "settings_receipt": str(SETTINGS.relative_to(ROOT)),
               "settings_receipt_sha256": sha(SETTINGS),
               "font_receipt": str(FONT.relative_to(ROOT)),
               "font_receipt_sha256": sha(FONT),
               "prior_archive": settings["archive"],
               "prior_archive_sha256": sha(archive_base),
               "prior_object": settings["linked_object"],
               "prior_object_sha256": sha(input_base),
               "font_loader_object": font["replacement_object"],
               "font_loader_object_sha256": sha(loader),
               "font_data_object": font["data_object"],
               "font_data_object_sha256": sha(data),
               "main_archive": str(main.relative_to(ROOT)),
               "main_archive_sha256": sha(main),
               "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "archive_members": len(members),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": ["audio_uart_ring_secondary_active"],
               "imports_added": [], "providers_added": sorted(added),
               "settings_extent_bytes": 104,
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Both corrections coexist in the early Main input archive; later receipt-linked waves require replay.",
                          "Selected font RAM extents and settings state do not establish final startup or hardware behavior."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
