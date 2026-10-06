#!/usr/bin/env python3
"""Offline MRAM-control/reset-register comparisons; no physical flash writes."""
import argparse,importlib.util,json,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
s=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
v.ENTRIES.update(mram_aligned=0x42e4a0,mram_dispatch=0x42e4f4,terminal_mode=0x42e514,dfu_error_transaction=0x42de0e,dfu_runtime_enable=0x42ddf2)
DATA=0x20032000;LOG=0x08002130
class Machine(v.Machine):
 def __init__(self,*args,real_bridge=False,real_critical=False,real_guards=False,**kw):
  super().__init__(*args,**kw);self.cpu.mem_map(0x40000000,4096);self.real_bridge=real_bridge;self.real_critical=real_critical;self.real_guards=real_guards;self.cpu.mem_map(0x40021000,4096);self.cpu.mem_map(0x0200f000,4096);self.cpu.mem_map(0x40014000,4096);self.w(0x40014024,0x55);self.last_cleanup=[0,0x55];self.saved=0;self.status=0;self.cpu.mem_write(DATA,bytes(range(64)))
 def code(self,uc,pc,size,user):
  cleanup=[self.u(0x40014008),self.u(0x40014024)]
  if cleanup!=self.last_cleanup:self.events.append(['cleanup_registers',*cleanup]);self.last_cleanup=cleanup
  if self.u(0x40000008) or self.u(0x40000004):self.events.append(['terminal_write',self.u(0x40000004),self.u(0x40000008)]);self.finished=True;uc.emu_stop();return
  r0,r1,r2,r3=self.args()
  if pc==0x41b8ec and not self.real_critical:self.events.append(['critical_save',self.saved]);uc.reg_write(v.a.UC_ARM_REG_PRIMASK,1);self.ret(self.saved);return
  if pc in [0x41bd92,0x41bde4] and not self.real_guards:self.events.append(['guard_begin' if pc==0x41bd92 else 'guard_end']);self.ret();return
  if self.real_guards and pc==0x41cd1a:self.events.append(['power_control',r0,r1,self.u(r2)]);self.ret(7);return
  if pc==(0x0200ff20 if self.real_bridge else 0x42e8a4):
   words=self.u(uc.reg_read(v.a.UC_ARM_REG_SP));assert words<=16;data=bytes(self.cpu.mem_read(r2,words*4)) if words else b'';self.events.append(['mram_provider',r0,r1,data.hex(),r3,words,self.status]);self.ret(self.status);return
  if pc==LOG:self.events.append(['log',r0,r1]);self.ret();return
  if pc in [0x41f8ba,0x41ba80,0x41c990]:self.events.append([{0x41f8ba:'mode_one',0x41ba80:'mode_two',0x41c990:'cleanup'}[pc]]+([r0] if pc!=0x41c990 else []));self.ret();return
  super().code(uc,pc,size,user)
 def invoke(self,name,args):
  d=self.run(name,args)
  if name in ['dfu_error_transaction','dfu_runtime_enable'] or (name=='terminal_mode' and (args[0]&255) in [0,1]):d.pop('return')
  d['primask']=self.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK);d['cleanup_registers']=[self.u(0x40014008),self.u(0x40014024)];d['reset_registers']=[self.u(0x40000004),self.u(0x40000008)];return d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--real-bridge',action='store_true');ap.add_argument('--real-critical',action='store_true');ap.add_argument('--real-guards',action='store_true');a=ap.parse_args();_,seg,sym=v.elf.elf_info(a.elf);cases=[];trace={}
 def check(name,args,fixture):
  ms=[Machine(real_bridge=a.real_bridge,real_critical=a.real_critical,real_guards=a.real_guards),Machine(True,seg,sym,real_bridge=a.real_bridge,real_critical=a.real_critical,real_guards=a.real_guards)]
  for m in ms:
   m.cpu.mem_write(0x200271a7,bytes([fixture.get('guard_enabled',0)]));m.w(0x40021018,fixture.get('guard_status',0))
   m.saved=fixture.get('saved',0);m.status=fixture.get('status',0);m.cpu.reg_write(v.a.UC_ARM_REG_PRIMASK,fixture.get('initial_mask',fixture.get('saved',0) if a.real_critical else 1))
  d=[m.invoke(name,args) for m in ms];assert d[0]==d[1],(name,args,fixture,{k:[x[k] for x in d] for k in d[0] if d[0][k]!=d[1][k]});trace.update(ms[0].trace);cases.append({'function':name,'arguments':args,'fixture':fixture,'result':d[0]})
 for name in ['mram_aligned','mram_dispatch']:
  for dest,words,status,saved in itertools.product([0x7fe000,0x7fe004,0x7fe010,0x7fe001,0x3ffff0,0],[0,1,3,4,8],[0,1,0x55,0xffffffff],[0,1]):check(name,[0x12344321,DATA,dest,words],{'status':status,'saved':saved})
 for mode in [0,1,2,6,255,256,257,0xffffffff]:check('terminal_mode',[mode],{})
 for saved,status in itertools.product([0,1],[0,1,0xffffffff]):check('dfu_error_transaction',[],{'saved':saved,'status':status})
 for saved in [0,1]:check('dfu_runtime_enable',[],{'saved':saved})
 if a.real_guards:
  for saved,status_word in itertools.product([0,1],[0,0x80]):check('mram_dispatch',[0x12344321,DATA,0x7fe000,4],{'saved':saved,'guard_enabled':1,'guard_status':status_word})
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 d={'status':'PASS','real_source_power_guards':a.real_guards,'real_source_critical_save':a.real_critical,'real_source_rom_bridge':a.real_bridge,'cases':len(cases),'comparisons':cases,'original_trace':trace,'distinct_original_trace_bytes':len(used),'original_sha256':v.SHA,'elf_sha256':v.sha(a.elf),'source_sha256':{p.name:v.sha(p) for p in Path(__file__).parent.iterdir() if p.suffix in ['.c','.h','.py','.ld','.S']},'limits':['Original/source alignment/control/error/reset-store and PRIMASK instructions execute; MMIO pages are synthetic and execution stops after observed terminal register write.','MRAM programming is synthetic at the ROM entry when real_source_rom_bridge is true (local cleanup helper executes), or at the local wrapper otherwise; critical save executes recovered assembly when real_source_critical_save is true; power guards execute when real_source_power_guards is true with power-control callback synthetic; other platform primitives remain synthetic. No flash writes or hardware reset.','Error transaction attempts fourFFFFFFFF words at7fe000 through guarded programmer then terminal mode0 regardless of returned program status.','PRIMASK restore is unconditionally MSR per original M-class instructions; erroneous raw decompiler privilege-check narrative is not adopted.','No actual ROM/MRAM driver, clock/cache/timing, infinite-loop silicon behavior or complete bootloader proof.']};a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':'PASS','cases':len(cases),'original_bytes':len(used)},indent=2))
if __name__=='__main__':main()
