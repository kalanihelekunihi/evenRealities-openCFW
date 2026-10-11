#!/usr/bin/env python3
"""Bounded stock/source Apollo osDelay comparison with selected IRQ/suspend/yield C."""
from pathlib import Path
import hashlib, itertools, json, struct, subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BLOB=OTA.read_bytes()[0x20:]
SOURCES=[ROOT/'g2/components/audio/scheduler_delay_candidate/delay.c',
         ROOT/'g2/components/audio/source_candidate_20261010/context_yield_provider.c',
         ROOT/'g2/components/audio/source_candidate_20261010/scheduler_suspend_provider.c',
         ROOT/'g2/components/audio/source_candidate_20261010/yield_provider.c']
objects=[]
for i,source in enumerate(SOURCES):
 obj=OUT/f'delay-oracle-{i}.o';objects.append(obj)
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(source),'-o',str(obj)],check=True)
elf=OUT/'delay-oracle.elf'
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','audio_delay','--defsym=audio_add_current_to_delayed=0x101001','--defsym=audio_resume=0x101011','--defsym=audio_delay_scheduler_assert=0x101021','-o',str(elf),*map(str,objects)],check=True)
with elf.open('rb') as f:
 e=ELFFile(f); seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}

def run(stock,ipsr,primask,basepri,ticks,resume):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in [(0x438000,(len(BLOB)+0xfff)&~0xfff),(0x100000,0x10000),(0x20000000,0x80000),(0xe000e000,0x2000)]:u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in seg:u.mem_write(base,data)
 u.mem_write(0x20074a3c,struct.pack('<I',1))
 u.mem_write(0x20074a58,struct.pack('<I',0))
 u.reg_write(A.UC_ARM_REG_R0,ticks);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x100f01)
 u.reg_write(A.UC_ARM_REG_IPSR,ipsr);u.reg_write(A.UC_ARM_REG_PRIMASK,primask);u.reg_write(A.UC_ARM_REG_BASEPRI,basepri)
 events=[];writes=[];done=[False]
 def code(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  entries={0x455fa8 if stock else 0x101000:'block',0x454dcc if stock else 0x101010:'resume'}
  if pc in entries:
   name=entries[pc];events.append((name,cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
   cpu.reg_write(A.UC_ARM_REG_R0,resume if name=='resume' else 0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 def write(cpu,access,addr,size,value,user):
  if addr in (0x20074a58,0xe000ed04):writes.append((addr,size,value))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 try:u.emu_start((0x449376 if stock else sy['audio_delay'])|1,0,count=500)
 except Exception:
  print("FAILPC",stock,hex(u.reg_read(A.UC_ARM_REG_PC)),hex(sy['audio_delay']));raise
 assert done[0]
 return dict(status=u.reg_read(A.UC_ARM_REG_R0),events=events,writes=writes,
             suspended=struct.unpack('<I',u.mem_read(0x20074a58,4))[0],sp=u.reg_read(A.UC_ARM_REG_SP))
rows=[]
for ipsr,primask,basepri,ticks,resume in itertools.product((0,1),(0,1),(0,0x30),(0,1,33,0xffffffff),(0,1)):
 f=dict(ipsr=ipsr,primask=primask,basepri=basepri,ticks=ticks,resume=resume)
 a=run(True,**f);b=run(False,**f)
 if a!=b:
  (OUT/'delay-oracle-failure.json').write_text(json.dumps({'fixture':f,'stock':a,'source':b},indent=2)+'\n')
  raise AssertionError(f)
 rows.append({'fixture':f,'result':a})
receipt={'status':'PASS_BOUNDED_DELAY','cases':len(rows),'source_sha256':hashlib.sha256(SOURCES[0].read_bytes()).hexdigest(),
 'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
 'limits':'Selected IRQ context, suspend and yield C execute. Delayed-list and resume child entries are cut with controlled ABI returns; suspended-scheduler fatal path excluded. No physical elapsed time or full scheduler claim.', 'rows':rows}
(OUT/'delay-oracle-results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],receipt['cases'])
