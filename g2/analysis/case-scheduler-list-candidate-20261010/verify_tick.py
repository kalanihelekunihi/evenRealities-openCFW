from pathlib import Path
import argparse,hashlib,itertools,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--archive-objects',action='store_true');args=parser.parse_args()
fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
raw=fw[32:];srcdir=ROOT/'g2/components/case/scheduler_list_candidate_20261010'
if args.archive_objects:
    build=ROOT/'g2/components/case/source_candidate_20261010/build'
    objects=[build/n for n in ('scheduler_list_candidate_20261010__waiter.c.o',
                               'scheduler_list_candidate_20261010__resume.c.o',
                               'scheduler_list_candidate_20261010__tick.c.o',
                               'source_candidate_20261010__critical_providers.c.o',
                               'source_candidate_20261010__yield_request.c.o')]
else:
    sources=[srcdir/n for n in ('waiter.c','resume.c','tick.c')]+[ROOT/'g2/components/case/source_candidate_20261010'/n for n in ('critical_providers.c','yield_request.c')]
    objects=[]
    for src in sources:
        obj=HERE/(src.stem+'.tick.o');objects.append(obj)
        subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
elfpath=HERE/'tick.elf'
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[str(x) for x in objects],'-o',str(elfpath)],check=True)
with elfpath.open('rb') as f:
    elf=ELFFile(f)
    segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
    entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='case_increment_tick')
S=0x20000128;READY=0x20000ff4;ACTIVE=0x20003000;OVER=0x20003100;EVENT=0x20004000
CURRENT=0x20006000;EXTRA=0x20006200;TASKS=[0x20007000,0x20007100];STOP=0x20000000
def w(u,a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
def init_list(u,a,items):
    end=a+8;w(u,a,len(items),end,0xffffffff,items[0] if items else end,items[-1] if items else end)
    for i,item in enumerate(items):w(u,item+4,items[i+1] if i+1<len(items) else end,items[i-1] if i else end);w(u,item+16,a)
def run(original,initial_tick,active_deadlines,overflow_deadlines,event_linked,priority,current_priority,extra_ready,yield_seed,suspended,pended_ticks):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,raw)
    u.mem_map(0x100000,0x10000)
    for a,b in segments:u.mem_write(a,bytes(b))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\0'*0x10000)
    w(u,S,CURRENT);w(u,S+8,1+len(active_deadlines)+len(overflow_deadlines)+extra_ready)
    w(u,S+0xc,initial_tick);w(u,S+0x10,current_priority)
    w(u,S+0x18,pended_ticks);w(u,S+0x1c,yield_seed);w(u,S+0x28,active_deadlines[0] if active_deadlines else 0xffffffff)
    w(u,S+0x30,suspended);w(u,S+0x34,ACTIVE);w(u,S+0x38,OVER)
    w(u,CURRENT+0x2c,current_priority);w(u,EXTRA+0x2c,current_priority)
    for i in range(5):init_list(u,READY+i*20,([CURRENT+4,EXTRA+4] if extra_ready else [CURRENT+4]) if i==current_priority else [])
    w(u,CURRENT+4+12,CURRENT);w(u,EXTRA+4+12,EXTRA)
    active_items=[TASKS[i]+4 for i in range(len(active_deadlines))]
    overflow_items=[TASKS[len(active_deadlines)+i]+4 for i in range(len(overflow_deadlines))]
    init_list(u,ACTIVE,active_items);init_list(u,OVER,overflow_items)
    event_items=[TASKS[i]+0x18 for i in range(len(active_deadlines)+len(overflow_deadlines))] if event_linked else []
    init_list(u,EVENT,event_items)
    for i,deadline in enumerate((*active_deadlines,*overflow_deadlines)):
        task=TASKS[i];w(u,task+4,deadline);w(u,task+4+12,task);w(u,task+0x18+12,task);w(u,task+0x2c,priority if i==0 else 2)
    u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.emu_start(0x0800ca79 if original else entry|1,STOP,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    return (u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(S,0x60)),bytes(u.mem_read(READY,0x80)),
            bytes(u.mem_read(ACTIVE,0x40)),bytes(u.mem_read(OVER,0x40)),bytes(u.mem_read(EVENT,0x30)),
            bytes(u.mem_read(CURRENT,0x40)),bytes(u.mem_read(EXTRA,0x40)),
            bytes(u.mem_read(TASKS[0],0x140)),u.reg_read(UC_ARM_REG_PRIMASK))
cases=[]
def compare(case):
    a=run(True,*case);b=run(False,*case)
    assert a==b,(case,[i for i,(x,y) in enumerate(zip(a,b)) if x!=y])
    cases.append(case)
for deadlines,event,priority,current,extra,yield_seed in itertools.product(((),(8,),(10,),(8,10),(8,8)),(0,1),(0,2,4),(0,2),(0,1),(0,1)):
    compare((7,deadlines,(),event,priority,current,extra,yield_seed,0,0))
for over,event,priority,current,extra,yield_seed in itertools.product(((),(0,),(1,)),(0,1),(0,2),(0,2),(0,1),(0,1)):
    compare((0xffffffff,(),over,event,priority,current,extra,yield_seed,0,0))
for suspended,pended,initial,deadline in itertools.product((1,2),(0,2),(7,0xffffffff),((),(8,))):
    compare((initial,deadline,(),1,2,0,0,1,suspended,pended))
def fatal_wrap(original):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,raw)
    u.mem_map(0x100000,0x10000)
    for a,b in segments:u.mem_write(a,bytes(b))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\0'*0x10000)
    w(u,S+0xc,0xffffffff);w(u,S+0x34,ACTIVE);init_list(u,ACTIVE,[TASKS[0]+4])
    u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.emu_start(0x0800ca79 if original else entry|1,0,count=100)
    assert u.reg_read(UC_ARM_REG_PRIMASK)==1 and u.reg_read(UC_ARM_REG_PC)!=STOP
fatal_wrap(True);fatal_wrap(False)
receipt={'status':'PASS','cases':len(cases),'firmware_sha256':hashlib.sha256(fw).hexdigest(),
         'source_sha256':hashlib.sha256((srcdir/'tick.c').read_bytes()).hexdigest(),
         'object_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in objects},
         'archive_sha256':hashlib.sha256((ROOT/'g2/components/case/source_candidate_20261010/build/libcase_source_candidate.a').read_bytes()).hexdigest() if args.archive_objects else None,
         'families':['running normal delayed wake','tick wrap/overflow delayed swap','scheduler-suspended pending tick'],
         'fatal_wrap_active':'Both versions IRQ-mask and remain nonreturning at 100-instruction bound.',
         'limits':['Synthetic coherent list/TCB state; no production scheduler or allocation proof.','No actual interrupt-driven tick cadence or hardware scheduling claim.']}
(HERE/('tick_archive_results.json' if args.archive_objects else 'tick_results.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(cases)}))
