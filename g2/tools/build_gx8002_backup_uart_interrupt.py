# SPDX-License-Identifier: MIT
"""Build shared UART interrupt C and compare backup dispatch traces."""
import json,subprocess
from itertools import product
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_interrupt import execute
from build_gx8002_backup_uart_fifo import build as build_fifo


def build():
    out=ROOT/'build/gx8002-backup-uart-interrupt';out.mkdir(exist_ok=True)
    src=ROOT/'components/shared/gx8002/runtime_gx8002_uart_interrupt.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'interrupt.o'
    command=[pre+'gcc',*FLAGS,'-Os','-DOPEN_CFW_GX8002_BACKUP_RX_ORDER=1','-DOPEN_CFW_GX8002_BACKUP_SPLIT_TX=1','-c',str(src),'-o',str(obj)];subprocess.run(command,check=True)
    fifo_src=ROOT/'components/shared/gx8002/runtime_gx8002_uart_fifo_depth.c'
    fifo_obj=out/'fifo.o'
    subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(fifo_src),'-o',str(fifo_obj)],check=True)
    ld=out/'interrupt.ld';ld.write_text('''SECTIONS {
.text 0x10004250 : { *(.text.open_cfw_gx8002_uart_interrupt) }
.fifo 0x1000433c : { *(.text.open_cfw_gx8002_uart_fifo_depth) }
.tx 0x1000435c : { *(.text.uart_write_bytes*) }
}
ASSERT(SIZEOF(.text) <= 236, "interrupt overflow")
ASSERT(SIZEOF(.fifo) <= 32, "FIFO overflow")
ASSERT(SIZEOF(.tx) <= 72, "transmit helper overflow")
''')
    path=out/'interrupt.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),str(fifo_obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'UART interrupt');sec=next(s for s in elf.sections if s['name']=='.text')
    # The linker bounds every complete body; no generated instruction clipping.
    assert {x['name'] for x in elf.sections if x['flags'] & 2} == {'.text','.fifo','.tx'}
    fifo_evidence=build_fifo()
    fifo_path=ROOT/'build/gx8002-backup-uart-fifo/fifo.elf'
    assert sha(fifo_path.read_bytes())==fifo_evidence['elf_sha256']
    assert sha(fifo_src.read_bytes())==fifo_evidence['source_sha256']
    fifo_elf=Elf32(fifo_path.read_bytes(),'qualified FIFO')
    fifo_section=next(x for x in elf.sections if x['name']=='.fifo')
    prior_fifo=next(x for x in fifo_elf.sections if x['name']=='.text')
    assert fifo_section['address']==prior_fifo['address']
    assert elf.contents(fifo_section)==fifo_elf.contents(prior_fifo)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';oldelf=Elf32(wrapper.read_bytes(),'stock')
    assert oldelf.contents(next(s for s in oldelf.sections if s['name']=='.data'))==stock
    text=subprocess.check_output([pre+'objdump','-d',str(path)],text=True);(out/'interrupt.disassembly.txt').write_text(text)
    new=decode(text);old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x3cb90','--stop-address=0x3cc7c',str(wrapper)],text=True));count=0;differences=[]
    for pending,rxmode,txmode,dma,available,mutation in product(range(16),(0,1,3),(0,1,3),(0,1),(0,7,0xffffffff),(False,True)):
        base=0x20016b84;device=0xa0100000;other=0xa0200000
        d=[0x12340000+i for i in range(32)];d[0]=0;d[1]=device;d[11]=dma;d[16]=rxmode;d[17]=txmode;d[20]=0x10300000;d[18]=0x10300010
        regs={dev+offset:0xa5a50000+offset for dev in (device,other) for offset in range(0,256,4)}
        regs.update({device+8:pending,device+0x84:available,device+0x80:17,device+0xf4:0x00101234,other+0x80:0xffffffff,other+0xf4:0x00011234})
        def mutate(target,memory):
            if mutation and target==d[20]:
                memory[base+4]=other;memory[base]=1;memory[base+17*4]=1;memory[base+19*4]=0xabcd1234;memory[device+8]=0
        original=execute(old,0x3cb90,d,regs,mutate,descriptor_base=base)
        actual=execute(new,0x10004250,d,regs,mutate,descriptor_base=base)
        if original!=actual: differences.append({'inputs':[pending,rxmode,txmode,dma,available,mutation],'stock_trace':original[2],'source_trace':actual[2],'returns':[original[0],actual[0]],'memory_equal':original[1]==actual[1]})
        count+=1
    result={'source_sha256':sha(src.read_bytes()),'fifo_source_sha256':sha(fifo_src.read_bytes()),'fifo_matches_qualified_body':True,'fifo_evidence':fifo_evidence,'command':command,'elf_sha256':sha(path.read_bytes()),'stock_sha256':IMAGE_SHA,'code_bytes':sec['size'],'source_sections':[{'name':x['name'],'address':x['address'],'bytes':x['size']} for x in elf.sections if x['name'] in ('.text','.fifo','.tx')],'stock_envelope_bytes':236,'fits':sec['size']<=236,'dispatch_cases':count,'dispatch_differences':differences,'source_admitted':False,'limits':['Complete source cluster fits linker-enforced bounds; FIFO bytes match the separately qualified source body.','Helper placement reclaims part of the old FIFO envelope; incoming/computed references and firmware integration remain pending. Other verifier reports qualify buffered, mutation, count and stall cases against this ELF hash. Callback bodies and MMIO are modeled; no hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-uart-interrupt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['code_bytes'],r['dispatch_cases'],len(r['dispatch_differences']))
