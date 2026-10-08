from pathlib import Path
import json,hashlib,struct,itertools,argparse
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn import arm_const as a
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());b=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=Path('/tmp/opencfw-iar-parser.elf'));args=ap.parse_args()
with args.elf.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
vis=set();helpers=set()
def run(stock,fmt,words,mask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for p,n in [(0x410000,0x30000),(0x70000,0x10000),(0x8000000,4096),(0x20000000,0x40000)]:u.mem_map(p,n)
 if stock:u.mem_write(0x410000,b)
 else:
  for p,data in segs:u.mem_write(p,data)
 SP=0x2003e000;FMT=0x20001000;CUR=0x20002000;WORDS=0x20003000;OUT=0x20004000
 u.mem_write(FMT,fmt.encode()+b'\0');u.mem_write(CUR,struct.pack('<I',WORDS));u.mem_write(WORDS,struct.pack('<II',*[x&0xffffffff for x in words]));u.mem_write(SP,b'\xa5'*192)
 u.reg_write(a.UC_ARM_REG_SP,SP);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_PRIMASK,mask)
 if stock:u.reg_write(a.UC_ARM_REG_R10,FMT);u.reg_write(a.UC_ARM_REG_R9,CUR)
 else:
  for reg,val in [(a.UC_ARM_REG_R0,FMT),(a.UC_ARM_REG_R1,CUR),(a.UC_ARM_REG_R2,OUT)]:u.reg_write(reg,val)
 done=[False]
 def hook(cpu,pc,size,_):
  if pc==(0x41e5fa if stock else 0x8000000):done[0]=True;cpu.emu_stop();return
  if stock:
   if 0x41e4b6<=pc<0x41e5fa:vis.update(range(pc,pc+size))
   elif 0x417c64<=pc<0x417d00:helpers.add(pc)
   else:raise AssertionError(('unexpected original parser PC',hex(pc)))
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x41e4b6 if stock else sy['opencfw_format_parse'])|1,0,count=20000);assert done[0]
 rd=lambda p:struct.unpack('<I',u.mem_read(p,4))[0]
 if stock:out=[int.from_bytes(u.mem_read(SP+0x40,2),'little'),rd(SP+0x3c),rd(SP+0x38),u.mem_read(SP+0x42,1)[0],u.mem_read(u.reg_read(a.UC_ARM_REG_R10),1)[0]];end=u.reg_read(a.UC_ARM_REG_R10)
 else:out=list(struct.unpack('<IIIII',u.mem_read(OUT,20)));end=u.reg_read(a.UC_ARM_REG_R0)
 return {'spec':out,'format_offset':end-FMT,'consumed_words':(rd(CUR)-WORDS)//4,'mask':u.reg_read(a.UC_ARM_REG_PRIMASK),'caller_words':bytes(u.mem_read(WORDS,8)).hex()}
formats=['%'+fl+w+pr+ln+'d' for fl,w,pr,ln in itertools.product(['',' +#-0','000','++  '],['','1','2147483639','999999999999','*'],['','.0','.12','.-42','.*'],['','h','hh','l','ll','j','t','z','L'])]
formats+=['%','%.','%ll','%*.*s','%+#00012.0003llx','%2147483638.2147483638d','%2147483649d']
rows=[]
# Exhaust syntax axes once; star edge values and interrupt masks separately.
fixtures=[(f,[-12,7],0) for f in formats]+[(f,words,m) for f,words,m in itertools.product(['%*d','%.*d','%*.*d'],[[0,0],[1,1],[-1,-1],[0x80000000,0x80000000],[0x7fffffff,0x7fffffff]],[0,1])]
for fmt,words,mask in fixtures:
 x=run(True,fmt,words,mask);y=run(False,fmt,words,mask)
 assert x==y,(fmt,words,mask,x,y)
 rows.append({'format':fmt,'words':words,'mask':mask,'result':x})
r={'status':'PASS_ORIGINAL_PARSER_FRAGMENT','cases':len(rows),'original_sha256':hashlib.sha256(b).hexdigest(),'fragment':{'start':'0x41e4b6','end':'0x41e5fa','bytes':324,'visited_bytes':len(vis),'unvisited':[hex(x) for x in sorted(set(range(0x41e4b6,0x41e5fa))-vis)],'sha256':hashlib.sha256(b[0xe4b6:0xe5fa]).hexdigest()},'native_elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((N/'format_parser.c').read_bytes()).hexdigest(),'original_helper_pcs':[hex(x) for x in sorted(helpers)],'results':rows,'limits':['Original fragment is entered at its parser boundary with synthetic stack and cursor state; this is not an independent original function or source-owned full-engine extent.','Original strchr helper executes authenticated instructions; no external-call stubs. Source side loads only compiled parser ELF.','Conversion execution, callback lifetime/error handling, integer rendering, floating rendering and secure flag semantics remain outside this parser comparison. No integration candidate change.']}
(N/'comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'],r['fragment'])
