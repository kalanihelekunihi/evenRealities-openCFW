from pathlib import Path
import json,struct,itertools,hashlib,sys
D=Path(__file__).resolve().parent;s=D.parent/'audio-thread-flags-closure-2026-10-08/verify.py';text=s.read_text().split('for id,flags,old,state,ipsr,mask,basepri,running')[0];ns={'__file__':str(s)};exec(text,ns)
from unicorn import *
from unicorn.arm_const import *
T=0x20006000;rows=[]
for requested,options,timeout,bits,state,ipsr in itertools.product([0,0x400000,0xc00000,0x80000000],[0,1,2,3],[0,3],[0,0x400000,0x800000,0xc00000],[0,1,2],[0,15]):
 vals=[]
 for entry in [0x4492c2,ns['symbols']['audio_flags_wait'],ns['symbols']['audio_public_flags_wait']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(ns['raw'])+4095)&~4095);u.mem_write(0x438000,ns['raw']);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in ns['segments']:u.mem_write(a,b)
  u.mem_write(T,bytes(128));u.mem_write(T+0x68,struct.pack('<IB',bits,state));u.mem_write(0x20074a20,struct.pack('<I',T));u.mem_write(0x20074a3c,struct.pack('<I',1));u.mem_write(0x20074a34,struct.pack('<I',0xfffffffe));u.reg_write(UC_ARM_REG_IPSR,ipsr);boundary=[]
  def code(u,a,n,d):
   if a==0x455fa8:boundary.extend([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.emu_stop()
   assert a!=0x4420bc,'yield_was_not_cut'
  def write(u,access,a,n,v,d):
   if T+0x68<=a<T+0x70:assert u.reg_read(UC_ARM_REG_BASEPRI)==0x30
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_R0,requested);u.reg_write(UC_ARM_REG_R1,options);u.reg_write(UC_ARM_REG_R2,timeout);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=30000);assert boundary or u.reg_read(UC_ARM_REG_PC)==0x20000000
  if boundary:assert boundary==[3,1];assert u.reg_read(UC_ARM_REG_BASEPRI)==0x30
  else:assert u.reg_read(UC_ARM_REG_BASEPRI)==0
  vals.append((None if boundary else u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(T,128)),bytes(u.mem_read(0x2000309c,4)),u.reg_read(UC_ARM_REG_BASEPRI),boundary))
 assert vals[0]==vals[1]==vals[2],('wait',requested,options,timeout,bits,state,ipsr);rows.append(dict(requested=hex(requested),options=options,timeout_ticks=timeout,initial_bits=hex(bits),notification_state=state,ipsr=ipsr,endpoint='block_before_entry' if vals[0][4] else 'return',return_value=None if vals[0][4] else hex(vals[0][0]),final_bits=hex(struct.unpack_from('<I',vals[0][1],0x68)[0]),final_notification_state=vals[0][1][0x6c]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),block_boundaries=sum(r['endpoint']=='block_before_entry' for r in rows),comparisons=rows,firmware_sha256=hashlib.sha256(ns['blob']).hexdigest(),elf_sha256=hashlib.sha256(ns['elf'].read_bytes()).hexdigest(),limits=['Original/public actual notify-wait versus independent index0 subset; actual context/tick/critical peers.','Positive waits stop before block455fa8; no timeout expiry/context switch/return model. Constant tick input synthetic, not frequency or elapsed time.','Allocated notification prefix, logical states0/1/2 and IPSR0/15; not real initialized running audio TCB or proof of all fixture reachability.']),indent=2)+'\n');print('PASS',len(rows),'wait comparisons; blocks',sum(r['endpoint']=='block_before_entry' for r in rows))
