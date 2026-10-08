from pathlib import Path
import itertools,json,hashlib
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries={'variant_initialize':0x5a08e4,'capture_trim_block':0x47fc14,'early_initialize_noop':0x5a0018,'middle_reset_noop':0x5a0a6c}
registers=[0x4002036c,0x40020088,0x40020044,0x4002004c,0x40020374,0x40020080,0x400201b0,0x40020344,0x4002034c,0x40020358,0x40020354]
def run(native,kind,major,revision,date,gate,flag,pattern,repeat=False):
 u=machine();w(u,0x4002000c,major);w(u,0x200001e8,revision);w(u,0x2007198c,date);w(u,0x40021108,gate<<4)
 for a in registers:w(u,a,pattern)
 u.mem_write(0x2007426c,b'\xa5'*64);u.mem_write(0x20074f60,b'\xa5'*32);u.mem_write(0x20074f63,bytes([flag]));writes=[]
 def hook(u,a,n,d):
  if not native and kind=='capture_trim_block' and a==0x47fdb4:u.emu_stop()
 def write(u,ac,a,n,v,d):writes.append([a,n,v])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x2007426c,end=0x200742ab);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x20074f60,end=0x20074f7f)
 for iteration in range(2 if repeat else 1):
  u.reg_write(UC_ARM_REG_R4,0x4002000c);u.reg_write(UC_ARM_REG_LR,0x2007f001)
  u.emu_start((sym['pcm_'+kind] if native else entries[kind])|1,0x2007f000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==(0x47fdb4 if not native and kind=='capture_trim_block' else 0x2007f000)
  if repeat:
   for a in registers:w(u,a,pattern^0xffffffff)
 return dict(cache=bytes(u.mem_read(0x2007426c,64)).hex(),flags=bytes(u.mem_read(0x20074f60,32)).hex(),writes=writes,status=None if kind=='capture_trim_block' else u.reg_read(UC_ARM_REG_R0))
rows=[]
def compare(kind,values,repeat=False):
 o=run(False,kind,*values,repeat=repeat);n=run(True,kind,*values,repeat=repeat);assert o==n,(kind,values,o,n);rows.append(dict(function=kind,inputs=values,repeat=repeat,output=o))
dates=[0,0xffffffff,(24<<25)|(12<<21)|(19<<16),(24<<25)|(12<<21)|(20<<16),(24<<25)|(12<<21)|(31<<16),(25<<25),(31<<25),(25<<25)|1,(24<<25)|(12<<21)|(20<<16)|1]
for major,rev,date in itertools.product([0x20,0x21,0x22,0x23,0x24,0x121],[0,1,2,3,4,0xffffffff],dates):compare('variant_initialize',[major,rev,date,3,0,0])
for major,rev,gate,flag,pattern in itertools.product([0x20,0x21,0x22,0x23,0x24,0x121],[0,1,2,3,4,0xffffffff],[0,2,3],[0,1,255],[0,0xffffffff,0x12345678]):compare('capture_trim_block',[major,rev,0,gate,flag,pattern])
for major,rev in itertools.product([0x21,0x22,0x23],[0,1,2,3]):compare('capture_trim_block',[major,rev,0,3,0,0xffffffff],True)
for kind in ['early_initialize_noop','middle_reset_noop']:compare(kind,[0x23,0,0,3,0,0xffffffff])
result=dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),counts={k:sum(r['function']==k for r in rows) for k in entries},comparisons=rows,limits=['Capture is a bounded block within common low-power initializer; original execution stops at actual continuation 0x47FDB4. Not full initializer validation.','Synthetic silicon revision/date/register values; no actual factory calibration or physical hardware.','No external return stubs; these bounded bodies contain no calls.'])
(D/'results.json').write_text(json.dumps(result,separators=(',',':'))+'\n');print('PASS',len(rows),result['counts'])
