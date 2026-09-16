# SPDX-License-Identifier: MIT
"""Inventory BSS address dependencies before changing the backup memory map."""
import json,re,struct,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32


def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    current=ROOT/'build/gx8002-fft-q15-centered-integration-experiment'
    report_path=current/'build-report.json';report=json.loads(report_path.read_text())
    candidate=(current/'firmware_codec.unadmitted.bin').read_bytes()
    assert sha(candidate)==report['firmware_sha256']
    start,end=struct.unpack_from('<I',stock,0x3ba88)[0],struct.unpack_from('<I',stock,0x3ba84)[0]
    assert (start,end)==(0x20017090,0x2002d79c)
    def owner(offset):
        row=next(r for r in report['ownership'] if r['offset']<=offset<r['offset']+r['size'])
        return {'kind':row['kind'],'symbol':row.get('symbol')}
    text=subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x3b940','--stop-address=0x4f9cc',str(wrapper)],text=True)
    loads=[]
    for line in text.splitlines():
        match=re.match(r'\s*([0-9a-f]+):.*\blrw\s+(r\d+),\s*0x([0-9a-f]+)\s*//\s*([0-9a-f]+)',line)
        if not match:continue
        pc,reg,value,pool=match.groups();pc,value,pool=int(pc,16),int(value,16),int(pool,16)
        if start<=value<end:
            assert struct.unpack_from('<I',stock,pool)[0]==value
            loads.append({'stock_consumer':pc,'register':reg,'value':value,'pool':pool,
                          'current_consumer_ownership':owner(pc),'current_pool_ownership':owner(pool),
                          'pool_word_unchanged':candidate[pool:pool+4]==stock[pool:pool+4]})
    words=[]
    for off in range(len(stock)-3):
        value=struct.unpack_from('<I',stock,off)[0]
        if start<=value<end:
            words.append({'offset':off,'value':value,'aligned':off%4==0,
                          'current_ownership':owner(off),'word_unchanged':stock[off:off+4]==candidate[off:off+4]})
    result={'stock_sha256':IMAGE_SHA,'candidate_sha256':sha(candidate),'ownership_report_sha256':sha(report_path.read_bytes()),
            'bss_bounds':[start,end],'bss_bytes':end-start,'literal_loads':loads,'stored_address_candidates':words,
            'unique_literal_addresses':sorted({r['value'] for r in loads}),
            'counts':{'literal_loads':len(loads),'unique_literal_addresses':len({r['value'] for r in loads}),
                      'stored_address_candidates':len(words),'literal_consumers_in_retained_stock':sum(r['current_consumer_ownership']['kind']=='retained_stock' for r in loads)},
            'source_admitted':False,'limits':['Stock linear disassembly includes possible data decoded as instructions; entries require individual use validation.',
                'Ownership identifies current source replacement regions, not whether their instructions retain the original references.',
                'Raw address candidates may be accidental and are not relocation records. Never mass-patch this list.',
                'Computed addresses, interior object pointers, immediate constructions, live stack/heap and hardware/DMA aliases require additional evidence before BSS moves.']}
    (ROOT/'docs/research/gx8002-backup-bss-relocation.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(analyze()['counts'])
