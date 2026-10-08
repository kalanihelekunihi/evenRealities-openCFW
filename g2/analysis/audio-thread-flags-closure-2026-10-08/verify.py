from pathlib import Path
import hashlib,struct,json,itertools,sys
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;fw=D.parents[2]/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=fw.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path(sys.argv[1]);segments=[];symbols={}
with elf.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
def word(at):return struct.unpack_from('<I',raw,at-0x438000)[0]
running_address=word(0x4558a4+4+0x7bc);suspended_address=word(((0x4558b2+4)&~3)+0x7b4);T=0x20006000;rows=[]
for id,flags,old,state,ipsr,mask,basepri,running in itertools.product([0,T],[0,0x400000,0x800000,0x7fffffff,0x80000000],[0,0x100,0x80000000],[0,2],[0,15],[0,1],[0,0x10,0x30],[0,1]):
 vals=[]
 for entry in [0x449238,symbols['audio_thread_flags_set'],symbols['audio_public_flags_set']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(T,b'\xa7'*128);u.mem_write(T+0x68,struct.pack('<IB',old,state));u.mem_write(running_address,struct.pack('<I',running));u.mem_write(suspended_address,bytes(4));u.mem_write(0x2000309c,bytes(4));u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_BASEPRI,basepri);calls=[];writes=[]
  def code(u,a,n,d):
   if a in [0x455c48,0x455dc0]:calls.append([hex(a),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3)])
   assert a not in [0x455d1e,0x455e94],'unexpected_waiting_task_path'
  def write(u,access,a,n,v,d):
   if T+0x68<=a<T+0x70:
    assert u.reg_read(UC_ARM_REG_BASEPRI)==0x30,'notify_write_not_protected';writes.append([hex(a),n,hex(v),0x30])
   assert a!=0xe000ed04,'unexpected_yield_nonwaiting_task'
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_R0,id);u.reg_write(UC_ARM_REG_R1,flags);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000;valid=bool(id and not flags&0x80000000);irq=bool(ipsr or running and (mask or basepri))
  assert u.reg_read(UC_ARM_REG_R0)==(old|flags if valid else 0xfffffffc)
  assert struct.unpack('<IB',u.mem_read(T+0x68,5))==((old|flags,2) if valid else (old,state))
  assert len(calls)==(2 if valid else 0)
  if valid:assert calls==[[hex(0x455dc0 if irq else 0x455c48),0,flags,1],[hex(0x455dc0 if irq else 0x455c48),0,0,0]]
  assert u.reg_read(UC_ARM_REG_PRIMASK)==mask;expected_base=basepri if not valid or irq else 0;assert u.reg_read(UC_ARM_REG_BASEPRI)==expected_base
  vals.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(T,128)),u.reg_read(UC_ARM_REG_BASEPRI),u.reg_read(UC_ARM_REG_PRIMASK),calls,writes))
 assert vals[0]==vals[1]==vals[2];rows.append(dict(thread_id=hex(id),flags=hex(flags),old=hex(old),notification_state=state,ipsr=ipsr,primask=mask,basepri=basepri,scheduler_running=running,return_value=hex(vals[0][0]),final_basepri=vals[0][2],provider_calls=vals[0][4]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(blob).hexdigest(),raw_sha256=hashlib.sha256(raw).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),scheduler_fixture=dict(running=hex(running_address),suspended=hex(suspended_address),critical_depth='0x2000309c'),limits=['Actual wrapper/context and generic notify task/ISR bodies execute; no entry stubs, selected nonwaiting notification states0/2 only.','Synthetic TCB and scheduler globals; waiting-state1, task wake/ready transitions, PendSV and audio dispatcher initialization excluded.','Cortex-M4 Unicorn profile for compatible code from M55 image; BASEPRI write protection0x30 and context-dependent restoration explicitly checked.','Invalid thread IDs testNULL only, not arbitrary pointer safety. No source-complete/byte-identical or hardware scheduling claim.']),indent=2)+'\n');print('PASS',len(rows),'actual-provider Apollo thread-flags cases')
