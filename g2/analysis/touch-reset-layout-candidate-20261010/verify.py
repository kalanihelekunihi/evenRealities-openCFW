from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
firmware=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()
assert hashlib.sha256(firmware).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
image=firmware[32:];src=ROOT/'g2/components/touch/reset_layout_candidate_20261010/reset_tables.c'
script=ROOT/'g2/components/touch/reset_layout_candidate_20261010/layout_fixture.ld'
obj=HERE/'reset_tables.o';fixture_obj=HERE/'layout_fixture.o';elfpath=HERE/'reset_tables.elf';layout=HERE/'layout_fixture.elf'
flags=['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-Wall','-Wextra','-Werror']
subprocess.run([*flags,'-c',str(src),'-o',str(obj)],check=True)
subprocess.run([*flags,'-c',str(HERE/'layout_fixture.c'),'-o',str(fixture_obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_touch_candidate_reset_tables',str(obj),'-o',str(elfpath)],check=True)
subprocess.run(['arm-none-eabi-ld','-T',str(script),str(obj),str(fixture_obj),'-o',str(layout)],check=True)
with layout.open('rb') as f:
    e=ELFFile(f)
    table=b''.join(e.get_section_by_name(n).data() for n in ('.copy_table','.zero_table'))
    assert table==image[0xb578-0x3300:0xb58c-0x3300]
    assert e.get_section_by_name('.touch_data')['sh_addr']==0x200004c0
    assert e.get_section_by_name('.touch_bss')['sh_addr']==0x200008a8
with elfpath.open('rb') as f:
    e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_touch_candidate_reset_tables')
STOP=0x110f00;SP=0x2000f000
def run(original,copy_words,zero_words,seed):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x3000,0x9000);u.mem_write(0x3300,image)
    u.mem_map(0x100000,0x10000)
    for addr,data in segments:u.mem_write(addr,bytes(data))
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\xa5'*0x10000)
    data=bytes(((i*37+seed)&255) for i in range(2400))
    u.mem_write(0x20004000,data)
    u.mem_write(0xb578,struct.pack('<III',0x20004000,0x200004c0,copy_words))
    u.mem_write(0xb584,struct.pack('<II',0x200008a8,zero_words))
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1)
    if original:u.emu_start(0x4693,0x46d6,count=100000)
    else:
        for reg,value in ((UC_ARM_REG_R0,0xb578),(UC_ARM_REG_R1,0xb584),
                          (UC_ARM_REG_R2,0xb584),(UC_ARM_REG_R3,0xb58c)):
            u.reg_write(reg,value)
        u.emu_start(entry|1,STOP,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==(0x46d6 if original else STOP)
    assert u.reg_read(UC_ARM_REG_SP)==SP
    return bytes(u.mem_read(0x20000000,0x5000))
cases=[]
for copy_words,zero_words,seed in itertools.product([0,1,2,241,400],[0,1,2,428,600],[0,17,255]):
    a=run(True,copy_words,zero_words,seed)
    b=run(False,copy_words,zero_words,seed)
    assert a==b,(copy_words,zero_words,seed)
    cases.append((copy_words,zero_words,seed))
receipt={'status':'PASS','comparisons':len(cases),
         'firmware_sha256':hashlib.sha256(firmware).hexdigest(),
         'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'linker_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),
         'descriptor_bytes':table.hex(),'descriptor_matches_stock':True,
         'domain':'One copy and one zero descriptor; synthetic source bytes/counts; complete RAM target-window comparison',
         'limits':['Reset prefix and call at 0x46d6 are outside source body.','Synthetic linker data do not reproduce original init values.','45-unit touch archive is not linked into this fixture.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'PASS','comparisons':len(cases),'descriptor_matches_stock':True}))
