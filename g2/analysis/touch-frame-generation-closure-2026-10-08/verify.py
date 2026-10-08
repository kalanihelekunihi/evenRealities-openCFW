from pathlib import Path
import sys,json,struct,itertools,hashlib
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;s=D.parent/'touch-slider-producer-closure-2026-10-08/verify.py';ns={'__file__':str(s)};exec(s.read_text().split('patterns=')[0],ns);counts={'mask':0,'divider':0,'sensor':0}
for mask,state,words in itertools.product([0,1,0x80000000,0xffffffff],range(16),[[0]*3,[0xffffffff]*3,[0xa5a5a5a5,0x55555555,0xff00ff00]]):
 vals=[]
 for native in [False,True]:
  u=ns['guest']();u.mem_write(0x20007000,struct.pack('<3I',*words));ns['call'](u,ns['symbols']['touch_frame_mask'] if native else 0x5188,[mask,state,0x20007000]);vals.append(u.mem_read(0x20007000,12).hex())
 assert vals[0]==vals[1];counts['mask']+=1
for method,clock,divider in itertools.product([0,1,2,10,255],[0,1,2,3,6,255],[0,1,3,4,24,65535]):
 vals=[]
 for native in [False,True]:u=ns['guest']();vals.append(ns['call'](u,ns['symbols']['touch_adjust_divider'] if native else 0x5528,[method,clock,divider]))
 assert vals[0]==vals[1],(method,clock,divider,vals);counts['divider']+=1
for typ,method,clock,divider,cdac_status,bypass in itertools.product([0,1,2],[1,2,10],range(4),[0,3,24,65535],[0,4],[0,1,2]):
 vals=[]
 for native in [False,True]:
  u=ns['guest']();u.mem_write(0x20002000+8,struct.pack('<III',0x20003500,0x20004000,0x20005000));u.mem_write(0x20002000+48,struct.pack('<II',0x20006000,0x20006100));u.mem_write(0x20006000,struct.pack('<4H',0,0,0,1));u.mem_write(0x20006100,struct.pack('<4H',0,7,0,8));u.mem_write(0x20003500,bytes(range(128)));u.mem_write(0x20004000+122,bytes([method]));u.mem_write(0x20004000+128,struct.pack('<H',1 if bypass==2 else 0));u.mem_write(0x20004000+132,b'\x02');u.mem_write(0x20004000+140,b'\x40');u.mem_write(0x20005000,b'\xa5'*60);u.mem_write(0x20005000+14,struct.pack('<H',divider));u.mem_write(0x20005000+33,bytes([clock]));u.mem_write(0x20005000+52,bytes([bool(bypass)]));u.mem_write(0x20007000,b'\x5a'*44);u.mem_write(0x20001000,b'\x70\x47');u.mem_write(0x20008000,struct.pack('<I',0x20001001));u.reg_write(UC_ARM_REG_R3,0x20002000);calls=[]
  def code(u,a,n,data):
   if a==(0x20001000 if native else 0x51bc):
    args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];calls.append(args);u.mem_write(args[1]+16,struct.pack('<I',0x12345678));u.reg_write(UC_ARM_REG_R0,cdac_status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(ns['UC_HOOK_CODE'],code);r=ns['call'](u,ns['symbols']['touch_generate_sensor'] if native else 0x5548,[typ,1,0x20007000]);vals.append((r,u.mem_read(0x20007000,44).hex(),calls))
 assert vals[0]==vals[1],(typ,method,clock,divider,cdac_status,bypass,vals);counts['sensor']+=1
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':counts,'elf_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'limits':['Mask/divider original and native leaf execution, no call stubs.','Sensor frame generator executes full body but CDAC51bc is explicitly stubbed with matched status/output on both sides.','Synthetic structures; no physical scan/frame/peripheral validation.']},indent=2)+'\n');print('PASS',counts)
