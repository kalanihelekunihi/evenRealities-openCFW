#!/usr/bin/env python3
"""Actual native/source timer wrap, unlink and synchronous callback graph."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib,subprocess,random
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;P=H.parent/'case-wave022-logging-stack';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';production=P/'final/case.elf';receipt=json.loads((P/'final/receipt.json').read_text());E=H/'fixture.elf';cmd=receipt['link_command'].copy();cmd.insert(1,'-ucase_boot_scheduler_counter_read');cmd[-1]=str(E);subprocess.run(cmd,check=True)
assert sha(F)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
with E.open('rb') as f:
 e=ELFFile(f);sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
SP=0x20008000;STOP=0x2000f000;OUT=0x20003000;LIST=0x20002000;SECOND=0x20002400;rows=[];rng=random.Random(0xb284)
inputs=[(n,p,c) for n in [0,1,0x7fffffff,0xffffffff] for p in [0,1,0x80000000,0xffffffff] for c in [0,1,2]]+[(rng.randrange(2**32),rng.randrange(2**32),rng.randrange(3)) for _ in range(96)]
def run(native,now,previous,count):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,F.read_bytes()[32:])
 else:
  for a,b in segments:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 w(0x20000134,now);w(0x2000016c,previous);w(0x20000170,LIST);w(0x20000174,SECOND);w(OUT,0xa5a5a5a5)
 # Conventional FreeRTOS circular list: genuine unlink consumes item+4,+8,+16.
 w(LIST,count);w(LIST+4,LIST+8);w(LIST+8,0xffffffff);w(SECOND,0)
 timers=[0x20002100+i*0x80 for i in range(count)];items=[t+4 for t in timers];nodes=[LIST+8]+items
 for i,node in enumerate(nodes):w(node+4,nodes[(i+1)%len(nodes)]);w(node+8,nodes[(i-1)%len(nodes)])
 for i,t in enumerate(timers):
  w(t+4,17+i);w(t+16,t);w(t+20,LIST);w(t+32,(0x0800ca6c if native else sy['case_boot_scheduler_counter_read'])|1);u.mem_write(t+40,b'\0')
 u.reg_write(UC_ARM_REG_R0,OUT);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);saved=[0xa4560000+i for i in range(8)]
 for r,v in zip(range(UC_ARM_REG_R4,UC_ARM_REG_R11+1),saved):u.reg_write(r,v)
 callbacks=[];accesses=[];low=SP
 def code(uc,address,size,data):
  nonlocal low
  low=min(low,uc.reg_read(UC_ARM_REG_SP))
  if address==(0x0800ca6c if native else sy['case_boot_scheduler_counter_read']&~1):
   if uc.reg_read(UC_ARM_REG_R0) in timers:callbacks.append(uc.reg_read(UC_ARM_REG_R0))
 def access(uc,kind,address,size,value,data):
  if address in [0x20000134,0x2000016c,0x20000170]:accesses.append((hex(address),size,'read' if kind==16 else 'write',hex(uc.reg_read(UC_ARM_REG_PC))))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,access);u.emu_start((0x0800b284 if native else sy['case_boot_timer_now'])|1,STOP,count=100000)
 assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
 assert [u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)]==saved
 ram=bytearray(u.mem_read(0x20000000,0x3000))
 for t in timers:ram[t-0x20000000+32:t-0x20000000+36]=bytes(4) # Namespace-normalize only immutable callback pointer fixture.
 return {'return':u.reg_read(UC_ARM_REG_R0),'overflow':struct.unpack('<I',bytes(u.mem_read(OUT,4)))[0],'ram':bytes(ram).hex(),'callbacks':callbacks,'stack_bytes':SP-low,'accesses':accesses}
for now,previous,count in inputs:
 a=run(True,now,previous,count);b=run(False,now,previous,count);fields=[k for k in a if k not in ['stack_bytes','accesses'] and a[k]!=b[k]]
 if fields:
  (H/'failure.json').write_text(json.dumps({'now':now,'previous':previous,'timers':count,'different_fields':fields,'native':a,'source':b},indent=2)+'\n');raise AssertionError((now,previous,count,fields))
 assert a['return']==now and a['overflow']==int(now<previous);assert len(a['callbacks'])==(count if now<previous else 0)
 rows.append({'now':now,'previous':previous,'timers':count,'callbacks':a['callbacks'],'native_stack_bytes':a['stack_bytes'],'source_stack_bytes':b['stack_bytes'],'native_accesses':a['accesses'],'source_accesses':b['accesses']})
r={'status':'PASS_FULL_TIMER_WRAP_UNLINK_CALLBACK_RAM_GRAPH','cases':len(rows),'production_ELF_sha256':sha(production),'fixture_ELF_sha256':sha(E),'link_command':cmd,'comparisons':rows,'limits':['Genuine counter reader retained as test-only synchronous callback, no production root promotion','Empty/one/two one-shot timers; autoreload/event-send/IRQ concurrency not covered','Only immutable callback address word normalized between native/source namespaces; all other12288RAM bytes compare','No child stubs/cuts/return injection or peripheral fixtures']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
