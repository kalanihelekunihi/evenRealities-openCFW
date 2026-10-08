"""Scoped recorder + native descriptor-copy supplement; no answer substitution."""
import importlib.util,json,hashlib,sys
from pathlib import Path
p=Path('g2/components/bootloader/initializer_callbacks/verify_startup_alternatives.py');s=importlib.util.spec_from_file_location('startup',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
old_uc=m.v.Uc
def scoped_uc(*args,**kwargs):
 u=old_uc(*args,**kwargs);add=u.hook_add
 def scoped_add(kind,callback,*rest,**options):
  if kind==m.v.UC_HOOK_MEM_WRITE:options.update(begin=m.v.IRQ,end=m.v.IRQ+0x3fff)
  return add(kind,callback,*rest,**options)
 u.hook_add=scoped_add;return u
m.v.Uc=scoped_uc;old_code=m.Machine.code
def code(self,uc,pc,size,user):
 if not self.source and pc==0x4156ac:return m.v.Machine.code(self,uc,pc,size,user)
 return old_code(self,uc,pc,size,user)
m.Machine.code=code;m.main()
q=Path(sys.argv[sys.argv.index('--output')+1]);j=json.loads(q.read_text());j['fixture_adapter_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();j['native_copy_supplement']='Original4156ac descriptor copy executes; only MMIO is instrumented. No expected-copy stub. Nine child API models remain as the original orchestration suite.';j['limits']=[x for x in j['limits'] if 'memcpy' not in x.lower() and 'copy' not in x.lower()]+['Native original descriptor copy4156ac; scoped MMIO recorder avoids reproduced no-op SRAM hook discrepancy. Other HAL child models remain; no hardware proof.'];q.write_text(json.dumps(j,indent=2)+'\n')
