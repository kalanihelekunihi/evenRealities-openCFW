from pathlib import Path
import sys,json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';im=fw[32:];elfpath=Path(sys.argv[1]);segments=[]
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='case_voltage_scaling')
def run(native,scale,cr1,clock,clear_after,mask):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 for a,n in [(0x08000000,0x10000),(0x100000,0x20000),(0x20000000,0x10000),(0x40007000,0x1000)]:u.mem_map(a,n)
 if native:
  for a,b in segments:u.mem_write(a,b)
 else:u.mem_write(0x08000000,im)
 u.mem_write(0x40007000,struct.pack('<I',cr1));u.mem_write(0x20000124,struct.pack('<I',clock));u.mem_write(0x40007014,struct.pack('<I',0xa0000400));u.reg_write(UC_ARM_REG_R0,scale);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_PRIMASK,mask);reads=[];writes=[]
 def read(u,access,addr,size,val,user):
  if addr==0x40007014:
   v=0xa0000400 if clear_after<0 or len(reads)<clear_after else 0xa0000000;u.mem_write(addr,struct.pack('<I',v));reads.append(v)
 def write(u,access,addr,size,val,user):
  if addr==0x40007000:writes.append([addr,size,val])
 u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((entry if native else 0x08005048)|1,0x20000000,count=200000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return {'return':u.reg_read(UC_ARM_REG_R0),'writes':writes,'busy_reads':reads,'sp':u.reg_read(UC_ARM_REG_SP),'primask':u.reg_read(UC_ARM_REG_PRIMASK)}
cases=[]
for scale,cr1,clock,mask in itertools.product([0,0x200,0x400,0x600,0xffffffff],[0,0xffffffff,0x12345678],[0,1,1000000,16000000,64000000,0xffffffff],[0,1]):
 budget=((clock*6)&0xffffffff)//1000000+1
 for clear in sorted(set([-1,0,1,budget,budget+1])):
  vals=(scale,cr1,clock,clear,mask);a=run(False,*vals);b=run(True,*vals);assert a==b,(vals,a,b)
  assert a['writes'][0][2]==((cr1&~0x600)|scale)
  timeout=scale==0x200 and (clear<0 or clear>budget);assert a['return']==(3 if timeout else 0)
  if scale!=0x200:assert not a['busy_reads']
  cases.append({'inputs':vals,'budget':budget,'result':a})
r={'status':'PASS_BOUNDED_VOLTAGE_SCALING_POLL','cases':len(cases),'source_sha256':hashlib.sha256((D/'voltage_scaling.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'stock_body_sha256':hashlib.sha256(im[0x5048:0x5086]).hexdigest(),'comparisons':cases,'limits':['Actual stock divide helper and source independent divide instructions execute, no semantic child cuts.','SR2 readiness changes are injected on read count, not real regulator time or clock transition.','Invalid raw scales/overflow clocks are callee tests, not endorsed API input.','Register writes, busy reads, return, SP and PRIMASK compare; other scratch registers/flags outside contract.']};(D/'results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'original/source voltage scaling cases')
