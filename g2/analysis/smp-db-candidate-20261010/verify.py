from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
for a,v in [(0x5429f4,0x200708ec),(0x542a28,0x200004b8)]:assert int.from_bytes(raw[a-0x438000:a-0x438000+4],'little')==v
src=ROOT/'g2/components/main/smp_db_candidates_20261010/db_service.c'
cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(HERE/'db_service.o')]
subprocess.run(cmd,check=True);subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_smp_candidate_db_service',str(HERE/'db_service.o'),'-o',str(HERE/'db_service.elf')],check=True)
cmd4=cmd.copy();cmd4[2]='-mcpu=cortex-m4';cmd4[-1]=str(HERE/'db_service-m4.o');subprocess.run(cmd4,check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_smp_candidate_db_service',str(HERE/'db_service-m4.o'),'-o',str(HERE/'db_service-m4.elf')],check=True)
with (HERE/'db_service-m4.elf').open('rb') as f:
    e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_smp_candidate_db_service')
base=0x200708ec;timer_active=base+253

def fixture(pattern,active,remaining,interval,expiry,count,divisor,period,timer_running):
    data=bytearray(256)
    indices=range(10) if pattern=='all' else ([] if pattern=='none' else [int(pattern)])
    for i in indices:
        row=i*24;data[row+7]=active;data[row+8:row+10]=count.to_bytes(2,'little')
        for off,val in [(12,remaining),(16,interval),(20,expiry)]:data[row+off:row+off+4]=val.to_bytes(4,'little')
    data[253]=timer_running
    return bytes(data)

def run(original,blob,divisor,period,set_running):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000)
    u.mem_write(base,blob)
    cfg=0x20002000;u.mem_write(0x200004b8,cfg.to_bytes(4,'little'))
    u.mem_write(cfg+16,period.to_bytes(4,'little'));u.mem_write(cfg+20,divisor.to_bytes(2,'little'))
    ctx=0x20001000;u.mem_write(ctx,(0x110e01).to_bytes(4,'little'))
    stop=0x110f00;u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,stop|1);u.reg_write(UC_ARM_REG_R0,0 if original else ctx)
    events=[]
    def hook(cpu,addr,size,_):
        if addr==stop:cpu.emu_stop()
        elif addr in (0x52a4c4,0x110e00):
            events.append((cpu.reg_read(UC_ARM_REG_R0),cpu.reg_read(UC_ARM_REG_R1)))
            if set_running:cpu.mem_write(timer_active,b'\x01')
            cpu.reg_write(UC_ARM_REG_PC,cpu.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((0x542960 if original else entry)|1,stop,count=2000)
    assert u.reg_read(UC_ARM_REG_PC)==stop and u.reg_read(UC_ARM_REG_SP)==0x20010000
    assert bytes(u.mem_read(cfg+16,6))==period.to_bytes(4,'little')+divisor.to_bytes(2,'little')
    return bytes(u.mem_read(base,256)),events

cases=0;paths=set()
scenarios=[
    (0,0,0,0,0),(1,0,0,0,0),(0,1000,1000,1000,1),(1,1001,1001,1001,1),
    (1,2000,0xffffffff,2000,4),(0,0,1,1,65535),(1,999,2000,0,7),
]
for pattern,(active,remaining,interval,expiry,count),divisor,period,timer_running,set_running in itertools.product(['none','all',0,1,5,9],scenarios,[0,1,3,1000],[0,1,2000],[0,1],[False,True]):
    blob=fixture(pattern,active,remaining,interval,expiry,count,divisor,period,timer_running)
    a=run(True,blob,divisor,period,set_running);b=run(False,blob,divisor,period,set_running)
    assert a==b,(pattern,active,remaining,interval,expiry,count,divisor,period,timer_running,set_running,a,b)
    paths.add((bool(a[1]),len(a[1]),a[0]!=blob));cases+=1
receipt={'status':'PASS','comparisons':cases,'path_shapes':len(paths),'original':'0x542960..0x5429f2','raw_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'compile_command':cmd,'limits':['Synthetic 10-row DB and timer state; timer-start provider callback observed, not implemented.','Cortex-M55 compile and Cortex-M4 Unicorn original/source comparisons; no initialized device database, wall-clock timing or byte identity.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':cases,'path_shapes':len(paths)}))
