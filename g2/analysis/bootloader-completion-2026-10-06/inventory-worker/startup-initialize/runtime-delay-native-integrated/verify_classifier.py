from pathlib import Path
import json,hashlib,random
from elftools.elf.elffile import ELFFile
from unicorn import *
import unicorn.arm_const as a
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
c=json.loads((HERE/'current-candidate.json').read_text());elf=ROOT/c['directory']/'candidate.elf';b=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with elf.open('rb') as f:
 e=ELFFile(f);segs=[(int(s['p_vaddr']),s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:int(s['st_value']) for s in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,bits):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for base,size in [(0x10000,0x10000),(0x30000,0x10000),(0x50000,0x10000),(0x410000,0x30000),(0x20000000,0x40000),(0x8000000,0x1000)]:u.mem_map(base,size)
 if stock:u.mem_write(0x410000,b)
 else:
  for base,data in segs:u.mem_write(base,data)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_FPSCR,0);u.reg_write(a.UC_ARM_REG_S0,bits);u.reg_write(a.UC_ARM_REG_R0,bits)
 done=[False]
 def hook(cpu,pc,size,data):
  if pc==0x8000000:done[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x427e0c if stock else sy['event_a_temperature_classify_bits'])|1,0,count=1000);assert done[0]
 return u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_FPSCR)
rng=random.Random(0x42a878);bits=[0,0x80000000,1,0x80000001,0x7f800000,0xff800000,0x7fc00000,0x7f800001,0xff800001]
for threshold in [0xc3888000,0xc1a00000,0,0x42480000,0x447a0000]:bits.extend([(threshold-1)&0xffffffff,threshold,(threshold+1)&0xffffffff])
bits+= [rng.getrandbits(32) for i in range(128)];rows=[]
for value in bits:
 x,xf=run(True,value);y,yf=run(False,value);assert x==y and xf==yf,(hex(value),x,y,hex(xf),hex(yf));rows.append(dict(bits=hex(value),bucket=x,stock_fpscr=hex(xf),source_fpscr=hex(yf),cumulative_flags_match=(xf&255)==(yf&255)))
(HERE/'classifier-comparison.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=c['sha256'],results=rows,known_cumulative_flag_differences=[r for r in rows if not r['cumulative_flags_match']],limits=['Compare bucket and full FPSCR at default0 with actual native VCMP sequence. Unicorn nondefault control/sticky behavior is independently bounded by the QEMU original-byte/native-object tests. No hardware scheduling/trap proof.']),indent=2));print('PASS',len(rows),'bucket fixtures;',sum(not r['cumulative_flags_match'] for r in rows),'cumulative FPSCR differences')
