# SPDX-License-Identifier: MIT
"""Inventory literal and stored-pointer references to reconstructed math data."""
import json,subprocess
from build_gx8002_backup_math_tables import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x3b940','--stop-address=0x4ee5c',str(wrapper)],text=True))
    records=[]
    for name,address,size in (('q14_pairs',0x100150d8,1024),('bit_lengths',0x100155d4,256)):
        literals=[];words=[]
        for pc,(op,args,width) in code.items():
            if op!='lrw':continue
            try:value=int(args.split(',')[-1].strip(),0)
            except ValueError:continue
            if address<=value<address+size:literals.append({'instruction':pc,'value':value})
        for offset in range(0x3893c,len(stock)-3):
            value=int.from_bytes(stock[offset:offset+4],'little')
            if address<=value<address+size:words.append({'offset':offset,'value':value})
        records.append({'name':name,'address':address,'bytes':size,'literal_loads':literals,'stored_pointers':words})
    report={'build':evidence,'tables':records,'source_admitted':False,
            'limits':['Linear literal loads and byte-aligned pointer census identify consumer candidates, not full call/control-flow qualification.']}
    (ROOT/'docs/research/gx8002-backup-math-table-references.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    for table in analyze()['tables']:print(table)
