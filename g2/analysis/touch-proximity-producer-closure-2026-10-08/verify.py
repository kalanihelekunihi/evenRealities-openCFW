from pathlib import Path
import sys,struct,itertools,json,hashlib
from unicorn.arm_const import UC_ARM_REG_R3
D=Path(__file__).resolve().parent
ns={'__file__':str(D.parent/'touch-slider-producer-closure-2026-10-08/verify.py')}
exec(Path(ns['__file__']).read_text().split('patterns=')[0],ns)
def fixture():
 u=ns['guest']();ns['prepare'](u,[0]*4,0,2);w=0x20004000;c=0x20005000;s=0x20006000
 u.mem_write(w+56,struct.pack('<H',1));u.mem_write(w+116,struct.pack('<H',0x3696));u.mem_write(w+36,struct.pack('<I',64));u.mem_write(c+8,struct.pack('<HH',480,200));u.mem_write(c+30,struct.pack('<H',55));return u
counts={'filters':0,'proximity':0};coverage=set()
def hook(u,a,n,data):
 if 0x4f6e<=a<0x4fee or 0x5054<=a<0x50ee or 0x5a0a<=a<0x5a94:coverage.update(range(a,a+n))
for x,prior,fraction,flags in itertools.product([0,1,500,2000,65535],[[0]*6,[100,900,300,200,100,50],[65535]*6],[0,1,255],[0x3696,0x10,0x80,0x280,0x400,0x1400]):
 result=[]
 for native in [False,True]:
  u=fixture();u.mem_write(0x20006000,struct.pack('<H',x));u.mem_write(0x20004000+116,struct.pack('<H',flags));u.mem_write(0x20007000,struct.pack('<6H',*prior));u.mem_write(0x20007100,bytes([fraction]));u.reg_write(UC_ARM_REG_R3,0x20007100)
  if not native:u.hook_add(ns['UC_HOOK_CODE'],hook)
  ns['call'](u,ns['symbols']['touch_raw_filters'] if native else 0x50a0,[0x20004000,0x20006000,0x20007000]);result.append((bytes(u.mem_read(0x20006000,10)),bytes(u.mem_read(0x20007000,12)),bytes(u.mem_read(0x20007100,1))))
 assert result[0]==result[1],('filter',x,prior,fraction,flags,result);counts['filters']+=1
for diff,status,deb,on in itertools.product([0,144,145,146,254,255,256,424,425,426,534,535,536,65535],range(8),[0,1,2,255],[0,1,2]):
 result=[]
 for native in [False,True]:
  u=fixture();u.mem_write(0x20006000+4,struct.pack('<HB',diff,status));u.mem_write(0x20006100,bytes([deb,deb]));u.mem_write(0x20005000+32,bytes([on]))
  if not native:u.hook_add(ns['UC_HOOK_CODE'],hook)
  ns['call'](u,ns['symbols']['touch_proximity_process'] if native else 0x5a0a,[0x20004000]);result.append((bytes(u.mem_read(0x20006000,10)),bytes(u.mem_read(0x20005000,60)),bytes(u.mem_read(0x20006100,2))))
 assert result[0]==result[1],('prox',diff,status,deb,on,result);counts['proximity']+=1
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':counts,'original_instruction_bytes_observed':sorted(coverage),'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Synthetic acquired raw/difference counts and coherent pointers.','No ADC, physical timing, runtime calibrated max raw or hardware validation.','Leaf filters/proximity only; full report composition pending.']},indent=2)+'\n');print(counts)
