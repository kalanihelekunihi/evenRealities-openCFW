#!/usr/bin/env python3
"""Run the existing 128 clock cases against a full shared ELF, with no stock
executable bytes in the source machine. ROM40 waits are explicit fixtures.
"""
import importlib.util,json,sys,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('clock_cases',ROOT/'g2/analysis/bootloader-completion-2026-10-06/upstream-worker/clock-manager/verify_clock_manager.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
OldMachine=v.Machine
OldUc=v.Uc
def mapped_uc(*args,**kwargs):
 cpu=OldUc(*args,**kwargs);write=cpu.mem_write
 def mapped_write(address,data):
  for page in range(address&~4095,(address+len(data)+4095)&~4095,4096):
   if not any(lo<=page<=hi for lo,hi,_ in cpu.mem_regions()):cpu.mem_map(page,4096)
  return write(address,data)
 cpu.mem_write=mapped_write
 return cpu
v.Uc=mapped_uc
class Machine(OldMachine):
 def __init__(self,source=False,segments=(),symbols=None):
  super().__init__(source,segments,symbols)
  self.source_exec=[(s['address'],s['address']+len(s['data'])) for s in segments if s['flags']&1]
  if source:
   self.cpu.mem_write(v.BASE,bytes(0x25000))
   for segment in segments:self.cpu.mem_write(segment['address'],segment['data'])
 def code(self,uc,pc,size,user):
  if self.source and pc not in (v.STOP,0x40):assert any(lo<=pc and pc+size<=hi for lo,hi in self.source_exec),('source reached non-source executable address',hex(pc))
  super().code(uc,pc,size,user)
v.Machine=Machine
def main():
 v.main()
 elf_path=Path(sys.argv[sys.argv.index('--elf')+1]);out=Path(sys.argv[sys.argv.index('--output')+1]);r=json.loads(out.read_text());_,segments,symbols=v.elf.elf_info(elf_path)
 fixture=dict(class6_feature_enabled=1,class2_enabled=1,class2_mode_selector=0,class3_enabled=1,syspll_lock_status=0,syspll_revision=34,delay_clear_after=2,primask=1)
 results=[];trace={}
 for source in (False,True):
  m=Machine(source,segments,symbols);first=m.run(0,6,11,fixture);statuses=[first['status']]
  for operation in (0,1,0):
   entry=(symbols['clock_request' if operation==0 else 'clock_release']&~1) if source else v.STOCK['request' if operation==0 else 'release']
   m.cpu.reg_write(v.a.UC_ARM_REG_XPSR,0x01000000);m.cpu.reg_write(v.a.UC_ARM_REG_R0,6);m.cpu.reg_write(v.a.UC_ARM_REG_R1,11);m.cpu.reg_write(v.a.UC_ARM_REG_SP,0x2002f000);m.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1);m.finished=False;m.cpu.emu_start(entry|1,v.STOP+2,count=300000);assert m.finished;statuses.append(m.cpu.reg_read(v.a.UC_ARM_REG_R0))
  results.append(dict(statuses=statuses,user_bits=bytes(m.cpu.mem_read(v.USER_BITS,56)).hex(),pll_context=bytes(m.cpu.mem_read(0x20027010,8)).hex(),pll_handle=bytes(m.cpu.mem_read(0x2002703c,4)).hex(),pll_registers=bytes(m.cpu.mem_read(0x400204d8,16)).hex(),primask=m.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),delay_calls=m.delay_calls))
  if not source:trace.update({hex(pc):raw.hex() for pc,raw in m.trace.items()})
 assert results[0]==results[1],results
 assert results[0]['statuses']==[4,0,0,4]
 r['cases']+=1;r['pll_timeout_retry']=results[0];r['original_trace']=dict(r['trace']);r['original_trace'].update(trace);r['elf_sha256']=hashlib.sha256(elf_path.read_bytes()).hexdigest();r['source_only_execution']=True;r['adapter_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();r['limits'].append('Shared source machine has no stock executable bytes and checks every executed source instruction against ELF executable ranges. Added class6 lock-timeout→duplicate request→release→request gives4,0,0,4; fixed MMIO/ROM wait fixtures do not establish physical PLL lock, frequency, IRQ/DMA scheduling or drain.')
 out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(status='PASS',shared_cases=r['cases'],pll_timeout_retry=results[0]['statuses'],elf_sha256=r['elf_sha256'])))
if __name__=='__main__':main()
