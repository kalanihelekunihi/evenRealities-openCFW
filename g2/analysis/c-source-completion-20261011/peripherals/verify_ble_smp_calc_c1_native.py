#!/usr/bin/env python3
"""Actual C/native C1 role/RPA/invalid-token effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_calc_c1.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_smp_handler_state[0xfc];
uint8_t *DmConnLocalRpa(uint8_t x){(void)x;return 0;}
uint8_t *DmConnPeerRpa(uint8_t x){(void)x;return 0;}
uint8_t *DmConnLocalAddr(uint8_t x){(void)x;return 0;}
uint8_t *DmConnPeerAddr(uint8_t x){(void)x;return 0;}
uint8_t DmConnLocalAddrType(uint8_t x){(void)x;return 0;}
uint8_t DmConnPeerAddrType(uint8_t x){(void)x;return 0;}
uint8_t BdaIsZeros(const uint8_t*x){(void)x;return 0;}
uint8_t SecAes(uint8_t*k,uint8_t*p,uint8_t h,uint16_t c,uint8_t e){(void)k;(void)p;(void)h;(void)c;(void)e;return 0;}
void smpSmExecute(uint8_t*c,void*e){(void)c;(void)e;}
'''
N={'DmConnLocalRpa':0x4b707c,'DmConnPeerRpa':0x4b6f28,
   'DmConnLocalAddr':0x4b6f0c,'DmConnPeerAddr':0x4b6eea,
   'DmConnLocalAddrType':0x4b6efa,'DmConnPeerAddrType':0x4b6ed8,
   'BdaIsZeros':0x4d2974,'SecAes':0x536426,'smpSmExecute':0x56ee62}
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O0',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,smpCalcC1Part1',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for part in (1,2):
  for role in (0,1):
   for zero in (False,True):
    for token in (0x2a,0xff):
     pair=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
      u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
      for addr,data in seg:u.mem_write(addr,data)
      ccb,key,random=0x20080000,0x20080100,0x20080200
      localr,peerr,locala,peera=0x20080300,0x20080400,0x20080500,0x20080600
      for addr,seed in ((localr,0x11),(peerr,0x22),(locala,0x33),(peera,0x44)):
       u.mem_write(addr,bytes(6) if zero and addr in (localr,peerr) else bytes(seed+i for i in range(6)))
      u.mem_write(ccb+0x20,bytes(range(14)));u.mem_write(ccb+0x3a,bytes([role]));u.mem_write(ccb+0x3d,b'\x05')
      u.mem_write(key,bytes(range(16)));u.mem_write(random,bytes(range(0x40,0x50)))
      state=sy['audio_ble_smp_handler_state'] if compiled else 0x20070aec
      u.mem_write(state+0xec,b'\x19')
      addresses={k:(sy[k]&~1) for k in N} if compiled else N
      calls=[]
      def hook(uc,pc,n,user):
       name=next(k for k,v in addresses.items() if pc==v)
       a,b,c,d=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
       if name in ('DmConnLocalRpa','DmConnPeerRpa','DmConnLocalAddr','DmConnPeerAddr'):
        uc.reg_write(UC_ARM_REG_R0,{'DmConnLocalRpa':localr,'DmConnPeerRpa':peerr,
                                   'DmConnLocalAddr':locala,'DmConnPeerAddr':peera}[name])
       elif name in ('DmConnLocalAddrType','DmConnPeerAddrType'):
        uc.reg_write(UC_ARM_REG_R0,2 if name=='DmConnLocalAddrType' else 3)
       elif name=='BdaIsZeros':
        uc.reg_write(UC_ARM_REG_R0,int(bytes(uc.mem_read(a,6))==bytes(6)))
       elif name=='SecAes':
        event=int.from_bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4),'little')&255
        calls.append(('aes',bytes(uc.mem_read(a,16)),bytes(uc.mem_read(b,16)),c,d,event))
        uc.reg_write(UC_ARM_REG_R0,token)
       else:calls.append(('sm',a,bytes(uc.mem_read(b,4))))
       uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      for addr in addresses.values():u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
      u.reg_write(UC_ARM_REG_R0,ccb);u.reg_write(UC_ARM_REG_R1,key);u.reg_write(UC_ARM_REG_R2,random)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      u.emu_start(((sy[f'smpCalcC1Part{part}'] if compiled else (0x537742 if part==1 else 0x53786c))|1),0x600000,count=5000)
      pair.append((bytes(u.mem_read(ccb+0x41,1)),calls))
     assert pair[0]==pair[1],(part,role,zero,token,pair)
print('PASS_BLE_SMP_CALC_C1_NATIVE 16')
