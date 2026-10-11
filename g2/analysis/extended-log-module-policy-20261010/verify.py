from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
sources=[ROOT/'g2/components/main/extended_log_module_policy_candidates_20261010/module_policy.c',ROOT/'g2/components/main/smp_provider_candidates_20261010/compare.c']
base=['clang','--target=arm-none-eabi','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    objs=[]
    for src in sources:
        obj=HERE/(src.stem+'-'+src.parent.name+suffix+'.o');objs.append(obj)
        subprocess.run(base[:2]+['-mcpu='+cpu]+base[2:]+['-c',str(src),'-o',str(obj)],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_module_policy',*map(str,objs),'-o',str(HERE/('module_policy'+suffix+'.elf'))],check=True)
with (HERE/'module_policy-m4.elf').open('rb') as f:
    elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_log_candidate_module_policy')
STATE=0x20070be8;CTX=0x20001000;STOP=0x110f00;SP=0x20010000
def run(original,enabled,match_index,active_index,policy_level):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    u.mem_write(CTX,(0x110d01).to_bytes(4,'little')+(0x110d21).to_bytes(4,'little'))
    u.mem_write(STATE+240,bytes([enabled]))
    for i in range(5):
        u.mem_write(STATE+49+33*i,bytes([policy_level]))
        u.mem_write(STATE+50+33*i,(b'SMP' if i==match_index else b'BAD')+b'\0')
        u.mem_write(STATE+81+33*i,bytes([1 if i==active_index else 0]))
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1)
    if original:u.reg_write(UC_ARM_REG_R0,0x56f148)
    else:u.reg_write(UC_ARM_REG_R0,CTX);u.reg_write(UC_ARM_REG_R1,0x56f148)
    events=[]
    names={0x43d416:'enter',0x43d438:'exit',0x110d00:'enter',0x110d20:'exit'}
    def hook(cpu,addr,size,_):
        if addr in names:
            events.append(names[addr]);cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((0x43d4b0 if original else entry)|1,STOP,count=1000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
    return u.reg_read(UC_ARM_REG_R0),events
count=0
for enabled,match_index,active_index,policy_level in itertools.product([0,1],range(-1,5),range(-1,5),[0,1,3,5,255]):
    a=run(True,enabled,match_index,active_index,policy_level);b=run(False,enabled,match_index,active_index,policy_level)
    assert a==b,(enabled,match_index,active_index,policy_level,a,b);count+=1
receipt={'status':'PASS','comparisons':count,'source_sha256':hashlib.sha256(sources[0].read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'domain':'nonnull module, five synthetic rows, enabled/disabled, active/inactive, match/mismatch','limits':['Null module fatal callback/recursion excluded.','Initialized production policy rows not established.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count}))
