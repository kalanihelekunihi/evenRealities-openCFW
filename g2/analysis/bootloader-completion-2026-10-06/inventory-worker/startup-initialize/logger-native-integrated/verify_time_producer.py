from pathlib import Path
import json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn import arm_const as a
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());c=json.loads((N/'current-candidate.json').read_text());elf=R/c['directory']/'candidate.elf';blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
with elf.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for tick,ipsr,primask,basepri in itertools.product([0,1,1234,0x7fffffff,0x80000000,0xffffffff],[0,16],[0,1],[0,48]):
 pair=[]
 for stock in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
  for p,n in [(0x410000,0x30000),(0x10000,0x10000),(0x30000,0x30000),(0x8000000,4096),(0x20000000,0x40000)]:u.mem_map(p,n)
  if stock:u.mem_write(0x410000,blob)
  else:
   for p,b in segs:u.mem_write(p,b)
  u.mem_write(0x20026f18,b'\xa5'*28);u.mem_write(0x20027148,struct.pack('<I',tick));u.mem_write(0x20027150,struct.pack('<I',1));u.mem_write(0x2000053c,struct.pack('<I',0x20004000));u.mem_write(0x20004000,b'.\0')
  u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_XPSR,0x1000000|ipsr);u.reg_write(a.UC_ARM_REG_PRIMASK,primask);u.reg_write(a.UC_ARM_REG_BASEPRI,basepri)
  for i in range(4,12):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),0xaac000+i)
  done=[False]
  def code(cpu,pc,size,_):
   if pc==0x8000000:done[0]=True;u.emu_stop()
  u.hook_add(UC_HOOK_CODE,code);u.emu_start((0x41a6aa if stock else sy['elog_port_get_time'])|1,0,count=20000);assert done[0]
  pair.append(dict(pointer=u.reg_read(a.UC_ARM_REG_R0),buffer=bytes(u.mem_read(0x20026f18,28)).hex(),sp=u.reg_read(a.UC_ARM_REG_SP),saved=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],primask=u.reg_read(a.UC_ARM_REG_PRIMASK),basepri=u.reg_read(a.UC_ARM_REG_BASEPRI)))
 if pair[0]!=pair[1]:(N/'time-producer-failure.json').write_text(json.dumps(dict(fixture=[tick,ipsr,primask,basepri],original=pair[0],source=pair[1]),indent=2));raise AssertionError((tick,ipsr,primask,basepri))
 expected=str(tick if tick<0x80000000 else tick-0x100000000).encode()+b'\0';assert bytes.fromhex(pair[0]['buffer']).startswith(expected)
 rows.append(dict(fixture=[tick,ipsr,primask,basepri],result=pair[0]))
r=dict(status='PASS_ORIGINAL_NATIVE_TIME_PRODUCER_AND_FORMATTER',cases=len(rows),candidate_sha256=c['sha256'],comparisons=rows,limits=['Actual original/native get_time and snprintf/formatter instructions, original CMSIS context-guard/tick query. Coherent raw tick RAM, no actual clock or scheduler delivery.','Tick count is formatted signed%d into fixed20026f18 buffer28; units are scheduler ticks. No milliseconds relationship established.']);(N/'time-producer-comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
