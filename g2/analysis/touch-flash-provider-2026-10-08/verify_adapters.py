from pathlib import Path
import sys,json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';im=fw[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
def guest(native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 for a,n in [(0x3000,0x9000),(0x100000,0x20000),(0x20000000,0x10000),(0x40100000,0x1000),(0x40030000,0x1000)]:u.mem_map(a,n)
 if native:
  for a,b in segments:u.mem_write(a,b)
 else:u.mem_write(0x3300,im)
 return u
def run(native,kind,address,size,mask,statuses,enabled=1):
 data=0x20003000
 u=guest(native);payload=bytes((i*7)&255 for i in range(512));u.mem_write(0x20003000,payload);u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,address);u.reg_write(UC_ARM_REG_R2,size);u.reg_write(UC_ARM_REG_R3,data);
 if kind=='gate':
  u.reg_write(UC_ARM_REG_R0,address);u.reg_write(UC_ARM_REG_R1,data);u.reg_write(UC_ARM_REG_R2,0x200008c8);ctx=bytearray(32);struct.pack_into('<H',ctx,2,128);struct.pack_into('<I',ctx,4,size);struct.pack_into('<I',ctx,28,0x20000ed4);ctx[15]=enabled;u.mem_write(0x200008c8,bytes(ctx));provider=bytearray(48)
  for slot,name,stock in [(6,'touch_storage_program',0x4811),(7,'touch_storage_zero',0x47b1),(11,'touch_storage_no_erase',0x47ab)]:struct.pack_into('<I',provider,slot*4,symbols[name] if native else stock)
  u.mem_write(0x20000ed4,bytes(provider))
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_PRIMASK,mask);events=[];positions={4:0,0x16:1,0x15:2,5:3,0x18:3,0x17:4};argstore=[];loads=0
 def write(u,access,addr,size,value,user):
  nonlocal loads
  if addr==0x40100008:argstore.append(value)
  if addr==0x40100004:
   cmd=value&255;arg=int.from_bytes(u.mem_read(0x40100008,4),'little');p=[]
   if cmd in [4,5,0x18]:
    p=list(struct.unpack('<II',u.mem_read(arg,8)));
    if cmd==4:
     want=bytes(128) if kind=='zero' else payload[loads*128:(loads+1)*128];assert bytes(u.mem_read(arg+8,128))==want;loads+=1
   elif cmd in [0x16,0x17]:p=list(struct.unpack('<II',u.mem_read(arg,8)))
   else:p=[arg]
   events.append(['srom-request',cmd,p,u.reg_read(UC_ARM_REG_PRIMASK)]);u.mem_write(0x40100008,struct.pack('<I',statuses[positions[cmd]]))
  if addr==0x40030030:events.append(['clock-write',addr,size,value])
 def code(u,pc,size,user):
  if pc==((symbols['touch_flash_write_row']&~1) if native else 0x8d50):
   a=u.reg_read(UC_ARM_REG_R0);p=u.reg_read(UC_ARM_REG_R1);events.append(['flash-entry',a,bytes(u.mem_read(p,128)).hex()])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);name={'zero':'touch_storage_zero','program':'touch_storage_program','gate':'touch_eeprom_program_gate'}[kind];old={'zero':0x47b0,'program':0x4810,'gate':0x7ea4}[kind];u.emu_start((symbols[name] if native else old)|1,0x20000000,count=15000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return {'return':u.reg_read(UC_ARM_REG_R0),'events':events,'sysarg_stores':len(argstore),'sp':u.reg_read(UC_ARM_REG_SP),'primask':u.reg_read(UC_ARM_REG_PRIMASK),'input':u.mem_read(0x20003000,512).hex()}
success=0xa0000000;patterns=[[success]*5,[0xf0000001]*5,[success,success,0xf0000005,success,success]];cases=[]
for vals in itertools.product(['zero','program'],[0xe400,0x10000,1,0xfffffff0],[0,1,127,128,256,512,129],[0,1],patterns):
 a=run(False,*vals);b=run(True,*vals);assert a==b,(vals,a,b);assert a['return']==(0x06160002 if vals[2]&127 else 0);cases.append({'inputs':vals,'result':a})
gates=[]
for vals in itertools.product([0xe400,0x10000,1],[128,256],[0,1],patterns,[0,1]):
 a=run(False,'gate',*vals);b=run(True,'gate',*vals);assert a==b,(vals,a,b);assert a['return']==0;assert bool([e for e in a['events'] if e[0]=='flash-entry'])==bool(vals[-1]);gates.append({'inputs':vals,'result':a})
r={'status':'PASS_REAL_PROVIDER_FLASH_CHAIN_SYNTHETIC_SROM','adapter_cases':len(cases),'program_gate_cases':len(gates),'elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'comparisons':cases,'gate_comparisons':gates,'limits':['Actual stock adapters/program gate/flash/critical/decoder/memcpy/division; native reconstructed helpers/flash and public critical assembly execute, no helper entry cuts.','Only SROM CPUSS requests receive synthetic status. No physical flash, voltage, clock or IRQ behavior.','Recovered slot11 returns0, so erase branch is unreachable with normal provider; normal program errors are discarded by adapter.','Invalid raw addresses/size/overflow are callee tests; zero buffer512 bytes and program stride128 match original instructions.']};(D/'adapter-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'adapter and',len(gates),'real provider/gate cases; flash errors discarded')
