#!/usr/bin/env python3
"""Stock/C random-ring copy and HCI refill effects on bounded lengths."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_sec_rand.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_stack_state_20072cb8[0x50];
volatile uint32_t calls;
void HciLeRandCmd(void){calls++;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,SecRand',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for length in (0,1,7,8,9,16,32):
  for bottom in (0,1,3):
   pair=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for addr,data in seg:u.mem_write(addr,data)
    state=sy['audio_ble_stack_state_20072cb8'] if compiled else 0x20072cb8
    dst=0x20080000
    u.mem_write(state,bytes((i*11)&255 for i in range(0x50)))
    u.mem_write(state+0x3a,bytes([bottom]));u.mem_write(dst,bytes([0xa5]*40))
    calls=[]
    if not compiled:
     def hook(uc,pc,n,user):
      calls.append(pc);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook,begin=0x52b304,end=0x52b304)
    u.reg_write(UC_ARM_REG_R0,dst);u.reg_write(UC_ARM_REG_R1,length)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy['SecRand'] if compiled else 0x53634e)|1,0x600000,count=5000)
    n=len(calls) if not compiled else int.from_bytes(u.mem_read(sy['calls'],4),'little')
    pair.append((bytes(u.mem_read(dst,40)),bytes(u.mem_read(state,0x50)),n))
   assert pair[0]==pair[1],(length,bottom,pair)
print('PASS_BLE_SEC_RAND_NATIVE 21')
