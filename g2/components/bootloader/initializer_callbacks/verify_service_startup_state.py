#!/usr/bin/env python3
"""Bound the shared original/source reset at actual EasyLogger callback return.
No DFU, task scheduling, hardware writes or return stubs added by this runner.
"""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('failure',HERE.parent/'thread_creation/verify_source_image_failures.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
class Machine(f.Machine):
 def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.service_return=None
 def code(self,uc,pc,size,user):
  if pc==self.initializer_native_entries.get('opencfw_boot_init_callback_services'):self.service_return=uc.reg_read(f.v.a.UC_ARM_REG_LR)&~1
  if self.service_return is not None and pc==self.service_return:self.stop('service-callback-return');return
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();_,segments,syms=f.v.elf.elf_info(args.elf);f.p.configure_profiles(syms);blob=f.v.BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()==f.v.SHA
 app=f.s.ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';assert f.v.sha(app)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';vector=app.read_bytes()[32:40];reset=struct.unpack('<2I',vector)[1]&~1;results=[];trace={}
 for source in (False,True):
  m=Machine(source,segments,syms);f.setup(m,b'\xff'*f.s.SIZE,blob,reset,vector);m.cpu.reg_write(f.v.a.UC_ARM_REG_SP,0x2007fb00);m.cpu.reg_write(f.v.a.UC_ARM_REG_LR,f.v.STOP|1);start=syms['opencfw_boot_reset_entry']&~1 if source else 0x43291a;m.cpu.emu_start(start|1,f.v.STOP+2,count=20000000);assert m.reason=='service-callback-return',m.reason
  results.append(dict(service_state=bytes(m.cpu.mem_read(0x20026700,256)).hex(),mutex=m.u(0x200270e8),mutex_cb=bytes(m.cpu.mem_read(0x20026cb0,80)).hex(),native_visits={name:m.initializer_native_visits[name] for name in f.p.initv.SERVICE_ENTRIES},events=[x for x in m.initializer_events if x[0].removesuffix('-native') in f.p.initv.SERVICE_ENTRIES]))
  if not source:trace.update(m.trace)
 assert results[0]==results[1],{k:[x[k] for x in results] for k in results[0] if results[0][k]!=results[1][k]}
 assert results[0]['mutex']==0x20026cb0
 state=bytes.fromhex(results[0]['service_state']);assert state[0]==5 and state[0xf0]==1
 assert state[0x31:0xd6]==bytes(165)
 assert results[0]['native_visits']['opencfw_bl_service_guard']==1
 assert len([x for x in results[0]['events'] if x[0]=='opencfw_provider_416610-native' and x[1]==0x433d28])==1
 r=dict(status='PASS',cases=1,elf_sha256=f.v.sha(args.elf),original_sha256=f.v.SHA,comparison=results[0],original_trace=trace,runner_sha256=f.v.sha(Path(__file__)),limits=['Exact shared ELF reset/initializer instructions execute to actual EasyLogger callback return; DFU and scheduler phases are outside this focused case.','Reuses the seven-case fixture and its existing explicit external ROM/MMIO/FP64/provider models. This is an additional observation boundary, not a hardware or general scheduling proof.','EasyLogger uses actual static80-byte mutex constructor and native queue initialization, without heap allocation. Mutex take/give remain lower kernel boundaries; no asynchronous exclusion/drain proof.']);args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','cases','elf_sha256']}))
if __name__=='__main__':main()
