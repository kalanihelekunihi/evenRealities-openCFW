#!/usr/bin/env python3
"""Compare bounded stock instructions and reconstructed C with direct BL cuts."""
from pathlib import Path
import hashlib, importlib.util, itertools, json, struct, sys
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_HOOK_MEM_INVALID
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
IMAGE = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
ELF = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/clockmux.elf')
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / 'native-comparison.json'
blob = IMAGE.read_bytes()
assert hashlib.sha256(blob).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
spec = importlib.util.spec_from_file_location('elf_reader', ROOT/'g2/components/bootloader/update_core/elf_reader.py')
elf_reader = importlib.util.module_from_spec(spec); spec.loader.exec_module(elf_reader)
_, segments, symbols = elf_reader.elf_info(ELF)
start, end = 0x41acb2, 0x41b04c
stock_cuts = {0x41d1c0:'delay', 0x41d246:'poll', 0x41d3e4:'gpio', 0x41d90e:'power_read', 0x41d92c:'power_update', 0x41ca5c:'prepare', 0x41bf84:'mode_enter', 0x41c17a:'mode_leave', 0x41e348:'cache', 0x41caa2:'finish'}
source_cuts = {
 'opencfw_hal_delay_us':'delay', 'opencfw_hal_status_poll':'poll',
 'opencfw_legacy_gpio_mode':'gpio', 'opencfw_power_register_read':'power_read',
 'opencfw_bl_power_register_update':'power_update', 'opencfw_low_power_prepare':'prepare',
 'opencfw_bl_mspi_mode_enter':'mode_enter', 'opencfw_bl_mspi_mode_leave':'mode_leave',
 'opencfw_cache_invalidate':'cache', 'opencfw_low_power_finish':'finish'}
source_cuts = {symbols[k]&~1:v for k,v in source_cuts.items()}
mmio_words = [0x40008858,0x4000885c,0x400200c0,0x400204d8,0x400204e8,0x40004044,
              0x40004030,0x40201000,0x40208100,0x40209100,0x400b2000,0x40210000]

def run(is_source, flags, r1, r2, r5, pin_read, irq, guard, magic, gpio_value):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS); u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo,sz in [(0x08000000,0x1000),(0x410000,0x25000),(0x10000,0x10000),(0x30000,0x10000),(0x20000000,0x40000),(0x40000000,0x300000),(0x47ff0000,0x10000)]: u.mem_map(lo,sz)
    if is_source:
        for seg in segments: u.mem_write(seg['address'],seg['data'])
    else: u.mem_write(0x410000,blob)
    def w(p,x): u.mem_write(p,struct.pack('<I',x&0xffffffff))
    # Guard enabled; seed every touched peripheral word with a stable value.
    state=(magic<<16)|flags
    w(0x40008858,state); w(0x4000885c,guard)
    for p in mmio_words[2:]: w(p,0x13579bdf)
    stack=0x2003f000; entry=0x20001000
    u.mem_write(stack-0x100,b'\xa5'*0x100)
    u.mem_write(entry,struct.pack('<III',r1,r2,r5))
    u.reg_write(a.UC_ARM_REG_SP,stack); u.reg_write(a.UC_ARM_REG_LR,0x08000001)
    u.reg_write(a.UC_ARM_REG_PRIMASK,irq)
    u.reg_write(a.UC_ARM_REG_R0,0x76543210); u.reg_write(a.UC_ARM_REG_R1,r1); u.reg_write(a.UC_ARM_REG_R2,r2)
    u.reg_write(a.UC_ARM_REG_R3,0x89abcdef); u.reg_write(a.UC_ARM_REG_R5,r5)
    for reg in [4,6,7,8,9,10,11]:u.reg_write(getattr(a,f'UC_ARM_REG_R{reg}'),0xa0000000+reg)
    pc=(symbols['opencfw_boot_clockmux_entry']&~1) if is_source else start
    cuts=source_cuts if is_source else stock_cuts
    events=[]; writes=[]; done=False; pcs=[]
    def hook(cpu,p,size,_):
        nonlocal done
        pcs.append(p)
        if p==0x08000000: done=True; cpu.emu_stop(); return
        if p not in cuts:return
        kind=cuts[p]; regs=[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)]
        sp=cpu.reg_read(a.UC_ARM_REG_SP); fifth=struct.unpack('<I',cpu.mem_read(sp,4))[0]
        ptrval=None
        if kind=='gpio' and regs[1]: ptrval=cpu.mem_read(regs[1],1)[0]
        if kind=='power_read' and regs[1]: ptrval=struct.unpack('<I',cpu.mem_read(regs[1],4))[0]
        if kind=='delay': event=[kind,regs[0]]
        elif kind=='poll': event=[kind,*regs,fifth]
        elif kind=='gpio': event=[kind,regs[0],ptrval]
        elif kind=='power_read': event=[kind,regs[0]]
        elif kind=='power_update': event=[kind,regs[0],regs[1]]
        elif kind in ('mode_enter','mode_leave'): event=[kind,regs[0]]
        elif kind=='cache': event=[kind,regs[0],regs[1]]
        else: event=[kind]
        events.append(event)
        if kind=='power_read' and regs[1]: w(regs[1],pin_read)
        if kind=='gpio' and regs[1] and gpio_value is not None:u.mem_write(regs[1],bytes([gpio_value]))
        if kind=='poll': cpu.reg_write(a.UC_ARM_REG_R0,0)
        cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR))
    def wr(cpu,access,p,size,value,_):
        if 0x40000000<=p<0x40300000:
            writes.append([p,size,value&((1<<(size*8))-1)])
    def invalid(cpu,access,address,size,value,_):
        raise RuntimeError(f'unmapped {access=} {address:#x} {size=} at PC={cpu.reg_read(a.UC_ARM_REG_PC):#x}, source={is_source}, flags={flags:#x}')
    u.hook_add(UC_HOOK_CODE,hook); u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40000000,end=0x402fffff)
    u.hook_add(UC_HOOK_MEM_INVALID,invalid)
    try: u.emu_start(pc|1,0,count=200000)
    except Exception as exc:
        raise RuntimeError(f'emu failure source={is_source} flags={flags:#x} lastpcs={[hex(x) for x in pcs[-16:]]} events={events[-4:]}') from exc
    assert done, ('did not return',is_source,hex(pc))
    regs={hex(p):struct.unpack('<I',u.mem_read(p,4))[0] for p in mmio_words}
    return {'return_registers':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in [0,1,2]],'callee_saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],'stack':u.reg_read(a.UC_ARM_REG_SP),'events':events,'mmio_writes':writes,'mmio_final':regs,'primask':u.reg_read(a.UC_ARM_REG_PRIMASK)}

rows=[]
for flags,r1,r2,r5,pin,guard,magic,gpio_value in itertools.product(
    [0x7f,0x20,0x45,0x0c,0x02,0x00,0x40,0x10],
    [0,0x11223344], [0,0x76543210], [0x20027064,0xa5b6c7d8], [0,0xdeadbeef],[0,2],[0x5af0,0],[None,0x5a]):
    irq=(flags ^ r1 ^ r5) & 1
    f={'flags':flags,'r1':r1,'r2':r2,'r5':r5,'pin_read':pin,'primask':irq,'guard':guard,'magic':magic,'gpio_value':gpio_value}
    stock=run(False,flags,r1,r2,r5,pin,irq,guard,magic,gpio_value); source=run(True,flags,r1,r2,r5,pin,irq,guard,magic,gpio_value)
    if stock!=source:
        OUT.with_suffix('.failure.json').write_text(json.dumps({'fixture':f,'stock':stock,'source':source},indent=2)+'\n')
        raise AssertionError((f, stock, source))
    rows.append({'fixture':f,'result':stock})
result={'status':'PASS','cases':len(rows),'original_sha256':hashlib.sha256(blob).hexdigest(),
 'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),
 'function_range':['0x41acb2','0x41b04c'],'wrapper_contract':'Capture ambient R1/R2/R5 before C entry; Restore R0=post-body GPIO stack word,R1=post-body pin stack word,R2=incomingR3, SP and callee-saved registers. R3/R12/condition flags outside comparison.', 'cut_model':'Direct child entries intercepted identically by semantic label; GPIO getter and power-register getter have deterministic controlled output; delay, poll completion, cache, power mode and low-power child bodies are cuts.',
 'coverage':['Original stock body executed from locked image in Unicorn2/Cortex-M33 mode.','Reconstructed C leaf executed from linked ARM ELF.','Compared child call sequence and defined register/stack args, ordered MMIO writes, final MMIO words, and PRIMASK preservation across state/R5 fixtures.','Direct child cuts do not exercise child IRQ behavior, physical timing, whole native closure, or byte identity.'],
 'comparisons':rows}
OUT.write_text(json.dumps(result,indent=2)+'\n'); print('PASS',len(rows),'stock-vs-C clockmux cases')
