"""No-error RX callback and disabled-error fall-through from public IRQ."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
fw_hash=hashlib.sha256(fw).hexdigest()
assert fw_hash=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
elf=D/'rx_fallthrough.elf';ld=D/'rx_fallthrough.ld';objects=[]
for src in (D/'rx_fallthrough.c',D/'mixed_tail.c',D/'rx_fallthrough_fixture.c',D/'tx_ready_fixture.c',D/'tx_complete_fixture.c'):
    obj=D/(src.stem+'.o');objects.append(obj)
    subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
ld.write_text('SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['arm-none-eabi-ld','-T',str(ld),*[str(x) for x in objects],'-o',str(elf)],check=True)
with elf.open('rb') as f:
    e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
H=0x20002000;HW=0x40013800;STOP=0x20000100
def run(stock,isr,cr1,cr3,primask,pointer,mutation,rx_pointer):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:])
    u.mem_map(0x00100000,0x10000)
    for a,b in seg:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000)
    u.mem_write(H,b'\xa5'*148);u.mem_write(H,struct.pack('<I',HW))
    u.mem_write(H+0x6c,struct.pack('<I',0))
    u.mem_write(H+0x74,struct.pack('<I',(sym['case_rx_tail_callback']|1) if rx_pointer else 0))
    u.mem_write(H+0x78,struct.pack('<I',(sym['case_tx_ready_callback']|1) if pointer else 0))
    u.mem_write(H+0x8c,struct.pack('<II',0x22,0))
    u.mem_write(HW,struct.pack('<III',cr1,0x12345678,cr3));u.mem_write(HW+0x1c,struct.pack('<II',isr,0xfeedface))
    for name in ('case_tx_complete_calls','case_tx_complete_arg','case_tx_calls','case_tx_arg'):u.mem_write(sym[name],bytes(4))
    for name in ('case_rx_tail_calls','case_rx_tail_arg'):u.mem_write(sym[name],bytes(4))
    u.mem_write(sym['case_rx_tail_mutation'],struct.pack('<I',int(mutation)))
    u.mem_write(sym['case_tx_cr1_xor'],struct.pack('<I',0x40 if mutation else 0))
    u.mem_write(sym['case_tx_pointer_xor'],struct.pack('<I',0x100 if mutation else 0))
    u.reg_write(UC_ARM_REG_R0,H);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,STOP|1);u.reg_write(UC_ARM_REG_PRIMASK,primask)
    writes=[];weak=[]
    def on_write(u,access,addr,width,value,data):
        if HW<=addr<HW+0x24:writes.append((addr,width,value,u.reg_read(UC_ARM_REG_PRIMASK)))
    def on_code(u,addr,width,data):
        if stock and addr==0x08006776:u.reg_write(UC_ARM_REG_PC,sym['case_tx_complete_provider']|1)
        if stock and addr in (0x08005efe,0x08005efc,0x08005e6c):weak.append((addr,u.reg_read(UC_ARM_REG_R0)))
    u.hook_add(UC_HOOK_MEM_WRITE,on_write)
    u.hook_add(UC_HOOK_CODE,on_code)
    u.emu_start(0x08005f51 if stock else sym['case_uart_rx_fallthrough']|1,STOP,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x20008000
    calls=tuple(struct.unpack('<I',u.mem_read(sym[name],4))[0] for name in ('case_rx_tail_calls','case_rx_tail_arg','case_tx_complete_calls','case_tx_complete_arg','case_tx_calls','case_tx_arg'))
    return bytes(u.mem_read(H,148)),bytes(u.mem_read(HW,0x24)),writes,calls,u.reg_read(UC_ARM_REG_PRIMASK),weak
rows=[]
bits=[0x100000,0x80,0x40,0x800000,0x1000000]
for mode,mask,primask,pointer,mutation,rx_pointer in itertools.product(['no_error_rx','disabled_error'],range(32),[0,1],[False,True],[False,True],[False,True]):
    isr=0
    for i,bit in enumerate(bits):
        if mask&(1<<i):isr|=bit
    cr1=0xc00000c0;cr3=0xc00000
    if mode=='no_error_rx':isr|=0x20;cr1|=0x20
    else:isr|=0x80f
    a=run(True,isr,cr1,cr3,primask,pointer,mutation,rx_pointer)
    b=run(False,isr,cr1,cr3,primask,pointer,mutation,rx_pointer)
    assert a[:5]==b[:5],(mode,hex(isr),primask,pointer,mutation,rx_pointer,[(i,x==y) for i,(x,y) in enumerate(zip(a,b))])
    expected_rx=1 if mode=='no_error_rx' and rx_pointer else 0
    assert a[3][:2]==(expected_rx,H if expected_rx else 0)
    rows.append({'mode':mode,'isr':isr,'cr1':cr1,'cr3':cr3,'primask':primask,'tx_pointer':pointer,'rx_pointer':rx_pointer,'rx_callback_mutation':mutation,'providers':a[3],'weak':a[5],'mmio_writes':a[2]})
out={'status':'PASS','cases':len(rows),'firmware_sha256':fw_hash,'source_sha256':hashlib.sha256((D/'rx_fallthrough.c').read_bytes()).hexdigest(),'fixture_sha256':hashlib.sha256((D/'rx_fallthrough_fixture.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'domain':'No-error RX-ready callback with mutation, or all-error flags and all error enables off falling through to mixed tail','rows':rows}
(D/'rx_fallthrough_results.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(rows),'RX/disabled-error fall-through public-entry fixtures')
