#!/usr/bin/env python3
"""Actual C/native ATT DB hash message assembly for two authenticated layouts."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_atts_db_hash.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_atts_state[0x268];
uint16_t attsIsHashableAttr(const uint8_t*a){(void)a;return 0;}
void *WsfBufAlloc(uint16_t n){(void)n;return 0;}
uint8_t AttsHashDatabaseString(uint8_t*k,uint8_t*m,uint16_t n){(void)k;(void)m;(void)n;return 1;}
void __aeabi_memcpy(void*d,const void*s,unsigned n){uint8_t*x=d;const uint8_t*y=s;for(unsigned i=0;i<n;i++)x[i]=y[i];}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,AttsCalculateDbHash',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for allocate in (False,True):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_atts_state'] if compiled else 0x2006e5f0
   group,attrs,uuid1,uuid2,val,lenptr,msg=0x20080000,0x20080100,0x20080200,0x20080300,0x20080400,0x20080500,0x20080600
   u.mem_write(state+0x258,group.to_bytes(4,'little'))
   u.mem_write(group,bytes(0x20));u.mem_write(group+4,attrs.to_bytes(4,'little'))
   u.mem_write(group+0x10,(1).to_bytes(2,'little'));u.mem_write(group+0x12,(2).to_bytes(2,'little'))
   u.mem_write(attrs,uuid1.to_bytes(4,'little'));u.mem_write(attrs+0x10,uuid2.to_bytes(4,'little'))
   u.mem_write(attrs+0x14,val.to_bytes(4,'little'));u.mem_write(attrs+0x18,lenptr.to_bytes(4,'little'))
   u.mem_write(attrs+0x1e,b'\x01')
   u.mem_write(uuid1,b'\x0a\x18');u.mem_write(uuid2,bytes(range(16)))
   u.mem_write(val,b'xyz');u.mem_write(lenptr,(3).to_bytes(2,'little'))
   u.mem_write(msg,bytes([0xa5]*64))
   calls=[]
   addresses={name:sy[name]&~1 for name in ('attsIsHashableAttr','WsfBufAlloc','AttsHashDatabaseString')} if compiled else {'attsIsHashableAttr':0x534ea8,'WsfBufAlloc':0x530446,'AttsHashDatabaseString':0x53525c,'memset':0x43c0e4,'memcpy':0x439be4}
   def hook(uc,pc,n,user):
    r0,r1,r2=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
    if pc==addresses['attsIsHashableAttr']:uc.reg_write(UC_ARM_REG_R0,4 if r0==attrs else 21)
    elif pc==addresses['WsfBufAlloc']:
     calls.append(('alloc',r0));uc.reg_write(UC_ARM_REG_R0,msg if allocate else 0)
    elif pc==addresses['AttsHashDatabaseString']:
     calls.append(('hash',r2,bytes(uc.mem_read(r0,16)),bytes(uc.mem_read(r1,r2))))
     uc.reg_write(UC_ARM_REG_R0,1)
    elif pc==addresses.get('memset'):
     uc.mem_write(r0,bytes([r2&255])*r1)
    elif pc==addresses.get('memcpy'):
     uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for addr in addresses.values():u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['AttsCalculateDbHash'] if compiled else 0x53527c)|1,0x600000,count=10000)
   pair.append((calls,bytes(u.mem_read(msg,64))))
  assert pair[0]==pair[1],(allocate,pair)
print('PASS_BLE_ATTS_DB_HASH_NATIVE 2')
