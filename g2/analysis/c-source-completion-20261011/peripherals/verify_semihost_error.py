#!/usr/bin/env python3
"""Authenticated semihost BKPT ABI and failure transition comparison."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/semihost_error_candidate/error.c';O=D/'semihost-error-m4.o';E=D/'semihost-error-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,status):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 for reg,v in ((A.UC_ARM_REG_R0,0x71f8e0),(A.UC_ARM_REG_R1,0x70c264),(A.UC_ARM_REG_R2,0x180b),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 events=[];done=[False]
 def code(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop()
 def intr(cpu,num,user):
  op=cpu.reg_read(A.UC_ARM_REG_R0);selector=cpu.reg_read(A.UC_ARM_REG_R1);ptr=cpu.reg_read(A.UC_ARM_REG_R2)
  args=[int.from_bytes(cpu.mem_read(ptr+4*i,4),'little') for i in range(3)] if 0x20000000<=ptr<0x20080000 else ptr
  events.append([op,selector,args if selector==0x21010 else None])
  cpu.reg_write(A.UC_ARM_REG_R0,status);cpu.reg_write(A.UC_ARM_REG_PC,(cpu.reg_read(A.UC_ARM_REG_PC)+2)|1)
  if len(events)==2:cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr)
 u.emu_start((0x4d09b4 if stock else sy['g2_file_close_error'])|1,0,count=180)
 return {'events':events,'returned':done[0]}
rows=[]
for status in (0,1,0xffffffff):
 a=run(True,status);b=run(False,status);assert a==b,(status,a,b);rows.append([status,a])
out={'status':'PASS_SEMIHOST_ERROR_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'BKPT intercepted; successful semihost reply returns, zero reply compared through first repeated SYS_EXIT call. No debugger or physical fatal execution.'}
(D/'semihost-error-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
