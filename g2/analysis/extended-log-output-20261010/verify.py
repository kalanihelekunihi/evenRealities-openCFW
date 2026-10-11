from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=ROOT/'g2/components/main/extended_log_output_candidates_20261010/output.c'
base=['clang','--target=arm-none-eabi','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    subprocess.run(base[:2]+['-mcpu='+cpu]+base[2:]+['-c',str(src),'-o',str(HERE/('output'+suffix+'.o'))],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_output',str(HERE/('output'+suffix+'.o')),'-o',str(HERE/('output'+suffix+'.elf'))],check=True)
with (HERE/'output-m4.elf').open('rb') as f:
    elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_log_candidate_output')
STOP=0x110f00;CTX=0x20001000;count=0
def run(original,buffer,length,level,handle):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    u.mem_write(CTX,(0x110d01).to_bytes(4,'little')+(0x110d21).to_bytes(4,'little'))
    u.mem_write(0x20074570,handle.to_bytes(4,'little'))
    u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    if original:args=[buffer,length,level]
    else:args=[CTX,buffer,length,level]
    for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,val)
    events=[]
    def hook(cpu,addr,size,_):
        name={0x448d4e:'submit',0x4495e4:'signal',0x110d00:'submit',0x110d20:'signal'}.get(addr)
        if not name:return
        events.append((name,cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1),cpu.reg_read(UC_ARM_REG_R2),cpu.reg_read(UC_ARM_REG_R3)) if name=='submit' else (name,cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1)))
        cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((0x44aa80 if original else entry)|1,STOP,count=100)
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x20010000
    return events
for buffer,length,level,handle in itertools.product([0,0x20002000],[0,1,1024],[0,1,5,6,255,256,0xffffffff],[0,1,0x20003000]):
    a=run(True,buffer,length,level,handle);b=run(False,buffer,length,level,handle)
    assert a==b,(buffer,length,level,handle,a,b)
    count+=1
receipt={'status':'PASS','comparisons':count,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'limits':['Submit and signal lower calls scripted; no transport delivery semantics.','Output wrapper is a lower provider and does not establish complete extended logger.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count}))
