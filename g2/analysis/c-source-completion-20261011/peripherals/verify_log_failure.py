#!/usr/bin/env python3
"""Stock/source bounded 0x4733ee callback/variadic ABI comparison."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/main/extended_log_runtime_candidate/transport_failure.c'
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
OBJ=OUT/'log-failure-m4.o';ELF=OUT/'log-failure-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(SRC),'-o',str(OBJ)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_log_transport_vformat_unbounded=0x101001','-o',str(ELF),str(OBJ)],check=True)
with ELF.open('rb') as f:
 e=ELFFile(f);SEG=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];SY={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,installed,args):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in SEG:u.mem_write(base,data)
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 w(0x200742f0,0x101021 if installed else 0)
 sp=0x2007f000
 for reg,val in ((A.UC_ARM_REG_R0,0x71e990 if stock else SY['g2_log_transport_queue_failure_message']),(A.UC_ARM_REG_R1,args[0]),(A.UC_ARM_REG_R2,args[1]),(A.UC_ARM_REG_R3,args[2]),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,val)
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  if pc==(0x473036 if stock else 0x101000):
   a=cpu.reg_read(A.UC_ARM_REG_R2)
   words=[int.from_bytes(cpu.mem_read(a+4*i,4),'little') for i in range(3)]
   events.append(['format',cpu.reg_read(A.UC_ARM_REG_R0),bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_R1),53)).split(b'\x00')[0].decode(),words])
   cpu.mem_write(0x2006b930,b'Q\x00');cpu.reg_write(A.UC_ARM_REG_R0,17);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
  if pc==0x101020:
   events.append(['emit',cpu.reg_read(A.UC_ARM_REG_R0),bytes(cpu.mem_read(0x2006b930,2)).hex()]);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4733ee if stock else SY['g2_log_transport_queue_failure'])|1,0,count=500)
 assert done[0],(stock,installed)
 return {'r0':u.reg_read(A.UC_ARM_REG_R0),'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for installed,args in ((0,(1,2,3)),(1,(1,2,3)),(1,(0xffffffff,0x12345678,0))):
 a=run(True,installed,args);b=run(False,installed,args)
 if a!=b:
  (OUT/'log-failure-failure.json').write_text(json.dumps({'installed':installed,'args':args,'stock':a,'source':b},indent=2)+'\n');raise AssertionError((installed,args))
 rows.append({'installed':installed,'arguments':args,'result':a})
receipt={'status':'PASS_LOG_FAILURE_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'limits':'Underlying 0x473036 formatter and installed callback cut; compares variadic ABI, product string, buffer, event order and return.'}
(OUT/'log-failure-results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(rows))
