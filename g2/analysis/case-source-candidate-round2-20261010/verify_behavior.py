#!/usr/bin/env python3
"""Original-vs-source wrapper execution with identical explicit kernel result boundaries."""
from pathlib import Path
import hashlib,itertools,json,struct,sys
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2]
F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';blob=F.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
raw=blob[32:];E=D/'build/behavior.elf';symbols={};segments=[]
with E.open('rb') as f:
 elf=ELFFile(f)
 for s in elf.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in elf.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
children={0x0800c4cc:'get',0x0800c478:'clear_isr',0x0800c44c:'clear_task',0x0800c568:'set_isr',0x0800c4de:'set_task'}
entries={'clear':(0x0800a7d2,symbols['case_clear_event']),'post':(0x0800a888,symbols['case_event_post']),'forward':(0x0800a888,symbols['case_forward_event'])}
def one(entry,event,flags,ipsr,mask,posted,wake,old):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x08000000,0x40000);u.mem_write(0x08000000,raw);u.mem_map(0x00100000,0x10000);u.mem_map(0x20000000,0x10000);u.mem_map(0xe000e000,0x1000)
 for a,b in segments:u.mem_write(a,b)
 u.mem_write(0xe000ed04,struct.pack('<I',0x123456));u.reg_write(UC_ARM_REG_R0,event);u.reg_write(UC_ARM_REG_R1,flags);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 calls=[];writes=[]
 def code(u,a,n,data):
  if a not in children:return
  kind=children[a];r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1);r2=u.reg_read(UC_ARM_REG_R2)
  if kind=='get':result=old;calls.append((kind,r0))
  elif kind=='clear_task':result=old;calls.append((kind,r0,r1))
  elif kind=='clear_isr':result=posted;calls.append((kind,r0,r1))
  elif kind=='set_task':result=old|r1;calls.append((kind,r0,r1))
  else:
   assert struct.unpack('<I',u.mem_read(r2,4))[0]==0
   u.mem_write(r2,struct.pack('<I',wake));result=posted;calls.append((kind,r0,r1,0))
  u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def write(u,access,a,n,v,data):
  if a==0xe000ed04:writes.append((v,u.reg_read(UC_ARM_REG_PRIMASK)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start(entry|1,0x20000000,count=2000)
 assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return (u.reg_read(UC_ARM_REG_R0),calls,writes,bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_IPSR))
counts={k:0 for k in entries};examples=[]
for kind,(orig,native) in entries.items():
 for event,flags,ipsr,mask,posted,wake,old in itertools.product([0,0x20005000],[0,0x8,0x1000000,0xffffffff],[0,15,16],[0,1],[0,1],[0,1],[0,0x48]):
  a=one(orig,event,flags,ipsr,mask,posted,wake,old);b=one(native,event,flags,ipsr,mask,posted,wake,old)
  assert a==b,(kind,event,flags,ipsr,mask,posted,wake,old,a,b)
  counts[kind]+=1
  if len(examples)<6 and event and not flags&0xff000000 and ipsr and posted:examples.append({'kind':kind,'flags':flags,'ipsr':ipsr,'return':a[0],'calls':a[1]})
receipt=json.loads((D/'behavior-build-receipt.json').read_text());result={'status':'PASS','counts':counts,'total':sum(counts.values()),'original_firmware_sha256':hashlib.sha256(blob).hexdigest(),'candidate_elf_sha256':hashlib.sha256(E.read_bytes()).hexdigest(),'python':sys.executable,'unicorn_version':__import__('unicorn').__version__,'pyelftools_version':__import__('elftools').__version__,'kernel_boundaries':children,'examples':examples,'scope':'Original and compiled source wrappers execute; identical explicit kernel result models intercept only documented child entries. No kernel implementation, scheduling, or hardware claim.'}
(D/'behavior-results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',counts)
