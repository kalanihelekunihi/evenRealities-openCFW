# SPDX-License-Identifier: MIT
"""Build recovered LVP allocation wrappers; allocator remains an explicit dependency."""
import json,subprocess
from build_gx8002_buffer_initialize import build as authenticate,ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS


def build():
    evidence=authenticate();out=ROOT/'build/gx8002-backup-heap-wrappers';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_heap_wrappers.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'wrappers.o')],check=True)
    functions=[('backup_heap_initialize',0x42850,28),('backup_allocate',0x4286c,8),('backup_callocate',0x42874,8),('backup_reallocate',0x4287c,8),('backup_free',0x42884,12)]
    bindings={'rt_system_heap_init':0x42384,'rt_malloc':0x423f8,'rt_calloc':0x4254c,'rt_realloc':0x425e4,'rt_free':0x4256c}
    ld='SECTIONS {\n'+''.join(f'.{name} {offset-0x38940+0x10000000:#x} : {{ *(.text.{name}) }}\n' for name,offset,size in functions)+'}\n'+''.join(f'{name} = {offset-0x38940+0x10000000:#x};\n' for name,offset in bindings.items())
    (out/'wrappers.ld').write_text(ld);path=out/'wrappers.elf';subprocess.run([pre+'ld','-T',str(out/'wrappers.ld'),str(out/'wrappers.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'heap wrappers');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    rows=[]
    for name,offset,size in functions:
        sec=next(s for s in elf.sections if s['name']=='.'+name);body=elf.contents(sec)
        assert len(body)<=size
        rows.append({'name':name,'bytes':len(body),'envelope_bytes':size,'exact_stock_prefix':body==stock[offset:offset+len(body)]})
    assert len([s for s in elf.sections if s['flags']&2 and s['size']])==5
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'wrappers.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream_evidence':evidence,'source_sha256':sha(source.read_bytes()),'functions':rows,'bindings_package_offsets':bindings,'heap_interval':[0x2001bb80,0x2002cb80],'source_admitted':False,'limits':['Only wrappers reconstructed. Allocator bodies and heap ownership still unresolved; source-only firmware incomplete.']}
    (ROOT/'docs/research/gx8002-backup-heap-wrappers.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['functions'])
