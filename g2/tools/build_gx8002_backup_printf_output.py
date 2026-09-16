# SPDX-License-Identifier: MIT
"""Place authenticated SDK character callback at its backup-image entry."""
import json,subprocess
from build_gx8002_backup_printf_candidate import build as candidate,ROOT,sha,Elf32
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA

def build():
    evidence=candidate();out=ROOT/'build/gx8002-backup-printf';command=evidence['command'].copy();command.insert(1,'-fno-shrink-wrap');command[-1]=str(out/'output.o');subprocess.run(command,check=True)
    ld='SECTIONS { .printf_output 0x10009924 : { *(.text._out_char) } /DISCARD/ : { *(.text*) *(.rodata*) } }\n_putchar = 0x10009990;\n'
    (out/'output.ld').write_text(ld);pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');path=out/'output.elf';subprocess.run([pre+'ld','-T',str(out/'output.ld'),str(out/'output.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'output');section=next(s for s in elf.sections if s['name']=='.printf_output');data=elf.contents(section);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert len(data)<=16
    (out/'output.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream':evidence,'bytes':len(data),'envelope_bytes':16,'byte_exact_prefix':data==stock[0x42264:0x42264+len(data)],'source_admitted':False,'limits':['Character callback only; _putchar remains bound to stock wrapper. Formatter and console path not included.']}
    (ROOT/'docs/research/gx8002-backup-printf-output.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print({k:v for k,v in build().items() if k!='upstream'})
