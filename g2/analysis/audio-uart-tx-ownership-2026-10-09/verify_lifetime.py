import verify as v
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib
rows=[]
for mode in ['fifo-partial','queue-partial','queue-complete']:
 phases=[]
 for native in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,v.raw);u.mem_map(0x100000,0x10000)
  for a,b in v.sections:u.mem_write(a,b)
  u.mem_map(0x20000000,0x100000);u.mem_map(0x40039000,0x1000)
  def w(a,x):u.mem_write(a,struct.pack('<I',x))
  w(v.STATE,0x1ea9e06);u.mem_write(v.SRC,b'abcde');cap=8 if mode=='queue-complete' else 2;u.mem_write(v.STATE+0x34,struct.pack('<6I',0,0,0,cap,1,v.QBUF));u.mem_write(v.TX,struct.pack('<13I',v.SRC,5,0,0,0,0,0,*([0]*6))+bytes([2,0,0,0]));u.mem_write(v.STATE+0xdc,bytes([mode!='fifo-partial']));w(0x40039018,0 if mode=='fifo-partial' else 0x20);fifo=[];remaining=[2 if mode=='fifo-partial' else 0];done=[]
  def memhook(uc,access,a,size,value,user):
   if a==0x40039000:
    fifo.append(value&255);remaining[0]-=1
    if remaining[0]==0:w(0x40039018,0x20)
  def hook(uc,pc,size,user):
   if pc==0x10ff00:done.append(True);uc.emu_stop();return
   if native:assert 0x100000<=pc<0x101000,hex(pc)
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,memhook)
  def invoke(name):
   done.clear();u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);u.reg_write(UC_ARM_REG_R0,v.STATE);u.reg_write(UC_ARM_REG_R1,v.TX);u.emu_start((v.syms[name] if native else v.bind[name])|1,0,count=10000);assert done
  invoke('nonblocking_write');phase1={'written':int.from_bytes(u.mem_read(v.STATE+0xd8,4),'little'),'writing':u.mem_read(v.STATE+0x119,1)[0],'queue_length':int.from_bytes(u.mem_read(v.STATE+0x3c,4),'little'),'fifo':list(fifo)}
  u.mem_write(v.SRC,b'ZZZZZ');remaining[0]=1000;w(0x40039018,0);invoke('nonblocking_write_sm');invoke('nonblocking_write_sm');end={'written':int.from_bytes(u.mem_read(v.STATE+0xd8,4),'little'),'writing':u.mem_read(v.STATE+0x119,1)[0],'queue_length':int.from_bytes(u.mem_read(v.STATE+0x3c,4),'little'),'fifo':list(fifo)}
  # Partial queue capacity2 requires one additional refill/drain to consume fifth byte.
  if end['writing']:invoke('nonblocking_write_sm');end={'written':int.from_bytes(u.mem_read(v.STATE+0xd8,4),'little'),'writing':u.mem_read(v.STATE+0x119,1)[0],'queue_length':int.from_bytes(u.mem_read(v.STATE+0x3c,4),'little'),'fifo':list(fifo)}
  assert end['writing']==0 and end['written']==5
  assert end['fifo']==(list(b'abcde') if mode=='queue-complete' else list(b'abZZZ'))
  phases.append({'after_first_return':phase1,'after_mutation_and_service':end})
 assert phases[0]==phases[1];rows.append({'mode':mode,**phases[0]})
(v.D/'lifetime-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(v.elf.read_bytes()).hexdigest(),'comparisons':rows,'limits':'Deliberate source mutation between manually scheduled calls, synthetic FIFO availability; illustrates borrow/copy contract, not a proved live firmware misuse or race.'},indent=2)+'\n');print('PASS',len(rows))
