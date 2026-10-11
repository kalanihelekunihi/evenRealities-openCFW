from pathlib import Path
import argparse,hashlib,itertools,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--archive-objects',action='store_true');args=parser.parse_args()
fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
raw=fw[32:]
srcdir=ROOT/'g2/components/case/scheduler_list_candidate_20261010'
inputs=[srcdir/'waiter.c',srcdir/'resume.c',ROOT/'g2/components/case/source_candidate_20261010/critical_providers.c',ROOT/'g2/components/case/source_candidate_20261010/yield_request.c']
objects=[]
if args.archive_objects:
    build=ROOT/'g2/components/case/source_candidate_20261010/build'
    objects=[build/name for name in ('scheduler_list_candidate_20261010__waiter.c.o',
                                     'scheduler_list_candidate_20261010__resume.c.o',
                                     'source_candidate_20261010__critical_providers.c.o',
                                     'source_candidate_20261010__yield_request.c.o')]
else:
    for source in inputs:
        obj=HERE/(source.stem+'.resume.o');objects.append(obj)
        subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
elfpath=HERE/'resume.elf'
subprocess.run(['arm-none-eabi-ld','-T',str(HERE/'resume_link.ld'),*[str(x) for x in objects],'-o',str(elfpath)],check=True)
with elfpath.open('rb') as f:
    elf=ELFFile(f)
    segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
    symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    entry=symbols['case_resume_scheduler']
S=0x20000128;PEND=0x2000147c;READY=0x20000ff4;DELAY=0x20003000;OVER=0x20003100
CURRENT=0x20006000;TASKS=[0x20007000,0x20007100];EXTRA=0x20007300;STOP=0x20000000
def w(u,a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
def init_list(u,a,items):
    end=a+8;w(u,a,len(items),end,0xffffffff,items[0] if items else end,items[-1] if items else end)
    for i,item in enumerate(items):w(u,item+4,items[i+1] if i+1<len(items) else end,items[i-1] if i else end);w(u,item+16,a)
def run(original,suspended,task_count,pending_count,ticks,yield_seed,task_priority,current_priority,depth,extra_delayed):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,raw)
    u.mem_map(0x100000,0x10000)
    for a,b in segments:u.mem_write(a,bytes(b))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\0'*0x10000)
    u.mem_map(0xe000e000,0x1000)
    w(u,S,CURRENT if task_count else 0);w(u,S+8,task_count);w(u,S+0x10,0);w(u,S+0x18,ticks);w(u,S+0x1c,yield_seed)
    w(u,S+0x28,100 if pending_count else 1000 if extra_delayed else 0xffffffff)
    w(u,S+0x30,suspended);w(u,S+0x34,DELAY);w(u,S+0x38,OVER)
    w(u,S+0xc,7);w(u,S+0x20,0);w(u,CURRENT+0x2c,current_priority)
    w(u,0x2000019c,depth)
    for i in range(5):init_list(u,READY+i*20,[])
    init_list(u,OVER,[])
    pending_items=[TASKS[i]+0x18 for i in range(pending_count)]
    delayed_items=[TASKS[i]+4 for i in range(pending_count)]+([EXTRA+4] if extra_delayed else [])
    init_list(u,PEND,pending_items);init_list(u,DELAY,delayed_items)
    for i in range(pending_count):
        w(u,TASKS[i]+0x18+12,TASKS[i]);w(u,TASKS[i]+4+12,TASKS[i]);w(u,TASKS[i]+0x2c,task_priority if i==0 else 2)
        w(u,TASKS[i]+4,100+i)
    if extra_delayed:w(u,EXTRA+4+12,EXTRA);w(u,EXTRA+4,1000);w(u,EXTRA+0x2c,0)
    u.reg_write(UC_ARM_REG_PRIMASK,1 if depth else 0)
    u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    events={'tick':0,'next_unblock':0,'yield':0}
    expected={'tick':0x0800ca78,'next_unblock':0x0800b260 if original else symbols['case_reset_next_unblock']&~1,
              'yield':0x0800c0a0 if original else symbols['case_yield_request']&~1}
    def hook(u,a,n,data):
        for kind,address in expected.items():
            if a==address:events[kind]+=1
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(0x0800cc0d if original else entry|1,STOP,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    return (u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(S,0x60)),bytes(u.mem_read(0x2000019c,4)),
            bytes(u.mem_read(PEND,0x30)),bytes(u.mem_read(DELAY,0x40)),bytes(u.mem_read(OVER,0x20)),
            bytes(u.mem_read(READY,0x80)),bytes(u.mem_read(TASKS[0],0x140)),bytes(u.mem_read(EXTRA,0x40)),
            bytes(u.mem_read(CURRENT,0x40)),bytes(u.mem_read(0xe000ed04,4)),u.reg_read(UC_ARM_REG_PRIMASK),events)
cases=[]
coverage={'tick':0,'next_unblock':0,'yield':0}
for vals in itertools.product((1,2),(0,1,2,3,4),(0,1,2),(0,1,2),(0,1),(0,1,3),(0,2),(0,1),(0,1)):
    suspended,task_count,pending_count,ticks,yield_seed,task_priority,current_priority,depth,extra_delayed=vals
    if task_count==0:
        if pending_count!=0 or extra_delayed:continue
    elif task_count < 1+pending_count+extra_delayed:continue
    a=run(True,*vals);b=run(False,*vals)
    assert a[:-1]==b[:-1],(vals,[i for i,(x,y) in enumerate(zip(a,b)) if x!=y])
    assert a[-1]['tick']==b[-1]['tick'] and a[-1]['yield']==b[-1]['yield'],(vals,a[-1],b[-1])
    for kind in coverage:coverage[kind]+=a[-1][kind]
    cases.append(vals)
assert all(coverage.values()),coverage
def fatal(original):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,raw)
    u.mem_map(0x100000,0x10000)
    for a,b in segments:u.mem_write(a,bytes(b))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\0'*0x10000)
    u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.emu_start(0x0800cc0d if original else entry|1,0,count=100)
    assert u.reg_read(UC_ARM_REG_PRIMASK)==1 and u.reg_read(UC_ARM_REG_PC)!=STOP
fatal(True);fatal(False)
receipt={'status':'PASS','cases':len(cases),'firmware_sha256':hashlib.sha256(fw).hexdigest(),
         'source_sha256':hashlib.sha256((srcdir/'resume.c').read_bytes()).hexdigest(),
         'object_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in objects},
         'archive_sha256':hashlib.sha256((ROOT/'g2/components/case/source_candidate_20261010/build/libcase_source_candidate.a').read_bytes()).hexdigest() if args.archive_objects else None,
         'lower_tick':'Original 0x0800ca78 called by both; source body retains explicit case_increment_tick import.',
         'domains':{'suspended':[1,2],'task_count':[0,1,2,3,4],'pending_ready_items':[0,1,2],
                    'pending_ticks':[0,1,2],'yield_seed':[0,1],'task_priority':[0,1,3],
                    'current_priority':[0,2],'critical_depth':[0,1],'extra_delayed':[0,1]},
         'branch_events':coverage,'fatal_zero_suspend':'Both versions IRQ-mask and remain nonreturning at 100-instruction bound.',
         'limits':['Synthetic coherent list/TCB state; original tick is lower peer.','No production scheduler or task-lifetime proof.']}
(HERE/('resume_archive_results.json' if args.archive_objects else 'resume_results.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(cases)}))
