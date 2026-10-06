#!/usr/bin/env python3
"""Source reset image with native MSPI command queue bodies and scalar table."""
import importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('power_profile',HERE/'verify_dfu_storage_power.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);s=p.s;v=p.v
EXTRA={'opencfw_hal_mspi_cq_init':0x423f28,'opencfw_hal_mspi_cq_disable':0x423fac,'opencfw_hal_mspi_cq_term':0x423f54,'opencfw_bl_mspi_cq_enable':0x423f8e,'opencfw_provider_427794':0x427794,'opencfw_provider_427878':0x427878,'opencfw_provider_4278c8':0x4278c8,'opencfw_provider_427ad6':0x427ad6,'update_indices':0x427754}
EVENTS={'opencfw_hal_mspi_cq_init':('cq-init',3),'opencfw_hal_mspi_cq_disable':('cq-disable',1),'opencfw_hal_mspi_cq_term':('cq-term',1),'opencfw_bl_mspi_cq_enable':('cq-enable',1)}
class Machine(p.Machine):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.queue_entries={name:(self.symbols[name]&~1) if self.source else pc for name,pc in EXTRA.items() if not self.source or name in self.symbols};self.actual_read.update(self.queue_entries.values())
 def code(self,uc,pc,size,user):
  for name,(event,count) in EVENTS.items():
   if pc==self.queue_entries[name]:self.boundary_events.append([event,*self.args()[:count]])
  # Bypass inherited exact-address CQ cuts, including the power profile's
  # enable cut. No stock instructions are copied into the source machine.
  if pc in self.queue_entries.values():
   assert any(lo<=pc<hi for lo,hi in self.exec_ranges)
   if not self.source:self.trace[hex(pc)]=bytes(uc.mem_read(pc,size)).hex()
   return
  super().code(uc,pc,size,user)
def main():
 s.Machine=Machine;s.main();out=Path(sys.argv[sys.argv.index('--output')+1]);r=json.loads(out.read_text());r['limits'][2]='Native NOR read/program/erase, transaction/HAL/FIFO, MSPI power, device configuration, clockgen, power domains and CQ init/enable/disable/term/generic queue bodies execute. MMIO/port completion and delay are synthetic; application image operations remain fixture byte callbacks. No physical persistence, timing or power-loss proof.';r['source_sha256'].update({str(x.relative_to(s.ROOT)):v.sha(x) for folder in ['nor_read','nor_write','nor_mspi_power','nor_mspi_queue','clock_manager','platform_control'] for x in (s.ROOT/'g2/components/bootloader'/folder).iterdir() if x.suffix in ['.c','.h']});out.write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
