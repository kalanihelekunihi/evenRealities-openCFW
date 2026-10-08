import argparse,hashlib,importlib.util,itertools,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[5];p=ROOT/'g2/components/bootloader/update_core/elf_reader.py';s=importlib.util.spec_from_file_location('elfread',p);elf=importlib.util.module_from_spec(s);s.loader.exec_module(elf)
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=Path('/tmp/opencfw-clock-config.elf'));ap.add_argument('--output',type=Path,default=Path(__file__).with_name('comparison.json'));args=ap.parse_args();_,segments,symbols=elf.elf_info(args.elf);BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';raw=BLOB.read_bytes();assert hashlib.sha256(raw).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
NAMES={4:'opencfw_boot_startup_select4',5:'opencfw_boot_startup_select5',6:'opencfw_boot_startup_select6'};ENTRIES={4:0x4216d4,5:0x4217d2,6:0x421978};SP=0x2002f000;STOP=0x08000000
class M:
 def __init__(self,source,fixture):
  self.source=source;self.f=fixture;self.cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33);self.cpu.mem_map(0x410000,0x25000);self.cpu.mem_map(0x20000000,0x40000);self.cpu.mem_map(0x40000000,0x100000);self.cpu.mem_map(STOP,0x10000);self.trace={};self.calls=[];self.writes=[];self.done=False
  if source:
   for x in segments:
    lo=x['address']&~4095;hi=(x['address']+len(x['data'])+4095)&~4095
    if not(0x410000<=lo<0x435000 or 0x20000000<=lo<0x20040000 or STOP<=lo<STOP+0x10000):self.cpu.mem_map(lo,hi-lo)
    self.cpu.mem_write(x['address'],x['data'])
  else:self.cpu.mem_write(0x410000,raw)
  self.cpu.hook_add(UC_HOOK_CODE,self.code)
  # Recorder needs only MMIO; a global no-op SRAM write hook corrupts
  # original conditional-copy execution in Unicorn2.1.x. No answer model.
  self.cpu.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=0x40000000,end=0x400fffff)
 def u(self,p):return int.from_bytes(self.cpu.mem_read(p,4),'little')
 def w(self,p,x):self.cpu.mem_write(p,struct.pack('<I',x))
 def ret(self,x):self.cpu.reg_write(a.UC_ARM_REG_R0,x);self.cpu.reg_write(a.UC_ARM_REG_PC,self.cpu.reg_read(a.UC_ARM_REG_LR))
 def write(self,u,access,p,size,val,z):self.writes.append([p,size,val&((1<<(size*8))-1)])
 def code(self,u,pc,n,z):
  if pc==STOP:self.done=True;u.emu_stop();return
  vals=[u.reg_read(r) for r in [a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3]]
  gen2=(symbols.get('opencfw_boot_startup_hf2_generate',0)&~1) if self.source else 0x426c24
  gen6=(symbols.get('opencfw_boot_startup_pll_generate',0)&~1) if self.source else 0x427160
  if pc==gen2:
   self.calls.append(['generate-hf2',*vals[:3]]);self.w(vals[3],0x12345678);self.ret(self.f['gen']);return
  if pc==gen6:
   self.calls.append(['generate-pll',vals[1],vals[2],self.cpu.mem_read(vals[0],1)[0]]);mode=self.cpu.mem_read(vals[0],1)[0];self.cpu.mem_write(vals[0],bytes([mode,2,3,4])+bytes.fromhex('7856341200000000'));self.ret(self.f['gen']);return
  for name,stock,label in [('opencfw_bl_clock_request_id2',0x421bd2,'request2'),('opencfw_bl_clock_request_id3',0x421b08,'request3'),('opencfw_bl_clock_release_id2',0x421cce,'release2'),('opencfw_bl_clock_release_id3',0x421b5c,'release3')]:
   entry=(symbols[name]&~1) if self.source else stock
   if pc==entry:
    self.calls.append([label,vals[0]])
    if label.startswith('request') and self.f['drop']:self.w(0x20026e9c,0);self.w(0x20026ea0,0)
    self.ret(0xabcdef01);return
  if not self.source:self.trace[pc]=bytes(u.mem_read(pc,n)).hex()
 def run(self):
  f=self.f;self.cpu.mem_write(0x20026fec,bytes([0xa5])*40);self.cpu.mem_write(0x20027030,struct.pack('<III',f['old'],f['old'],f['old']));self.cpu.mem_write(0x20000550,bytes([0xa5])*2);self.cpu.mem_write(0x20027198,bytes([0xa5])*8);self.w(0x20027044,0x12345678)
  self.cpu.mem_write(0x2000007c,struct.pack('<IIIII',0,f['ref1'],0,f.get('ref4',32768),f['ref2']))
  for cls in [4,5,6]:self.w(0x20026e74+cls*8,f['users']);self.w(0x20026e78+cls*8,0)
  for p in [0x40004020,0x40004048,0x4000404c,0x40004050]:self.w(p,0xa5a5a5a5)
  inp=0 if f['mode'] is None else 0x20001000
  if inp:self.cpu.mem_write(inp,bytes([f['mode'],2,0x55,0])+struct.pack('<II',0x01234567,0x89abcdef))
  u=self.cpu;u.reg_write(a.UC_ARM_REG_XPSR,0x01000000);u.reg_write(a.UC_ARM_REG_SP,SP);u.reg_write(a.UC_ARM_REG_LR,STOP|1);u.reg_write(a.UC_ARM_REG_R0,f['value']);u.reg_write(a.UC_ARM_REG_R1,inp);u.reg_write(a.UC_ARM_REG_PRIMASK,f['irq']);u.emu_start((symbols[NAMES[f['cls']]]&~1 if self.source else ENTRIES[f['cls']])|1,STOP+2,count=100000);assert self.done,(self.source,f,hex(u.reg_read(a.UC_ARM_REG_PC)))
  return {'return':u.reg_read(a.UC_ARM_REG_R0),'irq':u.reg_read(a.UC_ARM_REG_PRIMASK),'calls':self.calls,'writes':self.writes,'config_state':bytes(u.mem_read(0x20026fec,80)).hex(),'values':bytes(u.mem_read(0x20027030,28)).hex(),'flags':bytes(u.mem_read(0x20000550,2)).hex(),'active':bytes(u.mem_read(0x20027198,8)).hex(),'registers':[self.u(p) for p in [0x40004020,0x40004048,0x4000404c,0x40004050]]}
fixtures=[]
for cls,values in [(4,[0,48000000,48000001]),(5,[0,196608000,250000000,1]),(6,[0,123456789])]:
 for value,mode,refs,users,old,gen,drop,irq in itertools.product(values,[None,0,1,2],[(0,0),(32768,0),(0,24000000),(32768,24000000)],[0,1],[0,48000000,196608000,250000000], [0,5],[False,True],[0,1]):
  if cls!=5 and drop:continue
  if cls==4 and gen:continue
  fixtures.append(dict(cls=cls,value=value,mode=mode,ref1=refs[0],ref2=refs[1],users=users,old=old,gen=gen,drop=drop,irq=irq))
fixtures += [dict(cls=4,value=48000000,mode=None,ref1=0,ref2=0,ref4=0,users=u,old=o,gen=0,drop=False,irq=i) for u,o,i in itertools.product([0,1],[0,48000000],[0,1])]
rows=[];trace={}
for f in fixtures:
 obs=[]
 for source in [False,True]:m=M(source,f);obs.append(m.run());trace.update(m.trace)
 assert obs[0]==obs[1],(f,obs);rows.append({'fixture':f,'result':obs[0]})
control=dict(cls=4,value=48000000,mode=0,ref1=0,ref2=0,users=0,old=0,gen=0,drop=False,irq=0)
stock=M(False,control).run();changed=dict(control,value=48000001);different=M(True,changed).run();assert stock!=different
r={'negative_controls':{'changed_argument_rejected':stock!=different},'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((ROOT/'g2/components/bootloader/initializer_callbacks/startup_clock_config.c').read_bytes()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'comparisons':rows,'original_trace':{hex(p):b for p,b in trace.items()},'limits':['Two config generators and request/release side effects injected equally; hot request may synthetically clear class5 users. Not their child implementation or live scheduling proof.','Original critical/count/copy and HFADJ/HF2 register children execute; recorder scoped to MMIO so no SRAM-hook copy corruption or expected-copy stub.','Native source uses only ELF executable bytes. Synthetic coherent SRAM/MMIO, no hardware timing/drain or byte equality.']};args.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows))
