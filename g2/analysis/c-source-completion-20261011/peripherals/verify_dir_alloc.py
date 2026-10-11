#!/usr/bin/env python3
"""Bounded original-byte/compiled-C checks for LittleFS pair allocation."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

R = Path(__file__).resolve().parents[4]
D = Path(__file__).resolve().parent
S = R/'g2/components/audio/file_sync_candidate/dir_alloc.c'
O, E = D/'dir-alloc-m4.o', D/'dir-alloc-oracle.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(S),'-o',str(O)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=g2_lfs_alloc=0x101001',
                '--defsym=g2_lfs_bd_read=0x101011','-o',str(E),str(O)],check=True,stderr=subprocess.DEVNULL)
with E.open('rb') as f:
    elf=ELFFile(f)
    segs=[(x['p_vaddr'],x.data()) for x in elf.iter_segments() if x['p_type']=='PT_LOAD']
    sy={x.name:x['st_value'] for x in elf.get_section_by_name('.symtab').iter_symbols()}
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[0x20:]

def run(stock, cycle, rev, alloc_error, read_error):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    for a,n in ((0x438000,(len(B)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x100000)):
        u.mem_map(a,n)
    if stock:u.mem_write(0x438000,B)
    else:
        for a,d in segs:u.mem_write(a,d)
    def w(a,v):u.mem_write(a,int(v&0xffffffff).to_bytes(4,'little'))
    fs,cfg,dir,sp=0x20001000,0x20003000,0x20002000,0x200f0000
    w(fs+0x68,cfg);w(cfg+0x24,cycle)
    u.mem_write(dir,b'\xa5'*32)
    for reg,val in ((A.UC_ARM_REG_R0,fs),(A.UC_ARM_REG_R1,dir),
                    (A.UC_ARM_REG_SP,sp),(A.UC_ARM_REG_LR,0x101181)):
        u.reg_write(reg,val)
    events=[];done=[False]
    mapping={(0x4cb186 if stock else 0x101000):'alloc',
             (0x4ca83c if stock else 0x101010):'read'}
    def hook(cpu,pc,size,user):
        if pc==0x101180:done[0]=True;cpu.emu_stop();return
        if pc not in mapping:return
        kind=mapping[pc];events.append(kind)
        if kind=='alloc':
            result=alloc_error if len(events)==2 else 0
            if not result:w(cpu.reg_read(A.UC_ARM_REG_R1),10+len(events))
        else:
            result=read_error
            w(int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP)+8,4),'little'),rev)
        cpu.reg_write(A.UC_ARM_REG_R0,result&0xffffffff)
        cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((0x4cc502 if stock else sy['g2_lfs_dir_alloc'])|1,0,count=1000)
    assert done[0],(stock,events)
    return u.reg_read(A.UC_ARM_REG_R0),bytes(u.mem_read(dir,32)),events

n=0
for cycle in (0,1,2,3,10):
    for rev in (0,1,5,0x12345678):
        for ae,re in ((0,0),(0,-84),(0,-5),(-28,0)):
            a=run(True,cycle,rev,ae,re);b=run(False,cycle,rev,ae,re)
            assert a==b,(cycle,rev,ae,re,a,b)
            n+=1
print('PASS_DIR_ALLOC',n)
