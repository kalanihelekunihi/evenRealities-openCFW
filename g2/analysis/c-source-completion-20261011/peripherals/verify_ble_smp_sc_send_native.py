#!/usr/bin/env python3
"""Actual stock/C four SMP SC packet senders, allocation branches."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_sc_send.c'
STUB='''#include <stdint.h>
uint32_t allocation,call_log[64],call_count;
static void rec(uint32_t k,uint32_t a,uint32_t b,uint32_t c){uint32_t i=call_count++*4;call_log[i]=k;call_log[i+1]=a;call_log[i+2]=b;call_log[i+3]=c;}
void DmConnSetIdle(uint8_t a,uint16_t b,uint8_t c){rec(1,a,b,c);}
void smpStartRspTimer(void*c){rec(2,(uint32_t)c,0,0);}
uint8_t *smpMsgAlloc(uint16_t n){rec(3,n,0,0);return (uint8_t *)allocation;}
void WStrReverseCpy(uint8_t*d,const uint8_t*s,uint16_t n){rec(4,(uint32_t)d,(uint32_t)s,n);for(uint16_t i=0;i<n;i++)d[n-1-i]=s[i];}
void smpSendPkt(void*c,uint8_t*p){rec(5,(uint32_t)c,(uint32_t)p,0);}
void smpSmExecute(void*c,void*m){rec(6,(uint32_t)c,(uint32_t)m,0);}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,smpScSendPubKey',
                 str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[('pub',0x56cfec,'smpScSendPubKey'),('check',0x56d054,'smpScSendDHKeyCheck'),
        ('rand',0x56d0a8,'smpScSendRand'),('confirm',0x56d0fc,'smpScSendPairCnf')]
 for name,native,c_name in cases:
  for allocated in (False,True):
   pair=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    ccb,msg,sc,public,data,packet=0x20080000,0x20080100,0x20080200,0x20080300,0x20080400,0x20080500
    u.mem_write(ccb+0x3d,bytes([7]));u.mem_write(ccb+0x48,sc.to_bytes(4,'little'))
    u.mem_write(sc+0x0c,public.to_bytes(4,'little'))
    u.mem_write(public,bytes(range(64)));u.mem_write(data,bytes(range(0x70,0x80)))
    u.mem_write(msg,bytes([0xa5]*8));u.mem_write(packet,bytes([0xa5]*80))
    if compiled:u.mem_write(sy['allocation'],(packet if allocated else 0).to_bytes(4,'little'))
    calls=[]
    if not compiled:
     hooks={0x4b71dc:1,0x56e5cc:2,0x537bca:3,0x56d8c4:4,0x537a5a:5,0x56ee62:6}
     def hook(uc,pc,n,user):
      a,b,c=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
      k=hooks[pc]
      calls.append((k,a,b if k in (1,4,5,6) else 0,c if k in (1,4) else 0))
      if k==3:uc.reg_write(UC_ARM_REG_R0,packet if allocated else 0)
      if k==4:uc.mem_write(a,bytes(uc.mem_read(b,c))[::-1])
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     for a in hooks:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
    u.reg_write(UC_ARM_REG_R0,ccb);u.reg_write(UC_ARM_REG_R1,msg)
    u.reg_write(UC_ARM_REG_R2,data);u.reg_write(UC_ARM_REG_SP,0x200ff000)
    u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy[c_name] if compiled else native)|1,0x600000,count=8000)
    if compiled:
     count=int.from_bytes(u.mem_read(sy['call_count'],4),'little')
     raw=u.mem_read(sy['call_log'],count*16)
     calls=[tuple(int.from_bytes(raw[i+j:i+j+4],'little') for j in (0,4,8,12)) for i in range(0,len(raw),16)]
    pair.append((bytes(u.mem_read(msg,8)),bytes(u.mem_read(packet,80)),calls))
   assert pair[0]==pair[1],(name,allocated,pair)
print('PASS_BLE_SMP_SC_SEND_NATIVE 8')
