from pathlib import Path
import sys,json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';im=fw[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
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

def fixture(kind,parameter):
 if kind in ['zero','erased']:return bytes(2048) if kind=='zero' else b'\xff'*2048
 raw=bytearray(2048);record=struct.pack('<IHH',0x12345678 if kind=='wrongmagic' else 0x45564e55,321,parameter)
 for i in range(16):
  r=bytearray(128);struct.pack_into('<III',r,4,(i%8)+1,0,0);r[64:72]=record
  if i%8==7:struct.pack_into('<II',r,8,0,8);r[16:24]=record
  struct.pack_into('<I',r,0,checksum(r))
  if kind=='corrupt' or (kind=='mirror' and i<8) or (kind=='badhistoric' and i%8!=7):r[0]^=1
  raw[i*128:(i+1)*128]=r
 return bytes(raw)
def boot(native,kind,parameter,mode,mask,invalid=False,initial_storage=None):
 u=guest(native);u.mem_map(0x40100000,0x1000);u.mem_map(0x40030000,0x1000);u.mem_write(0xe400,fixture(kind,parameter) if initial_storage is None else initial_storage);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 if invalid:u.mem_write(0x200004c4,b'\x02')
 events=[];logs=[];phase='';latch=None;visit=set()
 names={'erase':('touch_application_erase',0x35b0),'write':('touch_application_write',0x3568),'read':('touch_application_read',0x3520),'delay':('touch_bootstrap_delay',0xa2f0),'log':('touch_bootstrap_log',0x3ee0)}
 entries={((symbols[n] if native else a)&~1):k for k,(n,a) in names.items()}
 def code(u,pc,n,user):
  nonlocal phase
  if not native and (0x395c<=pc<0x39f8 or 0x8ae0<=pc<0x8bf0):visit.update(range(pc,pc+n))
  k=entries.get(pc)
  if k in ['erase','write','read']:phase=k;events.append(['app',k])
  elif k=='delay':events.append(['delay-argument',u.reg_read(UC_ARM_REG_R0)])
  elif k=='log':
   fmt=u.reg_read(UC_ARM_REG_R0);vals=[u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2)]
   logs.append([fmt,*(vals if fmt==0xaba8 else vals[:1] if fmt in [0xaab8,0xab20,0xab48] else [])])
 def write(u,access,addr,n,value,user):
  nonlocal latch
  if addr==0x40100004:
   cmd=value&255;arg=int.from_bytes(u.mem_read(0x40100008,4),'little');status=0xa0000000
   params=list(struct.unpack('<II',u.mem_read(arg,8))) if cmd in [4,5,0x18,0x16,0x17] else [arg]
   dest=(params[0]>>16)*128 if cmd==5 else 0
   if mode=='load-error' and cmd==4:status=0xf0000005
   if mode in ['program-error','torn16','torn64'] and cmd==5:status=0xf0000005
   if mode=='erase-base-error' and phase=='erase' and cmd==5 and dest in [0xe400,0xe800]:status=0xf0000005
   if cmd in [4,5,0x18]:
    data=bytes(u.mem_read(arg+8,128));events.append(['srom',phase,cmd,params,data.hex(),status,u.reg_read(UC_ARM_REG_PRIMASK)])
    if cmd==4 and status==0xa0000000:latch=data
    if cmd==5:
     assert latch==data
     count=128 if status==0xa0000000 else 16 if mode=='torn16' else 64 if mode=='torn64' else 0
     if count:u.mem_write(dest,data[:count])
   else:events.append(['srom',phase,cmd,params,status])
   u.mem_write(0x40100008,struct.pack('<I',status))
  elif addr==0x40030030:events.append(['clock',value])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 call(u,symbols['touch_config_bootstrap'] if native else 0x395c,[],5000000)
 c=bytearray(u.mem_read(0x200008c8,32));c[28:32]=struct.pack('<I',0x20000ed4)
 result=dict(record=u.mem_read(0x200009d0,8).hex(),ready=u.mem_read(0x200008c4,1).hex(),context=c.hex(),storage=u.mem_read(0xe400,2048).hex(),events=events,logs=logs,sp=u.reg_read(UC_ARM_REG_SP),primask=u.reg_read(UC_ARM_REG_PRIMASK))
 return result,visit
cases=[];coverage=set()
for kind,parameter,mode,mask in itertools.product(['zero','erased','valid','wrongmagic','corrupt','mirror'],[0,1000,65535],['success','load-error','program-error','torn16','torn64','erase-base-error'],[0,1]):
 a,v=boot(False,kind,parameter,mode,mask);b,_=boot(True,kind,parameter,mode,mask);assert a==b,(kind,parameter,mode,mask,a,b);coverage.update(v);cases.append(dict(inputs=[kind,parameter,mode,mask],result=a))
for mask in [0,1]:
 a,v=boot(False,'zero',0,'success',mask,True);b,_=boot(True,'zero',0,'success',mask,True);assert a==b;coverage.update(v);cases.append(dict(inputs=['invalid-initializer',mask],result=a))
r=dict(status='PASS_ORIGINAL_NATIVE_BOOTSTRAP_NO_FUNCTION_CUTS',cases=len(cases),elf_sha256=hashlib.sha256(elfpath.read_bytes()).hexdigest(),coverage=sorted(coverage),comparisons=cases,limits=['SROM request responses and full/torn storage writes synthetic, not hardware behavior.','Actual reset copy/zero only; SystemInit not executed; delay argument10 and reset calibration are tested, physical units unverified.','Default extended row=sector128 geometry only; erase-failure branch not forced by function cuts.'])
(D/'results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'bootstrap cases')
