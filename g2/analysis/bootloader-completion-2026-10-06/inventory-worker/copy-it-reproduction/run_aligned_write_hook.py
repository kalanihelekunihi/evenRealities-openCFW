import json,hashlib
from pathlib import Path
from unicorn import *
from unicorn import arm_const as a
from elftools.elf.elffile import ELFFile
p=Path('/tmp/opencfw-copy-aligned.elf')
with p.open('rb') as f:
 e=ELFFile(f);text=e.get_section_by_name('.text');code=text.data();entry=e.header.e_entry
rows=[]
for name,mode in [('CORTEX_M33',UC_MODE_THUMB|UC_MODE_MCLASS),('CORTEX_M7',UC_MODE_THUMB|UC_MODE_MCLASS),('CORTEX_A9',UC_MODE_THUMB)]:
 for hook in [False,True]:
  for value in [4,8,12,16,20,24,28,32]:
   u=Uc(UC_ARCH_ARM,mode);u.ctl_set_cpu_model(getattr(a,'UC_CPU_ARM_'+name));u.mem_map(0x10000,4096);u.mem_write(0x10000,code);u.mem_map(0x20000000,4096);u.mem_map(0x8000000,4096);u.mem_write(0x20000100,b'\x31\x32\x33\x34');u.reg_write(a.UC_ARM_REG_SP,0x20000f00);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_R0,0x20000200);u.reg_write(a.UC_ARM_REG_R1,0x20000100);u.reg_write(a.UC_ARM_REG_R2,value);trace=[]
   if hook:u.hook_add(UC_HOOK_CODE,lambda cpu,pc,n,z:trace.append({'pc':hex(pc),'r0':hex(cpu.reg_read(a.UC_ARM_REG_R0)),'cpsr':hex(cpu.reg_read(a.UC_ARM_REG_CPSR))}))
   u.hook_add(UC_HOOK_MEM_WRITE,lambda *args:None)
   u.emu_start(entry|1,0x8000000,count=100);r=u.reg_read(a.UC_ARM_REG_R0);rows.append({'model':name,'hook':hook,'r2':value,'return':hex(r),'movs_zero_executed':r==0,'trace':trace})
r={'scope':'Independent assembled conditional-load/store tail plus caller MOVS0; no firmware or expected-answer stubs','elf_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'unicorn_version':__import__('unicorn').__version__,'comparisons':rows};Path(__file__).with_name('aligned-write-hook-result.json').write_text(json.dumps(r,indent=2)+'\n');print([(x['model'],x['hook'],x['r2'],x['return']) for x in rows])
