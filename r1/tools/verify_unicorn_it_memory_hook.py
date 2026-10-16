#!/usr/bin/env python3
"""Controlled reproduction of conditional-store IT corruption with a write hook."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
import unicorn
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-scanf-conversion';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 fixture=ROOT/'r1/tools/fixtures/scanf_it_memory_hook_replay.s';layout=ROOT/'r1/source-config/runtime/native_scanf_conversion_verification.ld';results=[]
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);obj=d/'replay.o';elf=d/'replay.elf';binary=d/'replay.bin';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-c',str(fixture),'-o',str(obj)],check=True);subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  for with_hook in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,4);u.reg_write(UC_ARM_REG_R2,0x20001300);u.reg_write(UC_ARM_REG_XPSR,0x01000000);trace=[]
   u.hook_add(UC_HOOK_CODE,lambda u,a,n,_:trace.append([a,u.reg_read(UC_ARM_REG_SP),u.reg_read(UC_ARM_REG_XPSR)]))
   if with_hook:u.hook_add(UC_HOOK_MEM_WRITE,lambda *args:None)
   error=None
   try:u.emu_start(0x1000001,0x20000100,count=100)
   except UcError as exc:error=str(exc)
   results.append(dict(memory_write_hook=with_hook,pc=u.reg_read(UC_ARM_REG_PC),sp=u.reg_read(UC_ARM_REG_SP),error=error,trace=trace,stored_bytes=bytes(u.mem_read(0x20001300,4)).hex()))
 assert results[0]['pc']==0x20000100 and results[0]['sp']==0x2003f000 and results[0]['error'] is None
 assert results[1]['pc']!=0x20000100 and results[1]['error'] and results[0]['stored_bytes']==results[1]['stored_bytes']=='04000000'
 receipt=dict(unicorn_version=unicorn.__version__,driver_sha256=sha(Path(__file__)),fixture=str(fixture.relative_to(ROOT)),fixture_sha256=sha(fixture),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),verification_only=True,results=results,conclusion='This controlled replay returns correctly without the memory-write hook and faults with it; source parser behavior must not be inferred from that hooked fault.')
 (OUT/'it-memory-hook-reproduction.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Conditional-store IT memory-hook fault reproduced; unhooked replay returns correctly')
if __name__=='__main__':main()
