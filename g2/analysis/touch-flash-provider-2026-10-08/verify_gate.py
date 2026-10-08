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
def run(native,enabled,physical,step,check,erase,program,mask):
 u=guest(native);ctx=bytearray(32);struct.pack_into('<H',ctx,2,physical);struct.pack_into('<I',ctx,4,step);struct.pack_into('<I',ctx,28,0x20002000);ctx[15]=enabled;u.mem_write(0x200008c8,bytes(ctx));table=bytearray(48);struct.pack_into('<I',table,0,0x12345678)
 for slot,addr in [(11,0x20001001),(7,0x20001021),(6,0x20001041)]:struct.pack_into('<I',table,slot*4,addr)
 u.mem_write(0x20002000,bytes(table))
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[0xe400,0x20003000,0x200008c8]):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_PRIMASK,mask);calls=[];cuts={0x20001000:('check',check,3),0x20001020:('erase',erase,3),0x20001040:('program',program,4)}
 def code(u,pc,n,user):
  if pc in cuts:
   name,status,count=cuts[pc];args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]][:count];calls.append([name,args]);u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start((symbols['touch_eeprom_program_gate'] if native else 0x7ea4)|1,0x20000000,count=500);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return {'return':u.reg_read(UC_ARM_REG_R0),'calls':calls,'context':u.mem_read(0x200008c8,32).hex(),'sp':u.reg_read(UC_ARM_REG_SP),'primask':u.reg_read(UC_ARM_REG_PRIMASK)}
cases=[]
for vals in itertools.product([0,1],[1,127,128,256],[0,64,128,512],[0,1],[0,1],[0,1],[0,1]):
 a=run(False,*vals);b=run(True,*vals);assert a==b,(vals,a,b);expect=0 if not vals[0] else 0x093e0003 if (vals[3] and vals[4]) or vals[5] else 0;assert a['return']==expect;cases.append({'inputs':vals,'result':a})
r={'status':'PASS_PROGRAM_GATE_CONTROLLED_CALLBACKS','cases':len(cases),'elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'comparisons':cases,'limits':['Three callbacks are explicit no-state-change status cuts; covers generic branch/error handling, not normal provider hardware behavior.','Provider/context table stable during callbacks; mutation/reentrancy outside contract.','Normal stock slot11 returns zero, so conditional erase branch is not inferred reachable in the actual installed provider.']};(D/'gate-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'program-gate cases with explicit callback cuts')
