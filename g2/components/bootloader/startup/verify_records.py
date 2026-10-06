#!/usr/bin/env python3
"""Execute stock scatter dispatcher/helpers versus reconstructed source chain."""
import importlib.util,json,hashlib,struct,argparse
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('startupv',HERE/'verify.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);v=m.v
v.ENTRIES.update(init_records_run=0x43299c,vector_base_init=0x432910,system_entry=0x43297c,fpu_init=0x432958)
class EntryMachine(m.Machine):
 def code(self,uc,pc,size,user):
  if pc==0x41b862:
   self.events.append(['platform_system_init',self.args()[0]]);self.ret();return
  if pc==0x4329c4:
   self.events.append(['platform_terminal']);self.finished=True;uc.emu_stop();return
  super().code(uc,pc,size,user)
def main():
 p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--source-table',action='store_true');a=p.parse_args()
 assert v.sha(v.BLOB)==v.SHA
 blob=v.BLOB.read_bytes();_,seg,sym=v.elf.elf_info(a.elf);cases=[];trace={}
 regions=[(0x40,24),(0x20000000,1371),(0x2000055c,0x26c6c),(0x20080000,4096),(0x20081000,0x74100)]
 for base in [0,0x20000000]:
  pair=[m.Machine(),m.Machine(True,seg,sym)]
  for machine in pair:
   # Authenticated table/streams are fixture data; no executable donor bytes.
   if machine.source:
    if a.source_table:assert bytes(machine.cpu.mem_read(0x4330d8,72))==blob[0x230d8:0x23120]
    else:machine.cpu.mem_write(0x4330d8,blob[0x230d8:0x23120])
    for start,n in [(0x434461,22),(0x4341c0,625),(0x434431,48)]:machine.cpu.mem_write(start,blob[start-v.BASE:start-v.BASE+n])
   for addr,n in regions:machine.cpu.mem_write(addr,b'\xcc'*n)
   machine.cpu.reg_write(v.a.UC_ARM_REG_R9,base)
   machine.run('init_records_run',[])
  hashes=[]
  for addr,n in regions:
   data=[bytes(machine.cpu.mem_read(addr,n)) for machine in pair]
   assert data[0]==data[1],hex(addr)
   if addr in [0x2000055c,0x20081000]:assert data[0]==b'\0'*n
   hashes.append(dict(address=hex(addr),bytes=n,sha256=hashlib.sha256(data[0]).hexdigest()))
  trace.update(pair[0].trace);cases.append(dict(base=hex(base),regions=hashes))
 pair=[m.Machine(),m.Machine(True,seg,sym)]
 for machine in pair:machine.w(0xe000ed08,0xdeadbeef)
 results=[machine.run('vector_base_init',[]) for machine in pair]
 assert results[0]==results[1] and results[0]['return']==1
 assert all(machine.u(0xe000ed08)==0x410000 for machine in pair)
 trace.update(pair[0].trace);cases.append(dict(vector_base='0x410000',return_value=1))
 pair=[EntryMachine(),EntryMachine(True,seg,sym)]
 for machine in pair:
  if machine.source:
   if a.source_table:assert bytes(machine.cpu.mem_read(0x4330d8,72))==blob[0x230d8:0x23120]
   else:machine.cpu.mem_write(0x4330d8,blob[0x230d8:0x23120])
   for start,n in [(0x434461,22),(0x4341c0,625),(0x434431,48)]:machine.cpu.mem_write(start,blob[start-v.BASE:start-v.BASE+n])
  for addr,n in regions:machine.cpu.mem_write(addr,b'\xcc'*n)
 results=[machine.run('system_entry',[]) for machine in pair]
 assert all(x['events']==[['platform_system_init',0],['platform_terminal']] for x in results)
 assert all(machine.u(0xe000ed08)==0x410000 for machine in pair)
 for addr,n in regions:assert bytes(pair[0].cpu.mem_read(addr,n))==bytes(pair[1].cpu.mem_read(addr,n))
 trace.update(pair[0].trace);cases.append(dict(system_entry_events=results[0]['events']))
 for initial in [0,0x00550055,0xffffffff]:
  pair=[m.Machine(),m.Machine(True,seg,sym)]
  for machine in pair:
   machine.w(0xe000ed88,initial);machine.cpu.reg_write(v.a.UC_ARM_REG_FPSCR,0)
  results=[machine.run('fpu_init',[]) for machine in pair]
  assert results[0]==results[1]
  assert all(machine.u(0xe000ed88)==(initial|0x00f00000) for machine in pair)
  fpscr=[machine.cpu.reg_read(v.a.UC_ARM_REG_FPSCR) for machine in pair]
  assert fpscr[0]==fpscr[1],fpscr
  trace.update(pair[0].trace);cases.append(dict(initial_cpacr=hex(initial),fpscr_written='0x02040000',fpscr_readback=hex(fpscr[0])))
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 report=dict(source_table={'compiled_bytes':72,'sha256':hashlib.sha256(blob[0x230d8:0x23120]).hexdigest()} if a.source_table else None,status='PASS',cases=len(cases),comparisons=cases,original_sha256=v.SHA,elf_sha256=v.sha(a.elf),distinct_original_trace_bytes=len(used),original_trace=trace,source_sha256={str(x.name):v.sha(x) for x in HERE.iterdir() if x.suffix in ['.c','.h','.S','.py','.ld'] or x.name=='Makefile'},limits=['Direct dispatcher/vector/helper cases have no provider stubs; system-entry case intercepts platform system init and terminal, checking exact call order and init argument0.','Source-table profile supplies72 compiled record bytes; other profiles use fixture records. Compressed streams remain authenticated fixture data and their representation is not reconstructed from source.','Adapters translate stock implicit R9 to the existing C helper interface; exact original compiler ABI/bytes are not claimed.','Only locked valid table tested; callback corruption or malformed streams remain unbounded.','FPU write instruction sets0x02040000 but emulator FPSCR readback may mask unsupported bits; identical readback does not prove silicon mode semantics. No reset/stack-limit, scheduler, ROM/SBL or hardware boot test.','Compatible Cortex-M4 source profile is not byte-identical Cortex-M55 firmware.'])
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status='PASS',cases=len(cases),original_bytes=len(used))))
if __name__=='__main__':main()
