# SPDX-License-Identifier: MIT
"""Build recovered console forwarding at backup entries."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-backup-console-wrappers';out.mkdir(exist_ok=True);pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_console_wrappers.c'
    subprocess.run([pre+'gcc','-Os','-fno-inline','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-c',str(source),'-o',str(out/'wrappers.o')],check=True)
    (out/'wrappers.ld').write_text('SECTIONS { .console 0x10004818 : { *(.text.backup_console_putc) } .putchar 0x10009990 : { *(.text.backup_putchar) } }\nbackup_console_port = 0x2001739c;\nbackup_uart_putc = 0x100045a0;\n')
    path=out/'wrappers.elf';subprocess.run([pre+'ld','-T',str(out/'wrappers.ld'),str(out/'wrappers.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'wrappers');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    for name,offset,size in (('.console',0x3d158,20),('.putchar',0x422d0,8)):
        sec=next(s for s in elf.sections if s['name']==name);data=elf.contents(sec);assert len(data)<=size
        rows.append({'section':name,'bytes':len(data),'envelope':size,'byte_exact_prefix':data==stock[offset:offset+len(data)]})
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'wrappers.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'sections':rows,'source_admitted':False,'limits':['Recovered forwarding only; console-port storage and UART writer external. Integration pending.']}
    (ROOT/'docs/research/gx8002-backup-console-wrappers.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
