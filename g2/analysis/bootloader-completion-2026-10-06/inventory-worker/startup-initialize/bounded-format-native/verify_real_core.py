from pathlib import Path
import json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import *
import unicorn.arm_const as a
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());c=json.loads((N/'current-candidate.json').read_text());elf=R/c['directory']/'candidate.elf';blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5';assert hashlib.sha256(elf.read_bytes()).hexdigest()==c['sha256']
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(int(s['p_vaddr']),s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:int(s['st_value']) for s in e.get_section_by_name('.symtab').iter_symbols()}
original_oracle_visits=set()
extents={'snprintf':(0x41b218,0x41b256),'vsnprintf':(0x41b25c,0x41b292),'writer':(0x415672,0x41568c)};visited={k:set() for k in extents}
def run(stock,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for address,size in [(0,4096),(0x10000,65536),(0x30000,65536),(0x50000,65536),(0x410000,0x30000),(0x20000000,0x40000),(0x8000000,0x3000)]:u.mem_map(address,size)
 u.mem_write(0x410000,blob)
 if not stock:
  for address,data in segments:u.mem_write(address,data)
 def w(p,v):u.mem_write(p,struct.pack('<I',v&0xffffffff))
 def rd(p):return struct.unpack('<I',u.mem_read(p,4))[0]
 stop=0x8000000;resume=0x8000010;u.mem_write(stop,b"\x00\xbf\xfe\xe7");u.mem_write(resume,b"\x00\xbf\xfe\xe7");dst=0x20002000;fmt=0x20003000;ap=0x20010000;sp=0x2003f000;u.mem_write(dst,bytes([0xaa])*512);u.mem_write(fmt,f['format'].encode()+b'\0');args=f['arg_words']+[0]*(6-len(f['arg_words']));u.mem_write(0x20011000,b'hello-boundary\0')
 for i,v in enumerate(args):w(ap+i*4,v)
 w(sp,args[1]);w(sp+4,args[2]);w(sp+8,args[3]);w(sp+12,args[4]);w(sp+16,args[5])
 for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xaac000+i)
 u.reg_write(a.UC_ARM_REG_SP,sp);u.reg_write(a.UC_ARM_REG_LR,stop|1);u.reg_write(a.UC_ARM_REG_PRIMASK,f['mask']);u.reg_write(a.UC_ARM_REG_R0,dst);u.reg_write(a.UC_ARM_REG_R1,f['capacity']);u.reg_write(a.UC_ARM_REG_R2,fmt);u.reg_write(a.UC_ARM_REG_R3,args[0] if f['entry']=='snprintf' else ap)
 ctx={};done=[False];writes=[];trace=[]
 def next_char():
  if ctx['index']==f['emits']:
   # Declared format engine model: mutate local cursor to show copied ownership.
   w(ctx['cursor_address'],rd(ctx['cursor_address'])+4*f.get('consume',0));u.reg_write(a.UC_ARM_REG_R0,f['engine_result']&0xffffffff);u.reg_write(a.UC_ARM_REG_PC,ctx['return']);return
  value=(65+ctx['index']%26)&255;ctx['index']+=1;u.reg_write(a.UC_ARM_REG_R0,ctx['state']);u.reg_write(a.UC_ARM_REG_R1,value);u.reg_write(a.UC_ARM_REG_LR,resume|1);u.reg_write(a.UC_ARM_REG_PC,ctx['callback'])
 def code(cpu,pc,size,_):
  trace.append([hex(pc),hex(cpu.reg_read(a.UC_ARM_REG_LR)),hex(cpu.reg_read(a.UC_ARM_REG_SP))])
  if stock:
   for k,(start,end) in extents.items():
    if start<=pc<end:visited[k].update(range(pc,pc+size))
  if pc in [stop,stop+2]:done[0]=True;cpu.emu_stop();return
  if pc in [resume,resume+2]:assert cpu.reg_read(a.UC_ARM_REG_R0)==ctx['state'],(stock,f,hex(cpu.reg_read(a.UC_ARM_REG_R0)),hex(ctx['state']),hex(ctx['callback']),ctx,trace[-20:]);next_char();return
  if pc==0x41e47a:
   state=cpu.reg_read(a.UC_ARM_REG_R1);cursor=cpu.reg_read(a.UC_ARM_REG_R3);ptr=rd(cursor);flag=rd(cpu.reg_read(a.UC_ARM_REG_SP));assert flag==0
   ctx['contract']=dict(state=[rd(state+4*i) for i in range(3)],args=[rd(ptr+4*i) for i in range(6)],flag=flag)
  if not stock and 0x410000<=pc<0x435000:
   # Original formatter and transitive helpers are a declared executable oracle.
   if any(start<=pc<end for start,end in extents.values()):raise AssertionError(('original wrapper/writer on C side',hex(pc)))
   original_oracle_visits.add(pc)
 def store(cpu,access,address,size,value,_):
  if dst<=address<dst+512:writes.append([address-dst,size,value&((1<<(8*size))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,store);entry=extents[f['entry']][0] if stock else sy['opencfw_boot_elog_'+f['entry']];u.emu_start(entry|1,0,count=100000);assert done[0]
 return dict(return_value=u.reg_read(a.UC_ARM_REG_R0),mask=u.reg_read(a.UC_ARM_REG_PRIMASK),sp=u.reg_read(a.UC_ARM_REG_SP),callee_saved=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],buffer=bytes(u.mem_read(dst,512)).hex(),writes=writes,core_contract=ctx['contract'],caller_va_bytes=bytes(u.mem_read(ap,24)).hex())
results=[]
formats=[('literal',[]),('%d:%u:%x',[-123,4000000000,0x1234]),('%08x', [0xabcdef]),('%.3s:%s',[0x20011000,0x20011000]),('%c:%c',[65,255]),('%ld/%lu',[-12,0xffffffff]),('%lld',[0,0x89abcdef,0x12345678]),('%s',[0x20011000]),('%d:%d:%d:%d:%d:%d',[1,2,3,4,5,6])]
for entry,cap,mask,(fmt,words) in itertools.product(['snprintf','vsnprintf'],[0,1,2,4,16,128],[0,1],formats):
 f=dict(entry=entry,capacity=cap,mask=mask,format=fmt,arg_words=[v&0xffffffff for v in words],emits=0,engine_result=0);x=run(True,f);y=run(False,f)
 if x!=y:(N/'real-core-failure.json').write_text(json.dumps(dict(fixture=f,stock=x,source=y),indent=2));raise AssertionError((f,x,y))
 results.append(dict(fixture=f,result=x))
out=dict(status='PASS_WRAPPERS_USING_ORIGINAL_FORMATTER_ORACLE',cases=len(results),candidate_sha256=c['sha256'],original_bodies={k:dict(start=hex(start),end=hex(end),bytes=end-start,visited=len(visited[k]),sha256=hashlib.sha256(blob[start-0x410000:end-0x410000]).hexdigest()) for k,(start,end) in extents.items()},original_formatter_instruction_pcs=[hex(v) for v in sorted(original_oracle_visits)],results=results,limits=['Compiled wrappers and writer execute with authenticated original formatter41e47a and its transitive helpers on C side; this is an explicitly hybrid oracle test, not source-only execution.','Original bytes are mapped solely into offline emulator memory; not linked into the candidate.','Selected literal/integer/string/character formats/capacities/ARM argument alignment tested; complete conversion/error/FP/scenario coverage remains open.'])
(N/'real-core-comparison.json').write_text(json.dumps(out,indent=2));print(out['status'],len(results),'original formatter PCs',len(original_oracle_visits))
