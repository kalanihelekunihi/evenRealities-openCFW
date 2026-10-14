#!/usr/bin/env python3
"""Native cd80 sender ambient-stack ABI with real16-byte queue providers."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib,itertools
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;E=H/'final/case.elf';F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with E.open('rb') as f:
 e=ELFFile(f);sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
Q=0x20002600;BUF=0x20002800;SP=0x20008000;STOP=0x2000f000;TASK=0x20002100;rows=[]
def run(native,op,seed,state,full,capacity,mask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,F.read_bytes()[32:])
 else:
  for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.mem_write(0x20007000,bytes([seed])*0x2000)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 w(SP,0);w(0x20000164,Q);w(Q,BUF);w(Q+4,BUF+(capacity-1)*16);w(Q+8,BUF+capacity*16);w(Q+12,BUF+(capacity-1)*16);w(Q+56,capacity if full else 0);w(Q+60,capacity);w(Q+64,16);u.mem_write(Q+68,b'\xff\xff');w(0x2000013c,int(state!=0));w(0x20000158,int(state==2))
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[TASK,op,0xaabb1234,0]):u.reg_write(r,v)
 saved=[0x45670000+i for i in range(8)]
 for r,v in zip(range(UC_ARM_REG_R4,UC_ARM_REG_R11+1),saved):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start((0x0800cd80 if native else sy['case_policy_task_event_send'])|1,STOP,count=100000)
 assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
 assert [u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)]==saved
 return {'return':u.reg_read(UC_ARM_REG_R0),'primask':u.reg_read(UC_ARM_REG_PRIMASK),'ram':bytes(u.mem_read(0x20000000,0x3000)).hex()}
for op,seed,state,full,capacity,mask in itertools.product([0,1,3,5,6,7,10,0xffffffff],[0,0xa5,0xff],[0,1,2],[False,True],[2,4],[0,1]):
 a=run(True,op,seed,state,full,capacity,mask);b=run(False,op,seed,state,full,capacity,mask)
 if a!=b:
  (H/'sender-failure.json').write_text(json.dumps({'op':op,'seed':seed,'state':state,'full':full,'capacity':capacity,'mask':mask,'native':a,'source':b},indent=2)+'\n');raise AssertionError((op,seed,state,full,capacity,mask))
 assert a['return']==int(not full)
 if not full:
  ram=bytes.fromhex(a['ram']);assert struct.unpack_from('<IIII',ram,0x2800+(capacity-1)*16)==(op,0xaabb1234,TASK,seed*0x01010101)
 rows.append({'op':hex(op),'seed':seed,'state':state,'full':full,'capacity':capacity,'initial_primask':mask,'final_primask':a['primask'],'return':a['return']})
r={'status':'PASS_NATIVE16_SENDER_AMBIENT_STACK_ABI','cases':len(rows),'ELF_sha256':sha(E),'firmware_sha256':sha(F),'comparisons':rows,'limits':['Real providers and native frame layout; fourth copied word reflects incoming stack bytes, not initialized/fabricated data','Synchronous empty/full generic/ISR queues with no waiting tasks; consumer/blocking/IRQ concurrency excluded','Defined returns, all12288RAM bytes, callee-saved and SP compare; stack traces outside observed domain not claimed']};(H/'sender-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
