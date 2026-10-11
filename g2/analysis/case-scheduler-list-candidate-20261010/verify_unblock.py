#!/usr/bin/env python3
"""Coherent original/source CASE event waiter unblock comparison."""
from pathlib import Path
import argparse,hashlib,itertools,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[2]
F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';fw=F.read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
p=argparse.ArgumentParser();p.add_argument('--archive-objects',action='store_true');a=p.parse_args()
S=R/'g2/components/case/scheduler_list_candidate_20261010/unblock.c'
if a.archive_objects:
    B=R/'g2/components/case/source_candidate_20261010/build'
    objs=[B/f'scheduler_list_candidate_20261010__{x}.c.o' for x in ('waiter','unblock')]
    archive=json.loads((R/'g2/analysis/case-source-candidate-round2-20261010/receipt.json').read_text())['archive_sha256']
else:
    objs=[];archive=None
    for name in ('waiter','unblock'):
        src=R/f'g2/components/case/scheduler_list_candidate_20261010/{name}.c';obj=H/f'{name}.unblock.o'
        subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
        objs.append(obj)
elfpath=H/'unblock.elf'
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','case_unblock_waiter',*[str(x) for x in objs],'-o',str(elfpath)],check=True)
with elfpath.open('rb') as f:
    e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='case_unblock_waiter')
    seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
SCHED=0x20000128;EVENT=0x20004000;DELAY=0x20004100;TASK=0x20007000;CUR=0x20007200;READY=0x20000ff4;STOP=0x20000000
def w(u,x,*v):u.mem_write(x,struct.pack('<'+'I'*len(v),*v))
def lst(u,x,item=None):
    end=x+8;w(u,x,0 if item is None else 1,end,0xffffffff,item or end,item or end)
    if item is not None:w(u,item+4,end,end);w(u,item+16,x)
def setup(priority,current,top,yield_seed,suspended,bits,owner=True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:])
    u.mem_map(0x100000,0x10000)
    for x,b in seg:u.mem_write(x,bytes(b))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\xa5'*0x10000)
    w(u,SCHED,CUR);w(u,SCHED+0x10,top);w(u,SCHED+0x1c,yield_seed);w(u,SCHED+0x30,suspended)
    w(u,TASK+0x2c,priority);w(u,CUR+0x2c,current)
    lst(u,EVENT,TASK+24);lst(u,DELAY,TASK+4)
    for i in range(5):lst(u,READY+i*20)
    w(u,TASK+24+12,TASK if owner else 0);w(u,TASK+4+12,TASK);w(u,TASK+24,bits)
    u.reg_write(UC_ARM_REG_R0,TASK+24);u.reg_write(UC_ARM_REG_R1,bits)
    u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    return u
def run(original,vals):
    u=setup(*vals);u.emu_start(0x0800c1cd if original else entry|1,STOP,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    return (bytes(u.mem_read(SCHED,0x40)),bytes(u.mem_read(EVENT,0x20)),bytes(u.mem_read(DELAY,0x20)),
            bytes(u.mem_read(READY,0x70)),bytes(u.mem_read(TASK,0x40)),u.reg_read(UC_ARM_REG_PRIMASK))
cases=[]
for vals in itertools.product((0,1,3,4),(0,1,3),(0,2,4),(0,1),(1,2),(0,8,0x2000000,0xFFFFFFFF)):
    v=(*vals,True);x=run(True,v);y=run(False,v)
    assert x==y,(vals,[i for i,(q,z) in enumerate(zip(x,y)) if q!=z]);cases.append(vals)
def fatal(suspended,owner):
    for original in (True,False):
        u=setup(2,1,0,0,suspended,8,owner)
        u.emu_start(0x0800c1cd if original else entry|1,0,count=100)
        assert u.reg_read(UC_ARM_REG_PRIMASK)==1 and u.reg_read(UC_ARM_REG_PC)!=STOP
fatal(0,True);fatal(1,False)
rec={'status':'PASS','cases':len(cases),'firmware_sha256':hashlib.sha256(fw).hexdigest(),
     'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),
     'object_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in objs},'archive_sha256':archive,
     'fatal':'Unsuspended scheduler and null owner mask IRQ and remain nonreturning at 100 instructions.',
     'limits':['Synthetic coherent TCB/list state, not production ownership.','No actual task switch or hardware execution.']}
(H/('unblock_archive_results.json' if a.archive_objects else 'unblock_results.json')).write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(cases)}))
