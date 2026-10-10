from pathlib import Path
import json,struct,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
D=Path('/repo/g2/analysis/tlsf-main-source-comparison-20261010-implementation'); O=Path('/tmp/tlsf-independent-preseed'); O.mkdir(exist_ok=True);R=Path('/repo');raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
with (D/'comparator.elf').open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_type']!='SHT_NOBITS'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
A=0x20080000;N=65536;STOP=0x300000;SP=0x20070000;guard=b'\xa9'*32
TRACE={}
entries={'create':0x4d06ec,'malloc':0x4d0722,'free':0x4d0808,'realloc':0x4d0868};source={'create':'tlsf_create_with_pool','malloc':'tlsf_malloc','free':'tlsf_free','realloc':'tlsf_realloc'}
def new(side,fill=0):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x100000,0x10000);u.mem_map(STOP,0x1000);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,raw[32:]);u.mem_map(0x20000000,0x100000);u.mem_write(A-32,guard+bytes([fill])*N+guard)
 if side=='source':
  for a,b in sections:u.mem_write(a,b)
 TRACE[id(u)]={'copy_entries':0,'instruction_addresses':set()}
 def code(u,a,n,d):
  TRACE[id(u)]['instruction_addresses'].add(a)
  if (side=='stock' and a==0x439be4) or (side=='source' and a==(sym['memcpy']&~1)):TRACE[id(u)]['copy_entries']+=1
  if a==STOP:u.emu_stop();return
  if side=='stock':
   assert a!=0x4d09b4,'stock assertion provider';assert 0x4cfd00<=a<0x4d09b4 or 0x439be4<=a<0x439c8a,('unmodeled stock dependency',hex(a))
  else:
   assert a not in [sym['__assert_func']&~1,sym['printf']&~1],'source assert/logger reached';assert 0x100000<=a<0x110000
 def write(u,acc,a,n,v,d):assert (A<=a and a+n<=A+N) or (SP-2048<=a and a+n<=SP),('unguarded write',hex(a),n)
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);return u
def call(u,side,fn,args):
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(r,v)
 u.emu_start((entries[fn] if side=='stock' else sym[source[fn]])|1,0,count=200000);assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP;assert bytes(u.mem_read(A-32,32))==guard and bytes(u.mem_read(A+N,32))==guard;return u.reg_read(UC_ARM_REG_R0)
# Each sequence uses a fresh zeroed arena; compare full arena after each operation.
sequences=[('small', [('malloc',i,s) for i,s in enumerate([0,1,3,4,5])]+[('free',i,0) for i in [1,2,3,4]]),('coalesce-forward',[('malloc',0,64),('malloc',1,64),('free',0,0),('free',1,0),('malloc',2,128)]),('coalesce-reverse',[('malloc',0,64),('malloc',1,64),('free',1,0),('free',0,0),('malloc',2,128)]),('failure',[('malloc',0,100000)]),('realloc',[('malloc',0,64),('realloc',0,16),('realloc',0,128),('realloc',0,100000),('free',0,0)])]
def invariant(u):
 word=lambda a:int.from_bytes(u.mem_read(a,4),'little')
 physical=[];free=set();h=A+0xc74-4;prev=None
 while True:
  sizeword=word(h+4);size=sizeword&~3
  if not size:break
  assert size>=12 and size%4==0 and h+size+4<A+N
  assert bool(sizeword&2)==(prev is not None and prev in free)
  if sizeword&2:assert word(h)==prev
  physical.append(h)
  if sizeword&1:free.add(h)
  prev=h;h+=size+4
 assert h==A+N-8 and bool(word(h+4)&2)==(prev in free)
 assert all(not (word(q+4)&2) for q in free)
 listed=set();bitmap=0
 for fl in range(24):
  slbits=0
  for sl in range(32):
   q=word(A+116+(fl*32+sl)*4);previous=A
   if q!=A:slbits|=1<<sl
   while q!=A:
    assert q in free and q not in listed;listed.add(q);assert word(q+12)==previous
    sz=word(q+4)&~3
    if sz<128:expected=(0,sz//4)
    else:
     bit=sz.bit_length()-1;expected=(bit-6,(sz>>(bit-5))^32)
    assert expected==(fl,sl);previous=q;q=word(q+8)
  assert word(A+20+fl*4)==slbits
  if slbits:bitmap|=1<<fl
 assert word(A+16)==bitmap and listed==free
 return dict(physical_blocks=len(physical),free_blocks=len(free),free_lists_and_bitmaps_valid=True)
sequences.append(('realloc-move',[('malloc',0,64),('malloc',1,64),('realloc',0,512),('free',0,0),('free',1,0)]))
sequences.append(('size-boundaries',[('malloc',i,n) for i,n in enumerate([11,12,13,15,16,17,127,128,129,255,256,257,511,512,513])]+[('free',i,0) for i in range(15)]))
sequences.append(('null-zero',[('free',0,0),('realloc',0,32),('realloc',0,0)]))
sequences.append(('sentinel-init',[('malloc',0,12),('free',0,0)]))
results=[]
for name,ops in sequences:
 us={s:new(s,0xa5 if name=='sentinel-init' else 0) for s in ['stock','source']};ptrs={s:{} for s in us};steps=[];lengths={};retention=[]
 for index,(fn,k,size) in enumerate([('create',0,N)]+ops):
  copies_before={s:TRACE[id(u)]['copy_entries'] for s,u in us.items()}
  ret={};prior={s:bytes(u.mem_read(ptrs[s].get(k,0),lengths.get(k,0))) if ptrs[s].get(k,0) else b'' for s,u in us.items()}
  for side,u in us.items():
   old=ptrs[side].get(k,0);args=[A,N] if fn=='create' else [A,size] if fn=='malloc' else [A,old] if fn=='free' else [A,old,size];ret[side]=call(u,side,fn,args)
   if fn in ['malloc','realloc']:
    if ret[side]:ptrs[side][k]=ret[side]
   elif fn=='free' or (fn=='realloc' and size==0):ptrs[side][k]=0
  if fn=='realloc':
   for side,u in us.items():
    pointer=ptrs[side].get(k,0);n=0 if size==0 else min(size,len(prior[side])) if ret[side] else len(prior[side])
    assert bytes(u.mem_read(pointer,n))==prior[side][:n]
   retention.append(dict(step=index,prefix_retained=True,failed_realloc_retained=not ret['stock']))
  assert bytes(us['stock'].mem_read(A,N))==bytes(us['source'].mem_read(A,N)),('preseed arena mismatch',name,index)
  if fn=='malloc' and ret['stock']:
   lengths[k]=size
   for side,u in us.items():u.mem_write(ret[side],bytes((j*17+k+3)&255 for j in range(size)))
  if fn=='realloc' and ret['stock']:lengths[k]=size
  if fn!='free':assert ret['stock']==ret['source'],(name,index,ret)
  invariants={side:invariant(u) for side,u in us.items()}
  bs={s:bytes(u.mem_read(A,N)) for s,u in us.items()};diff=[i for i,(a,b) in enumerate(zip(bs['stock'],bs['source'])) if a!=b]
  steps.append(dict(operation=fn,size=size,slot=k,returns={s:(v-A if v else None) for s,v in ret.items()},copy_provider_entries={s:TRACE[id(u)]['copy_entries']-copies_before[s] for s,u in us.items()},invariants=invariants,full_arena_equal=not diff,difference_offsets=diff[:100],arena_sha256={s:hashlib.sha256(b).hexdigest() for s,b in bs.items()}))
  if diff:
   (O/'results.json').write_text(json.dumps(dict(pass_=False,sequence=name,steps=steps),indent=2)+'\n');raise RuntimeError(('full arena mismatch',name,index,len(diff),diff[:20]))
 results.append(dict(sequence=name,steps=steps,retention_checks=retention))
(O/'results.json').write_text(json.dumps(dict(pass_=True,sequences=results),indent=2)+'\n');print('PASS full-arena TLSF sequence comparison')

(O/'executed-instructions.json').write_text(json.dumps({s:sorted(hex(a) for a in TRACE[id(u)]['instruction_addresses']) for s,u in us.items()},indent=2)+'\n')
