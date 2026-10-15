#!/usr/bin/env python3
"""Native/C comparison for Apollo display registry and locale selection."""
from pathlib import Path
import hashlib,struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_context_locale.c'
stub='''#include <stdint.h>
int32_t audio_uart_font_path_compare(const char*a,const char*b){for(;;){uint32_t x=(uint8_t)*a,y=(uint8_t)*b;if(x==0||x!=y)return (int32_t)(x-y);a++;b++;}}
'''
with tempfile.TemporaryDirectory() as d:
 tmp=Path(d);leaf=tmp/'leaf.c';leaf.write_text(stub);elf=tmp/'fixture.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_context_set',
                 '-Wl,--defsym,audio_uart_display_context_list_cell=0x200746c8',
                 '-Wl,--defsym,audio_uart_display_context_active_cell=0x200746cc',
                 '-Wl,--defsym,audio_uart_display_locale_index=0x20000030',
                 str(src),str(leaf),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 entries=[('set','audio_uart_display_context_set',0x460090),
          ('locale','audio_uart_display_layer_init',0x471164),
          ('commit','audio_uart_display_context_commit',0x4600b4)]
 cases=[('set',ptr) for ptr in (0,0x20080000,0x7560e4)] + \
       [('locale',index) for index in range(10)] + \
       [('commit',ptr) for ptr in (0x78d6a4,0x471318,0x47131c,0x471320,0x471324,0x471328,0x78d6ac,0x78d6b4,0x20080010)]
 for kind,value in cases:
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for address,data in segments:u.mem_write(address,data)
   u.mem_write(0x200746c8,struct.pack('<II',0x7560e4,0x12345678))
   u.mem_write(0x20000030,struct.pack('<I',value if kind=='locale' else 0))
   u.mem_write(0x20080000,b'\0'*8)
   u.mem_write(0x20080010,b'xx\0')
   target=next((entry for entry in entries if entry[0]==kind))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,value)
   u.emu_start((syms[target[1]] if compiled else target[2])|1,0x600000,count=20000)
   result=u.reg_read(UC_ARM_REG_R0)
   if kind=='locale':result=bytes(u.mem_read(result,24)).split(b'\0')[0]
   pair.append((result,bytes(u.mem_read(0x200746c8,8))))
  assert pair[0]==pair[1],(kind,value,pair)
print('PASS_DISPLAY_CONTEXT_LOCALE_NATIVE',len(cases))
