#!/usr/bin/env python3
"""Bounded stock/source static task constructor, valid caller memory."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/audio/thread_new_source_candidate/static_create.c';OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
OBJ=OUT/'static-create-m4.o';ELF=OUT/'static-create-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(SRC),'-o',str(OBJ)],check=True)
defs=['g2_thread_assert_failure=0x101001','g2_thread_initialize_tcb=0x101011','g2_thread_schedule_tcb=0x101021']
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={x}' for x in defs],'-o',str(ELF),str(OBJ)],check=True)
with ELF.open('rb') as f:
 e=ELFFile(f);SEG=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];SY={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,depth,priority):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in SEG:u.mem_write(base,data)
 sp=0x2007f000;stack=0x20010000;tcb=0x20012000;u.mem_write(tcb,b'\xaa'*0x70)
 def w(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def r(a):return int.from_bytes(u.mem_read(a,4),'little')
 w(sp,priority);w(sp+4,stack);w(sp+8,tcb)
 for reg,val in ((A.UC_ARM_REG_R0,0x20015001),(A.UC_ARM_REG_R1,0x20016000),(A.UC_ARM_REG_R2,depth),(A.UC_ARM_REG_R3,0x20017000),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,val)
 events=[];done=[False]
 old={0x454938:'init',0x4549fc:'schedule'};new={0x101010:'init',0x101020:'schedule'}
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  if pc==0x101000:raise AssertionError('unexpected assertion')
  name=(old if stock else new).get(pc)
  if name:
   regs=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if name=='init':
    ss=cpu.reg_read(A.UC_ARM_REG_SP);extra=[r(ss+4*i) for i in range(4)];w(extra[1],0x20017700);events.append([name,regs+extra[:1]+extra[2:]])
   else:events.append([name,regs[0]])
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x454820 if stock else SY['audio_daemon_create_static'])|1,0,count=1000)
 assert done[0]
 return {'r0':u.reg_read(A.UC_ARM_REG_R0),'events':events,'tcb':bytes(u.mem_read(tcb,0x70)).hex(),'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for depth,priority in ((1,1),(1024,54),(65536,56)):
 a=run(True,depth,priority);b=run(False,depth,priority)
 if a!=b:
  f={'depth':depth,'priority':priority};(OUT/'static-create-failure.json').write_text(json.dumps({'fixture':f,'stock':a,'source':b},indent=2)+'\n');raise AssertionError(f)
 rows.append({'depth':depth,'priority':priority})
result={'status':'PASS_STATIC_CREATE_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'limits':'Valid caller TCB/stack; TCB init and scheduler insert cut. Assertion, live task execution and ownership untested.'}
(OUT/'static-create-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(rows))
