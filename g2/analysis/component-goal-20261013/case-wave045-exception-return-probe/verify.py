#!/usr/bin/env python3
"""Actual native/source PendSV context graph up to real EXC_RETURN branch."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib,random
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;P=H.parent/'case-wave039-list-cursor-contract';E=P/'final/case.elf';F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with E.open('rb') as f:
 e=ELFFile(f);symbols=list(e.get_section_by_name('.symtab').iter_symbols());sy={s.name:s['st_value'] for s in symbols};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];v=next(s for s in symbols if s.name=='case_vector_pendsv_0102');source_start=v['st_value']&~1;source_size=v['st_size'];segment=next((a,b) for a,b in segs if a<=source_start<a+len(b));body=segment[1][source_start-segment[0]:source_start-segment[0]+source_size];returns=[source_start+i for i in range(0,len(body)-1,2) if body[i:i+2]==b'\x18\x47'];assert len(returns)==1;source_return=returns[0]
MSP=0x20002c88;STOP=0x2000f000;rows=[];rng=random.Random(0x102);cases=[(s,[rng.getrandbits(32) for _ in range(8)]) for s in ['same_priority','higher_priority','suspended','fallback_priority','only_current'] for _ in range(1)]
def run(native,scenario,registers):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,F.read_bytes()[32:])
 else:
  for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);low=MSP;phase='setup';endpoint=False
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def observe(uc,address,size,data):
  nonlocal low,endpoint
  low=min(low,uc.reg_read(UC_ARM_REG_MSP));assert low>=0x20002888
  if phase=='handler' and address==(0x0800b360 if native else sy['case_boot_service_task_entry']&~1) and uc.reg_read(UC_ARM_REG_IPSR)==0:endpoint=True;uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,observe)
 def invoke(address,arguments):
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],arguments[:4]+[0]*4):u.reg_write(r,v)
  for i,v in enumerate(arguments[4:]):w(MSP+i*4,v)
  u.reg_write(UC_ARM_REG_SP,MSP);u.reg_write(UC_ARM_REG_LR,STOP|1);u.emu_start(address|1,STOP,count=200000);assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==MSP
  return u.reg_read(UC_ARM_REG_R0)
 invoke(0x0800af70 if native else sy['case_boot_first_task_prepare'],[])
 tasks=[];frames=[];tops=[];priorities=[1,2 if scenario=='higher_priority' else 1]
 for i,priority in enumerate(priorities):
  task=invoke(0x0800b3e8 if native else sy['case_boot_transport_heap_allocate'],[96]);stack=invoke(0x0800b3e8 if native else sy['case_boot_transport_heap_allocate'],[256]);u.mem_write(task,bytes(96));w(task+48,stack);entry=(0x0800b360 if native else sy['case_boot_service_task_entry'])|1
  invoke(0x0800ae96 if native else sy['case_boot_task_initialize'],[entry,0,64,0x11110000+i,priority,0,task,0]);tasks.append(task);frame=struct.unpack('<I',bytes(u.mem_read(task,4)))[0];frames.append(frame);tops.append(frame+64)
  if i==0 or scenario!='only_current':invoke(0x0800bfe2 if native else sy['case_policy_task_list_insert'],[0x20000ff4+priority*20,task+4])
 old=tasks[0];new=old if scenario in ['suspended','only_current'] else tasks[1];w(0x20000128,old);w(0x20000138,3 if scenario=='fallback_priority' else max(priorities));w(0x20000158,int(scenario=='suspended'));w(0x20000ff4+priorities[0]*20+4,old+4)
 u.reg_write(UC_ARM_REG_MSP,MSP);u.reg_write(UC_ARM_REG_PSP,frames[0]+32);u.reg_write(UC_ARM_REG_CONTROL,0);u.reg_write(UC_ARM_REG_IPSR,14);u.reg_write(UC_ARM_REG_LR,0xfffffffd)
 for r,val in zip(range(UC_ARM_REG_R4,UC_ARM_REG_R11+1),registers):u.reg_write(r,val)
 phase='handler';u.emu_start((0x08000102 if native else source_start)|1,STOP,count=100000);assert endpoint and u.reg_read(UC_ARM_REG_LR)==(0x0800b31d if native else sy['case_boot_task_return'])
 assert u.reg_read(UC_ARM_REG_MSP)==MSP and u.reg_read(UC_ARM_REG_PRIMASK)==0
 assert struct.unpack('<I',bytes(u.mem_read(0x20000128,4)))[0]==new
 assert struct.unpack('<8I',bytes(u.mem_read(frames[0],32)))==tuple(registers)
 expected=registers if new==old else [0xa5a5a5a5]*8
 actual=[u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)];assert actual==expected
 selected=frames[0] if new==old else frames[1];assert u.reg_read(UC_ARM_REG_PSP)==selected+64
 ram=bytearray(u.mem_read(0x20000000,0x2888))
 for top in tops:
  assert struct.unpack('<I',bytes(u.mem_read(top-8,4)))[0]==entry
  assert struct.unpack('<I',bytes(u.mem_read(top-12,4)))[0]==(0x0800b31d if native else sy['case_boot_task_return'])
  ram[top-0x20000000-12:top-0x20000000-4]=bytes(8)
 return {'current':hex(new),'PSP':hex(u.reg_read(UC_ARM_REG_PSP)),'MSP':hex(u.reg_read(UC_ARM_REG_MSP)),'thread_R0':hex(u.reg_read(UC_ARM_REG_R0)),'registers':actual,'ram':ram.hex(),'stack_bytes':MSP-low,'IPSR':u.reg_read(UC_ARM_REG_IPSR)}
for scenario,registers in cases:
 pair=[]
 for native in [True,False]:
  try:pair.append({'status':'RETURNED_TO_THREAD_ENTRY','result':run(native,scenario,registers)})
  except UcError as error:pair.append({'status':'ARCHITECTURAL_FIXTURE_EXCEPTION','error':str(error),'errno':error.errno})
 rows.append({'scenario':scenario,'native':pair[0],'source':pair[1]})
r={'status':'EXCEPTION_RETURN_PROBE_COMPLETED','cases':len(rows),'ELF_sha256':sha(E),'firmware_sha256':sha(F),'comparisons':rows,'limits':['Actual source/native body runs through genuine exception-return instruction; no fabricatedreturn/providerstub','Manually seeded IPSR/PSP/MSP without active NVIC controller exception entry; failure here is an architectural fixture limit, not proof firmware is wrong','Physical exception delivery/return and complete controller state remain external validation dependencies']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases']);print([(x['scenario'],x['native']['status'],x['source']['status']) for x in rows])
