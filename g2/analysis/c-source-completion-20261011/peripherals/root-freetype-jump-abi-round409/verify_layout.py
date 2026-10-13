#!/usr/bin/env python3
"""Bind the native FreeType jump-buffer layout to pinned source evidence."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
NATIVE = Path("/tmp/opencfw-main-native.bin")
SMOOTH = ROOT / "g2/analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/objects/smooth.o"
OVERLAY = ROOT / "g2/analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include/setjmp.h"
NEWLIB = ROOT / "g2/analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/newlib-source/machine/arm/setjmp.S"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert sha(NATIVE) == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
native_text = subprocess.check_output([
    "arm-none-eabi-objdump", "-D", "-b", "binary", "-m", "arm", "-M", "force-thumb",
    "--adjust-vma=0x438000", "--start-address=0x56777c", "--stop-address=0x5677a8",
    str(NATIVE)], text=True)
worker_text = subprocess.check_output([
    "arm-none-eabi-objdump", "-D", "-b", "binary", "-m", "arm", "-M", "force-thumb",
    "--adjust-vma=0x438000", "--start-address=0x5e1594", "--stop-address=0x5e15a0",
    str(NATIVE)], text=True)
validator_text = subprocess.check_output([
    "arm-none-eabi-objdump", "-D", "-b", "binary", "-m", "arm", "-M", "force-thumb",
    "--adjust-vma=0x438000", "--start-address=0x524f70", "--stop-address=0x524f84",
    str(NATIVE)], text=True)
smooth_text = subprocess.check_output(["arm-none-eabi-objdump", "-d", str(SMOOTH)], text=True)
assert re.search(r"56777c:.*mov\s+ip, sp", native_text)
assert re.search(r"56777e:.*stmia\.w.*r4.*fp", native_text)
assert re.search(r"567782:.*stmia\.w.*ip, lr", native_text)
assert re.search(r"567786:.*vstmia.*d8-d15", native_text)
assert re.search(r"5e1598:.*ldr\.w.*\[r4, #128\]", worker_text)
assert re.search(r"524f70:.*str\.w.*\[r0, #128\]", validator_text)
assert re.search(r"524f74:.*str\.w.*\[r0, #132\]", validator_text)
assert re.search(r"524f7e:.*str\.w.*\[r0, #140\]", validator_text)
assert re.search(r"<gray_convert_glyph>:[\s\S]*?ldr\.w.*\[r0, #144\]", smooth_text)
assert re.search(r"<gray_convert_glyph>:[\s\S]*?ldr\.w.*\[r0, #148\]", smooth_text)
assert "typedef unsigned long jmp_buf[32];" in OVERLAY.read_text()
probe = json.loads((HERE / "probe-receipt.json").read_text())
assert probe["status"] == "PASS_NATIVE_NEWLIB_ARM_JUMP_REGISTER_AND_BUFFER_COMPARISON"
receipt = {
    "status": "PASS_NATIVE_128_BYTE_LAYOUT_AND_JUMP_BEHAVIOR_ANALYSIS_ONLY",
    "native_oracle_sha256": sha(NATIVE),
    "native_setjmp_entry": "0x56777c",
    "native_longjmp_entry": "0x567790",
    "native_save_footprint_bytes": 104,
    "native_gray_worker_first_field_offset": 128,
    "native_validator_fields_after_buffer": [128, 132, 136, 140],
    "analysis_overlay_sha256": sha(OVERLAY),
    "analysis_overlay_jmp_buf_bytes": 128,
    "compiled_smooth_object_sha256": sha(SMOOTH),
    "compiled_gray_convert_field_offsets": [144, 148],
    "newlib_assembly_sha256": sha(NEWLIB),
    "newlib_default_header_bytes": 160,
    "sampled_jump_comparisons": probe["comparisons"],
    "probe_receipt_sha256": sha(HERE / "probe-receipt.json"),
    "limits": ["Native 128-byte FreeType layout rejects unmodified Newlib 160-byte header for module compilation",
               "Assembly register behavior compared in QEMU; production runtime and other call sites unverified",
               "Class source side link is analysis only; initialized image and hardware gates remain open"],
}
(HERE / "layout-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"status": receipt["status"], "jump_comparisons": probe["comparisons"]}))
