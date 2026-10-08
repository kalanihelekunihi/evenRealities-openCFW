from pathlib import Path
import json,hashlib,struct
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0xe000e000,0x2000);u.mem_write(0x20074ab0,struct.pack('<I',0x20006000));boundary=[]
def hook(u,a,n,d):
 if a==0x454820:
  args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]+list(struct.unpack('<III',u.mem_read(u.reg_read(UC_ARM_REG_SP),12)));boundary.append(dict(entry=hex(a),arguments=[hex(v) for v in args]));u.emu_stop()
u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(0x47e675,0x2007f000,count=30000);assert len(boundary)==1 and int(boundary[0]['arguments'][0],16)==0x47e879 and int(boundary[0]['arguments'][4],16)==54
(D/'creation-boundary-results.json').write_text(json.dumps(dict(status='PASS_CREATION_ENTRY_BOUNDARY',original_only_cases=1,boundary=boundary,limits=['Actual constructor and memory-provider instructions execute with already-created timer queue handle; stops before static task creation first instruction.','Proves task entry pointer and priority arguments, not successful creation, task population, context switch or live precedence.']),indent=2)+'\n');print(boundary)
