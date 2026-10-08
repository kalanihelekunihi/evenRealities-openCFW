from pathlib import Path
import json,hashlib,struct,itertools,argparse,random
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn import arm_const as a
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,default=Path('/tmp/opencfw-iar-engine/candidate.elf'));args=ap.parse_args()
with args.elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
visited=set();helper_pcs=set()
def run(stock,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for p,n in [(0x410000,0x30000),(0x70000,0x10000),(0x8000000,4096),(0x20000000,0x40000)]:u.mem_map(p,n)
 if stock:u.mem_write(0x410000,blob)
 else:
  for p,data in segments:u.mem_write(p,data)
 SP=0x2003e000;FMT=0x20001000;CUR=0x20002000;WORDS=0x20003000+f.get('align',0);STR=0x20004000;OUT=0x20005000;STATE=0x20006000
 w=lambda p,v:u.mem_write(p,struct.pack('<I',v&0xffffffff))
 u.mem_write(FMT,f['format'].encode()+b'\0');u.mem_write(STR,f.get('string','hello-boundary').encode()+b'\0');u.mem_write(OUT,b'\xa5'*16);words=f['words']+[0]*16;u.mem_write(WORDS,struct.pack('<'+str(len(words))+'I',*[x&0xffffffff for x in words]));w(CUR,WORDS);w(0x20027190,0x8000201 if f.get('handler',True) else 0);w(SP,f.get('mode',0))
 for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xaac000+i)
 for reg,val in [(a.UC_ARM_REG_R0,0x8000101),(a.UC_ARM_REG_R1,STATE),(a.UC_ARM_REG_R2,FMT),(a.UC_ARM_REG_R3,CUR),(a.UC_ARM_REG_SP,SP),(a.UC_ARM_REG_LR,0x8000001),(a.UC_ARM_REG_PRIMASK,f.get('mask',0))]:u.reg_write(reg,val)
 events=[];done=[False];terminal=[False];writes=[]
 def string(p):
  out=bytearray()
  while u.mem_read(p,1)[0]:out+=u.mem_read(p,1);p+=1
  return out.decode()
 def hook(cpu,pc,size,_):
  if pc==0x8000000:done[0]=True;cpu.emu_stop();return
  if bytes(cpu.mem_read(pc,2))==b'\xab\xbe':
   events.append(['semihost_exit',cpu.reg_read(a.UC_ARM_REG_R0),cpu.reg_read(a.UC_ARM_REG_R1),cpu.reg_read(a.UC_ARM_REG_R2)]);terminal[0]=True;cpu.emu_stop();return
  if pc==0x8000100:
   i=sum(x[0]=='put' for x in events);state=cpu.reg_read(a.UC_ARM_REG_R0);byte=cpu.reg_read(a.UC_ARM_REG_R1);events.append(['put',state,byte]);cpu.reg_write(a.UC_ARM_REG_R0,0 if i==f.get('fail_at',-1) else STATE+4*(i+1));cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  if pc==0x8000200:
   events.append(['constraint',string(cpu.reg_read(a.UC_ARM_REG_R0)),cpu.reg_read(a.UC_ARM_REG_R1),cpu.reg_read(a.UC_ARM_REG_R2)]);cpu.reg_write(a.UC_ARM_REG_R0,f.get('handler_return',0));cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  if stock:
   assert 0x410000<=pc<0x435000,hex(pc)
   if 0x41e47a<=pc<0x41f132:visited.update(range(pc,pc+size))
   else:helper_pcs.add(pc)
  else:assert not 0x410000<=pc<0x435000,('original code on source side',hex(pc))
 def store(cpu,access,p,size,value,_):
  if OUT<=p<OUT+16:writes.append([p-OUT,size,value&((1<<(8*size))-1)])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,store);u.emu_start((0x41e47a if stock else sy['opencfw_iar_format_engine'])|1,0,count=200000);assert done[0] or terminal[0],(stock,f,hex(u.reg_read(a.UC_ARM_REG_PC)))
 if terminal[0]:return {'terminal_contract':True,'events':events,'cursor_bytes':struct.unpack('<I',u.mem_read(CUR,4))[0]-WORDS,'output':bytes(u.mem_read(OUT,16)).hex(),'writes':writes}
 return {'terminal_contract':False,'events':events,'return':u.reg_read(a.UC_ARM_REG_R0),'cursor_bytes':struct.unpack('<I',u.mem_read(CUR,4))[0]-WORDS,'output':bytes(u.mem_read(OUT,16)).hex(),'writes':writes,'caller_words':bytes(u.mem_read(WORDS,32)).hex(),'mask':u.reg_read(a.UC_ARM_REG_PRIMASK),'sp':u.reg_read(a.UC_ARM_REG_SP),'saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)]}
fixtures=[]
for conversion,flags,width,precision,value in itertools.product('diuoxX',['','+',' ','#','0','-0','+#0'],['','12'],['','.0','.3'],[0,1,0x80,0xffffffff,0x80000000]):fixtures.append(dict(format='pre%'+flags+width+precision+conversion+'post',words=[value]))
for length,conv,align in itertools.product(['hh','h','l','ll','j','t','z','L'],'diuoxX',[0,4]):fixtures.append(dict(format='%#20.4'+length+conv,words=[0x89abcdef,0x12345678,0x80000000],align=align))
for fmt,words in [('%s',[0x20004000]),('%s',[0]),('%20.3s',[0x20004000]),('%-20.3s',[0x20004000]),('%ls',[0x20004000]),('%c:%c',[0,255]),('%20c',[0x80000041]),('%p',[0]),('%#020p',[0x1234]),('%%:%q:%',[]),('%*.*d',[-12,4,-123]),('AB%hhn:%hn:%n:%llnZ',[0x20005000,0x20005004,0x20005008,0x20005008]),('%20n',[0x20005000]),('%n',[0])]:
 for mode,mask in itertools.product([0,1,256,257],[0,1]):fixtures.append(dict(format=fmt,words=words,mode=mode,mask=mask))
for fmt,words in [('literal',[]),('%#020x',[0x1234]),('%-20s',[0x20004000]),('%#20.5o',[42]),('%s%n',[0x20004000,0x20005000])]:
 for fail in [-1,0,1,2,4,10,19,25]:fixtures.append(dict(format=fmt,words=words,fail_at=fail,mask=1))
for fmt,words,mode in [('%s',[0],1),('%n',[0],0),('%n',[0x20005000],1)]:fixtures.append(dict(format=fmt,words=words,mode=mode,handler=False))
rows=[]
for f in fixtures:
 x=run(True,f);y=run(False,f)
 if x!=y:(N/'failure.json').write_text(json.dumps({'fixture':f,'stock':x,'source':y},indent=2));raise AssertionError((f,x,y))
 rows.append({'fixture':f,'result':x})
r={'status':'PASS_NONFLOAT_ENGINE','cases':len(rows),'original_sha256':hashlib.sha256(blob).hexdigest(),'native_elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((N/'engine.c').read_bytes()).hexdigest(),'engine_bytes':3256,'engine_visited_bytes':len(visited),'original_helper_pcs':[hex(x) for x in sorted(helper_pcs)],'comparisons':rows,'limits':['Synthetic external output callback with pointer-changing returns and failure points; configured constraint callback explicitly controlled. Real stock formatter and all internal helpers execute original bytes; no original image/code on source side.','Default constraint-handler abort and reconstructed semihost exit execute up to the original/native BKPT instruction; operation/reason registers compare, and the test stops before invoking semihosting.','Floating conversions return explicit unfinished -2 in draft source; no full engine ownership or successor integration promotion.']}
(N/'comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'],r['engine_visited_bytes'])
