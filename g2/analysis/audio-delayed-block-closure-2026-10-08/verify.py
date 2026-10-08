from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-delayed-block/block.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
T=0x20006000;OTHER=0x20006100;READY=0x20006200;DELAYED=0x20006300;OVERFLOW=0x20006400;SUSPEND=0x20073d4c;RET=0x2007f000
rows=[]
for tick,wait,indefinite,nextwake,other in itertools.product([0,100,0xfffffff0],[0,1,20,0xffffffff],[0,1],[10,0xffffffff],[0,1]):
 vals=[]
 for entry in [0x455fa8,sym['audio_add_current_to_delayed']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def init(L):w(L,0,L+8,0xffffffff,L+8,L+8)
  def append(L,I,owner,value):
   S=L+8;tail=word(S+8);w(I,value,S,tail,owner,L);w(tail+4,I);w(S+8,I);w(L,word(L)+1)
  for L in [READY,DELAYED,OVERFLOW,SUSPEND]:init(L)
  append(READY,T+4,T,0x1234)
  if other:
   append(READY,OTHER+4,OTHER,0);append(DELAYED,OTHER+24,OTHER,15);append(OVERFLOW,OTHER+44,OTHER,5);append(SUSPEND,OTHER+64,OTHER,0)
  w(0x20074a20,T);w(0x20074a24,DELAYED);w(0x20074a28,OVERFLOW);w(0x20074a34,tick);w(0x20074a50,nextwake);calls=[]
  def hook(u,a,n,d):
   if a in [0x4560e8,0x4560b2]:calls.append((hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1) if a==0x4560b2 else None))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,wait);u.reg_write(UC_ARM_REG_R1,indefinite);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,RET|1);u.emu_start(entry|1,RET,count=30000);assert u.reg_read(UC_ARM_REG_PC)==RET
  is_forever=wait==0xffffffff and indefinite;wake=(tick+wait)&0xffffffff;dest=SUSPEND if is_forever else OVERFLOW if wake<tick else DELAYED
  assert word(T+0x14)==dest and word(READY)==other and word(dest)==other+1;assert word(T+4)==(0x1234 if is_forever else wake)
  assert word(0x20074a50)==(min(nextwake,wake) if not is_forever and wake>=tick else nextwake)
  vals.append((calls,bytes(u.mem_read(T,0x420)),bytes(u.mem_read(SUSPEND,20)),bytes(u.mem_read(0x20074a20,64))))
 assert vals[0]==vals[1],(tick,wait,indefinite,nextwake,other);rows.append(dict(tick=hex(tick),wait=hex(wait),may_indefinite=indefinite,initial_nextwake=hex(nextwake),other=other,destination=hex(dest),wakeup=hex(wake),calls=vals[0][0]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Actual delayed-block provider and independent C with shared real remove/sorted-list peers; coherent synthetic current task/list state.','Zero wait, finite wait, overflow, indefinite-vs-finite MAX_DELAY and populated lists tested; no timeout expiration or context switching.','Provider assumes caller protects scheduler/list mutation; test invokes it in isolation, not a full notification/queue block or reachable task schedule.']),indent=2)+'\n');print('PASS',len(rows),'delayed block comparisons')
