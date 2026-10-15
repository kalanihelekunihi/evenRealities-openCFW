#!/usr/bin/env python3
"""Bind Main NOR flash caller names to selected source-owned Apollo providers."""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/norflash-aliases-round1039'
out.mkdir(parents=True, exist_ok=True)
source = root / 'components/main/norflash_alias_candidates_20261014/aliases.c'
base = root / 'build/c-firmware/radio-rom-tail-round1038/apollo-main-radio-rom-tail.o'
obj = out / 'aliases.o'
linked = out / 'apollo-main-norflash-aliases.o'
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'

pairs = {
    'g2_norflash_lock_46f65e': 'audio_uart_ring_config_lock',
    'g2_norflash_unlock_46f674': 'audio_uart_ring_config_unlock',
    'g2_norflash_scheduler_delay_449376': 'audio_os_delay',
}
defined = {line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm', '--defined-only', str(base)], text=True).splitlines()}
assert set(pairs.values()) <= defined, sorted(set(pairs.values()) - defined)
subprocess.run([
    'clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
    '-fshort-enums', '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
    '-Wall', '-Wextra', '-Werror', '-c', str(source), '-o', str(obj)
], check=True)
bridge_defined = {line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm', '--defined-only', str(obj)], text=True).splitlines()}
bridge_imports = {line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm', '-u', str(obj)], text=True).splitlines()}
assert bridge_defined == set(pairs) and bridge_imports == set(pairs.values())
before = {line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm', '-u', str(base)], text=True).splitlines()}
assert set(pairs) <= before
subprocess.run(['arm-none-eabi-ld', '-r', str(base), str(obj), '-o', str(linked)], check=True)
after = {line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm', '-u', str(linked)], text=True).splitlines()}
assert before - after == set(pairs) and not after - before, (sorted(before - after), sorted(after - before))

receipt = {
    'round': 1039,
    'status': 'PASS_NORFLASH_SOURCE_ALIAS_BINDING',
    'component': 'Main NOR flash lock, unlock, scheduler delay caller aliases',
    'source': str(source.relative_to(root)),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'official_image_sha256': hashlib.sha256(blob).hexdigest(),
    'provider_pairs': pairs,
    'linked_object': str(linked.relative_to(root)),
    'linked_sha256': hashlib.sha256(linked.read_bytes()).hexdigest(),
    'unresolved_before': len(before),
    'unresolved_after': len(after),
    'whole_image_complete': False,
    'hardware_proof': False,
    'gates': ['Bridge binding does not establish exact target placement or full NOR flash behavior',
              'Live mutex, device, scheduler and hardware execution remain open'],
}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], len(before), len(after), receipt['linked_sha256'])
