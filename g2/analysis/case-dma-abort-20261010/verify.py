"""Original/source CASE DMA abort and abort_IT complete-body RAM comparison."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();fw_hash=hashlib.sha256(fw).hexdigest()
assert fw_hash=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
flags=['--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror']
objects=[]
for name in ('dma_abort','callback'):
    obj=D/(name+'.o');objects.append(obj)
    source=(R/'g2/components/case/source_candidate_20261010/dma_abort_provider.c') if name=='dma_abort' else D/'callback.c'
    subprocess.run(['clang',*flags,'-c',str(source),'-o',str(obj)],check=True)
ld=D/'dma_abort.ld';elf=D/'dma_abort.elf'
ld.write_text('SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
subprocess.run(['arm-none-eabi-ld','-T',str(ld),*[str(x) for x in objects],'-o',str(elf)],check=True)
with elf.open('rb') as f:
    e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
DMA=0x20002000;MMIO=0x40014000;STOP=0x20000100
ptrs={0:MMIO,0x40:MMIO+0x40,0x48:MMIO+0x20,0x4c:MMIO+0x60,0x54:MMIO+0x80,0x58:MMIO+0xa0}
def run(stock,kind,state,mux,callback,lock,shift,null):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:]);u.mem_map(0x00100000,0x10000)
    for a,b in seg:u.mem_write(a,b)
    u.mem_map(0x20000000,0x10000);u.mem_map(MMIO,0x1000)
    u.mem_write(DMA,b'\xa5'*96)
    for offset,ptr in ptrs.items():u.mem_write(DMA+offset,struct.pack('<I',ptr if offset!=0x54 or mux else 0))
    u.mem_write(DMA+0x24,bytes([lock,state]))
    u.mem_write(DMA+0x38,struct.pack('<I',sym['case_abort_callback']|1 if callback else 0))
    u.mem_write(DMA+0x44,struct.pack('<I',shift))
    u.mem_write(DMA+0x50,struct.pack('<I',0x12345678))
    u.mem_write(DMA+0x5c,struct.pack('<I',0x87654321))
    for off in (0,0x20,0x40,0x60,0x80,0xa0):u.mem_write(MMIO+off,struct.pack('<II',0xffffffff,0xfedcba98))
    u.mem_write(sym['case_abort_callback_count'],bytes(4));u.mem_write(sym['case_abort_callback_arg'],bytes(4))
    u.reg_write(UC_ARM_REG_R0,0 if null else DMA);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    writes=[]
    def on_write(u,access,addr,width,value,data):
        if MMIO<=addr<MMIO+0xc0:writes.append((addr,width,value))
    u.hook_add(UC_HOOK_MEM_WRITE,on_write)
    entry=(0x0800487b if kind=='sync' else 0x080048e7) if stock else sym['case_dma_abort' if kind=='sync' else 'case_dma_abort_it']|1
    u.emu_start(entry,STOP,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==0x20008000
    calls=tuple(struct.unpack('<I',u.mem_read(sym[x],4))[0] for x in ('case_abort_callback_count','case_abort_callback_arg'))
    return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(DMA,96)),bytes(u.mem_read(MMIO,0xc0)),writes,calls
rows=[]
for kind,state,mux,callback,lock,shift in itertools.product(['sync','it'],[0,1,2,3],[False,True],[False,True],[0,1],[0,4,28]):
    a=run(True,kind,state,mux,callback,lock,shift,False);b=run(False,kind,state,mux,callback,lock,shift,False)
    assert a==b,(kind,state,mux,callback,lock,shift,[(i,x==y) for i,(x,y) in enumerate(zip(a,b))])
    rows.append({'kind':kind,'state':state,'mux':mux,'callback':callback,'lock':lock,'shift':shift,'return':a[0],'mmio_writes':a[3],'callback_state':a[4]})
for state in (0,2):
    a=run(True,'sync',state,False,False,0,0,True);b=run(False,'sync',state,False,False,0,0,True)
    assert a==b,('sync_null',state)
    rows.append({'kind':'sync_null','state':state,'return':a[0],'mmio_writes':a[3],'callback_state':a[4]})
out={'status':'PASS','cases':len(rows),'firmware_sha256':fw_hash,'source_sha256':hashlib.sha256((R/'g2/components/case/source_candidate_20261010/dma_abort_provider.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'domain':'Archive source compiled at -Os versus full stock sync/IT abort bodies with synthetic coherent DMA/MMIO state, optional mux and common callback; IT null excluded','rows':rows}
(D/'results.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(rows),'DMA abort sync/IT original-source fixtures')
