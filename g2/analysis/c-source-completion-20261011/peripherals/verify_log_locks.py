#!/usr/bin/env python3
"""Compare logger lock wrappers to stock through named mutex child cuts."""
from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/main/extended_log_runtime_candidate/locks.c';OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
OBJ=OUT/'log-locks-m4.o';ELF=OUT/'log-locks-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(SRC),'-o',str(OBJ)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_mutex_acquire=0x101001','--defsym=audio_mutex_release=0x101011','-o',str(ELF),str(OBJ)],check=True)
with ELF.open('rb') as f:
 e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,mode,handle,child_return):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 u.mem_map(0x438000,(len(BLOB)+4095)&~4095);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x80000)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in segs:u.mem_write(base,data)
 u.mem_write(0x20074578,handle.to_bytes(4,'little'))
 u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x100f01)
 event=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  target=(0x4497b6 if mode=='enter' else 0x44981c) if stock else (0x101000 if mode=='enter' else 0x101010)
  if pc==target:
   event.append([mode,cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1) if mode=='enter' else None]);cpu.reg_write(A.UC_ARM_REG_R0,child_return);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 entry=(0x44aa98 if mode=='enter' else 0x44aaa0) if stock else sy['g2_log_lock_'+mode]
 u.emu_start(entry|1,0,count=80)
 assert done[0]
 return {'events':event,'sp':u.reg_read(A.UC_ARM_REG_SP),'mutex':int.from_bytes(u.mem_read(0x20074578,4),'little')}
rows=[]
for mode,handle,child_return in itertools.product(('enter','exit'),(0,0x20001000,0x20001001,0xffffffff),(0,1,0xfffffffe)):
 a=run(True,mode,handle,child_return);b=run(False,mode,handle,child_return)
 if a!=b:raise AssertionError((mode,hex(handle),child_return,a,b))
 rows.append({'mode':mode,'handle':handle,'child_return':child_return,'result':a})
receipt={'status':'PASS_LOG_LOCK_WRAPPERS','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),'limits':'Mutex acquire/release child effects are cut; selected audio mutex source is separately compiled and linked, not executed here. Synthetic RAM only.'}
(OUT/'log-locks-results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(rows))
