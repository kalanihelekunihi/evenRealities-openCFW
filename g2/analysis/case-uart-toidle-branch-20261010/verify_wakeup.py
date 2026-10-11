"""Selected wakeup branch from complete stock public IRQ entry."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
fw_hash=hashlib.sha256(fw).hexdigest()
assert fw_hash=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
obj=D/'wakeup.o';elf=D/'wakeup.elf';ld=D/'wakeup.ld'
subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(D/'wakeup.c'),'-o',str(obj)],check=True)
ld.write_text('SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
with elf.open('rb') as f:
    e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
H=0x20002000;HW=0x40013800;STOP=0x20000100
def run(stock,isr,cr3,primask):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:])
    u.mem_map(0x00100000,0x10000)
    for a,b in seg:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000)
    u.mem_write(H,b'\xa5'*148);u.mem_write(H,struct.pack('<I',HW))
    u.mem_write(H+0x6c,struct.pack('<I',0));u.mem_write(H+0x74,bytes(8))
    u.mem_write(H+0x8c,struct.pack('<II',0x22,0))
    u.mem_write(HW,struct.pack('<III',0,0x12345678,cr3));u.mem_write(HW+0x1c,struct.pack('<II',isr,0xfeedface))
    u.reg_write(UC_ARM_REG_R0,H);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,STOP|1);u.reg_write(UC_ARM_REG_PRIMASK,primask)
    writes=[];calls=[]
    def on_write(u,access,addr,width,value,data):
        if HW<=addr<HW+0x24:writes.append((addr,width,value,u.reg_read(UC_ARM_REG_PRIMASK)))
    def on_code(u,addr,width,data):
        if stock and addr==0x08005efe:calls.append(u.reg_read(UC_ARM_REG_R0))
    u.hook_add(UC_HOOK_MEM_WRITE,on_write);u.hook_add(UC_HOOK_CODE,on_code)
    u.emu_start(0x08005f51 if stock else sym['case_uart_wakeup_branch']|1,STOP,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x20008000
    return bytes(u.mem_read(H,148)),bytes(u.mem_read(HW,0x24)),writes,calls,u.reg_read(UC_ARM_REG_PRIMASK)
rows=[]
for isr,cr3,primask in itertools.product([0,0x100000,0x100000|0x10,0x100000|0x80,0x100000|0x90],[0,0x400000,0x400001,0x1400000],[0,1]):
    # Other flags in this domain have no corresponding enable bits.
    a=run(True,isr,cr3,primask);b=run(False,isr,cr3,primask)
    assert a[:3]+a[4:]==b[:3]+b[4:],(hex(isr),hex(cr3),primask,[(i,x==y) for i,(x,y) in enumerate(zip(a,b))])
    assert a[3]==([H] if isr&0x100000 and cr3&0x400000 else [])
    rows.append({'isr':isr,'cr3':cr3,'primask':primask,'weak_callback':a[3],'mmio_writes':a[2]})
out={'status':'PASS','cases':len(rows),'firmware_sha256':fw_hash,'source_sha256':hashlib.sha256((D/'wakeup.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'domain':'No enabled error/RX/IDLE/TX; wakeup flag/enable and disabled IDLE/TXE flags; fixed-image weak no-op callback','rows':rows}
(D/'wakeup_results.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(rows),'wakeup public-entry fixtures')
