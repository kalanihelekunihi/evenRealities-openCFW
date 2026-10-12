#!/usr/bin/env python3
"""Bounded stock/current-C scheduler bootstrap call and state oracle."""
import hashlib,json,pathlib,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=pathlib.Path(__file__).resolve().parents[4]
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE=ROOT/'g2/components/bootloader/thread_creation/scheduler_bootstrap.c'
ELF=pathlib.Path(__file__).with_name('scheduler_bootstrap_m33.elf')
OUT=pathlib.Path(__file__).with_name('boot-scheduler-bootstrap-oracle.json')
blob=BLOB.read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with ELF.open('rb') as f:
    e=ELFFile(f)
    segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD' and s.data()]
    names={s.name:s['st_value'] for sec in e.iter_sections() if sec.header.sh_type=='SHT_SYMTAB' for s in sec.iter_symbols()}
stock_child={'idle':0x41b5d0,'static':0x417c7c,'timer':0x419240,'mask':0x41b2f8,'port':0x41b4f6}
source_child={'static':names['opencfw_bl_kernel_static_thread']&~1,
              'timer':names['opencfw_bl_timer_service_start']&~1,
              'mask':names['opencfw_bl_mask_interrupts']&~1,
              'port':names['opencfw_bl_port_start']&~1}

def put(cpu,addr,value):cpu.mem_write(addr,struct.pack('<I',value&0xffffffff))
def read(cpu,addr):return struct.unpack('<I',cpu.mem_read(addr,4))[0]

def run(stock,static_result,timer_result):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    for base,size in ((0x410000,0x30000),(0x500000,0x10000),(0x600000,0x1000),(0x20000000,0x30000)):
        cpu.mem_map(base,size)
    if stock:cpu.mem_write(0x410000,blob)
    else:
        for base,data in segs:
            if 0x500000<=base<0x510000:cpu.mem_write(base,data)
    put(cpu,0x200004c8,0x12345678)
    cpu.reg_write(A.UC_ARM_REG_SP,0x2002f000);cpu.reg_write(A.UC_ARM_REG_LR,0x600001)
    cpu.reg_write(A.UC_ARM_REG_XPSR,0x01000000)
    calls=[];done=[];visited=set()
    byaddr={v:k for k,v in (stock_child if stock else source_child).items()}
    def hook(c,pc,size,_):
        if pc==0x600000:done.append(True);c.emu_stop()
        elif pc in byaddr:
            label=byaddr[pc];calls.append(label)
            if label=='idle':
                put(c,c.reg_read(A.UC_ARM_REG_R0),0x20026970)
                put(c,c.reg_read(A.UC_ARM_REG_R1),0x200250d0)
                put(c,c.reg_read(A.UC_ARM_REG_R2),256)
            c.reg_write(A.UC_ARM_REG_R0,static_result if label=='static' else timer_result if label=='timer' else 0)
            c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
        elif stock and 0x418148<=pc<0x4181d8:visited.update(range(pc,pc+size))
    cpu.hook_add(UC_HOOK_CODE,hook)
    start=0x418148 if stock else names['opencfw_bl_kernel_start']&~1
    cpu.emu_start(start|1,0x600002,count=10000)
    assert done
    state=[read(cpu,a) for a in (0x20027168,0x20027164,0x20027150,0x20027148)]
    return (cpu.reg_read(A.UC_ARM_REG_R0),state,[x for x in calls if x!='idle']),visited

cases=[];visited=set()
for static_result,timer_result in ((0,0),(0x200269e0,0),(0x200269e0,1),(0x200269e0,2)):
    original,seen=run(True,static_result,timer_result)
    candidate,_=run(False,static_result,timer_result)
    assert original==candidate,(static_result,timer_result,original,candidate)
    cases.append((static_result,timer_result));visited|=seen
out={'status':'PASS','stock_sha256':hashlib.sha256(blob).hexdigest(),
     'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
     'isolated_elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),
     'cases':cases,'body_bytes':144,'visited_body_bytes':len(visited&set(range(0x418148,0x4181d8))),
     'unvisited_body_bytes':[hex(x) for x in sorted(set(range(0x418148,0x4181d8))-visited)],
     'limits':['Fatal timer result UINT32_MAX is structurally checked but not executed.',
               'Child calls are controlled cuts; no RTOS scheduler or hardware execution proof.']}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],len(cases),out['visited_body_bytes'])
