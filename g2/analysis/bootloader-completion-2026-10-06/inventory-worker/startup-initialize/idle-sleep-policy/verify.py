"""Compare locked original instructions with compiled reconstruction; no call stubs."""
from pathlib import Path
import json,hashlib,random,itertools
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
blob=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin';raw=blob.read_bytes();elf=Path('/tmp/opencfw-sleep-policy.elf');payloads=[]
with elf.open('rb') as f:
 e=ELFFile(f);syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for seg in e.iter_segments():
  if seg['p_type']=='PT_LOAD':payloads.append((seg['p_vaddr'],seg.data()))
covered=set();rows=[]
def run(pc,mem,original):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
 for a,n in [(0x410000,0x30000),(0x08000000,0x10000),(0x20000000,0x40000)]:u.mem_map(a,n)
 u.mem_write(0x410000,raw)
 for a,b in payloads:u.mem_write(a,b)
 for a,v in mem.items():u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 u.reg_write(UC_ARM_REG_SP,0x2003fff0);u.reg_write(UC_ARM_REG_LR,0x0800ff01)
 def hook(u,a,size,x):
  if a==0x0800ff00:u.emu_stop()
  elif original:covered.update(range(a,a+size))
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(pc|1,0,count=100);assert u.reg_read(UC_ARM_REG_PC)==0x0800ff00
 return u.reg_read(UC_ARM_REG_R0)
for name,pc in [('expected_idle_ticks',0x4181e4),('confirm_sleep',0x418a00)]:
 for i,vals in enumerate(itertools.product([0,1],[0,1],[0,1,2,3],[0,1],[0,1],[0,1])):
  top,prio,ready,pending,yielded,ticks=vals
  mem={0x2002714c:top,0x20027134:0x20030000,0x2003002c:prio,0x20024870:ready,0x20027164:[10,0xffffffff,0][i%3],0x20027148:[0,9,0xffffffff][i%3],0x20026f5c:pending,0x20027158:yielded,0x20027154:ticks,0x20026f84:i%4,0x20027144:(i//4)%4}
  a=run(pc,mem,True);b=run(syms[name],mem,False);assert a==b,(name,i,a,b);rows.append(dict(function=name,case=i,result=a))
for total,suspended in [(2,1),(1,0),(0,0xffffffff)]:
 mem={0x20026f5c:0,0x20027158:0,0x20027154:0,0x20026f84:suspended,0x20027144:total}
 a=run(0x418a00,mem,True);b=run(syms['confirm_sleep'],mem,False);assert a==b==2;rows.append(dict(function='confirm_sleep',case='all-other-tasks-suspended-'+str(total),result=a))
out=dict(status='PASS',cases=len(rows),blob_sha256=hashlib.sha256(raw).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),ranges=[dict(start=hex(a),end=hex(b),bytes=b-a,covered=sum(x in covered for x in range(a,b))) for a,b in [(0x4181e4,0x418228),(0x418a00,0x418a44)]],limits=['Static coherent/noncoherent snapshot fixtures, finite instruction paths; no concurrent scheduler changes, timing, idle-entry integration or hardware proof.','No external-call stubs: both functions are leaf routines.'],results=rows)
(HERE/'comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['cases'],out['ranges'])
