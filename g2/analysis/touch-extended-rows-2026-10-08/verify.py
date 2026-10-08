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
def run(native,address,size,seed,redundant,last,merge_status,bad,mask):
 u=guest(native);payload=bytes((i*11)&255 for i in range(512));u.mem_write(0x20003000,payload);ctx=bytearray(32);struct.pack_into('<HH',ctx,0,4,128);struct.pack_into('<I',ctx,4,128);struct.pack_into('<I',ctx,8,256);ctx[12]=2;ctx[14]=redundant;ctx[15]=1;struct.pack_into('<I',ctx,16,0xe400);struct.pack_into('<HH',ctx,20,64,48);struct.pack_into('<I',ctx,24,last);struct.pack_into('<I',ctx,28,0x20000ed4);u.mem_write(0x200008c8,bytes(ctx));provider=bytearray(48)
 for slot,name,stock in [(6,'touch_storage_program',0x4811),(7,'touch_storage_zero',0x47b1),(11,'touch_storage_no_erase',0x47ab)]:struct.pack_into('<I',provider,slot*4,symbols[name] if native else stock)
 u.mem_write(0x20000ed4,bytes(provider))
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[address,0x20003000,size,0x200008c8]):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_PRIMASK,mask);events=[]
 cuts={(symbols['extended_integrity_boundary']&~1 if native else 0x8058):'integrity',(symbols['extended_history_boundary']&~1 if native else 0x814c):'history',(symbols['extended_merge_boundary']&~1 if native else 0x8680):'merge'}
 def code(u,pc,n,user):
  if pc in cuts:
   name=cuts[pc];args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
   if name=='integrity':assert args[1]==0x200008c8;u.mem_write(args[0],struct.pack('<II',seed,0));events.append(['integrity',seed])
   else:
    assert args[0]==0x20000cd4 and args[2]==0x200008c8;events.append([name,args[1],bytes(u.mem_read(args[0],128)).hex()]);u.mem_write(args[0]+64,bytes([0xa5 if name=='history' else 0x5a])*64)
   u.reg_write(UC_ARM_REG_R0,merge_status if name=='merge' else 0x093e0002);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def write(u,access,addr,n,value,user):
  if addr==0x40100004:
   cmd=value&255;arg=int.from_bytes(u.mem_read(0x40100008,4),'little')
   if cmd in [4,5,0x18]:p=list(struct.unpack('<II',u.mem_read(arg,8)));data=bytes(u.mem_read(arg+8,128)).hex()
   elif cmd in [0x16,0x17]:p=list(struct.unpack('<II',u.mem_read(arg,8)));data=None
   else:p=[arg];data=None
   events.append(['srom',cmd,p,data,u.reg_read(UC_ARM_REG_PRIMASK)]);status=0xa0000000 if not bad or (bad==2 and cmd==4) else 0xf0000005;u.mem_write(0x40100008,struct.pack('<I',status))
  if addr==0x40030030:events.append(['clock',value])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((symbols['touch_extended_write'] if native else 0x8808)|1,0x20000000,count=150000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000,(native,address,size,seed,redundant,last,merge_status,bad,mask,hex(u.reg_read(UC_ARM_REG_PC)),events[-2:])
 return {'return':u.reg_read(UC_ARM_REG_R0),'events':events,'context':u.mem_read(0x200008c8,32).hex(),'row':u.mem_read(0x20000cd4,128).hex(),'input':u.mem_read(0x20003000,512).hex(),'sp':u.reg_read(UC_ARM_REG_SP),'primask':u.reg_read(UC_ARM_REG_PRIMASK)}
cases=[]
for vals in itertools.product([0,17],[1,48,49,96,145],[0,0xffffffff],[0,1],[0xe400,0xe780],[0,0x093e0004,0x093e0002],[0,1,2],[0,1]):
 a=run(False,*vals);b=run(True,*vals);assert a==b,(vals,a,b);assert a['return']==vals[5];cases.append({'inputs':vals,'result':a})
r={'status':'PASS_EXTENDED_ORCHESTRATION_EXPLICIT_HISTORY_CUTS','cases':len(cases),'elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'comparisons':cases,'limits':['Actual stock extended/division/next-row/CRC/memory/program-gate/provider/flash/critical instructions; corresponding independent native C and public critical assembly.','Integrity8058,history814c,merge8680 are explicit data/status cuts; historical data selection/recovery algorithms not proved.','External CPUSS/SROM completion is synthetic; no physical programming or persistence.','Source nonzero size/capacity, row128/capacity48, bounded counts; geometry choices are coherent fixtures rather than proof of stock configuration.']};(D/'results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'extended orchestration cases; three history cuts and SROM model explicit')
