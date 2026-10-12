#!/usr/bin/env python3
"""Connected source descriptor/encoder versus original nanopb bytes on simple ring messages."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
S=[p for p in sorted(D.glob('display_pb*.c')) if p.name!='display_pb_ostream_buffer.c']+[D/'display_ble_ring_pb_descriptor.c']
SHIM='''#include <stdint.h>
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){uint8_t *b=p;for(uint32_t i=0;i<n;i++)b[i]=(uint8_t)v;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_encode',*[str(x) for x in S],str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0,0,0),(1,0,0),(0,1,0),(1,1,0),(127,300,0)] + [(0,0,t) for t in list(range(3,15))+[128,129]]
 total=0
 for a,b,oneof in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for addr,data in seg:u.mem_write(addr,data)
   stream=0x20080000;msg=0x20081000;cb=0x20084000;u.mem_write(stream,struct.pack('<IIIII',cb+1,0,1000,0,0));u.mem_write(msg,bytes(4096));u.mem_write(msg,struct.pack('<B',a));u.mem_write(msg+2,struct.pack('<H',b));u.mem_write(msg+4,struct.pack('<I',oneof));output=[]
   def hook(uc,pc,n,user):
    ptr=uc.reg_read(UC_ARM_REG_R1);count=uc.reg_read(UC_ARM_REG_R2);output.append(bytes(uc.mem_read(ptr,count)))
    uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=cb,end=cb)
   u.reg_write(UC_ARM_REG_R0,stream);u.reg_write(UC_ARM_REG_R1,(sy['audio_ble_ring_connect_pb_descriptor'] if is_c else 0x7766dc));u.reg_write(UC_ARM_REG_R2,msg);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['audio_pb_encode'] if is_c else 0x490c32)|1,0x600000,count=50000)
   ptr=struct.unpack('<I',u.mem_read(stream+16,4))[0];err=bytes(u.mem_read(ptr,40)).split(b'\0')[0] if ptr else b''
   pair.append((u.reg_read(UC_ARM_REG_R0),b''.join(output),struct.unpack('<I',u.mem_read(stream+12,4))[0],err))
  assert pair[0]==pair[1],(a,b,oneof,pair)
  total+=1
print('PASS_RING_PB_CONNECTED_NATIVE',total)
