# SPDX-License-Identifier: MIT
"""Reuse recovered UART initializer at backup addresses with symbolic data."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS


def build():
    out=ROOT/'build/gx8002-backup-uart-initialize';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_initialize.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'initialize.o'
    command=[pre+'gcc',*FLAGS,'-Os','-c',str(source),'-o',str(obj)]
    subprocess.run(command,check=True)
    base=ROOT/'build/gx8002-backup-uart-descriptors';prior=json.loads((ROOT/'docs/research/gx8002-backup-uart-descriptors.json').read_text())
    assert sha((base/'uart.elf').read_bytes())==prior['elf_sha256']
    ld=out/'initialize.ld';delta=0x10003000-0x3b940
    bindings={'open_cfw_gx8002_platform_gate':0x3c528,'open_cfw_gx8002_clock_frequency':0x3c630,'open_cfw_gx8002_uart_configure':0x3cce4}
    ld.write_text('SECTIONS { .init 0x1000451c : { *(.text.open_cfw_gx8002_uart_initialize) } .descriptors 0x20016b84 : { *(.data.open_cfw_gx8002_uart_descriptors) } }\n'+''.join(f'{name} = {offset+delta:#x};\n' for name,offset in bindings.items()))
    path=out/'initialize.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),str(base/'descriptors.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'initializer');old=Elf32((base/'uart.elf').read_bytes(),'descriptors')
    section=next(s for s in elf.sections if s['name']=='.init');body=elf.contents(section)
    table=next(s for s in elf.sections if s['name']=='.descriptors')
    assert elf.contents(table)==old.contents(next(s for s in old.sections if s['name']=='.descriptors'))
    assert section['size']<=104
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    (out/'initialize.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'source_sha256':sha(source.read_bytes()),'command':command,'elf_sha256':sha(path.read_bytes()),'code_bytes':len(body),'stock_envelope_bytes':104,'stock_identical':body==stock[0x3ce5c:0x3ce5c+len(body)],'descriptor_evidence':prior,'external_bindings':bindings,'source_admitted':False,'limits':['Complete shared initializer linked with source descriptors; platform gate, clock and UART configuration are absolute targets requiring dependency qualification.','Clock-rounding boundaries, ordered calls/state writes, references and integration pending.']}
    (ROOT/'docs/research/gx8002-backup-uart-initialize.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['code_bytes'],r['stock_identical'],r['elf_sha256'])
