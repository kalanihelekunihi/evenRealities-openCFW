#!/usr/bin/env python3
"""Reset storage profile with real NOR read wrapper/HAL/FIFO and modeled NOR port."""
import importlib.util,json,sys
from pathlib import Path
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_INVALID
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('storage',HERE/'verify_dfu_storage.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s);v=s.v
EXTRA={'opencfw_boot_nor_read':0x420f70,'opencfw_provider_41fe9c':0x41fe9c,'opencfw_provider_41fed4':0x41fed4,'opencfw_bl_nor_read_before':0x41ff08,'opencfw_bl_nor_read_after':0x41ff1e,'opencfw_bl_nor_read_configure':0x420e8c,'opencfw_bl_nor_busy':0x42074e,'opencfw_bl_nor_wait':0x4207a2,'opencfw_bl_nor_read_delay':0x4207f4,'opencfw_hal_mspi_control_latency':0x41ff34,'opencfw_provider_41fe48':0x41fe48,'opencfw_provider_420e08':0x420e08,'opencfw_hal_mspi_control':0x4251c0,'opencfw_hal_mspi_pio_mixed':0x42488e}
class Machine(s.Machine):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.actual_read={(self.symbols[n]&~1) if self.source else pc for n,pc in EXTRA.items() if not self.source or n in self.symbols};self.pio_data=None;self.pio_offset=0;self.cpu.hook_add(UC_HOOK_MEM_READ,self.port_read,begin=0x40060014,end=0x40063014);self.cpu.hook_add(UC_HOOK_MEM_INVALID,self.fault)
 def fault(self,uc,access,address,size,value,user):
  print("MEMORY",hex(address),self.phase,self.args(),list(self.trace)[-20:]);return False
 def port_read(self,uc,access,address,size,value,user):
  if self.pio_data is not None and 0x40060000<=address<0x40064000 and (address-0x40060000)%0x1000==0x14:
   assert size==4;word=self.pio_data[self.pio_offset:self.pio_offset+4].ljust(4,b'\0');uc.mem_write(address,word);self.pio_offset+=4
 def code(self,uc,pc,size,user):
  if pc==0x08002220:raise AssertionError('unrecovered HAL control request')
  if pc==0x4166aa:assert self.args()[1] in [1000,0xffffffff];self.ret();return
  if pc==0x416088:self.ret(2);return
  if pc in [0x416378,0x41f9e6]:self.ret();return
  read=(self.symbols['opencfw_boot_nor_read']&~1) if self.source else 0x420f70
  if pc==read:self.storage_counts['read']+=1
  blocking=(self.symbols['opencfw_bl_mspi_blocking_transfer']&~1) if self.source else 0x4262e0
  if pc==blocking:
   cmd=self.args()[1];length=self.u(cmd);instruction=int.from_bytes(uc.mem_read(cmd+14,2),'little');address=self.u(cmd+8)
   if instruction==0x6c:
    assert s.NOR<=address<=address+length<=s.NOR+s.SIZE;self.pio_data=bytes(uc.mem_read(address,length));self.pio_offset=0
   elif instruction==5:self.pio_data=b'\0';self.pio_offset=0
   else:self.pio_data=None
  if pc in self.actual_read:
   assert any(lo<=pc<hi for lo,hi in self.exec_ranges)
   if not self.source:self.trace[hex(pc)]=bytes(uc.mem_read(pc,size)).hex()
   return
  super().code(uc,pc,size,user)
def main():
 s.Machine=Machine;s.main();out=Path(sys.argv[sys.argv.index('--output')+1]);r=json.loads(out.read_text());r['limits'][2]='Actual NOR-read wrapper, mutex/power brackets, read-mode setup, busy polling, HAL blocking transfer and FIFO instructions execute with a synthetic NOR-backed FIFO port. NOR program/erase and application image operations remain RAM callbacks; no physical timing/coherence/power-loss proof.';r['source_sha256'].update({str(p.relative_to(s.ROOT)):v.sha(p) for p in [s.ROOT/'g2/components/bootloader/nor_read'/n for n in ['nor_read.c','nor_read.h','runtime_helpers.c','runtime_helpers.h']]});out.write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
