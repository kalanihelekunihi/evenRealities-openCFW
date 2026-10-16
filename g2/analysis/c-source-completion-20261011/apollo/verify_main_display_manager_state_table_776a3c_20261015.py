#!/usr/bin/env python3
"""Compare Apollo display-manager callbacks and six-word interface table."""
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
SRC = G2 / 'components/audio/uart_thread_source_candidate/display_manager_state_table_776a3c.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-display-manager-state-table-776a3c'
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob = PAYLOAD.read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == PINNED
native_entries = (0x473e2e, 0x473ea0, 0x473f12, 0x473f84, 0x473ff6)
native_table = [int.from_bytes(blob[0x776a3c-0x438000+i*4:0x776a40-0x438000+i*4], 'little')
                for i in range(6)]
assert native_table == [1] + [a | 1 for a in native_entries]
assert blob[0x776a54-0x438000:0x776a5a-0x438000] == b'dmAdvA'
OUT.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as td:
    shim = Path(td) / 'shim.c'
    shim.write_text('''#include <stdint.h>
uint32_t audio_uart_display_manager_queue_cell;
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
int32_t audio_cmsis_queue_put(void*a,const void*b,uint8_t c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
    elf = Path(td) / 'test.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_display_manager_clear_473e2e',
                    str(SRC), str(shim), '-o', str(elf)], check=True)
    syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ['arm-none-eabi-nm', str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
    compiled_names = ('audio_display_manager_clear_473e2e',
                      'audio_display_manager_init_473ea0',
                      'audio_display_manager_power_up_473f12',
                      'audio_display_manager_power_down_473f84',
                      'audio_display_manager_brightness_473ff6')
    with elf.open('rb') as f:
        segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                    if s['p_type'] == 'PT_LOAD']
    def run(compiled, index, value, queue_status, log_mask):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for addr, data in segments: u.mem_write(addr, data)
        u.mem_map(0x20000000, 0x100000)
        queue_cell = syms['audio_uart_display_manager_queue_cell'] if compiled else 0x20000664
        u.mem_write(queue_cell, (0x20074000).to_bytes(4, 'little'))
        hooks = ({syms['audio_uart_buffer_zero'] & ~1: 'zero',
                  syms['audio_cmsis_queue_put'] & ~1: 'queue',
                  syms['audio_log_flags'] & ~1: 'flags',
                  syms['audio_log_extended'] & ~1: 'extended',
                  syms['compressed_log_output'] & ~1: 'compact'} if compiled else
                 {0x43c0e4: 'zero', 0x449abe: 'queue', 0x43d0ce: 'flags',
                  0x43d574: 'extended', 0x43ce9e: 'compact'})
        calls = []
        def string(cpu, addr):
            return bytes(cpu.mem_read(addr, 256)).split(b'\0')[0].decode('ascii')
        def word(cpu, addr): return int.from_bytes(cpu.mem_read(addr, 4), 'little')
        def hook(cpu, pc, size, user):
            kind = hooks.get(pc)
            if kind is None: return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            r1 = cpu.reg_read(A.UC_ARM_REG_R1)
            r2 = cpu.reg_read(A.UC_ARM_REG_R2)
            r3 = cpu.reg_read(A.UC_ARM_REG_R3)
            sp = cpu.reg_read(A.UC_ARM_REG_SP)
            if kind == 'zero':
                calls.append(('zero', r1, r2))
                cpu.mem_write(r0, b'\0' * r1)
            elif kind == 'queue':
                calls.append(('queue', r0, bytes(cpu.mem_read(r1, 36)).hex(), r2, r3))
                cpu.reg_write(A.UC_ARM_REG_R0, queue_status)
            elif kind == 'flags':
                cpu.reg_write(A.UC_ARM_REG_R0, log_mask)
            elif kind == 'extended':
                calls.append(('extended', r0, string(cpu, r1), string(cpu, r2),
                              string(cpu, r3), word(cpu, sp), string(cpu, word(cpu, sp+4))))
            else:
                calls.append(('compact', r0, string(cpu, r1), string(cpu, r2)))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        for reg, val in ((A.UC_ARM_REG_R0, value), (A.UC_ARM_REG_SP, 0x2007f000),
                         (A.UC_ARM_REG_LR, 0x600001)):
            u.reg_write(reg, val)
        address = syms[compiled_names[index]] if compiled else native_entries[index]
        u.emu_start(address | 1, 0x600000, count=20000)
        return calls
    cases = []
    for index in range(5):
        for value in (0, 0x12345678) if index == 4 else (0,):
            for queue_status in (0, 1):
                for log_mask in (0, 1, 2, 4, 7):
                    native = run(False, index, value, queue_status, log_mask)
                    source = run(True, index, value, queue_status, log_mask)
                    if native != source:
                        raise AssertionError((index, value, queue_status, log_mask,
                                              native, source))
                    cases.append({'callback': index, 'value': value,
                                  'queue_status': queue_status,
                                  'log_mask': log_mask, 'calls': len(native)})
    table = [int.from_bytes(next(data for addr, data in segments
                                 if addr <= syms['g2_display_state_table'] < addr+len(data))
                            [syms['g2_display_state_table']-next(addr for addr, data in segments
                              if addr <= syms['g2_display_state_table'] < addr+len(data))+i*4:]
                            [:4], 'little') for i in range(6)]
    assert table == [1] + [syms[n] | 1 for n in compiled_names], (table, [syms[n] for n in compiled_names])
    receipt = {'status': 'PASS_BOUNDED_MAIN_DISPLAY_MANAGER_TABLE_NATIVE_C',
               'cases': cases, 'native_table_words': [hex(x) for x in native_table],
               'source': str(SRC.relative_to(ROOT)),
               'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
               'payload_sha256': PINNED,
               'limits': ['Queue callback effects are compared through CMSIS call boundary; final placement and hardware are unproved.']}
    path = OUT / 'oracle.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(cases), hashlib.sha256(path.read_bytes()).hexdigest())
