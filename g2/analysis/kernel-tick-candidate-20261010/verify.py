from pathlib import Path
import hashlib, itertools, json, subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_IPSR, UC_ARM_REG_PRIMASK, UC_ARM_REG_BASEPRI

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
raw=STOCK.read_bytes()[32:]
assert hashlib.sha256(raw).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert len(raw)==3523364
for lit,expected in [(0x4557ac,0x20074a34),(0x456064,0x20074a3c),(0x456068,0x20074a58)]:
    assert int.from_bytes(raw[lit-0x438000:lit-0x438000+4],'little')==expected
src=ROOT/'g2/components/main/kernel_tick_candidates_20261010/tick.c'
obj=HERE/'tick.o'; elf=HERE/'tick.elf'
emu_obj=HERE/'tick-m4.o'; emu_elf=HERE/'tick-m4.elf'
compile_cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-std=c11','-Oz','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)]
subprocess.run(compile_cmd,check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_kernel_candidate_os_get_tick',str(obj),'-o',str(elf)],check=True)
subprocess.run([*compile_cmd[:3],'-mcpu=cortex-m4',*compile_cmd[4:-3],'-c',str(src),'-o',str(emu_obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','g2_kernel_candidate_os_get_tick',str(emu_obj),'-o',str(emu_elf)],check=True)
with emu_elf.open('rb') as f:
    e=ELFFile(f)
    segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    entries={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
functions=[('g2_kernel_candidate_scheduler_state',0x4558a4),('g2_kernel_candidate_is_irq',0x44900e),('g2_kernel_candidate_get_tick',0x454efe),('g2_kernel_candidate_get_tick_from_isr',0x454f06),('g2_kernel_candidate_os_get_tick',0x4490cc),('g2_flashdb_candidate_tick',0x4490cc)]
def execute(entry,stock,active,suspended,ipsr,primask,basepri,tick):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw)
    u.mem_map(0x100000,0x20000)
    for addr,data in segs:u.mem_write(addr,bytes(data))
    u.mem_map(0x20000000,0x80000)
    for addr,val in [(0x20074a34,tick),(0x20074a3c,active),(0x20074a58,suspended)]:u.mem_write(addr,val.to_bytes(4,'little'))
    before=bytes(u.mem_read(0x20074a30,0x30))
    stop=0x110f00
    u.reg_write(UC_ARM_REG_SP,0x20010000);u.reg_write(UC_ARM_REG_LR,stop|1)
    u.reg_write(UC_ARM_REG_IPSR,ipsr);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_BASEPRI,basepri)
    trace=[]
    def hook(cpu,addr,size,_):
        trace.append(addr)
        if addr==stop:cpu.emu_stop()
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(entry|1,stop,count=100)
    assert u.reg_read(UC_ARM_REG_PC)==stop,(hex(entry),trace)
    assert u.reg_read(UC_ARM_REG_SP)==0x20010000
    assert bytes(u.mem_read(0x20074a30,0x30))==before
    return u.reg_read(UC_ARM_REG_R0),trace
cases=0;paths=set()
for active,suspended,ipsr,primask,basepri,tick in itertools.product([0,1,2],[0,1,2],[0,1,15],[0,1],[0,1,0x80],[0,1,0xffffffff,0x80000000]):
    args=(active,suspended,ipsr,primask,basepri,tick)
    for name,original in functions:
        a,trace=execute(original,True,*args)
        b,_=execute(entries[name],False,*args)
        assert a==b,(name,args,hex(a),hex(b))
        cases+=1
        if name=='g2_kernel_candidate_os_get_tick':
            paths.add('isr' if 0x454f06 in trace else 'task')
assert paths=={'isr','task'},paths
receipt={'status':'PASS','comparisons':cases,'fixture_combinations':cases//len(functions),'functions':{n:hex(a) for n,a in functions},'wrapper_paths':sorted(paths),'raw_sha256':hashlib.sha256(raw).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'compile_command':compile_cmd,'limits':['Cortex-M4 Unicorn original/source execution; Cortex-M55 source object compilation.','Synthetic scheduler, tick and exception-mask state; no hardware timing, scheduler lifetime, linker placement or byte identity.']}
(HERE/'results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
