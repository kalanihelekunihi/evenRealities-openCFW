#!/usr/bin/env python3
"""Bounded stock/C comparison for Apollo EvenAI common-data callback."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/even_ai_common_data_4e2976.c'
IMAGE = (G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
BODY = IMAGE[0x4e2976-0x438000:0x4e2a40-0x438000]
assert hashlib.sha256(BODY).hexdigest() == '59f87112573f4879d6667c0bdba51d512c662a68c52f78f7ab6109e5ba452673'
LOWER = {
    'audio_even_ai_prepare_4e1f7c': 0x4e1f7c,
    'audio_even_ai_frame_process_4e31cc': 0x4e31cc,
    'audio_even_ai_local_decode_498092': 0x498092,
    'audio_even_ai_ready_4e20f2': 0x4e20f2,
    'audio_log_flags': 0x43d0ce,
    'audio_log_extended': 0x43d574,
    'compressed_log_output': 0x43ce9e,
}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / 'shim.c'
    shim.write_text('#include <stdint.h>\n' + '\n'.join(
        f'__attribute__((naked)) uint32_t {name}(uint32_t a,uint32_t b,uint32_t c,uint32_t d)' \
        '{__asm volatile("bx lr");}' for name in LOWER))
    elf = Path(temp) / 'oracle.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                    '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_registry_callback_4e2976',
                    str(SOURCE), str(shim), '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        parsed = ELFFile(f)
        segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments()
                    if s['p_type'] == 'PT_LOAD']
        symbols = {s.name: s['st_value'] for s in
                   parsed.get_section_by_name('.symtab').iter_symbols()}

    def run(compiled, kind, failed, flags, length):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, data in segments:
            cpu.mem_write(address, data)
        cpu.mem_map(0x20000000, 0x10000)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        cpu.reg_write(A.UC_ARM_REG_R0, kind)
        cpu.reg_write(A.UC_ARM_REG_R1, 0x20000100)
        cpu.reg_write(A.UC_ARM_REG_R2, length)
        hooks = {((symbols[name] & ~1) if compiled else address): name
                 for name, address in LOWER.items()}
        trace = []

        def word(addr): return int.from_bytes(cpu.mem_read(addr, 4), 'little')

        def cstring(addr):
            result = bytearray()
            for index in range(180):
                byte = cpu.mem_read(addr + index, 1)[0]
                if byte == 0: break
                result.append(byte)
            return result.decode('ascii')

        def lower(uc, address, size, _):
            name = hooks.get(address)
            if name is None: return
            r0, r1, r2, r3 = (uc.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if name == 'audio_log_extended':
                sp = uc.reg_read(A.UC_ARM_REG_SP)
                trace.append((name, r0, cstring(r1), cstring(r2), cstring(r3),
                              word(sp), cstring(word(sp+4))))
            elif name == 'compressed_log_output':
                trace.append((name, r0, cstring(r1), cstring(r2)))
            elif name in ('audio_even_ai_frame_process_4e31cc',
                          'audio_even_ai_local_decode_498092'):
                trace.append((name, r0, r1))
            elif name == 'audio_even_ai_ready_4e20f2':
                trace.append((name, r0))
            else:
                trace.append((name,))
            result = flags if name == 'audio_log_flags' else failed if name in (
                'audio_even_ai_frame_process_4e31cc',
                'audio_even_ai_local_decode_498092') else 0
            uc.reg_write(A.UC_ARM_REG_R0, result)
            uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, lower)
        entry = symbols['audio_uart_registry_callback_4e2976'] if compiled else 0x4e2976
        cpu.emu_start(entry | 1, 0x600000, count=500)
        return trace, cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)

    cases = 0
    for kind in (0, 5, 7):
        for failed in (0, 1):
            for flags in (0, 1, 2, 4, 7):
                for length in (0, 0x12345, 0xffffffff):
                    stock = run(False, kind, failed, flags, length)
                    candidate = run(True, kind, failed, flags, length)
                    assert stock == candidate, (kind, failed, flags, length, stock, candidate)
                    cases += 1

OUT = G2 / 'build/c-firmware/20261016/main-even-ai-common-4e2976'
OUT.mkdir(parents=True, exist_ok=True)
receipt = {'status': 'PASS_NATIVE_MAIN_EVEN_AI_COMMON_4E2976', 'cases': cases,
           'source': str(SOURCE.relative_to(ROOT)),
           'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           'official_payload_sha256': hashlib.sha256(IMAGE).hexdigest(),
           'native_body_sha256': hashlib.sha256(BODY).hexdigest(),
           'lower_boundary': LOWER,
           'limits': ['Four EvenAI lower providers are controlled, not source-complete.',
                      'The tested call and return behavior does not establish final placement or device operation.']}
path = OUT / 'oracle-receipt.json'
path.write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, hashlib.sha256(path.read_bytes()).hexdigest())
