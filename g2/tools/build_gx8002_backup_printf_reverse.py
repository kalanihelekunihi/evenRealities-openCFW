# SPDX-License-Identifier: MIT
"""Place unchanged SDK reverse-output helper with size-qualified flags."""
import json,subprocess
from build_gx8002_backup_printf_candidate import build as candidate,ROOT,sha,Elf32
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA

def build():
    evidence=candidate();out=ROOT/'build/gx8002-backup-printf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');command=evidence['command'].copy();command.insert(1,'-fno-tree-loop-optimize');command[-1]=str(out/'reverse.o');subprocess.run(command,check=True)
    (out/'reverse.ld').write_text('SECTIONS { .printf_reverse 0x10008a04 : { *(.text._out_rev) } /DISCARD/ : { *(.text*) *(.rodata*) } }\n')
    path=out/'reverse.elf';subprocess.run([pre+'ld','-T',str(out/'reverse.ld'),str(out/'reverse.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'reverse');sec=next(s for s in elf.sections if s['name']=='.printf_reverse');data=elf.contents(sec);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;assert len(data)<=156
    assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'reverse.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream':evidence,'command':command,'bytes':len(data),'envelope_bytes':156,'byte_exact_prefix':data==stock[0x41344:0x41344+len(data)],'source_admitted':False,'limits':['Unmodified SDK reverse-output helper; callback remains caller-supplied. Decoded padding/index-wrap behavior and integration pending.']}
    (ROOT/'docs/research/gx8002-backup-printf-reverse.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print({k:v for k,v in build().items() if k not in ('upstream','command')})
