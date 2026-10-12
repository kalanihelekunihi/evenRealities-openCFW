#!/usr/bin/env python3
"""Actual compiled-C/native 1000-ms SMP DB record service effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/smp_db_service.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_smp_database[0x100];const uint8_t *audio_ble_comm_registration_slot;
uint32_t smpDbRecordInUse(const uint8_t *p){(void)p;return 0;}
void smpDbStartServiceTimer(void){}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'service.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SmpDbService',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,pattern,divisor):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  base=sy['audio_ble_smp_database'] if compiled else 0x200708ec
  slot=sy['audio_ble_comm_registration_slot'] if compiled else 0x200004b8
  cfg=0x20083000;u.mem_write(slot,struct.pack('<I',cfg));config=bytearray(24);config[0x10:0x14]=struct.pack('<I',3300);config[0x14:0x16]=struct.pack('<H',divisor);u.mem_write(cfg,bytes(config))
  db=bytearray(0x100)
  for i in range(10):
   p=i*0x18;db[p]=1 if (pattern>>i)&1 else 0;db[p+7]=i+2;db[p+8:p+10]=struct.pack('<H',(i+1)*3)
   for off,v in ((0xc,[0,999,1000,1001,5000][i%5]),(0x10,[0,1000,1001,4000,999][i%5]),(0x14,[1001,1000,999,0,5000][i%5])):db[p+off:p+off+4]=struct.pack('<I',v)
  u.mem_write(base,bytes(db));trace=[]
  for name,cname,stock in [('in_use','smpDbRecordInUse',0x541e50),('timer','smpDbStartServiceTimer',0x541e34)]:
   addr=(sy[cname]&~1) if compiled else stock
   def hook(uc,pc,size,user,name=name):
    if name=='in_use':
     p=uc.reg_read(UC_ARM_REG_R0);index=(p-base)//0x18;trace.append(('in_use',index));uc.reg_write(UC_ARM_REG_R0,uc.mem_read(p,1)[0])
    else:trace.append(('timer',))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
  for r,v in ((UC_ARM_REG_R0,0x99999999),(UC_ARM_REG_R3,0x12345678),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(r,v)
  entry=(sy['SmpDbService']&~1) if compiled else 0x542960
  u.emu_start(entry|1,0x600000,count=30000)
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(base,0xf0)),trace
 cases=0
 for pattern in (0,1,0x155,0x3ff):
  for divisor in (0,1,2,3,10):
   a=run(False,pattern,divisor);b=run(True,pattern,divisor)
   assert a==b,(pattern,divisor,a[0],b[0],[(i,x,y) for i,(x,y) in enumerate(zip(a[1],b[1])) if x!=y][:8],a[2],b[2])
   cases+=1
 print('PASS_SMP_DB_SERVICE_NATIVE',cases)
