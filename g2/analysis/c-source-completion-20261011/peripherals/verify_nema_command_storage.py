#!/usr/bin/env python3
"""Verify Nema command BSS and initialized sentinel against startup records."""
from pathlib import Path
import hashlib, json, struct, subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
OTA = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_nema_command_state.c'
blob = OTA.read_bytes()
ota_hash = hashlib.sha256(blob).hexdigest()
assert ota_hash == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
raw = blob[0x20:]
word = lambda address: struct.unpack_from('<I', raw, address-0x438000)[0]

# Authenticated compressed startup initializer for RAM 0x20000000..0x20004557.
record = 0x75d3f4
encoded_start = record + word(record)
encoded_end = encoded_start + (word(record+4) >> 1)
assert word(record+8) == 0x20000000
data = bytearray()
pointer = encoded_start
while pointer < encoded_end:
    token = raw[pointer-0x438000]
    pointer += 1
    literals, match = token & 3, token >> 4
    if not literals:
        literals = raw[pointer-0x438000] + 3
        pointer += 1
    if match == 15:
        match = raw[pointer-0x438000] + 15
        pointer += 1
    for _ in range(literals-1):
        data.append(raw[pointer-0x438000])
        pointer += 1
    if match:
        distance = raw[pointer-0x438000]
        pointer += 1
        high = (token >> 2) & 3
        if high == 3:
            high = raw[pointer-0x438000]
            pointer += 1
        distance += high << 8
        assert 0 < distance <= len(data)
        for _ in range(match+2):
            data.append(data[-distance])
assert pointer == encoded_end and len(data) == 0x4558
decoded_hash = hashlib.sha256(data).hexdigest()
assert decoded_hash == 'df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743'
sentinel_address = 0x20002e08
assert struct.unpack_from('<I', data, sentinel_address-0x20000000)[0] == 0xffffffff

# Distinct zero callback owns the six-word command-state span.
zero_start, zero_length = word(0x75d3d0), word(0x75d3cc)
assert (zero_start, zero_length) == (0x20004558, 0x70af0)
displacement = struct.unpack('<i', struct.pack('<I', word(0x75d3c8)))[0]
assert 0x75d3c8 + displacement == 0x5fa01f
command_address, command_size, next_object = 0x20073bf0, 24, 0x20073c08
assert command_address + command_size == next_object
assert zero_start <= command_address and next_object <= zero_start + zero_length
uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
uc.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
uc.mem_map(0x438000, (len(raw)+4095) & ~4095)
uc.mem_write(0x438000, raw)
uc.mem_map(0x20000000, 0x80000)
uc.mem_write(zero_start-16, b'\xa5' * (zero_length+32))
uc.reg_write(A.UC_ARM_REG_R0, 0x75d3cc)
uc.reg_write(A.UC_ARM_REG_SP, 0x2007f000)
done = [False]
def hook(cpu, pc, size, user):
    if pc == 0x5fa04a and cpu.reg_read(A.UC_ARM_REG_R0) == 0x75d3d4:
        done[0] = True
        cpu.emu_stop()
uc.hook_add(UC_HOOK_CODE, hook)
uc.emu_start(0x5fa01f, 0, count=1200000)
assert done[0]
assert bytes(uc.mem_read(zero_start, zero_length)) == b'\0' * zero_length
assert bytes(uc.mem_read(zero_start-16, 16)) == b'\xa5' * 16
assert bytes(uc.mem_read(zero_start+zero_length, 16)) == b'\xa5' * 16

obj = OUT / 'nema-command-storage.o'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                '-std=c11', '-ffreestanding', '-O2', '-Wall', '-Wextra', '-Werror',
                '-c', str(SOURCE), '-o', str(obj)], check=True)
with obj.open('rb') as stream:
    elf = ELFFile(stream)
    symbols = {sym.name: sym for sym in elf.get_section_by_name('.symtab').iter_symbols()}
    command = symbols['audio_uart_nema_command_state_20073bf0']
    assert command['st_size'] == command_size
    assert elf.get_section(command['st_shndx'])['sh_type'] == 'SHT_NOBITS'
    sentinel = symbols['audio_uart_nema_last_submission']
    section = elf.get_section(sentinel['st_shndx'])
    assert sentinel['st_size'] == 4 and section['sh_type'] == 'SHT_PROGBITS'
    assert struct.unpack_from('<I', section.data(), sentinel['st_value'])[0] == 0xffffffff
result = {'status': 'PASS_NEMA_COMMAND_STORAGE_BOUNDED',
          'ota_sha256': ota_hash, 'decoded_sha256': decoded_hash,
          'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'object_sha256': hashlib.sha256(obj.read_bytes()).hexdigest(),
          'command_address': hex(command_address), 'command_size': command_size,
          'next_identified_object': hex(next_object),
          'sentinel_address': hex(sentinel_address), 'sentinel_initial_value': '0xffffffff',
          'limits': 'Initial storage classes and values verified; absolute linker placement, later mutations, boot and hardware remain unproven.'}
(OUT / 'nema-command-storage-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(result['status'], command_size, hex(sentinel_address))
