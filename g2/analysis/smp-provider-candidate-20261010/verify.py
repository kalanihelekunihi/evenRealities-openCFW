from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=ROOT/'g2/components/main/smp_provider_candidates_20261010/compare.c'
obj=HERE/'compare.o';elf=HERE/'compare.elf'
cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)]
subprocess.run(cmd,check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_smp_candidate_compare',str(obj),'-o',str(elf)],check=True)
m4obj=HERE/'compare-m4.o';m4elf=HERE/'compare-m4.elf'
cmd4=cmd.copy();cmd4[2]='-mcpu=cortex-m4';cmd4[-1]=str(m4obj)
subprocess.run(cmd4,check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_smp_candidate_compare',str(m4obj),'-o',str(m4elf)],check=True)
with m4elf.open('rb') as f:
    e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_smp_candidate_compare')
def run(original,a,b,length):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for address,data in segs:u.mem_write(address,bytes(data))
    u.mem_map(0x20000000,0x80000)
    lhs=0x20001000;rhs=0x20001100
    u.mem_write(lhs,a);u.mem_write(rhs,b)
    stop=0x110f00;u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,stop|1)
    if original:regs=[(UC_ARM_REG_R0,lhs),(UC_ARM_REG_R1,rhs),(UC_ARM_REG_R2,length)]
    else:regs=[(UC_ARM_REG_R0,0),(UC_ARM_REG_R1,lhs),(UC_ARM_REG_R2,rhs),(UC_ARM_REG_R3,length)]
    for reg,val in regs:u.reg_write(reg,val)
    u.hook_add(UC_HOOK_CODE,lambda cpu,address,size,_:cpu.emu_stop() if address==stop else None)
    u.emu_start((0x44b610 if original else entry)|1,stop,count=100)
    assert u.reg_read(UC_ARM_REG_PC)==stop and u.reg_read(UC_ARM_REG_SP)==0x20010000
    assert bytes(u.mem_read(lhs,len(a)))==a and bytes(u.mem_read(rhs,len(b)))==b
    return u.reg_read(UC_ARM_REG_R0)
values=[b'',b'a',b'abc',b'abd',b'ABC',b'\x00abc',b'a\x00z',b'\x7f',b'\x80',b'\xff']
cases=0
for x,y,n in itertools.product(values,values,[0,1,2,3,4]):
    a=x+b'\x00'*8;b=y+b'\x00'*8
    got=run(True,a,b,n);want=run(False,a,b,n)
    assert got==want,(x,y,n,got,want)
    cases+=1
receipt={'status':'PASS','cases':cases,'original_address':'0x44b610','original_extent':'0x44b610..0x44b63a','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'compile_command':cmd,'limits':['Cortex-M55 compilation; Cortex-M4 Unicorn comparison on synthetic RAM strings.','Caller literal/data identity and source archive integration remain separate.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':cases}))
