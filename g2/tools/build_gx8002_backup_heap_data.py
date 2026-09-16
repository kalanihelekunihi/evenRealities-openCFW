# SPDX-License-Identifier: MIT
"""Compile allocator state and diagnostic strings as source-owned objects."""
import json,subprocess
from build_gx8002_backup_heap_initialize import build as initialize_build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32


def build():
    evidence=initialize_build();out=ROOT/'build/gx8002-backup-heap-data';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_heap_data.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-c',str(source),'-o',str(out/'heap-data.o')],check=True)
    (out/'data.ld').write_text('''SECTIONS {
.heap_state 0x200176dc (NOLOAD) : { *(.bss.backup_heap_state) }
.heap_message_initialize 0x100131ac : { *(.heap_message.initialize) }
.heap_message_invalid 0x100131d8 : { *(.heap_message.invalid) }
.heap_message_malloc_align 0x10013214 : { *(.heap_message.malloc_align) }
.heap_message_malloc_large 0x10013238 : { *(.heap_message.malloc_large) }
.heap_message_realloc_large 0x100132a0 : { *(.heap_message.realloc_large) }
.heap_message_free_range 0x10013244 : { *(.heap_message.free_range) }
.heap_message_free_invalid 0x10013254 : { *(.heap_message.free_invalid) }
.heap_message_free_details 0x10013270 : { *(.heap_message.free_details) }
}
''')
    path=out/'data.elf';subprocess.run([pre+'ld','-T',str(out/'data.ld'),str(out/'heap-data.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'heap data');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    state=next(s for s in elf.sections if s['name']=='.heap_state');assert state['type']==8 and state['size']==24
    rows=[]
    for name,address in (('.heap_message_initialize',0x100131ac),('.heap_message_invalid',0x100131d8),('.heap_message_free_range',0x10013244),('.heap_message_free_invalid',0x10013254),('.heap_message_free_details',0x10013270),('.heap_message_malloc_align',0x10013214),('.heap_message_malloc_large',0x10013238),('.heap_message_realloc_large',0x100132a0)):
        sec=next(s for s in elf.sections if s['name']==name);body=elf.contents(sec);offset=address-0x10000000+0x38940
        assert sec['address']==address and body==stock[offset:offset+len(body)]
        rows.append({'name':name,'address':address,'bytes':len(body)})
    assert len([s for s in elf.sections if s['flags']&2 and s['size']])==9
    report={'initializer_evidence':evidence,'source_sha256':sha(source.read_bytes()),'header_sha256':sha((source.parent/'runtime_gx8002_backup_heap.h').read_bytes()),'messages':rows,'state_bytes':24,'source_admitted':False,'limits':['Six recovered state words including current and maximum used-byte statistics. Other allocator globals and heap arena ownership not claimed.']}
    (ROOT/'docs/research/gx8002-backup-heap-data.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['messages'])
