#!/usr/bin/env python3
"""Original/source Cortex-M task startup frame comparison."""
from pathlib import Path
import subprocess,hashlib,json
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/thread_new_source_candidate/initialize_stack.c';O=D/'initialize-stack-m4.o';E=D/'initialize-stack-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,top,base,entry,arg):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 for reg,v in ((A.UC_ARM_REG_R0,top),(A.UC_ARM_REG_R1,base),(A.UC_ARM_REG_R2,entry),(A.UC_ARM_REG_R3,arg),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x44215a if stock else sy['g2_thread_initialize_stack'])|1,0,count=120)
 assert done[0]
 return {'top':u.reg_read(A.UC_ARM_REG_R0),'frame':u.mem_read(top-72,72).hex(),'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for top in (0x20012080,0x20012100):
 for base in (0x20012000,0x20012020):
  for arg in (0,0x12345678):
   a=run(True,top,base,0x00445001,arg);b=run(False,top,base,0x00445001,arg);assert a==b,(top,base,arg,a,b);rows.append([hex(top),hex(base),hex(arg)])
out={'status':'PASS_INITIALIZE_STACK_FRAME','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Synthetic aligned stack; context switch and exception return not exercised.'}
(D/'initialize-stack-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
