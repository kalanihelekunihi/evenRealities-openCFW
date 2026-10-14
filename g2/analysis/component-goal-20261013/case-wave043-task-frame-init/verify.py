#!/usr/bin/env python3
"""Actual CASE static TCB/stack initialization and port frame providers."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib,itertools
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;P=H.parent/'case-wave039-list-cursor-contract';E=P/'final/case.elf';F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with E.open('rb') as f:
 e=ELFFile(f);sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
SP=0x20002c88;STOP=0x2000f000;TCB=0x2000182c;BASE=0x20001888;rows=[]
def run(native,words,priority,name_kind,seed):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,F.read_bytes()[32:])
 else:
  for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.mem_write(TCB,bytes([seed])*0x5c);u.mem_write(0x20002888,bytes([seed])*0x400)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 w(TCB+0x30,BASE);entry=(0x0800b360 if native else sy['case_boot_service_task_entry'])|1
 if name_kind=='stock':name=0x0800cd74 if native else sy['case_boot_service_task_name']
 elif name_kind=='null':name=0
 else:name=0x20003000;u.mem_write(name,b'abcdefghijklmnopX\0')
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[entry,name,words,0x20000020]):u.reg_write(r,v)
 for i,v in enumerate([priority,0,TCB,0]):w(SP+i*4,v)
 saved=[0x45670000+i for i in range(8)]
 for r,v in zip(range(UC_ARM_REG_R4,UC_ARM_REG_R11+1),saved):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);low=SP
 def observe(uc,address,size,data):
  nonlocal low
  low=min(low,uc.reg_read(UC_ARM_REG_SP));assert low>=0x20002888
 u.hook_add(UC_HOOK_CODE,observe);u.emu_start((0x0800ae96 if native else sy['case_boot_task_initialize'])|1,STOP,count=200000)
 assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
 assert [u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)]==saved
 top=(BASE+(words-1)*4)&~7;frame=struct.unpack('<I',bytes(u.mem_read(TCB,4)))[0];assert frame==top-64
 assert struct.unpack('<I',bytes(u.mem_read(top-4,4)))[0]==0x01000000
 assert struct.unpack('<I',bytes(u.mem_read(top-8,4)))[0]==entry
 return_fn=struct.unpack('<I',bytes(u.mem_read(top-12,4)))[0];assert return_fn==(0x0800b31d if native else sy['case_boot_task_return'])
 assert struct.unpack('<I',bytes(u.mem_read(top-32,4)))[0]==0x20000020
 assert bytes(u.mem_read(frame,32))==b'\xa5'*32
 assert struct.unpack('<I',bytes(u.mem_read(TCB+44,4)))[0]==min(priority,55)
 ram=bytearray(u.mem_read(0x20000000,0x2888));ram[top-0x20000000-12:top-0x20000000-4]=bytes(8)
 return {'frame':hex(frame),'ram':bytes(ram).hex(),'stack_bytes':SP-low}
for words,priority,name_kind,seed in itertools.product([64,128,256],[0,1,55,56,255],['stock','null','long'],[0,0xa5,0xff]):
 a=run(True,words,priority,name_kind,seed);b=run(False,words,priority,name_kind,seed);fields=[k for k in a if k!='stack_bytes' and a[k]!=b[k]]
 if fields:
  (H/'failure.json').write_text(json.dumps({'words':words,'priority':priority,'name':name_kind,'seed':seed,'different_fields':fields,'native':a,'source':b},indent=2)+'\n');raise AssertionError((words,priority,name_kind,seed,fields))
 rows.append({'words':words,'priority':priority,'name':name_kind,'seed':seed,'frame':a['frame'],'native_stack_bytes':a['stack_bytes'],'source_stack_bytes':b['stack_bytes']})
r={'status':'PASS_STATIC_TCB_STACK_PORT_FRAME_GRAPH','cases':len(rows),'ELF_sha256':sha(E),'firmware_sha256':sha(F),'comparisons':rows,'limits':['Real taskinit/stackfill/linkreset/portframe providers without cuts or injectedreturns','Known entry/returnfunction pointer namespaces normalized after exact identity checks; allotherRAM belowfooter compare','StaticTCB/stack storage layout and typed argument stream; no actual exceptionreturn/task execution/IRQdelivery proof','Bounded1024byte nativeMSPwindow, not global IRQ/reentrancy budget']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
