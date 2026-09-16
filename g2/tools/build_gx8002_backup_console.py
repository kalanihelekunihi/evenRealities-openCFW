# SPDX-License-Identifier: MIT
"""Build recovered console wrappers using authenticated upstream declarations."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS
from analyze_gx8002_upstream_objects import SDK_COMMIT,authenticated_blob


def build():
    out=ROOT/'build/gx8002-backup-console';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='include/driver/gx_uart.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    header=authenticated_blob(sdk/rel,blob).decode()
    declarations=['int gx_uart_init(int port, uint32_t baudrate);','void gx_uart_putc(int port, int ch);','int gx_console_init(int port, uint32_t baudrate);','void gx_console_putc(int ch);']
    assert all(d in header for d in declarations)
    (out/'console_upstream_declarations.h').write_text('#include <stdint.h>\n'+'\n'.join(declarations)+'\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_console.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj=out/'console.o';cmd=[pre+'gcc',*FLAGS,'-Os','-I',str(out),'-c',str(source),'-o',str(obj)]
    subprocess.run(cmd,check=True)
    delta=0x10003000-0x3b940
    ld=out/'console.ld';ld.write_text('SECTIONS { .init 0x10004808 : { *(.text.gx_console_init) } .putc 0x10004818 : { *(.text.gx_console_putc) } .port 0x2001739c (NOLOAD) : { *(.bss.backup_console_port) } }\n'+f'gx_uart_init = {0x3ce5c+delta:#x}; gx_uart_putc = {0x3cee0+delta:#x};\n')
    path=out/'console.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'console');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    sections=[]
    for name,offset,size in [('.init',0x3d148,16),('.putc',0x3d158,20)]:
        sec=next(s for s in elf.sections if s['name']==name);body=elf.contents(sec)
        assert sec['size']<=size and sec['address']==offset+delta
        sections.append({'name':name,'offset':offset,'bytes':len(body),'stock_envelope_bytes':size,'stock_identical':body==stock[offset:offset+len(body)]})
    state=next(s for s in elf.sections if s['name']=='.port');assert state['type']==8 and state['size']==4
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    (out/'console.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'sdk_commit':SDK_COMMIT,'header_path':rel,'header_blob':blob,'header_sha256':sha(header.encode()),'source_sha256':sha(source.read_bytes()),'command':cmd,'elf_sha256':sha(path.read_bytes()),'sections':sections,'source_admitted':False,'limits':['Complete console wrappers and symbolic BSS port; UART targets are absolute retained-function bindings, not a closed source implementation.','Decoded call/state behavior, incoming references and integration pending. No state relocation.']}
    (ROOT/'docs/research/gx8002-backup-console.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['sections'])
