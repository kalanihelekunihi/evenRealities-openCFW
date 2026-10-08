import importlib.util,json,struct,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];p=ROOT/'g2/components/bootloader/initializer_callbacks/verify_context_interrupt.py';s=importlib.util.spec_from_file_location('base',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v);_,segs,syms=v.elf.elf_info(Path('g2/build/bootloader-completion/source-image-compatible/snapshots/162b06837e95019d948c5e286c57188620ad1d032f1d7900e790ef1154dd280c/bootloader-source-test.elf'))
syms['config_copy']=syms['opencfw_boot_startup_clock_descriptor'];syms['config_dispatch']=syms['opencfw_boot_startup_clock_select']
class M(v.Machine):
 def __init__(self,source):super().__init__(source,segs,syms);self.calls=[]
 def code(self,u,pc,n,z):
  if pc==0x41568c:
   dst=u.reg_read(v.a.UC_ARM_REG_R0);src=u.reg_read(v.a.UC_ARM_REG_R1);size=u.reg_read(v.a.UC_ARM_REG_R2);self.calls.append(['copy',size]);u.mem_write(dst,bytes(u.mem_read(src,size)));u.reg_write(v.a.UC_ARM_REG_PC,u.reg_read(v.a.UC_ARM_REG_LR));return
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
 assert obs[0]==obs[1],(name,args,obs);rows.append({'function':name,'arguments':args,'result':obs[0]})
r={'status':'PASS','cases':len(rows),'original_sha256':hashlib.sha256(v.BLOB.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).with_name('leaves.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(Path('g2/build/bootloader-completion/source-image-compatible/snapshots/162b06837e95019d948c5e286c57188620ad1d032f1d7900e790ef1154dd280c/bootloader-source-test.elf').read_bytes()).hexdigest(),'comparisons':rows,'original_trace':{hex(p):b for p,b in trace.items()},'limits':['Original memcpy41568c modeled as exact synchronous byte copy; copy helper implementation not certified.','Three dispatcher children injected with argument/return checks; no MMIO or child behavior claimed.','Separate leaf module, not shared bootloader candidate; be4ede checkpoint preserved.']};Path(__file__).with_name('shared-162b.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows))
