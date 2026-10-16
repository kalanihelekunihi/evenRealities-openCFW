#!/usr/bin/env python3
"""Bind stock-compared LVGL image opacity and radius accessors."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-lv-image-draw-498ec0/apollo-main-lv-image-draw-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-lv-image-style-accessors-498634"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_image_style_accessors_498634.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_uart_lv_image_style_opa_498634",
            "audio_uart_lv_image_style_radius_49865e"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_STYLE_ACCESSORS_C_ORACLE" or \
            oracle["cases"] != 90 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("LVGL image style accessors oracle changed")
    before = imports(BASE)
    if len(before) != 203 or not RESOLVED <= before:
        raise RuntimeError("LVGL image style accessors frontier changed")
    obj = OUT / "display-lv-image-style-accessors.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-lv-image-style-accessors-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before or len(after) != 201:
        raise RuntimeError(f"LVGL image style accessors frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_STYLE_ACCESSORS_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 203, "unresolved_after": 201,
              "imports_resolved": sorted(RESOLVED), "imports_added": [],
              "source_complete": False, "full_payload_linked": False,
              "hardware_proof": False,
              "limits": ["Image draw descriptor initialization and lower draw scheduler remain open; final placement open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(path))


if __name__ == "__main__":
    main()
