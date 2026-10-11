#!/usr/bin/env python3
"""Bounded stock/source event-signal wrapper comparison."""
from pathlib import Path
import itertools,json,hashlib,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
ELF=OUT/'log-transport-m4.elf';SRC=ROOT/'g2/components/main/extended_log_runtime_candidate/transport.c'
with ELF.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,handle,bits,isr,published,woken):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in [(0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x10000),(0x20000000,0x80000),(0xe000e000,0x2000)]:u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in seg:u.mem_write(base,data)
 u.reg_write(A.UC_ARM_REG_R0,handle);u.reg_write(A.UC_ARM_REG_R1,bits);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x100f01)
 events=[];writes=[];done=[False]
 targets={'irq':(0x44900e,0x101040),'set_isr':(0x47ee4a,0x101060),'get':(0x47ed64,0x101070),'set_task':(0x47ed76,0x101050)}
 def code(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  for name,(old,new) in targets.items():
   if pc!=(old if stock else new):continue
   if name=='irq':events.append([name]);value=isr
   elif name=='set_isr':
    r2=cpu.reg_read(A.UC_ARM_REG_R2);events.append([name,cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)]);cpu.mem_write(r2,struct.pack('<I',woken));value=published
   else:events.append([name,cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1) if name=='set_task' else None]);value=3
   cpu.reg_write(A.UC_ARM_REG_R0,value);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
 def write(cpu,access,addr,size,value,user):
  if addr==0xe000ed04:writes.append([addr,size,value])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((0x4495e4 if stock else sy['g2_log_transport_signal'])|1,0,count=180)
 assert done[0]
 return {'events':events,'writes':writes,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for handle,bits,isr,published,woken in itertools.product((0,0x20011000),(1,0xff000001),(0,1),(0,1),(0,1)):
 if handle==0 or bits&0xff000000:
  if isr or published or woken:continue
 elif isr==0 and (published or woken):continue
 f=dict(handle=handle,bits=bits,isr=isr,published=published,woken=woken)
 a=run(True,**f);b=run(False,**f)
 if a!=b:
  (OUT/'log-signal-failure.json').write_text(json.dumps({'fixture':f,'stock':a,'source':b},indent=2)+'\n');raise AssertionError(f)
 rows.append({'fixture':f,'result':a})
receipt={'status':'PASS_LOG_SIGNAL_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),'limits':'IRQ-context and event-group children cut at typed entries; task/ISR return ignored by logger caller. Event lists/queue publication not executed.'}
(OUT/'log-signal-results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(rows))
