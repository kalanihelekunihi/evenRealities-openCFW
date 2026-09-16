# SPDX-License-Identifier: MIT
"""Inventory decoded IMCRA initializer calls, excluding embedded literal pools."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-imcra-initialize';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    ranges=((0x46cc4,0x47056),(0x4709c,0x470bc));code={}
    for start,end in ranges:
        raw=subprocess.check_output([pre+'objdump','-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True)
        (out/f'core-{start:x}.disassembly.txt').write_text(raw);code.update(decode(raw))
    elf=Elf32((ROOT/'build/gx8002-backup-startup-cluster/cluster.elf').read_bytes(),'cluster')
    calls={}
    for pc,(op,args,width) in code.items():
        if op=='bsr':calls.setdefault(int(args,0),[]).append(pc)
    targets=[]
    for target,sites in sorted(calls.items()):
        runtime=target-0x38940+0x10000000
        symbols=[s['name'] for s in elf.symbols() if s['value']==runtime and s['type']==2 and s['section'] not in (0,0xfff1)]
        targets.append({'package':hex(target),'runtime':hex(runtime),'call_sites':[hex(s) for s in sites],'allocated_functions':symbols})
    report={'stock_sha256':IMAGE_SHA,'entry_package':'0x46cc4','entry_runtime':'0x1000e384','envelope_bytes':0x470c4-0x46cc4,'instruction_ranges':[[hex(a),hex(b)] for a,b in ranges],'direct_targets':targets,'source_admitted':False,'observations':['Checks minimum buffer size 196 before writing state.','Writes fixed 16000 at state+8 and 512 at +12,+16,+24; writes 256 at +20 and 257 at +28.','Calls package 0x46c54 for workspace sizing and compares required size plus 196 against supplied size.','Literal pools at 0x47058..0x4709c and 0x470bc..0x470c4 are excluded from instruction inventory.'],'limits':['This inventory is static evidence, not reconstructed algorithm source or execution qualification. Field meanings beyond observed dimensions and header size need further validation.']}
    (ROOT/'docs/research/gx8002-backup-imcra-initializer-analysis.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(analyze(),indent=2))
