from pathlib import Path
import itertools,json,hashlib
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries={'common_capture_retention_block':0x47fc14,'common_capture_ton_block':0x47fc14,'ton_initialize_dispatch':0x4803ac,'lp_initialize_dispatch':0x4803f2,'lp_enable_dispatch':0x480408,'lp_disable_dispatch':0x48041e,'common_capture_to_return':0x47fc14}
registers=[0x4002036c,0x40020088,0x40020044,0x4002004c,0x40020374,0x40020080,0x400201b0,0x40020344,0x4002034c,0x40020358,0x40020354]
def run(native,kind,major,revision,date,gate,flag,pattern,repeat=False,slots=0,mask=0):
 u=machine();w(u,0x4002000c,major);w(u,0x200001e8,revision);w(u,0x2007198c,date);w(u,0x40021108,gate<<4)
 for a in registers:w(u,a,pattern)
 u.mem_write(0x2007426c,b'\xa5'*64);u.mem_write(0x20074f60,b'\xa5'*32);u.mem_write(0x20074f63,bytes([flag]));writes=[]
 def hook(u,a,n,d):
  if not native and kind in ['common_capture_retention_block','common_capture_ton_block'] and a==(0x47fdd4 if kind=='common_capture_retention_block' else 0x47fdf0):u.emu_stop()
 def write(u,ac,a,n,v,d):writes.append([a,n,v])
 u.reg_write(UC_ARM_REG_PRIMASK,mask);w(u,0x200732a0,(sym['pcm_lp_switch_initialize'] if native else 0x5a085f) if slots else 0);w(u,0x200732a4,(sym['pcm_lp_switch_enable'] if native else 0x5a08b7) if slots else 0);w(u,0x200732a8,(sym['pcm_lp_switch_disable'] if native else 0x5a08cb) if slots else 0);w(u,0x20073290,(sym['pcm_ton_initialize'] if native else 0x59fdc3) if slots else 0);w(u,0x20073294,(sym['pcm_ton_config_update'] if native else 0x59fe5b) if slots else 0);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x2007426c,end=0x200742ab);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x20074f60,end=0x20074f7f);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40020000,end=0x40021fff)
 for iteration in range(2 if repeat else 1):
  w(u,0x2007e014,0x2007f001);u.reg_write(UC_ARM_REG_R4,0x4002000c);u.reg_write(UC_ARM_REG_LR,0x2007f001)
  u.emu_start((sym['pcm_'+kind] if native else entries[kind])|1,0x2007f000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==((0x47fdd4 if kind=='common_capture_retention_block' else 0x47fdf0) if not native and kind in ['common_capture_retention_block','common_capture_ton_block'] else 0x2007f000)
  if repeat:
   for a in registers:w(u,a,pattern^0xffffffff)
 return dict(cache=bytes(u.mem_read(0x2007426c,64)).hex(),flags=bytes(u.mem_read(0x20074f60,32)).hex(),writes=writes,ton_cache=bytes(u.mem_read(0x2000453a,6)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK),status=None if kind in ['common_capture_retention_block','common_capture_ton_block'] else u.reg_read(UC_ARM_REG_R0))

rows=[]
for kind,major,revision,gate,flag,pattern,slots,mask in itertools.product(entries,[0x20,0x21,0x22,0x23],[0,1,2,3],[0,3],[0,1],[0,0xffffffff],[0,1],[0,1]):
 values=[major,revision,0,gate,flag,pattern]
 o=run(False,kind,*values,slots=slots,mask=mask);n=run(True,kind,*values,slots=slots,mask=mask)
 assert o==n,(kind,values,slots,mask,o,n)
 rows.append(dict(function=kind,inputs=values,slots=slots,mask=mask,output=o))
(D/'startup-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),counts={k:sum(r['function']==k for r in rows) for k in entries},comparisons=rows,limits=['Two explicitly bounded blocks plus capture-to-return suffix; prefix remains original/unreconstructed. Clock-mux reset executes original code with zero signature fixture, therefore gated-out reset branch.','Native capture/TON bodies composed; real IRQ-save, TON dispatch, delay and buck providers execute original instructions.','Synthetic callback registration, silicon revision, trim/MMIO and PRIMASK; no live scheduling or physical rail trace.']),separators=(',',':'))+'\n');print('PASS',len(rows),'startup comparisons')
