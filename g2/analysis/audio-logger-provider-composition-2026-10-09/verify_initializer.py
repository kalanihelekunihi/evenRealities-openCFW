from pathlib import Path
import json,hashlib
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,b);u.mem_map(0x20000000,0x100000);u.mem_write(0x20004558,b'\xa5'*0x70af0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_R0,0x75d3cc)
stop=[]
def hook(uc,pc,size,user):
 if pc==0x5fa024 and uc.reg_read(UC_ARM_REG_R0)==0x75d3d8:stop.append('before-second-zero-range');uc.emu_stop()
u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x5fa01f,0,count=1000000)
assert stop and bytes(u.mem_read(0x20004558,0x70af0))==bytes(0x70af0)
out={'status':'PASS','cases':1,'raw_sha256':hashlib.sha256(b).hexdigest(),'handler':'0x5FA01E','table':'0x75D3CC','destination_start':'0x20004558','bytes_cleared':0x70af0,'destination_end_exclusive':hex(0x20004558+0x70af0),'callback_initial':int.from_bytes(u.mem_read(0x200742f0,4),'little'),'flag_initial':u.mem_read(0x20074f4e,1)[0],'limits':'Original first zero-fill record only; stop before next range. Other scatter handlers and application runtime not executed.'}
Path(__file__).with_name('initializer-results.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
