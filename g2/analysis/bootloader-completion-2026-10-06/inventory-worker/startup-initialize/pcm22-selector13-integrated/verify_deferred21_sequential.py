from pathlib import Path
import json,struct,itertools,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import *
import unicorn.arm_const as a
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists());c=json.loads((HERE/'current-candidate.json').read_text());elf=ROOT/c['directory']/'candidate.elf';blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(int(s['p_vaddr']),s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:int(s['st_value']) for s in e.get_section_by_name('.symtab').iter_symbols()}
entries={'body':(0x429da4,'opencfw_pcm22_sequence21b'),'post':(0x42a036,'opencfw_pcm22_post_lptohp'),'hook':(0x41cdfa,'opencfw_boot_startup_hook28')};extents=[(0x429da4,0x429df6),(0x42a036,0x42a04a),(0x41cdfa,0x41ce10)];visited=set()
def run(stock,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for p,n in [(0,0x1000),(0x10000,0x10000),(0x30000,0x10000),(0x50000,0x10000),(0x410000,0x30000),(0x20000000,0x40000),(0x40000000,0x300000),(0x47ff0000,0x1000),(0xe000e000,0x2000),(0xe001e000,0x1000),(0x8000000,0x20000)]:u.mem_map(p,n)
 if stock:u.mem_write(0x410000,blob)
 else:
  for p,d in segments:u.mem_write(p,d)
 def w(p,v):u.mem_write(p,struct.pack('<I',v&0xffffffff))
 def r(p):return struct.unpack('<I',u.mem_read(p,4))[0]
 for i in range(20):w(0x20026ba4+i*4,((0x20+i)&127)|(((0x101+7*i)&1023)<<7)|((i&15)<<17)|(((0x40+i)&127)<<21))
 w(0x20000150,f['major']);w(0x200270c4,f.get('cached_target',19));w(0x40020080,0xabcdef01);w(0x40020044,0x87654321)
 u.mem_write(0x200271bc,bytes([f['flag']]));w(0x20026e60,0 if f.get('null_hook') else ((0x42a036 if stock else sy['opencfw_pcm22_post_lptohp'])|1))
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_PRIMASK,f['mask'])
 for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xabcd0000+i)
 writes=[];reads=[];done=[False];pending=[False];injected=[False];nested=[None];actions=[]
 def code(cpu,pc,size,data):
  if pc==0x8000000:done[0]=True;cpu.emu_stop();return
  if pc==0x8000100:
   assert nested[0] is not None;ctx,resume=nested[0];cpu.context_restore(ctx);nested[0]=None;cpu.reg_write(a.UC_ARM_REG_PC,resume|1);actions.append('nested-return');return
  if stock and any(lo<=pc<hi for lo,hi in extents):visited.update(range(pc,pc+size))
  if not stock and 0x410000<=pc<0x435000:raise AssertionError(('locked executable source',hex(pc)))
  if pending[0] and not injected[0] and nested[0] is None:
   pending[0]=False;injected[0]=True;action=f['action']
   if action=='cancel':cpu.mem_write(0x200271bc,b'\x00');actions.append('cancel-after-first-trim')
   elif action=='retarget':w(0x20000150,9);actions.append('retarget-after-first-trim')
   elif action=='republish':cpu.mem_write(0x200271bc,b'\x01');actions.append('republish-after-first-trim')
   elif action=='nested':
    if f['mask'] and not f.get('force_nonmaskable'):
     actions.append('maskable-reentry-deferred');return
    nested[0]=(cpu.context_save(),pc);cpu.reg_write(a.UC_ARM_REG_SP,0x2003e000);cpu.reg_write(a.UC_ARM_REG_LR,0x8000101);cpu.reg_write(a.UC_ARM_REG_PC,(0x42a036 if stock else sy['opencfw_pcm22_post_lptohp'])|1);actions.append('nested-entry')
 def write(cpu,access,p,size,v,data):
  if p in [0x40020080,0x40020044,0x200271bc]:
   writes.append([p,size,v&((1<<(size*8))-1)])
   if p==0x40020080 and not injected[0] and f.get('action'):pending[0]=True
 def read(cpu,access,p,size,v,data):
  if p in [0x20000150,0x200271bc,0x20026e60] or 0x20026ba4<=p<0x20026bf4:reads.append([p,size])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_MEM_READ,read)
 entry,name=entries[f['entry']];u.emu_start((entry if stock else sy[name])|1,0,count=20000);assert done[0] and nested[0] is None,(stock,f,hex(u.reg_read(a.UC_ARM_REG_PC)),actions,writes[-6:])
 if f.get('sequence'):
  before=len(writes)
  if f['sequence']=='rearm':w(0x20000150,9);u.mem_write(0x200271bc,b'\x01');actions.append('synthetic-rearm-between-calls')
  elif f['sequence']=='restore-hook':w(0x20026e60,(0x42a036 if stock else sy['opencfw_pcm22_post_lptohp'])|1);actions.append('restore-hook-between-calls')
  done[0]=False;u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.emu_start((entry if stock else sy[name])|1,0,count=20000);assert done[0]
  assert len(writes)-before == (0 if f['sequence']=='duplicate' else 4),(f,writes)
 return dict(result=u.reg_read(a.UC_ARM_REG_R0),sp=u.reg_read(a.UC_ARM_REG_SP),mask=u.reg_read(a.UC_ARM_REG_PRIMASK),saved=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],writes=writes,reads=reads,actions=actions,flag=u.mem_read(0x200271bc,1)[0],major=r(0x20000150),core=r(0x40020080),vddc=r(0x40020044))
fixtures=[]
for entry,sequence,mask in itertools.product(['post','hook'],['duplicate','rearm'],[0,1]):fixtures.append(dict(entry=entry,major=8,flag=1,mask=mask,sequence=sequence))
for mask in [0,1]:fixtures.append(dict(entry='hook',major=8,flag=1,mask=mask,sequence='restore-hook',null_hook=True))
rows=[]
for f in fixtures:
 x=run(True,f);y=run(False,f)
 if x!=y:(HERE/'deferred21-sequential-failure.json').write_text(json.dumps(dict(input=f,stock=x,source=y),indent=2));raise AssertionError((f,x,y))
 if f.get('action') in ['cancel','republish']:assert x['flag']==0 and len([w for w in x['writes'] if w[0] in [0x40020080,0x40020044]])==3
 rows.append(dict(input=f,result=x))
out=dict(status='PASS_BOUNDED_SCHEDULING',cases=len(rows),elf_sha256=c['sha256'],original_sha256=hashlib.sha256(blob).hexdigest(),functions=[dict(start=hex(lo),end=hex(hi),bytes=hi-lo,visited=len(visited&set(range(lo,hi))),sha256=hashlib.sha256(blob[lo-0x410000:hi-0x410000]).hexdigest()) for lo,hi in extents],results=rows,limits=['Host actions occur at guest instruction boundaries after the first committed CORE trim write. They are explicit synthetic scheduling stimuli, not observed device races.','Nested post handler executes original/source guest instructions on a separate guest stack and restores outer CPU context; memory effects persist. Maskable nesting is deferred under PRIMASK1. Forced nesting under mask1 models counterfactual/nonmaskable mutation only.','No allocator, scheduler or cancellation API is invented. Cancellation/republish are host byte changes. Source execution at original code addresses is forbidden.'])
(HERE/'deferred21-sequential-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(rows),[(x['bytes'],x['visited']) for x in out['functions']])
