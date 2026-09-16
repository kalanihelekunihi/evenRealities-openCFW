# SPDX-License-Identifier: MIT
"""Compile backup UART output with recovered polling and CRLF behavior."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-backup-uart-putc';out.mkdir(exist_ok=True);pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_uart_putc.c'
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-c',str(source),'-o',str(out/'putc.o')],check=True)
    (out/'putc.ld').write_text('SECTIONS { .uart_putc 0x100045a0 : { *(.text*) } }\nbackup_uart_descriptors = 0x20016b84;\n')
    path=out/'putc.elf';subprocess.run([pre+'ld','-T',str(out/'putc.ld'),str(out/'putc.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'putc');sec=next(s for s in elf.sections if s['name']=='.uart_putc');data=elf.contents(sec);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'putc.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'bytes':len(data),'envelope_bytes':56,'fits':len(data)<=56,'byte_exact_prefix':data==stock[0x3cee0:0x3cee0+len(data)],'source_admitted':False,'limits':['Recovered busy polling and CR before LF; no timeout introduced. Descriptor ownership, decoded behavior and integration pending.']}
    (ROOT/'docs/research/gx8002-backup-uart-putc.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
