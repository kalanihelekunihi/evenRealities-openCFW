# SPDX-License-Identifier: MIT
"""Analysis-only link of compact clock text plus source-authored PLL table."""
import json
import subprocess
from probe_gx8002_clock_frequency_table_size import probe,ROOT,Elf32,sha
from link_gx8002_clock_frequency_candidate import link


def build():
    link();candidate=probe()
    out=ROOT/'build/gx8002-clock-frequency-table-probe'
    script=(ROOT/'build/gx8002-clock-frequency/frequency-analysis.ld').read_text()
    script=script.replace('/DISCARD/', '.rodata.subband_hz 0x11001000 : { *(.rodata.subband_hz.*) }\n/DISCARD/')
    (out/'analysis.ld').write_text(script)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(out/'analysis.ld'),str(out/'frequency.o'),'-o',str(out/'analysis.elf')],check=True)
    elf=Elf32((out/'analysis.elf').read_bytes(),'table probe')
    text=next(s for s in elf.sections if s['name']=='.text.open_cfw_gx8002_clock_frequency')
    table=next(s for s in elf.sections if s['name']=='.rodata.subband_hz')
    if text['size']!=444 or table['size']!=16 or elf.relocations(text['index']) or elf.relocations(table['index']):
        raise ValueError('Table probe section contract')
    (out/'analysis.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'analysis.elf')],text=True))
    return {'candidate':candidate,'linked_text_bytes':text['size'],'linked_text_sha256':sha(elf.contents(text)),
            'table_bytes':table['size'],'table_sha256':sha(elf.contents(table)),
            'analysis_table_address':table['address'],'source_admitted':False,
            'limits':['Analysis-only table and switch addresses; firmware table placement and whole-function decoded qualification pending.']}

if __name__=='__main__':
    report=build();(ROOT/'docs/research/gx8002-clock-frequency-table-link.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
