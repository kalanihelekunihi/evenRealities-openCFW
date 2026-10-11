from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=ROOT/'g2/components/main/extended_log_policy_candidates_20261010/policy.c'
base=['clang','--target=arm-none-eabi','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    subprocess.run(base[:2]+['-mcpu='+cpu]+base[2:]+['-c',str(src),'-o',str(HERE/('policy'+suffix+'.o'))],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_mask_normal',str(HERE/('policy'+suffix+'.o')),'-o',str(HERE/('policy'+suffix+'.elf'))],check=True)
with (HERE/'policy-m4.elf').open('rb') as f:
    elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
names=['g2_log_candidate_mask_normal','g2_log_candidate_optional_128_normal','g2_log_candidate_optional_32_64_normal']
stock=[0x43d97c,0x43d9f0,0x43da0a]; stop=0x110f00; count=0
def run(original,index,level,mask,arg,bits):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    for i in range(6):u.mem_write(0x20070be8+216+4*i,bits.to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,stop|1)
    for reg,val in [(UC_ARM_REG_R0,level),(UC_ARM_REG_R1,mask),(UC_ARM_REG_R2,arg)]:u.reg_write(reg,val)
    u.hook_add(UC_HOOK_CODE,lambda cpu,addr,size,_:cpu.emu_stop() if addr==stop else None)
    u.emu_start((stock[index] if original else symbols[names[index]])|1,stop,count=100)
    assert u.reg_read(UC_ARM_REG_PC)==stop and u.reg_read(UC_ARM_REG_SP)==0x20010000
    return u.reg_read(UC_ARM_REG_R0)
for index,level,mask,arg,bits in itertools.product(range(3),range(6),[0,1,0x20,0x80,0xffffffff],[0,1,0x20001000],[0,1,0x20,0x80,0xffffffff]):
    a=run(True,index,level,mask,arg,bits);b=run(False,index,level,mask,arg,bits)
    assert a==b,(index,level,mask,arg,bits,a,b)
    count+=1
receipt={'status':'PASS','comparisons':count,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'domain':'levels 0..5; mask/argument zero and nonzero','limits':['Fatal level >=6 branch not implemented in this bounded source.','These lower policy helpers do not establish full 0x43d574 logger output.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count}))
