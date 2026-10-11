"""Original vs bounded source TOIDLE/no-DMA public-entry branch comparison."""
from pathlib import Path
import hashlib, itertools, json, struct, subprocess
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_PRIMASK
from elftools.elf.elffile import ELFFile

D = Path(__file__).resolve().parent
R = D.parents[2]
fw = (R / 'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
fw_hash = hashlib.sha256(fw).hexdigest()
assert fw_hash == '36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(D/'toidle_no_dma.c'),'-o',str(D/'toidle.o')], check=True)
subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(R/'g2/components/case/source_candidate_20261010/uart_event_callback.c'),'-o',str(D/'event.o')], check=True)
(D/'branch.ld').write_text('SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['arm-none-eabi-ld','-T',str(D/'branch.ld'),str(D/'toidle.o'),str(D/'event.o'),'-o',str(D/'branch.elf')], check=True)
with (D/'branch.elf').open('rb') as f:
    e=ELFFile(f)
    seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}

H=0x20002000; HW=0x40013800; STOP=0x20000100
def run(stock, size, count, primask, extra_cr1, extra_cr3):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:])
    u.mem_map(0x00100000,0x10000)
    for a,b in seg:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000)
    u.mem_write(H,b'\xa5'*148);u.mem_write(H,struct.pack('<I',HW))
    u.mem_write(H+0x5c,struct.pack('<HH',size,count))
    u.mem_write(H+0x6c,struct.pack('<II',1,0xa5a5a5a5))
    u.mem_write(H+0x74,struct.pack('<I',0x20004001))
    u.mem_write(H+0x8c,struct.pack('<II',0x22,0))
    u.mem_write(HW,struct.pack('<III',0x10|extra_cr1,0x12345678,extra_cr3))
    u.mem_write(HW+0x1c,struct.pack('<II',0x10,0xfeedface))
    u.reg_write(UC_ARM_REG_R0,H);u.reg_write(UC_ARM_REG_SP,0x20008000)
    u.reg_write(UC_ARM_REG_LR,STOP|1);u.reg_write(UC_ARM_REG_PRIMASK,primask)
    writes=[];events=[]
    def on_write(u, access, addr, width, value, data):
        if HW<=addr<HW+0x24:
            mask=u.reg_read(UC_ARM_REG_PRIMASK)
            writes.append((addr,width,value,mask))
            if addr in (HW,HW+8):assert mask==1,('atomic',stock,hex(addr),mask)
    def on_code(u,addr,width,data):
        if addr==(0x08005e6a if stock else sym['HAL_UARTEx_RxEventCallback'] & ~1):
            events.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
    u.hook_add(UC_HOOK_MEM_WRITE,on_write);u.hook_add(UC_HOOK_CODE,on_code)
    u.emu_start(0x08005f51 if stock else sym['case_uart_toidle_no_dma_branch']|1,STOP,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    assert u.reg_read(UC_ARM_REG_SP)==0x20008000
    return (bytes(u.mem_read(H,148)),bytes(u.mem_read(HW,0x24)),writes,events,u.reg_read(UC_ARM_REG_PRIMASK))

rows=[]
for size,count,primask,cr1,cr3 in itertools.product([0,1,8,0xffff],[0,1,4,0xffff],[0,1],[0,0x100,0x20,0x120],[0,1,0x10000000,0x10000001]):
    if cr1 & 0x20:continue  # source domain: no RX-ready enabled (ISR lacks RXNE anyway)
    got=run(False,size,count,primask,cr1,cr3)
    want=run(True,size,count,primask,cr1,cr3)
    assert got==want,(size,count,primask,hex(cr1),hex(cr3),[(i,a==b) for i,(a,b) in enumerate(zip(got,want))])
    rows.append({'size':size,'remaining':count,'primask':primask,'cr1_extra':cr1,'cr3_extra':cr3,'events':got[3],'mmio_writes':got[2]})
out={'status':'PASS','cases':len(rows),'firmware_sha256':fw_hash,'source_sha256':hashlib.sha256((D/'toidle_no_dma.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256((D/'branch.elf').read_bytes()).hexdigest(),'domain':'TOIDLE, ISR.IDLE and CR1.IDLEIE set, no errors, no DMAR, mapped synthetic handle/MMIO; source is a selected branch, not full IRQ','rows':rows}
(D/'results.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(rows),'TOIDLE/no-DMA public-entry stock/source fixtures')
