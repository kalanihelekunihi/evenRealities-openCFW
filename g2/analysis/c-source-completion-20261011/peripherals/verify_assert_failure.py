#!/usr/bin/env python3
"""Stock/source FreeRTOS assertion fault-prefix comparison."""
from pathlib import Path
import subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn import arm_const as A
R=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parent;S=R/'g2/components/audio/thread_new_source_candidate/assert_failure.c';O=D/'assert-failure-m4.o';E=D/'assert-failure-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_mask_save=0x101001','-o',str(E),str(O)],check=True)
with E.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(a,n)
 if stock:u.mem_write(0x438000,B)
 else:
  for a,d in seg:u.mem_write(a,d)
 u.reg_write(A.UC_ARM_REG_R0,0);u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x100f01)
 events=[]
 def code(cpu,pc,size,user):
  if pc==(0x5fa0a4 if stock else 0x101000):
   events.append('mask_save');cpu.reg_write(A.UC_ARM_REG_R0,0);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
 def mem(cpu,access,address,size,value,user):
  events.append(['fault_write',address,size,value]);return False
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,mem)
 try:u.emu_start((0x47ebf8 if stock else sy['g2_thread_assert_failure'])|1,0,count=80)
 except Exception:pass
 return events
old=run(True);new=run(False);assert old==new,(old,new)
out={'status':'PASS_ASSERT_FAILURE_PREFIX','cases':1,'events':old,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':'Only authenticated mask call and invalid write prefix; fatal loop/physical fault not executed.'}
(D/'assert-failure-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
