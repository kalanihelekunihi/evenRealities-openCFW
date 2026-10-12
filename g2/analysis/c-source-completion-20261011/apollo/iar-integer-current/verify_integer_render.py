from pathlib import Path
import json,hashlib,struct,itertools,argparse
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn import arm_const as a
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());b=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=Path('/tmp/opencfw-iar-render.elf'));args=ap.parse_args()
with args.elf.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
import random
visited=set();helpers=set()
def run(stock,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for p,n in [(0x410000,0x30000),(0x70000,0x10000),(0x8000000,4096),(0x20000000,0x40000)]:u.mem_map(p,n)
 if stock:u.mem_write(0x410000,b)
 else:
  for p,data in segs:u.mem_write(p,data)
 SP=0x2003e000;REC=0x20002000;BUF=0x20003000
 record=[f['low'],f['high'],0x12345678,BUF+f['prefix'],BUF,f['prefix'],0,0,0,0,0,0,f['precision']&0xffffffff,f['width']&0xffffffff,f['flags']|0x77880000]
 u.mem_write(REC,struct.pack('<15I',*record));u.mem_write(BUF,b'\xa5'*80)
 for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xaac000+i)
 for reg,val in [(a.UC_ARM_REG_R0,REC),(a.UC_ARM_REG_R1,ord(f['conversion'])),(a.UC_ARM_REG_R2,0x11223344),(a.UC_ARM_REG_R3,0xaabbccdd),(a.UC_ARM_REG_SP,SP),(a.UC_ARM_REG_LR,0x8000001),(a.UC_ARM_REG_PRIMASK,f['mask'])]:u.reg_write(reg,val)
 done=[False]
 def hook(cpu,pc,size,_):
  if pc==0x8000000:done[0]=True;cpu.emu_stop();return
  if stock:
   assert 0x410000<=pc<0x435000,hex(pc)
   if 0x41f15c<=pc<0x41f270:visited.update(range(pc,pc+size))
   else:helpers.add(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x41f15c if stock else sy['opencfw_format_integer_render'])|1,0,count=100000);assert done[0]
 return {'record':bytes(u.mem_read(REC,60)).hex(),'scratch':bytes(u.mem_read(BUF,80)).hex(),'returns':[u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)],'saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],'sp':u.reg_read(a.UC_ARM_REG_SP),'mask':u.reg_read(a.UC_ARM_REG_PRIMASK)}
random.seed(41715);rows=[]
values=[(0,0),(1,0),(0xffffffff,0),(0,1),(0xffffffff,0xffffffff),(0,0x80000000),(0x89abcdef,0x12345678),(0xffffffff,0x7fffffff)]
fixtures=[]
for conversion,flags,precision,(low,high) in itertools.product('diuoxX',[0,8,16,20,24,31],[-1,0,1,20],values):fixtures.append(dict(conversion=conversion,low=low,high=high,flags=flags,precision=precision,width=80,prefix=2,mask=0))
for _ in range(150):fixtures.append(dict(conversion=random.choice('diuoxX'),low=random.getrandbits(32),high=random.getrandbits(32),flags=random.choice([0,8,16,20,24,31]),precision=random.choice([-7,-1,0,1,60,0x7fffffff]),width=random.choice([-1,0,1,20,80,0x7fffffff]),prefix=random.choice([0,1,4,59,60]),mask=random.randrange(2)))
for f in fixtures:
 x=run(True,f);y=run(False,f);assert x==y,(f,x,y);rows.append({'fixture':f,'result':x})
r={'status':'PASS_ORIGINAL_INTEGER_RENDER_HELPER','cases':len(rows),'original_sha256':hashlib.sha256(b).hexdigest(),'body':{'start':'0x41f15c','end':'0x41f270','bytes':276,'visited':len(visited),'unvisited':[hex(x) for x in sorted(set(range(0x41f15c,0x41f270))-visited)],'sha256':hashlib.sha256(b[0xf15c:0xf270]).hexdigest()},'source_sha256':hashlib.sha256((N/'integer_render.c').read_bytes()).hexdigest(),'native_elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'original_helper_pcs':[hex(x) for x in sorted(helpers)],'results':rows,'limits':['Full original helper plus real lowercase/division callees on stock side; source side only independent C ELF, no child stubs.','Synthetic parser record/buffer fixtures. Not linked into229 candidate; full-engine dispatch/callback/float/secure conversion behavior remains unclosed.']}
(N/'integer-render-comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'],r['body'])
