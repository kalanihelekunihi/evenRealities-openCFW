#!/usr/bin/env python3
"""Bounded original/source TCB initialization and child ABI oracle."""
from pathlib import Path
import subprocess,hashlib,json
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/thread_new_source_candidate/initialize_tcb.c';O=D/'initialize-tcb-m4.o';E=D/'initialize-tcb-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
syms={'g2_log_stack_fill':0x101001,'g2_thread_initialize_stack':0x101011,'g2_thread_assert_failure':0x101021}
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}={v:#x}' for k,v in syms.items()],'-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];named={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,name,priority):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 u.mem_write(0x20012030,(0x20013000).to_bytes(4,'little'))
 u.mem_write(0x20015000,name+b'\0')
 sp=0x2007f000
 for i,v in enumerate((priority,0x20014000,0x20012000,0)):
  u.mem_write(sp+4*i,v.to_bytes(4,'little'))
 for reg,v in ((A.UC_ARM_REG_R0,0x20016001),(A.UC_ARM_REG_R1,0x20015000),(A.UC_ARM_REG_R2,64),(A.UC_ARM_REG_R3,0x20017000),(A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,v)
 events=[];done=[False];old={0x43c0e4:'fill',0x44215a:'stack'};new={0x101000:'fill',0x101010:'stack'}
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  n=(old if stock else new).get(pc)
  if n:
   args=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   events.append([n,args[:3] if n=='fill' else args]);
   if n=='fill':cpu.mem_write(args[0],bytes([args[2]&255])*args[1])
   cpu.reg_write(A.UC_ARM_REG_R0,0x20013e00 if n=='stack' else args[0]);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x454938 if stock else named['g2_thread_initialize_tcb'])|1,0,count=1200)
 assert done[0]
 return {'tcb':u.mem_read(0x20012000,0x70).hex(),'stack_sha':hashlib.sha256(u.mem_read(0x20013000,256)).hexdigest(),'created':u.mem_read(0x20014000,4).hex(),'events':events,'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for name in (b'a',b'long task name',b'abcdefghijklmnopqrstuvwxyz0123456789'):
 for priority in (0,7,55):
  a=run(True,name,priority);b=run(False,name,priority);assert a==b,(name,priority,a,b);rows.append([name.decode(),priority])
out={'status':'PASS_INITIALIZE_TCB_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Successful priorities, 64-word stack, selected fill and port stack-init effects cut. Invalid priority and context switch excluded.'}
(D/'initialize-tcb-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
