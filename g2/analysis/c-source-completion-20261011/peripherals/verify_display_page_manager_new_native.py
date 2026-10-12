#!/usr/bin/env python3
"""Connected native/C page-manager successful construction effects."""
from pathlib import Path
import re,subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_page_manager_new.c'
src=S.read_text()
decl=[]
for line in src.splitlines():
 if line.startswith('extern ') and '(' in line and 'audio_uart_display_fatal_handler' not in line:
  decl.append(line.removeprefix('extern ').split(';')[0])
stub='''#include <stdint.h>
void (*audio_uart_display_fatal_handler)(const char*,const char*,uint32_t);
const uint8_t audio_uart_display_page_style[4]={0};
uint32_t audio_uart_display_page_size_cell;
'''+''.join('__attribute__((naked)) '+d+'{__asm volatile("bx lr");}\n' for d in decl)
native={
 'file_heap_allocate':0x474cd2,'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,
 'compressed_log_output':0x43ce9e,'audio_ble_radio_ready_44b0ae':0x44b0ae,
 'audio_uart_display_default_get':0x44fa1a,
}
for name in re.findall(r'\b(audio_uart_page_[a-f0-9]{6})\b',src):
 native[name]=int(name[-6:],16)
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-Wno-c23-extensions','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_audio_new',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 results=[]
 for is_c in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  global_ptr=sym['audio_uart_display_page_manager'] if is_c else 0x20074858
  u.mem_write(global_ptr,bytes(4));u.mem_write(0x2007f000,bytes([0xa5]*0xec));u.mem_write(0x2007f100,bytes([0xaa]*0x400))
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x2007fd00)
  reverse={v:k for k,v in native.items()}
  reverse_c={sym[k]&~1:k for k in native if k in sym}
  seen=[]
  def hook(uc,a,size,_):
   name=(reverse_c if is_c else reverse).get(a)
   if not name:return
   seen.append(name)
   rv=0
   if name=='file_heap_allocate':rv=0x2007f000
   elif name=='audio_uart_display_default_get':rv=0x2007f900
   elif name=='audio_uart_page_488290':rv=0x2007fa00
   elif name=='audio_uart_page_487022':rv=0x2007fb00
   elif name=='audio_uart_page_44104c':rv=0x2007fc00
   elif name=='audio_uart_page_43de82':
    idx=seen.count(name)-1;rv=0x2007f100+idx*0x400
   uc.reg_write(UC_ARM_REG_R0,rv)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_uart_display_audio_new'] if is_c else 0x45f15a)|1,0x600000,count=1500)
  results.append((seen,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x2007f000,0xec)),bytes(u.mem_read(0x2007f110,4))))
 assert results[0]==results[1],[(i,a,b) for i,(a,b) in enumerate(zip(results[0][2],results[1][2])) if a!=b][:12] or (results[0][0],results[1][0])
 failure=[]
 for is_c in (False,True):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  global_ptr=sym['audio_uart_display_page_manager'] if is_c else 0x20074858
  fatal_ptr=sym['audio_uart_display_fatal_handler'] if is_c else 0x2007456c
  u.mem_write(global_ptr,bytes(4));u.mem_write(fatal_ptr,struct.pack('<I',0x2007fe01))
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x2007fd00)
  reverse={v:k for k,v in native.items()};reverse_c={sym[k]&~1:k for k in native if k in sym};seen=[]
  def hook(uc,a,size,_):
   if a==0x2007fe00:
    def cstr(p):return bytes(uc.mem_read(p,100)).split(b'\0')[0].decode('latin1')
    seen.append(('fatal',cstr(uc.reg_read(UC_ARM_REG_R0)),cstr(uc.reg_read(UC_ARM_REG_R1)),uc.reg_read(UC_ARM_REG_R2)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   name=(reverse_c if is_c else reverse).get(a)
   if name:
    seen.append((name,))
    uc.reg_write(UC_ARM_REG_R0,0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_uart_display_audio_new'] if is_c else 0x45f15a)|1,0x600000,count=300)
  failure.append((seen,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(global_ptr,4))))
 assert failure[0]==failure[1],failure
 print('PASS_DISPLAY_PAGE_MANAGER_NEW_NATIVE',len(results[0][0]),'success child calls and fatal callback failure')
