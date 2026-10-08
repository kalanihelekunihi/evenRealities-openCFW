"""Native startup configuration and response ABI, with synthetic external effects."""
from pathlib import Path
import argparse,hashlib,struct,json,itertools,importlib.util
from unicorn import *
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
ENTRIES={
 'configure':('opencfw_boot_startup_power_configure',0x41c86c,0x41c986),
 'temperature':('opencfw_boot_startup_temperature',0x41ca2c,0x41ca5c),
 'setter':('opencfw_boot_startup_external_mode',0x41583c,0x415844),
 'registers':('opencfw_boot_startup_register_setup',0x41c7de,0x41c834),
 'ready':('opencfw_boot_startup_resource_ready',0x41bf3a,0x41bf84),
 'before':('opencfw_boot_startup_hook_before',0x41cd76,0x41cd8c),
 'middle':('opencfw_boot_startup_hook_middle',0x41cd8c,0x41cda2),
 'after':('opencfw_boot_startup_hook_after',0x41cda2,0x41cdb8)}
SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()==SHA
 _,segs,syms=elf.elf_info(args.elf);trace={};rows=[]
 def run(source,name,f):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33);mapped=set()
  for lo,size in [(0x410000,0x25000),(0x20000000,0x40000),(0x08000000,0x10000),(0x40004000,0x1000),(0x40020000,0x2000),(0x40014000,0x1000),(0x400c0000,0x2000),(0xe0000000,0x10000)]:u.mem_map(lo,size);mapped.update(range(lo,lo+size,4096))
  if source:
   for seg in segs:
    for p in range(seg['address']&~4095,(seg['address']+seg['memory_size']+4095)&~4095,4096):
     if p not in mapped:u.mem_map(p,4096);mapped.add(p)
    u.mem_write(seg['address'],seg['data'])
  else:u.mem_write(0x410000,blob)
  def w(p,x):u.mem_write(p,struct.pack('<I',x&0xffffffff))
  def r(p):return int.from_bytes(u.mem_read(p,4),'little')
  events=[];writes=[];done=False;delays=0
  def code(cpu,pc,size,user):
   nonlocal done,delays
   if pc==0x08000000:done=True;u.emu_stop();return
   if not source and 0x410000<=pc<0x435000:trace[pc]=bytes(u.mem_read(pc,size)).hex()
   delay=syms['opencfw_hal_delay_us']&~1 if source else 0x41d1c0
   if pc==delay:
    value=u.reg_read(a.UC_ARM_REG_R0);delays+=1;events.append(['delay',value,u.reg_read(a.UC_ARM_REG_PRIMASK)])
    if delays==f.get('primary_after'):w(0x40020180,r(0x40020180)|0x100)
    if delays==f.get('secondary_after'):w(0x400c0a7c,r(0x400c0a7c)|1)
    u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
   if pc==0x08000100:
    op=u.reg_read(a.UC_ARM_REG_R0);enabled=u.reg_read(a.UC_ARM_REG_R1);ptr=u.reg_read(a.UC_ARM_REG_R2)
    assert 0x20000000<=ptr<=0x2003fff4
    data=bytes(u.mem_read(ptr,12 if op==2 else 4));events.append(['power-callback',op,enabled,data.hex(),u.reg_read(a.UC_ARM_REG_PRIMASK)])
    if op==2:
     if f.get('response','both') in ['first','both']:w(ptr+4,f.get('first_response',0x11223344))
     if f.get('response','both')=='both':w(ptr+8,f.get('second_response',0x55667788))
   elif pc in [0x08000110,0x08000120,0x08000130,0x08000140,0x08000150]:events.append(['hook',pc,u.reg_read(a.UC_ARM_REG_PRIMASK)])
   else:return
   u.reg_write(a.UC_ARM_REG_R0,f.get('callback_status',7));u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR))
  def write(cpu,access,p,size,value,user):
   writes.append([p,size,value&((1<<(8*size))-1)])
   if p==0x40021004 and f.get('ack',True):w(0x40021008,value)
   if p==0x400c0a80 and f.get('enable_ack',True):w(0x40020180,r(0x40020180)|0x100)
  def read(cpu,access,p,size,value,user):
   # Synthetic sticky command bits make both operation3 wait-error branches reachable.
   if (f.get('arg',0)&255)==3:
    if p==0x40021004 and f.get('stuck')==1:w(p,r(p)|1)
    if p==0x4002100c and f.get('stuck')==2:w(p,r(p)|4)
  u.hook_add(UC_HOOK_CODE,code)
  for lo,hi in [(0x40020000,0x40021fff),(0x400c0000,0x400c1fff),(0xe0000000,0xe000ffff)]:u.hook_add(UC_HOOK_MEM_WRITE,write,begin=lo,end=hi)
  u.hook_add(UC_HOOK_MEM_READ,read,begin=0x40021004,end=0x4002100f)
  regs=[0x40020060,0x40020378,0x4002033c,0x40021100,0x40020124,0x40020120,0x40020250,0xe000edfc]
  for p in regs:w(p,f.get('seed',0xa5a5a5a5))
  w(0x40021108,f.get('gate',0)<<4);w(0x40020180,0x100 if f.get('primary',True) else 0);w(0x400c0a7c,1 if f.get('secondary',True) else 0);w(0x400c0a80,0x12340000)
  w(0x40021004,0x200000 if f.get('powered',True) else 0);w(0x40021008,0x200000 if f.get('powered',True) else 0);w(0x4002100c,0x12340000);w(0x40021010,0)
  for offset,cb in [(4,0x08000100),(20,0x08000110),(24,0x08000120),(28,0x08000130),(12,0x08000140),(16,0x08000150)]:w(0x20026e38+offset,cb|1 if f.get('callbacks',False) else 0)
  w(0x20010000,0xaabbccdd);w(0x20010004,0xeeff0011);w(0x200270cc,0x08001235)
  u.reg_write(a.UC_ARM_REG_XPSR,0x01000000);u.reg_write(a.UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(a.UC_ARM_REG_SP,0x2002f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001);u.reg_write(a.UC_ARM_REG_PRIMASK,f.get('irq',0));u.reg_write(a.UC_ARM_REG_R0,0x20010000 if name=='temperature' else f.get('arg',0));u.reg_write(a.UC_ARM_REG_R1,f.get('r1',0x12345678));u.reg_write(a.UC_ARM_REG_R2,f.get('r2',0x9abcdef0));u.reg_write(a.UC_ARM_REG_S0,f.get('float_bits',0x41c80000))
  u.emu_start((syms[ENTRIES[name][0]] if source else ENTRIES[name][1])|1,0x08000002,count=100000);assert done,(name,source,f,hex(u.reg_read(a.UC_ARM_REG_PC)))
  return dict(result=u.reg_read(a.UC_ARM_REG_R0) if name not in ['registers','setter'] else None,events=events,writes=writes,irq=u.reg_read(a.UC_ARM_REG_PRIMASK),response=bytes(u.mem_read(0x20010000,8)).hex(),sink=hex(r(0x200270cc)),registers=[r(p) for p in regs+[0x40021004,0x40021008,0x4002100c,0x40020180,0x400c0a7c,0x400c0a80]])
 fixtures=[]
 for arg,gate,callbacks,status,irq,seed in itertools.product([0,1,2,3,4,255,256,257,258,259],[0,3],[False,True],[0,7],[0,1],[0,0xffffffff]):fixtures.append(('configure',dict(arg=arg,gate=gate,callbacks=callbacks,callback_status=status,irq=irq,seed=seed)))
 for primary,secondary,enable_ack,ack,after in itertools.product([False,True],[False,True],[False,True],[False,True],[None,1,100,101,200,201]):
  for name in ['ready','configure']:fixtures.append((name,dict(arg=1,primary=primary,secondary=secondary,enable_ack=enable_ack,ack=ack,primary_after=after,callbacks=True)))
 for powered,callbacks,irq in itertools.product([False,True],[False,True],[0,1]):fixtures.append(('configure',dict(arg=1,powered=powered,callbacks=callbacks,irq=irq)))
 for stuck,callbacks,status in itertools.product([1,2],[False,True],[0,7]):fixtures.append(('configure',dict(arg=3,stuck=stuck,callbacks=callbacks,callback_status=status)))
 for callbacks,status,response,bits,irq in itertools.product([False,True],[0,1,7],['none','first','both'],[0,0x80000000,0x41c80000,0x7fc12345],[0,1]):fixtures.append(('temperature',dict(callbacks=callbacks,callback_status=status,response=response,float_bits=bits,irq=irq)))
 for name in ['before','middle','after']:
  for callbacks,status in itertools.product([False,True],[0,7,0xffffffff]):fixtures.append((name,dict(callbacks=callbacks,callback_status=status)))
 for value in [0,1,0x08000101,0xffffffff]:fixtures.append(('setter',dict(arg=value)))
 for seed in [0,0xffffffff,0x12345678]:fixtures.append(('registers',dict(seed=seed)))
 for name,f in fixtures:
  stock=run(False,name,f);source=run(True,name,f)
  if stock!=source:args.output.with_suffix('.failure.json').write_text(json.dumps(dict(name=name,fixture=f,stock=stock,source=source),indent=2)+'\n');raise AssertionError((name,f,stock,source))
  rows.append(dict(name=name,fixture=f,result=stock))
 used={p+i for p,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 for p,b in trace.items():assert bytes.fromhex(b)==blob[p-0x410000:p-0x410000+len(bytes.fromhex(b))]
 report=dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_sha256=SHA,original_trace={hex(p):b for p,b in sorted(trace.items())},visited_body_bytes={name:len(used&set(range(lo,hi))) for name,(_,lo,hi) in ENTRIES.items()},comparisons=rows,limits=['All eight source bodies plus native callback/query/power23/clock-release/wait helpers execute; elapsed delay and registered callback bodies controlled.','Synthetic acknowledgement/readiness/sticky bits only, no hardware timing/concurrency/drain proof. Clock owner state initialized empty; no claim every release ownership state tested.','Temperature retains incomingR1/R2 response words without complete successful callback. FP32 S0 store executes natively; no float conversion, physical measurement units or calibrated temperature interpretation proved.'])
 args.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(rows),report['visited_body_bytes'])
if __name__=='__main__':main()
