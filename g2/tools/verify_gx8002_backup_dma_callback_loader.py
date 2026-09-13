# SPDX-License-Identifier: MIT
"""Verify normal backup loading of source DMA callback setter, without fill."""
import json,subprocess
from verify_gx8002_backup_memset_loader import execute,ROOT,IMAGE,IMAGE_SHA,sha,Elf32,decode

def verify():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    p=ROOT/'build/gx8002-backup-dma-callback/callback.elf';elf=Elf32(p.read_bytes(),str(p));image=bytearray(stock)
    sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert [(s['name'],s['address'],s['size']) for s in sections]==[('.text',0x10004cb8,16)]
    for s in sections:
        offset=s['address']-0x10003000+0x3b940
        image[offset:offset+s['size']]=elf.contents(s)
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    e=Elf32(wrapper.read_bytes(),str(wrapper));assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x396a0','--stop-address=0x396ee',str(wrapper)],text=True))
    cases=0
    for mode in (0,1,0xffffffff,0xaabbccdc):
        for seed in (0,91,0xffffffff):
            result,calls,memory=execute(code,bytes(image),mode,seed)
            loaded=b''.join(memory[a].to_bytes(4,'little') for a in range(0x10003000,0x1001708c,4))
            assert result==0 and loaded==image[0x3b940:0x4f9cc]
            for s in sections:
                offset=s['address']-0x10003000;assert loaded[offset:offset+s['size']]==elf.contents(s)
            cases+=1
    return {'candidate_elf_sha256':sha(p.read_bytes()),'candidate_image_sha256':sha(bytes(image)),'normal_loader_cases':cases,'source_admitted':False,'limits':['All 16 replacement bytes come from compiled C; no replacement tail fill.','External references and hardware remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-dma-callback-loader.json').write_text(json.dumps(r,indent=2)+'\n');print(r['normal_loader_cases'],'loader cases passed')
