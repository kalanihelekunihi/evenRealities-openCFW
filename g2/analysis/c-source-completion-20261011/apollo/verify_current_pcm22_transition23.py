#!/usr/bin/env python3
"""Bounded stock/current-C selector cache-publication oracle."""
import hashlib, json, pathlib, struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as A

ROOT=pathlib.Path(__file__).resolve().parents[4]
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE=ROOT/'g2/components/bootloader/initializer_callbacks/pcm22_selector23_native/pcm22_sequence23.c'
ELF=pathlib.Path(__file__).parent/'boot-coplacement-msprirq-mod-proof-round/boot.elf'
OUT=pathlib.Path(__file__).with_name('boot-current-transition23-oracle.json')
ENTRY=0x429f68
blob=STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with ELF.open('rb') as f:
    elf=ELFFile(f)
    segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s.data()]
    sym=elf.get_section_by_name('.symtab')
    names={s.name:s['st_value'] for s in sym.iter_symbols()}
assert names['opencfw_spot_pcm22_transition23']

def w(cpu,addr,value): cpu.mem_write(addr,struct.pack('<I',value))

def run(stock,target,current,ton,timer_ready,poll_ready):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    for base,size in ((0,0x1000),(0x410000,0x30000),(0x600000,0x1000),
                      (0x20000000,0x40000),(0x40000000,0x300000)):
        cpu.mem_map(base,size)
    if stock: cpu.mem_write(0x410000,blob)
    else:
        for base,data in segs:
            if 0x410000<=base<0x440000: cpu.mem_write(base,data)
    profile=0x20026ba0
    for i in range(30): w(cpu,profile+4+4*i,(0x02440013+i*0x001a240b)&0xffffffff)
    w(cpu,profile+0x64,0x0a654321)
    w(cpu,0x400083e0,1 if timer_ready else 0)
    w(cpu,0x40008064,0x40000000 if poll_ready else 0)
    w(cpu,0x4002004c,0x5a000027)
    cpu.reg_write(A.UC_ARM_REG_R0,target);cpu.reg_write(A.UC_ARM_REG_R1,current)
    cpu.reg_write(A.UC_ARM_REG_R2,ton);cpu.reg_write(A.UC_ARM_REG_R3,0xdeadbeef)
    cpu.reg_write(A.UC_ARM_REG_SP,0x2003f000);cpu.reg_write(A.UC_ARM_REG_LR,0x600001)
    cpu.reg_write(A.UC_ARM_REG_XPSR,0x01000000)
    writes=[];delays=[];timers=[];ton_adjust=[];visited=set();done=[]
    delay=0x41d1c0 if stock else names['opencfw_hal_delay_us']&~1
    timer=0x42a04a if stock else names['opencfw_pcm22_timer_service']&~1
    adjust=0x42a1bc if stock else names['event_a_power_ton_adjust']&~1
    def code(c,pc,size,_):
        if pc==0x600000: done.append(True);c.emu_stop()
        elif pc==delay:
            value=c.reg_read(A.UC_ARM_REG_R0)
            delays.append(value)
            c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
        elif pc==timer:
            timers.append(True);c.reg_write(A.UC_ARM_REG_R0,0);c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
        elif pc==adjust:
            ton_adjust.append((c.reg_read(A.UC_ARM_REG_R0),c.reg_read(A.UC_ARM_REG_R1)))
            c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
        elif stock and ENTRY<=pc<0x42a030:visited.update(range(pc,pc+size))
    def write(c,access,addr,size,value,_):
        if addr in (0x200270c0,0x200270c4,0x200270b8,0x200270bc,0x200270b0,0x200270b4,0x4002004c):
            writes.append((addr,size,value&((1<<(size*8))-1)))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    start=ENTRY if stock else names['opencfw_spot_pcm22_transition23']&~1
    try: cpu.emu_start(start|1,0x600002,count=100000)
    except Exception as exc: raise RuntimeError((stock,hex(cpu.reg_read(A.UC_ARM_REG_PC)),str(exc))) from exc
    assert done
    return {'return':cpu.reg_read(A.UC_ARM_REG_R0),'writes':writes,'delays':delays,'timers':len(timers),'ton_adjust':ton_adjust},visited

cases=[];seen=set()
for target,current,ton in ((0,1,0x12345678),(5,3,0x20),(23,16,0xffffffff)):
    for timer in (False,True):
        for ready in (False,True):
            native,v=run(True,target,current,ton,timer,ready)
            source,_=run(False,target,current,ton,timer,ready)
            assert native==source,(target,current,ton,timer,ready,native,source)
            seen|=v;cases.append((target,current,ton,timer,ready))
out={'status':'PASS','stock_sha256':hashlib.sha256(blob).hexdigest(),
     'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
     'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),
     'cases':len(cases),'body_bytes':200,'visited_body_bytes':len(seen&set(range(ENTRY,ENTRY+200))),
     'unvisited_body_bytes':[hex(x) for x in sorted(set(range(ENTRY,ENTRY+200))-seen)],
     'scope':'Return, ordered state/MMIO writes, delay arguments and timer-service calls; synthetic RAM/MMIO and child cuts; no physical timer proof.'}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],out['cases'],out['visited_body_bytes'])
