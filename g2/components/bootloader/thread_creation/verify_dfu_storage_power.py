#!/usr/bin/env python3
"""Reset/NOR profile additionally executes native MSPI power + power domains."""
import importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('nor_profile',HERE/'verify_dfu_storage_nor.py');n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n);s=n.s;v=n.v
EXTRA={'opencfw_bl_power_control':0x426808,'opencfw_bl_mspi_mode_enter':0x41bf84,'opencfw_bl_mspi_mode_leave':0x41c17a,'opencfw_bl_clock_release_all':0x4223d8,'opencfw_boot_power_release_needed':0x41c0be,'opencfw_boot_power_callback':0x41cd1a,'opencfw_boot_power_hook_begin':0x41cd34,'opencfw_boot_power_hook_end':0x41cd4a,'opencfw_boot_control_query_descriptor_copy':0x41b8f8,'opencfw_hal_mspi_device_configure':0x424be4,'opencfw_bl_mspi_clockgen_control':0x4249a0,'opencfw_bl_mspi_device_configure_private':0x424120,'opencfw_bl_mspi_get_xip_off_min_delay':0x424a18}
class Machine(n.Machine):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.actual_read.update((self.symbols[name]&~1) if self.source else pc for name,pc in EXTRA.items() if not self.source or name in self.symbols);self.cpu.mem_map(0x400c1000,0x1000);self.cpu.mem_map(0x40014000,0x1000);self.cpu.mem_map(0x40004000,0x1000)
 def code(self,uc,pc,size,user):
  if pc==0x423f8e:self.boundary_events.append(['cq-enable',self.args()[0]]);self.ret();return
  if pc==0x41bae8:raise AssertionError('selector20 special power mode not closed')
  super().code(uc,pc,size,user)
def main():
 s.Machine=Machine;s.main();out=Path(sys.argv[sys.argv.index('--output')+1]);r=json.loads(out.read_text());r['limits'][2]='Native NOR read/program/erase/local transaction/HAL/FIFO plus MSPI power save/restore, power-domain enable/disable and clock release-all execute. Synthetic NOR-backed ports deliver reads and apply WREN/WRDI/erase/program with1-to0 checks. Device configure, clockgen/CQ callbacks, delay and hardware acknowledgement remain modeled; application image operations remain byte callbacks.';r['source_sha256'].update({str(p.relative_to(s.ROOT)):v.sha(p) for folder in ['nor_read','nor_write','nor_mspi_power','clock_manager','platform_control'] for p in (s.ROOT/'g2/components/bootloader'/folder).iterdir() if p.suffix in ['.c','.h']});out.write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
