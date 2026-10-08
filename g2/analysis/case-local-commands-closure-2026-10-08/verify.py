from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=Path('/tmp/opencfw-case-local/local.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
rows=[];P=0x20004000
for cmd,n,p4,p5,state in itertools.product([0x50,0x5c,0x5d,0x68],[0,4,5,6,20],[0,1,2],[0,1],[0,1]):
 vals=[]
 for entry in [0x08000e1c,sym['case_local_selected']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x100000,0x10000);u.mem_map(0x50000000,0x1000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(P,bytes([cmd,0,2,0,p4,p5])+bytes(250));u.mem_write(0x200000bf,b'\x01');u.mem_write(0x20000880,bytes([state]));boundary=[];trace=[];gpio=[]
  def code(u,a,size,d):
   assert a!=0x08009170,'unexpected logger'
   if a==0x0800680c:
    count=u.reg_read(UC_ARM_REG_R1);boundary.append(dict(child=hex(a),payload=bytes(u.mem_read(u.reg_read(UC_ARM_REG_R0),count)).hex(),length=count));u.emu_stop()
   if a in [0x080068d0,0x08006b80,0x08006b98]:trace.append(dict(child=hex(a),arg0=u.reg_read(UC_ARM_REG_R0)))
  def write(u,access,a,n,v,d):
   if 0x50000000<=a<0x50001000:gpio.append([hex(a),n,v])
  u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,n);u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=10000);assert boundary or u.reg_read(UC_ARM_REG_PC)==0x20000000
  expected_gpio=[[hex(0x50000018 if not p5 else 0x50000028),4,0x40 if p4 else 0x80]] if cmd==0x5d and n>=6 else []
  assert gpio==expected_gpio
  vals.append((boundary,bytes(u.mem_read(0x20000000,0x900)),trace,gpio))
 assert vals[0]==vals[1],(cmd,n,p4,p5,state,vals[0][0],vals[1][0])
 rows.append(dict(command=hex(cmd),logical_length=n,byte4=p4,byte5=p5,status_byte=state,boundary=vals[0][0],final_control=vals[0][1][0xbf],child_trace=vals[0][2],gpio_writes=vals[0][3]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(blob).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Destination2, selected50/5c/5d/68; allocated256-byte input regardless logical length. No entry buffer safety guarantee.','Send stops before first instruction; actual ack/control/GPIO helpers execute as common peers, with expected MMIO write checks. No wire transmission or physical GPIO effect.','Logging flag1 at entry prevents logging; remaining commands and logging branches excluded.']),indent=2)+'\n');print('PASS',len(rows))
