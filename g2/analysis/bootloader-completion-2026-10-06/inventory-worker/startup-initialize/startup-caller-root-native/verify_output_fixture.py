import importlib.util,json,sys,hashlib
from pathlib import Path
p=Path('g2/components/bootloader/initializer_callbacks/verify_elog_output.py');s=importlib.util.spec_from_file_location('output',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.TIME=0x20026f18
old_code=m.Machine.code
def code(self,uc,pc,size,user):
 if self.source:
  for name,original in [('opencfw_boot_elog_snprintf',0x41b218),('opencfw_boot_elog_vsnprintf',0x41b25c)]:
   if pc==(self.symbols[name]&~1):pc=original;break
 return old_code(self,uc,pc,size,user)
m.Machine.code=code
m.main()
q=Path(sys.argv[sys.argv.index('--output')+1]);j=json.loads(q.read_text());j['fixture_adapter_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();j['fixture_correction']='Time metadata returns stock fixed buffer20026f18; source compiler may fold its returned pointer. Injected metadata still controls contents. Frozen runner unchanged. Relocated source snprintf/vsnprintf use the same explicit formatter fixture as stock; native wrapper behavior is covered separately by bounded-format and hybrid-core receipts.';q.write_text(json.dumps(j,indent=2)+'\n')
