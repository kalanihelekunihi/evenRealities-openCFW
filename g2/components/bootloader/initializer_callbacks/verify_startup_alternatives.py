#!/usr/bin/env python3
"""Native startup orchestration against explicit HAL children, including spins."""
import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
s=importlib.util.spec_from_file_location('base',Path(__file__).with_name('verify_context_interrupt.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v);a=v.a
old_uc=v.Uc
def m33_uc(*args,**kwargs):
 cpu=old_uc(*args,**kwargs);cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33);return cpu
v.Uc=m33_uc
CHILDREN={'first':('opencfw_boot_startup_shutdown_first',0x423d20),'second':('opencfw_boot_startup_shutdown_second',0x423dd0),'external-mode':('opencfw_boot_startup_external_mode',0x41583c),'power-update':('opencfw_boot_power_register_update',0x41d92c),'power-init':('opencfw_boot_startup_power_initialize',0x41c4b4),'power-config':('opencfw_boot_startup_power_configure',0x41c86c),'temperature':('opencfw_boot_startup_temperature',0x41ca2c),'descriptor':('opencfw_boot_startup_clock_descriptor',0x422416),'clock-select':('opencfw_boot_startup_clock_select',0x4222a0)}
class Machine(v.Machine):
 def __init__(self,source,segs,syms,f):super().__init__(source,segs,syms);self.f=f;self.events=[];self.failed=None;self.repeat={};self.spin=False
 def code(self,uc,pc,size,user):
  if pc==0x4156ac:
   dest=uc.reg_read(a.UC_ARM_REG_R0);src=uc.reg_read(a.UC_ARM_REG_R1);count=uc.reg_read(a.UC_ARM_REG_R2);assert count==20
   uc.mem_write(dest,bytes(uc.mem_read(src,count)));uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  for kind,(name,stock) in CHILDREN.items():
   if pc!=(self.symbols[name]&~1 if self.source else stock):continue
   args=[uc.reg_read(r) for r in [a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2]]
   if kind=='temperature':event=[kind,hex(uc.reg_read(a.UC_ARM_REG_S0))];uc.mem_write(args[0],bytes(8))
   elif kind=='descriptor':event=[kind,bytes(uc.mem_read(args[0],20)).hex()]
   elif kind=='power-init':event=[kind]
   else:event=[kind,*args[:{'first':0,'second':0,'external-mode':1,'power-update':2,'power-config':2,'clock-select':3}[kind]]]
   self.events.append(event);ret=self.f.get(kind,0)
   if kind in ['first','second'] and ret:self.failed=kind
   uc.reg_write(a.UC_ARM_REG_R0,ret);uc.reg_write(a.UC_ARM_REG_PC,uc.reg_read(a.UC_ARM_REG_LR));return
  if self.failed:
   self.repeat[pc]=self.repeat.get(pc,0)+1
   if self.repeat[pc]>4:self.spin=True;self.done=True;uc.emu_stop();return
  super().code(uc,pc,size,user)
 def run(self,conditional):
  self.cpu.mem_write(0x20027198,bytes([self.f['flag']]));self.cpu.mem_write(0x434154,struct.pack('<I',self.f.get('power-word',0x11223344)));self.cpu.reg_write(a.UC_ARM_REG_XPSR,0x01000000);self.cpu.reg_write(a.UC_ARM_REG_SP,v.SP);self.cpu.reg_write(a.UC_ARM_REG_LR,v.STOP|1);self.cpu.reg_write(a.UC_ARM_REG_C1_C0_2,0xf00000)
  pc=(self.symbols['opencfw_boot_startup_conditional' if conditional else 'opencfw_provider_41fa50']&~1) if self.source else (0x41fa98 if conditional else 0x41fa50);self.cpu.emu_start(pc|1,v.STOP+2,count=20000);assert self.done,(self.source,hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
  return dict(events=self.events,flag=self.cpu.mem_read(0x20027198,1)[0],spin=self.spin,failed=self.failed)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);arg=ap.parse_args();_,segs,syms=v.elf.elf_info(arg.elf);assert hashlib.sha256(v.BLOB.read_bytes()).hexdigest()==v.LOCKED_SHA;cases=[];trace={}
 for conditional,flag,first,second,clock in itertools.product([False,True],[0,1,2,255],[0,1],[0,7],[0,9]):
  f=dict(flag=flag,first=first,second=second,**{'clock-select':clock});obs=[]
  for source in [False,True]:
   m=Machine(source,segs,syms,f);obs.append(m.run(conditional))
   if not source:trace.update(m.trace)
  assert obs[0]==obs[1],(conditional,f,obs);cases.append(dict(conditional=conditional,fixture=f,observation=obs[0]))
 blob=v.BLOB.read_bytes()
 for pc,raw in trace.items():assert bytes.fromhex(raw)==blob[pc-v.BASE:pc-v.BASE+len(bytes.fromhex(raw))]
 r=dict(status='PASS',cases=len(cases),elf_sha256=hashlib.sha256(arg.elf.read_bytes()).hexdigest(),original_sha256=v.LOCKED_SHA,runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_trace={hex(pc):raw for pc,raw in trace.items()},comparisons=cases,limits=['Native startup conditional/orchestration executes. All nine HAL children injected; original4156ac20-byte copy modeled because native run produced incorrect descriptor/stack bytes in this emulator. Source constant copy executes. Not HAL/power/clock/memcpy closure.','First/second errors execute into recurring instruction loops, preserveflag1 and prevent subsequentcalls; no hardware halt or reset performed.','Float argument is passed inS0 and compares exact25.0f bits. Descriptor20bytes and explicitcalls compare; scratch pointer relocated and scratch bytes not used downstream.','Injected clock errors are ignored as stock; all-success conditional clearsflag only after externalmode/powerupdate. No hardware timing/drain or live scheduling proof.']);arg.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256']}))
if __name__=='__main__':main()
