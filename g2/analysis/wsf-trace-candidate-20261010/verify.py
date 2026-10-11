from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert raw[0x52a674-0x438000:0x52a678-0x438000]==b'\n\0\0\0'
assert int.from_bytes(raw[0x52a678-0x438000:0x52a67c-0x438000],'little')==0x006df094
src=ROOT/'g2/components/main/wsf_trace_candidates_20261010/trace.c'
cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(HERE/'trace.o')]
subprocess.run(cmd,check=True);subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_smp_candidate_log_fallback',str(HERE/'trace.o'),'-o',str(HERE/'trace.elf')],check=True)
cmd4=cmd.copy();cmd4[2]='-mcpu=cortex-m4';cmd4[-1]=str(HERE/'trace-m4.o');subprocess.run(cmd4,check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_smp_candidate_log_fallback',str(HERE/'trace-m4.o'),'-o',str(HERE/'trace-m4.elf')],check=True)
with (HERE/'trace-m4.elf').open('rb') as f:
    e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_smp_candidate_log_fallback')

def run(original,format_word,args,formatted_len,printed_len):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    ctx=0x20001000
    u.mem_write(ctx,b''.join((a|1).to_bytes(4,'little') for a in [0x110e00,0x110e20,0x110e40]))
    stop=0x110f00;sp=0x20010000;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,stop|1)
    if original: values=[format_word,*args]
    else: values=[ctx,format_word,args[0],args[1]];u.mem_write(sp,args[2].to_bytes(4,'little'))
    for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],values):u.reg_write(reg,val)
    events=[];print_calls=0
    def readstr(addr):
        b=bytes(u.mem_read(addr,1025));return b.split(b'\0',1)[0]
    def hook(cpu,addr,size,_):
        nonlocal print_calls
        if addr==stop:cpu.emu_stop();return
        kind={0x473036:'format',0x110e00:'format',0x4733ee:'print',0x110e20:'print',0x569a44:'assert',0x110e40:'assert'}.get(addr)
        if kind is None:return
        r=[cpu.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
        if kind=='format':
            vals=[int.from_bytes(cpu.mem_read(r[2]+4*i,4),'little') for i in range(3)]
            events.append(('format',r[1],*vals))
            payload=b'A'*min(formatted_len,1023)+b'\0';cpu.mem_write(r[0],payload)
            out=formatted_len
        elif kind=='print':
            content=readstr(r[0]);events.append(('print',len(content),hashlib.sha256(content).hexdigest()))
            out=printed_len if print_calls==0 else len(content);print_calls+=1
        else:events.append(('assert',r[0],r[1]));out=0
        cpu.reg_write(UC_ARM_REG_R0,out);cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((0x52a63c if original else entry)|1,stop,count=150)
    assert u.reg_read(UC_ARM_REG_PC)==stop and u.reg_read(UC_ARM_REG_SP)==sp
    return events
count=0;branches=set()
for fmt,args,formatted_len,printed_len in itertools.product([0x78e6e4,0x537868],[(0,1,2),(0x74e984,255,0xffffffff)],[0,1,20,1023,1024,2048],[0,1,1023,1024,2048]):
    a=run(True,fmt,args,formatted_len,printed_len);b=run(False,fmt,args,formatted_len,printed_len)
    assert a==b,(fmt,args,formatted_len,printed_len,a,b)
    branches.add(any(x[0]=='assert' for x in a));count+=1
assert branches=={False,True}
receipt={'status':'PASS','comparisons':count,'original':'0x52a63c..0x52a672','raw_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'compile_command':cmd,'limits':['Formatter 0x473036, print 0x4733ee and WsfAssert 0x569a44 are explicit scripted provider boundaries.','Buffer contents and return lengths are synthetic; full formatting, output routing and assert behavior are not implemented.','Cortex-M55 compile and Cortex-M4 Unicorn comparison; no byte equality or device trace claim.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count}))
