#!/usr/bin/env python3
"""Compose corrected settings and font source into the current combined RAM archive."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
RAM = G2 / "build/c-firmware/20261016/main-registry-ring-connect-ram/receipt.json"
SETTINGS = G2 / "build/c-firmware/20261016/main-settings-ram-archive-refresh/receipt.json"
FONT = G2 / "build/c-firmware/20261016/main-font-active-archive-refresh/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-combined-ram-settings-font-archive"


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
        raise RuntimeError("symbol missing/duplicated: " + name)
    return int(rows[0][1], 16)


def main():
    ram, settings, font = [json.loads(p.read_text()) for p in (RAM, SETTINGS, FONT)]
    if ram["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_AND_RING_RAM_C_ARCHIVE" or \
            settings["status"] != "PASS_EXPERIMENTAL_MAIN_SETTINGS_RAM_ARCHIVE_REFRESH_C" or \
            font["status"] != "PASS_EXPERIMENTAL_MAIN_FONT_ACTIVE_ARCHIVE_REFRESH_C":
        raise RuntimeError("source archive evidence status changed")
    archive_base = ROOT / ram["combined_archive"]
    input_base = ROOT / ram["combined_linked_object"]
    main = ROOT / font["main_archive"]
    source_objects = [(ROOT / settings["object"], settings["object_sha256"]),
                      (ROOT / font["replacement_object"], font["replacement_object_sha256"]),
                      (ROOT / font["data_object"], font["data_object_sha256"])]
    for path, digest in [(archive_base, ram["combined_archive_sha256"]),
                         (input_base, ram["combined_linked_sha256"]),
                         (main, font["main_archive_sha256"]), *source_objects]:
        if sha(path) != digest:
            raise RuntimeError("source archive input changed: " + str(path))
    if size(input_base, "audio_settings_last_message_state") != 13:
        raise RuntimeError("old combined archive settings extent changed")
    members = subprocess.check_output(["arm-none-eabi-ar", "t", str(archive_base)],
                                      text=True).splitlines()
    for name in (settings["member"], font["replacement_member"]):
        if members.count(name) != 1:
            raise RuntimeError("source archive member missing/duplicated: " + name)
    OUT.mkdir(parents=True, exist_ok=True)
    archive = OUT / "libaudio-combined-ram-settings-font.a"
    shutil.copyfile(archive_base, archive)
    subprocess.run(["arm-none-eabi-ar", "rcsD", str(archive),
                    *(str(path) for path, _ in source_objects)], check=True)
    after_members = subprocess.check_output(["arm-none-eabi-ar", "t", str(archive)],
                                            text=True).splitlines()
    if after_members != members + [source_objects[-1][0].name]:
        raise RuntimeError("composed archive ordering changed")
    linked = OUT / "candidate-input-combined-ram-settings-font.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "--whole-archive", str(archive),
                    str(main), "--no-whole-archive", "-o", str(linked)], check=True)
    before, after = names(input_base, "-u"), names(linked, "-u")
    previous, current = names(input_base, "-g", "--defined-only"), \
                        names(linked, "-g", "--defined-only")
    new_state = {"audio_uart_font_primary_active", "audio_uart_font_secondary_active"}
    if before - after != {"audio_uart_ring_secondary_active"} or after - before or \
            current - previous != new_state or previous - current or \
            size(linked, "audio_settings_last_message_state") != 104 or \
            not {"audio_registry_ring_connect_buffer", "audio_terminal_ui_state_base"} <= current:
        raise RuntimeError("composed RAM/settings/font frontier changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_SETTINGS_FONT_ARCHIVE_C",
               "ram_receipt": str(RAM.relative_to(ROOT)), "ram_receipt_sha256": sha(RAM),
               "settings_receipt": str(SETTINGS.relative_to(ROOT)),
               "settings_receipt_sha256": sha(SETTINGS),
               "font_receipt": str(FONT.relative_to(ROOT)),
               "font_receipt_sha256": sha(FONT),
               "prior_archive": ram["combined_archive"],
               "prior_archive_sha256": sha(archive_base),
               "prior_object": ram["combined_linked_object"],
               "prior_object_sha256": sha(input_base),
               "main_archive": str(main.relative_to(ROOT)),
               "main_archive_sha256": sha(main),
               "source_objects": {str(path.relative_to(ROOT)): sha(path)
                                  for path, _ in source_objects},
               "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "archive_members": len(after_members),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": ["audio_uart_ring_secondary_active"],
               "imports_added": [], "providers_added": sorted(new_state),
               "settings_extent_bytes": 104,
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["The composed archive retains both RAM providers, corrects font data/function identity, and expands settings state to 104 bytes. All later Main stages still require replay.",
                          "Selected extents and partial link do not establish final startup, physical behavior or whole-image source completeness."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
