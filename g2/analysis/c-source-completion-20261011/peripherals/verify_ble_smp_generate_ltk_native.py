#!/usr/bin/env python3
"""Bounded actual compiled C versus native 0x5379f4 LTK effects."""
from pathlib import Path
import subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_generate_ltk.c'
STUB='''#include <stdint.h>
void SecRand(uint8_t*p,uint8_t n){for(uint32_t i=0;i<n;i++)p[i]=(uint8_t)(0x80u+i);}
void DmSmpCbackExec(void*p){(void)p;}
void *memset(void*p,int c,unsigned n){uint8_t*q=p;for(unsigned i=0;i<n;i++)q[i]=(uint8_t)c;return p;}
void *memcpy(void*p,const void*s,unsigned n){uint8_t*q=p;const uint8_t*r=s;for(unsigned i=0;i<n;i++)q[i]=r[i];return p;}
'''
with tempfile.TemporaryDirectory() as td:
    t=Path(td);(t/'stub.c').write_text(STUB); elf=t/'candidate.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                    '-Wl,-e,smpGenerateLtk',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        e=ELFFile(f); seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
        sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
    for length in (0,7,16):
      for auth in (0,4):
        pair=[]
        for compiled in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for addr,data in seg:u.mem_write(addr,data)
            ccb,scratch=0x20080000,0x20080100
            u.mem_write(ccb+0x30,scratch.to_bytes(4,'little'))
            u.mem_write(ccb+0x40,bytes([auth]))
            u.mem_write(scratch,bytes((i*7)&255 for i in range(0x80)))
            u.mem_write(scratch+0x20,bytes([length]))
            calls=[]
            if not compiled:
              def child(uc,pc,n,user):
                a,b,c=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
                if pc==0x53634e:
                    uc.mem_write(a,bytes((0x80+i)&255 for i in range(b)));calls.append(('rand',a,b))
                elif pc==0x43c0e4:
                    uc.mem_write(a,bytes([c&255])*b);calls.append(('zero',a,b))
                elif pc==0x439be4:
                    uc.mem_write(a,bytes(uc.mem_read(b,c)));calls.append(('copy',a,b,c))
                elif pc==0x4d24a8:calls.append(('callback',a))
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
              for addr in (0x53634e,0x43c0e4,0x439be4,0x4d24a8):u.hook_add(UC_HOOK_CODE,child,begin=addr,end=addr)
            u.reg_write(UC_ARM_REG_R0,ccb);u.reg_write(UC_ARM_REG_SP,0x200ff000)
            u.reg_write(UC_ARM_REG_LR,0x600001)
            u.emu_start((sy['smpGenerateLtk'] if compiled else 0x5379f4)|1,0x600000,count=5000)
            pair.append(bytes(u.mem_read(scratch,0x60)))
        assert pair[0]==pair[1],(length,auth)
print('PASS_BLE_SMP_GENERATE_LTK_NATIVE 6')
