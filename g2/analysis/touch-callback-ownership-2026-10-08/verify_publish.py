from pathlib import Path
import sys,json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;ROOT=D.parents[2];fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';image=fw[32:];elfpath=Path(sys.argv[1]);segments=[]
with elfpath.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='touch_report_publish_slice')
def run(native,seed,mask,oldcount):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
 for a,n in [(0x3000,0x9000),(0x100000,0x10000),(0x20000000,0x10000),(0x40040000,0x1000)]:u.mem_map(a,n)
 if native:
  for a,b in segments:u.mem_write(a,b)
 else:u.mem_write(0x3300,image)
 report=bytes((seed+i*17)&255 for i in range(16));u.mem_write(0x20000980,b'\xdd'*80);u.mem_write(0x20000990,report);ctx=bytearray(b'\xcc'*84);struct.pack_into('<I',ctx,48,oldcount);u.mem_write(0x200008ec,bytes(ctx));u.reg_write(UC_ARM_REG_R4,0x20000990);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.reg_write(UC_ARM_REG_PRIMASK,mask);events=[]
 def code(u,pc,size,user):
  if not native and pc==0x3c36:u.emu_stop()
 def write(u,access,addr,size,val,user):
  if 0x200009b0<=addr<0x200009c0 or 0x20000914<=addr<=0x20000920 or addr==0x40040444:events.append([addr,size,val])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((entry if native else 0x3c18)|1,0x20000000,count=400);assert u.reg_read(UC_ARM_REG_PC)==(0x20000000 if native else 0x3c36)
 return {'memory':u.mem_read(0x20000980,80).hex(),'context':u.mem_read(0x200008ec,84).hex(),'events':events,'sp':u.reg_read(UC_ARM_REG_SP),'primask':u.reg_read(UC_ARM_REG_PRIMASK)}
cases=[]
for vals in itertools.product([0,1,127,255],[0,1],[0,7,16,0xffffffff]):
 a=run(False,*vals);b=run(True,*vals);assert a==b,(vals,a,b);assert bytes.fromhex(b['context'])[40:56]==struct.pack('<IIII',0x200009b0,16,0,0);cases.append({'inputs':vals,'result':b})
r={'status':'PASS_BOUNDED_REPORT_PUBLISH_SLICE','cases':len(cases),'stock_range':['0x3c18','0x3c36'],'stock_slice_sha256':hashlib.sha256(image[0x918:0x936]).hexdigest(),'source_sha256':hashlib.sha256((D/'report_publish.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'comparisons':cases,'limits':['Stock comparison starts at internal slice with r4=report storage, ends before logger; not a whole-function replacement.','Actual stock and public descriptor-arm instructions, no child stubs; synthetic RAM/GPIO, no physical IRQ or host read.','Ordered writes compare; unrelated caller registers/flags outside contract.']};(D/'publish-results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'original publish slice/source cases')
