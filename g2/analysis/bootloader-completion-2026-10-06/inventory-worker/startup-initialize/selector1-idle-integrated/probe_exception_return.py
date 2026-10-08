"""Bounded backend capability probe, not firmware behavioral equivalence."""
from pathlib import Path
import json,struct,hashlib
from unicorn import *
from unicorn import arm_const as a
from capstone import *
ROOT=Path(__file__).resolve().parents[6];b=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
m=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);bx=next(x for x in m.disasm(b[0x41b31c-0x410000:0x41b374-0x410000],0x41b31c) if x.mnemonic=='bx' and x.op_str=='r3')
rows=[]
for ipsr in [0,14]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,n in [(0x410000,0x30000),(0x20000000,0x40000),(0xe000e000,0x1000)]:u.mem_map(lo,n)
 u.mem_write(0x410000,b);psp=0x20031000;target=0x4189ad
 u.mem_write(psp,struct.pack('<8I',0x1111,0x2222,0x3333,0x4444,0xcccc,0xfffffffd,target,0x01000000))
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_PSP,psp);u.reg_write(a.UC_ARM_REG_R3,0xfffffffd);u.reg_write(a.UC_ARM_REG_IPSR,ipsr)
 interrupts=[];error=None
 def intr(cpu,no,_):interrupts.append(no);cpu.emu_stop()
 u.hook_add(UC_HOOK_INTR,intr)
 try:u.emu_start(bx.address|1,0,count=1)
 except UcError as e:error=str(e)
 rows.append({'seeded_ipsr':ipsr,'instruction_address':hex(bx.address),'instruction':bx.mnemonic+' '+bx.op_str,'interrupts':interrupts,'error':error,'result_pc':hex(u.reg_read(a.UC_ARM_REG_PC)),'result_psp':hex(u.reg_read(a.UC_ARM_REG_PSP)),'result_ipsr':u.reg_read(a.UC_ARM_REG_IPSR),'result_r0':hex(u.reg_read(a.UC_ARM_REG_R0)),'expected_unstacked_target':hex(target&~1)})
Path(__file__).with_name('exception-return-capability.json').write_text(json.dumps({'status':'CAPABILITY_OBSERVATION_ONLY','backend':'Unicorn2.1.4 Cortex-M33 compatibility','comparisons':rows,'limits':['IPSR and a basic frame are manually seeded. Architectural NVIC active-exception state/exception entry is not established; rejection cannot prove firmware fault or complete backend support/absence.','This bounded probe must not substitute a Python unstack model for actual exception-return behavior.']},indent=2)+'\n');print(rows)
