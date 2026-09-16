# SPDX-License-Identifier: MIT
"""Check loader growth constraints against stock instructions and BSS bounds."""
import json,struct,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_backup_memset_loader import execute


def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x396a0','--stop-address=0x396ee',str(wrapper)],text=True))
    words={off:struct.unpack_from('<I',stock,off)[0] for off in (0x39728,0x39734,0x39738,0x3973c,0x3ba84,0x3ba88)}
    length=words[0x39734]+words[0x39738]-words[0x39728]-words[0x3973c]
    assert length==0x1408c
    extension=bytes((i*17+3)&255 for i in range(8192))
    cases=0
    for mode in (0,1,0xffffffff,0xaabbccdc):
        for seed in (0,91,0xffffffff):
            result,calls,memory=execute(code,stock+extension,mode,seed)
            assert result==0 and calls[1]==['read',0x323b4,0x10003000,length]
            assert 0x1001708c not in memory
            cases+=1
    reduction=ROOT/'build/gx8002-reduction-source-closure/reduction.elf'
    report=json.loads((ROOT/'docs/research/gx8002-reduction-source-closure.json').read_text())
    assert sha(reduction.read_bytes())==report['elf_sha256']
    e=Elf32(reduction.read_bytes(),'reducer');sec=next(s for s in e.sections if s['name']=='.reduction')
    data_start=sec['address']+0x10000000;data_end=data_start+sec['size']
    bss_start,bss_end=words[0x3ba88],words[0x3ba84]
    overlap=max(0,min(data_end,bss_end)-max(data_start,bss_start))
    assert overlap==sec['size']==3990
    result={'stock_sha256':IMAGE_SHA,'loader_literal_words':{hex(k):hex(v) for k,v in words.items()},
            'fixed_copy_bytes':length,'append_probe_bytes':len(extension),'append_probe_loader_cases':cases,
            'appended_bytes_loaded':0,'bss_bounds':[bss_start,bss_end],
            'reducer_elf_sha256':report['elf_sha256'],'reducer_analysis_data_alias':[data_start,data_end],
            'reducer_bytes_overlapping_bss':overlap,'source_admitted':False,
            'limits':['Appending bytes does not extend the fixed copy length; first flash word controls source displacement, not length.',
                      'Existing analysis reducer allocation overlaps the startup-cleared BSS alias. Merely enlarging the loader copy cannot qualify it.',
                      'Growth requires coordinated loader, BSS/global placement, references and container changes; no firmware was changed by this diagnostic.']}
    (ROOT/'docs/research/gx8002-backup-growth.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=analyze();print(r['append_probe_loader_cases'],r['appended_bytes_loaded'],r['reducer_bytes_overlapping_bss'])
