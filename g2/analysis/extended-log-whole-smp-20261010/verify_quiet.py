from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
paths=[ROOT/'g2/components/main/extended_log_smp_quiet_candidates_20261010/quiet.c',ROOT/'g2/components/main/extended_log_postformat_candidates_20261010/postformat.c',ROOT/'g2/components/main/extended_log_append_candidates_20261010/append.c',ROOT/'g2/components/main/extended_log_smp_format_candidates_20261010/smp_format.c']
base=['clang','--target=arm-none-eabi','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    objs=[]
    for path in paths:
        obj=HERE/(path.stem+'-'+path.parent.name+suffix+'.o');objs.append(obj)
        subprocess.run(base[:2]+['-mcpu='+cpu]+base[2:]+['-c',str(path),'-o',str(obj)],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_smp_quiet',*map(str,objs),'-o',str(HERE/('quiet'+suffix+'.elf'))],check=True)
with (HERE/'quiet-m4.elf').open('rb') as f:
    elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
STATE=0x20070be8;BUF=0x2006bd30;CTX=0x20001000;STOP=0x110f00;SP=0x20010000;ARGS=0x20004000
def run(original,fmt,active,limit,level,a,b):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for x,data in segs:u.mem_write(x,bytes(data))
    u.mem_map(0x20000000,0x80000)
    u.mem_write(STATE,bytes([limit]));u.mem_write(STATE+241,bytes([active]))
    u.mem_write(BUF,b'Z'*1040)
    u.mem_write(0x20003000,b'event\0');u.mem_write(0x20003100,b'state\0')
    u.mem_write(ARGS,a.to_bytes(4,'little')+b.to_bytes(4,'little'))
    u.mem_write(CTX,b''.join((v|1).to_bytes(4,'little') for v in [symbols['g2_log_candidate_smp_format'],0x110d00,0x110d20,0x110d40,0x110d60]))
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1)
    if original:
        u.mem_write(SP,(852).to_bytes(4,'little')+fmt.to_bytes(4,'little')+a.to_bytes(4,'little')+b.to_bytes(4,'little'))
        for reg,val in [(UC_ARM_REG_R0,level),(UC_ARM_REG_R1,0x56f148),(UC_ARM_REG_R2,0x6e1994),(UC_ARM_REG_R3,0x789060)]:u.reg_write(reg,val)
    else:
        for reg,val in [(UC_ARM_REG_R0,CTX),(UC_ARM_REG_R1,level),(UC_ARM_REG_R2,fmt),(UC_ARM_REG_R3,ARGS)]:u.reg_write(reg,val)
    events=[];trace=[]
    names={0x43d416:'lock',0x43d438:'unlock',0x44aa80:'output',0x110d60:'lock',0x110d40:'unlock',0x110d20:'output',0x110d00:'filter'}
    def hook(cpu,addr,size,_):
        trace.append(addr)
        name=names.get(addr)
        if name is None:return
        if name=='output':events.append((name,cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1),cpu.reg_read(UC_ARM_REG_R2)))
        else:events.append((name,))
        cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    try:u.emu_start((0x43d574 if original else symbols['g2_log_candidate_smp_quiet'])|1,STOP,count=50000)
    except Exception as exc:raise RuntimeError((original,hex(fmt),active,limit,level,a,b,hex(u.reg_read(UC_ARM_REG_PC)),events,[hex(x) for x in trace[-20:]])) from exc
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP,(original,events,hex(u.reg_read(UC_ARM_REG_PC)),hex(u.reg_read(UC_ARM_REG_SP)))
    return events,bytes(u.mem_read(BUF,1040))
count=0;shapes=set()
for fmt,active,limit,level in itertools.product([0x77bf14,0x765710],[0,1],[0,3,5],range(6)):
    values=[(0x20003000,0x20003100)] if fmt==0x77bf14 else [(0,0),(17,4),(0xffffffff,0x80000000)]
    for a,b in values:
        x=run(True,fmt,active,limit,level,a,b);y=run(False,fmt,active,limit,level,a,b)
        assert x==y,(hex(fmt),active,limit,level,a,b,x,y)
        shapes.add(tuple(e[0] for e in x[0]));count+=1
receipt={'status':'PASS','comparisons':count,'call_shapes':len(shapes),'source_sha256':hashlib.sha256(paths[0].read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'domain':'entry-to-return SMP logger path with state[240]=0, state[1]=0, all masks zero, state[245]=0, state[32]=0, two authenticated formats','limits':['This is a restricted path, not the complete 1,026-byte logger body.','Only lock/output calls scripted; actual transport and initialized logger RAM remain unestablished.']}
(HERE/'quiet_results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count,'call_shapes':len(shapes)}))
