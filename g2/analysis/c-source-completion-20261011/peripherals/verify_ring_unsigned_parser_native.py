#!/usr/bin/env python3
"""Compare parser body and endptr with native under a fixed ASCII locale."""
from pathlib import Path
import subprocess,tempfile,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_unsigned_parser.c'
STUB='''#include <stdint.h>
int32_t audio_uart_ring_locale_space_4d58ae(uint32_t x){(void)x;return 0;}
int32_t audio_uart_ring_locale_lower_4d58c2(uint32_t x){return (int32_t)x;}
void audio_uart_ring_errno_range_set_439cb2(void){}
'''
cases=[('2.2.6.10',10),('  +123x',10),('-1',10),('000',0),('0xff',0),('0XAf',16),('0779',0),('z!',36),('!',10),('+',10),('0x',0),('0x00',0),('4294967295',10),('4294967296',10),('18446744073709551615',10),('ffffffff',16),('100000000',16),('xyz',1),('123',37),('123',0xffffffff)]
rng=random.Random(0x48d874)
for _ in range(80):
 base=rng.choice((2,8,10,16,20,36));digits='0123456789abcdefghijklmnopqrstuvwxyz'[:base]
 cases.append((rng.choice(('', '+', '-', '  '))+''.join(rng.choice(digits) for _ in range(rng.randrange(1,24)))+'!',base))
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_parse_uint_48d874',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for string,base in cases:
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   u.mem_write(0x20070000,string.encode()+b'\0');u.mem_write(0x20071000,b'\xff'*4)
   errno=[]
   for name,cs,stock in (('space','audio_uart_ring_locale_space_4d58ae',0x4d58ae),('lower','audio_uart_ring_locale_lower_4d58c2',0x4d58c2),('range','audio_uart_ring_errno_range_set_439cb2',0x439cb2)):
    target=sym[cs] if compiled else stock
    def hook(uc,pc,size,user,name=name):
     x=uc.reg_read(UC_ARM_REG_R0)&255
     if name=='space':uc.reg_write(UC_ARM_REG_R0,int(x in (9,10,11,12,13,32)))
     elif name=='lower':uc.reg_write(UC_ARM_REG_R0,x+32 if 65<=x<=90 else x)
     else:errno.append(1)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   u.reg_write(UC_ARM_REG_R0,0x20070000);u.reg_write(UC_ARM_REG_R1,0x20071000);u.reg_write(UC_ARM_REG_R2,base)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_uart_ring_parse_uint_48d874'] if compiled else 0x48d874)|1,0x600000,count=30000)
   end=struct.unpack('<I',u.mem_read(0x20071000,4))[0]
   pair.append((u.reg_read(UC_ARM_REG_R0),end-0x20070000,len(errno)))
  assert pair[0]==pair[1],(string,base,pair)
print('PASS_RING_UNSIGNED_PARSER_NATIVE',len(cases))
