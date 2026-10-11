"""TOIDLE/DMA precedence over simultaneous later IRQ families."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
fw_hash=hashlib.sha256(fw).hexdigest()
assert fw_hash=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
flags=['--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
sources=[D/'toidle_dma.c',D/'dma_fixture.c',R/'g2/components/case/source_candidate_20261010/uart_event_callback.c']
objects=[]
for source in sources:
    obj=D/(source.stem+'.o');objects.append(obj)
    subprocess.run(['clang',*flags,'-c',str(source),'-o',str(obj)],check=True)
(D/'dma_branch.ld').write_text('SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['arm-none-eabi-ld','-T',str(D/'dma_branch.ld'),*[str(x) for x in objects],'-o',str(D/'dma_branch.elf')],check=True)
with (D/'dma_branch.elf').open('rb') as f:
    e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
H=0x20002000;DMA=0x20003000;HW=0x40013800;CH=0x40014000;STOP=0x20000100
def run(stock,size,remaining,circular,primask,extra_cr1,extra_cr3,abort_result,later):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:])
    u.mem_map(0x00100000,0x10000)
    for a,b in seg:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x2000)
    u.mem_write(H,b'\xa5'*148);u.mem_write(H,struct.pack('<I',HW))
    u.mem_write(H+0x5c,struct.pack('<HH',size,0xa5a5))
    u.mem_write(H+0x6c,struct.pack('<II',1,0xa5a5a5a5))
    u.mem_write(H+0x74,struct.pack('<I',0x20004001))
    u.mem_write(H+0x80,struct.pack('<I',DMA))
    u.mem_write(H+0x8c,struct.pack('<II',0x22,0))
    u.mem_write(HW,struct.pack('<III',0x10|extra_cr1|0xc00000c0,0x12345678,0x40|extra_cr3|0xc00000))
    u.mem_write(HW+0x1c,struct.pack('<II',0x10|later,0xfeedface))
    u.mem_write(DMA,b'\xa5'*64);u.mem_write(DMA,struct.pack('<I',CH))
    u.mem_write(CH,struct.pack('<II',0x20 if circular else 0,remaining))
    u.mem_write(sym['case_dma_abort_result'],struct.pack('<I',abort_result))
    u.mem_write(sym['case_dma_abort_count'],bytes(4));u.mem_write(sym['case_dma_abort_argument'],bytes(4))
    u.reg_write(UC_ARM_REG_R0,H);u.reg_write(UC_ARM_REG_SP,0x20008000)
    u.reg_write(UC_ARM_REG_LR,STOP|1);u.reg_write(UC_ARM_REG_PRIMASK,primask)
    writes=[];events=[]
    def on_write(u,access,addr,width,value,data):
        if HW<=addr<HW+0x24:
            mask=u.reg_read(UC_ARM_REG_PRIMASK);writes.append((addr,width,value,mask))
            if addr in (HW,HW+8):assert mask==1,('atomic',stock,hex(addr),mask)
    def on_code(u,addr,width,data):
        if stock and addr==0x0800487a:
            u.reg_write(UC_ARM_REG_PC,sym['case_dma_abort']|1)
        elif addr==(0x08005e6a if stock else sym['HAL_UARTEx_RxEventCallback']&~1):
            events.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
    u.hook_add(UC_HOOK_MEM_WRITE,on_write);u.hook_add(UC_HOOK_CODE,on_code)
    u.emu_start(0x08005f51 if stock else sym['case_uart_toidle_dma_branch']|1,STOP,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x20008000
    provider=tuple(struct.unpack('<I',u.mem_read(sym[x],4))[0] for x in ('case_dma_abort_count','case_dma_abort_argument'))
    return (bytes(u.mem_read(H,148)),bytes(u.mem_read(HW,0x24)),bytes(u.mem_read(DMA,64)),bytes(u.mem_read(CH,8)),writes,events,provider,u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
for size,remaining,circular,primask,abort_result,later in itertools.product([1,8],[0,1,4],[0,1],[0,1],[0,1],[0,0x100000,0x80,0x40,0x1800000,0x19000c0]):
    a=run(True,size,remaining,circular,primask,0,0,abort_result,later)
    b=run(False,size,remaining,circular,primask,0,0,abort_result,later)
    assert a==b,(size,remaining,circular,primask,abort_result,hex(later),[(i,x==y) for i,(x,y) in enumerate(zip(a,b))])
    rows.append({'size':size,'remaining':remaining,'circular':circular,'primask':primask,'abort_result':abort_result,'later_isr':later,'events':a[5],'provider':a[6],'mmio_writes':a[4]})
out={'status':'PASS','cases':len(rows),'firmware_sha256':fw_hash,'source_sha256':hashlib.sha256((D/'toidle_dma.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256((D/'dma_branch.elf').read_bytes()).hexdigest(),'domain':'TOIDLE DMA with simultaneous enabled wakeup/TX-ready/TC/TXFE/RXFF later flags; common abort provider','rows':rows}
(D/'toidle_mixed_dma_results.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(rows),'TOIDLE mixed DMA public-entry fixtures')
