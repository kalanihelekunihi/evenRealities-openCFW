#!/usr/bin/env python3
"""Native/C queue first/tail transitions and nested critical depth/PRIMASK."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_wsf_queue_critical.c'
stub='''#include <stdint.h>
volatile uint8_t audio_wsf_cs_depth;
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,WsfQueueEnq',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('enter','exit','enq'):
  for depth in (0,1,2):
   for nonempty in ((0,1) if mode=='enq' else (0,)):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     cell=sym['audio_wsf_cs_depth'] if is_c else 0x20075045
     u.mem_write(cell,bytes((depth,)));queue=0x2007f000;node=0x2007f100;old=0x2007f200
     if nonempty:u.mem_write(queue,struct.pack('<II',old,old))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,queue);u.reg_write(UC_ARM_REG_R1,node)
     entry=sym[{'enter':'WsfCsEnter','exit':'WsfCsExit','enq':'WsfQueueEnq'}[mode]] if is_c else {'enter':0x52b8a4,'exit':0x52b8b6,'enq':0x538c24}[mode]
     u.emu_start(entry|1,0x600000,count=300)
     pair.append((bytes(u.mem_read(cell,1)),bytes(u.mem_read(queue,8)),bytes(u.mem_read(node,4)),bytes(u.mem_read(old,4)),u.reg_read(UC_ARM_REG_PRIMASK)))
    assert pair[0]==pair[1],(mode,depth,nonempty,pair)
    cases+=1
 print('PASS_BLE_WSF_QUEUE_CRITICAL_NATIVE',cases)
