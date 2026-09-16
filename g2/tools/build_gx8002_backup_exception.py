# SPDX-License-Identifier: MIT
"""Build authenticated upstream backup exception handling, including its BSS."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32


def build():
    out=ROOT/'build/gx8002-backup-exception';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';evidence=[]
    for name in ('vectors.S','trap_c.c'):
        rel='arch/soc/grus/'+name
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        source=authenticated_blob(sdk/rel,blob)
        adapted=source.replace(b'#include <stdio.h>\n',b'').replace(b'#include <stdlib.h>\n',b'')
        (out/name).write_bytes(adapted)
        evidence.append({'path':rel,'blob':blob,'sha256':sha(source),'build_source_sha256':sha(adapted)})
    (out/'csi_config.h').write_text('/* No configuration used by exception sources. */\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    for name in ('vectors.S','trap_c.c'):
        subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-I',str(out),'-c',str(out/name),'-o',str(out/(name+'.o'))],check=True)
    (out/'exception.ld').write_text('''SECTIONS {
.trap_c 0x100031f0 : { *trap_c.c.o(.text) }
.exception 0x100031fc : { *vectors.S.o(.text) }
.trap_stack 0x20017090 (NOLOAD) : { *vectors.S.o(.bss) }
}
''')
    path=out/'exception.elf';subprocess.run([pre+'ld','-T',str(out/'exception.ld'),str(out/'trap_c.c.o'),str(out/'vectors.S.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'exception');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    rows=[]
    for name,offset,limit in (('.trap_c',0x3bb30,12),('.exception',0x3bb3c,80)):
        section=next(s for s in elf.sections if s['name']==name);body=elf.contents(section)
        assert len(body)<=limit and body==stock[offset:offset+len(body)]
        rows.append({'name':name,'bytes':len(body),'envelope_bytes':limit,'exact_stock_prefix':body==stock[offset:offset+len(body)]})
    stack=next(s for s in elf.sections if s['name']=='.trap_stack');assert stack['type']==8 and stack['size']==772
    symbols={s['name']:s['value'] for s in elf.symbols()}
    assert symbols['Default_Handler']==0x10003240 and symbols['g_top_trapstack']==symbols['g_trap_sp']==0x20017390
    (out/'exception.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream_commit':SDK_COMMIT,'sources':evidence,'sections':rows,'elf_sha256':sha(path.read_bytes()),'bss_bytes':772,'source_admitted':False,'limits':['Authentic existing terminal exception behavior, not a replacement for missing application code. Unused stdio.h/stdlib.h includes removed because diagnostics are preprocessor-disabled. Architecture frame execution pending; hardware unqualified.']}
    (ROOT/'docs/research/gx8002-backup-exception.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build())
