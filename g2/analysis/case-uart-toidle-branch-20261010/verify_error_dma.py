"""Selected ORE/DMAR public-entry IRQ branch with abort callback continuation."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
fw_hash=hashlib.sha256(fw).hexdigest()
assert fw_hash=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
flags=['--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
objects=[]
for source in [D/'error_dma.c',D/'error_fixture.c']:
    obj=D/(source.stem+'.o');objects.append(obj)
    subprocess.run(['clang',*flags,'-c',str(source),'-o',str(obj)],check=True)
(D/'error_branch.ld').write_text('SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['arm-none-eabi-ld','-T',str(D/'error_branch.ld'),*[str(x) for x in objects],'-o',str(D/'error_branch.elf')],check=True)
with (D/'error_branch.elf').open('rb') as f:
    e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
H=0x20002000;DMA=0x20003000;HW=0x40013800;STOP=0x20000100
def run(stock,result,primask,reception,initial_error,cr1_extra,cr3_extra):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:])
    u.mem_map(0x00100000,0x10000)
    for a,b in seg:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000)
    u.mem_write(H,b'\xa5'*148);u.mem_write(H,struct.pack('<I',HW))
    u.mem_write(H+0x56,struct.pack('<H',7));u.mem_write(H+0x5e,struct.pack('<H',11))
    u.mem_write(H+0x6c,struct.pack('<I',reception));u.mem_write(H+0x74,bytes(4))
    u.mem_write(H+0x80,struct.pack('<I',DMA));u.mem_write(H+0x8c,struct.pack('<II',0x22,initial_error))
    u.mem_write(HW,struct.pack('<III',0x20|cr1_extra,0x12345678,0x40|cr3_extra))
    u.mem_write(HW+0x1c,struct.pack('<II',8,0xfeedface))
    u.mem_write(DMA,b'\xa5'*64);u.mem_write(DMA+0x28,struct.pack('<I',H))
    u.mem_write(sym['case_abort_it_result'],struct.pack('<I',result))
    u.mem_write(sym['case_abort_it_count'],bytes(4));u.mem_write(sym['case_abort_it_argument'],bytes(4))
    u.reg_write(UC_ARM_REG_R0,H);u.reg_write(UC_ARM_REG_SP,0x20008000)
    u.reg_write(UC_ARM_REG_LR,STOP|1);u.reg_write(UC_ARM_REG_PRIMASK,primask)
    writes=[];callbacks=[]
    def on_write(u,access,addr,width,value,data):
        if HW<=addr<HW+0x24:
            mask=u.reg_read(UC_ARM_REG_PRIMASK);writes.append((addr,width,value,mask))
            if addr in (HW,HW+8):assert mask==1,('atomic',stock,hex(addr),mask)
    def on_code(u,addr,width,data):
        if stock and addr==0x080048e6:
            u.reg_write(UC_ARM_REG_PC,sym['case_dma_abort_it']|1)
        elif addr==(0x080086e0 if stock else sym['case_dma_abort_on_error']&~1):
            callbacks.append(u.reg_read(UC_ARM_REG_R0))
    u.hook_add(UC_HOOK_MEM_WRITE,on_write);u.hook_add(UC_HOOK_CODE,on_code)
    u.emu_start(0x08005f51 if stock else sym['case_uart_error_dma_branch']|1,STOP,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x20008000
    dma=bytearray(u.mem_read(DMA,64))
    callback_ptr=struct.unpack_from('<I',dma,0x38)[0]
    expected=0x080086e1 if stock else sym['case_dma_abort_on_error']|1
    assert callback_ptr==expected,(stock,hex(callback_ptr),hex(expected))
    dma[0x38:0x3c]=b'CALL'  # compare semantic callback identity separately
    provider=tuple(struct.unpack('<I',u.mem_read(sym[x],4))[0] for x in ('case_abort_it_count','case_abort_it_argument'))
    return bytes(u.mem_read(H,148)),bytes(u.mem_read(HW,0x24)),bytes(dma),writes,callbacks,provider,u.reg_read(UC_ARM_REG_PRIMASK)
rows=[]
for result,primask,reception,error,cr1,cr3 in itertools.product([0,1],[0,1],[0,1],[0,4],[0,0x110],[0,0x10000001]):
    a=run(True,result,primask,reception,error,cr1,cr3)
    b=run(False,result,primask,reception,error,cr1,cr3)
    assert a==b,(result,primask,reception,error,hex(cr1),hex(cr3),[(i,x==y) for i,(x,y) in enumerate(zip(a,b))])
    rows.append({'abort_result':result,'primask':primask,'reception':reception,'initial_error':error,'cr1_extra':cr1,'cr3_extra':cr3,'callbacks':a[4],'provider':a[5],'mmio_writes':a[3]})
out={'status':'PASS','cases':len(rows),'firmware_sha256':fw_hash,'source_sha256':hashlib.sha256((D/'error_dma.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256((D/'error_branch.elf').read_bytes()).hexdigest(),'domain':'ORE enabled, DMAR set, nonnull DMA, no RX-ready; HAL_DMA_Abort_IT common compiled fixture provider; stock/source callback bodies execute','rows':rows}
(D/'error_dma_results.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(rows),'error/DMAR public-entry stock/source fixtures')
