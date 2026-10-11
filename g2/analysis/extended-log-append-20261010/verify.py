from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=ROOT/'g2/components/main/extended_log_append_candidates_20261010/append.c'
base=['clang','--target=arm-none-eabi','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    subprocess.run(base[:2]+['-mcpu='+cpu]+base[2:]+['-c',str(src),'-o',str(HERE/('append'+suffix+'.o'))],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_append_normal',str(HERE/('append'+suffix+'.o')),'-o',str(HERE/('append'+suffix+'.elf'))],check=True)
with (HERE/'append-m4.elf').open('rb') as f:
    elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_log_candidate_append_normal')
STOP=0x110f00;DEST=0x20002000;SOURCE=0x20003000;count=0
def run(original,offset,length,pattern):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    u.mem_write(DEST,b'Z'*2048)
    u.mem_write(SOURCE,bytes([pattern])*length+b'\0')
    u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    for reg,val in [(UC_ARM_REG_R0,offset),(UC_ARM_REG_R1,DEST),(UC_ARM_REG_R2,SOURCE)]:u.reg_write(reg,val)
    u.hook_add(UC_HOOK_CODE,lambda cpu,addr,size,_:cpu.emu_stop() if addr==STOP else None)
    u.emu_start((0x44b668 if original else entry)|1,STOP,count=20000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x20010000
    return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(DEST,2048))
for offset,length,pattern in itertools.product([0,1,8,512,1022,1023,1024,1025,0xffffffff],[0,1,2,5,512,1025],[0x41,0x7f]):
    a=run(True,offset,length,pattern);b=run(False,offset,length,pattern)
    assert a==b,(offset,length,pattern,a[0],b[0])
    count+=1
receipt={'status':'PASS','comparisons':count,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'limits':['Nonnull destination/source branch only; the stock null arguments enter an assert/fatal path.','Appender is a lower provider and does not establish complete extended logger.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count}))
