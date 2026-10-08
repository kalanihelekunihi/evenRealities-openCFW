from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-slider-producer-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('patterns=')[0],ns);rows=[]
for kind,count,output,analog,irq in itertools.product(['electrodes','shields','cmod'],[0,1,3],[0,1],[0,1],[0,1]):
 vals=[]
 for native in [False,True]:
  u=ns['guest']();u.mem_map(0x40020000,0x1000);u.mem_map(0x40040000,0x1000);u.mem_write(0x40020000,b'\xa5'*0x1000);u.mem_write(0x40040000,b'\x5a'*0x1000);u.mem_write(0x20002000,struct.pack('<I',0x20003000));u.mem_write(0x20002000+20,struct.pack('<II',0x20006000,0x20006000));u.mem_write(0x20003000+8,struct.pack('<I',0x20003100));u.mem_write(0x20003000+12,struct.pack('<H',count));u.mem_write(0x20003000+44,bytes([count]));u.mem_write(0x20003100+8,struct.pack('<IB3xIB3x',0x40040000,2,0x40040100,7));u.mem_write(0x20006000,b''.join(struct.pack('<IB3x',0x40040000+(j%2)*256,j) for j in range(3)));bus=[];u.reg_write(UC_ARM_REG_PRIMASK,irq)
  def read(u,access,a,n,v,data):
   if 0x40020000<=a<0x40041000:bus.append(['read',a,n,u.reg_read(UC_ARM_REG_PRIMASK)])
  def write(u,access,a,n,v,data):
   if 0x40020000<=a<0x40041000:bus.append(['write',a,n,v,u.reg_read(UC_ARM_REG_PRIMASK)])
  u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
  if kind=='electrodes':u.reg_write(UC_ARM_REG_R3,analog);u.mem_write(0x20008000,struct.pack('<I',0x20002000));args=[9,0,output];pc=0x6078
  else:u.reg_write(UC_ARM_REG_R3,0x20002000);args=[9,0,analog];pc=0x60ea if kind=='shields' else 0x6044
  name={'electrodes':'touch_config_electrodes','shields':'touch_config_shields','cmod':'touch_config_cmod'}[kind];ns['call'](u,ns['symbols'][name] if native else pc,args);vals.append((bus,u.mem_read(0x40020000,0x1000).hex(),u.mem_read(0x40040000,0x1000).hex(),u.reg_read(UC_ARM_REG_PRIMASK)))
 assert vals[0]==vals[1],(kind,count,output,analog,irq,vals);rows.append({'kind':kind,'count':count,'output':output,'analog':analog,'primask':irq,'bus':vals[0][0]})
(D/'wrapper-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'scope':'Complete original/native electrode/shield/CMOD wrappers and actual pin/critical helpers; synthetic GPIO/HSIOM; no function stubs'},indent=2)+'\n');print('PASS',len(rows))
