from pathlib import Path
import json,hashlib,random
from elftools.elf.elffile import ELFFile
from unicorn import *
import unicorn.arm_const as a
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
c=json.loads((HERE/'current-candidate.json').read_text());elf=ROOT/c['directory']/'candidate.elf';b=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with elf.open('rb') as f:
 e=ELFFile(f);segs=[(int(s['p_vaddr']),s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:int(s['st_value']) for s in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,bits,fpscr=0):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for base,size in [(0x10000,0x10000),(0x30000,0x10000),(0x50000,0x10000),(0x410000,0x30000),(0x20000000,0x40000),(0x8000000,0x1000)]:u.mem_map(base,size)
 if stock:u.mem_write(0x410000,b)
 else:
  for base,data in segs:u.mem_write(base,data)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_FPSCR,fpscr);u.reg_write(a.UC_ARM_REG_S0,bits);u.reg_write(a.UC_ARM_REG_R0,bits)
 initial_readback=u.reg_read(a.UC_ARM_REG_FPSCR)
 done=[False]
 def hook(cpu,pc,size,data):
  if pc==0x8000000:done[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x427e0c if stock else sy['event_a_temperature_classify_bits'])|1,0,count=1000);assert done[0]
 return u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_FPSCR),initial_readback
bits=[0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x00800000,0x80800000,0x7f800000,0xff800000,0x7fc00000,0xffc00000,0x7f800001,0xff800001,0x7fffffff,0xffffffff,0xc1a00000,0x42480000]
rows=[]
for mode in [0,1<<24,1<<25,3<<24,0x9f,(3<<24)|0x9f]:
 for value in bits:
  x,xf,xi=run(True,value,mode);y,yf,yi=run(False,value,mode);rows.append(dict(bits=hex(value),requested_fpscr=hex(mode),stock_initial_readback=hex(xi),source_initial_readback=hex(yi),stock_bucket=x,source_bucket=y,stock_fpscr=hex(xf),source_fpscr=hex(yf),bucket_match=x==y,cumulative_flags_match=(xf&0x9f)==(yf&0x9f)))
result=dict(status='PASS_EMULATOR_COMPARISON',cases=len(rows),elf_sha256=c['sha256'],results=rows,bucket_mismatches=[r for r in rows if not r['bucket_match']],exception_flag_mismatches=[r for r in rows if not r['cumulative_flags_match']],limits=['Original VCMP/VMRS instructions execute with supplied FPSCR modes in Cortex-M33 Unicorn. No mismatch normalization. FZ/DN and sticky exception behavior are explicitly varied; these emulator observations do not establish physical FPU scheduling or enabled exception-trap behavior.'])
assert all(r['bucket_match'] and r['cumulative_flags_match'] and r['stock_fpscr']==r['source_fpscr'] for r in rows)
(HERE/'classifier-mode-comparison.json').write_text(json.dumps(result,indent=2));print('RECORDED',len(rows),'fixtures;',len(result['bucket_mismatches']),'bucket mismatches;',len(result['exception_flag_mismatches']),'exception flag mismatches')
