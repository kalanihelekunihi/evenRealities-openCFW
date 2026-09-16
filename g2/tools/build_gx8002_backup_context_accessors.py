# SPDX-License-Identifier: MIT
"""Build context readers against source-owned header storage."""
import json,subprocess
from build_gx8002_backup_context_storage import build as storage_build,ROOT,sha,Elf32,FLAGS
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA


def build():
    evidence=storage_build();out=ROOT/'build/gx8002-backup-context-accessors';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_context_accessors.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-I',str(ROOT/'build/upstream-nationalchip-lvp-kws/include'),'-c',str(source),'-o',str(out/'accessors.o')],check=True)
    functions={'backup_pcm_frames_per_context':0x42890,'backup_pcm_frames_per_channel':0x428b4,'backup_pcm_sample_rate':0x428c0,'backup_context_count':0x428d0,'backup_microphone_count':0x428dc}
    ld='SECTIONS {\n'+''.join(f'.{name} {offset-0x38940+0x10000000:#x} : {{ *(.text.{name}) }}\n' for name,offset in functions.items())+'}\nbackup_context_header = 0x20017700;\n'
    (out/'accessors.ld').write_text(ld);path=out/'accessors.elf';subprocess.run([pre+'ld','-T',str(out/'accessors.ld'),str(out/'accessors.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'accessors');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    rows=[]
    for name,offset in functions.items():
        sec=next(s for s in elf.sections if s['name']=='.'+name);body=elf.contents(sec)
        assert len(body)==12 and body==stock[offset:offset+12]
        rows.append({'name':name,'package_offset':offset,'bytes':12,'exact_stock':True})
    assert len([s for s in elf.sections if s['flags']&2 and s['size']])==5
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    report={'storage_evidence':evidence,'source_sha256':sha(source.read_bytes()),'functions':rows,'source_admitted':False,'limits':['Exact stock reader bodies, symbolic header binding. Concurrent memory semantics and hardware remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-context-accessors.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['functions'])
