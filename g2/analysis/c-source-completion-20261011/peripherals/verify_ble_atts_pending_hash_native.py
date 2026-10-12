#!/usr/bin/env python3
"""Actual C/native pending ATT database-hash response error and success effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_atts_pending_hash_rsp.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_att_common_state[0x64];
uint8_t *attMsgAlloc(uint16_t n){(void)n;return 0;}
uint8_t *attsFindByHandle(uint16_t h,void **g){(void)h;(void)g;return 0;}
void attsErrRsp(uint8_t*c,uint8_t b,uint8_t o,uint16_t h,uint8_t e){(void)c;(void)b;(void)o;(void)h;(void)e;}
void L2cDataReq(uint16_t c,uint16_t h,uint16_t n,uint8_t*b){(void)c;(void)h;(void)n;(void)b;}
void WsfBufFree(void*b){(void)b;}
void __aeabi_memcpy(void*d,const void*s,unsigned n){uint8_t*x=d;const uint8_t*y=s;for(unsigned i=0;i<n;i++)x[i]=y[i];}
'''
N={'attMsgAlloc':0x4b50ae,'attsFindByHandle':0x56c5d4,'attsErrRsp':0x534c9a,
   'L2cDataReq':0x530bbc,'WsfBufFree':0x5304d4,'memcpy':0x439be4}
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,attsCheckPendDbHashReadRsp',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for scenario in ('alloc_fail','missing_attr','success'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_att_common_state'] if compiled else 0x200610ac
   pending,msg,attr,val,length=0x20080000,0x20080100,0x20080200,0x20080300,0x20080400
   u.mem_write(state,(64).to_bytes(2,'little'))
   u.mem_write(state+0xc,(0x1234).to_bytes(2,'little'))
   u.mem_write(state+0x10,pending.to_bytes(4,'little'))
   u.mem_write(pending,(0x3344).to_bytes(2,'little')+(0x5566).to_bytes(2,'little'))
   u.mem_write(msg,bytes([0xa5]*0x30))
   u.mem_write(attr+4,val.to_bytes(4,'little'));u.mem_write(attr+8,length.to_bytes(4,'little'))
   u.mem_write(val,bytes(range(16)));u.mem_write(length,(16).to_bytes(2,'little'))
   addrs={k:sy[k]&~1 for k in N if k!='memcpy'} if compiled else N
   calls=[]
   def hook(uc,pc,n,user):
    name=next(k for k,v in addrs.items() if pc==v)
    regs=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if name=='attMsgAlloc':
     calls.append(('alloc',regs[0]));uc.reg_write(UC_ARM_REG_R0,0 if scenario=='alloc_fail' else msg)
    elif name=='attsFindByHandle':
     calls.append(('find',regs[0]));uc.reg_write(UC_ARM_REG_R0,0 if scenario=='missing_attr' else attr)
    elif name=='attsErrRsp':
     error=int.from_bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4),'little')&255
     calls.append(('error',regs[0]-state,regs[1],regs[2],regs[3],error))
    elif name=='L2cDataReq':calls.append(('send',regs[0],regs[1],regs[2],bytes(uc.mem_read(regs[3],0x1c))))
    elif name=='WsfBufFree':calls.append(('free',regs[0]-pending))
    else:uc.mem_write(regs[0],bytes(uc.mem_read(regs[1],regs[2])))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addrs.values():u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['attsCheckPendDbHashReadRsp'] if compiled else 0x534dd8)|1,0x600000,count=4000)
   pair.append((bytes(u.mem_read(state,0x3c)),bytes(u.mem_read(msg,0x30)),calls))
  assert pair[0]==pair[1],(scenario,pair)
print('PASS_BLE_ATTS_PENDING_HASH_NATIVE 3')
