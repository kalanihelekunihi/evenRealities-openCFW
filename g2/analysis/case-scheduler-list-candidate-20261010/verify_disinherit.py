#!/usr/bin/env python3
"""Compare original mutex disinherit with isolated or CASE-archive C objects."""
from pathlib import Path
import argparse,hashlib,itertools,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
FW=ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin'
fw=FW.read_bytes();assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
raw=fw[32:]
SRC=ROOT/'g2/components/case/scheduler_list_candidate_20261010/disinherit.c'
ap=argparse.ArgumentParser();ap.add_argument('--archive-objects',action='store_true');args=ap.parse_args()
if args.archive_objects:
    build=ROOT/'g2/components/case/source_candidate_20261010/build'
    objects=[build/'scheduler_list_candidate_20261010__waiter.c.o',build/'scheduler_list_candidate_20261010__disinherit.c.o']
    receipt=json.loads((ROOT/'g2/analysis/case-source-candidate-round2-20261010/receipt.json').read_text())
    archive_sha=receipt['archive_sha256']
else:
    objects=[];archive_sha=None
    for name in ('waiter','disinherit'):
        src=ROOT/f'g2/components/case/scheduler_list_candidate_20261010/{name}.c'
        obj=HERE/f'{name}.disinherit.o';objects.append(obj)
        subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og',
                        '-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror',
                        '-c',str(src),'-o',str(obj)],check=True)
linked=HERE/'disinherit.elf'
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','case_disinherit',*[str(x) for x in objects],'-o',str(linked)],check=True)
with linked.open('rb') as f:
    elf=ELFFile(f)
    entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='case_disinherit')
    segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']

SCHED=0x20000128;READY=0x20000ff4;TASK=0x20007000;OTHER=0x20007200;STOP=0x20000000
def w(u,a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
def lst(u,a,item=None):
    end=a+8;w(u,a,0 if item is None else 1,end,0xffffffff,item or end,item or end)
    if item is not None:w(u,item+4,end,end);w(u,item+16,a)
def fixture(original,holder,priority,base,held,top,event_value):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,raw)
    u.mem_map(0x100000,0x10000)
    for a,b in segments:u.mem_write(a,bytes(b))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\xa5'*0x10000)
    w(u,SCHED,TASK);w(u,SCHED+0x10,top)
    for i in range(5):lst(u,READY+i*20,TASK+4 if i==priority else None)
    w(u,TASK+0x2c,priority);w(u,TASK+0x4c,base);w(u,TASK+0x50,held)
    w(u,TASK+0x18,event_value)
    u.reg_write(UC_ARM_REG_R0,holder);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.emu_start(0x0800cb39 if original else entry|1,STOP,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    return (u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(SCHED,0x40)),
            bytes(u.mem_read(READY,0x70)),bytes(u.mem_read(TASK,0x60)),u.reg_read(UC_ARM_REG_PRIMASK))
cases=[]
for vals in itertools.product((0,TASK),(0,1,2,4),(0,1,2,4),(1,2,3),(0,2,4),(0x11,0x38)):
    # All list items and priorities are coherent; null-holder still has a live current TCB.
    a=fixture(True,*vals);b=fixture(False,*vals)
    assert a==b,(vals,[i for i,(x,y) in enumerate(zip(a,b)) if x!=y])
    cases.append(vals)
def fatal(holder,held):
    for original in (True,False):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
        u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,raw)
        u.mem_map(0x100000,0x10000)
        for a,b in segments:u.mem_write(a,bytes(b))
        u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\0'*0x10000)
        w(u,SCHED,TASK);w(u,TASK+0x50,held)
        u.reg_write(UC_ARM_REG_R0,holder);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
        u.emu_start(0x0800cb39 if original else entry|1,0,count=100)
        assert u.reg_read(UC_ARM_REG_PRIMASK)==1 and u.reg_read(UC_ARM_REG_PC)!=STOP
fatal(OTHER,1);fatal(TASK,0)
receipt={'status':'PASS','cases':len(cases),'firmware_sha256':hashlib.sha256(fw).hexdigest(),
         'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
         'object_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in objects},
         'archive_sha256':archive_sha,'fatal':'Wrong holder and zero held count both IRQ-mask and remain nonreturning at 100 instructions.',
         'limits':['Coherent synthetic TCB/list state; no live mutex ownership proof.','No production scheduling or hardware claim.']}
name='disinherit_archive_results.json' if args.archive_objects else 'disinherit_results.json'
(HERE/name).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(cases)}))
