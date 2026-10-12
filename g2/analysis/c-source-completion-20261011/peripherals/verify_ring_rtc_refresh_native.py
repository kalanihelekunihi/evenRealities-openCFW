#!/usr/bin/env python3
"""Compare stock/C RTC refresh child call order and returned epoch value."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_rtc_refresh.c'
STUB='#include <stdint.h>\nuint32_t audio_rtc_read_calendar(uint8_t*p){(void)p;return 0;}\nuint32_t audio_time_epoch_seconds(const uint8_t*p){(void)p;return 0;}\n'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_rtc_refresh',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for seed in (0,0x55):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   trace=[]
   for kind,cs,stock in (('snapshot','audio_rtc_read_calendar',0x47ef10),('epoch','audio_time_epoch_seconds',0x44a108)):
    address=sym[cs] if compiled else stock
    def child(uc,pc,size,user,kind=kind):
     p=uc.reg_read(UC_ARM_REG_R0)
     if kind=='snapshot':uc.mem_write(p,bytes((i+seed)&255 for i in range(40)));uc.reg_write(UC_ARM_REG_R0,0)
     else:trace.append((kind,bytes(uc.mem_read(p,40))));uc.reg_write(UC_ARM_REG_R0,0x12340000+seed)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,child,begin=address&~1,end=address&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_uart_ring_rtc_refresh'] if compiled else 0x44a1ea)|1,0x600000,count=2000)
   pair.append((u.reg_read(UC_ARM_REG_R0),trace))
  assert pair[0]==pair[1],(seed,pair)
print('PASS_RING_RTC_REFRESH_NATIVE 2')
