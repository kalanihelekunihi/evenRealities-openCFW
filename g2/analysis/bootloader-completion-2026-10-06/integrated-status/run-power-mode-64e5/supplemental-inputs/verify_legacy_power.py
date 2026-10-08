"""Historical power-domain API-cut regression, remapped to current source PCs."""
from pathlib import Path
import importlib.util,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[5];p=ROOT/'g2/components/bootloader/platform_control/verify_power_domains.py';sp=importlib.util.spec_from_file_location('power',p);power=importlib.util.module_from_spec(sp);sp.loader.exec_module(power);original=power.Machine.code
CUTS={'opencfw_boot_control_critical_save':0x41b8ec,'opencfw_hal_status_poll':0x41d246,'opencfw_boot_control_delay_status_change':0x41d21c,'opencfw_hal_delay_us':0x41d1c0,'opencfw_boot_power_special_mode':0x41bae8,'opencfw_bl_clock_release_all':0x4223d8,'clock_request':0x4222f0,'clock_release':0x422364}
def code(self,uc,pc,size,user):
 if self.source:
  for symbol,canonical in CUTS.items():
   if pc==(self.symbols[symbol]&~1):original(self,uc,canonical,size,user);return
 original(self,uc,pc,size,user)
power.Machine.code=code
if __name__=='__main__':
 power.main();out=Path(sys.argv[sys.argv.index('--output')+1]);d=json.loads(out.read_text());d['fixture_adapter_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();d['limits'].append('Legacy API cuts remapped to native source PCs. Special-mode and clocks are intentionally controlled in this suite; native1394+selector20 native256 suites establish new special body separately.');out.write_text(json.dumps(d,indent=2)+'\n')
