#!/usr/bin/env python3
"""Bind stock-compared LVGL image constructor and destroyer."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-lv-image-class-756108/apollo-main-lv-image-class-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-lv-image-lifecycle-498bd0"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_image_lifecycle_498bd0.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_uart_lv_image_ctor_498bd0", "audio_uart_lv_image_dtor_498c6c"}
ADDED = set()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_LIFECYCLE_C_ORACLE" or \
            oracle["cases"] != 84 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("LVGL image lifecycle oracle changed")
    before = imports(BASE)
    if len(before) != 203 or not RESOLVED <= before:
        raise RuntimeError("LVGL image lifecycle frontier changed")
    obj = OUT / "display-lv-image-lifecycle.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-lv-image-lifecycle-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before != ADDED or len(after) != 201:
        raise RuntimeError(f"LVGL image lifecycle frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_LIFECYCLE_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 203, "unresolved_after": 201,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False,
              "hardware_proof": False,
              "limits": ["Image event callback and final placement remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(path))


if __name__ == "__main__":
    main()
