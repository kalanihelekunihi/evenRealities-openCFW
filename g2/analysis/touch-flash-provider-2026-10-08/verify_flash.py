from pathlib import Path
import sys,json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
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
def run(native,address,data,mask,statuses):
 u=guest(native);payload=bytes((i*7)&255 for i in range(128));u.mem_write(0x20003000,payload);u.reg_write(UC_ARM_REG_R0,address);u.reg_write(UC_ARM_REG_R1,data);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_PRIMASK,mask);events=[];positions={4:0,0x16:1,0x15:2,5:3,0x18:3,0x17:4};argstore=[]
 def write(u,access,addr,size,value,user):
  if addr==0x40100008:argstore.append(value)
  if addr==0x40100004:
   cmd=value&255;arg=int.from_bytes(u.mem_read(0x40100008,4),'little');p=[]
   if cmd in [4,5,0x18]:
    p=list(struct.unpack('<II',u.mem_read(arg,8)));assert bytes(u.mem_read(arg+8,128))==payload
   elif cmd in [0x16,0x17]:p=list(struct.unpack('<II',u.mem_read(arg,8)))
   else:p=[arg]
   events.append(['srom-request',cmd,p,u.reg_read(UC_ARM_REG_PRIMASK)]);u.mem_write(0x40100008,struct.pack('<I',statuses[positions[cmd]]))
  if addr==0x40030030:events.append(['clock-write',addr,size,value])
 u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((symbols['touch_flash_write_row'] if native else 0x8d50)|1,0x20000000,count=4000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return {'return':u.reg_read(UC_ARM_REG_R0),'events':events,'sysarg_stores':len(argstore),'sp':u.reg_read(UC_ARM_REG_SP),'primask':u.reg_read(UC_ARM_REG_PRIMASK),'input':u.mem_read(0x20003000,128).hex()}
success=0xa0000000;patterns=[[success]*5]
for stage,bad in itertools.product(range(5),[0xf0000001,0xf0000014,0xf000001f,0]):
 p=[success]*5;p[stage]=bad;patterns.append(p)
patterns.extend([[success,success,success,0xf0000001,0xf0000014],[success,success,success,0,0xf0000001]])
cases=[]
for vals in itertools.product([0,0xe400,0xff80,0x10000,1,0x0ffff200,0x0ffff280,0x0ffff400,0xffffffff],[0,0x20003000],[0,1],patterns):
 a=run(False,*vals);b=run(True,*vals);assert a==b,(vals,a,b);assert a['primask']==vals[2];cases.append({'inputs':vals,'result':a})
decoders=[]
for status in [0,0x80000000,0xa0000000,0xafffffff,*range(0xf0000000,0xf0000017),0xffffffff]:
 results=[]
 for native in [False,True]:
  u=guest(native);u.mem_write(0x40100008,struct.pack('<I',status));u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start((symbols['touch_flash_status'] if native else 0x8bf4)|1,0x20000000,count=100);assert u.reg_read(UC_ARM_REG_PC)==0x20000000;results.append(u.reg_read(UC_ARM_REG_R0))
 assert results[0]==results[1];decoders.append({'status':status,'return':results[0]})
r={'status':'PASS_NATIVE_FLASH_CHOREOGRAPHY_SYNTHETIC_SROM','cases':len(cases),'decoder_cases':len(decoders),'elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'comparisons':cases,'decoder_comparisons':decoders,'limits':['Actual stock flash/decoder/clock/critical/memcpy and independent native flash/public critical instructions execute; no helper function cuts.','CPUSS request writes receive synthetic immediate SROM status; SROM physical code/programming/clock effects not executed.','Transient stack pointers normalized as parameter contents plus store counts; final SP/PRIMASK compare.','Stock decoder reads SYSARG once; no timer, retry or physical syscall-completion proof.']};(D/'flash-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'flash choreography;',len(decoders),'decoder cases; SROM responses synthetic')
