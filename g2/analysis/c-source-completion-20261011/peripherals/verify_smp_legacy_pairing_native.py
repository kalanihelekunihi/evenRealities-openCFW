#!/usr/bin/env python3
"""Actual compiled-C/native SMP legacy pairing state, event, and lower effects."""
from pathlib import Path
import subprocess,tempfile,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_pairing.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_smp_handler_state[0x100];const uint8_t *audio_ble_comm_registration_slot;
uint8_t SmpScAllocScratchBuffers(void *p){(void)p;return 0;}
uint8_t *DmSecGetEccKey(void){return 0;}
void *audio_queue_copy_bytes(void*d,const void*s,uint32_t n){(void)d;(void)s;(void)n;return d;}
void smpSmExecute(uint8_t*c,const uint8_t*e){(void)c;(void)e;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'sc.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_smp_pairing_callback_56e6e0',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 names={'alloc':('SmpScAllocScratchBuffers',0x56cdc0),'key':('DmSecGetEccKey',0x53490c),'copy':('audio_queue_copy_bytes',0x439be4),'execute':('smpSmExecute',0x56ee62)}
 def run(compiled,io1,io2,auth1,auth2,flag,sc_on,allocated,minimum,role):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  ccb=0x20080000;sc=0x20081000;cfg=0x20082000;mitm=0x20083000;passkey=0x20083001;key=0x20084000;buf1=0x20085000;buf2=0x20086000
  data=bytearray([0xa5]*0x60);data[0x21]=io1;data[0x28]=io2;data[0x22]=flag;data[0x29]=flag;data[0x23]=auth1;data[0x2a]=auth2;data[0x24]=16;data[0x2b]=16;data[0x3a]=role;data[0x3d]=7;data[0x48:0x4c]=struct.pack('<I',sc);u.mem_write(ccb,bytes(data))
  record=bytearray([0xa5]*0x1c);record[0xc:0x10]=struct.pack('<I',buf1);record[0x10:0x14]=struct.pack('<I',buf2);u.mem_write(sc,bytes(record))
  c=bytearray(32);c[5]=minimum;c[8]=auth2;u.mem_write(cfg,bytes(c));u.mem_write(mitm,b'\xa5\xa5');u.mem_write(key,bytes(range(96)));u.mem_write(buf1,bytes([0xee]*96));u.mem_write(buf2,bytes([0xee]*32))
  state=sy['audio_ble_smp_handler_state'] if compiled else 0x20070aec;slot=sy['audio_ble_comm_registration_slot'] if compiled else 0x200004b8
  u.mem_write(state+0xf8,bytes([sc_on]));u.mem_write(slot,struct.pack('<I',cfg));u.mem_write(0x200fef00,bytes([0xa5]*256));trace=[]
  for name,(cs,ns) in names.items():
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    r0,r1,r2=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
    if name=='alloc':trace.append(('alloc',r0==ccb));uc.reg_write(UC_ARM_REG_R0,allocated)
    elif name=='key':trace.append(('key',));uc.reg_write(UC_ARM_REG_R0,key)
    elif name=='copy':
     trace.append(('copy',r0-buf1 if buf1<=r0<buf1+96 else 0x100+r0-buf2,r1-key,r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));uc.reg_write(UC_ARM_REG_R0,r0)
    else:trace.append(('execute',r0==ccb,bytes(uc.mem_read(r1,24))))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  for r,v in ((UC_ARM_REG_R0,ccb),(UC_ARM_REG_R1,mitm),(UC_ARM_REG_R2,passkey),(UC_ARM_REG_R3,0x12345678),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(r,v)
  a=sy['audio_ble_smp_pairing_callback_56e6e0'] if compiled else 0x56e6e0
  u.emu_start(a|1,0x600000,count=50000)
  return (u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(ccb,0x50)),bytes(u.mem_read(sc,0x1c)),bytes(u.mem_read(mitm,2)),bytes(u.mem_read(buf1,96)),bytes(u.mem_read(buf2,32)),trace)
 cases=0
 configs=[(0,0,8,8,0),(1,1,8,8,1),(4,2,8,8,0),(2,2,8,8,0),(1,1,0,0,0),(4,2,0,0,0),(2,2,4,0,0)]
 for cfg in configs:
  for sc_on in (0,1):
   for allocated in (0,1):
    for minimum in (0,16):
     a,b=run(False,*cfg,sc_on,allocated,minimum,0),run(True,*cfg,sc_on,allocated,minimum,0)
     assert a==b,(cfg,sc_on,allocated,minimum,a[-1],b[-1],a[:4],b[:4])
     cases+=1
 rng=random.Random(0x56e6e0)
 for _ in range(200):
  cfg=(rng.randrange(5),rng.randrange(5),rng.choice((0,4,8,12,16,28)),rng.choice((0,4,8,12,16,28)),rng.randrange(2))
  sc_on=rng.randrange(2);allocated=rng.randrange(2);minimum=rng.choice((0,16,20));role=rng.randrange(2)
  a,b=run(False,*cfg,sc_on,allocated,minimum,role),run(True,*cfg,sc_on,allocated,minimum,role)
  assert a==b,(cfg,sc_on,allocated,minimum,role,a[-1],b[-1],a[:4],b[:4])
  cases+=1
 print('PASS_SMP_LEGACY_PAIRING_NATIVE',cases)
