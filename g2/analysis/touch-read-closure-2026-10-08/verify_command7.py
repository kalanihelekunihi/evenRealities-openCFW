from pathlib import Path
import sys,json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
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
def checksum(row):
 crc=255
 for v in row[1:len(row)-3]:
  crc^=v
  for j in range(8):crc=((crc<<1)^(0x31 if crc&128 else 0))&255
 return crc
def rows(pattern):
 raw=bytearray(2048)
 for i in range(16):
  r=bytearray(128);seq=[0xfffffffe,0xffffffff,0,1,2,3,4,5][i%8] if pattern=='wrap' else i%8+1
  struct.pack_into('<III',r,4,seq,(i%4)*64+((i%2)*8),[1,16,48][i%3]);r[16:64]=bytes((i*17+j)&255 for j in range(48));r[64:]=bytes((i*29+j)&255 for j in range(64));struct.pack_into('<I',r,0,checksum(r))
  if pattern=='blank':r=bytearray(128)
  elif pattern=='erased':r=bytearray(b'\xff'*128)
  elif pattern=='bad-main' and i<8:r[0]^=1
  elif pattern=='bad-all':r[0]^=1
  elif pattern=='torn-last' and i==7:r[16:48]=b'\x3c'*32
  raw[i*128:(i+1)*128]=r
 return bytes(raw)
cs=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
with elfpath.open('rb') as f:
 e=ELFFile(f);text=e.get_section_by_name('.text');native_returns=set()
 for sym in e.get_section_by_name('.symtab').iter_symbols():
  if sym.name=='touch_deferred':
   a=sym['st_value']&~1
   for ins in cs.disasm(text.data()[a-text['sh_addr']:a-text['sh_addr']+sym['st_size']],a):
    if ins.mnemonic=='bl' and ins.op_str=='#'+hex(symbols['config_persist']&~1):native_returns.add(ins.address+ins.size)
def run(native,pattern,initialized,simple,mode,parameter,mask):
 u=guest(native);u.mem_map(0xc000,0x4000);u.mem_map(0x40040000,0x1000);u.mem_write(0xe400,rows(pattern));u.mem_write(0x200009a0,bytes([7,parameter&255,parameter>>8])+bytes(13));u.mem_write(0x200009b0,b'\xcc'*16);u.mem_write(0x200009d0,b'UNVE'+struct.pack('<HH',0x4321,0x4567));u.mem_write(0x200008c4,bytes([initialized]));u.mem_write(0x200004e8,struct.pack('<H',0x4567));u.mem_write(0x200008ec+64,struct.pack('<I',3));ctx=bytearray(32);struct.pack_into('<HH',ctx,0,4,128);struct.pack_into('<I',ctx,4,128);struct.pack_into('<I',ctx,8,256);ctx[12]=2;ctx[13]=simple;ctx[14]=1;ctx[15]=1;struct.pack_into('<I',ctx,16,0xe400);struct.pack_into('<HH',ctx,20,64,48);struct.pack_into('<I',ctx,24,0xe780);struct.pack_into('<I',ctx,28,0x20000ed4);u.mem_write(0x200008c8,bytes(ctx));provider=bytearray(48)
 for slot,name,stock in [(5,'touch_storage_copy',0x4861),(6,'touch_storage_program',0x4811),(7,'touch_storage_zero',0x47b1),(11,'touch_storage_no_erase',0x47ab)]:struct.pack_into('<I',provider,slot*4,symbols[name] if native else stock)
 u.mem_write(0x20000ed4,bytes(provider));events=[];adapter_status=[];latch=None
 def code(u,pc,n,user):
  if pc in (native_returns if native else {0x3ac0}):adapter_status.append(u.reg_read(UC_ARM_REG_R0))
 def write(u,access,addr,n,value,user):
  nonlocal latch
  if addr==0x40100004:
   cmd=value&255;arg=int.from_bytes(u.mem_read(0x40100008,4),'little');status=0xa0000000
   if (mode=='load-error' and cmd==4) or (mode in ['program-error','torn16'] and cmd==5) or (mode=='restore-error' and cmd==0x17):status=0xf0000005
   if cmd in [4,5]:
    p=list(struct.unpack('<II',u.mem_read(arg,8)));data=bytes(u.mem_read(arg+8,128));events.append(['srom',cmd,p,data.hex(),status])
    if cmd==4 and status==0xa0000000:latch=data
    if cmd==5:
     dest=(p[0]>>16)*128;assert 0xe400<=dest<0xec00 and latch==data;prefix=128 if status==0xa0000000 else 16 if mode=='torn16' else 0
     if prefix:u.mem_write(dest,data[:prefix])
   else:p=list(struct.unpack('<II',u.mem_read(arg,8))) if cmd in [0x16,0x17] else [arg];events.append(['srom',cmd,p,None,status])
   u.mem_write(0x40100008,struct.pack('<I',status))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 for name,old,arg in [('app_event',0x3700,0x20),('touch_deferred',0x3a80,0)]:
  u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start((symbols[name] if native else old)|1,0x20000000,count=1500000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
  if name=='app_event':ack=bytes(u.mem_read(0x200009b0,3)).hex();assert not events;events.append(['ack-prepared',ack])
 assert ack==('070017' if parameter else '07ff17');assert bool(adapter_status)==bool(parameter)
 return {'ack':ack,'application_storage_status':adapter_status,'events':events,'gesture':u.mem_read(0x20000940,80).hex(),'config':u.mem_read(0x200009cd,11).hex(),'storage':u.mem_read(0xe400,2048).hex(),'eeprom_context':u.mem_read(0x200008c8,32).hex(),'i2c_context':u.mem_read(0x200008ec,84).hex(),'primask':u.reg_read(UC_ARM_REG_PRIMASK)}
cases=[]
for vals in itertools.product(['blank','valid','bad-all','torn-last','wrap'],[0,1],[0,1],['success','load-error','program-error','torn16','restore-error'],[0,1,0x1234,0xffff],[0,1]):
 a=run(False,*vals);b=run(True,*vals);assert a==b,(vals,a,b);assert a['primask']==vals[-1];cases.append({'inputs':vals,'result':a})
r={'status':'PASS_FULL_COMMAND7_NATIVE_STOCK_NO_FUNCTION_CUTS','cases':len(cases),'elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'comparisons':cases,'limits':['Actual stock/native callback/deferred/write dispatch/simple or extended/history/provider/flash/critical instructions; no function cuts.','Only SROM status/full/torn programming is synthetic guest RAM behavior; partial-write model is not hardware evidence.','Sequential callback then deferred invocation, no IRQ/task scheduling/host ACK delivery or physical durability claim.','Coherent128-byte provider geometry; callback source remains bounded sensor/reset contracts outside command7 suite.']};(D/'command7-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'native/stock full command7 outcomes; no function cuts, SROM synthetic')
