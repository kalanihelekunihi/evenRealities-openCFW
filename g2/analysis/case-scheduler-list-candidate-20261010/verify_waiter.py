from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
raw=fw[32:]
source=ROOT/'g2/components/case/scheduler_list_candidate_20261010/waiter.c'
obj=HERE/'waiter.o';linked=HERE/'waiter.elf'
subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og',
                '-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror',
                '-c',str(source),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','case_remove_waiter',str(obj),'-o',str(linked)],check=True)
with (HERE/'waiter.elf').open('rb') as f:
    elf=ELFFile(f)
    entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='case_remove_waiter')
    segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
SCHED=0x20000128;EVENT=0x20004000;DELAY=0x20004100
TASK=0x20007000;CURRENT=0x20007200;READY=0x20000ff4;PENDING=0x2000147c;STOP=0x20000000
def w(u,a,*values):u.mem_write(a,struct.pack('<'+'I'*len(values),*values))
def list_init(u,a,item=None):
    end=a+8
    w(u,a,0 if item is None else 1,end,0xffffffff,item or end,item or end)
    if item is not None:
        w(u,item+4,end,end)
        w(u,item+16,a)
def run(original,suspended,priority,current_priority,top_priority,initial_yield):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,raw)
    u.mem_map(0x100000,0x10000)
    for a,b in segments:u.mem_write(a,bytes(b))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\xa5'*0x10000)
    w(u,SCHED,CURRENT);w(u,SCHED+0x10,top_priority);w(u,SCHED+0x1c,initial_yield);w(u,SCHED+0x30,suspended)
    w(u,TASK+0x2c,priority);w(u,CURRENT+0x2c,current_priority)
    list_init(u,EVENT,TASK+0x18);list_init(u,DELAY,TASK+4)
    list_init(u,PENDING)
    for i in range(5):list_init(u,READY+i*20)
    w(u,TASK+0x18+12,TASK);w(u,TASK+4+12,TASK)
    u.reg_write(UC_ARM_REG_R0,EVENT);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.emu_start(0x0800cba1 if original else entry|1,STOP,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    return (u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(SCHED,0x40)),
            bytes(u.mem_read(READY,0x80)),bytes(u.mem_read(PENDING,0x20)),
            bytes(u.mem_read(EVENT,0x20)),bytes(u.mem_read(DELAY,0x20)),
            bytes(u.mem_read(TASK,0x40)),bytes(u.mem_read(CURRENT,0x40)),
            u.reg_read(UC_ARM_REG_PRIMASK))
cases=[]
for vals in itertools.product((0,1,2),(0,1,3,4),(0,1,3),(0,2,4),(0,1)):
    a=run(True,*vals);b=run(False,*vals)
    assert a==b,(vals,[i for i,(x,y) in enumerate(zip(a,b)) if x!=y])
    cases.append(vals)
def fatal(original):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,raw)
    u.mem_map(0x100000,0x10000)
    for a,b in segments:u.mem_write(a,bytes(b))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\0'*0x10000)
    list_init(u,EVENT,TASK+0x18);w(u,TASK+0x18+12,0)
    u.reg_write(UC_ARM_REG_R0,EVENT);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.emu_start(0x0800cba1 if original else entry|1,0,count=100)
    assert u.reg_read(UC_ARM_REG_PRIMASK)==1
    assert u.reg_read(UC_ARM_REG_PC)!=STOP
    assert struct.unpack('<I',u.mem_read(EVENT,4))[0]==1
fatal(True);fatal(False)
receipt={'status':'PASS','cases':len(cases),'firmware_sha256':hashlib.sha256(fw).hexdigest(),
         'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'domains':{'suspended':[0,1,2],'task_priority':[0,1,3,4],'current_priority':[0,1,3],
                    'top_ready_priority_seed':[0,2,4],'yield_seed':[0,1]},
         'fatal_null_owner':'Both original and source disable IRQ and remain nonreturning at 100-instruction bound.',
         'limits':['Coherent synthetic lists and TCBs; no production scheduler state.','Fatal paths have bounded stop assertions, not a return comparison.','No allocation/lifetime or interrupt scheduling proof.']}
(HERE/'waiter_results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(cases)}))
