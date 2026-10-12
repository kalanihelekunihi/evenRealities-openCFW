#!/usr/bin/env python3
"""Stock/current-C queue reset with controlled RTOS lower calls."""
import hashlib,json,pathlib,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=pathlib.Path(__file__).resolve().parents[4]
BLOB=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE=ROOT/'g2/components/bootloader/thread_creation/timer_service.c'
RESET_SOURCE=ROOT/'g2/components/bootloader/thread_creation/queue_reset.c'
ELF=pathlib.Path(__file__).with_name('timer_queue_fresh_m33.elf')
OUT=pathlib.Path(__file__).with_name('boot-timer-queue-fresh-composed-oracle.json')
blob=BLOB.read_bytes(); assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
with ELF.open('rb') as f:
    e=ELFFile(f)
    segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD' and s.data()]
    names={s.name:s['st_value'] for sec in e.iter_sections() if sec.header.sh_type=='SHT_SYMTAB' for s in sec.iter_symbols()}
stock_lowers={'enter':0x41b3e4,'exit':0x41b3fc,'remove':0x41872c,'reschedule':0x41b3d0,'init':0x41b53c}
source_lowers={'enter':names['opencfw_bl_kernel_enter']&~1,'exit':names['opencfw_bl_kernel_exit']&~1,
               'remove':names['opencfw_bl_remove_event_waiter']&~1,
               'reschedule':names['opencfw_bl_kernel_reschedule']&~1,
               'init':names['opencfw_boot_list_initialize']&~1}

def run(stock,count,item_size,storage,queue_type):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    for base,size in ((0x410000,0x30000),(0x500000,0x10000),(0x600000,0x1000),(0x20000000,0x30000)):
        cpu.mem_map(base,size)
    if stock:cpu.mem_write(0x410000,blob)
    else:
        for base,data in segs:
            if 0x500000<=base<0x510000:cpu.mem_write(base,data)
    q=bytearray(0x80)
    cpu.mem_write(0x20010000,bytes(q))
    cpu.reg_write(A.UC_ARM_REG_R0,count);cpu.reg_write(A.UC_ARM_REG_R1,item_size)
    cpu.reg_write(A.UC_ARM_REG_R2,storage);cpu.reg_write(A.UC_ARM_REG_R3,0x20010000)
    cpu.reg_write(A.UC_ARM_REG_SP,0x2002f000);cpu.reg_write(A.UC_ARM_REG_LR,0x600001)
    cpu.mem_write(0x2002f000,struct.pack('<I',queue_type))
    cpu.reg_write(A.UC_ARM_REG_XPSR,0x01000000)
    calls=[];visited=set();done=[]
    lower=stock_lowers if stock else source_lowers
    byaddr={v:k for k,v in lower.items()}
    def hook(c,pc,size,_):
        if pc==0x600000:done.append(True);c.emu_stop()
        elif pc in byaddr:
            label=byaddr[pc]
            calls.append((label,c.reg_read(A.UC_ARM_REG_R0) if label in ('remove','init') else None))
            c.reg_write(A.UC_ARM_REG_R0,0)
            c.reg_write(A.UC_ARM_REG_PC,c.reg_read(A.UC_ARM_REG_LR))
        elif stock and (0x419be8<=pc<0x419c9c or 0x419c9c<=pc<0x419cfa or 0x419d68<=pc<0x419d8a):visited.update(range(pc,pc+size))
    cpu.hook_add(UC_HOOK_CODE,hook)
    start=0x419c9c if stock else names['opencfw_boot_timer_queue_fresh']&~1
    try: cpu.emu_start(start|1,0x600002,count=10000)
    except Exception as exc: raise RuntimeError((stock,hex(cpu.reg_read(A.UC_ARM_REG_PC)),str(exc))) from exc
    assert done
    return (cpu.reg_read(A.UC_ARM_REG_R0),bytes(cpu.mem_read(0x20010000,0x80)),calls),visited

cases=[];visited=set()
for count,item_size,storage,queue_type in ((3,4,0x20018000,5),(50,16,0x20018000,0),(1,0,0,2)):
    native,seen=run(True,count,item_size,storage,queue_type)
    source,_=run(False,count,item_size,storage,queue_type)
    assert native==source,(count,item_size,storage,queue_type,native[0],source[0],native[2],source[2],[(i,native[1][i],source[1][i]) for i in range(0x80) if native[1][i]!=source[1][i]][:8])
    cases.append((count,item_size,storage,queue_type));visited|=seen
out={'status':'PASS','stock_sha256':hashlib.sha256(blob).hexdigest(),
     'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
     'reset_source_sha256':hashlib.sha256(RESET_SOURCE.read_bytes()).hexdigest(),
     'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),
     'cases':cases,'reset_catalogue_body_bytes':180,
     'visited_reset_catalogue_bytes':len(visited&set(range(0x419be8,0x419c9c))),
     'limits':['Count is nonzero as required by stock UDIV; zero-count fault behavior not modeled.',
               'RTOS children are typed controlled cuts; scheduler runtime and fatal paths unqualified.']}
OUT.write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],len(cases),out['visited_reset_catalogue_bytes'])
