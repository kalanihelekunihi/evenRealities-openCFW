#!/usr/bin/env python3
"""Compare bounded CMSIS kernel-state paths in compiled ARM C and stock."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_kernel_state.c'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text('#include <stdint.h>\nvolatile uint32_t audio_uart_ring_kernel_initialized_20074384;\nuint32_t audio_scheduler_state(void){return 0;}\n');elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_kernel_state',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for state in (0,1,2):
  for flag in (0,1,2):
   pair=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    u.mem_write(sym['audio_uart_ring_kernel_initialized_20074384'] if compiled else 0x20074384,struct.pack('<I',flag))
    target=sym['audio_scheduler_state'] if compiled else 0x4558a4
    def scheduler(uc,pc,size,user):uc.reg_write(UC_ARM_REG_R0,state);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,scheduler,begin=target&~1,end=target&~1)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sym['audio_uart_ring_kernel_state'] if compiled else 0x44906c)|1,0x600000,count=200)
    pair.append(u.reg_read(UC_ARM_REG_R0))
   assert pair[0]==pair[1],(state,flag,pair)
print('PASS_RING_KERNEL_STATE_NATIVE 9')
