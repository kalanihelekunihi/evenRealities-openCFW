from pathlib import Path
import hashlib,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_IPSR
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STOP=0x110f00;CB=0x110d00;S=0x20070be8
cases=[
    ('interrupt',1,1,5,0,0,0,0),
    ('logger_disabled',0,0,5,0,0,0,0),
    ('global_level',0,1,5,4,0,0,0),
    ('module_level',0,1,5,5,4,0,0),
    ('module_filter',0,1,5,5,5,0,0),
    ('fatal_callback',0,0,6,0,0,0,1),
    ('fatal_missing',0,0,6,0,0,0,0),
]
out=[]
for name,ipsr,active,level,global_limit,policy_limit,compare_result,callback in cases:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x110000,0x2000);u.mem_map(0x20000000,0x80000)
    u.mem_write(S+241,bytes([active]));u.mem_write(S,bytes([global_limit]))
    u.mem_write(0x2007456c,(CB+1 if callback else 0).to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,0x20010000)
    u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.reg_write(UC_ARM_REG_R0,level)
    u.reg_write(UC_ARM_REG_R1,0x20002000)
    u.reg_write(UC_ARM_REG_R2,0x20002100)
    u.reg_write(UC_ARM_REG_R3,0x20002200)
    u.reg_write(UC_ARM_REG_IPSR,ipsr)
    events=[]
    def hook(cpu,addr,size,_):
        if addr==STOP:events.append(('return',));cpu.emu_stop();return
        if addr==CB:
            events.append(('fatal_callback',cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1),cpu.reg_read(UC_ARM_REG_R2)))
            cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR));return
        if addr==0x43d4b0:
            events.append(('policy',cpu.reg_read(UC_ARM_REG_R0)))
            cpu.reg_write(UC_ARM_REG_R0,policy_limit);cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR));return
        if addr==0x44b63a:
            events.append(('compare',cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1)))
            cpu.reg_write(UC_ARM_REG_R0,compare_result);cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR));return
        if addr==0x44b0ae:
            events.append(('fatal_loop',));cpu.emu_stop();return
        if addr==0x43d416:events.append(('lock_enter',));cpu.emu_stop();return
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(0x43d575,STOP,count=1000)
    if u.reg_read(UC_ARM_REG_PC)==STOP:events.append(('return',))
    out.append({'case':name,'events':events,'final_pc':hex(u.reg_read(UC_ARM_REG_PC))})
assert [x['events'][-1][0] for x in out]==['return','return','return','return','return','return','fatal_loop']
assert out[5]['events'][0][0]=='fatal_callback'
(HERE/'logger_frontier.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(out),'outcomes':[x['events'][-1][0] for x in out]}))
