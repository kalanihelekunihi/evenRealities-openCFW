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
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_A15)
 u.reg_write(a.UC_ARM_REG_C1_C0_2,0xf<<20);u.reg_write(a.UC_ARM_REG_FPEXC,1<<30);u.reg_write(a.UC_ARM_REG_FPSCR,f.get('fpscr',0))
 for p,n in [(0x410000,0x30000),(0x70000,0x10000),(0x8000000,4096),(0x20000000,0x40000)]:u.mem_map(p,n)
 if stock:u.mem_write(0x410000,blob)
 else:
  for p,data in segments:u.mem_write(p,data)
 SP=0x2003e000;FMT=0x20001000;CUR=0x20002000;WORDS=0x20003000+f.get('align',0);STR=0x20004000;OUT=0x20005000;STATE=0x20006000
 w=lambda p,v:u.mem_write(p,struct.pack('<I',v&0xffffffff))
 u.mem_write(FMT,f['format'].encode()+b'\0');u.mem_write(STR,f.get('string','hello-boundary').encode()+b'\0');u.mem_write(OUT,b'\xa5'*16);words=f['words']+[0]*16;u.mem_write(WORDS,struct.pack('<'+str(len(words))+'I',*[x&0xffffffff for x in words]));w(CUR,WORDS);w(0x2000053c,0x20007000);u.mem_write(0x20007000,f.get('decimal','.').encode()+b'\0');w(0x20027190,0x8000201 if f.get('handler',True) else 0);w(SP,f.get('mode',0))
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
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,store);
 try:u.emu_start((0x41e47a if stock else sy['opencfw_iar_format_engine'])|1,0,count=200000)
 except UcError as e:raise AssertionError(('emulator',stock,f,hex(u.reg_read(a.UC_ARM_REG_PC)),e))
 assert done[0] or terminal[0],(stock,f,hex(u.reg_read(a.UC_ARM_REG_PC)))
 if terminal[0]:return {'terminal_contract':True,'events':events,'cursor_bytes':struct.unpack('<I',u.mem_read(CUR,4))[0]-WORDS,'output':bytes(u.mem_read(OUT,16)).hex(),'writes':writes}
 return {'fpscr':u.reg_read(a.UC_ARM_REG_FPSCR),'terminal_contract':False,'events':events,'return':u.reg_read(a.UC_ARM_REG_R0),'cursor_bytes':struct.unpack('<I',u.mem_read(CUR,4))[0]-WORDS,'output':bytes(u.mem_read(OUT,16)).hex(),'writes':writes,'caller_words':bytes(u.mem_read(WORDS,32)).hex(),'mask':u.reg_read(a.UC_ARM_REG_PRIMASK),'sp':u.reg_read(a.UC_ARM_REG_SP),'saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)]}
fixtures=[]
def words(value):return list(struct.unpack('<II',struct.pack('<d',value)))
values=[0.0,-0.0,1.0,1.5,-12.375,0.1,2.5,1e-5,1e10,1e20,float('inf'),float('-inf'),float('nan')]
for conversion,precision,flags,value in itertools.product('aAeEfFgG',['','.0','.1','.3','.6','.12'],['','+','#','020','-20'],values):fixtures.append(dict(format='%'+flags+precision+conversion,words=words(value)))
for value,fmt,fpscr in itertools.product([1.25,0.1,-1.25,1e-5],['%a','%.1f','%g','%.12e'],[0,0x00400000,0x00800000,0x00c00000,0x01000000,0x02000000,0x9f]):fixtures.append(dict(format=fmt,words=words(value),fpscr=fpscr))
for fmt,value,fail in itertools.product(['%+020.6f','%-20.3e','%#.6g','%a'],[1.25,0.1],[-1,0,1,4,10]):fixtures.append(dict(format=fmt,words=words(value),fail_at=fail))
rows=[]
for f in fixtures:
 x=run(True,f);y=run(False,f)
 if x!=y:(N/'float-failure.json').write_text(json.dumps({'fixture':f,'stock':x,'source':y},indent=2));raise AssertionError((f,x,y))
 rows.append({'fixture':f,'result':x})
r={'status':'PASS_FLOAT_ENGINE_DP_DECODER','cases':len(rows),'original_sha256':hashlib.sha256(blob).hexdigest(),'native_elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'engine_visited_bytes':len(visited),'original_helper_pcs':[hex(x) for x in sorted(helper_pcs)],'comparisons':rows,'limits':['Cortex-A15 Thumb decoder used solely for shared DP instruction semantics because installed Unicorn M33 model rejects stock binary64 VFP instructions. Not a Cortex-M55 interrupt/scheduling proof; separate M55 QEMU validation required.','Full FPSCR and callee state compared without flags normalization or register repair. Synthetic external callback/locale/stack fixtures; original image absent on C side.','Draft engine, not integrated candidate; decimal nonpositive generation budget remains an explicitly marked unresolved stack-dependence boundary.']}
(N/'float-comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'],r['engine_visited_bytes'])
