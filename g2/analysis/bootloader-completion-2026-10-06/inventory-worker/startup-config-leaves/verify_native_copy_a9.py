import importlib.util,json,struct,hashlib
original_uc=None
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];p=ROOT/'g2/components/bootloader/initializer_callbacks/verify_context_interrupt.py';s=importlib.util.spec_from_file_location('base',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v);_,segs,syms=v.elf.elf_info(Path('/tmp/opencfw-startup-leaves.elf'))
original_uc=v.Uc
def oracle_uc(arch,mode):
 u=original_uc(arch,mode & ~v.UC_MODE_MCLASS);u.ctl_set_cpu_model(v.a.UC_CPU_ARM_CORTEX_A9);return u
v.Uc=oracle_uc
class M(v.Machine):
 def __init__(self,source):super().__init__(source,segs,syms);self.calls=[]
 def code(self,u,pc,n,z):
  slots={0x4216d4:4,0x4217d2:5,0x421978:6,0x08001000:4,0x08001010:5,0x08001020:6}
  if pc in slots:
   kind=slots[pc];self.calls.append([kind,u.reg_read(v.a.UC_ARM_REG_R0),u.reg_read(v.a.UC_ARM_REG_R1)]);u.reg_write(v.a.UC_ARM_REG_R0,0xa0000000|kind);u.reg_write(v.a.UC_ARM_REG_PC,u.reg_read(v.a.UC_ARM_REG_LR));return
  super().code(u,pc,n,z)
rows=[];trace={}
for name,entry,args in [('config_copy',0x422416,[p,0,0]) for p in [0,0x20001000,0x20001001]]+ [('config_dispatch',0x4222a0,[sel,0x12345678,0xabcdef01]) for sel in list(range(260))+[0xffffff04,0xffffffff]]:
 obs=[]
 for source in [False,True]:
  m=M(source);u=m.cpu;u.mem_write(0x20001000,bytes(range(64)));u.mem_write(0x20000070,bytes([0xa5])*64);u.reg_write(v.a.UC_ARM_REG_SP,v.SP);u.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
  for r,val in zip([v.a.UC_ARM_REG_R0,v.a.UC_ARM_REG_R1,v.a.UC_ARM_REG_R2],args):u.reg_write(r,val)
  u.emu_start((syms[name]&~1 if source else entry)|1,v.STOP+2,count=10000);assert m.done;obs.append({'return':u.reg_read(v.a.UC_ARM_REG_R0),'region':bytes(u.mem_read(0x20000070,64)).hex(),'calls':[x for x in m.calls if x[0]!='copy']});trace.update(m.trace)
 rows.append({'function':name,'arguments':args,'match':obs[0]==obs[1],'stock':obs[0],'source':obs[1]})
r={'status':'PASS' if all(x['match'] for x in rows) else 'COUNTEREXAMPLE','cases':len(rows),'original_sha256':hashlib.sha256(v.BLOB.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).with_name('leaves.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(Path('/tmp/opencfw-startup-leaves.elf').read_bytes()).hexdigest(),'comparisons':rows,'original_trace':{hex(p):b for p,b in trace.items()},'limits':['Original memcpy41568c executes natively under A9 instruction oracle; target M-profile model and hardware are not certified.','Three dispatcher children injected with argument/return checks; no MMIO or child behavior claimed.','Separate leaf module, not shared bootloader candidate; be4ede checkpoint preserved.']};Path(__file__).with_name('native-copy-a9.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],len(rows))
