import importlib.util,sys
from pathlib import Path
p=Path('g2/components/bootloader/initializer_callbacks/verify_elog_setters.py').resolve();s=importlib.util.spec_from_file_location('settercheck',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
old=m.Machine.code
def code(self,uc,pc,size,user):
 if self.source and pc==(self.symbols.get('opencfw_boot_elog_output',0)&~1):pc=0x4176ce
 return old(self,uc,pc,size,user)
m.Machine.code=code;m.main()
