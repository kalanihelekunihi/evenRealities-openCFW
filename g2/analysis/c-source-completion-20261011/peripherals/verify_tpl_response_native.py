#!/usr/bin/env python3
"""Bounded actual compiled-C/native _tplReponse buffer and return effects.

Log level is zero; callback-null and nonzero-pipe paths are covered. Product
buffer placement, callback body, and enabled diagnostics remain separate.
"""
from pathlib import Path
import subprocess, tempfile, struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

R = Path(__file__).resolve().parents[3]
B = (R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S = R/'components/audio/uart_thread_source_candidate/display_tpl_response.c'
STUB = '''#include <stdint.h>
uint8_t audio_tpl_response_buffer[8];
uint8_t audio_tpl_service_table[20];
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t x,const char*a,const char*b,const char*c,uint32_t d,const char*e,...){(void)x;(void)a;(void)b;(void)c;(void)d;(void)e;}
uint32_t compressed_log_output(uint32_t x,const char*a,const char*b,...){(void)x;(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
    t=Path(td); (t/'stub.c').write_text(STUB); elf=t/'c.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-ffreestanding','-fno-builtin','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_tpl_response',str(S),
                    str(t/'stub.c'),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        e=ELFFile(f)
        seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
        sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
    def run(compiled,pipe,sync,service,code,old):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
        for a,d in seg:u.mem_write(a,d)
        buf=sy['audio_tpl_response_buffer'] if compiled else 0x20004204
        tab=sy['audio_tpl_service_table'] if compiled else 0x20071414
        u.mem_write(buf,bytes([0xa5,0xb7,0x63,0xa5,0xa5,0xa5,0x72,old]))
        u.mem_write(tab+16,bytes(4))
        if compiled:
            for name in ('audio_log_level','audio_log_extended','compressed_log_output'):
                a=sy[name]&~1
                def hook(uc,pc,n,user):
                    uc.reg_write(UC_ARM_REG_R0,0)
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
        else:
            for a in (0x43d0ce,0x43d574,0x43ce9e):
                def hook(uc,pc,n,user):
                    uc.reg_write(UC_ARM_REG_R0,0)
                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
        for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),
                       (pipe,sync,service,code)):u.reg_write(r,v)
        u.reg_write(UC_ARM_REG_SP,0x200ff000)
        u.reg_write(UC_ARM_REG_LR,0x600001)
        u.emu_start((sy['audio_tpl_response'] if compiled else 0x4b9012)|1,
                    0x600000,count=2000)
        return (bytes(u.mem_read(buf,8)),u.reg_read(UC_ARM_REG_R0),
                u.reg_read(UC_ARM_REG_R1))
    cases=0
    for pipe in (0,1,0x100,0xff):
        for code in (0,1,15,255):
            for old in (0,0xa5):
                args=(pipe,0x123400bd,0x567800a6,code,old)
                a,b=run(False,*args),run(True,*args)
                assert a==b,(args,a,b)
                cases+=1
    print('PASS_TPL_RESPONSE_NATIVE',cases)
