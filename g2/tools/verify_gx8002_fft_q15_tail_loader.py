# SPDX-License-Identifier: MIT
"""Load the physical source cluster together with its source clock-tail host."""
import json,subprocess
from build_gx8002_fft_q15_tail_layout import build
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,Elf32,sha
from verify_gx8002_backup_memset_loader import execute
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    census_path=ROOT/'docs/research/gx8002-backup-replacement-tails.json';census=json.loads(census_path.read_text())
    assert sha((ROOT/'build/gx8002-source-candidate/build-report.json').read_bytes())==census['source_build_report_sha256']
    clock=next(t for t in census['tails'] if t['function']=='clock_lookup')
    cluster_path=ROOT/'build/gx8002-fft-q15-tail-layout/component.elf';cluster=Elf32(cluster_path.read_bytes(),'cluster')
    assert sha(cluster_path.read_bytes())==evidence['elf_sha256']
    clock_path=ROOT/'build/gx8002-source-candidate/backup-clock-lookup/tables.elf';host=Elf32(clock_path.read_bytes(),'clock')
    start=clock['stock_envelope'][0];address=start-0x3b940+0x10003000
    section=next(s for s in host.sections if s['address']==address and s['flags']&4)
    body=host.contents(section);assert sha(body)==clock['compiled_sha256'] and start+len(body)==clock['tail'][0]
    patches=[{'offset':start,'address':address,'payload':body,'name':'source_clock_lookup'}]
    for section in cluster.sections:
        if section['flags']&2 and section['size']:
            row=evidence['sections'][section['name']];body=cluster.contents(section);assert sha(body)==row['sha256']
            patches.append({'offset':row['offset'],'address':row['address'],'payload':body,'name':section['name']})
    image=bytearray(stock);occupied=set()
    for patch in patches:
        off=patch['offset'];body=patch['payload'];span=set(range(off,off+len(body)));assert not occupied&span;occupied|=span
        image[off:off+len(body)]=body
    assert all(a==b for i,(a,b) in enumerate(zip(stock,image)) if i not in occupied)
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock')
    assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x396a0','--stop-address=0x396ee',str(wrapper)],text=True));cases=0
    for mode in (0,1,0xffffffff,0xaabbccdc):
        for seed in (0,91,0xffffffff):
            result,calls,memory=execute(code,bytes(image),mode,seed)
            loaded=b''.join(memory[a].to_bytes(4,'little') for a in range(0x10003000,0x1001708c,4))
            assert result==0 and loaded==image[0x3b940:0x4f9cc];cases+=1
    result={'build':evidence,'clock_elf_sha256':sha(clock_path.read_bytes()),'tail_census_sha256':sha(census_path.read_bytes()),'loader_cases':cases,'patched_bytes':len(occupied),'source_admitted':False,'hardware_qualified':False,
            'limits':['Combined cluster and authenticated source clock host through decoded stock loader. Exact loaded bytes and unrelated input preservation checked.','Loader-input experiment only: container checksums are not regenerated here. Clock execution, tail reuse admission, full-container composition and hardware qualification remain separate.']}
    (ROOT/'docs/research/gx8002-fft-q15-tail-loader.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=verify();print(r['loader_cases'],r['patched_bytes'])
