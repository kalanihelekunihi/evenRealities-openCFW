from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=ROOT/'g2/components/main/extended_log_postformat_candidates_20261010/postformat.c'
append=ROOT/'g2/components/main/extended_log_append_candidates_20261010/append.c'
base=['clang','--target=arm-none-eabi','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    for name,path in [('postformat',src),('append',append)]:subprocess.run(base[:2]+['-mcpu='+cpu]+base[2:]+['-c',str(path),'-o',str(HERE/(name+suffix+'.o'))],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_postformat',str(HERE/('postformat'+suffix+'.o')),str(HERE/('append'+suffix+'.o')),'-o',str(HERE/('postformat'+suffix+'.elf'))],check=True)
with (HERE/'postformat-m4.elf').open('rb') as f:
    elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_log_candidate_postformat')
STATE=0x20070be8;BUF=0x2006bd30;CTX=0x20001000;STOP=0x110f00;SP=0x20010000;FMT=0x20003000;ARGS=0x20004000
def run(original,level,offset,fmt_result,filter_on,filter_result,suffix_on):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    u.mem_write(CTX,b''.join((0x110d00+0x20*i+1).to_bytes(4,'little') for i in range(4)))
    u.mem_write(STATE+32,bytes([ord('Z') if filter_on else 0])+b'\0')
    u.mem_write(STATE+245,bytes([suffix_on]))
    u.mem_write(BUF,b'Z'*1040)
    u.mem_write(FMT,b'%s\0')
    u.mem_write(ARGS,(0x12345678).to_bytes(4,'little'))
    if original:
        frame=SP-72;u.reg_write(UC_ARM_REG_SP,frame)
        u.mem_write(frame+76,FMT.to_bytes(4,'little'));u.mem_write(frame+4,ARGS.to_bytes(4,'little'))
        u.reg_write(UC_ARM_REG_R4,offset);u.reg_write(UC_ARM_REG_R5,level)
        u.reg_write(UC_ARM_REG_R8,STATE);u.reg_write(UC_ARM_REG_R10,1)
    else:
        u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1)
        u.reg_write(UC_ARM_REG_R0,CTX);u.reg_write(UC_ARM_REG_R1,level)
        u.reg_write(UC_ARM_REG_R2,offset);u.reg_write(UC_ARM_REG_R3,FMT)
        u.mem_write(SP,ARGS.to_bytes(4,'little'))
    events=[];stop=0x43d970 if original else STOP
    hook_names={0x44b76c:'format',0x44b63a:'filter',0x44aa80:'output',0x43d438:'unlock',0x110d00:'format',0x110d20:'filter',0x110d40:'output',0x110d60:'unlock'}
    def hook(cpu,addr,size,_):
        if addr==stop:cpu.emu_stop();return
        name=hook_names.get(addr)
        if name is None:return
        if name=='format':
            events.append((name,*[cpu.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]))
            cpu.reg_write(UC_ARM_REG_R0,fmt_result&0xffffffff)
        elif name=='filter':
            events.append((name,cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1)))
            cpu.reg_write(UC_ARM_REG_R0,filter_result)
        elif name=='output':events.append((name,cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1),cpu.reg_read(UC_ARM_REG_R2)))
        else:events.append((name,))
        cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    try:u.emu_start((0x43d8dc if original else entry)|1,stop,count=5000)
    except Exception as exc:raise RuntimeError((original,level,offset,fmt_result,filter_on,filter_result,suffix_on,hex(u.reg_read(UC_ARM_REG_PC)),events)) from exc
    assert u.reg_read(UC_ARM_REG_PC)==stop,(original,events,hex(u.reg_read(UC_ARM_REG_PC)))
    return events,bytes(u.mem_read(BUF,1040)),u.reg_read(UC_ARM_REG_R4) if original else u.reg_read(UC_ARM_REG_R0)
count=0;shapes=set()
for level,offset,fmt_result,filter_on,filter_result,suffix_on in itertools.product([0,1,5,255],[0,1,5,1018,1019,1020,1024],[-1,0,1,4,5,100,1024],[0,1],[0,BUF],[0,1]):
    a=run(True,level,offset,fmt_result,filter_on,filter_result,suffix_on)
    b=run(False,level,offset,fmt_result,filter_on,filter_result,suffix_on)
    assert a==b,(level,offset,fmt_result,filter_on,filter_result,suffix_on,a,b)
    shapes.add(tuple(e[0] for e in a[0]));count+=1
receipt={'status':'PASS','comparisons':count,'call_shapes':len(shapes),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'domain':'postformat suffix entered at 0x43d8dc with synthetic live frame, source linked to validated append primitive','limits':['Variadic formatter, filter result, output and unlock scripted.','Only local suffix through 0x43d970; earlier logger and initialized shared state not established.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count,'call_shapes':len(shapes)}))
