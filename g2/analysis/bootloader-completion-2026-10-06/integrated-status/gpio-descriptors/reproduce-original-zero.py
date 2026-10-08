import importlib.util
from pathlib import Path
from unicorn import arm_const as a,UC_HOOK_CODE
p=Path('g2/components/bootloader/initializer_callbacks/verify_context_interrupt.py');s=importlib.util.spec_from_file_location('v',p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
m=v.Machine(False);cnt=[0]
def debug(uc,pc,size,user):
 if pc in [0x417c3a,0x417c42] and cnt[0]<10:
  print(hex(pc),hex(uc.reg_read(a.UC_ARM_REG_R1)),hex(uc.reg_read(a.UC_ARM_REG_XPSR)));cnt[0]+=1
m.cpu.hook_add(UC_HOOK_CODE,debug)
for reg,value in [(a.UC_ARM_REG_R0,0x20010000),(a.UC_ARM_REG_R1,28),(a.UC_ARM_REG_R2,0),(a.UC_ARM_REG_SP,v.SP),(a.UC_ARM_REG_LR,v.STOP|1)]:m.cpu.reg_write(reg,value)
m.cpu.emu_start(0x415ff5,v.STOP+2,count=100);print(m.done)
