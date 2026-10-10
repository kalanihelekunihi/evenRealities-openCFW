from pathlib import Path
import hashlib,json,struct,itertools,random
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent; R=D.parents[2]
stock=(R/'g2/build/pseudocode-first/20260930T190500Z/attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with (D/'runtime.elf').open('rb') as f:
 e=ELFFile(f);symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
P=0x20001000;Q=P+0x200;S=P+0x400;CB=0x100f00;STOP=0x100f80
counts={};coverage={}
def run(name,addr,args,data,callback=None,zero=False):
 vals=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(stock)+4095)&~4095);u.mem_write(0x438000,stock);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x10000)
  for a,b in segments:u.mem_write(a,bytes(b))
  for a,b in data:u.mem_write(a,bytes(b))
  trace=[];seen=set()
  def hook(u,a,n,_):
   if a==CB:
    av=tuple(u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2));trace.append(av);ret=callback(av,len(trace));u.reg_write(UC_ARM_REG_R0,ret&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   elif a==STOP:u.emu_stop()
   elif original:seen.add(a)
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,val&0xffffffff)
  if zero:u.reg_write(UC_ARM_REG_R9,args[1])
  u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
  u.emu_start((addr if original else symbols[name])|1,STOP,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==STOP
  ret=u.reg_read(UC_ARM_REG_R0) if name!='g2_ungetn' else None
  vals.append((ret,bytes(u.mem_read(P,0x800)),trace))
  if original:coverage.setdefault(name,set()).update(seen)
 assert vals[0]==vals[1],(name,args,vals[0][0],vals[1][0])
 counts[name]=counts.get(name,0)+1
for c in range(-256,768):run('g2_isxdigit',0x595984,[c],[])
strings=[b'',b'a',b'abc',b'aaaa',bytes([128,255,65]),b'abcabc']
for s,t in itertools.product(strings,repeat=2):
 data=[(P,s+b'\0'),(Q,t+b'\0')]
 for name,addr in [('g2_strcat',0x567c80),('g2_strcspn',0x541b30),('g2_strspn',0x541b52)]:run(name,addr,[P,Q],data)
for s,c in itertools.product(strings,range(256)):run('g2_strrchr',0x567c64,[P,c],[(P,s+b'\0')])
for p in [b'',b'a',b'ab',b'a-z',b'z-a',b'a-z0-9',b'-a-',bytes([128,45,255]),b'ab-c-']:
 for c in range(256):run('g2_ranmatch',0x4d2112,[P,c,len(p)],[(P,p)])
for width,consumed in itertools.product([0,1,2,0x80000000,0xffffffff],[0,1,0xffffffff]):
 data=[(P,struct.pack('<5I',123,17,19,consumed,width))]
 run('g2_getn',0x4d15fa,[CB|1,P],data,lambda a,n:0xffffffff if a[0]==123 else 0)
 for c in [-1,0,255]:run('g2_ungetn',0x4d161c,[CB|1,P,c],data,lambda a,n:77)
for n,fail,count in itertools.product([0,1,2,8],[0,1,3],[0,0xffffffff]):
 state=bytearray(48);struct.pack_into('<I',state,8,123);struct.pack_into('<I',state,44,count)
 run('g2_putchars',0x482684,[CB|1,P,Q,n],[(P,state),(Q,b'abcdefgh')],lambda a,i:0 if i==fail else a[0]+1)
for n,flag in itertools.product(range(4,65),[0,1]):
 base=Q if flag else 0;dst=1 if flag else Q
 run('g2_zero_init3',0x5fa01e,[P,base],[(P,struct.pack('<3I',n,dst,0)),(Q,b'\xa5'*128)],zero=True)
result={'status':'PASS','cases':sum(counts.values()),'cases_by_body':counts,'stock_sha256':hashlib.sha256(stock).hexdigest(),'elf_sha256':hashlib.sha256((D/'runtime.elf').read_bytes()).hexdigest(),'original_instruction_addresses_visited':{k:len(v) for k,v in coverage.items()},'limits':['Unget void return intentionally excluded: stock EOF path leaves state pointer in r0.','Callbacks are controlled external contracts, not complete scanf or formatter integration.','Zero-init adapter binds r9 explicitly; tested descriptor lengths 4..64, direct and flagged destinations.','No hardware execution, original link layout, byte-identical C code, or whole-firmware completion claimed.']}
(D/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
