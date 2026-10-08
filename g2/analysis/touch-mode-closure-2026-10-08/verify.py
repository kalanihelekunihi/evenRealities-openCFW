from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-scan-watchdog-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split("counts={'watchdog'")[0],ns);g=ns['ns'];counts={'mode':0,'mrss':0,'init_fields':0};coverage=set()
def fixture():
 u=ns['guest']();u.mem_write(0x20002000+4,struct.pack('<I',0x20003200));u.mem_write(0x20002000+28,struct.pack('<I',0x20003400));u.mem_write(0x20002000+36,struct.pack('<I',0x20003600));u.mem_write(0x20003100+4,struct.pack('<I',0x20003700));u.mem_write(0x20003200+8,struct.pack('<I',0xffffffff));u.mem_write(0x20003400+21,b'\xff');u.mem_write(0x20003500+113,b'\xff');u.mem_write(0x20003500+115,b'\xff');u.mem_write(0x20000870,b'\x01');u.mem_write(0x40000180,struct.pack('<I',1));u.mem_write(0x40000000,struct.pack('<I',0xffffffff));return u
for old,desired,busy in itertools.product([0,1,2,3,4,5,6,7,8,255],[0,1,2,3,4,5,6,7,8,255],[0,1]):
 results=[]
 for native in [False,True]:
  u=fixture();u.mem_write(0x20003500+85,bytes([old]));u.mem_write(0x20007300,struct.pack('<5I',*[0x20001001+4*i for i in range(5)]));u.mem_write(0x20001000,b'\x70\x47'*10);calls=[];bus=[]
  labels={0x6078:'ios',0x60ea:'shield',0x6044:'cmod',0x8fd0:'configure',0x68ec:'dither'};native_labels={0x20001000+4*i:name for i,name in enumerate(['ios','shield','cmod','configure','dither'])}
  def code(u,a,n,data):
   if not native and 0x6ac0<=a<0x6bca:coverage.update(range(a,a+n))
   label=(native_labels if native else labels).get(a)
   if label:
    regs=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
    if label=='configure':calls.append([label,regs]);u.reg_write(UC_ARM_REG_R0,busy)
    else:
     if not native and label in ['ios','shield','cmod']:
      assert regs[:2]==[9,0]
      assert regs[2]==(0 if label=='ios' else 1)
     calls.append([label]);u.reg_write(UC_ARM_REG_R0,0)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def read(u,access,a,n,v,data):
   if 0x40000000<=a<0x40004000:bus.append(['read',a-0x40000000,n])
  def write(u,access,a,n,v,data):
   if 0x40000000<=a<0x40004000:bus.append(['write',a-0x40000000,n,v])
  u.hook_add(g['UC_HOOK_CODE'],code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);r=g['call'](u,g['symbols']['touch_switch_mode'] if native else 0x6ac0,[desired,0x20002000,0x20007300]);results.append((r,u.mem_read(0x20003200,32).hex(),u.mem_read(0x20003400,128).hex(),u.mem_read(0x20003500,128).hex(),calls,bus))
 assert results[0]==results[1],(old,desired,busy,results);counts['mode']+=1
for timeout,target,change_after in itertools.product([0,1,3,315],[0,1,2,3,4],[0,1,4,500]):
 results=[]
 for native in [False,True]:
  u=fixture();reads=[0];mask=0x1000000 if target in [2,3] else 1;expected=((target<<24)&mask) if target in [2,3] else target
  def read(u,access,a,n,v,data):
   if a==0x40000180:
    val=expected if reads[0]<change_after else expected^mask;u.mem_write(a,struct.pack('<I',val));reads[0]+=1
  u.hook_add(UC_HOOK_MEM_READ,read);r=g['call'](u,g['symbols']['touch_wait_mrss'] if native else 0x6608,[timeout,target,0x20002000]);results.append((r,reads[0]))
 assert results[0]==results[1],(timeout,target,change_after,results);counts['mrss']+=1
for maximums,flags in itertools.product([[0]*6,[0,1,1,0,65535,65535],[65535]*6],[0,1,255]):
 results=[]
 for native in [False,True]:
  u=fixture();u.mem_write(0x20003000,bytes(range(64)));u.mem_write(0x20004000,struct.pack('<I',0x20005000));u.mem_write(0x20003500,b'\xa5'*128)
  for j in range(3):u.mem_write(0x20005000+j*60+4,struct.pack('<HH',*maximums[j*2:j*2+2]));u.mem_write(0x20005000+j*60+35,bytes([flags]))
  if native:g['call'](u,g['symbols']['touch_cap_init_fields'],[0x20002000])
  else:
   u.reg_write(UC_ARM_REG_R0,0x20002000);u.reg_write(UC_ARM_REG_R4,0x20002000);u.emu_start(0x4c85,0x4d8e,count=10000)
  results.append((u.mem_read(0x20003500,128).hex(),u.mem_read(0x20005000,180).hex()))
 assert results[0]==results[1],(maximums,flags,results);counts['init_fields']+=1
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':counts,'mode_original_instruction_bytes':sorted(coverage),'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Regular/BIST/dither helper calls and regular PDLconfigure explicitly stubbed identically; saturation/CPU/MRSS/delay execute independently sourced helpers.','Initialization4c84..4d8e is an instruction slice before mode/capture calls.','Synthetic MMIO/status changes, no physical delay or IRQ concurrency proof.']},indent=2)+'\n');print('PASS',counts)
