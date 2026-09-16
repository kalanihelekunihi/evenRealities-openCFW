# SPDX-License-Identifier: MIT
"""Pinned scalar upstream adaptation versus existing decoded stock DSP executor."""
import json,subprocess
from build_gx8002_beam_shift_q15 import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_shift_buffer_decoded import execute as stock_execute
from execute_gx8002_imcra_process import execute as source_execute

def verify(startup=False):
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    provenance=json.loads((ROOT/'docs/research/gx8002-csky-dsp-upstream-evidence.json').read_text())
    for row in provenance['files']:assert sha((ROOT/'build/upstream-xuantie-qemu-csky'/row['file']).read_bytes())==row['sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    original=decode(subprocess.check_output([pre,'-D','--start-address=0x47a00','--stop-address=0x47a74',str(path)],text=True))
    compiled=decode((ROOT/'build/gx8002-beam-shift-q15/shift.disassembly.txt').read_text());cases=0
    if startup:
        target=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
        integrated=Elf32(target.read_bytes(),'startup')
        symbol=next(s for s in integrated.symbols() if s['name']=='beam_shift_q15')
        assert symbol['section'] not in (0,0xfff1) and symbol['value']==0x1000f0c0
        evidence['startup_elf_sha256']=sha(target.read_bytes())
        compiled=decode((target.parent/'cluster.disassembly.txt').read_text())
    for count in range(33):
      for shift in range(-128,32):
       for delta in (0,256):
        for pattern in (0,1):
            values=bytes((i*73+19)&255 for i in range(512)) if pattern==0 else bytes(512)
            wanted,trace=stock_execute(original,0x47a00,values,shift,count,delta)
            base=0x21000000
            actual=source_execute(compiled,0x1000f0c0,{base+i:v for i,v in enumerate(values)},[base+64,shift,base+64+delta,count],{})
            assert actual['memory']=={base+i:v for i,v in enumerate(wanted)},(count,shift,delta,pattern)
            old_writes=[(base+a+i,(v>>(8*i))&255) for op,a,n,v in trace if op=='write' for i in range(n)]
            new_writes=[(a+i,(v>>(8*i))&255) for op,a,v,n in actual['trace'] for i in range(n)]
            assert old_writes==new_writes
            cases+=1
    report={'build':evidence,'startup':startup,'vendor_commit':provenance['commit'],'cases':cases,'source_admitted':False,'limits':['Stock packed DSP and compiled source final memory/ordered byte writes match for -128..31, word-aligned disjoint and exact in-place buffers.','Access grouping differs; partial overlap, atomicity, hardware and full-register shift ABI are not qualified. Upstream C shift parameter is int8_t.','Caller range/reference closure and integration remain pending.']}
    (ROOT/('docs/research/gx8002-beam-shift-stock'+('-startup' if startup else '')+'.json')).write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
