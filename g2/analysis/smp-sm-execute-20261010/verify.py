from pathlib import Path
import hashlib, itertools, json, subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=ROOT/'g2/components/main/smp_sm_execute_candidates_20261010/execute.c'
tail=ROOT/'g2/components/main/smp_sm_dispatch_tail_20261010/dispatch_tail.c'
basecmd=['clang','--target=arm-none-eabi','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    for name,path in [('execute',src),('tail',tail)]:
        subprocess.run(basecmd[:2]+['-mcpu='+cpu]+basecmd[2:]+['-c',str(path),'-o',str(HERE/(name+suffix+'.o'))],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_smp_candidate_execute',str(HERE/('execute'+suffix+'.o')),str(HERE/('tail'+suffix+'.o')),'-o',str(HERE/('execute'+suffix+'.elf'))],check=True)
with (HERE/'execute-m4.elf').open('rb') as f:
    elf=ELFFile(f); segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']; entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_smp_candidate_execute')

SMP=0x20070aec; CCB=0x20002000; MSG=0x20002100; CTX=0x20001000; STOP=0x110f00; STACK=0x20010000
original_hooks={0x4b73c4:'role',0x4c9c50:'gate',0x44b610:'compare',0x43d0ce:'flags',0x56d454:'state',0x56d31e:'event',0x43d574:'log',0x52a63c:'trace'}
source_hooks={0x110e00+i*0x20+0x10:name for i,name in enumerate(['role','gate','compare','flags','state','event','log','trace'])}

def run(original, enabled_case, selected, gate_pattern, compare_result, flags, event, state, conn_id):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    for i,name in enumerate(['role','gate','compare','flags','state','event','log','trace']):u.mem_write(CTX+4*i,(0x110e00+i*0x20+0x11).to_bytes(4,'little'))
    if enabled_case==0:u.mem_write(SMP+248,b'\0')
    else:u.mem_write(SMP+248,b'\1')
    if enabled_case==2:u.mem_write(CCB+72,(0).to_bytes(4,'little'))
    else:u.mem_write(CCB+72,(0x20002200).to_bytes(4,'little'))
    u.mem_write(0x20002200,bytes([1 if enabled_case==3 else 0]))
    u.mem_write(CCB+61,bytes([conn_id,state]));u.mem_write(MSG+2,bytes([event]))
    group=0x20003000;rows=0x20004000;handlers=0x20005000;fallback=0x20006000;row=0x20007000
    u.mem_write(SMP+232,group.to_bytes(4,'little'))
    u.mem_write(group,rows.to_bytes(4,'little')+handlers.to_bytes(4,'little')+fallback.to_bytes(4,'little'))
    u.mem_write(rows+4*state,row.to_bytes(4,'little'))
    u.mem_write(row,bytes([event,17,1,0,0,0]))
    u.mem_write(fallback,b'\0'*12)
    u.mem_write(handlers+4,(0x110d01).to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,STACK);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.reg_write(UC_ARM_REG_R0,CCB if original else CTX)
    u.reg_write(UC_ARM_REG_R1,MSG if original else CCB)
    if not original:u.reg_write(UC_ARM_REG_R2,MSG)
    events=[];gates=0
    def hook(cpu,addr,size,_):
        nonlocal gates
        if addr==STOP:cpu.emu_stop();return
        name=(original_hooks if original else source_hooks).get(addr)
        if addr==0x110d00:name='action'
        if name is None:return
        r0=cpu.reg_read(UC_ARM_REG_R0);r1=cpu.reg_read(UC_ARM_REG_R1);r2=cpu.reg_read(UC_ARM_REG_R2);r3=cpu.reg_read(UC_ARM_REG_R3)
        value=0
        if name=='gate':
            gates+=1;value=gate_pattern[gates-1]
            events.append((name,value))
        elif name=='compare':
            value=compare_result
            events.append((name,r0,r1,r2,value))
        elif name=='flags':value=flags;events.append((name,value))
        elif name=='state':value=0x100+r0;events.append((name,r0,value))
        elif name=='event':value=0x200+r0;events.append((name,r0,value))
        elif name=='log':
            sp=cpu.reg_read(UC_ARM_REG_SP);extra=[int.from_bytes(cpu.mem_read(sp+4*i,4),'little') for i in range(4)]
            events.append((name,r0,r1,r2,r3,*extra))
        elif name=='trace':events.append((name,r0,r1,r2,r3))
        elif name=='role':events.append((name,r0));value=0
        elif name=='action':events.append((name,r0,r1))
        cpu.reg_write(UC_ARM_REG_R0,value)
        cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    try:u.emu_start((0x56ee62 if original else entry)|1,STOP,count=4000)
    except Exception as e:raise RuntimeError((original,enabled_case,selected,gate_pattern,compare_result,flags,hex(u.reg_read(UC_ARM_REG_PC)),events)) from e
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==STACK,(original,events,hex(u.reg_read(UC_ARM_REG_PC)),hex(u.reg_read(UC_ARM_REG_SP)))
    return events,bytes(u.mem_read(CCB,76)),bytes(u.mem_read(MSG,8))

count=0;shapes=set()
for enabled_case,selected,compare_result,flags,event,state,conn_id in itertools.product(range(4),range(6),[0,1],[0,2], [5,19],[0,2],[0,7]):
    pattern=[0]*5
    if selected<5:pattern[selected]=1
    a=run(True,enabled_case,selected,pattern,compare_result,flags,event,state,conn_id)
    b=run(False,enabled_case,selected,pattern,compare_result,flags,event,state,conn_id)
    assert a==b,(enabled_case,selected,compare_result,flags,event,state,conn_id,a,b)
    shapes.add(tuple(e[0] for e in a[0]));count+=1
receipt={'status':'PASS','comparisons':count,'call_shapes':len(shapes),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'entry':'0x56ee62','end':'0x56f144','limits':['Eight lower provider results and action callback scripted; logger formatting and protocol action bodies not established.','RAM transition/config tables synthetic; initialized device state not established.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count,'call_shapes':len(shapes)}))
