from pathlib import Path
import hashlib,itertools,json,random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert raw[0x77bf14-0x438000:0x77bf14-0x438000+23].startswith(b'SMP Exe: evt=%s st=%s\0')
assert raw[0x765710-0x438000:0x765710-0x438000+36].startswith(b'smpSmExecute event=%d state=%d\0')
src=ROOT/'g2/components/main/extended_log_smp_format_candidates_20261010/smp_format.c'
base=['clang','--target=arm-none-eabi','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    subprocess.run(base[:2]+['-mcpu='+cpu]+base[2:]+['-c',str(src),'-o',str(HERE/('smp_format'+suffix+'.o'))],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_smp_format',str(HERE/('smp_format'+suffix+'.o')),'-o',str(HERE/('smp_format'+suffix+'.elf'))],check=True)
with (HERE/'smp_format-m4.elf').open('rb') as f:
    elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_log_candidate_smp_format')
STOP=0x110f00;DEST=0x20002000;ARGS=0x20003000;A=0x20004000;B=0x20004100
def run(original,fmt,capacity,x,y,string_mode):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000);u.mem_write(DEST,b'Z'*2048)
    if string_mode:
        u.mem_write(A,x.encode()+b'\0');u.mem_write(B,y.encode()+b'\0');x=A;y=B
    u.mem_write(ARGS,x.to_bytes(4,'little')+y.to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    for reg,val in [(UC_ARM_REG_R0,DEST),(UC_ARM_REG_R1,capacity),(UC_ARM_REG_R2,fmt),(UC_ARM_REG_R3,ARGS)]:u.reg_write(reg,val)
    u.hook_add(UC_HOOK_CODE,lambda cpu,addr,size,_:cpu.emu_stop() if addr==STOP else None)
    u.emu_start((0x44b76c if original else entry)|1,STOP,count=50000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x20010000
    return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(DEST,2048))
count=0
strs=['','A','abc','state','X'*32]
for capacity,x,y in itertools.product([0,1,2,4,8,16,32,128,1024],strs,strs):
    a=run(True,0x77bf14,capacity,x,y,True);b=run(False,0x77bf14,capacity,x,y,True)
    assert a==b,(capacity,x,y,a[0],b[0]);count+=1
nums=[0,1,9,10,1234,0x7fffffff,0x80000000,0xffffffff]
for capacity,x,y in itertools.product([0,1,2,4,8,16,32,128,1024],nums,nums):
    a=run(True,0x765710,capacity,x,y,False);b=run(False,0x765710,capacity,x,y,False)
    assert a==b,(capacity,x,y,a[0],b[0]);count+=1
receipt={'status':'PASS','comparisons':count,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'domain':'two smpSmExecute literal formats with two word arguments','limits':['Not a general variadic formatter; all other format strings outside domain.','Actual name-provider strings and whole logger body remain separate.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count}))
