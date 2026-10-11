from pathlib import Path
import hashlib,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STATE=0x20070be8;BUF=0x2006bd30;STOP=0x110f00;SP=0x20010000
results=[]
for fmt,a,b in [(0x77bf14,0x20003000,0x20003100),(0x765710,17,4)]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x110000,0x2000);u.mem_map(0x20000000,0x80000)
    u.mem_write(STATE,bytes([5]));u.mem_write(STATE+241,b'\1')
    u.mem_write(BUF,b'Z'*1040)
    u.mem_write(0x20003000,b'event\0');u.mem_write(0x20003100,b'state\0')
    u.mem_write(SP,(852).to_bytes(4,'little')+fmt.to_bytes(4,'little')+a.to_bytes(4,'little')+b.to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1)
    for reg,val in [(UC_ARM_REG_R0,1),(UC_ARM_REG_R1,0x56f148),(UC_ARM_REG_R2,0x6e1994),(UC_ARM_REG_R3,0x789060)]:u.reg_write(reg,val)
    calls=[];trace=[]
    hooks={0x43d416:'lock',0x43d438:'unlock',0x44aa80:'output'}
    def hook(cpu,addr,size,_):
        trace.append(addr)
        name=hooks.get(addr)
        if name:
            calls.append((name,cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1),cpu.reg_read(UC_ARM_REG_R2)))
            cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    try:u.emu_start(0x43d575,STOP,count=50000)
    except Exception as exc:raise RuntimeError((hex(fmt),hex(u.reg_read(UC_ARM_REG_PC)),calls,[hex(x) for x in trace[-20:]])) from exc
    results.append({'format':hex(fmt),'pc':hex(u.reg_read(UC_ARM_REG_PC)),'calls':calls,'buffer':bytes(u.mem_read(BUF,160)).split(b'\0')[0].decode('latin1'),'trace_tail':[hex(x) for x in trace[-15:]]})
(HERE/'original_probe.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
