# SPDX-License-Identifier: MIT
"""Direct decoded stock DSP versus compiled scalar buffer comparison."""
import json,subprocess
from build_gx8002_backup_shift_q15 import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_shift_buffer_decoded import execute

def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    provenance=json.loads((ROOT/'docs/research/gx8002-csky-dsp-upstream-evidence.json').read_text())
    for record in provenance['files']:assert sha((ROOT/'build/upstream-xuantie-qemu-csky'/record['file']).read_bytes())==record['sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    original=decode(subprocess.check_output([pre,'-D','--start-address=0x47a00','--stop-address=0x47a74',str(path)],text=True))
    compiled=decode((ROOT/'build/gx8002-backup-shift-q15/shift.disassembly.txt').read_text());cases=0
    # Positive shifts <=31 avoid the vendor model's zero/oversized-shift UB.
    shifts=(-0x80000000,-33,-32,-31,-16,-1,0,1,8,15,16,17,31)
    for count in range(33):
      for shift in shifts:
       for delta in (-16,-8,-4,0,4,8,16,256):
        for pattern in (0,1):
            values=bytes((i*73+19)&255 for i in range(512)) if pattern==0 else bytes(512)
            assert execute(original,0x47a00,values,shift,count,delta)==execute(compiled,evidence['entry'],values,shift,count,delta),(count,shift,delta,pattern)
            cases+=1
    report={'build':evidence,'vendor_commit':provenance['commit'],'direct_stock_cases':cases,'source_admitted':False,'hardware_qualified':False,
            'limits':['Direct decoded stock packed DSP versus compiled scalar helper calls: full memory and ordered sample access traces. Zero and patterned buffers, bounded counts and overlaps.','Doubleword load modeled as two word reads; bus atomicity not modeled. Positive shift counts above 31 excluded because vendor zero behavior is undefined. Hardware and full-domain proof remain pending.']}
    (ROOT/'docs/research/gx8002-shift-stock-decoded.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['direct_stock_cases'],'direct stock cases')
