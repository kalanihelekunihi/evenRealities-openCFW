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
trace={}
def run(source,name,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,sz in [(0x410000,0x25000),(0x08000000,0x20000),(0x10000,0x10000),(0x30000,0x10000),(0x20000000,0x40000),(0xe000e000,0x1000),(0xe001e000,0x1000)]:u.mem_map(lo,sz)
 if source:
  for seg in segments:u.mem_write(seg['address'],seg['data'])
 else:u.mem_write(0x410000,blob)
 def w(p,x):u.mem_write(p,struct.pack('<I',x&0xffffffff))
 w(0xe000ed14,f.get('scr',0));w(0xe001e300,f.get('value',0));u.mem_write(0x20001000,b'\xa5'*4)
 if name not in ['read','write']:w(0x20026e38+int(name,16),0x08000101 if f['present'] else 0)
 events=[];writes=[];done=False
 def hook(cpu,p,size,_):
  nonlocal done
  if p==0x08000000:done=True;u.emu_stop();return
  if not source and 0x410000<=p<0x435000:trace[p]=bytes(u.mem_read(p,size)).hex()
  if p==0x08000100:
   events.append([u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)] if name=='24' else ['noarg'])
   u.reg_write(a.UC_ARM_REG_R0,f['status']);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR))
 def write(cpu,access,p,size,value,_):writes.append([p,size,value&((1<<(8*size))-1)])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xe000e000,end=0xe001efff)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001);u.reg_write(a.UC_ARM_REG_R0,0x20001000 if name=='read' else f.get('arg',0));u.reg_write(a.UC_ARM_REG_R1,f.get('second',0));u.reg_write(a.UC_ARM_REG_PRIMASK,f.get('irq',0))
 pc=(symbols[entries[name][0]]&~1) if source else entries[name][1];u.emu_start(pc|1,0,count=1000);assert done
 return dict(ret=None if name=='read' else u.reg_read(a.UC_ARM_REG_R0),writes=writes,events=events,output=bytes(u.mem_read(0x20001000,4)).hex(),irq=u.reg_read(a.UC_ARM_REG_PRIMASK))
fixtures=[]
for scr,arg,value,irq in itertools.product([0,0x10000,0x20000,0x30000,0xffffffff],[0,1,2,3,4,0x103,0x030201,0xffffff,0xffffffff],[0,0xffffffff],[0,1]):fixtures.append(('write',dict(scr=scr,arg=arg,value=value,irq=irq)))
for x,y,z in itertools.product(range(4),repeat=3):
 for rest in [0,0xfffffccc]:fixtures.append(('read',dict(value=(x<<8)|(y<<4)|z|rest)))
for name in ['20','24','28','30','34','38']:
 for present,status,first,second,irq in itertools.product([False,True],[0,7,0xffffffff],[0,0x101,0xffffffff],[0,0x103,0xffffffff],[0,1]):fixtures.append((name,dict(present=present,status=status,arg=first,second=second,irq=irq)))
rows=[]
for name,f in fixtures:
 stock=run(False,name,f);source=run(True,name,f)
 if stock!=source:args.output.with_suffix('.failure.json').write_text(json.dumps(dict(name=name,fixture=f,stock=stock,source=source),indent=2));raise AssertionError((name,f,stock,source))
 rows.append(dict(name=name,fixture=f,result=stock))
used={p+i for p,b in trace.items() for i in range(len(bytes.fromhex(b)))}
for p,b in trace.items():assert blob[p-0x410000:p-0x410000+len(bytes.fromhex(b))]==bytes.fromhex(b)
r=dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=hashlib.sha256(blob).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_trace={hex(p):b for p,b in sorted(trace.items())},visited_body_bytes={name:len(used&set(range(lo,hi))) for name,(_,lo,hi) in entries.items()},comparisons=rows,limits=['Native original/source leaves; only registered callback bodies controlled. No SRAM write hooks. MMIO is mapped memory, not hardware.','No-argument callback registers are unspecified; comparison records call occurrence/status only. Two-byte callback arguments compare exactly.','Standalone prerequisite module; initializer and integrated-image reachability not established.'])
args.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows),r['visited_body_bytes'])
