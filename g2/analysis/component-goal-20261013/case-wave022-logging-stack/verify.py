#!/usr/bin/env python3
"""Real variadic logger/formatter/callback/UART graph, synthetic ready/BUSY inputs."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib,itertools
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;E=H/'final/case.elf';F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert E.exists()
assert sha(F)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
with E.open('rb') as f:
 e=ELFFile(f);sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
SP=0x20008000;STOP=0x2000f000;FMT=0x20005000;STRING=0x20005200;OUT=0x20005300
formats=[('literal\r\n',[]),('%u',[0]),('%d',[0x80000000]),('%08x',[0xdeadbeef]),('%+8d',[0xfffffff9]),('%#x %#o',[0x123,9]),('%-8.3s',[STRING]),('%c %%',[65]),('%u %u %u %u %u %u',[1,2,3,4,5,6]),('%*.*x',[10,4,0x123]),('abc%nZ',[OUT]),('abc%hhnZ',[OUT]),('abc%hnZ',[OUT]),('%hhu %hd',[0xffffffab,0xffff8000]),('%p',[0x20001234]),('%llu',[0,0xffffffff,1]),('%llx',[0,0xabcdef01,0x12345678])]
rows=[]
def run(native,fmt,args,busy):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,F.read_bytes()[32:])
 else:
  for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000);u.mem_write(FMT,fmt.encode()+b'\0');u.mem_write(STRING,b'abcdef\0');u.mem_write(OUT,b'\xa5'*8)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 w(0x20000e24,0x40013800);w(0x20000e24+0x88,0 if busy else 0x20);w(0x4001381c,0xc0)
 for i,v in enumerate(args[3:]):w(SP+i*4,v)
 regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
 for reg,v in zip(regs,[FMT]+args[:3]+[0]*3):u.reg_write(reg,v)
 saved=[0x45670000+i for i in range(8)]
 for reg,v in zip(range(UC_ARM_REG_R4,UC_ARM_REG_R11+1),saved):u.reg_write(reg,v)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);writes=[];attempts=[];low=SP;callbacks=0
 def code(uc,address,size,data):
  nonlocal low,callbacks
  low=min(low,uc.reg_read(UC_ARM_REG_SP))
  if address==(0x0800a380 if native else sy['case_log_output_char']&~1):callbacks+=1
  if address==(0x080066ac if native else sy['case_write_controller_blocking']&~1):
   assert uc.reg_read(UC_ARM_REG_R0)==0x20000e24 and uc.reg_read(UC_ARM_REG_R2)==1 and uc.reg_read(UC_ARM_REG_R3)==65535
   attempts.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),1))[0])
 def write(uc,access,address,size,value,data):
  if address==0x40013828:writes.append(value)
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((0x08009170 if native else sy['g2_log_printf'])|1,STOP,count=300000)
 assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
 assert [u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)]==saved
 return {'return':u.reg_read(UC_ARM_REG_R0),'ram':bytes(u.mem_read(0x20000000,0x3000)).hex(),'n_output':bytes(u.mem_read(OUT,8)).hex(),'attempts':attempts,'writes':writes,'callbacks':callbacks,'stack_bytes':SP-low}
for (fmt,args),busy in itertools.product(formats,[False,True]):
 a=run(True,fmt,args,busy);b=run(False,fmt,args,busy)
 fields=[k for k in a if k!='stack_bytes' and a[k]!=b[k]]
 if fields:
  (H/'failure.json').write_text(json.dumps({'format':fmt,'args':args,'busy':busy,'different_fields':fields,'native':a,'source':b},indent=2)+'\n');raise AssertionError((fmt,busy,fields))
 assert a['callbacks']==len(a['attempts'])==a['return']
 assert a['writes']==([] if busy else a['attempts'])
 rows.append({'format':fmt,'args':args,'busy':busy,'return':a['return'],'output_hex':bytes(a['attempts']).hex(),'native_stack_bytes':a['stack_bytes'],'source_stack_bytes':b['stack_bytes']})
r={'status':'PASS_FULL_LOGGER_CALLBACK_UART_GRAPH','cases':len(rows),'ELF_sha256':sha(E),'firmware_sha256':sha(F),'comparisons':rows,'native_max_stack_bytes':max(x['native_stack_bytes'] for x in rows),'source_max_stack_bytes':max(x['source_stack_bytes'] for x in rows),'limits':['Synthetic static TXE/TC ready or BUSY input; not physical UART proof','Stack maximum only these bounded synchronous cases, excludes interrupts/reentrancy and global worst case','Actual callbacks and providers execute; no child cuts/stubs/return injection']};(H/'logger-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'],r['native_max_stack_bytes'],r['source_max_stack_bytes'])
