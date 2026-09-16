# SPDX-License-Identifier: MIT
"""Backup context ordered-store comparison against independent layout values."""
import json,subprocess
from build_gx8002_backup_context_initialize import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_buffer_initialize import execute
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x426bc','--stop-address=0x42758',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-context-initialize/context.disassembly.txt').read_text())
    writes=[(0,0x20191222),(8,2),(80,0x20030000),(84,12288),(24,1),(72,0x2001a380),(76,6144),(52,12),(40,12),(108,40),(96,256),(28,16),(68,2784),(32,16000),(64,2816),(12,0),(88,0),(92,0),(16,0),(100,0),(104,0),(44,0),(20,0),(112,0),(116,0),(48,0),(36,3),(56,0x20017780),(60,4),(4,0)]
    expected=[('clear',0x20017700,0,120),('clear',0x20017780,0,11264)]+[('write',o,v) for o,v in writes]
    cases=0
    for seed in (0,1,0xffffffff,0xa5a5a5a5,0x80000000):
        for code,entry,delta in ((old,0x426bc,0x10000000-0x38940),(new,0x10009d7c,0)):
            assert execute(code,entry,seed,header_address=0x20017700,helper_address=0x100113c4,stock_delta=delta)==(0,expected)
            cases+=1
    from build_gx8002_backup_memset import build as clear_build
    clear_evidence=clear_build()
    old_clear=decode(subprocess.check_output([pre,'-D','--start-address=0x49d04','--stop-address=0x49da4',str(path)],text=True))
    new_clear=decode((ROOT/'build/gx8002-backup-memset/memset-candidate.disassembly.txt').read_text())
    nested=0
    for seed in (0,1,0xffffffff,0xa5a5a5a5,0x80000000):
        initial={a:((a*37+seed)%255)+1 for a in range(0x200176f0,0x2001a390)}
        wanted=initial.copy()
        for start,size in ((0x20017700,120),(0x20017780,11264)):
            for a in range(start,start+size):wanted[a]=0
        for offset,value in writes:
            for i,b in enumerate(value.to_bytes(4,'little')):wanted[0x20017700+offset+i]=b
        for code,entry,delta in ((old,0x426bc,0x10000000-0x38940),(new,0x10009d7c,0)):
            for helper,helper_entry in ((old_clear,0x49d04),(new_clear,clear_evidence['runtime_address'])):
                memory=initial.copy()
                assert execute(code,entry,seed,memory,helper,helper_entry,header_address=0x20017700,helper_address=0x100113c4,stock_delta=delta)==(0,expected)
                assert memory==wanted
                nested+=1
    report={'nested_clear_cases':nested,'clear_build':clear_evidence,'build':evidence,'decoded_cases':cases,'source_admitted':False,'limits':['Exact ordered header stores and memset arguments; Actual decoded stock/source clearing bodies executed across marshalled helper frames; caller-saved registers poisoned. Surrounding bytes and header gap checked unchanged. Storage ownership and hardware remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-context-initialize-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['decoded_cases'])
