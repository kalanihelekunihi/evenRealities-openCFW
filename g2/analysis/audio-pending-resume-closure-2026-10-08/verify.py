from pathlib import Path
import itertools,struct,json,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-resume/resume.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
READY=0x2006a49c;PENDING=0x20073d24;DELAYED=0x20006300;CUR=0x20006000;rows=[]
for suspended,current_prio,priorities,initial_yield in itertools.product([1,2],[0,1,2],[[],[0],[1],[2],[0,2],[1,1],[2,0]],[0,1]):
 vals=[]
 for entry in [0x454dcc,sym['audio_resume_pending_selected']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segments:u.mem_write(a,b)
  def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def init_list(L):w(L,0,L+8,0xffffffff,L+8,L+8)
  def append(L,I,owner,value=0):
   S=L+8;tail=word(S+8);w(I,value,S,tail,owner,L);w(tail+4,I);w(S+8,I);w(L,word(L)+1)
  for i in range(3):init_list(READY+20*i)
  init_list(PENDING);init_list(DELAYED);w(CUR+0x2c,current_prio);append(READY+20*current_prio,CUR+4,CUR)
  for i,prio in enumerate(priorities):
   T=0x20006100+256*i;w(T+0x2c,prio);w(T+0x68,0x800000);u.mem_write(T+0x6c,b'\x02');append(DELAYED,T+4,T,100+i);append(PENDING,T+24,T)
  w(0x20074a20,CUR);w(0x20074a24,DELAYED);w(0x20074a30,len(priorities)+1);w(0x20074a38,current_prio);w(0x20074a3c,1);w(0x20074a40,0);w(0x20074a44,initial_yield);w(0x20074a50,0x1234);w(0x20074a58,suspended);boundary=[];removes=[]
  def code(u,a,n,d):
   if a==0x4560e8:removes.append(u.reg_read(UC_ARM_REG_R0))
   if a==0x4420bc:boundary.append(hex(a));u.emu_stop()
   assert a!=0x45504c,'pending tick processing excluded'
  def write(u,access,a,n,v,d):
   if CUR<=a<DELAYED+20 or READY<=a<READY+60 or PENDING<=a<PENDING+20:assert u.reg_read(UC_ARM_REG_BASEPRI)==0x30
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(entry|1,0x2007f000,count=50000);assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
  processed=suspended==1;should_yield=processed and bool(initial_yield or any(p>=current_prio for p in priorities));assert bool(boundary)==should_yield;assert word(PENDING)==(0 if processed else len(priorities));assert word(DELAYED)==(0 if processed else len(priorities));assert word(0x20074a58)==suspended-1
  for i,p in enumerate(priorities):
   T=0x20006100+256*i;assert word(T+0x14)==(READY+20*p if processed else DELAYED);assert word(T+0x28)==(0 if processed else PENDING);assert word(T+0x68)==0x800000
  assert removes==[] # stock resume removes inline; native independently reconstructs inline removal
  assert u.reg_read(UC_ARM_REG_BASEPRI)==(0x30 if boundary else 0);assert word(0x20074a50)==(0xffffffff if processed and priorities else 0x1234)
  vals.append((boundary,None if boundary else u.reg_read(UC_ARM_REG_R0),removes,bytes(u.mem_read(CUR,0x400)),bytes(u.mem_read(READY,60)),bytes(u.mem_read(PENDING,20)),bytes(u.mem_read(0x20074a20,60)),bytes(u.mem_read(0x2000309c,4)),u.reg_read(UC_ARM_REG_BASEPRI)))
 assert vals[0]==vals[1],(suspended,current_prio,priorities,initial_yield);rows.append(dict(suspended=suspended,current_priority=current_prio,pending_priorities=priorities,initial_yield=initial_yield,endpoint='yield_before_entry' if vals[0][0] else 'return',list_remove_helper_calls=vals[0][2],moved_tasks=len(priorities) if suspended==1 else 0))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(blob).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Independent selected resume/ready insertion with independent list removal, actual critical/next-unblock peers; coherent synthetic TCB/lists, no stubs.','Pending ticks0; nested counts1/2, zero/one/two pending tasks. Yield stops before first original entry; no PendSV/context switch.','No complete initialized application task population, scheduler timing or producer quiescence.']),indent=2)+'\n');print('PASS',len(rows))
