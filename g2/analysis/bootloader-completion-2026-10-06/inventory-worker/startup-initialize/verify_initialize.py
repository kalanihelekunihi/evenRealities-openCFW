"""Execute stock bytes and independent source leaves; callback bodies controlled."""
from pathlib import Path
import sys,json,hashlib,struct,itertools,importlib.util
from unicorn import *
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
_,segments,symbols=elf.elf_info(args.elf)
entries={'write':('opencfw_boot_startup_sleep_fields_write',0x41c9ca,0x41ca08),'read':('opencfw_boot_startup_sleep_fields_read',0x41ca0c,0x41ca2c)}
for name,lo,hi in [('20',0x41cdca,0x41cde0),('24',0x41cde0,0x41cdfa),('28',0x41cdfa,0x41ce10),('30',0x41ce10,0x41ce26),('34',0x41ce26,0x41ce3c),('38',0x41ce3c,0x41ce52)]:entries[name]=('opencfw_boot_startup_hook'+name,lo,hi)
entries['init']=('reconstructed_initialize',0x41c4b4,0x41c7de)
CHILDREN=[4334894, 4309370, 4309720, 4308868, 4307224, 4309792, 4330824, 4312658, 4307920, 4308534, 4307180, 4304050]
trace={}
def run(source,name,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,sz in [(0x410000,0x25000),(0x08000000,0x20000),(0x10000,0x10000),(0x20000000,0x40000),(0xe000e000,0x1000),(0xe001e000,0x1000),(0x40000000,0x100000)]:u.mem_map(lo,sz)
 if source:
  for seg in segments:u.mem_write(seg['address'],seg['data'])
 else:u.mem_write(0x410000,blob)
 def w(p,x):u.mem_write(p,struct.pack('<I',x&0xffffffff))
 w(0xe000ed14,f.get('scr',0));w(0xe001e300,f.get('value',0));u.mem_write(0x20001000,b'\xa5'*4)
 if name not in ['read','write','init']:w(0x20026e38+int(name,16),0x08000101 if f['present'] else 0)
 
 if name=='init':
  for p in [0x4000885c,0x40020250,0x4002021c,0x400201bc,0x40004044,0x40004120,0x40020448,0x4002036c,0x40020088,0x40020044,0x4002004c,0x40020374,0x40020080,0x400201b0,0x40020344,0x4002034c,0x40020358,0x40020354,0x4002037c,0x40020380,0x400211c8]:w(p,f.get('seed',0))
  w(0x400201bc,f.get('gate29',0));w(0x40021108,f.get('gate',0)<<4);w(0x4002000c,f['revision']);w(0x20000098,f['variant']);w(0x200267f8,0x1f01600d if f.get('cached',True) else 0)
  for p in range(0x2002704c,0x2002708c,4):w(p,0xa5a5a5a5)
  for p in [0x200271a3,0x200271a8,0x2000009c,0x200271a5]:u.mem_write(p,bytes([f.get('saved',0) if p==0x200271a8 else (f.get('skipdebug',0) if p==0x200271a3 else (f.get('modebyte',0) if p==0x200271a5 else 0))]))
  for slot in [0x20026e58,0x20026e5c,0x20026e68]:w(slot,0x08000101 if f.get('present',False) else 0)
 events=[];writes=[];done=False
 def hook(cpu,p,size,_):
  nonlocal done
  if p==0x08000000:done=True;u.emu_stop();return
  if not source and 0x410000<=p<0x435000:trace[p]=bytes(u.mem_read(p,size)).hex()
  if name=='init':
   for index,original in enumerate(CHILDREN):
    entry=0x08000200+index*0x10 if source else original
    if p==entry:
     r0=u.reg_read(a.UC_ARM_REG_R0);r1=u.reg_read(a.UC_ARM_REG_R1);r2=u.reg_read(a.UC_ARM_REG_R2);r3=u.reg_read(a.UC_ARM_REG_R3);irq=u.reg_read(a.UC_ARM_REG_PRIMASK)
     event=[hex(original),irq]
     if original in [0x41c17a,0x41bf84]:event+=[r0]
     if original==0x41be36:event+=[r0]
     if original==0x41bbd0:event+=[r0,bytes(u.mem_read(r0,1)).hex()]
     if original==0x421548:event+=[r0,r1,r2,r3]
     result=0
     if original==0x41c2d8:event+=[r0];u.mem_write(r1,bytes([f.get('active',0)]))
     if original==0x41b918:w(r0,0x12345678)
     if original==0x421548:
      result=f.get('failure',0) if r1==f.get('fail_selector',0) else 0
      if not result:w(r3,0x87654321)
     if original==0x41b8ec:result=irq;u.reg_write(a.UC_ARM_REG_PRIMASK,1)
     events.append(event);u.reg_write(a.UC_ARM_REG_R0,result);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if p==0x08000100:
   events.append(['callback',u.reg_read(a.UC_ARM_REG_PRIMASK)]) if name=='init' else events.append([u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)] if name=='24' else ['noarg'])
   u.reg_write(a.UC_ARM_REG_R0,f.get('status',7));u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR))
 def write(cpu,access,p,size,value,_):writes.append([p,size,value&((1<<(8*size))-1)])
 u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x400fffff);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xe000e000,end=0xe001efff)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001);u.reg_write(a.UC_ARM_REG_R0,0x20001000 if name=='read' else f.get('arg',0));u.reg_write(a.UC_ARM_REG_R1,f.get('second',0));u.reg_write(a.UC_ARM_REG_PRIMASK,f.get('irq',0))
 pc=(symbols[entries[name][0]]&~1) if source else entries[name][1];u.emu_start(pc|1,0,count=20000);assert done
 if name=='init':return dict(ret=u.reg_read(a.UC_ARM_REG_R0),writes=writes,events=events,irq=u.reg_read(a.UC_ARM_REG_PRIMASK),calibration=bytes(u.mem_read(0x2002704c,64)).hex(),saved=bytes(u.mem_read(0x200271a8,1)).hex(),revisionflag=bytes(u.mem_read(0x2000009c,1)).hex())
 return dict(ret=None if name=='read' else u.reg_read(a.UC_ARM_REG_R0),writes=writes,events=events,output=bytes(u.mem_read(0x20001000,4)).hex(),irq=u.reg_read(a.UC_ARM_REG_PRIMASK))
fixtures=[]
for revision,variant,gate,seed,saved,present,irq in itertools.product([32,33,34,35,36],[0,1,2,3,4],[0,3],[0,0xffffffff],[0,1],[False,True],[0,1]):fixtures.append(dict(revision=revision,variant=variant,gate=gate,seed=seed,saved=saved,present=present,irq=irq))
for selector,status,active,skipdebug in itertools.product([0x210,0x245],[0,7],[0,1],[0,1]):fixtures.append(dict(revision=34,variant=1,gate=3,seed=0xffffffff,saved=0,present=True,irq=0,cached=False,fail_selector=selector,failure=status,gate29=8,active=active,skipdebug=skipdebug,modebyte=255))
rows=[]
for f in fixtures:
 stock=run(False,'init',f);source=run(True,'init',f)
 if stock!=source:args.output.with_suffix('.failure.json').write_text(json.dumps(dict(fixture=f,stock=stock,source=source),indent=2));raise AssertionError((f,stock,source))
 rows.append(dict(fixture=f,result=stock))
for p,b in trace.items():assert blob[p-0x410000:p-0x410000+len(bytes.fromhex(b))]==bytes.fromhex(b)
used={p+i for p,b in trace.items() for i in range(len(bytes.fromhex(b)))}
r=dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=hashlib.sha256(blob).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_trace={hex(p):b for p,b in sorted(trace.items())},visited_body_bytes={name:len(used&set(range(lo,hi))) for name,(_,lo,hi) in entries.items()},comparisons=rows,limits=['Original810-byte orchestration versus independent source with twelve explicit child cuts; sleep-field and registered-hook wrappers execute natively.','Child cuts compare ordering/selected args and synthetic responses, not native child behavior. Callback bodies controlled; hardware, real IRQ scheduling and drain unverified.','Standalone analysis module only; not linked into promoted image or counted as closed OTA alias.'])
args.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows),r['visited_body_bytes'])
