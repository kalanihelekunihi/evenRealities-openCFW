from pathlib import Path
import json,hashlib,struct,itertools,argparse
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn import arm_const as a
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());b=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=Path('/tmp/opencfw-iar-integer.elf'));args=ap.parse_args()
with args.elf.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
visited={0:set(),1:set()}
def run(stock,length,signed,align,words,mask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for p,n in [(0x410000,0x30000),(0x70000,0x10000),(0x8000000,4096),(0x20000000,0x40000)]:u.mem_map(p,n)
 if stock:u.mem_write(0x410000,b)
 else:
  for p,data in segs:u.mem_write(p,data)
 SP=0x2003e000;CUR=0x20002000;WORDS=0x20003000+align;OUT=0x20004000
 u.mem_write(CUR,struct.pack('<I',WORDS));u.mem_write(0x20003000,struct.pack('<IIII',*[x&0xffffffff for x in words]));u.mem_write(SP,b'\xa5'*192)
 u.reg_write(a.UC_ARM_REG_SP,SP);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_PRIMASK,mask)
 if stock:u.reg_write(a.UC_ARM_REG_R9,CUR);u.mem_write(SP+0x42,bytes([length]))
 else:
  for reg,val in [(a.UC_ARM_REG_R0,CUR),(a.UC_ARM_REG_R1,length),(a.UC_ARM_REG_R2,signed),(a.UC_ARM_REG_R3,OUT)]:u.reg_write(reg,val)
 start,end=(0x41f022,0x41f088) if signed else (0x41ef8c,0x41eff2);done=[False]
 def hook(cpu,pc,size,_):
  if pc==(end if stock else 0x8000000):done[0]=True;cpu.emu_stop();return
  if stock:assert start<=pc<end,hex(pc);visited[signed].update(range(pc,pc+size))
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((start if stock else sy['opencfw_format_integer_fetch'])|1,0,count=1000);assert done[0]
 return {'value_words':list(struct.unpack('<II',u.mem_read(SP+8 if stock else OUT,8))),'consumed_bytes':struct.unpack('<I',u.mem_read(CUR,4))[0]-WORDS,'mask':u.reg_read(a.UC_ARM_REG_PRIMASK),'caller_words':bytes(u.mem_read(0x20003000,16)).hex()}
rows=[]
for length,signed,align,words,mask in itertools.product([0,*map(ord,'bhjlqtzL')],[0,1],[0,4],[[0,0,0,0],[0xff,0xffff,0x80000000,0xffffffff],[0x80000000,0xffffffff,1,0],[0x7fffffff,0x12345678,0x89abcdef,0x80000000]],[0,1]):
 x=run(True,length,signed,align,words,mask);y=run(False,length,signed,align,words,mask);assert x==y,(length,signed,align,words,x,y);rows.append({'length':length,'signed':signed,'alignment_offset':align,'words':words,'mask':mask,'result':x})
r={'status':'PASS_ORIGINAL_INTEGER_CURSOR_FRAGMENTS','cases':len(rows),'original_sha256':hashlib.sha256(b).hexdigest(),'source_sha256':hashlib.sha256((N/'integer_cursor.c').read_bytes()).hexdigest(),'native_elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'fragments':[{'start':hex(lo),'end':hex(hi),'bytes':hi-lo,'visited':len(visited[k]),'sha256':hashlib.sha256(b[lo-0x410000:hi-0x410000]).hexdigest()} for k,lo,hi in [(0,0x41ef8c,0x41eff2),(1,0x41f022,0x41f088)]],'results':rows,'limits':['Fragment boundary entry with synthetic stack/cursor state; no stubbed children or original image loaded on C side.','Independent helper for future source engine. Not an independent original function, not linked into229 candidate, and not counted as full source-owned engine bytes. Integer rendering, sign-prefix construction, precision/padding and all floating/secure paths remain separate.']}
(N/'integer-cursor-comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'],r['fragments'])
