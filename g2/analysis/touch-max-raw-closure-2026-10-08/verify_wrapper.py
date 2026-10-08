from pathlib import Path
import sys,json,struct,itertools
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-slider-producer-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('patterns=')[0],ns);rows=[]
for value,status,flags in itertools.product([0,1,65535,65536,0xffffffff],[0,4,8],[0,1,8,15]):
 outputs=[]
 for native in [False,True]:
  u=ns['guest']();u.mem_write(0x20002000+12,struct.pack('<I',0x20004000));u.mem_write(0x20004000,struct.pack('<I',0x20005000));u.mem_write(0x20004000+128,struct.pack('<H',7));u.mem_write(0x20005000+35,bytes([flags]));u.mem_write(0x20005000+4,struct.pack('<H',123));u.mem_write(0x20001000,b'\x70\x47');calls=[]
  def hook(u,a,n,data):
   if a==(0x20001000 if native else 0x7bc0):
    arg=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];arg.append(struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0]);calls.append(arg[1:]);u.mem_write(arg[0],struct.pack('<I',value));u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(ns['UC_HOOK_CODE'],hook);r=ns['call'](u,ns['symbols']['touch_max_raw_init'] if native else 0x5cac,[0,0x20002000,0x20001001]);outputs.append((r,u.mem_read(0x20005000,60).hex(),calls))
 assert outputs[0]==outputs[1],(value,status,flags,outputs);rows.append({'scan_value':value,'scan_status':status,'flags':flags,'result':outputs[0]})
(D/'wrapper-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'comparisons':rows,'external_boundary':'ExecuteSaturatedScan7bc0 explicitly stubbed with identical injected outputs/status on both guests. No analog/hardware validation.'},indent=2)+'\n');print('PASS',len(rows),'wrapper cases')
