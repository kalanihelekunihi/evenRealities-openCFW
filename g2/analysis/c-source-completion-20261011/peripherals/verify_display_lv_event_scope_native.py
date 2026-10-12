#!/usr/bin/env python3
"""Compare compiled nested-event scope C with stock Thumb RAM effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_event_scope.c'
assert struct.unpack_from('<I',B,0x4502b4-0x438000)[0]==0x2006f548
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_event_scope_begin_44ffd0','-Wl,--defsym=audio_uart_display_lv_root=0x2006f548',str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,native in [('audio_uart_lv_event_scope_begin_44ffd0',0x44ffd0),('audio_uart_lv_event_scope_end_44ffdc',0x44ffdc)]:
  for old in (0,0x2007f300,0x12345678):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segments:u.mem_write(a,d)
    event=0x2007f100;u.mem_write(event,b'\xa5'*28);u.mem_write(event+20,struct.pack('<I',old));u.mem_write(0x2006f548+0x6c,struct.pack('<I',old))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,event)
    u.emu_start((sym[name] if is_c else native)|1,0x600000,count=50)
    pair.append((u.mem_read(event,28),u.mem_read(0x2006f548+0x6c,4)))
   assert pair[0]==pair[1],(name,hex(old),pair)
   cases+=1
 print('PASS_DISPLAY_LV_EVENT_SCOPE_NATIVE',cases)
