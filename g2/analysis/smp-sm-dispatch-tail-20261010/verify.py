from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert int.from_bytes(raw[0x56f154-0x438000:0x56f158-0x438000],'little')==0x20070aec
src=ROOT/'g2/components/main/smp_sm_dispatch_tail_20261010/dispatch_tail.c'
cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(HERE/'dispatch_tail.o')]
subprocess.run(cmd,check=True);subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_smp_candidate_dispatch_tail',str(HERE/'dispatch_tail.o'),'-o',str(HERE/'dispatch_tail.elf')],check=True)
cmd4=cmd.copy();cmd4[2]='-mcpu=cortex-m4';cmd4[-1]=str(HERE/'dispatch_tail-m4.o');subprocess.run(cmd4,check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_smp_candidate_dispatch_tail',str(HERE/'dispatch_tail-m4.o'),'-o',str(HERE/'dispatch_tail-m4.elf')],check=True)
with (HERE/'dispatch_tail-m4.elf').open('rb') as f:
    e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_smp_candidate_dispatch_tail')
base=0x20070aec;ccb=0x20002000;msg=0x20002100;ctx=0x20001000;stop=0x110f00

def run(original,role,state,event,variant):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    u.mem_write(ctx,(0x110e01).to_bytes(4,'little'))
    u.mem_write(ccb+61,bytes([7,state]));u.mem_write(msg+2,bytes([event]))
    for group_index in range(2):
        g=0x20003000+group_index*0x100;rows=0x20004000+group_index*0x100;handlers=0x20005000+group_index*0x100;fallback=0x20006000+group_index*0x100
        u.mem_write(base+228+4*group_index,g.to_bytes(4,'little'))
        u.mem_write(g,rows.to_bytes(4,'little')+handlers.to_bytes(4,'little')+fallback.to_bytes(4,'little'))
        for s in range(3):
            row=0x20007000+group_index*0x300+s*0x40
            u.mem_write(rows+4*s,row.to_bytes(4,'little'))
            first=5 if variant==0 else 9
            u.mem_write(row,bytes([first,1+s,1,11,2+s,2,0,0,0]))
        u.mem_write(fallback,bytes([22,3,3,33,4,4,44,5,5,55,6,6,0]))
        for h in range(7):u.mem_write(handlers+4*h,(0x110e40+2*h+1).to_bytes(4,'little'))
    initial=bytes(u.mem_read(ccb,76))+bytes(u.mem_read(msg,8))
    events=[];trace=[];s0=0x20010000
    if original:
        u.reg_write(UC_ARM_REG_SP,s0-40);u.mem_write(s0-20,(0).to_bytes(4,'little')*4+(stop|1).to_bytes(4,'little'))
        for reg,val in [(UC_ARM_REG_R4,ccb),(UC_ARM_REG_R5,msg),(UC_ARM_REG_R6,base),(UC_ARM_REG_R7,0)]:u.reg_write(reg,val)
    else:
        u.reg_write(UC_ARM_REG_SP,s0);u.reg_write(UC_ARM_REG_LR,stop|1)
        for reg,val in [(UC_ARM_REG_R0,ctx),(UC_ARM_REG_R1,ccb),(UC_ARM_REG_R2,msg)]:u.reg_write(reg,val)
    def hook(cpu,addr,size,_):
        trace.append((addr,cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1)))
        if addr==stop:cpu.emu_stop();return
        if addr in (0x4b73c4,0x110e00):
            events.append(('role',cpu.reg_read(UC_ARM_REG_R0)));cpu.reg_write(UC_ARM_REG_R0,role);cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR));return
        if 0x110e40<=addr<0x110e50 and addr%2==0:
            events.append(('handler',(addr-0x110e40)//2,cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1)))
            cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    try:u.emu_start((0x56f0ec if original else entry)|1,stop,count=600)
    except Exception as exc:raise RuntimeError((original,role,state,event,variant,hex(u.reg_read(UC_ARM_REG_PC)),[hex(x) for x,_,_ in trace[-20:]],events)) from exc
    assert u.reg_read(UC_ARM_REG_PC)==stop and u.reg_read(UC_ARM_REG_SP)==s0,(original,role,state,event,variant,hex(u.reg_read(UC_ARM_REG_PC)),hex(u.reg_read(UC_ARM_REG_SP)),[(hex(x),hex(y),hex(z)) for x,y,z in trace[-25:]],events)
    after=bytes(u.mem_read(ccb,76))+bytes(u.mem_read(msg,8))
    return after,events,initial
count=0;shapes=set()
for role,state,event,variant in itertools.product([0,1,2],[0,1,2],[0,5,9,11,22,33,44,55,99],[0,1]):
    a=run(True,role,state,event,variant);b=run(False,role,state,event,variant)
    assert a==b,(role,state,event,variant,a,b)
    shapes.add(tuple(e[0] for e in a[1]));count+=1
receipt={'status':'PASS','comparisons':count,'call_shapes':len(shapes),'original_tail':'0x56f0ec..0x56f144','raw_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'compile_command':cmd,'limits':['Tail entered with original saved-register/stack frame; preceding logging path not executed.','Role provider and indirect action callbacks are scripted; initialized transition tables and action side effects not established.','Only this 88-byte tail subcontract, not complete 738-byte smpSmExecute.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count,'call_shapes':len(shapes)}))
