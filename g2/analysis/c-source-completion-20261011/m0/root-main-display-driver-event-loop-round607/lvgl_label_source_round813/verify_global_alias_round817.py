#!/usr/bin/env python3
"""Verify the trial LVGL alias against the authenticated Apollo literal."""
from pathlib import Path
import hashlib
import re
import struct
import subprocess

repo = Path(__file__).resolve().parents[6]
image = repo / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
script = Path(__file__).with_name('lvgl_global_alias_round817.ld')
prior = repo / 'g2/build/c-firmware/root-main-lvgl-label-providers-round814/candidate.o'
out = prior.with_name('candidate-global-alias-round817.o')
data = image.read_bytes()
assert hashlib.sha256(data).hexdigest() == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
root = struct.unpack_from('<I', data, 32 + 0x47364c - 0x438000)[0]
assert root == 0x2006f548
subprocess.run(['arm-none-eabi-ld', '-r', '-T', str(script), str(prior), '-o', str(out)], check=True)
symbols = subprocess.check_output(['arm-none-eabi-nm', '-g', str(out)], text=True)
for name in ('audio_uart_display_lv_root', 'lv_global'):
    assert re.search(r'^2006f548 A ' + name + r'$', symbols, re.M), name
undefined = subprocess.check_output(['arm-none-eabi-nm', '-u', str(out)], text=True).splitlines()
assert len(undefined) == 605, len(undefined)
print('PASS_LVGL_GLOBAL_ALIAS_TRIAL', hex(root), len(undefined))
