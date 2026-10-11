from pathlib import Path
import hashlib, itertools, json, subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=ROOT/'g2/components/main/extended_log_common_format_candidates_20261010/common_format.c'
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    obj=HERE/('common_format'+suffix+'.o'); elfpath=HERE/('common_format'+suffix+'.elf')
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu='+cpu,'-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_common_format',str(obj),'-o',str(elfpath)],check=True)
with (HERE/'common_format-m4.elf').open('rb') as f:
    elf=ELFFile(f)
    segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
    entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_log_candidate_common_format')
STOP=0x110f00; DEST=0x20002000; ARGS=0x20003000; STRS=[0x20004000+i*0x100 for i in range(5)]
cases=[
    (0x730d64,[]), # no conversion
    (0x75d430,[0,1,0x7fffffff,0x80000000,0xffffffff]),
    (0x75d4b0,[0,1,0x7fffffff,0x80000000,0xffffffff]),
    (0x749dbc,['','A','state','X'*32]),
    (0x7815fc,[0,1,0xdeadbeef]),
    (0x727950,[0,1,0xffffffff]),
    (0x74c10c,[0,1,0xdeadbeef]),
    (0x6f385c,[0,1,0x20001000,0xffffffff]),
]
def signature(format_addr):
    end=raw.find(b'\0',format_addr-0x438000)
    return raw[format_addr-0x438000:end].decode('utf-8','replace')
def run(original,format_addr,capacity,values,cpu_model=UC_CPU_ARM_CORTEX_M4):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(cpu_model)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000);u.mem_write(DEST,b'Z'*2048)
    words=[]
    for i,value in enumerate(values):
        if isinstance(value,str):
            u.mem_write(STRS[i],value.encode()+b'\0');words.append(STRS[i])
        else:words.append(value)
    u.mem_write(ARGS,b''.join(v.to_bytes(4,'little') for v in words) or b'\0\0\0\0')
    u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    for reg,val in [(UC_ARM_REG_R0,DEST),(UC_ARM_REG_R1,capacity),(UC_ARM_REG_R2,format_addr),(UC_ARM_REG_R3,ARGS)]:u.reg_write(reg,val)
    u.hook_add(UC_HOOK_CODE,lambda cpu,addr,size,_:cpu.emu_stop() if addr==STOP else None)
    try:u.emu_start((0x44b76c if original else entry)|1,STOP,count=50000)
    except Exception as exc:raise RuntimeError(hex(u.reg_read(UC_ARM_REG_PC))) from exc
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x20010000
    return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(DEST,2048))
total=0; selected=[]
for fmt,values in cases:
    s=signature(fmt)
    count=s.count('%')
    combinations=[()] if count==0 else itertools.product(values,repeat=count)
    for args in combinations:
        for capacity in [0,1,2,8,32,128,1024]:
            a=run(True,fmt,capacity,args);b=run(False,fmt,capacity,args)
            assert a==b,(hex(fmt),capacity,args,a[0],b[0],a[1][:100],b[1][:100])
            total+=1
    selected.append({'format':hex(fmt),'text':s})
receipt={'status':'PASS','comparisons':total,'formats':selected,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'image_sha256':hashlib.sha256(raw).hexdigest(),'limits':['Only exact plain conversion syntax in selected formats','No flags, widths, precision, float, pointer or arbitrary varargs ABI']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'PASS','comparisons':total}))
