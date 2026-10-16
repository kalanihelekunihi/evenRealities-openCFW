#!/usr/bin/env python3
"""Bind the stock-verified source-owned LVGL image class descriptor."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-session-row-visibility-5897ee/apollo-main-terminal-session-row-visibility-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-lv-image-class-756108"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_image_class_756108.c"
ORACLE = OUT / "oracle-receipt.json"
OBJECT = OUT / "display-lv-image-class.o"
RESOLVED = {"audio_uart_image_class_756108"}
ADDED = {"audio_uart_lv_image_ctor_498bd0", "audio_uart_lv_image_dtor_498c6c",
         "audio_uart_lv_image_event_498c9c"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_CLASS_C_ORACLE" or \
            oracle["source_sha256"] != sha(SOURCE) or oracle["object_sha256"] != sha(OBJECT):
        raise RuntimeError("LVGL image class oracle changed")
    before = imports(BASE)
    if len(before) != 201 or not RESOLVED <= before:
        raise RuntimeError("LVGL image class frontier changed")
    linked = OUT / "apollo-main-lv-image-class-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(OBJECT),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before != ADDED or len(after) != 203:
        raise RuntimeError(f"LVGL image class frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_CLASS_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(OBJECT.relative_to(ROOT)), "object_sha256": sha(OBJECT),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 201, "unresolved_after": 203,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False,
              "hardware_proof": False,
              "limits": ["Three LVGL image-class callbacks and final placement remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(path))


if __name__ == "__main__":
    main()
