# SPDX-License-Identifier: MIT
"""Reuse source-authored UART defaults at backup placement and link putc."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS
from analyze_gx8002_upstream_objects import SDK_COMMIT,authenticated_blob
from build_gx8002_backup_uart_putc import build as putc_build


def build():
    out=ROOT/'build/gx8002-backup-uart-descriptors';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';headers=[]
    for rel in ('arch/soc/grus/include/base_addr.h','arch/soc/grus/include/soc.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        data=authenticated_blob(sdk/rel,blob);headers.append({'path':rel,'blob':blob,'sha256':sha(data)})
    source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_storage.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'descriptors.o'
    command=[pre+'gcc',*FLAGS,'-I',str(sdk/'arch/soc/grus/include'),'-c',str(source),'-o',str(obj)]
    subprocess.run(command,check=True)
    prior=putc_build()
    base=ROOT/'build/gx8002-backup-uart-putc'
    ld=out/'uart.ld';ld.write_text('SECTIONS { .uart_putc 0x100045a0 : { *putc.o(.text*) } .descriptors 0x20016b84 : { *(.data.open_cfw_gx8002_uart_descriptors) } }\nbackup_uart_descriptors = open_cfw_gx8002_uart_descriptors;\n')
    path=out/'uart.elf';subprocess.run([pre+'ld','-T',str(ld),str(base/'putc.o'),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'backup UART');old=Elf32((base/'putc.elf').read_bytes(),'putc')
    sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==2
    text=next(s for s in sections if s['name']=='.uart_putc')
    assert elf.contents(text)==old.contents(next(s for s in old.sections if s['name']=='.uart_putc'))
    table=next(s for s in sections if s['name']=='.descriptors');body=elf.contents(table)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert table['address']==0x20016b84 and len(body)==256 and body==stock[0x4f4c4:0x4f5c4]
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    result={'sdk_commit':SDK_COMMIT,'headers':headers,'source_sha256':sha(source.read_bytes()),'command':command,'elf_sha256':sha(path.read_bytes()),'putc_build':prior,'putc_unchanged':True,'descriptor_bytes':256,'descriptor_sha256':sha(body),'stock_sha256':IMAGE_SHA,'source_admitted':False,'limits':['All descriptor initial bytes generated from existing C defaults and pinned SDK constants. Runtime field semantics beyond known offsets remain incomplete.','Putc code unchanged; initialization/mutation consumers, references and integrated loader qualification pending.']}
    (ROOT/'docs/research/gx8002-backup-uart-descriptors.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build())
