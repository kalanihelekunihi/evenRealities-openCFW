"""Minimal authenticated wrapper/helper execution; no provider or answer stubs."""
import json,hashlib,struct
from pathlib import Path
from unicorn import *
from unicorn import arm_const as a
ROOT=Path(__file__).resolve().parents[5];blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
rows=[]
for name,mode in [('CORTEX_M33',UC_MODE_THUMB|UC_MODE_MCLASS),('CORTEX_M7',UC_MODE_THUMB|UC_MODE_MCLASS),('CORTEX_A9',UC_MODE_THUMB)]:
 for hook in [False,True]:
  for offset in [0,1,2,3]:
   u=Uc(UC_ARCH_ARM,mode);u.ctl_set_cpu_model(getattr(a,'UC_CPU_ARM_'+name));u.mem_map(0x410000,0x25000)
   for lo,hi in [(0x41568c,0x41573a),(0x422416,0x422432),(0x422464,0x422468)]:u.mem_write(lo,blob[lo-0x410000:hi-0x410000])
   u.mem_map(0x20000000,0x40000);u.mem_map(0x8000000,4096);u.mem_write(0x20001000,bytes(range(64)));u.reg_write(a.UC_ARM_REG_SP,0x2002f000);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_R0,0x20001000+offset);trace=[]
   def stop_hook(cpu,pc,n,z):
    trace.append({'pc':hex(pc),'r0':hex(cpu.reg_read(a.UC_ARM_REG_R0)),'cpsr':hex(cpu.reg_read(a.UC_ARM_REG_CPSR))})
    if pc==0x8000000:cpu.emu_stop()
   u.hook_add(UC_HOOK_CODE,stop_hook)
   u.emu_start(0x422417,0x8000002,count=10000);rows.append({'model':name,'hook':hook,'source_offset':offset,'return':hex(u.reg_read(a.UC_ARM_REG_R0)),'copied':bytes(u.mem_read(0x2000007c,20)).hex(),'expected_source_bytes':bytes(range(offset,offset+20)).hex(),'trace':trace})
r={'scope':'Only authentic26-byte wrapper, copy helper span and one literal loaded; zero code/provider/expected-answer modifications','unicorn_version':__import__('unicorn').__version__,'comparisons':rows};Path(__file__).with_name('stop-hook-result.json').write_text(json.dumps(r,indent=2)+'\n');print([(x['model'],x['hook'],x['source_offset'],x['return']) for x in rows])
