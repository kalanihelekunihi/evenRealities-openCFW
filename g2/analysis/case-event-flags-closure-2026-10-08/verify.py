"""Wrapper instruction comparisons with explicit compiled kernel child models."""
from pathlib import Path
import sys,struct,json,hashlib,itertools
D=Path(__file__).resolve().parent;s=D.parent/'case-uart-receive-closure-2026-10-08/verify.py';text=s.read_text().split('rows=[]')[0];start=text.index('entries={w:');end=text.index('\ndef guest',start);text=text[:start]+'entries={}'+text[end:];ns={'__file__':str(s)};exec(text,ns);symbols=ns['symbols'];rows=[]
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
entries=[0x0800a888,symbols['case_event_flags_set'],symbols['case_public_event_set_v1031'],symbols['case_public_event_set_v1046'],symbols['case_public_event_set_v1051']]
for id,flags,ipsr,mask,profile in itertools.product([0,0x20005000],[0,8,0x40,0xffffff,0x1000000,0x80000000,0xffffffff],[0,15,16],[0,1],[(0,0,0),(1,0,0x100),(1,1,0x100),(2,2,0)]):
 vals=[];posted,yield_value,old=profile
 for entry in entries:
  u=ns['guest'](0x20,1,0xff,0,0,0,mask,0);u.mem_map(0xe000e000,0x1000);u.mem_write(0xe000ed04,struct.pack('<I',0x123456));u.mem_write(0x20003000,struct.pack('<III',*profile));u.reg_write(UC_ARM_REG_IPSR,ipsr);calls=[];writes=[];write_masks=[]
  def child(u,a,n,data):
   if a==0x0800c568:
    p=u.reg_read(UC_ARM_REG_R2);calls.append(['modeled_from_isr',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),struct.unpack('<I',u.mem_read(p,4))[0]]);u.reg_write(UC_ARM_REG_PC,symbols['case_model_from_isr']|1)
   if a==0x0800c4de:
    calls.append(['modeled_thread',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.reg_write(UC_ARM_REG_PC,symbols['case_model_thread']|1)
  def write(u,access,a,n,v,data):
   if a==0xe000ed04:
    writes.append(v);write_masks.append(u.reg_read(UC_ARM_REG_PRIMASK));assert u.reg_read(UC_ARM_REG_PRIMASK)==mask,('unexpected_mask_at_pendsv_write',entry,mask)
  u.hook_add(UC_HOOK_CODE,child);u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_R0,id);u.reg_write(UC_ARM_REG_R1,flags);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000;assert u.reg_read(UC_ARM_REG_PRIMASK)==mask;assert u.reg_read(UC_ARM_REG_IPSR)==ipsr;vals.append((u.reg_read(UC_ARM_REG_R0),calls,writes,bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_IPSR)))
 assert vals[0]==vals[1]==vals[2]==vals[3],('wrapper',id,flags,ipsr,mask,profile)
 different=bool(id and not flags&0xff000000 and ipsr and posted and (old&~flags));assert (vals[4]!=vals[0])==different
 if id==0 or flags&0xff000000:assert vals[0][0]==0xfffffffc and vals[0][1]==[]
 elif ipsr:
  assert vals[0][0]==(flags if posted else 0xfffffffd);assert vals[0][2]==([0x10000000] if posted and yield_value else [])
 else:assert vals[0][0]==old|flags and vals[0][2]==[]
 rows.append(dict(id=hex(id),flags=hex(flags),ipsr=ipsr,primask=mask,modeled_posted=posted,modeled_yield=yield_value,modeled_old_bits=hex(old),stock_return=hex(vals[0][0]),kernel_model_calls=vals[0][1],icsr_writes=[hex(x) for x in vals[0][2]],icsr_write_primask=([mask]*len(vals[0][2])),v1051_return=hex(vals[4][0]),v1051_differs=different))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,v1051_differences=sum(x['v1051_differs'] for x in rows),firmware_sha256=hashlib.sha256(ns['blob']).hexdigest(),elf_sha256=hashlib.sha256(ns['elf'].read_bytes()).hexdigest(),limits=['Actual wrapper instructions execute, but kernel children0800c568/0800c4de are intercepted and replaced by compiled synthetic result providers on all sides. This is not full kernel integration or original-child execution.','Models supply post status, higher-priority-task wake and existing event bits; they are test inputs, not observed scheduler state.','Four-way wrapper agreement with independent and selected publicv10.3.1/v10.4.6 bodies; IRQ_Context fixture IPSR-only, not full public context helper or producer version proof.','Registeredv10.5.1 body differs under synthetic valid ISR/existing-bit inputs, providing a semantic control; no hardware race or thread scheduling claim.','No firmware/index/device changes or whole-image source/byte-equality claim.']),indent=2)+'\n');print('PASS',len(rows),'modeled-child wrapper cases; newer-version differences',sum(x['v1051_differs'] for x in rows))
