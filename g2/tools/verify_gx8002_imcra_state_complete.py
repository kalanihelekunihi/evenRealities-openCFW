# SPDX-License-Identifier: MIT
"""Complete entry/return execution; helper models remain explicit limitations."""
import json,subprocess
from build_gx8002_backup_imcra_state import build,ROOT
from verify_gx8002_memcpy_source import decode
from execute_gx8002_imcra_state import execute

def verify(concrete_cosine=False):
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x46cc4','--stop-address=0x470c4',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-backup-imcra-state/state.disassembly.txt').read_text());cases=[]
    source_cosine=stock_cosine=None
    if concrete_cosine:
        from execute_gx8002_cosine_numeric import execute as cos_execute
        from build_transparent_image import Elf32
        from analyze_gx8002_upstream_objects import IMAGE
        path=ROOT/'build/gx8002-backup-cosine/cosine.elf';elf=Elf32(path.read_bytes(),'cosine')
        table=elf.contents(next(s for s in elf.sections if s['name']=='.sine_table'))
        stock_table=IMAGE.read_bytes()[0x4d214:0x4d214+2052];assert table==stock_table
        source_code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
        stock_code=decode(subprocess.check_output([pre,'-D','--start-address=0x477a4','--stop-address=0x4781c',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
        source_cosine=lambda x,f:cos_execute(source_code,0x1000ee64,x,table,f)
        stock_cosine=lambda x,f:cos_execute(stock_code,0x477a4,x,stock_table,f)
    for size in (42320,43008,65536):
        for fused in (False,True):
            a=execute(old,0x46cc4,size,fused,stock_cosine);b=execute(new,0x1000e384,size,fused,source_cosine)
            assert a==b, (size,fused,next(((i,x,y) for i,(x,y) in enumerate(zip(a['trace'],b['trace'])) if x!=y),None))
            assert a['result']==0x20010000;cases.append({'capacity':size,'fused':fused,'effects':len(a['trace'])})
    report={'concrete_cosine':concrete_cosine,'build':evidence,'cases':cases,'source_admitted':False,'limits':['Full stock/source entry-to-return register and memory execution. Cosine uses decoded stock/source implementations when concrete_cosine is true, otherwise shared host-math model; power fixed observed result, workspace/printf/memset/conversion modeled. No physical FPU qualification or arbitrary helper mutation proof. Cosine composition occurs at a helper boundary with its own register file. Ordered state writes and helper effects compared; memory reads not traced.']}
    (ROOT/('docs/research/gx8002-imcra-state-source-cosine.json' if concrete_cosine else 'docs/research/gx8002-imcra-state-complete.json')).write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
