"""Combined public-entry stock/source RAM-fixture matrix for one C handler."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();fw_hash=hashlib.sha256(fw).hexdigest()
assert fw_hash=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
names=['irq_unified.c','error_dma.c','error_fixture.c','toidle_dma.c','toidle_no_dma.c','dma_fixture.c','mixed_tail.c','tx_ready_fixture.c','tx_complete_fixture.c','rx_fallthrough_fixture.c']
sources=[D/n for n in names]+[R/'g2/components/case/source_candidate_20261010/uart_event_callback.c']
objects=[];flags=['--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
for source in sources:
    obj=D/(source.stem+'.o');objects.append(obj)
    subprocess.run(['clang',*flags,'-c',str(source),'-o',str(obj)],check=True)
ld=D/'irq_unified.ld';elf=D/'irq_unified.elf'
ld.write_text('SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['arm-none-eabi-ld','-T',str(ld),*[str(x) for x in objects],'-o',str(elf)],check=True)
with elf.open('rb') as f:
    e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
H=0x20002000;DMA=0x20003000;HW=0x40013800;CH=0x40014000;STOP=0x20000100
def run(stock,case):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:]);u.mem_map(0x00100000,0x10000)
    for a,b in seg:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x2000)
    u.mem_write(H,b'\xa5'*148);u.mem_write(H,struct.pack('<I',HW))
    u.mem_write(H+0x5c,struct.pack('<HH',case['size'],case['count']))
    u.mem_write(H+0x6c,struct.pack('<I',case['reception']))
    rx=sym['case_rx_tail_callback'] if case['rx']=='tail' else sym['case_rx_mutate']
    u.mem_write(H+0x74,struct.pack('<I',rx|1 if case['rx'] else 0))
    u.mem_write(H+0x78,struct.pack('<I',sym['case_tx_ready_callback']|1))
    u.mem_write(H+0x80,struct.pack('<I',DMA if case['dma_ptr'] else 0))
    u.mem_write(H+0x8c,struct.pack('<II',0x22,case['initial_error']))
    u.mem_write(HW,struct.pack('<III',case['cr1'],0x12345678,case['cr3']))
    u.mem_write(HW+0x1c,struct.pack('<II',case['isr'],0xfeedface))
    u.mem_write(DMA,b'\xa5'*64);u.mem_write(DMA,struct.pack('<I',CH));u.mem_write(DMA+0x28,struct.pack('<I',H))
    u.mem_write(CH,struct.pack('<II',0x20 if case['circular'] else 0,case['remaining']))
    for name in ('case_dma_abort_count','case_dma_abort_argument','case_abort_it_count','case_abort_it_argument','case_rx_count','case_rx_tail_calls','case_rx_tail_arg','case_tx_calls','case_tx_arg','case_tx_complete_calls','case_tx_complete_arg','case_tx_cr1_xor','case_tx_pointer_xor','case_rx_tail_mutation','case_rx_mutation','case_rx_cr3_mutation'):
        u.mem_write(sym[name],bytes(4))
    u.mem_write(sym['case_dma_abort_result'],struct.pack('<I',case['abort']))
    u.mem_write(sym['case_abort_it_result'],struct.pack('<I',case['abort']))
    u.mem_write(sym['case_rx_tail_mutation'],struct.pack('<I',case['mutate']))
    u.mem_write(sym['case_rx_cr3_mutation'],struct.pack('<I',0x40 if case['mutate'] else 0))
    u.reg_write(UC_ARM_REG_R0,H);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,STOP|1);u.reg_write(UC_ARM_REG_PRIMASK,case['primask'])
    writes=[];events=[];callbacks=[]
    def on_write(u,access,addr,width,value,data):
        if HW<=addr<HW+0x24:writes.append((addr,width,value,u.reg_read(UC_ARM_REG_PRIMASK)))
    def on_code(u,addr,width,data):
        if stock and addr==0x0800487a:u.reg_write(UC_ARM_REG_PC,sym['case_dma_abort']|1)
        elif stock and addr==0x080048e6:u.reg_write(UC_ARM_REG_PC,sym['case_dma_abort_it']|1)
        elif stock and addr==0x08006776:u.reg_write(UC_ARM_REG_PC,sym['case_tx_complete_provider']|1)
        elif addr==(0x08005e6a if stock else sym['HAL_UARTEx_RxEventCallback']&~1):events.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
        elif addr==(0x080086e0 if stock else sym['case_dma_abort_on_error']&~1):callbacks.append(u.reg_read(UC_ARM_REG_R0))
    u.hook_add(UC_HOOK_MEM_WRITE,on_write);u.hook_add(UC_HOOK_CODE,on_code)
    u.emu_start(0x08005f51 if stock else sym['case_uart_irq_unified']|1,STOP,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x20008000
    dma=bytearray(u.mem_read(DMA,64));ptr=struct.unpack_from('<I',dma,0x38)[0]
    if ptr!=0xa5a5a5a5:
        assert ptr==(0x080086e1 if stock else sym['case_dma_abort_on_error']|1)
        dma[0x38:0x3c]=b'CALL'
    counters=tuple(struct.unpack('<I',u.mem_read(sym[x],4))[0] for x in ('case_dma_abort_count','case_dma_abort_argument','case_abort_it_count','case_abort_it_argument','case_rx_count','case_rx_tail_calls','case_rx_tail_arg','case_tx_calls','case_tx_arg','case_tx_complete_calls','case_tx_complete_arg'))
    return bytes(u.mem_read(H,148)),bytes(u.mem_read(HW,0x24)),bytes(dma),bytes(u.mem_read(CH,8)),writes,events,callbacks,counters,u.reg_read(UC_ARM_REG_PRIMASK)
cases=[]
def add(kind,isr,cr1,cr3,**kw):
    c=dict(kind=kind,isr=isr,cr1=cr1,cr3=cr3,size=8,count=4,reception=0,dma_ptr=True,circular=False,remaining=4,rx=None,initial_error=0,abort=0,mutate=0,primask=0)
    c.update(kw);cases.append(c)
tailflags=[0,0x100000,0x80,0x40,0x800000,0x1000000,0x19000c0]
for f,pm in itertools.product(tailflags,[0,1]):
    add('tail',f,0xc00000c0,0xc00000,primask=pm)
    add('noerror_rx',f|0x20,0xc00000e0,0xc00000,rx='tail',mutate=1,primask=pm)
    add('disabled_error',f|0x80f,0xc00000c0,0xc00000,primask=pm)
    add('enabled_error',f|8,0xc00000e0,0xc00040,rx='error',mutate=1,primask=pm)
for f,dm,rem,circ,pm in itertools.product(tailflags,[0,1],[0,4],[0,1],[0,1]):
    add('toidle',f|0x10,0xc00000d0,0xc00000|(0x40 if dm else 0),reception=1,remaining=rem,circular=bool(circ),primask=pm)
tailbits=[0x100000,0x80,0x40,0x800000,0x1000000]
enables=[(0,0),(0x40,0),(0x80,0),(0,0x800000),(0,0x400000),(0x40000000,0),(0x80000000,0),(0xc00000c0,0xc00000)]
for mask,(cr1,cr3),pm in itertools.product(range(32),enables,[0,1]):
    f=sum(bit for i,bit in enumerate(tailbits) if mask&(1<<i))
    add('tail_exhaustive',f,cr1,cr3,primask=pm)
for flag,rx,mut,abort,pm in itertools.product(range(1,32),[0,0x20],[0,1],[0,1],[0,1]):
    isr=sum(bit for i,bit in enumerate([1,2,4,8,0x800]) if flag&(1<<i))|rx|0x19000d0
    add('error_exhaustive',isr,0xc40001f0,0x10c00041,rx='error',mutate=mut,abort=abort,primask=pm)
for mask,dm,rem,circ,pm in itertools.product([0,0x19000c0],[0,1],[0,1,4,8,9],[0,1],[0,1]):
    add('toidle_edges',mask|0x10,0xc00000d0,0xc00000|(0x40 if dm else 0),size=8,count=rem,reception=1,remaining=rem,circular=bool(circ),primask=pm)
for dma_ptr,abort,pm in itertools.product([False,True],[0,1],[0,1]):
    add('error_null_dma',8,0x20,0x40,rx='error',dma_ptr=dma_ptr,abort=abort,primask=pm)
for c in cases:
    a=run(True,c);b=run(False,c)
    assert a==b,(c,[(i,x==y) for i,(x,y) in enumerate(zip(a,b))])
out={'status':'PASS','cases':len(cases),'firmware_sha256':fw_hash,'source_sha256':hashlib.sha256((D/'irq_unified.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'domain':'One compiled public-entry C handler across tail, RX, disabled/enabled error and TOIDLE DMA/no-DMA with simultaneous later flags; explicit lower fixture providers','case_kinds':{kind:sum(c['kind']==kind for c in cases) for kind in sorted(set(c['kind'] for c in cases))}}
(D/'irq_unified_results.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(cases),'unified public-entry stock/source fixtures')
