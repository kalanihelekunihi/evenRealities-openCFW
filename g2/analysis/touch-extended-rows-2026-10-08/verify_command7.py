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
cs=Cs(CS_ARCH_ARM,CS_MODE_THUMB);flash_returns={i.address+i.size for a,z in [(0x4810,0x485a),(0x47b0,0x4806)] for i in cs.disasm(im[a-0x3300:z-0x3300],a) if i.mnemonic=='bl' and i.op_str=='#0x8d50'}
cases=[]
for initialized,simple,bad,parameter,mask in itertools.product([0,1],[0,1],[0,1,2],[0,1,0x1234,0xffff],[0,1]):
 u=guest(False);u.mem_map(0xc000,0x4000);u.mem_map(0x40040000,0x1000);u.mem_write(0xe400,b'\x55'*2048);u.mem_write(0x200009a0,bytes([7,parameter&255,parameter>>8])+bytes(13));u.mem_write(0x200009b0,b'\xcc'*16);u.mem_write(0x200009d0,b'UNVE'+struct.pack('<HH',0x4321,0x4567));u.mem_write(0x200008c4,bytes([initialized]));u.mem_write(0x200004e8,struct.pack('<H',0x4567));u.mem_write(0x200008ec+64,struct.pack('<I',3));ctx=bytearray(32);struct.pack_into('<HH',ctx,0,4,128);struct.pack_into('<I',ctx,4,128);struct.pack_into('<I',ctx,8,256);ctx[12]=2;ctx[13]=simple;ctx[15]=1;struct.pack_into('<I',ctx,16,0xe400);struct.pack_into('<HH',ctx,20,64,48);struct.pack_into('<I',ctx,24,0xe400);struct.pack_into('<I',ctx,28,0x20000ed4);u.mem_write(0x200008c8,bytes(ctx));provider=bytearray(48)
 for slot,pc in [(5,0x4861),(6,0x4811),(7,0x47b1),(11,0x47ab)]:struct.pack_into('<I',provider,slot*4,pc)
 u.mem_write(0x20000ed4,bytes(provider));events=[];low_status=[];adapter_status=[]
 def code(u,pc,n,user):
  if pc in flash_returns:low_status.append(u.reg_read(UC_ARM_REG_R0))
  if pc==0x3ac0:adapter_status.append(u.reg_read(UC_ARM_REG_R0))
  if pc in [0x8058,0x814c,0x8680]:
   if pc==0x8058:u.mem_write(u.reg_read(UC_ARM_REG_R0),struct.pack('<II',0,0))
   else:u.mem_write(u.reg_read(UC_ARM_REG_R0)+64,b'\x5a'*64)
   events.append(['history-cut',hex(pc)]);u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def write(u,access,addr,n,value,user):
  if addr==0x40100004:
   cmd=value&255;events.append(['srom-request',cmd]);status=0xa0000000 if not bad or (bad==2 and cmd!=0x17) else 0xf0000005;u.mem_write(0x40100008,struct.pack('<I',status))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 for pc,arg in [(0x3700,0x20),(0x3a80,0)]:
  u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(pc|1,0x20000000,count=50000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
  if pc==0x3700:ack=bytes(u.mem_read(0x200009b0,3)).hex();assert not events;events.append(['ack-prepared',ack])
 assert ack==('070017' if parameter else '07ff17');assert bool(low_status)==bool(parameter and initialized)
 if parameter and initialized:assert adapter_status==[0];assert all(v==(0 if not bad else 0x00520005) for v in low_status)
 elif parameter:assert adapter_status==[1]
 else:assert not adapter_status
 assert u.reg_read(UC_ARM_REG_PRIMASK)==mask
 cases.append({'inputs':[initialized,simple,bad,parameter,mask],'ack':ack,'low_flash_status':low_status,'application_storage_status':adapter_status,'events':events,'gesture_parameter':u.mem_read(0x20000940,2).hex()})
r={'status':'PASS_STOCK_COMMAND7_ACK_VS_DEFERRED_OUTCOME','cases':len(cases),'comparisons':cases,'limits':['Actual stock callback/deferred/write adapter/simple or extended/provider/flash instructions execute; simple path has no history cuts.','Extended history helpers are explicit synthetic cuts; SROM completion synthetic for both modes.','Sequential callback then deferred invocation is a constructed ordering, not NVIC/task scheduling or host ACK delivery.','No actual flash content is programmed; guest flash supports read preservation only.']};(D/'command7-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'actual stock command7/deferred outcomes; ACK never conveys later flash failure')
