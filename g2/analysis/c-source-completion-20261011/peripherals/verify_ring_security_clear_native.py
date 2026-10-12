#!/usr/bin/env python3
"""Execute native AppMasterSecClearAddr and actual ARM C with controlled memset."""
from pathlib import Path
import subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

R = Path(__file__).resolve().parents[3]
B = (R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S = R/'components/audio/uart_thread_source_candidate/display_ble_master_security_clear.c'
STUB = '''#include <stdint.h>
volatile uint8_t audio_ble_master_security_address[7];
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t value){(void)p;(void)n;(void)value;}
'''
with tempfile.TemporaryDirectory() as td:
    t=Path(td); stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_master_security_clear_address',
                    str(S),str(stub),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        e=ELFFile(f)
        seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
        sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
    for seed in (bytes(range(7)),b'ABCDEFG',b'\xff'*7):
        results=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in seg:u.mem_write(a,d)
            address=sym['audio_ble_master_security_address'] if is_c else 0x200003d8
            u.mem_write(address,seed)
            target=sym['audio_uart_buffer_zero'] if is_c else 0x43c0e4
            def zero(uc,pc,size,user):
                ptr=uc.reg_read(UC_ARM_REG_R0);n=uc.reg_read(UC_ARM_REG_R1)
                value=uc.reg_read(UC_ARM_REG_R2)&255
                uc.mem_write(ptr,bytes([value])*n)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,zero,begin=target&~1,end=target&~1)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.emu_start((sym['audio_ble_master_security_clear_address'] if is_c else 0x4d8ff6)|1,
                        0x600000,count=1000)
            results.append(bytes(u.mem_read(address,7)))
        assert results[0]==results[1]==b'\0'*6+b'\xff',(seed,results)
print('PASS_RING_SECURITY_CLEAR_NATIVE 3')
