# SPDX-License-Identifier: MIT
"""Inventory stored and immediate data-alias references to candidate tails."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    source=ROOT/'docs/research/gx8002-backup-replacement-tails.json';tails=json.loads(source.read_text())['tails']
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x3b940','--stop-address=0x4f9cc',str(path)],text=True));rows=[]
    for row in tails:
        lo,hi=[v-0x3b940+0x20003000 for v in row['tail']];words=[];literals=[]
        for offset in range(len(stock)-3):
            value=int.from_bytes(stock[offset:offset+4],'little')
            if lo<=value<hi:words.append({'offset':offset,'value':value})
        for pc,(op,args,width) in code.items():
            if op=='lrw':
                try:value=int(args.split(',')[-1].strip(),0)
                except ValueError:continue
                if lo<=value<hi:literals.append({'pc':pc,'value':value})
        rows.append({'function':row['function'],'data_alias':[lo,hi],'stored_words':words,'loaded_literals':literals})
    report={'stock_sha256':IMAGE_SHA,'tail_census_sha256':sha(source.read_bytes()),'results':rows,'reclaim_admitted':False,'limits':['Known 0x20000000 data alias only; whole-image byte-aligned words and backup-text literal loads. Arithmetic address construction and other mappings are not excluded.','No tail reuse, firmware write or loader modification.']}
    (ROOT/'docs/research/gx8002-backup-tail-data-aliases.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
    for r in analyze()['results']:print(r['function'],r['stored_words'],r['loaded_literals'])
