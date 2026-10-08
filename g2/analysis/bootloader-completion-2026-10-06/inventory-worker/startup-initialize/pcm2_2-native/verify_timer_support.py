from pathlib import Path
import struct,json,hashlib,importlib.util,itertools,argparse
from unicorn import *
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[6];HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
_,segments,symbols=elf.elf_info(args.elf)
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
entries={'2b':('opencfw_pcm22_sequence2b',0x428378,0x4283e2),'7b':('opencfw_pcm22_sequence7b',0x428a94,0x428ba8),'ISR':('opencfw_pcm22_timer_service',0x42a04a,0x42a078),'start':('opencfw_pcm22_spot_timer_start',0x41cc48,0x41cc92),'stop':('opencfw_pcm22_spot_timer_stop',0x41ccd6,0x41cd1a),'cache':('opencfw_pcm22_icache_disable',0x41e22e,0x41e266)}
functions={int(d['entry'],16):d for d in map(json.loads,(ROOT/'g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines())}
for _,lo,hi in entries.values():assert hashlib.sha256(blob[lo-0x410000:hi-0x410000]).hexdigest()==functions[lo]['body_sha256']
trace={}
def run(source,kind,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,n in [(0,0x1000),(0x410000,0x25000),(0x10000,0x10000),(0x30000,0x10000),(0x08000000,0x20000),(0x20000000,0x40000),(0x40000000,0x300000),(0xe0000000,0x200000),(0x47ff0000,0x10000)]:u.mem_map(lo,n)
 if source:
  for seg in segments:u.mem_write(seg['address'],seg['data'])
 else:u.mem_write(0x410000,blob)
 def w(p,v):u.mem_write(p,struct.pack('<I',v&0xffffffff))
 for p in [0x40020044,0x4002004c,0x40020080,0x4002037c,0x400083e0,0x40008010]:w(p,0xa5a5a5a5)
 for p,v in [(0x200270b0,0x123),(0x200270bc,0x39),(0x200270b8,0x823),(0x200270b4,0x178),(0x40021000,f['mode']),(0x40004044,f['clock_enable']),(0x40004030,f['ready']),(0x47ff0000,0xabcdef01),(0xe001e300,f['cacheguard']),(0xe000ed14,0x20000)]:w(p,v)
 u.mem_write(0x2000055a,bytes([f['ongoing']]))
 events=[];writes=[];done=False
 def hook(cpu,pc,size,_):
  nonlocal done
  if pc==0x08000000:done=True;u.emu_stop();return
  if pc==0x40:events.append(['ROM40',u.reg_read(a.UC_ARM_REG_R0)]);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if source and 0x410000<=pc<0x435000:raise AssertionError(('stock fallback',hex(pc)))
  if not source and 0x410000<=pc<0x435000:trace[pc]=bytes(u.mem_read(pc,size)).hex()
 def write(cpu,access,p,n,v,_):writes.append([p,n,v&((1<<(n*8))-1)])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x402fffff);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xe0000000,end=0xe01fffff)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001);u.reg_write(a.UC_ARM_REG_PRIMASK,f['irq']);u.reg_write(a.UC_ARM_REG_R0,f.get('wait',50));u.reg_write(a.UC_ARM_REG_R3,0x10203040);u.reg_write(a.UC_ARM_REG_R7,0x50607080)
 pc=(symbols[entries[kind][0]]&~1) if source else entries[kind][1];u.emu_start(pc|1,0,count=500000);assert done,(kind,f,hex(u.reg_read(a.UC_ARM_REG_PC)))
 return dict(ret=u.reg_read(a.UC_ARM_REG_R0) if kind in ['ISR','cache'] else None,irq=u.reg_read(a.UC_ARM_REG_PRIMASK),stack=u.reg_read(a.UC_ARM_REG_SP),ongoing=u.mem_read(0x2000055a,1).hex(),cached=u.mem_read(0x200270b0,16).hex(),writes=writes,events=events)
rows=[]
for kind in entries:
 for irq,ongoing,mode,enable,ready,guard in itertools.product([0,1],[2,7,26],[0,2,6],[0,0x20],[0,0x1000000],[0,0x300]):
  f=dict(irq=irq,ongoing=ongoing,mode=mode,clock_enable=enable,ready=ready,cacheguard=guard)
  stock=run(False,kind,f);source=run(True,kind,f)
  if stock!=source:args.output.with_suffix('.failure.json').write_text(json.dumps(dict(kind=kind,fixture=f,stock=stock,source=source),indent=2));raise AssertionError((kind,f))
  rows.append(dict(kind=kind,fixture=f,result=stock))
for p,b in trace.items():assert blob[p-0x410000:p-0x410000+len(bytes.fromhex(b))]==bytes.fromhex(b)
used={p+i for p,b in trace.items() for i in range(len(bytes.fromhex(b)))}
r=dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=hashlib.sha256(blob).hexdigest(),coverage={k:dict(body_bytes=hi-lo,visited=len(set(range(lo,hi))&used)) for k,(_,lo,hi) in entries.items()},original_trace={hex(p):b for p,b in sorted(trace.items())},comparisons=rows,limits=['Nativecompiledsource vs actualoriginal instructions; only absentROM40 waitingservice controlled. No physical IRQ/time or fullscheduler claim.','2b/7b/start/stop are effect-only APIs; their incidental originalR0/R1 values not asserted. EnclosingISR returnirq is compared; sourcecompiledclock manager and classproviders execute without stubs.'])
args.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows),r['coverage'])
