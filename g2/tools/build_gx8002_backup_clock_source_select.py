# SPDX-License-Identifier: MIT
"""Build source clock selector with its register helper inlined for backup layout."""
import json,subprocess
from build_gx8002_backup_cfft import IMAGE,IMAGE_SHA
from build_gx8002_clock_source_select_candidate import build as authenticate,ROOT,Elf32,sha


def build():
    evidence=authenticate();out=ROOT/'build/gx8002-backup-clock-source-select';out.mkdir(exist_ok=True)
    original=ROOT/'components/shared/gx8002/runtime_gx8002_clock_source_select.c'
    source=original.read_text().replace('__attribute__((noinline)) void open_cfw_clock_register_set','static inline __attribute__((always_inline)) void open_cfw_clock_register_set')
    (out/'source.c').write_text(source);sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*evidence['flags'],'-I'+str(ROOT/'build/gx8002-board/clock-source-select-config'),'-isystem',str(sdk/'arch/soc/grus/include'),'-isystem',str(sdk/'include'),'-isystem',str(sdk/'include/utility'),'-c',str(out/'source.c'),'-o',str(out/'source.o')],check=True)
    (out/'source.ld').write_text('SECTIONS { .text 0x100035a0 : { *(.text.open_cfw_gx8002_clock_source_select) } }\n')
    path=out/'source.elf';subprocess.run([pre+'ld','-T',str(out/'source.ld'),str(out/'source.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'source selector');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    size=next(s['size'] for s in elf.sections if s['name']=='.text');assert size<=32
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert elf.contents(next(s for s in elf.sections if s['name']=='.text'))==stock[0x3bee0:0x3bee0+size]
    (out/'source.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream_evidence':evidence,'source_sha256':sha(source.encode()),'elf_sha256':sha(path.read_bytes()),'bytes':size,'stock_byte_exact':True,'envelope_bytes':32,'source_admitted':False,'limits':['Source helper inlined to match backup call structure; shifts have C-defined behavior for offsets0..31 only. Decoded verification and firmware integration pending.']}
    (ROOT/'docs/research/gx8002-backup-clock-source-select.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['bytes'])
