from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-scan-watchdog-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split("counts={'watchdog'")[0],ns);g=ns['ns'];rows=[]
for status,fifo,completion,kind in itertools.product([0,1,4,8],[0,1,100,65535],[0,2,1000],[2,6]):
 results=[]
 for native in [False,True]:
  u=ns['guest']();u.mem_write(0x20002000+16,struct.pack('<I',0x20005000));u.mem_write(0x20002000+40,struct.pack('<I',0x20006000));u.mem_write(0x20004000+122,bytes([1,kind]));u.mem_write(0x20006000,struct.pack('<7I',0x11,0x22,0x33,0xffffffff,0x55667788,0x00170000,0x99));u.mem_write(0x40003200,struct.pack('<I',fifo|0xabcd0000));u.mem_write(0x40000000,struct.pack('<I',0x12345678));u.mem_write(0x20001000,b'\x70\x47');u.mem_write(0x20008000,struct.pack('<I',0x20001001 if native else 0x20002000));state={'polls':0,'cleared':False};bus=[];calls=[]
  def code(u,a,n,data):
   if a==(0x20001000 if native else 0x6ac0):
    calls.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def read(u,access,a,n,v,user):
   if 0x40000000<=a<0x40004000:bus.append(['read',a-0x40000000,n])
   if a==0x40000100:
    # Pre-start acknowledgment read is outside completion polling.
    if u.reg_read(UC_ARM_REG_PC) in [0x69a4] or (native and state.get('armed',False)):
     u.mem_write(a,struct.pack('<I',0x100 if state['polls']>=completion else 0));state['polls']+=1
  def write(u,access,a,n,v,user):
   if 0x40000000<=a<0x40004000:bus.append(['write',a-0x40000000,n,v])
   if a==0x40003800:state['armed']=True
   if a==0x40000100 and state.get('armed',False):state['armed']=False
  u.hook_add(g['UC_HOOK_CODE'],code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
  for reg,value in [(UC_ARM_REG_R0,0x20007000),(UC_ARM_REG_R1,0),(UC_ARM_REG_R2,0),(UC_ARM_REG_R3,0x20002000 if native else 0),(UC_ARM_REG_SP,0x20008000),(UC_ARM_REG_LR,0x20000001)]:u.reg_write(reg,value)
  u.emu_start((g['symbols']['touch_execute_saturated'] if native else 0x7bc0)|1,0x20000000,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000
  results.append((u.reg_read(UC_ARM_REG_R0),u.mem_read(0x20007000,4).hex(),bus,calls))
 assert results[0]==results[1],(status,fifo,completion,kind,results);rows.append({'state_switch_status':status,'fifo':fifo,'completion_after':completion,'widget_type':kind,'status':results[0][0],'maximum_le':results[0][1],'bus':results[0][2]})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['State-switch6ac0 is explicitly stubbed; synthetic MMIO completion and FIFO.','Full original7bc0 non-type7 body versus native helpers; no retained executable calls in native module.','Physical ADC, mode lifecycle and IRQ concurrency unverified.']},indent=2)+'\n');print('PASS',len(rows))
