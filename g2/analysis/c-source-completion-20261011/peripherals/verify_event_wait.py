#!/usr/bin/env python3
"""Bounded stock/source CMSIS event wait outer status and child ABI."""
from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/audio/event_wait_source_candidate/event_wait.c';OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
OBJ=OUT/'event-wait-m4.o';ELF=OUT/'event-wait-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(SRC),'-o',str(OBJ)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_irq_context=0x101001','--defsym=g2_event_wait_bits=0x101011','-o',str(ELF),str(OBJ)],check=True)
with ELF.open('rb') as f:
 e=ELFFile(f);SEG=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];SY={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,handle,bits,options,timeout,irq,got):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in SEG:u.mem_write(base,data)
 for reg,val in ((A.UC_ARM_REG_R0,handle),(A.UC_ARM_REG_R1,bits),(A.UC_ARM_REG_R2,options),(A.UC_ARM_REG_R3,timeout),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,val)
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  if pc==(0x44900e if stock else 0x101000):events.append(['irq']);cpu.reg_write(A.UC_ARM_REG_R0,irq);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
  if pc==(0x47ebf8 if stock else 0x101010):
   sp=cpu.reg_read(A.UC_ARM_REG_SP)
   events.append(['wait']+[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]+[int.from_bytes(cpu.mem_read(sp,4),'little')])
   cpu.reg_write(A.UC_ARM_REG_R0,got);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x44969c if stock else SY['osEventFlagsWait'])|1,0,count=600)
 assert done[0]
 return {'r0':u.reg_read(A.UC_ARM_REG_R0),'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for handle,bits,options,timeout,irq,got in itertools.product((0,0x20010000),(1,3,0x1000001),(0,1,2,3),(0,10),(0,1),(0,1,3)):
 a=run(True,handle,bits,options,timeout,irq,got);b=run(False,handle,bits,options,timeout,irq,got)
 if a!=b:
  f={'handle':handle,'bits':bits,'options':options,'timeout':timeout,'irq':irq,'got':got}
  (OUT/'event-wait-failure.json').write_text(json.dumps({'fixture':f,'stock':a,'source':b},indent=2)+'\n');raise AssertionError(f)
 rows.append(1)
result={'status':'PASS_EVENT_WAIT_BOUNDED','cases':len(rows),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'limits':'FreeRTOS xEventGroupWaitBits and IRQ context cut; no blocking/waiter scheduling proof.'}
(OUT/'event-wait-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(rows))
