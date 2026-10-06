#!/usr/bin/env python3
"""Native NOR read/program/erase instructions; synthetic command/FIFO device."""
import importlib.util,json,sys
from pathlib import Path
from unicorn import UC_HOOK_MEM_WRITE
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('read_profile',HERE/'verify_dfu_storage_read.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);s=r.s;v=r.v
EXTRA={'opencfw_provider_420b0c':0x420b0c,'opencfw_provider_420a08':0x420a08,'opencfw_provider_420984':0x420984,'opencfw_provider_4209c4':0x4209c4,'opencfw_provider_420f10':0x420f10}
class Machine(r.Machine):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.actual_read.update((self.symbols[n]&~1) if self.source else pc for n,pc in EXTRA.items() if not self.source or n in self.symbols);self.write_enable=False;self.pending_tx=None;self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.port_write,begin=0x40060010,end=0x40063010)
 def port_write(self,uc,access,address,size,value,user):
  if self.pending_tx is None or (address-0x40060000)%0x1000!=0x10:return
  assert size==4;dest,length,data=self.pending_tx;data+=value.to_bytes(4,'little')
  if len(data)>=length:
   assert self.write_enable and s.NOR<=dest<=dest+length<=s.NOR+s.SIZE;old=bytes(uc.mem_read(dest,length));new=bytes(data[:length]);assert all((x&y)==y for x,y in zip(old,new));uc.mem_write(dest,new);self.pending_tx=None
 def code(self,uc,pc,size,user):
  for name,original,key in [('opencfw_provider_420b0c',0x420b0c,'program'),('opencfw_provider_420a08',0x420a08,'erase')]:
   entry=(self.symbols[name]&~1) if self.source else original
   if pc==entry:self.storage_counts[key]+=1
  blocking=(self.symbols['opencfw_bl_mspi_blocking_transfer']&~1) if self.source else 0x4262e0
  if pc==blocking:
   cmd=self.args()[1];length=self.u(cmd);instruction=int.from_bytes(uc.mem_read(cmd+14,2),'little');address=self.u(cmd+8);self.pending_tx=None
   if instruction==6:self.write_enable=True
   elif instruction==4:self.write_enable=False
   elif instruction==0x20:
    assert self.write_enable and s.NOR<=address<=address+4096<=s.NOR+s.SIZE and address%4096==0;uc.mem_write(address,b'\xff'*4096)
   elif instruction==2:self.pending_tx=[address,length,bytearray()]
  super().code(uc,pc,size,user)
  if pc==blocking and int.from_bytes(uc.mem_read(self.args()[1]+14,2),'little')==5:self.pio_data=bytes([2 if self.write_enable else 0])
def main():
 s.Machine=Machine;s.main();out=Path(sys.argv[sys.argv.index('--output')+1]);report=json.loads(out.read_text());report['limits'][2]='Actual NOR read/program/page-splitting/sector-erase/WREN/WRDI/local-transaction/HAL-blocking/FIFO instructions execute. A synthetic command/FIFO model applies WREN/WRDI, immediate sector erase and completed-page programming with1-to0 checks. Physical timings, power loss within a page, and peripheral coherency unproved; application erase/program/read remains RAM callbacks.';report['source_sha256'].update({str(p.relative_to(s.ROOT)):v.sha(p) for p in [s.ROOT/'g2/components/bootloader/nor_write/nor_write.c',s.ROOT/'g2/components/bootloader/nor_write/nor_write.h',s.ROOT/'g2/components/bootloader/nor_read/runtime_helpers.c',s.ROOT/'g2/components/bootloader/nor_read/nor_read.c']});out.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
