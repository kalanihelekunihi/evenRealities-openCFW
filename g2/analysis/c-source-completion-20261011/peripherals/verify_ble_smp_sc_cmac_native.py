#!/usr/bin/env python3
"""Actual ARM C/stock CMAC dispatch and failure cleanup branches."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_sc_cmac.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_smp_handler_state[256];uint32_t sec_result,call_log[18],call_count;
static void rec(uint32_t a,uint32_t b,uint32_t c){uint32_t i=call_count++*3;call_log[i]=a;call_log[i+1]=b;call_log[i+2]=c;}
uint8_t SecCmac(const uint8_t*k,uint8_t*t,uint16_t n,uint8_t h,uint16_t c,uint8_t e){rec(1,(uint32_t)k,(uint32_t)t);rec(2,n,h);rec(3,c,e);return sec_result;}
void WsfBufFree(void *p){rec(4,(uint32_t)p,0);}
void smpSmExecute(void *c,void*m){rec(5,(uint32_t)c,(uint32_t)m);}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SmpScCmac',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for sec_result in (0,1):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   key,text,ccb,msg=0x20081000,0x20081100,0x20081200,0x20081300
   u.mem_write(ccb+0x3d,bytes([7]));u.mem_write(msg,bytes([0xa5]*8))
   handler=sy['audio_ble_smp_handler_state'] if compiled else 0x20070aec
   u.mem_write(handler+0xec,bytes([0x34]))
   if compiled:u.mem_write(sy['sec_result'],sec_result.to_bytes(4,'little'))
   calls=[]
   if not compiled:
    def hook(uc,pc,n,user):
     if pc==0x53665c:
      sp=uc.reg_read(UC_ARM_REG_SP)
      args=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
      args += [int.from_bytes(uc.mem_read(sp+i,4),'little') for i in (0,4)]
      calls.extend([(1,args[0],args[1]),(2,args[2],args[3]),(3,args[4],args[5])])
      uc.reg_write(UC_ARM_REG_R0,sec_result)
     elif pc==0x5304d4:calls.append((4,uc.reg_read(UC_ARM_REG_R0),0))
     else:calls.append((5,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in (0x53665c,0x5304d4,0x56ee62):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   sp=0x200ff000;u.mem_write(sp,msg.to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_R0,key);u.reg_write(UC_ARM_REG_R1,text)
   u.reg_write(UC_ARM_REG_R2,0x41);u.reg_write(UC_ARM_REG_R3,ccb)
   u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['SmpScCmac'] if compiled else 0x56cec2)|1,0x600000,count=4000)
   if compiled:
    n=int.from_bytes(u.mem_read(sy['call_count'],4),'little')
    raw=u.mem_read(sy['call_log'],n*12)
    calls=[tuple(int.from_bytes(raw[i+j:i+j+4],'little') for j in (0,4,8)) for i in range(0,len(raw),12)]
   pair.append((bytes(u.mem_read(msg,8)),calls))
  assert pair[0]==pair[1],(sec_result,pair)
print('PASS_BLE_SMP_SC_CMAC_NATIVE 2')
