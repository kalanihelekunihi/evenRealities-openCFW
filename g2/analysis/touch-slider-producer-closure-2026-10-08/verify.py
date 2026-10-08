from pathlib import Path
import sys,json,hashlib,struct,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;fw=(D.parents[2]/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';elf=Path(sys.argv[1]);segments=[];symbols={}
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
coverage=set()
def guest():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x3000,0x9000);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x10000);u.mem_write(0x3300,fw[32:])
 for a,b in segments:u.mem_write(a,b)
 return u
def call(u,pc,args):
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(pc|1,0x20000000,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return u.reg_read(UC_ARM_REG_R0)
def prepare(u,diffs,active,debounce,threshold=100,hysteresis=10,on=2,config=0x800102,centroid=1,resolution=200,declared=4):
 w=bytearray(144);struct.pack_into('<II',w,0,0x20005000,0x20006000);struct.pack_into('<I',w,40,0x20006100);struct.pack_into('<I',w,48,centroid);struct.pack_into('<HH',w,52,resolution,0);struct.pack_into('<H',w,56,declared);struct.pack_into('<I',w,60,0x20006200);struct.pack_into('<I',w,112,config);w[122:124]=bytes([1,2]);u.mem_write(0x20004000,bytes(w));c=bytearray(60);struct.pack_into('<H',c,8,threshold);struct.pack_into('<H',c,30,hysteresis);c[32]=on;c[35]=0x20|active;struct.pack_into('<I',c,36,0x20006300);c[40]=1;u.mem_write(0x20005000,bytes(c));s=bytearray(40)
 for i,d in enumerate(diffs):struct.pack_into('<HHHBBBB',s,i*10,2000,1900,d,4,7,8,9)
 u.mem_write(0x20006000,bytes(s));u.mem_write(0x20006100,bytes([debounce]));u.mem_write(0x20006200,struct.pack('<IB3x',0x20006400,1));u.mem_write(0x20006300,struct.pack('<4H',77,88,99,111));u.mem_write(0x20006400,struct.pack('<4H',20,30,40,50))
def snap(u):
 return {'context':u.mem_read(0x20005000,60).hex(),'sensors':u.mem_read(0x20006000,40).hex(),'debounce':u.mem_read(0x20006100,1).hex(),'history_header':u.mem_read(0x20006200,8).hex(),'history_x':u.mem_read(0x20006400,2).hex(),'position_x':u.mem_read(0x20006300,2).hex(),'sp':u.reg_read(UC_ARM_REG_SP),'primask':u.reg_read(UC_ARM_REG_PRIMASK)}
def run(native,diffs,active,debounce,threshold,hysteresis,on,config,centroid=1,resolution=200,declared=4):
 u=guest();prepare(u,diffs,active,debounce,threshold,hysteresis,on,config,centroid,resolution,declared);u.reg_write(UC_ARM_REG_PRIMASK,active)
 if not native:
  def hook(u,a,n,user):
   if 0x48cc<=a<0x49ce or 0x49d4<=a<0x4abe or 0x5a94<=a<0x5ba2:coverage.update(range(a,a+n))
  u.hook_add(UC_HOOK_CODE,hook)
 call(u,symbols['touch_slider_process'] if native else 0x5a94,[0x20004000]);return snap(u)
patterns=[[0,0,0,0],[0,0,0,111],[111,0,0,0],[0,110,110,0],[0,111,111,0],[100,200,150,0],[65535,65535,65535,65535],[90,90,90,90],[91,91,91,91]];cases=[]
for diffs,active,debounce,on,config in itertools.product(patterns,[0,1],[0,1,2,3],[0,2],[0,0x800102]):
 args=(diffs,active,debounce,100,10,on,config);a=run(False,*args);b=run(True,*args);assert a==b,(args,{k:(a[k],b[k]) for k in a if a[k]!=b[k]});cases.append({'inputs':args,'result':a})
for centroid,resolution,declared in itertools.product([0,1,2,257],[0,1,200,65535],[0,1,2,3,4]):
 args=([50,100,80,0],1,0,100,10,2,0,centroid,resolution,declared);a=run(False,*args);b=run(True,*args);assert a==b,(args,a,b);cases.append({'inputs':args,'result':a})
r={'status':'PASS_ORIGINAL_NATIVE_SLIDER_DEFINED_FIELDS','cases':len(cases),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'coverage':sorted(coverage),'comparisons':cases,'limits':['Inputdifferences synthetic, not scan/ADC acquisition or baseline update.','Atleastthree allocatedsensorrecords even declaredcount<3 because stockcentroidforcesminimum3.','Only definedX/count/status/debounce/historyX compared; stocklocalY/Z/paddinguninitialized,nativezeros excluded.','Coherent bounded widget/context/history pointers; no malformedmemory safety claim.']};(D/'results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'defined slider cases;',len(coverage),'bytes covered')
