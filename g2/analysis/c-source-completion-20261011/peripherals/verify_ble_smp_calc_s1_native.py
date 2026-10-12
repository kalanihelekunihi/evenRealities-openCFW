#!/usr/bin/env python3
"""Bounded actual C/native S1 encryption and invalid-token event effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_calc_s1.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_smp_handler_state[0xfc];
void Calc128Cpy64(uint8_t*d,const uint8_t*s){(void)d;(void)s;}
uint8_t SecAes(uint8_t*k,uint8_t*p,uint8_t h,uint16_t c,uint8_t e){(void)k;(void)p;(void)h;(void)c;(void)e;return 0;}
void smpSmExecute(uint8_t*c,void*e){(void)c;(void)e;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O0',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,smpCalcS1',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for token in (0x23,0xff):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for addr,data in seg:u.mem_write(addr,data)
   ccb,key,rand1,rand2=0x20080000,0x20080100,0x20080200,0x20080300
   u.mem_write(ccb+0x3d,b'\x05');u.mem_write(key,bytes(range(16)))
   u.mem_write(rand1,bytes(range(0x10,0x18)));u.mem_write(rand2,bytes(range(0x20,0x28)))
   state=sy['audio_ble_smp_handler_state'] if compiled else 0x20070aec
   u.mem_write(state+0xec,b'\x19')
   calls=[]
   addrs={('copy' if name=='Calc128Cpy64' else 'aes' if name=='SecAes' else 'sm'):(sy[name]&~1)
          for name in ('Calc128Cpy64','SecAes','smpSmExecute')} if compiled else {'copy':0x542a52,'aes':0x536426,'sm':0x56ee62}
   def hook(uc,pc,n,user):
    a,b,c,d=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if pc==addrs['copy']:
     uc.mem_write(a,bytes(uc.mem_read(b,8)))
    elif pc==addrs['aes']:
     event=int.from_bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4),'little')&255
     calls.append(('aes',bytes(uc.mem_read(a,16)),bytes(uc.mem_read(b,16)),c,d,event))
     uc.reg_write(UC_ARM_REG_R0,token)
    else:calls.append(('sm',a,bytes(uc.mem_read(b,4))))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addrs.values():u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   for reg,val in ((UC_ARM_REG_R0,ccb),(UC_ARM_REG_R1,key),(UC_ARM_REG_R2,rand1),(UC_ARM_REG_R3,rand2)):
    u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['smpCalcS1'] if compiled else 0x537998)|1,0x600000,count=3000)
   pair.append((bytes(u.mem_read(ccb+0x41,1)),calls))
  assert pair[0]==pair[1],(token,pair)
print('PASS_BLE_SMP_CALC_S1_NATIVE 2')
