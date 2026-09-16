# SPDX-License-Identifier: MIT
"""Ground denoise initialization branches/callees in the authenticated backup image."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    text=subprocess.check_output([pre,'-D','--start-address=0x44584','--stop-address=0x44694',str(path)],text=True)
    code=decode(text);calls=[];strings={}
    for pc,(op,args,width) in code.items():
        if pc>=0x4465a:continue
        if op=='bsr':calls.append({'site':pc,'target_package':int(args,0),'target_runtime':int(args,0)-0x38940+0x10000000})
        if op=='lrw':
            value=int(args.split(',')[-1].strip(),0)
            if 0x10013700<=value<0x10013b00:
                offset=value-0x10000000+0x38940;end=stock.index(0,offset)
                strings[hex(value)]=stock[offset:end].decode('ascii')
    assert {c['target_package'] for c in calls}=={0x3c8f8,0x42d58,0x42274,0x428e8,0x42850,0x428c0,0x4286c,0x470c4,0x44140,0x4425c}
    branches={hex(pc):{'opcode':op,'operands':args} for pc,(op,args,w) in code.items() if pc<0x4465a and op in ('bf','bt','bez','bnez','br')}
    report={'stock_sha256':IMAGE_SHA,'package_interval':[0x44584,0x44694],'runtime_entry':0x1000bc44,'function_sha256':sha(stock[0x44584:0x44694]),'calls':calls,'branches':branches,'strings':strings,'state_base':0x2002d2bc,'observations':[
        'Unsigned status from3c8f8 >=2 skips local setup and proceeds to audio registration.',
        'Local setup invokes428e8(state+28,state+52,40,4), then42850.',
        'State word+16 equal0 invokes44140 (beamforming); equal1 invokes4425c (IMCRA); other values skip both with no-noise-reduction diagnostic.',
        'Either algorithm setup nonzero returns-1 after diagnostic.',
        'Two428c0 calls occur before DRC setup: first diagnostic argument, second retained as DRC argument0. Allocate512 via4286c; call470c4(retained,256,allocation), store returned pointer at state+24.',
        'Null DRC result returns-1; nonnull proceeds to42d58(callback1000bd54). Nonzero audio registration returns-1; zero logs two success messages and returns0.'
    ],'source_admitted':False,'limits':['Control-flow analysis only. Callee semantics not inferred from names alone. Denoise source implementation, state ownership, callback body and composed execution remain incomplete.']}
    out=ROOT/'build/gx8002-backup-denoise-initialize';out.mkdir(exist_ok=True);(out/'stock.disassembly.txt').write_text(text)
    (ROOT/'docs/research/gx8002-backup-denoise-initialize-analysis.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(len(analyze()['calls']))
