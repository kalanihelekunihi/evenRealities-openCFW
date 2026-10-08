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
def run(native,restart,reload,threshold,initialized,status,mask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 for a,n in [(0x3000,0x9000),(0x100000,0x20000),(0x20000000,0x10000)]:u.mem_map(a,n)
 if native:
  for a,b in segments:u.mem_write(a,b)
 else:u.mem_write(0x3300,im)
 u.mem_write(0x20000938,b'\xdd'*112);u.mem_write(0x200009cd,bytes([reload,restart]));u.mem_write(0x200004e8,struct.pack('<H',threshold));u.mem_write(0x200008c4,bytes([initialized]));u.mem_write(0x200009d0,bytes(range(8)));u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_PRIMASK,mask);calls=[]
 payload=b'UNVE'+struct.pack('<HH',0x4321,0x9876)
 def code(u,pc,size,user):
  if pc==((symbols['eeprom_write_boundary']&~1) if native else 0x8aac):
   args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];calls.append([args,u.reg_read(UC_ARM_REG_PRIMASK)]);assert args==[0,0x200009d0,8,0x200008c8]
   assert bytes(u.mem_read(args[1],4))==b'UNVE';u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start((symbols['touch_deferred'] if native else 0x3a80)|1,0x20000000,count=4000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return {'state_guards':u.mem_read(0x20000938,112).hex(),'flags':u.mem_read(0x200009cd,2).hex(),'configuration':u.mem_read(0x200009d0,8).hex(),'threshold':u.mem_read(0x200004e8,2).hex(),'calls':calls,'sp':u.reg_read(UC_ARM_REG_SP),'primask':u.reg_read(UC_ARM_REG_PRIMASK)}
cases=[]
for vals in itertools.product([0,1],[0,1],[0,1,0x1234,0xffff],[0,1],[0,0x093e0004,1],[0,1]):
 a=run(False,*vals);b=run(True,*vals);assert a==b,(vals,a,b);assert b['flags']=='0000';assert bool(b['calls'])==bool(vals[1] and vals[3]);assert b['primask']==vals[-1]
 if vals[0]:assert bytes.fromhex(b['state_guards'])[8:88]==struct.pack('<H',vals[2] or 1000)+bytes(78)
 cases.append({'inputs':vals,'result':b})
r={'status':'PASS_DEFERRED_WITH_EXPLICIT_EEPROM_BOUNDARY','cases':len(cases),'elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((D/'deferred.c').read_bytes()).hexdigest(),'comparisons':cases,'limits':['Actual stock deferred/init/memset/default/read-adapter/critical instructions; native reconstructed deferred with public critical assembly.','EEPROM write entry0x8aac and native provider entry are explicit synthetic data/status-return cuts; no EEPROM or flash semantics proved.','Write provider retains input bytes and returns synthetic status; no physical programming or persistence proof.','No actual NVIC interruption or storage timing; external work occurs after saved PRIMASK is restored.']};(D/'deferred-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'deferred/source cases; EEPROM entry explicitly controlled')
