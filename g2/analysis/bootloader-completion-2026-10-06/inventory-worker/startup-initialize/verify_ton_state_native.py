"""TON event/temporary-trim family: stock instructions versus source ELF."""
from pathlib import Path
import argparse,hashlib,importlib.util,itertools,json,struct
from unicorn import *
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[5]
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf);_,segments,symbols=elf.elf_info(args.elf)
entries={'event':('opencfw_boot_ton_state_event',0x42f38e,0x42f3da),'begin':('opencfw_boot_ton_lowpower_begin',0x42f204,0x42f2fa),'end':('opencfw_boot_ton_lowpower_end',0x42f2fa,0x42f38e),'gate':('opencfw_boot_ton_clock_gate',0x42f1c8,0x42f204)}
trace={};words=[0x40021100,0x40021108,0x40020060,0x40020080,0x40020088,0x40020044,0x4002004c,0x400201b0,0x40020374,0x40020340,0x40020344,0x4002034c,0x40020354,0x40020358,0x2002704c,0x20027050,0x20027054,0x20027058,0x20027090,0x20027094]
def run(source,name,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,size in [(0,0x1000),(0x10000,0x10000),(0x30000,0x10000),(0x410000,0x25000),(0x08000000,0x1000),(0x20000000,0x40000),(0x40000000,0x100000),(0xe000e000,0x1000)]:u.mem_map(lo,size)
 if source:
  for seg in segments:u.mem_write(seg['address'],seg['data'])
 else:u.mem_write(0x410000,blob)
 def w(p,v):u.mem_write(p,struct.pack('<I',v&0xffffffff))
 for p in words:w(p,0x13579bdf)
 w(0x40021108,f['hw_mode']<<4);w(0x40021100,0xa5a5a5a0|f['busy']);w(0x2002704c,f['trim']);w(0x20027050,f['trim']);u.mem_write(0x200271a8,bytes([f['cache']]))
 u.mem_write(0x20000554,bytes([14,31,11,7,21,31]));w(0x20026e5c,(symbols['opencfw_boot_ton_trim_apply'] if source else 0x42f4b3) if f['hook'] else 0)
 payload=0x20001000;w(payload,f['payload']);w(payload+4,0xa5a5a5a5);w(payload+8,0x5a5a5a5a)
 events=[];writes=[];done=False
 def hook(cpu,p,size,_):
  nonlocal done
  if p==0x08000000:done=True;cpu.emu_stop();return
  if not source and 0x410000<=p<0x435000:trace[p]=bytes(cpu.mem_read(p,size)).hex()
  if p==0x40:events.append(['ROM40cycles',cpu.reg_read(a.UC_ARM_REG_R0)]);cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR))
 def write(cpu,access,p,size,value,_):writes.append([p,size,value&((1<<(8*size))-1)])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x400fffff)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001);u.reg_write(a.UC_ARM_REG_PRIMASK,f['irq'])
 for reg in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{reg}'),0xa0000000+reg)
 u.reg_write(a.UC_ARM_REG_R0,f['selector']);u.reg_write(a.UC_ARM_REG_R1,0x87654321);u.reg_write(a.UC_ARM_REG_R2,payload)
 pc=(symbols[entries[name][0]]&~1) if source else entries[name][1];u.emu_start(pc|1,0,count=100000);assert done,(name,f,source)
 return dict(status=None if name=='gate' else u.reg_read(a.UC_ARM_REG_R0),callee_saved=[u.reg_read(getattr(a,f'UC_ARM_REG_R{reg}')) for reg in range(4,12)],stack=u.reg_read(a.UC_ARM_REG_SP),primask=u.reg_read(a.UC_ARM_REG_PRIMASK),events=events,writes=writes,words={hex(p):struct.unpack('<I',u.mem_read(p,4))[0] for p in words},payload=bytes(u.mem_read(payload,12)).hex(),trim_cache=bytes(u.mem_read(0x20000554,6)).hex())
fixtures=[]
for selector,payload,mode,cache,hook in itertools.product([0,1,2,3,4,5,6,7,257,258],[0,1,2,3],[0,3],[0,1],[0,1]):fixtures.append(('event',dict(selector=selector,payload=payload,hw_mode=mode,cache=cache,hook=hook,trim=119,busy=1,irq=selector&1)))
for selector,mode,cache,trim,busy,hook in itertools.product([0,1,2,255,258],[0,3],[0,1],[0,118,119,127,0xffffffff],[0,1],[0,1]):fixtures.append(('begin',dict(selector=selector,payload=0,hw_mode=mode,cache=cache,hook=hook,trim=trim,busy=busy,irq=cache)))
for mode,cache,trim,busy,hook in itertools.product([0,3],[0,1],[0,1,127,0xffffffff],[0,1],[0,1]):fixtures.append(('end',dict(selector=0,payload=0,hw_mode=mode,cache=cache,hook=hook,trim=trim,busy=busy,irq=cache)))
for selector,busy in itertools.product([0,1,2,255,256,257],[0,1]):fixtures.append(('gate',dict(selector=selector,payload=0,hw_mode=3,cache=1,hook=0,trim=0,busy=busy,irq=1)))
rows=[]
for name,f in fixtures:
 stock=run(False,name,f);source=run(True,name,f)
 if stock!=source:args.output.with_suffix('.failure.json').write_text(json.dumps(dict(function=name,fixture=f,stock=stock,source=source),indent=2));raise AssertionError((name,f,stock,source))
 rows.append(dict(function=name,fixture=f,result=stock))
used={p+i for p,b in trace.items() for i in range(len(bytes.fromhex(b)))}
for p,b in trace.items():assert blob[p-0x410000:p-0x410000+len(bytes.fromhex(b))]==bytes.fromhex(b)
result=dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),stock_sha256=hashlib.sha256(blob).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),body_coverage={k:dict(start=hex(lo),end_exclusive=hex(hi),visited_bytes=len(used&set(range(lo,hi))),body_bytes=hi-lo) for k,(_,lo,hi) in entries.items()},original_trace={hex(p):b for p,b in sorted(trace.items())},comparisons=rows,limits=['TON event, begin/end, gate, installed trim apply, native gate writer and delay bodies execute compiled source/original instructions. Only resident ROM40 cycle-wait is controlled; no physical elapsed time claim.','Gate C API is void: original R0 is popped caller R7 and is ignored by recovered callers. R1-R3 scratch effects are not compared in this C-interface suite; root ABI suite compares its enclosing root registers.','Nine configuration bytes are explicit source data; alternative table second-selector branches remain outside locked-data coverage.'])
args.output.write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(rows),result['body_coverage'])
