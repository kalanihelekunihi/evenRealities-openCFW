"""Bounded stock assertion-path entry observations; never infer return."""
import hashlib,json
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CB=0x110d00; STOP=0x110f00; CELL=0x2007456c
def run(kind,callback):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x110000,0x2000);u.mem_map(0x20000000,0x80000)
    u.mem_write(CELL,(CB|1 if callback else 0).to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.reg_write(UC_ARM_REG_R0,0 if kind=='null_module' else 6)
    u.reg_write(UC_ARM_REG_R1,0 if kind=='level_six' else 0)
    events=[]
    def hook(cpu,addr,size,_):
        if addr==CB:
            events.append(('callback',cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1),cpu.reg_read(UC_ARM_REG_R2)))
            cpu.emu_stop()
        elif addr==0x44b0ae:
            events.append(('fatal_loop',));cpu.emu_stop()
        elif addr==STOP:
            events.append(('return',));cpu.emu_stop()
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((0x43d4b0 if kind=='null_module' else 0x43d574)|1,STOP,count=10000)
    return {'kind':kind,'callback_installed':callback,'events':events,'stop_pc':hex(u.reg_read(UC_ARM_REG_PC))}
out=[run(kind,callback) for kind in ('null_module','level_six') for callback in (0,1)]
assert [r['events'][0][0] for r in out]==['fatal_loop','callback','fatal_loop','callback']
assert out[1]['events'][0][-1]==481 and out[3]['events'][0][-1]==572
result={'status':'PASS','image_sha256':hashlib.sha256(raw).hexdigest(),
        'cases':out,'limit':'Callback-present path stops at callback entry; its return behavior and target installation are not established. Missing callback stops at first fatal-loop call.'}
(HERE/'fatal_probe.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(out),'outcomes':[r['events'][0][0] for r in out]}))
