from pathlib import Path
import hashlib,json,random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert raw[0x43da6c-0x438000:0x43da70-0x438000]==b'%ld\0'
src=ROOT/'g2/components/main/extended_log_time_candidates_20261010/time.c'
base=['clang','--target=arm-none-eabi','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
for cpu,suffix in [('cortex-m55',''),('cortex-m4','-m4')]:
    subprocess.run(base[:2]+['-mcpu='+cpu]+base[2:]+['-c',str(src),'-o',str(HERE/('time'+suffix+'.o'))],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_log_candidate_timestamp_5',str(HERE/('time'+suffix+'.o')),'-o',str(HERE/('time'+suffix+'.elf'))],check=True)
with (HERE/'time-m4.elf').open('rb') as f:
    elf=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_log_candidate_timestamp_5')
STOP=0x110f00;DEST=0x20002000
def run(original,value):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for a,data in segs:u.mem_write(a,bytes(data))
    u.mem_map(0x20000000,0x80000);u.mem_write(DEST,b'Z'*32)
    u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.reg_write(UC_ARM_REG_R0,DEST)
    if original:
        u.reg_write(UC_ARM_REG_R1,5);u.reg_write(UC_ARM_REG_R2,0x43da6c);u.reg_write(UC_ARM_REG_R3,value)
    else:u.reg_write(UC_ARM_REG_R1,value)
    u.hook_add(UC_HOOK_CODE,lambda cpu,addr,size,_:cpu.emu_stop() if addr==STOP else None)
    u.emu_start((0x44b728 if original else entry)|1,STOP,count=50000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x20010000
    return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(DEST,32))
values={0,1,9,10,99,100,999,1000,9999,10000,12345,99999,0x7fffffff,0x80000000,0xffffffff,0xffffff9c}
for n in range(1,11):values.update([10**n-1,10**n,10**n+1,(-10**n+1)&0xffffffff,(-10**n)&0xffffffff,(-10**n-1)&0xffffffff])
rng=random.Random(0x43d574);values.update(rng.getrandbits(32) for _ in range(128))
for value in sorted(values):
    a=run(True,value);b=run(False,value)
    assert a==b,(hex(value),a,b)
receipt={'status':'PASS','comparisons':len(values),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'domain':'stock logger fixed call capacity 5, format %ld, 32-bit value','limits':['Only fixed timestamp call, not general snprintf or variadic formatter.','No initialized logger buffer or output side effects established.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','comparisons':len(values)}))
