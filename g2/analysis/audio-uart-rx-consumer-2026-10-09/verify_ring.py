import verify as v
from unicorn import *
from unicorn.arm_const import *
import struct,json,itertools,hashlib
STATE=0x20040000;BUF=0x20041000;SRC=0x20042000;bind={'uart3_ring_full':0x598146,'uart3_ring_put':0x598198,'uart3_ring_write':0x5981c4}
def run(name,f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,v.raw);u.mem_map(0x100000,0x10000)
 for a,b in v.sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_write(STATE,struct.pack('<4I',BUF,63,f['read'],f['write']));u.mem_write(BUF,bytes(range(64)));u.mem_write(SRC,bytes((i*13+5)&255 for i in range(205)));u.reg_write(UC_ARM_REG_R0,STATE);u.reg_write(UC_ARM_REG_R1,0xa3 if name=='uart3_ring_put' else SRC);u.reg_write(UC_ARM_REG_R2,f.get('n',0));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);stop=[]
 def hook(uc,pc,size,user):
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  if native:assert 0x100000<=pc<0x104000,hex(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PC,(v.syms[name] if native else bind[name])|1)
 for _ in range(20000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stop
 return {'return':u.reg_read(UC_ARM_REG_R0) if name=='uart3_ring_full' else None,'state':bytes(u.mem_read(STATE,16)).hex(),'storage':bytes(u.mem_read(BUF,64)).hex()}
rows=[]
for name,r,w,n in itertools.product(bind,[0,1,63],[0,1,62,63],[0,1,3,64,65,205]):
 f={'read':r,'write':w,'n':n};a=run(name,f,False);b=run(name,f,True);assert a==b,(name,f,a,b);rows.append({'function':name,'fixture':f,'observed':a})
(v.D/'ring-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(v.elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(v.raw).hexdigest(),'comparisons':rows,'limits':'Original and reconstructed ring instruction behavior in valid mask63 fixtures; no atomicity, UART arrival rate or hardware loss claim.'},indent=2)+'\n');print('RING PASS',len(rows))
