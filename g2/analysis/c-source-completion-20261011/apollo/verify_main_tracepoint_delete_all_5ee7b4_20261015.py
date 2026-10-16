#!/usr/bin/env python3
"""Compare tracepoint delete-all callback and 0x206-byte reply constructor."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/tracepoint_delete_all_5ee7b4.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-tracepoint-delete-all-5ee7b4'
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob = PAYLOAD.read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == PINNED
assert int.from_bytes(blob[0x5eeb60-0x438000:0x5eeb64-0x438000], 'little') == 0x2037bbc8
OUT.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as td:
    shim = Path(td) / 'shim.c'
    shim.write_text('''#include <stdint.h>
uint8_t audio_tracepoint_reply_buffer[0x206];
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_tracepoint_role_char_5edadc(void){return 82;}
int32_t audio_tracepoint_delete_all_files_5ee650(void){return 0;}
void audio_tracepoint_reply_result_5ee134(uint8_t*a){(void)a;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
    elf = Path(td) / 'test.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_tracepoint_delete_all_5ee7b4',
                    str(SOURCE), str(shim), '-o', str(elf)], check=True)
    syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ['arm-none-eabi-nm', str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
    with elf.open('rb') as f:
        segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                    if s['p_type'] == 'PT_LOAD']
    def run(compiled, magic, role, result, log_mask):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for addr, data in segments: u.mem_write(addr, data)
        u.mem_map(0x20000000, 0x400000)
        buffer = syms['audio_tracepoint_reply_buffer'] if compiled else 0x2037bbc8
        u.mem_write(buffer, b'\xaa'*0x206)
        hooks = ({syms['audio_uart_buffer_zero'] & ~1: 'zero',
                  syms['audio_tracepoint_role_char_5edadc'] & ~1: 'role',
                  syms['audio_tracepoint_delete_all_files_5ee650'] & ~1: 'delete',
                  syms['audio_tracepoint_reply_result_5ee134'] & ~1: 'reply',
                  syms['audio_log_flags'] & ~1: 'flags',
                  syms['audio_log_extended'] & ~1: 'extended',
                  syms['compressed_log_output'] & ~1: 'compact'} if compiled else
                 {0x43c0e4: 'zero', 0x5edadc: 'role', 0x5ee650: 'delete',
                  0x5ee134: 'reply', 0x43d0ce: 'flags', 0x43d574: 'extended',
                  0x43ce9e: 'compact'})
        calls = []
        def string(cpu, addr):
            return bytes(cpu.mem_read(addr, 256)).split(b'\0')[0].decode('ascii')
        def word(cpu, addr): return int.from_bytes(cpu.mem_read(addr, 4), 'little')
        def fmt_args(cpu, fmt, values):
            return tuple(values[:fmt.count('%')])
        def hook(cpu, pc, size, user):
            kind = hooks.get(pc)
            if kind is None: return
            r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            sp = cpu.reg_read(A.UC_ARM_REG_SP)
            if kind == 'zero':
                calls.append(('zero', r0 == buffer, r1, r2))
                cpu.mem_write(r0, b'\0'*r1)
            elif kind == 'role': cpu.reg_write(A.UC_ARM_REG_R0, role)
            elif kind == 'delete':
                calls.append(('delete',)); cpu.reg_write(A.UC_ARM_REG_R0, result & 0xffffffff)
            elif kind == 'reply':
                calls.append(('reply', r0 == buffer, bytes(cpu.mem_read(r0, 8)).hex()))
            elif kind == 'flags': cpu.reg_write(A.UC_ARM_REG_R0, log_mask)
            elif kind == 'extended':
                fmt = string(cpu, word(cpu, sp+4))
                calls.append(('extended', r0, string(cpu,r1), string(cpu,r2),
                              string(cpu,r3), word(cpu,sp), fmt,
                              fmt_args(cpu,fmt,[word(cpu,sp+8+4*i) for i in range(3)])))
            else:
                fmt = string(cpu,r1)
                calls.append(('compact',r0,fmt,string(cpu,r2),
                              fmt_args(cpu,fmt,[r3,word(cpu,sp)])))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        for reg,val in ((A.UC_ARM_REG_R0,magic),(A.UC_ARM_REG_SP,0x2007f000),
                        (A.UC_ARM_REG_LR,0x600001)):
            u.reg_write(reg,val)
        entry = syms['audio_tracepoint_delete_all_5ee7b4'] if compiled else 0x5ee7b4
        u.emu_start(entry | 1,0x600000,count=20000)
        return {'calls':calls,'buffer_sha256':hashlib.sha256(bytes(u.mem_read(buffer,0x206))).hexdigest()}
    cases=[]
    for magic in (0,0x47,255):
      for role in (ord('R'),ord('L')):
       for result in (-1,0,7):
        for log_mask in (0,1,2,4,7):
         native=run(False,magic,role,result,log_mask)
         source=run(True,magic,role,result,log_mask)
         if native!=source:
          raise AssertionError((magic,role,result,log_mask,native,source))
         cases.append({'magic':magic,'role':role,'result':result,
                       'log_mask':log_mask,'calls':len(native['calls'])})
    receipt={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_DELETE_ALL_NATIVE_C',
             'cases':cases,'source':str(SOURCE.relative_to(ROOT)),
             'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             'payload_sha256':PINNED,
             'limits':['File-delete and reply-send effects are compared at call boundaries; final placement and hardware are unproved.']}
    path=OUT/'oracle.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
