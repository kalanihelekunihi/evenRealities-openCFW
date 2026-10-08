from pathlib import Path
import sys,json,hashlib,struct,itertools,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
D=Path(__file__).resolve().parent;fw=(D.parents[2]/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes();assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';elf=Path(sys.argv[1]);segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);pc=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='touch_gesture_step');segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
visited=set()
def run(native,state,active,position,stamp,mask,null=False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x3000,0x9000);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x10000);u.mem_write(0x3300,fw[32:])
 for a,b in segments:u.mem_write(a,b)
 u.mem_write(0x20006000,bytes(state));u.mem_map(0x40040000,0x1000);u.mem_write(0x20000874,struct.pack('<I',24000));u.mem_write(0x2000086c,struct.pack('<I',0x2ee00000));gpio=[]
 def mmio(u,access,a,n,v,user):gpio.append([a,v])
 u.hook_add(UC_HOOK_MEM_WRITE,mmio,begin=0x40040400,end=0x400404ff)
 def code(u,a,n,user):
  if 0x4070<=a<0x43da:visited.update(range(a,a+n))
 if not native:u.hook_add(UC_HOOK_CODE,code,begin=0x4070,end=0x43d8)
 for reg,v in [(UC_ARM_REG_R0,0 if null else 0x20006000),(UC_ARM_REG_R1,active),(UC_ARM_REG_R2,position),(UC_ARM_REG_R3,stamp),(UC_ARM_REG_SP,0x20008000),(UC_ARM_REG_LR,0x20000001),(UC_ARM_REG_PRIMASK,mask)]:u.reg_write(reg,v)
 u.emu_start((pc if native else 0x4070)|1,0x20000000,count=20000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
 return {'return':u.reg_read(UC_ARM_REG_R0),'gpio':gpio,'state':u.mem_read(0x20006000,80).hex(),'sp':u.reg_read(UC_ARM_REG_SP),'primask':u.reg_read(UC_ARM_REG_PRIMASK)}

rng=random.Random(20261008);cases=[]
def state_fixture(mode,previous,pending,count=2):
 s=bytearray(rng.randbytes(80));struct.pack_into('<H',s,0,1000);s[12]=previous;s[13]=100;s[21]=100;s[32]=count;s[33]=pending;s[44]=100;s[72:77]=bytes([0,3,100,0,mode]);
 for off in [16,24,36,40]:struct.pack_into('<I',s,off,100)
 return s
for mode,previous,active,elapsed,position,pending in itertools.product([0,1,2,3],[0,1],[0,1,2],[0,99,100,299,300,301,999,1000,1001,0xffffffff],[75,76,85,86,100,114,115,124,125],[0,1]):
 s=state_fixture(mode,previous,pending);stamp=(100+elapsed)&0xffffffff;mask=mode&1;a=run(False,s,active,position,stamp,mask);b=run(True,s,active,position,stamp,mask);assert a==b,([mode,previous,active,elapsed,position,pending],{k:(a[k],b[k]) for k in a if a[k]!=b[k]});cases.append({'inputs':[mode,previous,active,elapsed,position,pending,mask],'result':a})
for count,pending,elapsed in itertools.product([0,1,2,3,4,5,9,10,255],[0,1],[300,301]):
 if count in [5,9] and elapsed==301 and not pending:continue
 s=state_fixture(0,0,pending,count);a=run(False,s,0,100,100+elapsed,0);b=run(True,s,0,100,100+elapsed,0);assert a==b,(count,pending,elapsed,a,b);cases.append({'inputs':['idle-count',count,pending,elapsed],'result':a})
for count in [1,3,4,5,9,10,255]:
 s=state_fixture(0,1,0,count);a=run(False,s,0,100,200,0);b=run(True,s,0,100,200,0);assert a==b;cases.append({'inputs':['release-count',count],'result':a})
s=state_fixture(0,0,1,255);a=run(False,s,1,100,200,0);b=run(True,s,1,100,200,0);assert a==b;cases.append({'inputs':['saturated-tap-count'],'result':a})
for threshold in [0,1,65535]:
 for elapsed in [max(0,(threshold or 1000)-1),threshold or 1000,(threshold or 1000)+1]:
  s=state_fixture(0,1,0);struct.pack_into('<H',s,0,threshold);a=run(False,s,1,100,100+elapsed,0);b=run(True,s,1,100,100+elapsed,0);assert a==b;cases.append({'inputs':['threshold',threshold,elapsed],'result':a})
for mask in [0,1]:
 a=run(False,bytes(80),0,0,0,mask,True);b=run(True,bytes(80),0,0,0,mask,True);assert a==b;cases.append({'inputs':['null',mask],'result':a})
r={'status':'PASS_INDEPENDENT_NATIVE_ORIGINAL_GESTURE_MACHINE_NO_FUNCTION_CUTS','cases':len(cases),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'original_instruction_bytes_visited':len(visited),'coverage':sorted(visited),'comparisons':cases,'limits':['Valid80-byte state/ring domain; direct state configurations can be synthetic rather than normally reachable.','Standalone native source includes independent speed/delay; no borrowed firmware functions.','GPIO/SysTick cadence/physical elapsed units not simulated; rearm delay loops execute using reset-scale24000.']};(D/'results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'machine cases;',len(visited),'original bytes covered')
