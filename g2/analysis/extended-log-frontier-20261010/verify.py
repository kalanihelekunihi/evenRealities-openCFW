from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert int.from_bytes(raw[0x43da70-0x438000:0x43da74-0x438000],'little')==0x20070be8
src=ROOT/'g2/components/main/extended_log_helpers_20261010/guard.c'
cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(HERE/'guard.o')]
subprocess.run(cmd,check=True);subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_guard_enter',str(HERE/'guard.o'),'-o',str(HERE/'guard.elf')],check=True)
cmd4=cmd.copy();cmd4[2]='-mcpu=cortex-m4';cmd4[-1]=str(HERE/'guard-m4.o');subprocess.run(cmd4,check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_guard_enter',str(HERE/'guard-m4.o'),'-o',str(HERE/'guard-m4.elf')],check=True)
with (HERE/'guard-m4.elf').open('rb') as f:
    e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}

def run(original,mode,flag,prior1,prior2):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    ctx=0x20001000;u.mem_write(ctx,(0x110e01).to_bytes(4,'little')+(0x110e21).to_bytes(4,'little'))
    base=0x20070be8;u.mem_write(base+242,bytes([flag,prior1,prior2]))
    stop=0x110f00;u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,stop|1);u.reg_write(UC_ARM_REG_R0,0 if original else ctx)
    events=[]
    def hook(cpu,addr,size,_):
        if addr==stop:cpu.emu_stop()
        elif addr in [0x44aa98,0x110e00,0x44aaa0,0x110e20]:
            events.append('enter' if addr in [0x44aa98,0x110e00] else 'exit')
            cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    orig_entry={'enter':0x43d416,'exit':0x43d438}[mode]
    src_entry=syms['g2_log_candidate_guard_'+mode]
    u.emu_start((orig_entry if original else src_entry)|1,stop,count=30)
    assert u.reg_read(UC_ARM_REG_PC)==stop and u.reg_read(UC_ARM_REG_SP)==0x20010000
    return bytes(u.mem_read(base+242,3)),events
count=0
for mode,flag,p1,p2 in itertools.product(['enter','exit'],[0,1,2,255],[0,1,255],[0,1,255]):
    a=run(True,mode,flag,p1,p2);b=run(False,mode,flag,p1,p2)
    assert a==b,(mode,flag,p1,p2,a,b);count+=1
receipt={'status':'PASS','comparisons':count,'original_entries':{'enter':'0x43d416','exit':'0x43d438'},'original_bytes':68,'raw_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'compile_command':cmd,'limits':['Lower provider entry 0x44aa98 and exit 0x44aaa0 intercepted identically; their mutex/kernel effects not implemented.','Guard helpers only; extended log 0x43d574 body remains unimplemented.','Cortex-M55 compile and Cortex-M4 Unicorn comparison; synthetic log control state.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':count}))
