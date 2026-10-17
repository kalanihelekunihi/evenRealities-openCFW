#!/usr/bin/env python3
"""Replace the two-slot locale member with the five-callback C table."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-locale-relocatable-archive/receipt.json"
EVIDENCE = G2 / "build/c-firmware/20261016/main-locale-five-callback-table/receipt.json"
CLASSIFY = G2 / "build/c-firmware/20261016/main-locale-classify-callbacks/receipt.json"
TABLE_SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ring_locale_dispatch_five_callbacks_200044c0.c"
CLASSIFY_SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ring_locale_classify_callbacks_4d4368.c"
OUT = G2 / "build/c-firmware/20261016/main-locale-five-archive"
ADDED = {"audio_uart_locale_ascii_alpha_4d436e",
         "audio_uart_locale_ascii_lowercase_4d4368",
         "audio_uart_locale_ascii_uppercase_4d436c"}
OLD_MEMBER = "display_ring_locale_dispatch_relocatable_200044c0.o"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", *args, str(path)], text=True).splitlines()}


def main():
    base, evidence, classify = [json.loads(path.read_text()) for path in
                                (BASE, EVIDENCE, CLASSIFY)]
    if base["status"] != "PASS_EXPERIMENTAL_MAIN_LOCALE_RELOCATABLE_ARCHIVE_C" or \
            evidence["status"] != "PASS_EXPERIMENTAL_MAIN_LOCALE_FIVE_CALLBACK_TABLE_C" or \
            classify["status"] != "PASS_EXPERIMENTAL_MAIN_LOCALE_CLASSIFY_CALLBACKS_C" or \
            evidence["classify_receipt_sha256"] != sha(CLASSIFY):
        raise RuntimeError("five-callback archive evidence changed")
    prior_archive = ROOT / base["archive"]
    prior_object = ROOT / base["linked_object"]
    main_archive = ROOT / base["main_archive"]
    if sha(prior_archive) != base["archive_sha256"] or \
            sha(prior_object) != base["linked_object_sha256"] or \
            sha(main_archive) != base["main_archive_sha256"]:
        raise RuntimeError("two-slot archive changed")
    members = subprocess.check_output(["arm-none-eabi-ar", "t", str(prior_archive)],
                                      text=True).splitlines()
    if members.count(OLD_MEMBER) != 1 or \
            "display_ring_locale_classify_callbacks_4d4368.o" in members:
        raise RuntimeError("locale archive member inventory changed")
    for source in (TABLE_SOURCE, CLASSIFY_SOURCE):
        if evidence["sources"][str(source.relative_to(ROOT))] != sha(source):
            raise RuntimeError("five-callback source changed")
    OUT.mkdir(parents=True, exist_ok=True)
    flags = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
             "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
             "-Wextra", "-Werror", "-c"]
    table_obj = OUT / OLD_MEMBER
    classify_obj = OUT / "display_ring_locale_classify_callbacks_4d4368.o"
    for source, obj in ((TABLE_SOURCE, table_obj), (CLASSIFY_SOURCE, classify_obj)):
        subprocess.run([*flags, str(source), "-o", str(obj)], check=True)
    archive = OUT / "libaudio-locale-five-callbacks.a"
    shutil.copyfile(prior_archive, archive)
    subprocess.run(["arm-none-eabi-ar", "rcsD", str(archive),
                    str(table_obj), str(classify_obj)], check=True)
    after_members = subprocess.check_output(["arm-none-eabi-ar", "t", str(archive)],
                                            text=True).splitlines()
    if after_members != members + [classify_obj.name]:
        raise RuntimeError("five-callback archive ordering changed")
    linked = OUT / "candidate-input-locale-five-callbacks.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "--whole-archive", str(archive),
                    str(main_archive), "--no-whole-archive", "-o", str(linked)], check=True)
    before, after = names(prior_object, "-u"), names(linked, "-u")
    before_d, after_d = names(prior_object, "-g", "--defined-only"), \
                        names(linked, "-g", "--defined-only")
    if before != after or after_d - before_d != ADDED or before_d - after_d:
        raise RuntimeError("five-callback archive frontier changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LOCALE_FIVE_ARCHIVE_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "evidence_receipt": str(EVIDENCE.relative_to(ROOT)),
               "evidence_receipt_sha256": sha(EVIDENCE),
               "classify_receipt": str(CLASSIFY.relative_to(ROOT)),
               "classify_receipt_sha256": sha(CLASSIFY),
               "prior_archive": base["archive"], "prior_archive_sha256": sha(prior_archive),
               "prior_object": base["linked_object"],
               "prior_object_sha256": sha(prior_object),
               "main_archive": base["main_archive"],
               "main_archive_sha256": sha(main_archive),
               "source_objects": {str(TABLE_SOURCE.relative_to(ROOT)): {
                   "source_sha256": sha(TABLE_SOURCE),
                   "object": str(table_obj.relative_to(ROOT)),
                   "object_sha256": sha(table_obj)},
                   str(CLASSIFY_SOURCE.relative_to(ROOT)): {
                   "source_sha256": sha(CLASSIFY_SOURCE),
                   "object": str(classify_obj.relative_to(ROOT)),
                   "object_sha256": sha(classify_obj)}},
               "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": [], "imports_added": [],
               "providers_added": sorted(ADDED),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["All five locale function slots are C-relocatable in the early archive; two data pointers, runtime mutation and later stage replay remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(after), sha(path))


if __name__ == "__main__":
    main()
