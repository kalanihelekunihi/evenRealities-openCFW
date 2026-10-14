#!/usr/bin/env python3
"""Compare native and C Nema boot uploads for both status-bit branches."""
from pathlib import Path
import hashlib, json, struct, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
OTA = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_nema_boot_upload.c'
blob = OTA.read_bytes()
ota_hash = hashlib.sha256(blob).hexdigest()
assert ota_hash == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
raw = blob[0x20:]
word = lambda address: struct.unpack_from('<I', raw, address-0x438000)[0]
assert word(0x513e70) == 0x200043a8
rom_words = struct.unpack_from('<6I', raw, 0x513ea8-0x438000)
assert rom_words == (0, 0, 0x08000002, 0x80000009, 0, 0)

# Decode the authenticated startup image to bind the native initial state.
record = 0x75d3f4
pointer = record + word(record)
end = pointer + (word(record+4) >> 1)
assert word(record+8) == 0x20000000
decoded = bytearray()
while pointer < end:
    token = raw[pointer-0x438000]
    pointer += 1
    literal_count, match = token & 3, token >> 4
    if not literal_count:
        literal_count = raw[pointer-0x438000] + 3
        pointer += 1
    if match == 15:
        match = raw[pointer-0x438000] + 15
        pointer += 1
    for _ in range(literal_count-1):
        decoded.append(raw[pointer-0x438000])
        pointer += 1
    if match:
        distance = raw[pointer-0x438000]
        pointer += 1
        high = (token >> 2) & 3
        if high == 3:
            high = raw[pointer-0x438000]
            pointer += 1
        distance += high << 8
        assert 0 < distance <= len(decoded)
        for _ in range(match+2):
            decoded.append(decoded[-distance])
assert pointer == end and len(decoded) == 0x4558
decoded_hash = hashlib.sha256(decoded).hexdigest()
assert decoded_hash == 'df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743'
initial = bytes(decoded[0x43a8:0x43b0])
assert initial == bytes.fromhex('0000000000800000')

with tempfile.TemporaryDirectory() as temporary:
    shim = Path(temporary) / 'children.c'
    shim.write_text('''#include <stdint.h>
__attribute__((noinline)) void audio_uart_nema_instruction_upload_522920(const uint32_t *p,uint32_t n,uint32_t a){(void)p;(void)n;(void)a;}
__attribute__((noinline)) uint32_t audio_uart_nema_child_522602(void){return 0;}
__attribute__((noinline)) void audio_uart_nema_rop_blend_mode_522956(uint32_t a){(void)a;}
''')
    elf_path = Path(temporary) / 'boot.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_uart_nema_child_5138a4',
                    str(SOURCE), str(shim), '-o', str(elf_path)], check=True)
    symbols = {parts[2]: int(parts[0], 16)
               for line in subprocess.check_output(['arm-none-eabi-nm', str(elf_path)], text=True).splitlines()
               if len(parts := line.split()) == 3}
    with elf_path.open('rb') as stream:
        elf = ELFFile(stream)
        segments = [(seg['p_vaddr'], seg.data()) for seg in elf.iter_segments()
                    if seg['p_type'] == 'PT_LOAD']
        state_sym = next(sym for sym in elf.get_section_by_name('.symtab').iter_symbols()
                         if sym.name == 'audio_uart_nema_boot_state_200043a8')
        assert state_sym['st_size'] == 8
        section = elf.get_section(state_sym['st_shndx'])
        assert section['sh_type'] == 'SHT_PROGBITS'
        offset = state_sym['st_value'] - section['sh_addr']
        assert section.data()[offset:offset+8] == initial

    def run(candidate, status):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        uc.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        uc.mem_map(0x20000000, 0x80000)
        if candidate:
            uc.mem_map(0x100000, 0x200000)
            for address, payload in segments:
                uc.mem_write(address, payload)
            cuts = {symbols['audio_uart_nema_instruction_upload_522920'] & ~1: 'upload',
                    symbols['audio_uart_nema_child_522602'] & ~1: 'status',
                    symbols['audio_uart_nema_rop_blend_mode_522956'] & ~1: 'mode'}
            state_address = symbols['audio_uart_nema_boot_state_200043a8']
            entry = symbols['audio_uart_nema_child_5138a4'] | 1
        else:
            uc.mem_map(0x438000, (len(raw)+4095) & ~4095)
            uc.mem_write(0x438000, raw)
            state_address = 0x200043a8
            uc.mem_write(state_address, initial)
            cuts = {0x522920: 'upload', 0x522602: 'status', 0x522956: 'mode'}
            entry = 0x5138a5
        uc.reg_write(A.UC_ARM_REG_SP, 0x2007f000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        trace = []
        def hook(cpu, pc, size, user):
            kind = cuts.get(pc)
            if kind is None:
                return
            if kind == 'upload':
                address = cpu.reg_read(A.UC_ARM_REG_R0)
                trace.append((kind, bytes(cpu.mem_read(address, 8)).hex(),
                              cpu.reg_read(A.UC_ARM_REG_R1),
                              cpu.reg_read(A.UC_ARM_REG_R2)))
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            elif kind == 'status':
                trace.append((kind,))
                cpu.reg_write(A.UC_ARM_REG_R0, status)
            else:
                trace.append((kind, cpu.reg_read(A.UC_ARM_REG_R0)))
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        uc.hook_add(UC_HOOK_CODE, hook)
        uc.emu_start(entry, 0x600000, count=3000)
        return trace, bytes(uc.mem_read(state_address, 8))

    cases = {}
    for label, status in [('clear', 0), ('set', 1 << 28)]:
        native, candidate = run(False, status), run(True, status)
        assert native == candidate, (label, native, candidate)
        expected_state = bytes.fromhex('0100000000000000') if status else initial
        assert native[1] == expected_state
        assert len(native[0]) == (10 if status else 9)
        cases[label] = {'trace': native[0], 'final_state': native[1].hex()}

result = {'status': 'PASS_NEMA_BOOT_UPLOAD_CONNECTED_BOUNDED',
          'ota_sha256': ota_hash, 'decoded_sha256': decoded_hash,
          'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'rom_words': [hex(value) for value in rom_words], 'cases': cases,
          'limits': 'Outer call traces and state writes match with child calls intercepted; child behavior, final placement, boot and hardware remain unproven.'}
(OUT / 'nema-boot-upload-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(result['status'], len(cases))
