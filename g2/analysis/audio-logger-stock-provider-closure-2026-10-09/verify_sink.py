from pathlib import Path
import json,hashlib
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;R=D.parents[2];raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
def machine():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x100000);u.mem_map(0x100000,0x1000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x100001);return u
rows=[];u=machine();cut=[]
def init_hook(uc,pc,size,user):
 if pc==0x57deea:cut.append({'boundary':hex(pc),'r0':uc.reg_read(UC_ARM_REG_R0),'r1':uc.reg_read(UC_ARM_REG_R1)});uc.emu_stop()
u.hook_add(UC_HOOK_CODE,init_hook);u.emu_start(0x54171d,0,count=1000)
assert cut and int.from_bytes(u.mem_read(0x200742f0,4),'little')==0x5415c3
assert int.from_bytes(u.mem_read(0x20000d2c+0x1c+0x14,4),'little')==0x5415e7
rows.append({'kind':'init-prefix','sink_pointer':'0x5415C3','channel1_callback':'0x5415E7','cut':cut})
for text in [b'',b'abc',b'log\n',b'A'*205]:
 for active in [0,1]:
  u=machine();u.mem_write(0x20040000,text+b'\0');u.reg_write(UC_ARM_REG_R0,0x20040000);u.mem_write(0x20000d2c+0x1c+0x18,bytes([active]));u.mem_write(0x20000d2c+0x1c+4,(0x20050000).to_bytes(4,'little'));cut=[]
  def sink_hook(uc,pc,size,user):
   if pc==0x58e3f8:
    p=uc.reg_read(UC_ARM_REG_R1);desc=bytes(uc.mem_read(p,56));assert int.from_bytes(desc[:4],'little')==0x20040000 and int.from_bytes(desc[4:8],'little')==len(text) and desc[8:]==bytes(48)
    assert uc.reg_read(UC_ARM_REG_R0)==0x20050000
    cut.append({'boundary':hex(pc),'handle':hex(uc.reg_read(UC_ARM_REG_R0)),'descriptor_hex':desc.hex()});uc.emu_stop()
   elif pc==0x100000:cut.append({'boundary':'return','result':uc.reg_read(UC_ARM_REG_R0)});uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,sink_hook);u.emu_start(0x5415c3,0,count=10000)
  assert cut and (cut[0]['boundary']=='0x58e3f8')==bool(active)
  rows.append({'kind':'sink-to-driver-boundary','text_hex':text.hex(),'channel_active':active,'cut':cut})
(D/'sink-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'raw_sha256':hashlib.sha256(raw).hexdigest(),'comparisons':rows,'limits':'Original setter, registration callback, strlen, memset and UART wrapper instructions executed. Initialization stops before allocator57DEEA; active TX stops before HAL58E3F8. No physical UART, TX completion or driver ownership claim.'},indent=2)+'\n');print('PASS',len(rows))
