from pathlib import Path
import hashlib, json, subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import *

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
component=ROOT/'g2/components/touch/reset_layout_candidate_20261010'
fw=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
image=fw[32:]
flags=['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror']
objects=[]
for stem in ('reset_tables','reset_suffix','reset_prefix'):
    obj=HERE/(stem+'.o');objects.append(obj)
    subprocess.run([*flags,'-c',str(component/(stem+'.c')),'-o',str(obj)],check=True)
elf=HERE/'reset_suffix.elf'
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_touch_candidate_reset_suffix',*[str(p) for p in objects],'-o',str(elf)],check=True)
with elf.open('rb') as f:
    e=ELFFile(f)
    segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_touch_candidate_reset_suffix')
    prefix=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_touch_candidate_reset_prefix')
STOP=0x110f00
def run_prefix(original,pattern):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x3000,0x9000);u.mem_write(0x3300,image)
    u.mem_map(0x100000,0x20000)
    for a,b in segments:u.mem_write(a,bytes(b))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes([pattern])*0x10000)
    u.mem_map(0x40030000,0x1000);u.mem_write(0x40030000,bytes([pattern])*0x1000)
    sp=0x2000f000;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.emu_start(0x4675 if original else prefix|1,0x467e if original else STOP,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==(0x467e if original else STOP)
    return bytes(u.mem_read(0x40030000,0x1000)),u.reg_read(UC_ARM_REG_PRIMASK)
def run(original,pattern):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x3000,0x9000);u.mem_write(0x3300,image)
    u.mem_map(0x100000,0x20000)
    for a,b in segments:u.mem_write(a,bytes(b))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,bytes([pattern])*0x10000)
    u.mem_map(0xe000e000,0x1000)
    sp=0x2000f000;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,STOP|1)
    if original:u.emu_start(0x467f,0x46d6,count=100000)
    else:
        for reg,val in ((UC_ARM_REG_R0,0x3300),(UC_ARM_REG_R1,0x20000400),
                        (UC_ARM_REG_R2,0xe000ed08),(UC_ARM_REG_R3,0xb578)):
            u.reg_write(reg,val)
        for off,val in enumerate((0xb584,0xb584,0xb58c)):
            u.mem_write(sp+off*4,val.to_bytes(4,'little'))
        u.emu_start(entry|1,STOP,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==(0x46d6 if original else STOP)
    return bytes(u.mem_read(0x20000000,0x2000)),bytes(u.mem_read(0xe000ed08,4))
for pattern in (0,1,0x5a,0xff):
    assert run_prefix(True,pattern)==run_prefix(False,pattern),('prefix',pattern)
    assert run(True,pattern)==run(False,pattern),pattern
result={'status':'PASS','patterns':[0,1,90,255],
        'domain':'stock 0x4674..0x467e prefix MMIO/PRIMASK and 0x467e..0x46d6 suffix versus compiled source; RAM and VTOR bytes',
        'limits':['MMIO peripheral response is not simulated','0x46d6 runtime call excluded','source uses stock initialized bytes as validation input only']}
(HERE/'suffix_results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
