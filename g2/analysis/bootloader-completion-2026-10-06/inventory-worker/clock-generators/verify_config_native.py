"""Native generators inside stock/source select5/6 callers; request/release cuts retained."""
from pathlib import Path
import hashlib,json,itertools
base=Path(__file__).resolve().parents[1]/'clock-config-children/verify.py'
code=base.read_text().split('fixtures=[]')[0]
code=code.replace('if pc==gen2:','if False and pc==gen2:').replace('if pc==gen6:','if False and pc==gen6:')
code=code.replace("self.cpu.hook_add(UC_HOOK_CODE,self.code)","self.cpu.mem_map(0xe000e000,0x1000);self.cpu.mem_write(0xe000ed88,(0xf00000).to_bytes(4,'little'));self.cpu.reg_write(a.UC_ARM_REG_C1_C0_2,0xf00000);self.cpu.reg_write(a.UC_ARM_REG_FPEXC,0x40000000);self.cpu.reg_write(a.UC_ARM_REG_FPSCR,0);self.cpu.hook_add(UC_HOOK_CODE,self.code)")
# Reuse exact original fixture definitions without running their stub suite.
exec(compile(code,str(base),'exec'))
rows=[];traces={}
for cls,ref1,ref2,value,users,irq in itertools.product([5,6],[12000000,24000000],[0],[0,196608000,250000000],[0,1],[0,1]):
 f=dict(cls=cls,value=value,mode=None,ref1=ref1,ref2=ref2,users=users,old=0,gen=0,drop=False,irq=irq)
 observed=[]
 for source in [False,True]:
  m=M(source,f);observed.append(m.run());traces.update(m.trace)
 assert observed[0]==observed[1],(f,observed)
 rows.append({'fixture':f,'result':observed[0]})
report={'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'base_runner_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'comparisons':rows,'original_trace':{hex(p):b for p,b in sorted(traces.items())},'limits':['CortexM33 native original and source class5/6 + complete generators/FP helpers. CPACR/FPEXC enabled; FPSCR starts0. No generator answer models.','Request/release side effects retain identical cuts; no live scheduling, hardware clock lock/timing or byte equality. Original copy executes with MMIO-only recording.']}
args.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(rows))
