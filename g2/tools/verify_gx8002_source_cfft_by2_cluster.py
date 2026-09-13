# SPDX-License-Identifier: MIT
"""Linked radix-4-by-2 CFFT versus composed decoded stock arithmetic."""
import json,random,subprocess
from build_gx8002_source_cfft_cluster import build,ROOT,Elf32,sha
from verify_gx8002_source_cfft_cluster import execute as linked
from verify_gx8002_backup_radix4_stock_host import execute as radix
from verify_gx8002_backup_radix4_by2_decoded import execute as by2,DELTA,IMAGE,IMAGE_SHA
from verify_gx8002_memcpy_source import decode
from generate_gx8002_backup_math_tables import coefficients as generate

def verify(shared=False):
    if shared:
        from build_gx8002_source_rfft_cluster import build as rfft_build
        evidence=rfft_build(shared_radix4=True,shared_by2=True);out=ROOT/'build/gx8002-source-rfft-double-shared-cluster'
    else:
        evidence=build();out=ROOT/'build/gx8002-source-cfft-cluster'
    code=decode((out/'cluster.disassembly.txt').read_text())
    elf=Elf32((out/'cluster.elf').read_bytes(),'cluster');entry=next(s['value'] for s in elf.symbols() if s['name']=='open_cfw_gx8002_backup_cfft');ro=next(s for s in elf.sections if s['name']=='.rodata')
    original={ro['address']+i:v for i,v in enumerate(elf.contents(ro))}
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');raw=generate(complex_fft=True);base=raw[0] if isinstance(raw,tuple) else raw
    rng=random.Random(128);cases=0
    for inverse in (0,1):
        start,end,lower,lower_end=(0x47c98,0x47d3c,0x47f50,0x48164) if inverse else (0x47bf4,0x47c98,0x47d3c,0x47f50)
        stock_by2=decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(wrapper)],text=True))
        stock_radix=decode(subprocess.check_output([pre,'-D',f'--start-address={lower:#x}',f'--stop-address={lower_end:#x}',str(wrapper)],text=True))
        for length in (32,128):
            stride=256//length
            coefficients=[base[2*i*stride+j] for i in range(3*length//4) for j in (0,1)]
            bits=length.bit_length()-1;permutation=[int(f'{i:0{bits}b}'[::-1],2) for i in range(length)]
            table=[v*8 for i,j in enumerate(permutation) if i<j for v in (i,j)]
            memory=dict(original)
            def put(a,v,n):
                for i in range(n):memory[a+i]=(v>>(i*8))&255
            for i in range(16):put(0x9000+i,0,1)
            put(0x9000,length,2);put(0x9004,0xa000,4);put(0x9008,0xb000,4);put(0x900c,len(table),2)
            for i,v in enumerate(coefficients):put(0xa000+2*i,v,2)
            for i,v in enumerate(table):put(0xb000+2*i,v,2)
            for trial in range(8):
                values=[(-32768 if i%2 else 32767) if trial==0 else rng.randrange(-32768,32768) for i in range(length*2)]
                expected,calls=by2(stock_by2,start,DELTA,values,coefficients,inverse,helper=lambda data,coeff,modifier:radix(stock_radix,lower,data,coeff,modifier))
                assert len(calls)==2
                for reversal in (0,1,255):
                    result=linked(code,entry,values,memory,0x9000,inverse,reversal)
                    oracle=tuple(expected[2*permutation[i]+j] for i in range(length) for j in (0,1)) if reversal else expected
                    assert result==oracle,(inverse,length,trial,reversal)
                    cases+=1
    report={'build':evidence,'linked_by2_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Actual linked source dispatcher, radix-4-by-2, both lower radix-4 calls, scaling and optional reversal executed. Compared with decoded stock by2 and stock radix arithmetic composition.','Lengths 32/128 use source-derived coefficient subsampling and generated reversal descriptors in test RAM. This is not qualification of extra shipped firmware descriptors.','Whole linked outputs, preserved registers and read-only data checked; no firmware placement or hardware qualification.']}
    (ROOT/('docs/research/gx8002-source-cfft-by2-shared-verification.json' if shared else 'docs/research/gx8002-source-cfft-by2-cluster-verification.json')).write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['linked_by2_cases'])
