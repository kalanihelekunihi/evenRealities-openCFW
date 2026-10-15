#!/usr/bin/env python3
"""Bounded original/source TLSF free-list transition oracle."""
from pathlib import Path
import subprocess
import hashlib
import json
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A

R=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parent
S=R/'g2/components/audio/file_pool_free_candidate'
E=D/'tlsf-free-lists-oracle.elf'
objects=[]
for stem in ('tlsf_free_lists','tlsf_align'):
    obj=D/f'{stem}-free-lists-m4.o'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror',
                    '-c',str(S/f'{stem}.c'),'-o',str(obj)],check=True)
    objects.append(obj)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',
                '--defsym=g2_file_close_error=0x101001','-o',str(E),
                *map(str,objects)],check=True)
with E.open('rb') as f:
    e=ELFFile(f)
    seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD']
    sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]
def run(stock,op,head_case,empty_after,fl,sl):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):
        u.mem_map(a,n)
    if stock:u.mem_write(0x438000,B)
    else:
        for a,d in seg:u.mem_write(a,d)
    pool=0x20010000;block=0x20012000;other=0x20013000
    head=pool+0x74+fl*128+sl*4
    def w(a,v):u.mem_write(a,v.to_bytes(4,'little'))
    def rd(a):return int.from_bytes(u.mem_read(a,4),'little')
    w(0x78f4c0,8)
    w(pool+16,0x10 if op=='insert' else 0x10|(1<<fl))
    w(pool+20+fl*4,0x20 if op=='insert' else 0x20|(1<<sl))
    if op=='insert':
        w(head,pool);w(pool+12,pool)
    else:
        prev=pool if head_case else other
        nxt=pool if empty_after else other
        w(block+12,prev);w(block+8,nxt)
        w(prev+8,block);w(nxt+12,block)
        w(head,block if head_case else other)
    for reg,v in ((A.UC_ARM_REG_R0,pool),(A.UC_ARM_REG_R1,block),
                  (A.UC_ARM_REG_R2,fl),(A.UC_ARM_REG_R3,sl),
                  (A.UC_ARM_REG_SP,0x200f0000),(A.UC_ARM_REG_LR,0x101101)):
        u.reg_write(reg,v)
    done=[False]
    def hook(cpu,pc,sz,user):
        if pc==0x101100:done[0]=True;cpu.emu_stop()
        if pc==0x101000:raise AssertionError('assertion path')
    u.hook_add(UC_HOOK_CODE,hook)
    address=((0x4d00d0 if op=='insert' else 0x4d003a) if stock else
             sy['g2_tlsf_'+('insert' if op=='insert' else 'remove')+'_free_block'])
    u.emu_start(address|1,0,count=300)
    assert done[0],(stock,op)
    return tuple(rd(a) for a in (head,pool+16,pool+20+fl*4,block+8,block+12,pool+8,pool+12,other+8,other+12))
rows=[]
for op in ('insert','remove'):
    for hc in (False,True):
        for empty in (False,True):
            for fl,sl in ((0,0),(2,7),(8,31)):
                if op=='insert' and (hc or empty):continue
                a=run(True,op,hc,empty,fl,sl);b=run(False,op,hc,empty,fl,sl)
                assert a==b,(op,hc,empty,fl,sl,a,b)
                rows.append((op,hc,empty,fl,sl))
receipt={'status':'PASS_TLSF_FREE_LISTS','cases':len(rows),
         'source_sha256':{stem:hashlib.sha256((S/f'{stem}.c').read_bytes()).hexdigest()
                          for stem in ('tlsf_free_lists','tlsf_align')},
         'limits':'Bounded valid insert/remove transitions; malformed allocator states excluded.'}
(D/'tlsf-free-lists-results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(rows))
