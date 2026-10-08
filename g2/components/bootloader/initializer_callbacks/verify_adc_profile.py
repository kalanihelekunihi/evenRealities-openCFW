#!/usr/bin/env python3
"""Native ADC profile and reused user15 power/clock chain; external ROM/callback fixtures explicit."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import arm_const as a
s=importlib.util.spec_from_file_location('sample',Path(__file__).with_name('verify_adc_samples.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
POOL=0x20026df0;PROFILE=0x20004600
REGS=[0x4003800c+4*i for i in range(8)]+[0x40038040,0x4003802c,0x40038030,0x40038200]
class Machine(v.Machine):
 def __init__(self,source,segs,syms,fixture):
  super().__init__(source,segs,syms,fixture);self.external=[]
 def memwrite(self,uc,access,address,size,value,user):
  super().memwrite(uc,access,address,size,value,user)
  if address in REGS and address not in (0x40038040,0x40038200) and not 0x4003802c<=address<=0x40038034:self.records.append([address,size,value&0xffffffff])
  if address==0x40021004:self.records.append([address,size,value&0xffffffff])
 def code(self,uc,pc,size,user):
  if pc==0x40:
   self.external.append(['resident-ROM40-cycle-wait',uc.reg_read(a.UC_ARM_REG_R0)]);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  if pc in (0x08002400,0x08002410,0x08002420):
   if pc==0x08002400:self.external.append(['callback',uc.reg_read(a.UC_ARM_REG_R0),uc.reg_read(a.UC_ARM_REG_R1),self.r(uc.reg_read(a.UC_ARM_REG_R2))])
   else:self.external.append(['hook',hex(pc)])
   uc.reg_write(a.UC_ARM_REG_R0,7);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  super().code(uc,pc,size,user)
 def profile_call(self,kind,params):
  self.done=False;self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000)
  for reg,n in zip((a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3),params+[0]*4):self.cpu.reg_write(reg,n)
  self.cpu.reg_write(a.UC_ARM_REG_SP,v.v.v.v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.v.v.v.STOP|1);name,orig={'transfer':('opencfw_bl_adc_profile_transfer',0x42f020),'apply':('opencfw_bl_adc_apply_profile',0x42ea68),'power-enter':('opencfw_bl_mspi_mode_enter',0x41bf84),'power-leave':('opencfw_bl_mspi_mode_leave',0x41c17a)}[kind];pc=self.symbols[name]&~1 if self.source else orig;self.cpu.emu_start(pc|1,v.v.v.v.STOP+2,count=50000);assert self.done;return self.cpu.reg_read(a.UC_ARM_REG_R0)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();_,segs,syms=v.v.v.v.elf.elf_info(args.elf);cases=[];trace={}
 def compare(label,seq,fixture=None):
  f=dict(flags=0x01afafaf,saved=1,allowed=1,users=0,power_control=0,power_status=0x2000,callbacks=False,primask=0,profile=[2,1,0,7,1,0,1]);f.update(fixture or {});observations=[]
  for source in (False,True):
   m=Machine(source,segs,syms,f);m.cpu.mem_write(POOL,b'\xa5'*72);m.w(POOL,f['flags']);m.w(POOL+4,0);m.cpu.mem_write(POOL+0xc,bytes([f['saved']]));m.w(POOL+0x10,0x0700101d)
   for i,reg in enumerate(REGS):m.w(reg,0xa5000100+i);m.w(POOL+0x14+4*i,0x5a000101+i)
   m.w(0x40038000,0x0200101d);m.cpu.mem_write(PROFILE,bytes(f['profile']));m.w(0x40021004,f['power_control']);m.w(0x40021008,f['power_status']);m.cpu.mem_write(0x20000550,bytes([f['allowed']]));m.w(0x20026e94,f['users']);m.w(0x20026e98,0);m.cpu.mem_write(0x2002719c,b'\x00');m.cpu.mem_write(0x2002719e,b'\x00');m.w(0x20027030,0);m.w(0x20027044,0);m.w(0x40004044,0xabcdef00);m.w(0x20026e3c,0x08002401 if f['callbacks'] else 0);m.w(0x20026e44,0x08002411 if f['callbacks'] else 0);m.w(0x20026e48,0x08002421 if f['callbacks'] else 0);m.cpu.reg_write(a.UC_ARM_REG_PRIMASK,f['primask']);m.records.clear();status=[m.profile_call(k,p) for k,p in seq]
   ptr=m.r(0x20027044);assert not ptr or v.v.v.v.SP-0x1000<=ptr<v.v.v.v.SP
   o=dict(status=status,writes=m.records,context=bytes(m.cpu.mem_read(POOL,72)).hex(),registers=[m.r(x) for x in REGS],config=m.r(0x40038000),power_control=m.r(0x40021004),power_status=m.r(0x40021008),users=m.r(0x20026e94),hfadj=m.r(0x40004044),callback_pointer='stack-local' if ptr else 'null',external=m.external,primask=m.cpu.reg_read(a.UC_ARM_REG_PRIMASK),fpscr=m.cpu.reg_read(a.UC_ARM_REG_FPSCR));observations.append(o)
   if not source:trace.update({hex(pc):raw for pc,raw in m.trace.items()})
  assert observations[0]==observations[1],(label,f,observations);cases.append(dict(label=label,fixture=f,observation=observations[0]));return observations[0]
 for op,save,flags,handle in itertools.product((0,1,2,3,256,257,258,255),(0,1,256,257),(0,0x01afafaf,0x03afafaf),(0,POOL)):
  o=compare('transfer-guards-'+str((op,save,flags,handle)),[('transfer',[handle,op,save])],dict(flags=flags));
  if not handle or not flags:assert o['status']==[2]
 for op,save,saved,allowed,control,status,callbacks,primask in itertools.product((0,1,2),(0,1),(0,1),(0,1),(0,0x2000),(0,0x2000),(False,True),(0,1)):
  o=compare('transfer-'+str((op,save,saved,allowed,control,status,callbacks,primask)),[('transfer',[POOL,op,save])],dict(saved=saved,allowed=allowed,power_control=control,power_status=status,callbacks=callbacks,primask=primask))
  expected=7 if op==0 and save and not saved else 1 if op==0 and save and not allowed else 0;assert o['status']==[expected]
  if op==0 and save and saved and not allowed:assert o['context'][24:26]=='01' and o['power_control']&0x2000 and o['config']==0x0200101d
 for clock,allowed,flags,handle in itertools.product((0,2,3,255),(0,1),(0,0x01afafaf),(0,POOL)):
  o=compare('apply-guards-'+str((clock,allowed,flags,handle)),[('apply',[handle,PROFILE])],dict(flags=flags,allowed=allowed,profile=[clock,1,0,7,1,0,1]));assert o['status']==[2 if not handle or not flags else 6 if clock!=2 else 1 if not allowed else 0]
 for byte,value in itertools.product(range(1,7),(0,1,7,255)):
  fields=[2,1,0,7,1,0,1];fields[byte]=value;compare('apply-field-'+str((byte,value)),[('apply',[POOL,PROFILE])],dict(profile=fields))
 for control,status,callbacks in itertools.product((0,0x2000),(0,0x2000),(False,True)):
  for kind in ('power-enter','power-leave'):compare('native-user15-'+str((kind,control,status,callbacks)),[(kind,[15])],dict(power_control=control,power_status=status,callbacks=callbacks))
 for operation in (1,2):
  o=compare('snapshot-restore-roundtrip-'+str(operation),[('transfer',[POOL,operation,1]),('transfer',[POOL,0,1])],dict(power_control=0x2000,power_status=0x2000));assert o['status']==[0,0] and o['config']==0x0200101d and o['context'][24:26]=='00'
 blob=v.v.v.v.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==v.v.v.v.LOCKED_SHA
 for pc,raw in trace.items():p=int(pc,16);assert blob[p-v.v.v.v.BASE:p-v.v.v.v.BASE+len(bytes.fromhex(raw))]==bytes.fromhex(raw)
 ranges=[(0x42ea68,0x42eaf6),(0x42f020,0x42f14e)];visited=sum(len(bytes.fromhex(raw)) for pc,raw in trace.items() if any(lo<=int(pc,16)<hi for lo,hi in ranges));assert visited==444
 r=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=v.v.v.v.LOCKED_SHA,original_trace=trace,visited_new_body_bytes=visited,comparisons=cases,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limits=['Profile/apply, descriptor query, user15 power enter/leave/release-needed/hooks, critical save, clock route/class4 and status poll/delay execute native instructions.','Only absent resident ROM40 cyclewait and selected optional callback/hook bodies are controlled; fixed power status models acknowledgement success/timeout, not physical timing.','Existing clock callback pointer stack addresses normalized as stack-local after mapped bounds check; no lifetime/callback quiescence proof.','User15-specific dependency paths; special selector20/23/28/29 and nonnull configuration/HFADJ async scheduling remain outside this profile.','Snapshot/restore and ignored power/leave statuses do not establish rollback, safe stop/drain or hardware operation.']);args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256','visited_new_body_bytes']}))
if __name__=='__main__':main()
