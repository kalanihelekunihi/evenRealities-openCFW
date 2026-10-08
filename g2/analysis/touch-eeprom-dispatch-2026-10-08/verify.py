from pathlib import Path
import sys,json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';im=fw[32:];elfpath=Path(sys.argv[1]);segments=[];symbols={}
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
def run(native,address,size,bound,data,simple,status,mask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 for a,n in [(0x3000,0x9000),(0x100000,0x20000),(0x20000000,0x10000)]:u.mem_map(a,n)
 if native:
  for a,b in segments:u.mem_write(a,b)
 else:u.mem_write(0x3300,im)
 ctx=0x200008c8;u.mem_write(ctx,b'\xaa'*32);u.mem_write(ctx+8,struct.pack('<I',bound));u.mem_write(ctx+13,bytes([simple]));u.mem_write(0x20003000,b'\xdd'*32)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[address,data,size,ctx]):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_PRIMASK,mask);calls=[]
 cuts={(symbols['eeprom_simple_boundary']&~1 if native else 0x85d4):'simple',(symbols['eeprom_extended_boundary']&~1 if native else 0x8808):'extended'}
 def code(u,pc,size,user):
  if pc in cuts:
   args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];calls.append([cuts[pc],args]);u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start((symbols['touch_eeprom_write_dispatch'] if native else 0x8aac)|1,0x20000000,count=500);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return {'return':u.reg_read(UC_ARM_REG_R0),'calls':calls,'context':u.mem_read(ctx,32).hex(),'buffer':u.mem_read(0x20003000,32).hex(),'sp':u.reg_read(UC_ARM_REG_SP),'primask':u.reg_read(UC_ARM_REG_PRIMASK)}
cases=[]
for vals in itertools.product([0,1,255,0xfffffffe],[0,1,8,0xffffffff],[0,8,256,0xffffffff],[0,0x20003000],[0,1,255],[0,0x093e0004,0xffffffff],[0,1]):
 a=run(False,*vals);b=run(True,*vals);assert a==b,(vals,a,b);valid=vals[1]!=0 and ((vals[0]+vals[1])&0xffffffff)<=vals[2] and vals[3]!=0;assert bool(a['calls'])==valid;assert a['return']==(vals[5] if valid else 0x093e0000);cases.append({'inputs':vals,'result':a})
r={'status':'PASS_EEPROM_DISPATCH_EXPLICIT_PROVIDER_CUTS','cases':len(cases),'elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((D/'write_dispatch.c').read_bytes()).hexdigest(),'stock_body_sha256':hashlib.sha256(im[0x57ac:0x57dc]).hexdigest(),'comparisons':cases,'limits':['Actual dispatcher instructions; simple/extended providers are explicit return-status cuts, no bytes read or storage implementation proved.','Modulo32 address+size behavior preserved; malformed overflow inputs not endorsed. Context is always valid mapped RAM.','Return, call choice/arguments, unchanged buffers/context, SP and PRIMASK compare; scratch registers/flags and read ordering outside contract.']};(D/'results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'EEPROM dispatch cases with explicit provider cuts')
