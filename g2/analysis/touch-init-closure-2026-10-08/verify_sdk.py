from pathlib import Path
import sys,json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';im=fw[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_sections():
  if s.name.startswith('.match_') or s.name in ['.wrapper','.factory']:segments.append((s['sh_addr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
slots={1:('touch_provider_read_size',0x4781),2:('touch_provider_program_size',0x4785),3:('touch_provider_erase_size',0x4789),4:('touch_provider_erase_value',0x478d),5:('touch_storage_copy',0x4861),6:('touch_storage_program',0x4811),7:('touch_storage_zero',0x47b1),10:('touch_provider_in_range',0x4791),11:('touch_storage_no_erase',0x47ab)}
with elfpath.open('rb') as f:
 e=ELFFile(f);factory=symbols['touch_factory_eeprom_configuration']
 matches=[data[factory-a:factory-a+12] for a,data in segments if a<=factory and factory+12<=a+len(data)]
 assert matches==[im[0xb58c-0x3300:0xb58c-0x3300+12]]
visited=set()
def call(u,pc,args,limit=1500000):
 for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(pc|1,0x20000000,count=limit);assert u.reg_read(UC_ARM_REG_PC)==0x20000000,hex(u.reg_read(UC_ARM_REG_PC));return u.reg_read(UC_ARM_REG_R0)
def checksum(row):
 crc=255
 for v in row[1:len(row)-3]:
  crc^=v
  for j in range(8):crc=((crc<<1)^(0x31 if crc&128 else 0))&255
 return crc
def storage(pattern,main_rows):
 raw=bytearray(7168)
 for i in range(56):
  r=bytearray(128);seq=[0xfffffffe,0xffffffff,0,1,2,3,4,5][i%8] if pattern=='wrap' else i%8+1
  if pattern=='mirror-newer' and i>=main_rows:seq+=8
  struct.pack_into('<III',r,4,seq,(i%4)*64,16);r[16:64]=bytes((i*17+j)&255 for j in range(48));r[64:]=bytes((i*29+j)&255 for j in range(64));struct.pack_into('<I',r,0,checksum(r))
  if pattern=='zero':r=bytearray(128)
  elif pattern=='erased':r=bytearray(b'\xff'*128)
  elif pattern=='bad-main' and i<main_rows:r[0]^=1
  elif pattern=='bad-all':r[0]^=1
  elif pattern=='torn-last' and i==main_rows-1:r[16:48]=b'\x3c'*32
  raw[i*128:(i+1)*128]=r
 return bytes(raw)
def guest(native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x3000,0x9000);u.mem_map(0xc000,0x4000);u.mem_map(0x100000,0x20000);u.mem_map(0x20000000,0x10000);u.mem_write(0x3300,im);u.mem_write(0x20000000,b'\xcc'*0x10000)
 if native:
  for a,b in segments:u.mem_write(a,b)
 # Actual original reset data-copy and BSS-zero slice; prerequisite setup only.
 u.emu_start(0x4693,0x46d6,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x46d6
 assert bytes(u.mem_read(0x200004c0,12)).hex()=='000100000002010100000000'
 assert bytes(u.mem_read(0x200008a8,0x1ac*4))==bytes(0x1ac*4)
 return u
def snapshot(u,native,result,events):
 table=list(struct.unpack('<12I',u.mem_read(0x20000ed4,48)))
 if native:
  for slot,(name,pc) in slots.items():
   if table[slot]==symbols[name]:table[slot]=pc
 return dict(return_value=result,context=u.mem_read(0x200008c0,40).hex(),config=u.mem_read(0x200004c0,12).hex(),provider=table,events=events,storage_sha256=hashlib.sha256(u.mem_read(0xe400,7168)).hexdigest(),sp=u.reg_read(UC_ARM_REG_SP),primask=u.reg_read(UC_ARM_REG_PRIMASK))
def run(native,kind,pattern,config,initialized=0,nulls=0):
 u=guest(native);cfg=struct.pack('<I4BI',*config);u.mem_write(0x20006000,cfg);u.mem_write(0x200004c0,cfg);u.mem_write(0x200008c4,bytes([initialized]));cap,sm,wear,red,blocking,base=config;main_rows=((cap+63)//64)*wear if not sm else (cap+127)//128;before=storage(pattern,main_rows);u.mem_write(0xe400,before);events=[]
 tracked={((symbols[name] if native else pc)&~1):(slot,2 if slot in [1,2,3,4] else 3) for slot,(name,pc) in slots.items() if slot in [2,3,10]}
 def code(u,pc,n,user):
  if not native and (0x898c<=pc<0x8a34 or 0x34d8<=pc<0x350a):visited.update(range(pc,pc+n))
  if pc in tracked:
   slot,argc=tracked[pc];events.append([slot,*[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2][:argc]]])
 u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_PRIMASK,initialized&1)
 if kind=='bd':
  call(u,symbols['touch_provider_init'] if native else 0x486c,[0x20000ed4]);u.mem_write(0x200008c8,b'\xdd'*32)
  args=[0 if nulls&1 else 0x20006000,0 if nulls&2 else 0x200008c8,0 if nulls&4 else 0x20000ed4];result=call(u,symbols['touch_eeprom_init_bd'] if native else 0x898c,args)
 elif kind=='adapter':result=call(u,symbols['touch_eeprom_init'] if native else 0x8a38,[0x20006000,0x200008c8])
 else:result=call(u,symbols['touch_application_eeprom_init'] if native else 0x34d8,[])
 assert bytes(u.mem_read(0xe400,7168))==before
 return snapshot(u,native,result,events)
results=[]
for pattern,cap,sm,wear,red,blocking in itertools.product(['zero','erased','valid','bad-main','bad-all','torn-last','wrap'],[0,1,64,128,256,1024],[0,1],[1,2,7,10],[0,1],[0,1]):
 cfg=(cap,sm,wear,red,blocking,0xe400);a=run(False,'bd',pattern,cfg);b=run(True,'bd',pattern,cfg);assert a==b,(pattern,cfg,a,b);results.append(dict(kind='bd',pattern=pattern,configuration=cfg,result=a))
for pattern,initialized in itertools.product(['zero','erased','valid','bad-main','bad-all','mirror-newer','torn-last','wrap'],[0,1,255]):
 cfg=(256,0,2,1,1,0);a=run(False,'app',pattern,cfg,initialized);b=run(True,'app',pattern,cfg,initialized);assert a==b,(pattern,initialized,a,b);results.append(dict(kind='app',pattern=pattern,initialized=initialized,configuration=cfg,result=a))
for kind,cfg in itertools.product(['bd','adapter','app'],[(256,2,2,1,1,0xe400),(256,0,0,1,1,0xe400),(256,0,11,1,1,0xe400),(256,0,2,2,1,0xe400),(256,0,2,1,2,0xe400),(256,0,2,1,0,0xe400),(256,0,2,1,1,0),(256,0,2,1,1,0xff80),(0x400000,0,2,1,1,0xe400)]):
 a=run(False,kind,'zero',cfg);b=run(True,kind,'zero',cfg);assert a==b,(kind,cfg,a,b);results.append(dict(kind=kind,pattern='zero',configuration=cfg,result=a))
for nulls in range(1,8):
 cfg=(256,0,2,1,1,0xe400);a=run(False,'bd','valid',cfg,0,nulls);b=run(True,'bd','valid',cfg,0,nulls);assert a==b,(nulls,a,b);results.append(dict(kind='bd',nulls=nulls,result=a))
r=dict(status='PASS_STOCK_SDK_INITIALIZATION_NO_FUNCTION_CUTS',cases=len(results),elf_sha256=hashlib.sha256(elfpath.read_bytes()).hexdigest(),original_instruction_bytes_visited=len(visited),comparisons=results,limits=['Original reset data-copy/BSS-zero slice initializes fixtureRAM; not full reset/boot/hardware validation.','Only selected SDK ELF sections overlay stock fixturecode; ELF segment padding excluded to preserve originalCRT/borrowedprimitives. SDKcompiled EEPROM/provider helpers execute; stockmemory/division borrowed by address; noentrycuts/SROMcalls; notall-native-source closure.','Storage rows are constructed7168-byte region, not device capture; native provider addresses normalized by identity.','Configuration and raw16/32-bit truncation/overflow are preserved; malformed pointer/zero provider granularity outside contract.','Initialization success does not prove valid persisted UNVE record or physicaldurability.'])
(D/'sdk-initializer-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(results),'native/original initialization cases, no function cuts')
