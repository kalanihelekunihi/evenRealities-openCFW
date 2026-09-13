# SPDX-License-Identifier: MIT
"""Prove decoded comparison wrappers differ only in PC-relative placement."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_double_wrapper_references import analyze

def verify():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x4aae0','--stop-address=0x4abd0',str(path)],text=True))
    records=[]
    for source,target,size in [(0x4aae0,0x4ab20,64),(0x4ab60,0x4ab98,56)]:
        pc=source;count=0
        while pc<source+size:
            op,args,width=code[pc];other,otherargs,otherwidth=code[target+pc-source]
            assert op==other and width==otherwidth
            if op in ('bt','bf','br','bsr'):
                a,b=int(args,0),int(otherargs,0)
                if source<=a<source+size:assert b-target==a-source
                else:assert a==b
            else:assert args==otherargs
            pc+=width;count+=1
        assert pc==source+size
        refs=analyze(target,target+size)
        records.append({'verified_wrapper':source,'twin_entry':target,'bytes':size,'instructions':count,'stock_sha256':sha(stock[target:target+size]),'references':refs})
    result={'firmware_sha256':IMAGE_SHA,'twins':records,'source_admitted':False,'limits':['Complete decoded instruction/operand equality under internal-PC translation, including unchanged external helper call targets. Supports reusing corresponding source comparison semantics; source placement/link and firmware integration pending.']}
    (ROOT/'docs/research/gx8002-double-comparison-twins.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print([(r['twin_entry'],r['instructions'],len(r['references']['external_branches'])) for r in verify()['twins']])
