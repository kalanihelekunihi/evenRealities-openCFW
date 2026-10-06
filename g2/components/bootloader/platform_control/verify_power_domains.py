#!/usr/bin/env python3
"""Power-domain source instructions with bounded callback/poll providers."""
import argparse,importlib.util,json,itertools,struct
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
s=importlib.util.spec_from_file_location('v',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v);v.ENTRIES.update(enter=0x41bf84,leave=0x41c17a,needed=0x41c0be)
class Machine(v.Machine):
 def __init__(self,*a,fixture=None,**kw):
  super().__init__(*a,**kw);self.f=fixture or {}
  for base,size in [(0x40020000,0x2000),(0x40014000,0x1000),(0x400c1000,0x1000)]:self.cpu.mem_map(base,size)
  if self.source:
   for n,sym in [('enter','opencfw_bl_mspi_mode_enter'),('leave','opencfw_bl_mspi_mode_leave'),('needed','opencfw_boot_power_release_needed')]:self.symbols['opencfw_boot_'+n]=self.symbols[sym]
  self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=0x40000000,end=0x400fffff)
 def write(self,uc,access,address,size,value,user):self.events.append(['mmio-write',hex(address),size,value])
 def code(self,uc,pc,size,user):
  a=self.args();f=self.f
  if pc==0x41b8ec:saved=uc.reg_read(v.a.UC_ARM_REG_PRIMASK);uc.reg_write(v.a.UC_ARM_REG_PRIMASK,1);self.ret(saved);return
  if pc in [0x41d246,0x41d21c]:self.events.append(['poll',hex(pc),*a]+([self.u(uc.reg_read(v.a.UC_ARM_REG_SP))] if pc==0x41d246 else []));self.ret(f.get('poll_status',0));return
  if pc in [0x41d1c0,0x41bae8,0x4223d8,0x4222f0,0x422364]:self.events.append([hex(pc),*a[:2]] if pc in [0x4222f0,0x422364] else [hex(pc),a[0]]);self.ret(7);return
  if pc==0x08002400:self.events.append(['callback',a[0],a[1],self.u(a[2]) if a[0]!=1 else uc.mem_read(a[2],1)[0]]);self.ret(7);return
  if pc in [0x08002410,0x08002420]:self.events.append(['hook',hex(pc)]);self.ret(7);return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA;_,segs,syms=v.elf.elf_info(a.elf);cases=[];trace={};blob=v.BLOB.read_bytes()
 fixtures=[dict(control=0,status=0xffffffff,poll_status=0),dict(control=0xffffffff,status=0,poll_status=0),dict(control=0xffffffff,status=0xffffffff,poll_status=4),dict(control=0xffffffff,status=0,poll_status=7),dict(control=0,status=0,poll_status=4),dict(control=0xffffffff,status=0,pm_mode=3,pm_saved=3,callbacks=True),dict(control=0xffffffff,status=0xffffffff,revision=0,poll_status=0),dict(control=0xffffffff,status=0,revision=255,callbacks=True)]
 for name,selector,f in itertools.product(['enter','leave','needed'],list(range(36))+[255,256,272,0xffffffff],fixtures):
  pair=[Machine(fixture=f),Machine(True,segs,dict(syms),fixture=f)]
  for m in pair:
   for addr in [0x40021004,0x4002100c]:m.w(addr,f['control'])
   for addr in [0x40021008,0x40021010]:m.w(addr,f['status'])
   m.w(0x4002000c,f.get('revision',0));m.w(0xe000edfc,0xffffffff);m.w(0x40020250,0xffffffff);m.cpu.mem_write(0x200271a5,bytes([f.get('pm_mode',0),f.get('pm_saved',0)]));m.cpu.reg_write(v.a.UC_ARM_REG_PRIMASK,0)
   m.w(0x20026e3c,0x08002401 if f.get('callbacks') else 0);m.w(0x20026e44,0x08002411 if f.get('callbacks') else 0);m.w(0x20026e48,0x08002421 if f.get('callbacks') else 0)
  result=[m.run(name,[selector]) for m in pair];got=[{'return':r['return'],'events':r['events'],'primask':m.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),'control':[m.u(x) for x in [0x40021004,0x4002100c,0xe000edfc,0x40020250]],'pm_saved':ucbyte(m,0x200271a6)} for m,r in zip(pair,result)];assert got[0]==got[1],(name,selector,f,got);trace.update(pair[0].trace);cases.append(dict(function=name,selector=selector,fixture=f,result=got[0]))
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))};report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in [HERE/'power_domains.c',HERE/'power_domains.h',HERE/'power_domains_module.ld',HERE/'runtime_query.c',Path(__file__)]},original_trace=trace,comparisons=cases,limits=['Actual descriptor copy, power control-register updates, shared-domain release test and optional-hook dispatch execute. Poll/status/delay/clock/special-mode providers controlled; no hardware acknowledgement or time proof.','Special mode41bae8 remains explicit dependency only selector20. Optional callback bodies synthetic, selector1 callback payload compared only its stock one-byte value.','Critical save is controlled here; existing actual assembly is separately validated. No hardware writes or full source closure.']);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
def ucbyte(m,p):return m.cpu.mem_read(p,1)[0]
if __name__=='__main__':main()
