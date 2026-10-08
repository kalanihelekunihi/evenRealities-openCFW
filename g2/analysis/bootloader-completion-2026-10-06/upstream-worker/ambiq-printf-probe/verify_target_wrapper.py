import argparse,importlib.util,json,struct,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];p=ROOT/'g2/components/bootloader/initializer_callbacks/verify_context_interrupt.py';s=importlib.util.spec_from_file_location('base',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v);old=v.Uc
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=Path('/tmp/opencfw-plain-printf.elf'));ap.add_argument('--output',type=Path,default=Path(__file__).with_name('target-wrapper.json'));arg=ap.parse_args();_,segs,syms=v.elf.elf_info(arg.elf)
def oracle(arch,mode):
 u=old(arch,mode & ~v.UC_MODE_MCLASS);u.ctl_set_cpu_model(v.a.UC_CPU_ARM_CORTEX_A9);u.reg_write(v.a.UC_ARM_REG_C1_C0_2,0xf<<20);u.reg_write(v.a.UC_ARM_REG_FPEXC,0x40000000);u.reg_write(v.a.UC_ARM_REG_FPSCR,0);return u
v.Uc=oracle
class M(v.Machine):
 def __init__(self,source):super().__init__(source,segs,syms);self.events=[]
 def code(self,u,pc,n,z):
  if pc==0x08000100:
   ptr=u.reg_read(v.a.UC_ARM_REG_R0);self.events.append(bytes(u.mem_read(ptr,512)).split(b'\0')[0].hex());u.reg_write(v.a.UC_ARM_REG_PC,u.reg_read(v.a.UC_ARM_REG_LR));return
  super().code(u,pc,n,z)
cases=[(fmt,value,prefix) for fmt in ['%f','%.0f','%.2f','%.6f'] for value in [1.25,-1.25,0.,-0.,1.363995,1.996,math.inf,-math.inf,math.nan] for prefix in [False,True]];rows=[]
for enabled in [False,True]:
 for translated in [False,True]:
  for fmt,value,prefix in cases:
   form=('%d:'+fmt) if prefix else fmt;obs=[]
   for source in [False,True]:
    m=M(source);u=m.cpu;u.mem_write(0x200270cc,struct.pack('<I',0x08000101 if enabled else 0));u.mem_write(0x200271c4,bytes([translated]));u.mem_write(0x20001000,form.encode()+b'\0');u.reg_write(v.a.UC_ARM_REG_SP,v.SP);u.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1);u.reg_write(v.a.UC_ARM_REG_R0,0x20001000);u.reg_write(v.a.UC_ARM_REG_R1,7 if prefix else 0);bits=int.from_bytes(struct.pack('<d',value),'little');u.reg_write(v.a.UC_ARM_REG_R2,bits&0xffffffff);u.reg_write(v.a.UC_ARM_REG_R3,bits>>32);u.emu_start((syms['opencfw_boot_plain_printf']&~1 if source else 0x415fae)|1,v.STOP+2,count=300000);assert m.done;obs.append({'return':u.reg_read(v.a.UC_ARM_REG_R0),'events':m.events})
   assert obs[0]==obs[1],(form,value,obs);rows.append({'enabled':enabled,'translation':translated,'format':form,'value':repr(value),'result':obs[0]})
r={'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(arg.elf.read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'comparisons':rows,'limits':['Actual original and compiled ARM wrapper/parser instructions under A9 FP64 oracle. Synthetic synchronous sink only; no expected formatter output injected.','Default FPSCR, no task/IRQ/reentrancy/drain/hardware or large-output safety proof.']};arg.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows))
