#!/usr/bin/env python3
"""Queue image additionally executes actual cache-maintenance wrapper41e348."""
import importlib.util,json,sys,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('queue_profile',HERE/'verify_dfu_storage_queue.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q);s=q.s;v=q.v
class Machine(q.Machine):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.cache_entry=(self.symbols['opencfw_boot_cache_maintain']&~1) if self.source else 0x41e348;self.actual_read.add(self.cache_entry)
 def code(self,uc,pc,size,user):
  if pc==self.application_reset:self.boundary_events.append(['application-page-sha256',hashlib.sha256(uc.mem_read(0x438000,4096)).hexdigest()])
  if pc==self.cache_entry:self.boundary_events.append(['runtime-update',*self.args()[:2]])
  super().code(uc,pc,size,user)
def main():
 s.Machine=Machine;s.main();out=Path(sys.argv[sys.argv.index('--output')+1]);r=json.loads(out.read_text());r['limits'][3]='Platform descriptor/application byte callbacks remain fixtures pending recovered descriptor integration; filesystem mutex providers and delays synthetic. Runtime cache-maintenance body executes with modeled SCB registers, no physical coherence claim. Filesystem logger adapter omitted; task DFU log level/line retained.';r['source_sha256'].update({str(x.relative_to(s.ROOT)):v.sha(x) for folder in ['nor_read','nor_write','nor_mspi_power','nor_mspi_queue','clock_manager','platform_control'] for x in (s.ROOT/'g2/components/bootloader'/folder).iterdir() if x.suffix in ['.c','.h']});out.write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
