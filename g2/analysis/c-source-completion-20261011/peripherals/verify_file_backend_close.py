#!/usr/bin/env python3
"""Bounded stock/source littlefs backend close wrapper ABI."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/audio/file_backend_close_candidate/backend_close.c';OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
OBJ=OUT/'backend-close-m4.o';ELF=OUT/'backend-close-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(SRC),'-o',str(OBJ)],check=True)
defs=['g2_lfs_mlist_isopen=0x101001','g2_lfs_file_close=0x101011','g2_file_close_error=0x101021']
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={x}' for x in defs],'-o',str(ELF),str(OBJ)],check=True)
with ELF.open('rb') as f:
 e=ELFFile(f);SEG=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];SY={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,isopen,result):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in SEG:u.mem_write(base,data)
 u.mem_write(0x20010028,(0x20014400).to_bytes(4,'little'))
 for reg,val in ((A.UC_ARM_REG_R0,0x20010000),(A.UC_ARM_REG_R1,0x20012200),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,val)
 events=[];done=[False]
 old={0x4cb082:'open',0x4d09b4:'error',0x4cdce4:'close'};new={0x101000:'open',0x101020:'error',0x101010:'close'}
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  name=(old if stock else new).get(pc)
  if name:
   args=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1)]
   if name=='error':args.append(cpu.reg_read(A.UC_ARM_REG_R2))
   events.append([name,args]);cpu.reg_write(A.UC_ARM_REG_R0,isopen if name=='open' else result if name=='close' else 0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x4cfad0 if stock else SY['audio_file_backend_close'])|1,0,count=500)
 assert done[0]
 return {'r0':u.reg_read(A.UC_ARM_REG_R0),'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for isopen in (0,1):
 for result in (0,0xffffffff):
  a=run(True,isopen,result);b=run(False,isopen,result)
  if a!=b:
   f={'isopen':isopen,'result':result};(OUT/'backend-close-failure.json').write_text(json.dumps({'fixture':f,'stock':a,'source':b},indent=2)+'\n');raise AssertionError(f)
  rows.append({'isopen':isopen,'result':result})
receipt={'status':'PASS_FILE_BACKEND_CLOSE_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'limits':'littlefs isopen, diagnostic and close children cut; no actual filesystem mutation or fatal behavior proof.'}
(OUT/'backend-close-results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(rows))
