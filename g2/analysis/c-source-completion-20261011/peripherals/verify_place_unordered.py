#!/usr/bin/env python3
"""Bounded stock/source unordered event-list insertion."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/event_wait_source_candidate/place_unordered.c';O=D/'place-unordered-m4.o';E=D/'place-unordered-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_block_ticks=0x101001','--defsym=g2_event_place_assert=0x101011','-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,value,ticks):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 listp=0x20011000;index=0x20011008;prev=0x20011020;tcb=0x20012000
 u.mem_write(0x20074a58,(1).to_bytes(4,'little'));u.mem_write(0x20074a20,tcb.to_bytes(4,'little'))
 u.mem_write(listp+4,index.to_bytes(4,'little'));u.mem_write(index+8,prev.to_bytes(4,'little'))
 u.mem_write(prev+4,index.to_bytes(4,'little'))
 for reg,v in ((A.UC_ARM_REG_R0,listp),(A.UC_ARM_REG_R1,value),(A.UC_ARM_REG_R2,ticks),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  if pc==(0x455fa8 if stock else 0x101000):
   events.append([cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)]);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4552ae if stock else sy['g2_event_place_unordered'])|1,0,count=130)
 assert done[0]
 return {'list':u.mem_read(listp,0x2c).hex(),'tcb':u.mem_read(tcb+0x18,0x14).hex(),'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for v in (1,0x01000001,0x04000003):
 for t in (1,10,0xffffffff):
  a=run(True,v,t);b=run(False,v,t);assert a==b,(v,t,a,b);rows.append([v,t])
out={'status':'PASS_EVENT_PLACE_UNORDERED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'One synthetic list/index/previous node and suspended scheduler; delayed placement child cut.'}
(D/'place-unordered-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
