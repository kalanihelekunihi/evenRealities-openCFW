#!/usr/bin/env python3
"""RTOS allocator byte-for-byte arena/global comparison, suspend/resume stubs."""
import argparse,importlib.util,json,hashlib,random
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('heap_v',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);v.ENTRIES.update(rtos_allocate=0x419730,rtos_free=0x419830)
class Machine(v.Machine):
 def code(self,uc,pc,size,user):
  if pc in [0x4181d8,0x418228]:self.events.append(['suspend' if pc==0x4181d8 else 'resume']);self.ret();return
  if pc==0x41b5f6:self.events.append(['malloc-failed']);self.finished=True;uc.emu_stop();return
  if pc==0x41b2f8:raise AssertionError('unexpected fatal assertion')
  super().code(uc,pc,size,user)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert v.sha(v.BLOB)==v.SHA
 _,segments,symbols=v.elf.elf_info(a.elf);pair=[Machine(),Machine(True,segments,symbols)];trace={};cases=[];allocated=[];rng=random.Random(17)
 operations=[('alloc',n) for n in [1,7,8,9,16,112,1024,257,4096]]
 operations += [('random',i) for i in range(100)]
 operations += [('drain',i) for i in range(100)]
 operations += [('alloc',0),('alloc',0xffffffff),('alloc',0x80000000),('alloc',0x20000),('alloc',81880),('drain',0)]
 for kind,value in operations:
  if kind=='random':kind='free' if allocated and rng.randrange(3)==0 else 'alloc';value=rng.randrange(1,4096) if kind=='alloc' else allocated.pop(rng.randrange(len(allocated)))
  if kind=='drain':
   if not allocated:continue
   kind='free';value=allocated.pop(0)
  name='rtos_allocate' if kind=='alloc' else 'rtos_free';results=[]
  for m in pair:
   ret=m.run(name,[value]);failed=['malloc-failed'] in ret['events'];results.append(dict(result=ret['return'] if kind=='alloc' and not failed else None,events=ret['events'],arena=hashlib.sha256(m.cpu.mem_read(0x2000055c,0x14000)).hexdigest(),head=bytes(m.cpu.mem_read(0x20027020,8)).hex(),globals=bytes(m.cpu.mem_read(0x20027108,20)).hex(),failed=failed))
  assert results[0]==results[1],(kind,value,results)
  if kind=='alloc' and not results[0]['failed']:allocated.append(results[0]['result'])
  trace.update(pair[0].trace);cases.append(dict(operation=kind,value=value,result=results[0]))
 assert pair[0].u(0x2002710c)==0x13ff0
 used={int(pc,0)+i for pc,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 report=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_sha256=v.SHA,elf_sha256=v.sha(a.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.is_file()},original_trace=trace,comparisons=cases,limits=['Scheduler suspend/resume synthetic; allocation failure stops at stock hook41b5f6 (its logger/nonreturn implementation not executed). Invalid/double frees not tested.','Full81920-byte arena/hash and all heap globals compared after each operation. Stack alignment/header constants derived from locked data4341a0=8. Separate from TLSF.','M4 compatibility, no real scheduler race/IRQ/hardware/exact build proof.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
