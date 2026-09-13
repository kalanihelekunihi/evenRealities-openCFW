# SPDX-License-Identifier: MIT
"""Reference census for specific recovered-function tails, not free-space admission."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
# Explicit stock envelopes established by their corresponding recovery builders.
FUNCTIONS={'dma_configure':(0x3d314,408),'dma_descriptors':(0x3d210,260),'clock_lookup':(0x3be20,192),'clock_frequency':(0x3c630,492),'platform_read':(0x3c81c,220),'platform_gate':(0x3c528,264)}
DELTA=0x10003000-0x3b940

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    report_path=ROOT/'build/gx8002-source-candidate/build-report.json';report=json.loads(report_path.read_text())
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');assembly=subprocess.check_output([pre,'-D','--start-address=0x3b940','--stop-address=0x4f9cc',str(wrapper)],text=True);code=decode(assembly);rows=[]
    for name,(start,size) in FUNCTIONS.items():
        owner=next(r for r in report['ownership'] if r['offset']==start and r['kind']=='compiled_c')
        tail=start+owner['size'];end=start+size;assert start<tail<end
        assert any(r['kind']=='retained_stock' and r['offset']<=tail and end<=r['offset']+r['size'] for r in report['ownership'])
        branches=[];pools=[];pointers=[]
        for pc,(op,args,width) in code.items():
            if start<=pc<end or op not in ('br','bsr','bt','bf','bez','bnez','bhz','blz','bhsz','blsz','bnezad'):continue
            try:target=int(args.split(',')[-1].strip(),0)
            except ValueError:continue
            if tail<=target<end:branches.append({'pc':pc,'target':target})
        for line in assembly.splitlines():
            m=re.match(r'\s*([0-9a-f]+):.*\blrw\s+.*//\s*([0-9a-f]+)\s',line)
            if m:
                pc,target=(int(x,16) for x in m.groups())
                if not start<=pc<end and tail<=target<end:pools.append({'pc':pc,'pool':target})
        for off in range(len(stock)-3):
            value=int.from_bytes(stock[off:off+4],'little')
            if tail+DELTA<=value<end+DELTA:pointers.append({'offset':off,'value':value,'in_old_function':start<=off<end})
        rows.append({'function':name,'source_symbol':owner['symbol'],'compiled_sha256':owner['sha256'],'stock_envelope':[start,end],'tail':[tail,end],'bytes':end-tail,'external_branches':branches,'external_pool_loads':pools,'runtime_pointers':pointers,'reference_findings_absent':not(branches or pools or pointers),'reclaim_admitted':False})
    result={'stock_sha256':IMAGE_SHA,'source_build_report_sha256':sha(report_path.read_bytes()),'tails':rows,'total_tail_bytes':sum(r['bytes'] for r in rows),'limits':['No reuse admitted. Raw backup-text linear branch/pool census and whole-image known-runtime-pointer scan only.','Old-function references excluded from branch/pool census because source has replaced them; source ELF control-flow and pool closure must be checked separately.','Computed references, data-alias reads and all placement/loader effects remain to be qualified.']}
    (ROOT/'docs/research/gx8002-backup-replacement-tails.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=analyze()
    for row in r['tails']:print(row['function'],row['bytes'],row['external_branches'],row['external_pool_loads'],row['runtime_pointers'])
    print('Total:',r['total_tail_bytes'])
