# SPDX-License-Identifier: MIT
"""Record stock reducer instruction/literal extent and source placement demand."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_double_wrapper_references import analyze


def analyze_layout():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    text=subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x4863c','--stop-address=0x489e4',str(wrapper)],text=True)
    code=decode(text);assert code[0x4863c][:2]==('push','r4-r11, r15')
    calls=[{'pc':pc,'target':int(args,16)} for pc,(op,args,width) in code.items() if pc<0x48994 and op=='bsr']
    pools=[]
    import re
    for line in text.splitlines():
        m=re.search(r'^\s*([0-9a-f]+):.*\blrw\s+.*// ([0-9a-f]+)',line)
        if m and int(m[1],16)<0x48994:pools.append({'consumer':int(m[1],16),'pool':int(m[2],16)})
    assert min(r['pool'] for r in pools)==0x48994
    assert max(r['pool'] for r in pools)==0x489e0
    report=json.loads((ROOT/'docs/research/gx8002-reduction-probe.json').read_text())
    result={'stock_sha256':IMAGE_SHA,'entry':0x4863c,'next_entry':0x489e4,'region_bytes':0x489e4-0x4863c,'literal_start':0x48994,'calls':calls,'call_targets':sorted(set(r['target'] for r in calls)),'literal_consumers':pools,'references':analyze(0x4863c,0x489e4,require_entry_only=False),'upstream_objects':report['objects'],'source_admitted':False,'limits':['Stock reducer uses a different large-input path with a scale table, not an identified call to the upstream large-argument kernel. Complete upstream source requires additional space; cannot assume a matching stock kernel region exists. Instruction/literal extent is bounded evidence, not computed-reference closure.']}
    (ROOT/'docs/research/gx8002-reducer-layout.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=analyze_layout();print(r['region_bytes'],[hex(v) for v in r['call_targets']])
