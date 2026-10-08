"""Original M33 instructions vs native source; only delay and callback bodies cut."""
from pathlib import Path
import argparse,hashlib,struct,json,itertools,importlib.util
from unicorn import *
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
ENTRIES={
 'first':('opencfw_boot_startup_shutdown_first',0x423d20,0x423d58),
 'prepare':('opencfw_boot_shutdown_prepare',0x423d58,0x423d7a),
 'wait_clear':('opencfw_boot_shutdown_wait_clear',0x423d7a,0x423d9a),
 'wait_slot':('opencfw_boot_shutdown_wait_slot',0x423da0,0x423dc4),
 'wait_zero':('opencfw_boot_shutdown_wait_zero',0x423dc4,0x423dce),
 'second':('opencfw_boot_startup_shutdown_second',0x423dd0,0x423e0c),
 'clock':('opencfw_boot_shutdown_clock_release',0x422468,0x4224b2),
 'resource':('opencfw_boot_shutdown_resource',0x4224b2,0x42252e),
 'debug':('opencfw_boot_shutdown_debug_release',0x42252e,0x422574)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
 _,segs,syms=elf.elf_info(args.elf);trace={};rows=[]
 def run(source,name,f):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33);mapped=set()
  for lo,size in [(0x410000,0x25000),(0x20000000,0x40000),(0x08000000,0x10000),(0x40004000,0x1000),(0x40020000,0x2000),(0xe0000000,0x10000)]:u.mem_map(lo,size);mapped.update(range(lo,lo+size,4096))
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
    if delays==f.get('ready_after'):w(0xe0000000,1);w(0xe0000e80,r(0xe0000e80)&~0x800000)
    u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
   if pc in [0x08000200,0x08000210]:
    events.append(['callback',pc,u.reg_read(a.UC_ARM_REG_PRIMASK)]);u.reg_write(a.UC_ARM_REG_R0,7);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  def write(cpu,access,p,size,value,user):writes.append([p,size,value&((1<<(8*size))-1)])
  u.hook_add(UC_HOOK_CODE,code)
  for lo,hi in [(0x40020000,0x40021fff),(0xe0000000,0xe000ffff)]:u.hook_add(UC_HOOK_MEM_WRITE,write,begin=lo,end=hi)
  w(0xe0000000,1 if f.get('slot_ready',True) else 0);w(0xe0000004,1);w(0xe0000e80,0x55550011|(0 if f.get('clear_ready',True) else 0x800000));w(0xe000edfc,0xa5a5a5a5);w(0x40020250,0xffffffff)
  w(0x40021004,0x04000000 if f.get('powered',False) else 0);w(0x40021008,0x04000000 if f.get('powered',False) else 0)
  # Power acknowledgement changes are synthetic fixture state, never hardware evidence.
  if f.get('ack',True):
   def ack(cpu,access,p,size,value,user):w(0x40021008,value)
   u.hook_add(UC_HOOK_MEM_WRITE,ack,begin=0x40021004,end=0x40021007)
  for p in [0x200271a1,0x200271a2,0x200271a3,0x200271c3]:u.mem_write(p,bytes([f.get('resource_count',f.get('count',0)) if p==0x200271a2 else f.get('count',0)]))
  u.mem_write(0x200271a4,bytes([f.get('owner',0)]));u.mem_write(0x200271c2,b'\xa5')
  for p,cb in [(0x20026e44,0x08000200),(0x20026e48,0x08000210)]:w(p,cb|1 if f.get('callbacks',False) else 0)
  u.reg_write(a.UC_ARM_REG_XPSR,0x01000000);u.reg_write(a.UC_ARM_REG_SP,0x2002f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001);u.reg_write(a.UC_ARM_REG_PRIMASK,f.get('irq',0));u.reg_write(a.UC_ARM_REG_R0,f.get('arg',0))
  u.emu_start((syms[ENTRIES[name][0]] if source else ENTRIES[name][1])|1,0x08000002,count=250000);assert done,(name,source,f,hex(u.reg_read(a.UC_ARM_REG_PC)))
  return dict(result=u.reg_read(a.UC_ARM_REG_R0),events=events,writes=writes,irq=u.reg_read(a.UC_ARM_REG_PRIMASK),cache=[u.mem_read(p,1)[0] for p in [0x200271a1,0x200271a2,0x200271a3,0x200271a4,0x200271c2,0x200271c3]],registers=[r(p) for p in [0xe0000000,0xe0000e80,0xe000edfc,0x40020250,0x40021004,0x40021008]])
 fixtures=[]
 for name,count,owner,irq,callbacks,powered in itertools.product(['first','second','clock','resource','debug'],[0,1,2,255],[0,1,2,3],[0,1],[False,True],[False,True]):fixtures.append((name,dict(count=count,owner=owner,irq=irq,callbacks=callbacks,powered=powered)))
 for arg,count,owner,powered,ack in itertools.product([1,255,256,257],[0,1,255],[0,1,2,3],[False,True],[False,True]):fixtures.append(('resource',dict(arg=arg,count=count,owner=owner,powered=powered,ack=ack,callbacks=True)))
 for name,slot,clear,after in itertools.product(['first','prepare','wait_clear','wait_zero'],[False,True],[False,True],[None,1,1000,1001]):fixtures.append((name,dict(slot_ready=slot,clear_ready=clear,ready_after=after)))
 for count,resource in itertools.product([0,1],[2,255]):fixtures.append(('second',dict(count=count,resource_count=resource)))
 for arg in [0,1,0x40000000]:fixtures.append(('wait_slot',dict(arg=arg)))
 for name,f in fixtures:
  stock=run(False,name,f);source=run(True,name,f)
  if stock!=source:args.output.with_suffix('.failure.json').write_text(json.dumps(dict(name=name,fixture=f,stock=stock,source=source),indent=2)+'\n');raise AssertionError((name,f,stock,source))
  rows.append(dict(name=name,fixture=f,result=stock))
 used={p+i for p,b in trace.items() for i in range(len(bytes.fromhex(b)))}
 for p,b in trace.items():assert bytes.fromhex(b)==blob[p-0x410000:p-0x410000+len(bytes.fromhex(b))]
 report=dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_trace={hex(p):b for p,b in sorted(trace.items())},visited_body_bytes={name:len(used&set(range(lo,hi))) for name,(_,lo,hi) in ENTRIES.items()},comparisons=rows,limits=['All nine source bodies plus actual critical/query/power28/wait helpers execute. Only elapsed delay and registered callback bodies controlled. No SRAM-write recorder.','Power acknowledgement is synthetic; real MMIO semantics, scheduling and IRQ/task drain unproven. Delay arguments not wall-clock proof.'])
 args.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(rows),report['visited_body_bytes'])
if __name__=='__main__':main()
