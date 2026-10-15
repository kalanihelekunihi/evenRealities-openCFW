#!/usr/bin/env python3
"""Compare Apollo 0x4b3bec to compiled C and bind its callback body."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/ble-subsystem-primary-round1040'
out.mkdir(parents=True, exist_ok=True)
source_dir = root / 'components/audio/uart_thread_source_candidate'
source = source_dir / 'display_ble_subsystem_primary_handler.c'
callers = [source_dir / 'display_ble_subsystem_children.c', source_dir / 'app_main_handler.c']
base = root / 'build/c-firmware/norflash-aliases-round1039/apollo-main-norflash-aliases.o'
obj = out / 'display_ble_subsystem_primary_handler.o'
linked = out / 'apollo-main-ble-subsystem-primary.o'
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native = blob[0x4b3bec - 0x438000:0x4b3c02 - 0x438000]
assert native.endswith(bytes.fromhex('7047')), native.hex()
flags = ['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
         '-fshort-enums', '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
         '-Wall', '-Wextra', '-Werror', '-c']
for src in [source, *callers]:
    dest = obj if src == source else out / (src.stem + '.o')
    subprocess.run([*flags, str(src), '-o', str(dest)], check=True)

with tempfile.TemporaryDirectory() as temp:
    elf_path = Path(temp) / 'test.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mthumb', '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_ble_subsystem_primary_handler_4b3bec',
                    str(source), '-o', str(elf_path)], check=True)
    symbols = {parts[2]: int(parts[0], 16) for line in subprocess.check_output(
        ['arm-none-eabi-nm', str(elf_path)], text=True).splitlines()
        if len(parts := line.split()) == 3}
    with elf_path.open('rb') as stream:
        segments = [(segment['p_vaddr'], segment.data()) for segment in ELFFile(stream).iter_segments()
                    if segment['p_type'] == 'PT_LOAD']
    cases = []
    for event_id in (0, 1, 0x7fff, 0xffff):
        for event_class in (0, 15, 16, 32, 255):
            outputs = []
            for compiled in (False, True):
                cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
                cpu.mem_map(0x400000, 0x400000)
                cpu.mem_write(0x438000, blob)
                cpu.mem_map(0x100000, 0x100000)
                for address, data in segments:
                    cpu.mem_write(address, data)
                cpu.mem_map(0x20000000, 0x200000)
                address = 0x20010000
                data = event_id.to_bytes(2, 'little') + bytes([event_class, 0x5a])
                cpu.mem_write(address, data)
                cpu.reg_write(A.UC_ARM_REG_R0, address)
                cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
                cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
                entry = symbols['audio_ble_subsystem_primary_handler_4b3bec'] if compiled else 0x4b3bec
                cpu.emu_start(entry | 1, 0x600000, count=100)
                outputs.append((cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(address, 4))))
            assert outputs[0] == outputs[1] == (event_class, data), (event_id, event_class, outputs)
            cases.append((event_id, event_class))

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines()}

name = 'audio_ble_subsystem_primary_handler_4b3bec'
before = imports(base)
assert name in before and not imports(obj)
subprocess.run(['arm-none-eabi-ld', '-r', str(base), str(obj), '-o', str(linked)], check=True)
after = imports(linked)
assert before - after == {name} and not after - before
receipt = {
    'round': 1040,
    'status': 'PASS_NATIVE_BLE_SUBSYSTEM_PRIMARY_CALLBACK',
    'component': 'Apollo BLE subsystem primary callback 0x4b3bec',
    'source': str(source.relative_to(root)),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'caller_sources': [{'path': str(s.relative_to(root)), 'sha256': hashlib.sha256(s.read_bytes()).hexdigest()} for s in callers],
    'official_image_sha256': hashlib.sha256(blob).hexdigest(),
    'native_body_sha256': hashlib.sha256(native).hexdigest(),
    'native_cases': len(cases),
    'linked_object': str(linked.relative_to(root)),
    'linked_sha256': hashlib.sha256(linked.read_bytes()).hexdigest(),
    'unresolved_before': len(before),
    'unresolved_after': len(after),
    'whole_image_complete': False,
    'hardware_proof': False,
    'gates': ['Valid aligned event buffers tested; invalid pointer behavior remains unqualified',
              'Callback slot ownership, image placement and full BLE operation remain open'],
}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], len(cases), len(before), len(after), receipt['linked_sha256'])
