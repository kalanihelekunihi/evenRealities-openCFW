# SPDX-License-Identifier: MIT
"""Locate MPU write encodings in the entire authenticated codec, including overlays."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_backup_fft_mpu import verify

def analyze():
    evidence=verify();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D',str(wrapper)],text=True))
    # mtcr rN, cr<18..21,0>: source register is the low five bits of
    # the first halfword. Scan all aligned instruction starts, independent
    # of the linear decoder's choice of preceding instruction width.
    raw=[]
    for off in range(0,len(stock)-3,2):
        first=int.from_bytes(stock[off:off+2],'little');second=int.from_bytes(stock[off+2:off+4],'little')
        if first&0xffe0==0xc000 and second in (0x6432,0x6433,0x6434,0x6435):
            raw.append({'offset':off,'register':second-0x6420,'source_register':first&31})
    starts=[0x5152,0x15562,0x3ba8e];relative=[0x16,0x2c,0x36,0x42]
    assert [r['offset'] for r in raw]==[a+b for a in starts for b in relative]
    slices=[];reference=stock[starts[-1]:starts[-1]+70]
    for start in starts:
        assert stock[start:start+70]==reference
        normalized=[(pc-start,op,args,width) for pc,(op,args,width) in code.items() if start<=pc<start+70]
        target=[(pc-starts[-1],op,args,width) for pc,(op,args,width) in code.items() if starts[-1]<=pc<starts[-1]+70]
        # Includes resolved lrw value, proving identical bytes refer to the
        # same mask even though literal pool addresses differ by overlay.
        assert normalized==target
        assert any(op=='lrw' and args=='r1, 0xfefffcfe' for _,op,args,_ in normalized)
        slices.append({'start':start,'bytes':70,'sha256':sha(reference),'identical_decoded_semantics':True})
    result={'stock_sha256':IMAGE_SHA,'backup_model':evidence,'aligned_encoding_matches':raw,'initialization_slices':slices,
            'source_admitted':False,'hardware_qualified':False,'limits':['All observed encodings for mtcr rN, cr<18..21,0> in the codec occur in three identical region-0 startup slices.','Only this instruction encoding and register bank are scanned. ROM, external code, alternate mechanisms and initial hardware state are outside the image.','All three slices preserve other region state; this evidence does not establish effective MPU priority or reset state.']}
    (ROOT/'docs/research/gx8002-codec-mpu-writes.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=analyze();print(len(r['aligned_encoding_matches']),'MPU writes;',len(r['initialization_slices']),'identical startup slices')
